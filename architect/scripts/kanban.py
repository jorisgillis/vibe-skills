#!/usr/bin/env python3
"""Architect kanban tool — manages kanban.db for the architect skill."""

import argparse
import random
import sqlite3
import sys
from datetime import datetime, timezone

DB_PATH = "kanban.db"

WORDS_A = [
    "amber", "azure", "bold", "brave", "bright", "calm", "clear", "cold",
    "crisp", "dark", "deep", "dense", "dry", "dusk", "faint", "fast",
    "firm", "flat", "fleet", "free", "fresh", "full", "grand", "great",
    "hard", "keen", "kind", "lean", "light", "long", "loud", "mild",
    "open", "plain", "prime", "pure", "quick", "quiet", "real", "rich",
    "round", "safe", "sharp", "slim", "slow", "smart", "smooth", "soft",
    "solid", "still", "strong", "swift", "tall", "thin", "true", "warm",
    "wide", "wild", "wise", "young",
]

WORDS_B = [
    "arc", "ash", "bay", "beam", "bird", "blade", "bloom", "bridge",
    "brook", "cloud", "coast", "crest", "dawn", "dune", "dust", "edge",
    "falls", "field", "flame", "flint", "flow", "forge", "frost", "gate",
    "glade", "glen", "grove", "gulf", "hawk", "helm", "hill", "horn",
    "isle", "lake", "leaf", "mast", "mesa", "mill", "mist", "moon",
    "moor", "mount", "oak", "peak", "pine", "pool", "port", "reef",
    "ridge", "rise", "river", "rock", "root", "sail", "shore", "sky",
    "slope", "snow", "star", "stone", "storm", "stream", "vale", "wave",
    "wind", "wood",
]

VALID_STATUSES = {"BACKLOG", "ANALYSIS", "PLANNED", "IN PROGRESS", "REVIEW", "DONE"}

STATUS_ORDER = {s: i for i, s in enumerate(
    ["BACKLOG", "ANALYSIS", "PLANNED", "IN PROGRESS", "REVIEW", "DONE"]
)}


def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            functional_elaboration TEXT,
            functional_acceptance_criteria TEXT,
            board_status TEXT NOT NULL DEFAULT 'BACKLOG',
            version TEXT,
            epic TEXT,
            technical_design TEXT,
            technical_acceptance_criteria TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.commit()


def generate_id(conn):
    for _ in range(100):
        tid = f"{random.choice(WORDS_A)}-{random.choice(WORDS_B)}-{random.randint(1, 99)}"
        if not conn.execute("SELECT 1 FROM tickets WHERE id = ?", (tid,)).fetchone():
            return tid
    raise RuntimeError("Could not generate a unique ticket ID after 100 attempts")


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


# ── commands ──────────────────────────────────────────────────────────────────

