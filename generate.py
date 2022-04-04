#!/usr/bin/env python
import argparse
import collections
import json
import logging
import os
import re
import shutil
import sys
import time
from yaml import safe_load

import markdown
from jinja2 import Environment, FileSystemLoader
from librelingo_yaml_loader.yaml_loader import load_course

languages = ['english', 'french', 'hebrew', 'spanish', 'turkish', 'portuguese']

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--course", help="path to course directory that contains the course.yaml",
    )
    parser.add_argument(
        "--dictionary", help="path to directory where we find the dictionary files",
    )
    parser.add_argument(
        "--html", help="path to directory where to generate html files",
    )
    parser.add_argument("--log", action="store_true", help="Additional logging")
    args = parser.parse_args()
    return args


def guess_path_to_course(path_to_course):
    if not path_to_course:
        if os.path.exists("course.yaml"):
            path_to_course = "."
        elif os.path.exists(os.path.join("course", "course.yaml")):
            path_to_course = "course"
    return path_to_course


def parse_skill_path(path):
    match = re.search(r"^([a-zA-Z0-9-]+)/skills/([a-zA-Z0-9_-]+)\.yaml$", path)
    if not match:
        raise Exception(f"unrecoginized skill path: '{path}'")
    return match


def skillfile_filter(path):
    match = parse_skill_path(path)
    # return match.group(1) + '/' + match.group(2)
    return match.group(2)


def render(template_file, **args):
    root = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(root, "templates")
    env = Environment(loader=FileSystemLoader(templates_dir), autoescape=True)
    env.filters["skillfile"] = skillfile_filter
    env.filters["yaml2md"] = lambda path: re.sub(r"\.yaml$", ".md", path)
    env.filters["yaml2html"] = lambda path: re.sub(r"\.yaml$", ".html", path)
    env.filters["md2html"] = markdown.markdown
    template = env.get_template(template_file)
    html = template.render(**args)
    return html


def export_main_html_page(course, count, html_dir):
    logging.info("Export main html page")
    branch = "main"  # how can we know which is the default branch of a repository?
    #'count', 'dictionary', 'index', 'license', 'modules', 'repository_url',
    #'settings', 'source_language', 'special_characters', 'target_language'
    # course.modules[0].skills[0].phrases
    # from ptpython.repl import embed
    # embed(globals(), locals())

    html = render(
        "about.html",
        title=f"Ladino dictionary - about",
        page="index",
        course=course,
        count=count,
        languages=languages,
    )
    with open(os.path.join(html_dir, "about.html"), "w") as fh:
        fh.write(html)

    html = render(
        "converter.html",
        title=f"Ladino dictionary",
        page="converter",
        course=course,
    )
    with open(os.path.join(html_dir, "index.html"), "w") as fh:
        fh.write(html)

    html = render(
        "modules.html",
        title=f"{course.target_language.name} for {course.source_language.name} speakers",
        page="modules",
        branch=branch,
        course=course,
        repository_url=get_repository_url(course),
    )
    with open(os.path.join(html_dir, "modules.html"), "w") as fh:
        fh.write(html)

def export_skill_html_pages(course, html_dir):
    logging.info("Export skill html pages")
    branch = "main"  # how can we know which is the default branch of a repository?
    for module in course.modules:
        for skill in module.skills:
            html = render(
                "skill.html",
                title=f"{course.target_language.name} for {course.source_language.name} speakers",
                branch=branch,
                course=course,
                skill=skill,
                repository_url=get_repository_url(course),
            )
            match = parse_skill_path(skill.filename)
            module_name = match.group(1)
            file_name = match.group(2)
            dir_path = os.path.join(html_dir, "course", module_name, "skills")
            # print(dir_path)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            # filename = skillurl_filter(skill.filename)
            with open(os.path.join(dir_path, file_name + ".html"), "w") as fh:
                fh.write(html)


def collect_phrases(course):
    target_to_source = {}
    source_to_target = {}
    for module in course.modules:
        for skill in module.skills:
            for phrase in skill.phrases:
                # print(phrase)
                for sentence in phrase.in_target_language:
                    # if sentence in target_to_source:
                    #    print(f"Same sentence '{sentence}' found twice")
                    target_to_source[sentence] = phrase.in_source_language
                for sentence in phrase.in_source_language:
                    # if sentence in source_to_target:
                    #    print(f"Same sentence '{sentence}' found twice")
                    source_to_target[sentence] = phrase.in_target_language
    return target_to_source, source_to_target


def collect_words(language, direction):
    all_words = {}
    for word, translations in language["words"].items():
        if word not in all_words:
            all_words[word] = []
        for translation in translations:
            if direction == "source-to-target":
                all_words[word].extend(translation["word"].in_target_language)
            else:
                all_words[word].extend(translation["word"].in_source_language)

    for word, translations in language["dictionary"].items():
        if word not in all_words:
            all_words[word] = []
        for translation in translations:
            all_words[word].extend(translation["word"])
    return all_words


