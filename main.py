#!/usr/bin/env python3

import argparse
import datetime
import json
import logging
import os
import subprocess
from datetime import datetime
from pathlib import Path


class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    GREY = "\033[90m"

    @staticmethod
    def Background(color: str) -> str:
        return color.replace("[3", "[4", 1)


class CustomFormatter(logging.Formatter):
    time_format = f"{Colors.GREY}%(asctime)s{Colors.RESET}"
    FORMATS = {
        logging.DEBUG: f"{time_format} {Colors.BOLD}{Colors.CYAN}DEBG{Colors.RESET} %(message)s",
        logging.INFO: f"{time_format} {Colors.BOLD}{Colors.GREEN}INFO{Colors.RESET} %(message)s",
        logging.WARNING: f"{time_format} {Colors.BOLD}{Colors.YELLOW}WARN{Colors.RESET} %(message)s",
        logging.ERROR: f"{time_format} {Colors.BOLD}{Colors.RED}ERRR{Colors.RESET} %(message)s",
        logging.CRITICAL: f"{time_format} {Colors.BOLD}{Colors.Background(Colors.RED)}CRIT{Colors.RESET} %(message)s",
    }

    def format(self, record: any) -> str:
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%H:%M")
        return formatter.format(record)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="reads Arc Browser JSON data, converts it to HTML, and writes the output to a specified file."
    )
    parser.add_argument("-s", "--silent", action="store_true", help="silence output")
    parser.add_argument(
        "-o", "--output", type=Path, required=False, help="specify the output file path"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="enable verbose output",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="print the git short hash and commit time",
    )

    args = parser.parse_args()

    if args.silent:
        logging.disable(logging.CRITICAL)
    else:
        setup_logging(args.verbose)

    if args.version:
        commit_hash, commit_time = get_version()
        if commit_hash is None or commit_time is None:
            logging.critical("Could not fetch Git metadata.")
            return
        print(
            f"{Colors.BOLD}GIT TIME{Colors.RESET} | {Colors.GREEN}{commit_time.strftime('%Y-%m-%d')}{Colors.RESET} [{Colors.YELLOW}{int(commit_time.timestamp())}{Colors.RESET}]"
        )
        print(
            f"{Colors.BOLD}GIT HASH{Colors.RESET} | {Colors.MAGENTA}{commit_hash}{Colors.RESET}"
        )
        return

    data: dict = read_json()
    html: str = convert_json_to_html(data)
    write_html(html, args.output)
    logging.info("Done!")


def setup_logging(is_verbose: bool) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(CustomFormatter())
    logging.basicConfig(level=logging.DEBUG, handlers=[handler])

    if is_verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)


def get_version() -> tuple[str, datetime]:
    try:
        commit_hash: str = (
            subprocess.check_output(["git", "rev-parse", "--short", "HEAD"])
            .decode("utf-8")
            .strip()
        )
        commit_time_str: str = (
            subprocess.check_output(["git", "log", "-1", "--format=%ct"])
            .decode("utf-8")
            .strip()
        )
        commit_time = datetime.fromtimestamp(int(commit_time_str))
    except Exception:
        commit_hash = None
        commit_time = None

    return commit_hash, commit_time


def read_json() -> dict:
    logging.info("Reading JSON...")

    filename: Path = Path("StorableSidebar.json")
    if os.name == "nt":
        arc_root_parent_path: Path = Path(
            os.path.expanduser(r"~\AppData\Local\Packages")
        )
        arc_root_paths: list[Path] = [
            f
            for f in arc_root_parent_path.glob("*")
            if f.name.startswith("TheBrowserCompany.Arc")
        ]
        if len(arc_root_paths) != 1:
            raise FileNotFoundError

        library_path: Path = Path(
            arc_root_paths[0].joinpath(r"LocalCache\Local\Arc")
        ).joinpath(filename)

    else:
        library_path: Path = Path(
            os.path.expanduser("~/Library/Application Support/Arc/")
        ).joinpath(filename)

    data: dict = {}

    if filename.exists():
        with filename.open("r", encoding="utf-8") as f:
            logging.debug(f"Found {filename} in current directory.")
            data = json.load(f)

    elif library_path.exists():
        with library_path.open("r", encoding="utf-8") as f:
            logging.debug(f"Found {filename} in Library directory.")
            data = json.load(f)

    else:
        logging.critical(
            '> File not found. Look for the "StorableSidebar.json" '
            '  file within the "~/Library/Application Support/Arc/" folder.'
        )
        raise FileNotFoundError

    return data


