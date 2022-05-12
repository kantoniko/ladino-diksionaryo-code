import copy
import logging
import os
import glob
import json
import shutil
import re
import datetime

import markdown
from jinja2 import Environment, FileSystemLoader

from ladino.common import languages
import ladino.common
from ladino.export_to_hunspell import export_to_hunspell
from ladino.pdf import create_pdf_dictionaries

sitemap = []

def render(template, filename=None, **args):
    root = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(root, "templates")
    env = Environment(loader=FileSystemLoader(templates_dir), autoescape=True)
    env.filters["yaml2html"] = lambda path: re.sub(r"\.yaml$", ".html", path)
    html_template = env.get_template(template)
    html = html_template.render(**args)
    if filename is not None:
        sitemap.append(filename)
        with open(filename, "w") as fh:
            fh.write(html)
    return html

def export_dictionary_pages(pages, sounds, html_dir):
    logging.info("Export dictionary pages")
    words_dir = os.path.join(html_dir, 'words')
    os.makedirs(words_dir, exist_ok=True)
    #for language, words in pages.items():
    #if not words:
    #    continue
    language = 'ladino'
    words = pages['ladino']
    language_dir = os.path.join(words_dir, language)
    logging.info(f"Export dictionary pages of {language} to {language_dir}")
    os.makedirs(language_dir, exist_ok=True)
    for word, data in words.items():
        enhanced_data = add_links(copy.deepcopy(data), words)
        filename = f'{word}.html'
        logging.info(f"Export to {filename}")
        render(
            template="word.html",
            filename=os.path.join(words_dir, language, filename),

            data=enhanced_data,
            title=f"{word}",
            #sounds=sounds.get(word) if sounds else [],
            word=word,
        )

        export_json(data, os.path.join(words_dir, language, f'{word}.json'))

def export_dictionary_lists(pages, html_dir):
    words_dir = os.path.join(html_dir, 'words')
    language = 'ladino'
    words = pages['ladino']
    os.makedirs(os.path.join(words_dir, language), exist_ok=True)
    render(
        template="words.html",
        filename=os.path.join(words_dir, language, 'index.html'),

        title=f"{language}",
        words=sorted(words.keys()),
    )

    render(
        template="dictionary_languages.html",
        filename=os.path.join(words_dir, 'index.html'),

        title=f"Languages",
        languages=sorted(languages),
    )


def export_about_html_page(count, html_dir):
    logging.info("Export about html page")
    end = datetime.datetime.now().replace(microsecond=0)
    elapsed = (end-ladino.common.start).total_seconds()
    render(
        template="about.html",
        filename=os.path.join(html_dir, "about.html"),

        title=f"Ladino dictionary - about",
        page="about",
        count=count,
        start=str(ladino.common.start),
        elapsed=elapsed,
        languages=languages,
    )


def export_main_html_page(html_dir):
    logging.info("Export main html page")

    render(
        template="index.html",
        filename=os.path.join(html_dir, "index.html"),

        title=f"Ladino dictionary",
        page="index",
    )

def export_json(all_words, filename, pretty=False):
    with open(filename, "w") as fh:
        if pretty:
            json.dump(all_words, fh, indent=4, ensure_ascii=False, sort_keys=True)
        else:
            json.dump(all_words, fh, ensure_ascii=False, sort_keys=True)

def export_missing_words(all_words, languages):
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    helper = os.path.join(root, 'helper')
    os.makedirs(helper, exist_ok=True)

    for language in languages:
        missing_rows = []
        existing_rows = []
        for word in all_words:
            for version in word['versions']:
                if 'translations' not in version:
                    continue
                translations = version['translations'].get(language)
                if translations:
                    existing_rows.append((version['ladino'], translations))
                    continue
                missing_rows.append(version['ladino'])
        with open(os.path.join(helper, f"{language}-missing.txt"), 'w') as fh:
            for row in sorted(missing_rows):
                print(f"{row:20} =", file=fh)

        with open(os.path.join(helper, f"{language}-has.txt"), 'w') as fh:
            for ladino, translations in sorted(existing_rows):
                print(f"{ladino:20} = {', '.join(translations)}", file=fh)