def export_json(all_words, filename, pretty=False):
    with open(filename, "w") as fh:
        if pretty:
            json.dump(all_words, fh, indent=4, ensure_ascii=False, sort_keys=True)
        else:
            json.dump(all_words, fh)

def export_words_html_pages(html_dir, dictionary):
    print("---")
    print(dictionary)


def export_words_html_page(course, all_words, language, path, html_file):
    logging.info("Export words html page")
    html = render(
        "words.html",
        title=f"{course.target_language.name} for {course.source_language.name} speakers",
        page=path,
        path=path,
        course=course,
        all_words=all_words,
        words=language["words"],
        dictionary=language["dictionary"],
        phrases=language["phrases"],
    )
    with open(html_file, "w") as fh:
        fh.write(html)

    #    word_class = ""
    #    if len(words[word]) > 1:
    #        word_class = 'warning'
    #    dictionary_class = ""
    #    if len(dictionary[word]) > 1:
    #        dictionary_class = 'warning'
    #    if len(words[word]) == 0 and len(dictionary[word]) == 0:
    #        word_class = 'warning'
    #        dictionary_class = 'warning'


def get_repository_url(course):
    return course.repository_url


def export_word_html_pages(course, all_words, language, words_dir):
    logging.info("Export word html page")
    branch = "main"

    for target_word in all_words:
        html = render(
            "word.html",
            title=f"{target_word} in {course.target_language.name}",
            target_word=target_word,
            word_translations=language["words"][target_word],
            dictionary_words=language["dictionary"][target_word],
            phrases=language["phrases"][target_word],
            repository_url=get_repository_url(course),
            branch=branch,
            course=course,
        )
        with open(os.path.join(words_dir, target_word.lower() + ".html"), "w") as fh:
            fh.write(html)


def export_to_html(course, target, source, dictionary, count, html_dir):
    logging.info("Export to HTML")
    if not os.path.exists(html_dir):
        os.mkdir(html_dir)
    # TODO remove all the old content from html_dir
    shutil.copytree("js", os.path.join(html_dir, "js"))
    for path in ["target", "source"]:
        words_dir = os.path.join(html_dir, path)
        if not os.path.exists(words_dir):
            os.mkdir(words_dir)
    all_target_words = (
        set(target["words"].keys())
        .union(set(target["dictionary"].keys()))
        .union(set(target["phrases"].keys()))
    )
    count["target_words"] = len(all_target_words)

    all_source_words = (
        set(source["words"].keys())
        .union(set(source["dictionary"].keys()))
        .union(set(source["phrases"].keys()))
    )
    count["source_words"] = len(all_source_words)

    logging.info("Export JSON files")
    export_json(collect_words(source, "source-to-target"), os.path.join(html_dir, "source-to-target.json"))
    export_json(collect_words(target, "target-to-source"), os.path.join(html_dir, "target-to-source.json"))
    export_json(dictionary, os.path.join(html_dir, "dictionary.json"))

    export_main_html_page(course, count, html_dir)
    export_skill_html_pages(course, html_dir)
    export_words_html_page(
        course,
        all_target_words,
        target,
        "target",
        os.path.join(html_dir, "target.html"),
    )
    export_words_html_page(
        course,
        all_source_words,
        source,
        "source",
        os.path.join(html_dir, "source.html"),
    )
    export_words_html_pages(html_dir, dictionary)
    export_word_html_pages(
        course, all_target_words, target, os.path.join(html_dir, "target")
    )
    export_word_html_pages(
        course, all_source_words, source, os.path.join(html_dir, "source")
    )
    with open(os.path.join(html_dir, "course.json"), "w") as fh:
        json.dump(count, fh)


def clean(text):
    return re.sub(r'[{}.!?¡¿",/]', "", text)


def _collect_phrases(skill, count, target, source):
    for phrase in skill.phrases:
        for sentence in phrase.in_target_language:
            count["target_phrases"] += 1
            for word in clean(sentence).split(" "):
                target["phrases"][word.lower()].append(
                    {"sentence": sentence, "skill": skill}
                )
        for sentence in phrase.in_source_language:
            count["source_phrases"] += 1
            for word in clean(sentence).split(" "):
                source["phrases"][word.lower()].append(
                    {"sentence": sentence, "skill": skill}
                )