def cmd_add(args, conn):
    if args.status and args.status.upper() not in VALID_STATUSES:
        print(f"Invalid status '{args.status}'. Valid: {', '.join(sorted(VALID_STATUSES))}", file=sys.stderr)
        sys.exit(1)
    tid = generate_id(conn)
    conn.execute(
        """INSERT INTO tickets
           (id, name, functional_elaboration, functional_acceptance_criteria,
            board_status, version, epic, technical_design, technical_acceptance_criteria)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            tid,
            args.name,
            args.elaboration,
            args.criteria,
            (args.status.upper() if args.status else "BACKLOG"),
            args.version,
            args.epic,
            args.technical_design,
            args.technical_criteria,
        ),
    )
    conn.commit()
    print(tid)


def cmd_update(args, conn):
    row = conn.execute("SELECT id FROM tickets WHERE id = ?", (args.id,)).fetchone()
    if not row:
        print(f"Ticket '{args.id}' not found.", file=sys.stderr)
        sys.exit(1)

    fields = {}
    if args.name is not None:
        fields["name"] = args.name
    if args.elaboration is not None:
        fields["functional_elaboration"] = args.elaboration
    if args.criteria is not None:
        fields["functional_acceptance_criteria"] = args.criteria
    if args.status is not None:
        s = args.status.upper()
        if s not in VALID_STATUSES:
            print(f"Invalid status '{args.status}'. Valid: {', '.join(sorted(VALID_STATUSES))}", file=sys.stderr)
            sys.exit(1)
        fields["board_status"] = s
    if args.version is not None:
        fields["version"] = args.version
    if args.epic is not None:
        fields["epic"] = args.epic
    if args.technical_design is not None:
        fields["technical_design"] = args.technical_design
    if args.technical_criteria is not None:
        fields["technical_acceptance_criteria"] = args.technical_criteria

    if not fields:
        print("Nothing to update — specify at least one field.", file=sys.stderr)
        sys.exit(1)

    fields["updated_at"] = now()
    set_clause = ", ".join(f"{k} = ?" for k in fields)
    conn.execute(
        f"UPDATE tickets SET {set_clause} WHERE id = ?",
        [*fields.values(), args.id],
    )
    conn.commit()


def cmd_list(args, conn):
    conditions, params = [], []
    if args.status:
        conditions.append("board_status = ?")
        params.append(args.status.upper())
    if args.version:
        conditions.append("version = ?")
        params.append(args.version)

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    rows = conn.execute(
        f"SELECT id, name, board_status, version, epic FROM tickets {where} ORDER BY created_at",
        params,
    ).fetchall()

    if not rows:
        print("(no tickets)")
        return

    for r in rows:
        ver = f"  [{r['version']}]" if r["version"] else ""
        epic = f"  ({r['epic']})" if r["epic"] else ""
        print(f"{r['id']}{ver}{epic}  {r['board_status']}  {r['name']}")


def cmd_show(args, conn):
    r = conn.execute("SELECT * FROM tickets WHERE id = ?", (args.id,)).fetchone()
    if not r:
        print(f"Ticket '{args.id}' not found.", file=sys.stderr)
        sys.exit(1)

    print(f"ID:      {r['id']}")
    print(f"Name:    {r['name']}")
    print(f"Status:  {r['board_status']}")
    if r["version"]:
        print(f"Version: {r['version']}")
    if r["epic"]:
        print(f"Epic:    {r['epic']}")
    if r["functional_elaboration"]:
        print(f"\nFunctional Elaboration:\n{r['functional_elaboration']}")
    if r["functional_acceptance_criteria"]:
        print(f"\nFunctional Acceptance Criteria:\n{r['functional_acceptance_criteria']}")
    if r["technical_design"]:
        print(f"\nTechnical Design:\n{r['technical_design']}")
    if r["technical_acceptance_criteria"]:
        print(f"\nTechnical Acceptance Criteria:\n{r['technical_acceptance_criteria']}")
    print(f"\nCreated: {r['created_at']}  Updated: {r['updated_at']}")


def cmd_summary(args, conn):
    status_rows = conn.execute(
        "SELECT board_status, COUNT(*) AS n FROM tickets GROUP BY board_status"
    ).fetchall()
    counts = {r["board_status"]: r["n"] for r in status_rows}

    print("Status:")
    for s in ["BACKLOG", "ANALYSIS", "PLANNED", "IN PROGRESS", "REVIEW", "DONE"]:
        if s in counts:
            print(f"  {s}: {counts[s]}")

    version_rows = conn.execute(
        "SELECT version, COUNT(*) AS n FROM tickets WHERE version IS NOT NULL GROUP BY version ORDER BY version"
    ).fetchall()
    if version_rows:
        print("\nBy version:")
        for r in version_rows:
            print(f"  {r['version']}: {r['n']}")


# ── CLI wiring ─────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="kanban.py",
        description="Architect kanban tool",
    )
    sub = parser.add_subparsers(dest="command", metavar="command")

    # add
    p = sub.add_parser("add", help="Create a new ticket")
    p.add_argument("--name", required=True, help="Ticket name")
    p.add_argument("--elaboration", default=None, help="Functional elaboration")
    p.add_argument("--criteria", default=None, help="Functional acceptance criteria")
    p.add_argument("--technical-design", default=None, help="Technical design")
    p.add_argument("--technical-criteria", default=None, help="Technical acceptance criteria")
    p.add_argument("--status", default="BACKLOG", help="Initial status (default: BACKLOG)")
    p.add_argument("--version", default=None, help="Target version, e.g. V1")
    p.add_argument("--epic", default=None, help="Epic name for grouping")

    # update
    p = sub.add_parser("update", help="Update a ticket")
    p.add_argument("id", help="Ticket ID")
    p.add_argument("--name", default=None)
    p.add_argument("--elaboration", default=None)
    p.add_argument("--criteria", default=None)
    p.add_argument("--technical-design", default=None)
    p.add_argument("--technical-criteria", default=None)
    p.add_argument("--status", default=None)
    p.add_argument("--version", default=None)
    p.add_argument("--epic", default=None)

    # list
    p = sub.add_parser("list", help="List tickets")
    p.add_argument("--status", default=None, help="Filter by status")
    p.add_argument("--version", default=None, help="Filter by version")

    # show
    p = sub.add_parser("show", help="Show full ticket detail")
    p.add_argument("id", help="Ticket ID")

    # summary
    sub.add_parser("summary", help="Count tickets by status and version")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    conn = connect()
    init_db(conn)

    {"add": cmd_add, "update": cmd_update, "list": cmd_list,
     "show": cmd_show, "summary": cmd_summary}[args.command](args, conn)

    conn.close()


if __name__ == "__main__":
    main()