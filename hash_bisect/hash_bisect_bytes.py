#!/usr/bin/env python3
"""
Interactive binary search hash comparison.

Run this on BOTH systems with the SAME file offsets/answers.
At each step it hashes a chunk of the file and shows you the hash.
Compare the hash printed on system A with the hash printed on system B.
Answer 'y' if they match, 'n' if they don't, and the script will narrow
down the search until it isolates the smallest differing region.

Usage:
    python3 hash_bisect.py /path/to/file

You can also run it non-interactively per-step if you prefer to script
the comparison, using --start/--end/--auto (see --help).
"""

import argparse
import hashlib
import os
import sys


def hash_range(path, start, end, chunk_size=1024 * 1024):
    """Hash bytes in [start, end) of the file at path."""
    h = hashlib.sha256()
    remaining = end - start
    with open(path, "rb") as f:
        f.seek(start)
        while remaining > 0:
            to_read = min(chunk_size, remaining)
            data = f.read(to_read)
            if not data:
                break
            h.update(data)
            remaining -= len(data)
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
    file_size = os.path.getsize(path)
    print(f"File: {path}")
    print(f"Size: {file_size} bytes")
    print(f"Searching range: [{start}, {end})\n")

    round_num = 0
    while end - start > 1:
        round_num += 1
        mid = start + (end - start) // 2

        # Hash the first half of the current range
        h = hash_range(path, start, mid)
        length = mid - start

        print(f"--- Round {round_num} ---")
        print(f"Range:  [{start}, {mid})  (length {length} bytes)")
        print(f"SHA256: {h}")

        match = ask_yes_no("Does this hash match the other system? (y/n): ")

        if match:
            # First half matches -> difference is in second half
            start = mid
        else:
            # First half differs -> difference is in this half
            end = mid

        print(f"Narrowed to: [{start}, {end})  ({end - start} bytes remaining)\n")

    print("=" * 50)
    if end - start == 1:
        print(f"Difference isolated to single byte at offset {start}.")
        with open(path, "rb") as f:
            f.seek(start)
            b = f.read(1)
        print(f"Byte value on this system: {b!r} (0x{b.hex()})")
    else:
        print(f"Range collapsed with no difference found: [{start}, {end})")
    print("=" * 50)


def auto_step(path, start, end):
    """Non-interactive: just print the hash of the first half and the split point."""
    mid = start + (end - start) // 2
    h = hash_range(path, start, mid)
    print(f"range=[{start},{end}) mid={mid} first_half_hash={h}")


def main():
    parser = argparse.ArgumentParser(description="Interactive binary-search hash diff tool")
    parser.add_argument("file", help="Path to the file to hash")
    parser.add_argument("--start", type=int, default=0, help="Start offset (default 0)")
    parser.add_argument("--end", type=int, default=None, help="End offset (default: file size)")
    parser.add_argument(
        "--auto-step",
        action="store_true",
        help="Print hash of first half of range and exit (for scripted use instead of interactive prompts)",
    )
    args = parser.parse_args()

    if not os.path.isfile(args.file):
        print(f"Error: {args.file} is not a valid file", file=sys.stderr)
        sys.exit(1)

    file_size = os.path.getsize(args.file)
    start = args.start
    end = args.end if args.end is not None else file_size

    if start < 0 or end > file_size or start >= end:
        print(f"Error: invalid range [{start}, {end}) for file of size {file_size}", file=sys.stderr)
        sys.exit(1)

    if args.auto_step:
        auto_step(args.file, start, end)
    else:
        interactive_bisect(args.file, start, end)


if __name__ == "__main__":
    main()
