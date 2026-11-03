"""Batch Miro board sync for the miro-orchestrator workflow (from the Dungeon_Game project).

Workers never call Miro. They drop JSON files into the shared outbox; the orchestrator
syncs the board once per round:

  1. canvas_read_as_svg(widget_ids=[kanban, ideas]) -> save result to a file
  2. python board_batch.py ingest <read.svg>   (refresh mirror, export new ideas as files)
  3. python board_batch.py build              (writes batch.svg: one update for everything)
  4. canvas_update_from_svg(batch.svg)         -> save result to a file
  5. python board_batch.py commit <result.svg> (archive outbox, learn new record ids)

Shared folder (outside the repo, visible to all worktrees):
  $BOARD_ROOT/
    config.json      widget ids of the kanban and the ideas table
    mirror.json      last known kanban rows {record_id: {column: value}} and ideas rows
    outbox/*.json    pending card changes from workers
    ideas/*.json     ideas exported for workers (status: read -> processed/clarify/rejected)
    archive/         consumed outbox files and finished ideas

Outbox file formats (one change per file, name: <utc-time>-<worker>-<task>.json):
  {"task": "T38", "set": {"Status": "Done", "Description": "...", "Progress": 100}}
  {"task": "T73", "create": {"Title": "T73 ...", "Status": "Todo: Claude can do",
     "Milestone": "M3 Raids", "Description": "...", "Owner": "Claude", "Ready": "Ready",
     "Progress": 0, "Session": ""}}
"""
import html
import json
import re
import shutil
import sys
import time
from pathlib import Path

import os
_root = os.environ.get("BOARD_ROOT")
if not _root:
    sys.exit("Set BOARD_ROOT to the shared board folder (config.json, mirror.json, outbox/, ideas/, archive/).")
ROOT = Path(_root)
OUTBOX, IDEAS, ARCHIVE = ROOT / "outbox", ROOT / "ideas", ROOT / "archive"
CONFIG, MIRROR, BATCH = ROOT / "config.json", ROOT / "mirror.json", ROOT / "batch.svg"
PENDING = ROOT / "pending.json"  # what the last build sent, consumed by commit

KANBAN_COLUMNS = ["Title", "Status", "Milestone", "Description", "Owner", "Ready", "Progress", "Session"]
IDEA_COLUMNS = ["Idea", "Details", "Status", "Created todos", "Worker note"]