def export_single_page_dictionaries(dictionary, html_dir):
    logging.info("Export single-page dictionaries")

    for language in languages:
        render(
            template="dictionary.html",
            filename=os.path.join(html_dir, f"{language}-ladino.html"),

            title=f"{language.title()} to Ladino dictionary",
            source=language.title(),
            target="Ladino",
            words=dictionary[language],
        )

        render(
            template="dictionary.html",
            filename=os.path.join(html_dir, f"ladino-{language}.html"),

            title=f"Ladino to {language.title()} dictionary",
            source="Ladino",
            target=language.title(),
            trg=language,
            words=dictionary['ladino'],
        )



def export_to_html(config, categories, lists, verbs, all_examples, extra_examples, dictionary, count, pages, all_words, sounds, path_to_repo, html_dir, pretty=False):
    logging.info("Export to HTML")
    os.makedirs(html_dir, exist_ok=True)

    remove_previous_content_of(html_dir)

    export_json(dictionary, os.path.join(html_dir, "dictionary.json"), pretty=pretty)

    global sitemap
    sitemap = []
    generate_main_page(html_dir)
    export_missing_words(all_words, languages)

    export_single_page_dictionaries(dictionary, html_dir)

    create_pdf_dictionaries(all_words, languages)

    export_dictionary_lists(pages, html_dir)
    export_json(count, os.path.join(html_dir, "count.json"), pretty=pretty)
    export_about_html_page(count, html_dir)
    export_lists_html_page(config, html_dir)
    export_categories(categories, html_dir)
    export_lists(lists, html_dir)
    export_verbs(verbs, html_dir)
    export_examples(copy.deepcopy(all_examples), extra_examples, pages['ladino'], html_dir)
    export_markdown_pages(config, path_to_repo, html_dir)

    export_dictionary_pages(pages, sounds, html_dir)
    #export_to_hunspell(dictionary)

def export_lists_html_page(config, html_dir):
    render(
        template="lists.html",
        filename=os.path.join(html_dir, "lists.html"),

        title=f"Ladino lists",
        config=config,
    )
    render(
        template="dictionaries.html",
        filename=os.path.join(html_dir, "dictionaries.html"),

        title=f"Ladino dictionaries",
        github_run_id=os.environ.get('GITHUB_RUN_ID', ''),
        languages=languages,
    )


def export_markdown_pages(config, path_to_repo, html_dir):
    for source, target in config['pajinas'].items():
        with open(os.path.join(path_to_repo, 'pajinas', source)) as fh:
            text = fh.read()

        title = 'Pajina'
        match = re.search(r'^#\s+(.*?)\s*$', text, re.MULTILINE)
        if match:
            title = match.group(1)
        content = markdown.markdown(text, extensions=['tables'])

        render(
            template="page.html",
            filename=os.path.join(html_dir, target),

            title=title,
            page=target.replace('.html', ''),
            content=content,
        )

def export_examples(all_examples, extra_examples, words, html_dir):
    if not all_examples:
        return
    all_examples.sort(key=lambda ex: ex['example']['ladino'])
    for example in all_examples:
        example['example']['ladino_html'] = link_words(example['example']['ladino'], words)

    extra_examples.sort(key=lambda ex: ex['example']['ladino'])
    for example in extra_examples:
        example['example']['ladino_html'] = link_words(example['example']['ladino'], words)

    #print(all_examples)
    target = 'egzempios.html'
    render(
        template="examples.html",
        filename=os.path.join(html_dir, target),

        title='Egzempios',
        page=target.replace('.html', ''),
        all_examples=all_examples,
        extra_examples=extra_examples,
    )