def convert_json_to_html(json_data: dict) -> str:
    containers: list = json_data["sidebar"]["containers"]
    try:
        target: int = next(i + 1 for i, c in enumerate(containers) if "global" in c)
    except StopIteration:
        raise ValueError("No container with 'global' found in the sidebar data")

    spaces: dict = get_spaces(json_data["sidebar"]["containers"][target]["spaces"])
    items: list = json_data["sidebar"]["containers"][target]["items"]

    bookmarks: dict = convert_to_bookmarks(spaces, items)
    html_content: str = convert_bookmarks_to_html(bookmarks)

    return html_content


def get_spaces(spaces: list) -> dict:
    logging.info("Getting spaces...")

    spaces_names: dict = {"pinned": {}, "unpinned": {}}
    spaces_count: int = 0
    n: int = 1

    for space in spaces:
        if "title" in space:
            title: str = space["title"]
        else:
            title: str = "Space " + str(n)
            n += 1

        # TODO: Find a better way to determine if a space is pinned or not
        if isinstance(space, dict):
            containers: list = space["newContainerIDs"]

            for i in range(len(containers)):
                if isinstance(containers[i], dict):
                    if "pinned" in containers[i]:
                        spaces_names["pinned"][str(containers[i + 1])]: str = title
                    elif "unpinned" in containers[i]:
                        spaces_names["unpinned"][str(containers[i + 1])]: str = title

            spaces_count += 1

    logging.debug(f"Found {spaces_count} spaces.")

    return spaces_names


def convert_to_bookmarks(spaces: dict, items: list) -> dict:
    logging.info("Converting to bookmarks...")

    bookmarks: dict = {"bookmarks": []}
    bookmarks_count: int = 0
    item_dict: dict = {item["id"]: item for item in items if isinstance(item, dict)}

    def recurse_into_children(parent_id: str) -> list:
        nonlocal bookmarks_count
        children: list = []
        for item_id, item in item_dict.items():
            if item.get("parentID") == parent_id:
                if "data" in item and "tab" in item["data"]:
                    children.append(
                        {
                            "title": item.get("title", None)
                            or item["data"]["tab"].get("savedTitle", ""),
                            "type": "bookmark",
                            "url": item["data"]["tab"].get("savedURL", ""),
                        }
                    )
                    bookmarks_count += 1
                elif "title" in item:
                    child_folder: dict = {
                        "title": item["title"],
                        "type": "folder",
                        "children": recurse_into_children(item_id),
                    }
                    children.append(child_folder)
        return children

    for space_id, space_name in spaces["pinned"].items():
        space_folder: dict = {
            "title": space_name,
            "type": "folder",
            "children": recurse_into_children(space_id),
        }
        bookmarks["bookmarks"].append(space_folder)

    logging.debug(f"Found {bookmarks_count} bookmarks.")

    return bookmarks


def convert_bookmarks_to_html(bookmarks: dict) -> str:
    logging.info("Converting bookmarks to HTML...")

    html_str: str = """<!DOCTYPE NETSCAPE-Bookmark-file-1>
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<TITLE>Bookmarks</TITLE>
<H1>Bookmarks</H1>
<DL><p>"""

    def traverse_dict(d: dict, html_str: str, level: int) -> str:
        indent: str = "\t" * level
        for item in d:
            if item["type"] == "folder":
                html_str += f'\n{indent}<DT><H3>{item["title"]}</H3>'
                html_str += f"\n{indent}<DL><p>"
                html_str = traverse_dict(item["children"], html_str, level + 1)
                html_str += f"\n{indent}</DL><p>"
            elif item["type"] == "bookmark":
                html_str += f'\n{indent}<DT><A HREF="{item["url"]}">{item["title"]}</A>'
        return html_str

    html_str = traverse_dict(bookmarks["bookmarks"], html_str, 1)
    html_str += "\n</DL><p>"

    logging.debug("HTML converted.")

    return html_str


def write_html(html_content: str, output: Path = None) -> None:
    logging.info("Writing HTML...")

    if output is not None:
        output_file: Path = output
    else:
        current_date: str = datetime.now().strftime("%Y_%m_%d")
        output_file: Path = Path("arc_bookmarks_" + current_date).with_suffix(".html")

    with output_file.open("w", encoding="utf-8") as f:
        f.write(html_content)

    logging.debug(f"HTML written to {output_file}.")


if __name__ == "__main__":
    main()
