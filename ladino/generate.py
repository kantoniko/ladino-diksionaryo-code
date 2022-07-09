#!/usr/bin/env python

import argparse
import collections
import logging
import os
import sys
import datetime
from yaml import safe_load

import ladino.common
from ladino.load import load_dictionary, load_examples, load_config
from ladino.export import generate_main_page, export_to_html, create_sitemap

ladino.common.start = datetime.datetime.now().replace(microsecond=0)

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dictionary", help="path to directory where we find the dictionary files",
    )
    parser.add_argument(
        "--html", help="path to directory where to generate html files",
    )
    parser.add_argument(
        "--whatsapp", help="path to whatsapp files",
    )
    parser.add_argument(
        "--unafraza", help="path to una fraza files",
    )
    parser.add_argument(
        "--sounds", help="path to sounds repository",
    )
    parser.add_argument(
        "--pages", help="path to fixed pages repository",
    )
    parser.add_argument(
        "--books", help="pathes to repository of a book", nargs="+",
    )
    action = parser.add_mutually_exclusive_group(required=False)
    action.add_argument("--main", action='store_true', help="Create the main page only")
    action.add_argument("--all",  action='store_true', help="Create all the pages")

    parser.add_argument("--log", action="store_true", help="Additional logging")
    parser.add_argument("--pretty", action="store_true", help="Pretty save json files")
    parser.add_argument("--limit", type=int, help="Limit number of words")

    args = parser.parse_args()

    if args.all and not args.dictionary:
        print("\n* If --all is provided we also need --directory\n")
        parser.print_help()
        exit(1)

    if (args.main or args.all) and not args.html:
        print("\n* If either --main or --all are provided we also need --html\n")
        parser.print_help()
        exit(1)

    return args

def main():
    args = get_args()
    if args.log:
        logging.basicConfig(level=logging.INFO)
    logging.info("Start generating Ladino dictionary website")

    if args.main:
        generate_main_page(args.html)

    if args.dictionary:
        path_to_repo = args.dictionary
        config = load_config(path_to_repo)

        dictionary = load_dictionary(config, args.limit, os.path.join(path_to_repo, 'words'))
        extra_examples = load_examples(os.path.join(path_to_repo, 'examples'))
        logging.info(dictionary.count)

    sound_people = {}
    if args.sounds:
        with open(os.path.join(args.sounds, 'people.yaml')) as fh:
            sound_people = safe_load(fh)

    if args.all:
        export_to_html(config, dictionary, extra_examples, sound_people, path_to_repo, args.html, whatsapp=args.whatsapp, unafraza=args.unafraza, pages=args.pages, books=args.books, pretty=args.pretty)
        create_sitemap(args.html)


    end = datetime.datetime.now().replace(microsecond=0)
    logging.info(f"Elapsed time: {(end-ladino.common.start).total_seconds()} sec")


if __name__ == "__main__":
    main()