def export_whatsapp(messages, words, html_dir):
    whatsapp_dir = os.path.join(html_dir, 'whatsapeando')
    os.makedirs(whatsapp_dir, exist_ok=True)
    messages.sort(key=lambda message: message['pub'], reverse=True)
    render(
        template="whatsapeando_list.html",
        filename=os.path.join(whatsapp_dir, 'index.html'),

        title='Estamos Whatsapeando',
        messages=messages,
    )
    for idx, message in enumerate(messages):
        text = link_words(message['text'], words)
        text = text.replace("\n", "<br>")
        next_idx = idx+1 if idx+1 < len(messages) else 0
        #print(next_idx)
        render(
            template="whatsapeando_page.html",
            filename=os.path.join(whatsapp_dir, f"{message['page']}.html"),

            title=message['titulo'],
            sound_filename=message['filename'],
            text=text,
            title_links=link_words(message['titulo'], words),
            prev_message=messages[idx-1]['page'],
            next_message=messages[next_idx]['page'],
        )

def generate_main_page(html_dir):
    root = os.path.dirname(os.path.abspath(__file__))

    for part in ["js", "css"]:
        source_dir = os.path.join(root, part)

        part_dir = os.path.join(html_dir, part)
        os.makedirs(part_dir, exist_ok=True)

        for filename in os.listdir(source_dir):
            if part == "js":
                with open(os.path.join(source_dir, filename)) as fh:
                    lines = filter(lambda line: not line.startswith('module.exports'), fh.readlines())
                with open(os.path.join(part_dir, filename), "w") as fh:
                    for line in lines:
                        print(line, end="", file=fh)
            else:
                shutil.copy(os.path.join(source_dir, filename), os.path.join(part_dir, filename))

    export_main_html_page(html_dir)

def remove_previous_content_of(html_dir):
    for thing in glob.glob(os.path.join(html_dir, '*')):
        if os.path.isdir(thing):
            shutil.rmtree(thing) # TODO remove all the old content from html_dir
        else:
            os.remove(thing)

def add_links(data, words):
    for entry in data:
        if 'examples' in entry:
            for example in entry['examples']:
                example['ladino_html'] = link_words(example['ladino'], words)
    return data

def link_words(sentence, words):
    return re.sub(r'(\w+)', lambda match:
        f'<a href="/words/ladino/{match.group(0).lower()}.html">{match.group(0)}</a>' if match.group(0).lower() in words else match.group(0), sentence)

def export_categories(categories, html_dir):
    for cat in categories.keys():
        render(
            template="category.html",
            filename=os.path.join(html_dir, f"{cat}.html"),

            title=cat,
            words=categories[cat],
            languages=languages,
        )
        for language in languages:
            render(
                template="dictionary.txt",
                filename=os.path.join(html_dir, f"{cat}-ladino-{language}.txt"),

                words=categories[cat],
                language=language,
            )

def export_lists(lists, html_dir):
    for lst in lists.keys():
        render(
            template="category.html",
            filename=os.path.join(html_dir, f"{lst}.html"),

            title=lst,
            words=lists[lst],
            languages=languages,
        )

def export_verbs(verbs, html_dir):
    verbs_dir = os.path.join(html_dir, 'verbos')
    os.makedirs(verbs_dir, exist_ok=True)
    verbs.sort(key=lambda word: (word['versions'][0]['ladino'], word['versions'][0]['translations']['english']))
    render(
        template="category.html",
        filename=os.path.join(html_dir, f"verbos.html"),

        title="Verbos",
        words=verbs,
        languages=languages,
    )
    for verb in verbs:
        ladino = verb['versions'][0]['ladino']
        data = {
            'to': verb['versions'][0]['ladino'],
        }
        if ladino.endswith('er'):
            root = ladino[0:-2]
            data['prezente'] = {
                'yo': root + 'o',
                'tu': root + 'es',
                'el': root + 'e',
                'moz': root + 'emos',
                'voz': root + 'ésh',
                'eyos': root + 'en',
            }
        export_json(data, os.path.join(verbs_dir, f'{ladino}.json'))

def create_sitemap(html_dir):
    xml = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd" xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
'''
    for entry in sitemap:
        xml += f'''<url>
            <loc>https://diksionaryo.szabgab.com/{entry}</loc>
            </url>'''
    xml += '</urlset>'
    with open(os.path.join(html_dir, 'sitemap.xml'), 'w') as fh:
        fh.write(xml)

