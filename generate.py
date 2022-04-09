#!/usr/bin/env python

import argparse
import collections
import copy
import glob
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

lili_repository_url = 'https://github.com/szabgab/LibreLingo-Judeo-Spanish-from-English'

class LadinoError(Exception):
    pass


languages = ['english', 'french', 'hebrew', 'spanish', 'turkish', 'portuguese']

def parse_skill_path(path):
    match = re.search(r"^([a-zA-Z0-9-]+)/skills/([a-zA-Z0-9_-]+)\.yaml$", path)
    if not match:
        raise LadinoError(f"unrecoginized skill path: '{path}'")
    return match


def render(template_file, **args):
    root = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(root, "templates")
    env = Environment(loader=FileSystemLoader(templates_dir), autoescape=True)
    env.filters["yaml2html"] = lambda path: re.sub(r"\.yaml$", ".html", path)
    template = env.get_template(template_file)
    html = template.render(**args)
    return html

def export_dictionary_pages(pages, html_dir):
    logging.info("Export dictionary pages")
    words_dir = os.path.join(html_dir, 'words')
    os.makedirs(words_dir, exist_ok=True)
    branch = "main"
    #for language, words in pages.items():
    #if not words:
    #    continue
    language = 'ladino'
    words = pages['ladino']
    language_dir = os.path.join(words_dir, language)
    logging.info(f"Export dictionary pages of {language} to {language_dir}")
    os.makedirs(language_dir, exist_ok=True)
    for word, data in words.items():
        filename = f'{word}.html'
        logging.info(f"Export to {filename}")
        #logging.info(f"Export to {data}")
        html = render(
            "dictionary_word.html",
            data=data,
            title=f"{word}",
            word=word,
        )
        with open(os.path.join(words_dir, language, filename), "w") as fh:
            fh.write(html)
        export_json(data, os.path.join(words_dir, language, f'{word}.json'))

    html = render(
        "dictionary_words.html",
        title=f"{language}",
        words=sorted(words.keys()),
    )
    with open(os.path.join(words_dir, language, 'index.html'), "w") as fh:
        fh.write(html)

    html = render(
        "dictionary_languages.html",
        title=f"Languages",
        languages=sorted(languages),
    )
    with open(os.path.join(words_dir, 'index.html'), "w") as fh:
        fh.write(html)


def export_about_html_page(count, html_dir):
    logging.info("Export about html page")

    html = render(
        "about.html",
        title=f"Ladino dictionary - about",
        page="index",
        count=count,
        languages=languages,
    )
    with open(os.path.join(html_dir, "about.html"), "w") as fh:
        fh.write(html)


def export_main_html_page(html_dir):
    logging.info("Export main html page")

    html = render(
        "converter.html",
        title=f"Ladino dictionary",
        page="converter",
    )
    with open(os.path.join(html_dir, "index.html"), "w") as fh:
        fh.write(html)

def export_skill_html_pages(course, html_dir):
    logging.info("Export skill html pages")
    branch = "main"  # how can we know which is the default branch of a repository?
    for module in course.modules:
        for skill in module.skills:
            html = render(
                "skill.html",
                title=f"Ladino for English speakers",
                branch=branch,
                skill=skill,
                repository_url=lili_repository_url,
            )
            match = parse_skill_path(skill.filename)
            module_name = match.group(1)
            file_name = match.group(2)
            dir_path = os.path.join(html_dir, "course", module_name, "skills")
            # print(dir_path)
            os.makedirs(dir_path, exist_ok=True)
            # filename = skillurl_filter(skill.filename)
            with open(os.path.join(dir_path, file_name + ".html"), "w") as fh:
                fh.write(html)


def export_json(all_words, filename, pretty=False):
    with open(filename, "w") as fh:
        if pretty:
            json.dump(all_words, fh, indent=4, ensure_ascii=False, sort_keys=True)
        else:
            json.dump(all_words, fh, ensure_ascii=False, sort_keys=True)


def export_words_html_page(all_words, language, path, html_file):
    logging.info("Export words html page")
    html = render(
        "words.html",
        title=f"Ladino for English words",
        page=path,
        path=path,
        all_words=all_words,
        dictionary=language["dictionary"],
        phrases=language["phrases"],
    )
    with open(html_file, "w") as fh:
        fh.write(html)


def export_word_html_pages(all_words, language, words_dir):
    logging.info("Export word html page")
    branch = "main"

    for target_word in all_words:
        html = render(
            "word.html",
            title=f"{target_word} in Ladino",
            target_word=target_word,
            word_translations=language["words"][target_word],
            dictionary_words=language["dictionary"][target_word],
            phrases=language["phrases"][target_word],
            repository_url=lili_repository_url,
            branch=branch,
        )
        with open(os.path.join(words_dir, target_word.lower() + ".html"), "w") as fh:
            fh.write(html)