def load(path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def save(path, data):
    path.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")


def ensure_dirs():
    for d in (OUTBOX, IDEAS, ARCHIVE):
        d.mkdir(parents=True, exist_ok=True)


def esc(v):
    return html.escape("" if v is None else str(v), quote=False)


def parse_tables(svg):
    """Return {miro_id: {"fields": [(field_id, name)], "rows": {record_id: [cells]}}}."""
    tables = {}
    for m in re.finditer(r'<foreignObject\b([^>]*)>(.*?)</foreignObject>', svg, re.S):
        attrs, body = m.group(1), m.group(2)
        mid = re.search(r'data-miro-id="([^"]+)"', attrs)
        if not mid or "<table" not in body:
            continue
        fields = [(re.search(r'data-field-id="([^"]+)"', th.group(1)).group(1) if 'data-field-id' in th.group(1) else None,
                   html.unescape(re.sub(r"<[^>]+>", "", th.group(2))).strip())
                  for th in re.finditer(r"<th\b([^>]*)>(.*?)</th>", body, re.S)]
        rows = {}
        for tr in re.finditer(r'<tr\b[^>]*data-record-id="([^"]+)"[^>]*>(.*?)</tr>', body, re.S):
            cells = []
            for td in re.finditer(r"<td\s*/>|<td\b[^>]*>(.*?)</td>", tr.group(2), re.S):
                inner = td.group(1) or ""
                cells.append(html.unescape(re.sub(r"<[^>]+>", "", inner)).strip())
            rows[tr.group(1)] = cells
        tables[mid.group(1)] = {"fields": fields, "rows": rows}
    return tables


def to_dict(fields, cells):
    return {name: (cells[i] if i < len(cells) else "") for i, (_, name) in enumerate(fields)}


def cmd_ingest(read_file):
    ensure_dirs()
    cfg = load(CONFIG, {})
    mirror = load(MIRROR, {"kanban": {}, "kanban_fields": {}, "ideas": {}, "ideas_fields": {}})
    tables = parse_tables(Path(read_file).read_text(encoding="utf-8"))
    kb, it = tables.get(cfg.get("kanban_id")), tables.get(cfg.get("ideas_id"))
    if kb:
        mirror["kanban_fields"] = {name: fid for fid, name in kb["fields"]}
        mirror["kanban"] = {rid: to_dict(kb["fields"], c) for rid, c in kb["rows"].items()}
    new_ideas = 0
    if it:
        mirror["ideas_fields"] = {name: fid for fid, name in it["fields"]}
        mirror["ideas"] = {rid: to_dict(it["fields"], c) for rid, c in it["rows"].items()}
        for rid, row in mirror["ideas"].items():
            f = IDEAS / f"IDEA-{rid}.json"
            if row.get("Status", "").strip() == "New" and row.get("Idea", "").strip() and not f.exists():
                save(f, {"record_id": rid, "idea": row.get("Idea", ""), "details": row.get("Details", ""),
                         "status": "read", "created_todos": [], "note": "", "exported": time.strftime("%Y-%m-%dT%H:%M:%S")})
                new_ideas += 1
    save(MIRROR, mirror)
    print(f"ingest: kanban rows={len(mirror['kanban'])} ideas rows={len(mirror['ideas'])} new ideas exported={new_ideas}")


def find_record(mirror, task):
    for rid, row in mirror["kanban"].items():
        if row.get("Title", "").split(" ")[0] == task:
            return rid
    return None


def cmd_build():
    ensure_dirs()
    cfg, mirror = load(CONFIG, {}), load(MIRROR, None)
    if not mirror or not mirror.get("kanban_fields"):
        sys.exit("build: run ingest first (mirror has no kanban fields)")
    kf = mirror["kanban_fields"]
    updates, creates, used, unresolved, update_sets = {}, [], [], [], []
    for f in sorted(OUTBOX.glob("*.json")):
        try:
            item = json.loads(f.read_text(encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            print(f"skip unreadable {f.name}: {e}")
            continue
        task = item.get("task", "")
        if "create" in item:
            if find_record(mirror, task) or any(c.get("Title", "").startswith(task + " ") for c in creates):
                item = {"task": task, "set": item["create"]}  # already exists: treat as update
            else:
                creates.append(item["create"])
                used.append(f.name)
                continue
        rid = item.get("record_id") or find_record(mirror, task)
        if not rid:
            unresolved.append(f.name)
            continue
        row = updates.setdefault(rid, {**mirror["kanban"].get(rid, {}), "__files": []})
        row.update({k: v for k, v in item.get("set", {}).items()})
        row["__files"].append(f.name)
        update_sets.append(item.get("set", {}))
        used.append(f.name)

    # Ideas: mark exported ones "Read"; delete rows whose idea file is finished.
    idea_updates, idea_deletes, idea_files_done = {}, [], []
    for f in sorted(IDEAS.glob("IDEA-*.json")):
        idea = load(f, {})
        rid, st = idea.get("record_id"), idea.get("status")
        if rid not in mirror.get("ideas", {}):
            continue
        current = mirror["ideas"][rid].get("Status", "")
        if st == "processed":
            idea_deletes.append(rid)
            idea_files_done.append(f.name)
        elif st == "clarify":
            idea_updates[rid] = {**mirror["ideas"][rid], "Status": "Needs clarification", "Worker note": idea.get("note", "")}
            idea_files_done.append(f.name)
        elif st == "rejected":
            idea_updates[rid] = {**mirror["ideas"][rid], "Status": "Rejected", "Worker note": idea.get("note", "")}
            idea_files_done.append(f.name)
        elif st in ("read", "claimed") and current == "New":
            idea_updates[rid] = {**mirror["ideas"][rid], "Status": "Read"}

    parts = []
    if updates or creates:
        # Send only the columns this batch changes (plus Title). Columns left out keep their board
        # value, so untouched descriptions are never wiped. Creates must supply every sent column.
        touched = {"Title"} | {k for row in creates for k in row} | {k for row in update_sets for k in row}
        cols = [c for c in KANBAN_COLUMNS if c in kf and c in touched]
        for rid in list(updates):
            missing = [c for c in cols if c not in updates[rid]]
            if missing:
                print(f"build: row {updates[rid].get('Title', rid)} lacks {missing}; kept for next round")
                unresolved.extend(updates.pop(rid)["__files"])
                for name in unresolved:
                    if name in used:
                        used.remove(name)
        ths = "".join(f'<th data-field-id="{kf[c]}">{esc(c)}</th>' for c in cols)
        trs = "".join(f'<tr data-record-id="{rid}">' + "".join(f"<td>{esc(row.get(c, ''))}</td>" for c in cols) + "</tr>"
                      for rid, row in updates.items())
        trs += "".join("<tr>" + "".join(f"<td>{esc(row.get(c, ''))}</td>" for c in cols) + "</tr>" for row in creates)
        parts.append(f'<foreignObject data-type="kanban" data-miro-id="{cfg["kanban_id"]}"><table><thead><tr>{ths}</tr></thead><tbody>{trs}</tbody></table></foreignObject>')
    if (idea_updates or idea_deletes) and cfg.get("ideas_id"):
        itf = mirror["ideas_fields"]
        cols = [c for c in IDEA_COLUMNS if c in itf]
        ths = "".join(f'<th data-field-id="{itf[c]}">{esc(c)}</th>' for c in cols)
        trs = "".join(f'<tr data-record-id="{rid}">' + "".join(f"<td>{esc(row.get(c, ''))}</td>" for c in cols) + "</tr>"
                      for rid, row in idea_updates.items())
        trs += "".join(f'<tr data-record-id="{rid}" data-deleted="true"/>' for rid in idea_deletes)
        parts.append(f'<foreignObject data-type="table" data-miro-id="{cfg["ideas_id"]}"><table><thead><tr>{ths}</tr></thead><tbody>{trs}</tbody></table></foreignObject>')

    if not parts:
        BATCH.unlink(missing_ok=True)
        print("build: nothing to send")
        return
    BATCH.write_text("<svg>" + "".join(parts) + "</svg>", encoding="utf-8")
    sent_rows = {rid: {k: v for k, v in row.items() if k != "__files"} for rid, row in updates.items()}
    save(PENDING, {"outbox": used, "idea_files_done": idea_files_done, "idea_deletes": idea_deletes,
                   "sent_rows": sent_rows, "sent_creates": creates})
    print(f"build: kanban updates={len(updates)} creates={len(creates)} idea updates={len(idea_updates)} "
          f"idea deletes={len(idea_deletes)} -> {BATCH}")
    if unresolved:
        print("build: unresolved (task not on board yet, kept for next round): " + ", ".join(unresolved))


def cmd_commit(result_file):
    ensure_dirs()
    pending, mirror = load(PENDING, None), load(MIRROR, {})
    if not pending:
        sys.exit("commit: nothing pending")
    stamp = time.strftime("%Y%m%d-%H%M%S")
    dest = ARCHIVE / stamp
    dest.mkdir(parents=True, exist_ok=True)
    for name in pending["outbox"]:
        if (OUTBOX / name).exists():
            shutil.move(str(OUTBOX / name), str(dest / name))
    for name in pending["idea_files_done"]:
        if (IDEAS / name).exists():
            shutil.move(str(IDEAS / name), str(dest / name))
    kanban = mirror.setdefault("kanban", {})
    for rid, row in pending.get("sent_rows", {}).items():
        kanban.setdefault(rid, {}).update(row)
    # New rows: record ids come from the update result, either a saved result file or
    # "T73=<record-id>,T74=<record-id>" pairs copied from result_svg.
    new_ids = {}
    if result_file and Path(result_file).exists():
        tables = parse_tables(Path(result_file).read_text(encoding="utf-8"))
        kb = tables.get(load(CONFIG, {}).get("kanban_id"))
        if kb and kb["fields"]:
            for rid, cells in kb["rows"].items():
                row = to_dict(kb["fields"], cells)
                new_ids[row.get("Title", "").split(" ")[0]] = rid
    elif result_file:
        for pair in result_file.split(","):
            if "=" in pair:
                t, rid = pair.split("=", 1)
                new_ids[t.strip()] = rid.strip()
    for row in pending.get("sent_creates", []):
        task = row.get("Title", "").split(" ")[0]
        if task in new_ids:
            kanban[new_ids[task]] = dict(row)
        else:
            print(f"commit: no record id given for new card {task}; pass it as {task}=<record-id>")
    for rid in pending["idea_deletes"]:
        mirror.get("ideas", {}).pop(rid, None)
    save(MIRROR, mirror)
    PENDING.unlink(missing_ok=True)
    print(f"commit: archived to {dest}")


def cmd_status():
    ensure_dirs()
    print(f"outbox: {len(list(OUTBOX.glob('*.json')))} pending card changes")
    for f in sorted(IDEAS.glob("IDEA-*.json")):
        i = load(f, {})
        print(f"idea {f.name}: {i.get('status')} | {i.get('idea')[:60]} | todos={i.get('created_todos')}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    {"ingest": lambda: cmd_ingest(sys.argv[2]), "build": cmd_build,
     "commit": lambda: cmd_commit(sys.argv[2] if len(sys.argv) > 2 else None),
     "status": cmd_status}[cmd]()
