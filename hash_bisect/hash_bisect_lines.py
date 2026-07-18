#!/usr/bin/env python3
"""
Interactive binary search hash comparison - LINE BASED.

Run this on BOTH systems with the SAME answers at each step.
At each round it hashes the first half of the current line range and
shows you the MD5 hash. Compare the hash printed on system A with the
hash printed on system B. Answer 'y' if they match, 'n' if they don't,
and the script will narrow down the search until it isolates the
smallest differing line (or range of lines).

Usage:
    python3 hash_bisect.py /path/to/file.txt
"""

import argparse
import hashlib
import os
import sys


def read_lines(path):
    """Read all lines from the file, keeping line endings as-is."""
    with open(path, "rb") as f:
        return f.readlines()


def hash_lines(lines, start, end):
    """MD5 hash of lines[start:end] concatenated."""
    h = hashlib.md5()
    for line in lines[start:end]:
        h.update(line)
    return h.hexdigest()


def ask_yes_no(prompt):
    while True:
        resp = input(prompt).strip().lower()
        if resp in ("y", "yes"):
            return True
        if resp in ("n", "no"):
            return False
        print("Please answer y or n.")


def interactive_bisect(path, start, end):
    lines = read_lines(path)
    total_lines = len(lines)
    print(f"File: {path}")
    print(f"Total lines: {total_lines}")
    print(f"Searching line range: [{start}, {end})  (0-indexed, end exclusive)\n")

    round_num = 0
    while end - start > 1:
        round_num += 1
        mid = start + (end - start) // 2

        h = hash_lines(lines, start, mid)
        length = mid - start

        print(f"--- Round {round_num} ---")
        print(f"Lines:  [{start}, {mid})  (line numbers {start + 1}-{mid}, {length} lines)")
        print(f"MD5:    {h}")

        match = ask_yes_no("Does this hash match the other system? (y/n): ")

        if match:
            start = mid
        else:
            end = mid

        print(f"Narrowed to: [{start}, {end})  ({end - start} lines remaining)\n")

    print("=" * 50)
    if end - start == 1:
        line_num = start + 1
        print(f"Difference isolated to line {line_num}.")
        content = lines[start].decode("utf-8", errors="replace").rstrip("\n").rstrip("\r")
        print(f"Content on this system: {content!r}")
    else:
        print(f"Range collapsed with no difference found: [{start}, {end})")
    print("=" * 50)


def auto_step(path, start, end):
    """Non-interactive: print the hash of the first half and the split point."""
    lines = read_lines(path)
    mid = start + (end - start) // 2
    h = hash_lines(lines, start, mid)
    print(f"range=[{start},{end}) mid={mid} first_half_md5={h}")


def main():
    parser = argparse.ArgumentParser(description="Interactive binary-search line/MD5 diff tool")
    parser.add_argument("file", help="Path to the text file to hash")
    parser.add_argument("--start", type=int, default=0, help="Start line index, 0-based (default 0)")
    parser.add_argument("--end", type=int, default=None, help="End line index, exclusive (default: total lines)")
    parser.add_argument(
        "--auto-step",
        action="store_true",
        help="Print hash of first half of range and exit (for scripted use instead of interactive prompts)",
    )
    args = parser.parse_args()

    if not os.path.isfile(args.file):
        print(f"Error: {args.file} is not a valid file", file=sys.stderr)
        sys.exit(1)

    total_lines = len(read_lines(args.file))
    start = args.start
    end = args.end if args.end is not None else total_lines

    if start < 0 or end > total_lines or start >= end:
        print(f"Error: invalid range [{start}, {end}) for file with {total_lines} lines", file=sys.stderr)
        sys.exit(1)

    if args.auto_step:
        auto_step(args.file, start, end)
    else:
        interactive_bisect(args.file, start, end)


if __name__ == "__main__":
    main()