def collect_data(course, dictionary_source):
    count = {
        "target_phrases": 0,
        "source_phrases": 0,
        "target_language_name": course.target_language.name,
        "source_language_name": course.source_language.name,
        "target_language_code": course.target_language.code,
        "source_language_code": course.source_language.code,
    }
    target = {
        "words": collections.defaultdict(list),
        "dictionary": collections.defaultdict(list),
        "phrases": collections.defaultdict(list),
    }
    source = {
        "words": collections.defaultdict(list),
        "dictionary": collections.defaultdict(list),
        "phrases": collections.defaultdict(list),
    }
    dictionary = {}

    collect_data_from_dictionary(dictionary_source, dictionary, count)
    collect_data_from_course(course, target, source, dictionary, count)

    return target, source, dictionary, count

def collect_data_from_course(course, target, source, dictionary, count):
    for module in course.modules:
        for skill in module.skills:
            for word in skill.words:
                for txt in word.in_target_language:
                    target["words"][clean(txt).lower()].append(
                        {"word": word, "skill": skill}
                    )
                for txt in word.in_source_language:
                    source["words"][clean(txt).lower()].append(
                        {"word": word, "skill": skill}
                    )

            for left, right, target_to_source in skill.dictionary:
                if target_to_source:
                    target["dictionary"][clean(left).lower()].append(
                        {"word": right, "skill": skill}
                    )
                else:
                    source["dictionary"][clean(left).lower()].append(
                        {"word": right, "skill": skill}
                    )

            _collect_phrases(skill, count, target, source)

def check_word(filename, data):
    if 'grammar' not in data:
        logging.error("Grammar is missing from file %s", filename)
        return
    #if data['grammar'] == 'noun':
    if 'versions' not in data:
        logging.error('versions are missing from file %s', filename)
    else:
        for version in data['versions']:
            if 'ladino' not in version:
                logging.error('Ladino is missing from file %s', filename)


def load_dictionary(path_to_dictionary):
    logging.info("Path to dictionary: '%s'", path_to_dictionary)
    if path_to_dictionary is None:
        return
    files = os.listdir(path_to_dictionary)
    words = []
    for filename in files:
        path = os.path.join(path_to_dictionary, filename)
        logging.info(path)
        with open(path) as fh:
            data = safe_load(fh)
        check_word(filename, data)
        for version in data['versions']:
            words.append(version)
        if 'conjugations' in data:
            for verb_time, conjugation in data['conjugations'].items():
                print(verb_time)
                print(conjugation)
                for pronoun, version in conjugation.items():
                    words.append(version)
    return words

class Lili:
    def __init__(self):
        self.warnings = []
        self.errors = []

def collect_data_from_dictionary(dictionary_source, dictionary, count):
    logging.info("Collect more data")
    count['dictionary'] = {}
    count['grammar'] = {
        'noun': 0,
        'verb': 0,
        'conjugated-verb': 0,
    }
    for language in ['ladino'] + languages:
        count['dictionary'][language] = {
            'words': 0,
            'phrases': 0,
        }
        dictionary[language] = {}

    for entry in dictionary_source:
        #grammar = entry['grammar']
        #count['grammar'][grammar] += 1
        dictionary['ladino'][ entry['ladino'] ] = entry
        # it is both ok if we overwrite the ladino entry or if we create a new entry
        if 'accented' in entry:
            dictionary['ladino'][ entry['accented'] ] = entry

        count['dictionary']['ladino']['words'] += 1
        if 'alternative-spelling' in entry:
            count['dictionary']['ladino']['words'] += len(entry['alternative-spelling'])
            for alt_entry in entry['alternative-spelling']:
                dictionary['ladino'][ alt_entry['ladino'] ] = entry
                dictionary['ladino'][ alt_entry['accented'] ] = entry

        for language in languages:
            word = entry['translations'].get(language)
            if word is not None and word != '':
                if word.__class__.__name__ == 'str':
                    count['dictionary'][language]['words'] += 1
                elif word.__class__.__name__ == 'list':
                    count['dictionary'][language]['words'] += len(word)
                else:
                    raise Exception(f"Invalid type {word.__class__.__name__}")

def main():
    start = time.time()
    args = get_args()
    if args.log:
        logging.basicConfig(level=logging.INFO)
    logging.info("Start generating Ladino dictionary website")

    path_to_course = guess_path_to_course(args.course)
    logging.info("Path to course: '%s'", path_to_course)
    course = load_course(path_to_course)
    logging.info("Course loaded")
    dictionary_source = load_dictionary(args.dictionary)

    lili = Lili()
    if args.html:
        target, source, dictionary, count = collect_data(course, dictionary_source)
        logging.info(count)
        export_to_html(course, target, source, dictionary, count, args.html)

    if lili.warnings:
        print("------------------ WARNINGS ---------------------")
        for warn in lili.warnings:
            print(warn)

    if lili.errors:
        print("------------------ ERRORS ---------------------")
        for err in lili.errors:
            print(err)
        sys.exit(1)
    end = time.time()
    logging.info(f"Elapsed time: {int(end-start)} sec")


if __name__ == "__main__":
    main()
