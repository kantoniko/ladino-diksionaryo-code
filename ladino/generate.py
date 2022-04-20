#!/usr/bin/env python

import argparse
import collections
import json
import logging
import os
import sys
import datetime

from ladino.common import LadinoError, languages
import ladino.common
from ladino.load import load_dictionary, load_config
from ladino.export import generate_main_page, export_to_html, export_examples,  export_markdown_pages, export_whatsapp
from ladino.export_to_hunspell import export_to_hunspell

ladino.common.start = datetime.datetime.now().replace(microsecond=0)

def add_word(dictionary, source_language, target_language, source_word, target_words):
    if target_language not in dictionary[source_language][source_word]:
        dictionary[source_language][source_word][target_language] = []
    dictionary[source_language][source_word][target_language].extend(target_words)
    dictionary[source_language][source_word][target_language] = sorted(set(dictionary[source_language][source_word][target_language]))

def add_ladino_word(original_word, accented_word, dictionary, pages, entry, count):
    word = original_word.lower()
    logging.info(f"Add ladino word: '{original_word}' '{word}' '{accented_word}'")
    #print(entry)
    count['dictionary']['ladino']['words'] += 1

    for example in entry.get('examples', []):
        if 'ladino' in example:
            count['dictionary']['ladino']['examples'] += 1
    source_language = 'ladino'
    if word not in dictionary[source_language]:
        dictionary[source_language][word] = {}
    for target_language, target_words in entry['translations'].items():
        add_word(dictionary, source_language, target_language, word, target_words)
    add_word(dictionary, source_language, 'ladino', word, [original_word])

    if word not in pages[source_language]:
        pages[source_language][word] = []
    pages[source_language][word].append(entry)
    pages[source_language][word].sort(key=lambda x: (x['ladino'], x['translations']['english'][0]))

    if accented_word:
        add_word(dictionary, source_language, target_language='accented', source_word=word, target_words=[accented_word])

def add_translated_words(source_language, dictionary, pages, entry, count):
    translations = entry['translations'].get(source_language)
    #print(f"{source_language}: {translations}")
    if translations is None:
        return

    for word in translations:
        word = word.lower()
        if word not in dictionary[source_language]:
            dictionary[source_language][word] = []
        dictionary[source_language][word].append(entry['ladino'])
        dictionary[source_language][word] = sorted(set(dictionary[source_language][word]))
        count['dictionary'][source_language]['words'] += 1

        if word not in pages[source_language]:
            pages[source_language][word] = []
        pages[source_language][word].append(entry)
        pages[source_language][word].sort(key=lambda x: len(json.dumps(x, sort_keys=True)))


def collect_data(dictionary_source):
    logging.info("Collect more data")
    count = {}
    dictionary = {}
    #print(dictionary_source)
    count['dictionary'] = {}
    pages = {}
    for language in ['ladino'] + languages:
        count['dictionary'][language] = {
            'words': 0,
            'examples': 0,
        }
        dictionary[language] = {}
        pages[language] = {}

    for entry in dictionary_source:
        add_ladino_word(entry['ladino'], entry.get('accented'), dictionary, pages, entry, count)

        if 'alternative-spelling' in entry:
            for alt_entry in entry['alternative-spelling']:
                add_ladino_word(alt_entry['ladino'], alt_entry.get('accented'), dictionary, pages, entry, count)

        for language in languages:
            add_translated_words(language, dictionary, pages, entry, count)

    return dictionary, count, pages

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

        dictionary_source, all_examples = load_dictionary(config, os.path.join(path_to_repo, 'words'))
        dictionary, count, pages = collect_data(dictionary_source)
        logging.info(count)

    if args.all:
        export_to_html(dictionary, count, pages, args.html, pretty=args.pretty)
        export_examples(all_examples, pages['ladino'], args.html)
        export_markdown_pages(config, path_to_repo, args.html)
        export_to_hunspell(dictionary)
        if args.whatsapp:
            sys.path.insert(0, args.whatsapp)
            import ladino.whatsapeando as whatsapp
            messages = whatsapp.get_messages()
            #print(messages)
            export_whatsapp(messages, pages['ladino'], args.html)


    end = datetime.datetime.now().replace(microsecond=0)
    logging.info(f"Elapsed time: {(end-ladino.common.start).total_seconds()} sec")


if __name__ == "__main__":
    main()
