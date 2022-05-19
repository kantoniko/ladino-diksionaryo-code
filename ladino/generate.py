#!/usr/bin/env python

import argparse
import collections
import logging
import os
import sys
import datetime

import ladino.common
from ladino.load import load_dictionary, load_examples, load_config
from ladino.export import generate_main_page, export_to_html, export_whatsapp, create_sitemap

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
        "--sounds", help="path to sounds repository",
    )
    action = parser.add_mutually_exclusive_group(required=False)
    action.add_argument("--main", action='store_true', help="Create the main page only")
    action.add_argument("--all",  action='store_true', help="Create all the pages")

    parser.add_argument("--log", action="store_true", help="Additional logging")
    parser.add_argument("--pretty", action="store_true", help="Pretty save json files")

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

        dictionary = load_dictionary(config, os.path.join(path_to_repo, 'words'))
        extra_examples = load_examples(os.path.join(path_to_repo, 'examples'))
        logging.info(dictionary.count)

    sounds = None
    #if args.sounds:
    #    sys.path.insert(0, args.sounds)
    #    from ladino.sounds import load_sounds
    #    sounds = load_sounds()
    #print(sounds)

    if args.all:
        export_to_html(config, dictionary, extra_examples, sounds, path_to_repo, args.html, pretty=args.pretty)
        if args.whatsapp:
            sys.path.insert(0, args.whatsapp)
            import ladino.whatsapeando as whatsapp
            messages = whatsapp.get_messages()
            #print(messages)
            export_whatsapp(messages, dictionary.pages['ladino'], args.html)
        create_sitemap(args.html)


    end = datetime.datetime.now().replace(microsecond=0)
    logging.info(f"Elapsed time: {(end-ladino.common.start).total_seconds()} sec")


if __name__ == "__main__":
    main()
