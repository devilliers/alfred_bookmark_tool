import argparse
import json
import os
import sys

bookmark_item_template = {
    "date_added": "13366903973098408",
    "date_last_used": "0",
    "guid": "7a2651e9-6148-4cae-adcf-902ed0ca556d",
    "id": "989",
    "meta_info": {"power_bookmark_meta": ""},
    "name": "",
    "type": "url",
    "url": "",
}

item = {
    "title": "",
    "subtitle": "",
    "arg": "",
}


def parse_arguments():
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Add a new bookmark to Chrome bookmarks",
    )
    parser.add_argument("method", type=str, help="Add or remove bookmark")
    parser.add_argument("name", nargs="?", type=str, help="Name of the bookmark")
    parser.add_argument("url", nargs="?", type=str, help="URL of the bookmark")
    cli_args = parser.parse_args()
    return cli_args


def update_bookmark_json(current_bookmarks, new_bookmarks):
    current_bookmarks["roots"]["bookmark_bar"]["children"][1]["children"][0][
        "children"
    ] = new_bookmarks
    return current_bookmarks


def _list_bookmarks(current_bookmarks):
    return current_bookmarks["roots"]["bookmark_bar"]["children"][1]["children"][0][
        "children"
    ]


def insert_new_bookmark(current_bookmarks_json, cli_args):
    bookmarks: list = _list_bookmarks(current_bookmarks_json)
    bookmark_item_template["name"] = cli_args.name
    bookmark_item_template["url"] = cli_args.url
    bookmarks.append(bookmark_item_template)
    new_bookmarks = update_bookmark_json(current_bookmarks_json, bookmarks)
    return new_bookmarks


def list_bookmarks(file_path):
    alfred_payload = {"items": []}
    with open(file_path) as file:
        current_bookmarks_json = json.load(file)
        current_bookmarks = _list_bookmarks(current_bookmarks_json)
        for bm in current_bookmarks:
            item = {
                "title": "",
                "subtitle": "",
                "arg": "",
            }
            item["title"] = bm["name"]
            item["subtitle"] = bm["name"]
            item["arg"] = bm["name"]
            alfred_payload["items"].append(item)
    return alfred_payload


def add_bookmark(file_path, cli_args):
    with open(file_path, "r+") as file:
        current_bookmarks_json = json.load(file)
        new_bookmarks_json = insert_new_bookmark(current_bookmarks_json, cli_args)
        file.seek(0)
        json.dump(new_bookmarks_json, file, indent=2)


def remove_bookmark(file_path, cli_args):
    with open(file_path, "r+") as file:
        current_bookmarks_json = json.load(file)
        current_bookmarks = _list_bookmarks(current_bookmarks_json)
        new_bookmarks = [
            bm for bm in current_bookmarks if cli_args.name not in bm["name"]
        ]
        new_bookmarks_json = update_bookmark_json(
            current_bookmarks_json,
            new_bookmarks,
        )
        file.seek(0)
        file.truncate(0)
        json.dump(new_bookmarks_json, file, indent=2)


def main():
    file_path = os.environ["BOOKMARKS_FILE_PATH"]
    cli_args = parse_arguments()

    if cli_args.method == "add":
        add_bookmark(file_path, cli_args)
    elif cli_args.method == "remove":
        remove_bookmark(file_path, cli_args)
    elif cli_args.method == "list":
        bookmarks = list_bookmarks(file_path)
        json.dump(bookmarks, sys.stdout, indent=2)
    else:
        raise Exception(
            f"Method not recognised; use add or remove. Method passed: {cli_args.method}",
        )
        os.exit(1)


if __name__ == "__main__":
    main()