def remove_previous_content_of(html_dir):
    for thing in glob.glob(os.path.join(html_dir, '*')):
        if os.path.isdir(thing):
            shutil.rmtree(thing) # TODO remove all the old content from html_dir
        else:
            os.remove(thing)

def export_to_html(course, target, source, dictionary, count, pages, html_dir, pretty=False):
    logging.info("Export to HTML")
    root = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(html_dir, exist_ok=True)
    remove_previous_content_of(html_dir)

    shutil.copytree(os.path.join(root, "js"), os.path.join(html_dir, "js"))


    export_json(dictionary, os.path.join(html_dir, "dictionary.json"), pretty=pretty)
    export_main_html_page(html_dir)
    export_dictionary_pages(pages, html_dir)

    if course:
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

        for path in ["target", "source"]:
            words_dir = os.path.join(html_dir, path)
            os.makedirs(words_dir, exist_ok=True)
        export_json(collect_words(source, "source-to-target"), os.path.join(html_dir, "source-to-target.json"), pretty=pretty)
        export_json(collect_words(target, "target-to-source"), os.path.join(html_dir, "target-to-source.json"), pretty=pretty)

        export_skill_html_pages(course, html_dir)
        export_words_html_page(
            all_target_words,
            target,
            "target",
            os.path.join(html_dir, "target.html"),
        )
        export_words_html_page(
            all_source_words,
            source,
            "source",
            os.path.join(html_dir, "source.html"),
        )
        export_word_html_pages(
            all_target_words, target, os.path.join(html_dir, "target")
        )
        export_word_html_pages(
            all_source_words, source, os.path.join(html_dir, "source")
        )
    export_about_html_page(count, html_dir)
    export_json(count, os.path.join(html_dir, "count.json"), pretty=pretty)


def clean(text):
    return re.sub(r'[{}.!?¡¿",/]', "", text)

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

    pages = collect_data_from_dictionary(dictionary_source, dictionary, count)
    if course:
        collect_data_from_course(course, target, source, dictionary, count)

    return target, source, dictionary, count, pages

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

def _make_it_list(target_words, filename):
    if target_words.__class__.__name__ == 'str':
        if target_words == '':
            return []
        else:
            return [target_words]
    elif target_words.__class__.__name__ == 'list':
        return target_words
    else:
        raise LadinoError(f"bad type {target_words.__class__.__name__} for {translations} in '{filename}'")


def _make_them_list(translations, filename):
    for language in languages:
        if language not in translations:
            continue
        translations[language] = _make_it_list(translations[language], filename)

def check_categories(config, data, filename):
    if 'categories' not in data:
        return
    for cat in data['categories']:
        if cat not in config['kategorias']:
            raise LadinoError(f"Invalid category '{cat}' in file '{filename}'")

def load_dictionary(config, path_to_dictionary):
    logging.info(f"Path to dictionary: '{path_to_dictionary}'")
    if path_to_dictionary is None:
        return

    files = os.listdir(path_to_dictionary)
    words = []
    for filename in files:
        path = os.path.join(path_to_dictionary, filename)
        logging.info(path)
        with open(path) as fh:
            data = safe_load(fh)

        if 'grammar' not in data:
            raise LadinoError(f"The 'grammar' field is missing from file '{filename}'")
        grammar = data['grammar']
        if grammar not in ['adjective', 'adverb', 'noun', 'verb', 'preposition', 'pronoun', None]:
            raise LadinoError(f"Invalid grammar '{grammar}' in file '{filename}'")

        if 'origen' not in data:
            raise LadinoError(f"The 'origen' field is missing from file '{filename}'")
        origen  = data['origen']
        if origen not in ['Jeneral', 'Estanbol', 'Izmir', 'Salonik', 'Balkanes', 'Aki Yerushalayim', 'Torah/Tanah', 'Otros', 'Gresia', 'Ladinokomunita', 'Sarayevo', 'NA']:
            raise LadinoError(f"Invalid origen '{origen}' in file '{filename}'")

        check_categories(config, data, filename)

        if 'versions' not in data:
            raise LadinoError(f"The 'versions' field is missing from file '{filename}'")

        if grammar == 'verb' and 'conjugations' not in data:
            raise LadinoError(f"Grammar is 'verb', but there is NO 'conjugations' field in '{filename}'")
        if grammar != 'verb' and 'conjugations' in data:
            raise LadinoError(f"Grammar is NOT verb, but there are conjugations in {filename}")

        if grammar in ['noun']: # 'adjective',
            for version in data['versions']:
                gender = version.get('gender')
                if gender is None:
                    raise LadinoError(f"The 'gender' field is None in '{filename}' version {version}")
                if gender not in ['feminine', 'masculine']:
                    raise LadinoError(f"Invalid value '{gender}' in 'gender' field in '{filename}' version {version}")
                number = version.get('number')
                if number is None:
                    raise LadinoError(f"The 'number' field is None in '{filename}' version {version}")
                if number not in ['singular', 'plural']:
                    raise LadinoError(f"The 'number' field is '{number}' in '{filename}' version {version}")

        if 'examples' not in data:
            raise LadinoError(f"examples is missing in {filename}")
        examples = data['examples']
        if examples == []:
            examples = None
        comments = data.get('comments')
        if comments == []:
            comments = None

        for version in data['versions']:
            if 'ladino' not in version:
                raise LadinoError(f'Ladino is missing from file {filename}')
            version['source'] = filename

            if 'translations' in version:
                _make_them_list(version['translations'], filename)

            # Add examples and comments to the first version of the word.
            if examples is not None:
                version['examples'] = examples
                examples = None
            if comments is not None:
                version['comments'] = comments
                comments = None
            words.append(version)

        if 'conjugations' in data:
            for verb_time, conjugation in data['conjugations'].items():
                #print(verb_time)
                #print(conjugation)
                for pronoun, version in conjugation.items():
                    if 'ladino' not in version:
                        raise LadinoError(f'Ladino is missing from file {filename}')
                    version['source'] = filename
                    if 'translations' in version:
                        _make_them_list(version['translations'], filename)
                    words.append(version)
    #print(words)
    return words

