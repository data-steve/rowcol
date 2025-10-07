#!/usr/bin/env python3
# dev/agent/auto.py
import json
import subprocess
import shlex
import time
from pathlib import Path
import yaml  # Requires pyyaml

RUNS = Path("dev/agent/runs")
RUNS.mkdir(parents=True, exist_ok=True)

def run(cmd):
    """Execute a command and capture output."""
    p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    lines = []
    for ln in p.stdout:
        print(ln, end="")
        lines.append(ln.rstrip())
    return p.wait(), lines

def compact(lines, keep=50):
    """Compact long output for storage."""
    if len(lines) <= keep:
        return lines
    return lines[:20] + ["...<snip>..."] + lines[-30:]

def record(step, cmd, code, out):
    """Record command execution for debugging."""
    ts = time.strftime("%Y%m%d-%H%M%S")
    f = RUNS / f"{ts}-{step}.json"
    f.write_text(json.dumps({"ts": ts, "step": step, "cmd": cmd, "code": code, "out": compact(out)}, indent=2))
    print(f"[AUTO] wrote {f}")

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--taskfile", default="dev/agent/TASK.md")
    args = ap.parse_args()
    
    task_path = Path(args.taskfile)
    if not task_path.exists():
        print(f"[AUTO] Error: {args.taskfile} not found.")
        exit(1)

    try:
        # Read the YAML front matter from the task file
        content = task_path.read_text()
        if '---' not in content:
            print("[AUTO] Error: No YAML front matter found in task file.")
            exit(1)
            
        yaml_content = content.split('---')[1]
        front_matter = yaml.safe_load(yaml_content)
        plan = front_matter.get("plan", {})
    except Exception as e:
        print(f"[AUTO] Error parsing task file: {e}")
        exit(1)

    print(f"[AUTO] Executing plan for task: {front_matter.get('task_id', 'unknown')}")
    
    # Execute tests
    tests = plan.get("tests", [])
    for i, test_cmd in enumerate(tests):
        print(f"[AUTO] Running test {i+1}: {test_cmd}")
        code, out = run(test_cmd)
        record(f"test-{i+1}", test_cmd, code, out)
        if code != 0:
            print(f"[AUTO] Test failed with exit code {code}")
            break
    
    # Execute verification
    verifications = plan.get("verification", [])
    for i, verify_cmd in enumerate(verifications):
        print(f"[AUTO] Running verification {i+1}: {verify_cmd}")
        code, out = run(verify_cmd)
        record(f"verify-{i+1}", verify_cmd, code, out)
        if code != 0:
            print(f"[AUTO] Verification failed with exit code {code}")
            break
    
    print("[AUTO] Execution complete")

if __name__ == "__main__":
    main()