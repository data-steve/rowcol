import argparse
import os
from engine import AutoCoder, load_rules_yaml, learn_from_corrections

def cmd_autocode(args):
    rules = load_rules_yaml(args.rules)
    coder = AutoCoder(rules)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    coder.autocode(args.input, args.out)
    print(f"[OK] Autocoded -> {args.out}")

def cmd_learn(args):
    learn_from_corrections(args.input, args.rules, args.out, scope="client")
    print(f"[OK] Updated rules -> {args.out}")

def main():
    p = argparse.ArgumentParser(description="Escher Autocode v0.1")
    sub = p.add_subparsers(dest="cmd")

    a = sub.add_parser("autocode", help="Autocode a transactions CSV")
    a.add_argument("input", help="Path to transactions CSV")
    a.add_argument("--rules", required=True, help="Path to rules.yaml")
    a.add_argument("--out", required=True, help="Path to write coded CSV")
    a.set_defaults(func=cmd_autocode)

    l = sub.add_parser("learn", help="Promote corrections to deterministic rules")
    l.add_argument("input", help="Path to corrections CSV")
    l.add_argument("--rules", required=True, help="Path to existing rules.yaml")
    l.add_argument("--out", required=True, help="Path to write updated rules.yaml")
    l.set_defaults(func=cmd_learn)

    args = p.parse_args()
    if not args.cmd:
        p.print_help()
        return
    args.func(args)

if __name__ == "__main__":
    main()
