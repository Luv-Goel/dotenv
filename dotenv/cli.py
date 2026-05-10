"""Dotenv CLI."""

import argparse
import sys
import os

from . import __version__
from .core import load_env, check_env, generate_template, merge_envs, diff_envs, format_env, get_variables


def main():
    parser = argparse.ArgumentParser(prog="dotenv", description=".env file toolkit")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("load", help="Parse and display .env contents")
    p.add_argument("file", nargs="?", default=".env")

    p = sub.add_parser("check", help="Check .env for issues")
    p.add_argument("file", nargs="?", default=".env")

    p = sub.add_parser("template", help="Generate .env.example")
    p.add_argument("file", nargs="?", default=".env")
    p.add_argument("-o", "--output", default=".env.example")

    p = sub.add_parser("merge", help="Merge two .env files")
    p.add_argument("primary")
    p.add_argument("secondary")
    p.add_argument("-o", "--output", default=None)

    p = sub.add_parser("diff", help="Diff two .env files")
    p.add_argument("file_a")
    p.add_argument("file_b")

    p = sub.add_parser("sort", help="Sort .env file alphabetically")
    p.add_argument("file", nargs="?", default=".env")
    p.add_argument("-o", "--output", default=None)

    args = parser.parse_args()

    if args.command in ("load", "check", "template", "sort"):
        if not os.path.exists(args.file):
            print(f"[ERR] File not found: {args.file}", file=sys.stderr)
            sys.exit(1)

        entries = load_env(args.file)
        vars_dict = get_variables(entries)

        if args.command == "load":
            print(f"[OK] {len(entries)} lines, {len(vars_dict)} variables")
            for k, v in sorted(vars_dict.items()):
                display = v[:60] + "..." if len(v) > 60 else v
                print(f"  {k}={display}")

        elif args.command == "check":
            issues = check_env(entries)
            if issues:
                print(f"[ISSUES] {len(issues)} found:")
                for issue in issues:
                    print(f"  {issue}")
            else:
                print("[OK] No issues found")

        elif args.command == "template":
            tmpl = generate_template(entries)
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(tmpl)
            print(f"[OK] Template written to {args.output}")

        elif args.command == "sort":
            out = format_env(entries, sort=True)
            out_path = args.output or args.file
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(out)
            print(f"[OK] Sorted {len(vars_dict)} variables to {out_path}")

    elif args.command == "merge":
        if not os.path.exists(args.primary):
            print(f"[ERR] File not found: {args.primary}", file=sys.stderr)
            sys.exit(1)
        if not os.path.exists(args.secondary):
            print(f"[ERR] File not found: {args.secondary}", file=sys.stderr)
            sys.exit(1)
        primary = load_env(args.primary)
        secondary = load_env(args.secondary)
        merged = merge_envs(primary, secondary)
        out = format_env(merged)
        out_path = args.output or f"{args.primary}.merged"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(out)
        print(f"[OK] Merged {len(get_variables(merged))} variables to {out_path}")

    elif args.command == "diff":
        if not os.path.exists(args.file_a):
            print(f"[ERR] File not found: {args.file_a}", file=sys.stderr)
            sys.exit(1)
        if not os.path.exists(args.file_b):
            print(f"[ERR] File not found: {args.file_b}", file=sys.stderr)
            sys.exit(1)
        a_entries = load_env(args.file_a)
        b_entries = load_env(args.file_b)
        diffs = diff_envs(a_entries, b_entries)
        if diffs:
            for d in diffs:
                if d["type"] == "added":
                    print(f"  + {d['key']}={d['value']}")
                elif d["type"] == "removed":
                    print(f"  - {d['key']}={d['value']}")
                elif d["type"] == "changed":
                    print(f"  ~ {d['key']}: '{d['old']}' -> '{d['new']}'")
        else:
            print("[OK] Files are identical")


if __name__ == "__main__":
    main()
