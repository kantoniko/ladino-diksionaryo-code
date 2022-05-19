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

language_names = {
            'english'    : 'inglez',
            'french'     : 'fransez',
            'hebrew'     : 'ebreo',
            'portuguese' : 'portugez',
            'spanish'    : 'kasteyano',
            'turkish'    : 'turko'
}

sitemap = []
html_path = None

def render(template, filename=None, **args):
    root = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(root, "templates")
    env = Environment(loader=FileSystemLoader(templates_dir), autoescape=True)
    env.filters["yaml2html"] = lambda path: re.sub(r"\.yaml$", ".html", path)
    html_template = env.get_template(template)
    html = html_template.render(**args)
    with open(os.path.join(html_path, filename), "w") as fh:
        fh.write(html)
    if filename == 'index.html':
        sitemap.append('')
    elif filename.endswith('.html'):
        sitemap.append(filename[0:-5])

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
    for plain_word, data in words.items():
        enhanced_data = add_links(copy.deepcopy(data), words)
        filename = f'{plain_word}.html'
        logging.info(f"Export to {filename}")
        render(
            template="word.html",
            filename=os.path.join('words', language, filename),

            data=enhanced_data,
            title=f"{plain_word}",
            #sounds=sounds.get(plain_word) if sounds else [],
            plain_word=plain_word,
            language_names=language_names,
        )

        export_json(data, os.path.join(words_dir, language, f'{plain_word}.json'))

def export_dictionary_lists(pages, html_dir):
    words_dir = os.path.join(html_dir, 'words')
    language = 'ladino'
    words = pages['ladino']
    os.makedirs(os.path.join(words_dir, language), exist_ok=True)
    examples = {}
    for word, data in words.items():
        ex = 0
        for dt in data:
            ex += len(dt.get('examples', []))
        examples[word] = ex
    render(
        template="words.html",
        filename=os.path.join('words', language, 'index.html'),

        title=f"{language}",
        words=words,
        examples=examples,
    )

    render(
        template="dictionary_languages.html",
        filename=os.path.join('words', 'index.html'),

        title=f"Languages",
        languages=sorted(languages),
    )


def export_about_html_page(count, html_dir):
    logging.info("Export about html page")
    end = datetime.datetime.now().replace(microsecond=0)
    elapsed = (end-ladino.common.start).total_seconds()
    render(
        template="about.html",
        filename="about.html",

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
        filename="index.html",

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

def export_single_page_dictionaries(word_mapping, html_dir):
    logging.info("Export single-page dictionaries")

    for language in languages:
        render(
            template="dictionary.html",
            filename=f"{language}-ladino.html",

            title=f"{language.title()} to Ladino dictionary",
            source=language.title(),
            target="Ladino",
            words=word_mapping[language],
        )

        render(
            template="dictionary.html",
            filename=f"ladino-{language}.html",

            title=f"Ladino to {language.title()} dictionary",
            source="Ladino",
            target=language.title(),
            trg=language,
            words=word_mapping['ladino'],
        )



def export_to_html(config, dictionary, extra_examples, sounds, path_to_repo, html_dir, pretty=False):
    logging.info("Export to HTML")
    os.makedirs(html_dir, exist_ok=True)
    global html_path
    html_path = html_dir

    remove_previous_content_of(html_dir)

    export_json(dictionary.word_mapping, os.path.join(html_dir, "dictionary.json"), pretty=pretty)

    global sitemap
    sitemap = []
    generate_main_page(html_dir)
    export_missing_words(dictionary.all_words, languages)

    export_single_page_dictionaries(dictionary.word_mapping, html_dir)

    create_pdf_dictionaries(dictionary.all_words, languages)

    export_dictionary_lists(dictionary.pages, html_dir)
    export_json(dictionary.count, os.path.join(html_dir, "count.json"), pretty=pretty)
    export_about_html_page(dictionary.count, html_dir)
    export_lists_html_page(config, html_dir)
    export_categories(dictionary.categories, html_dir)
    export_lists(dictionary.lists, html_dir)
    export_verbs(dictionary.verbs, html_dir)
    export_examples(copy.deepcopy(dictionary.all_examples), extra_examples, dictionary.pages['ladino'], html_dir)
    export_markdown_pages(config, path_to_repo, html_dir)

    export_dictionary_pages(dictionary.pages, sounds, html_dir)
    #export_to_hunspell(dictionary.word_mapping)

def export_lists_html_page(config, html_dir):
    render(
        template="lists.html",
        filename="lists.html",

        title=f"Ladino lists",
        config=config,
    )
    render(
        template="dictionaries.html",
        filename="dictionaries.html",

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
            filename=target,

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
        filename=target,

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
        filename=os.path.join('whatsapeando', 'index.html'),

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
            filename=os.path.join('whatsapeando', f"{message['page']}.html"),

            title=message['titulo'],
            sound_filename=message['filename'],
            text=text,
            title_links=link_words(message['titulo'], words),
            prev_message=messages[idx-1]['page'],
            next_message=messages[next_idx]['page'],
        )

def copy_static_files(html_dir):
    root = os.path.dirname(os.path.abspath(__file__))

    shutil.copy(os.path.join(root, 'robots.txt'), os.path.join(html_dir, 'robots.txt'))
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

def generate_main_page(html_dir):
    copy_static_files(html_dir)
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
        f'<a href="/words/ladino/{match.group(0).lower()}">{match.group(0)}</a>' if match.group(0).lower() in words else match.group(0), sentence)

def export_categories(categories, html_dir):
    for cat in categories.keys():
        render(
            template="category.html",
            filename=f"{cat}.html",

            title=cat,
            words=categories[cat],
            languages=languages,
        )
        for language in languages:
            render(
                template="dictionary.txt",
                filename=f"{cat}-ladino-{language}.txt",

                words=categories[cat],
                language=language,
            )

def export_lists(lists, html_dir):
    for lst in lists.keys():
        render(
            template="category.html",
            filename=f"{lst}.html",

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
        filename=f"verbos.html",

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
    #return
    xml = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd" xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
'''
    for entry in sorted(sitemap):
        xml += f'''<url><loc>https://diksionaryo.szabgab.com/{entry}</loc></url>\n'''
    xml += '</urlset>'
    with open(os.path.join(html_dir, 'sitemap.xml'), 'w') as fh:
        fh.write(xml)