def _add_word(dictionary, source_language, target_language, source_word, target_words):
    if target_language not in dictionary[source_language][source_word]:
        dictionary[source_language][source_word][target_language] = []
    dictionary[source_language][source_word][target_language].extend(target_words)
    dictionary[source_language][source_word][target_language] = sorted(set(dictionary[source_language][source_word][target_language]))

def _add_ladino_word(original_word, accented_word, dictionary, pages, entry, count):
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
        _add_word(dictionary, source_language, target_language, word, target_words)
    _add_word(dictionary, source_language, 'ladino', word, [original_word])

    if word not in pages[source_language]:
        pages[source_language][word] = []
    pages[source_language][word].append(entry)
    pages[source_language][word].sort(key=lambda x: (x['ladino'], x['translations']['english'][0]))

    if accented_word:
        _add_word(dictionary, source_language, target_language='accented', source_word=word, target_words=[accented_word])

def _add_translated_words(source_language, dictionary, pages, entry, count):
    translations = entry['translations'].get(source_language)
    #print(f"{source_language}: {translations}")
    if translations is None:
        return

    for word in translations:
        if word not in dictionary[source_language]:
            dictionary[source_language][word] = []
        dictionary[source_language][word].append(entry['ladino'])
        dictionary[source_language][word] = sorted(set(dictionary[source_language][word]))
        count['dictionary'][source_language]['words'] += 1

        if word not in pages[source_language]:
            pages[source_language][word] = []
        pages[source_language][word].append(entry)
        pages[source_language][word].sort(key=lambda x: len(json.dumps(x, sort_keys=True)))


def collect_data_from_dictionary(dictionary_source, dictionary, count):
    logging.info("Collect more data")
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
        _add_ladino_word(entry['ladino'], entry.get('accented'), dictionary, pages, entry, count)

        if 'alternative-spelling' in entry:
            for alt_entry in entry['alternative-spelling']:
                _add_ladino_word(alt_entry['ladino'], alt_entry.get('accented'), dictionary, pages, entry, count)

        for language in languages:
            _add_translated_words(language, dictionary, pages, entry, count)

    return pages

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--course", help="path to course directory that contains the course.yaml",
    )
    parser.add_argument(
        "--dictionary", help="path to directory where we find the dictionary files",
        required=True,
    )
    parser.add_argument(
        "--html", help="path to directory where to generate html files",
    )
    parser.add_argument("--log", action="store_true", help="Additional logging")
    args = parser.parse_args()
    return args

def load_config(path_to_repo):
    with open(os.path.join(path_to_repo, 'config.yaml')) as fh:
        return safe_load(fh)

def main():
    start = time.time()
    args = get_args()
    if args.log:
        logging.basicConfig(level=logging.INFO)
    logging.info("Start generating Ladino dictionary website")

    logging.info("Path to course: '%s'", args.course)
    course = load_course(args.course) if args.course else None
    logging.info("Course loaded")
    path_to_repo = args.dictionary
    config = load_config(path_to_repo)
    dictionary_source = load_dictionary(config, os.path.join(path_to_repo, 'words'))

    if args.html:
        target, source, dictionary, count, pages = collect_data(course, dictionary_source)
        logging.info(count)
        export_to_html(course, target, source, dictionary, count, pages, args.html)

    end = time.time()
    logging.info(f"Elapsed time: {int(end-start)} sec")


if __name__ == "__main__":
    main()
