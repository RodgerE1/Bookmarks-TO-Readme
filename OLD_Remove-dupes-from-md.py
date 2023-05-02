"""
A script to remove duplicate links from a markdown file.
"""

import logging
import argparse
import re
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def read_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.readlines()

def write_file(file_path, lines):
    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

def remove_duplicate_links(file_path):
    try:
        lines = read_file(file_path)

        unique_lines, dupes_count = remove_duplicates(lines)

        write_file(file_path, unique_lines)

        logger.info("Duplicate links removed from %s", file_path)
        print(f"Number of duplicate links removed: {dupes_count}")
    except FileNotFoundError as e:
        logger.error("Error: %s", e)
        print(f"Error: {e}")

def remove_duplicates(lines):
    seen = set()
    unique_lines = []
    dupes_count = 0

    url_pattern = re.compile(r"\((http[s]?://[^\)]+)\)")

    for line in tqdm(lines, desc="Processing lines"):
        match = url_pattern.search(line)
        if not match:
            unique_lines.append(line)
            continue

        url = match.group(1)

        if url not in seen:
            seen.add(url)
            unique_lines.append(line)
        else:
            dupes_count += 1

    return unique_lines, dupes_count

def main():
    parser = argparse.ArgumentParser(description="Remove duplicate links from a file.")
    parser.add_argument("file_path", help="Path of the file containing links.")
    args = parser.parse_args()

    remove_duplicate_links(args.file_path)

