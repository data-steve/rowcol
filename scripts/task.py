#!/usr/bin/env python3
import argparse
import datetime
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
TASK_FILE = ROOT / "dev/agent/TASK.md"
TEMPLATE_FILE = ROOT / "dev/agent/task_template.md"
ARCHIVE_DIR = ROOT / "dev/agent/archive"

def slugify(text):
    return "".join(c for c in text.lower().replace(" ", "-") if c.isalnum() or c == "-")[:40]

def _get_task_id_from_file():
    if not TASK_FILE.exists():
        return None, None
    content = TASK_FILE.read_text()
    for line in content.splitlines():
        if line.startswith("task_id:"):
            task_id = line.split(":", 1)[1].strip()
            return task_id, content
    return None, content

def create_task(description: str):
    if not TEMPLATE_FILE.exists():
        print(f"Error: Template file not found at {TEMPLATE_FILE}", file=sys.stderr)
        sys.exit(1)

    template = TEMPLATE_FILE.read_text()
    timestamp = datetime.datetime.utcnow().isoformat() + "Z"
    task_id = f"{slugify(description)}-{datetime.datetime.utcnow().strftime('%Y-%m-%d')}"
    
    content = template.replace("{{task_id}}", task_id)
    content = content.replace("{{objective}}", description)
    content = content.replace("{{timestamp}}", timestamp)
    
    TASK_FILE.write_text(content)
    print(f"Created task: {task_id}")
    print(f"File: {TASK_FILE}")

def archive_task():
    task_id, content = _get_task_id_from_file()
    if not task_id:
        print("No active task to archive", file=sys.stderr)
        sys.exit(1)
    
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    archive_file = ARCHIVE_DIR / f"{task_id}.md"
    archive_file.write_text(content)
    TASK_FILE.unlink()
    
    print(f"Archived task {task_id} to {archive_file}")

def main():
    parser = argparse.ArgumentParser(description="Manage agent tasks")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new task")
    create_parser.add_argument("description", help="Task description")
    
    # Archive command
    archive_parser = subparsers.add_parser("archive", help="Archive the current task")
    
    args = parser.parse_args()
    
    if args.command == "create":
        create_task(args.description)
    elif args.command == "archive":
        archive_task()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()