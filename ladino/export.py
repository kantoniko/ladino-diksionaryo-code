import copy
import logging
import os
import glob
import json
import shutil
import re
import datetime
import sys
from yaml import safe_load

import markdown
from jinja2 import Environment, FileSystemLoader

from ladino.common import languages
import ladino.common
from ladino.export_to_hunspell import export_to_hunspell
from ladino.pdf import create_pdf_dictionaries
import ladino.whatsapeando as whatsapp
from ladino.ufad import load_ufad
from ladino.ladinadores import load_ladinadores
from ladino.videos import load_videos

language_codes = {
            'inglez'   : 'en',
            'fransez'  : 'fr',
            'ebreo'    : 'he',
            'portugez' : 'pt',
            'kasteyano': 'es',
            'turko'    : 'tr'
}


html_path = None

accents = {
    'á': 'a',
    'é': 'e',
    'í': 'i',
    'ó': 'o',
    'ú': 'u',
}


# TODO: make this more efficient
def deaccent(text):
    for k, v in accents.items():
        text = text.replace(k, v)
    return text


def render(template, filename=None, **args):
    root = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(root, "templates")
    env = Environment(loader=FileSystemLoader(templates_dir), autoescape=True)
    env.filters["yaml2html"] = lambda path: re.sub(r"\.yaml$", ".html", path)
    html_template = env.get_template(template)
    lang = "lad"
    if filename.startswith("en/"):
        lang = "en"
    if filename.startswith("he/"):
        lang = "he"
    html = html_template.render(**args, lang=lang)

    full_path = os.path.join(html_path, filename)
    dir_path = os.path.dirname(full_path)
    os.makedirs(dir_path, exist_ok=True)

    with open(full_path, "w") as fh:
        fh.write(html)
    if filename.endswith('index.html'):
        sitemap.add(filename[0:-10])
    elif filename.endswith('.html'):
        sitemap.add(filename[0:-5])

def export_dictionary_pages(pages, word_to_examples, word_to_whatsapp, word_to_una_fraza, word_to_afish, html_dir):
    logging.info("export_dictionary_pages")
    words_dir = os.path.join(html_dir, 'words')
    os.makedirs(words_dir, exist_ok=True)
    #for language, words in pages.items():
    #if not words:
    #    continue
    language = 'ladino'
    words = pages['ladino']
    language_dir = os.path.join(words_dir, language)
    logging.info(f"Export one page for every word for {language} to {language_dir}")
    os.makedirs(language_dir, exist_ok=True)
    for plain_word, data in words.items():
        filename = f'{plain_word}.html'
        logging.info(f"Export to {filename}")
        render(
            template="word.html",
            filename=os.path.join('words', language, filename),

            data=copy.deepcopy(data),
            title=f"{plain_word}",
            plain_word=plain_word,
            language_codes=language_codes,
            whatsapp=word_to_whatsapp.get(plain_word, {}),
            afishes=word_to_afish.get(plain_word, {}),
            ufad=word_to_una_fraza.get(plain_word, {}),
            examples=sorted(word_to_examples.get(plain_word, {}), key=lambda ex: ex['ladino']),
        )

        export_json(data, os.path.join(words_dir, language, f'{plain_word}.json'))

def export_dictionary_lists(pages, word_to_examples, word_to_whatsapp, word_to_una_fraza, word_to_afish, html_dir):
    words_dir = os.path.join(html_dir, 'words')
    language = 'ladino'
    words = pages['ladino']

    total = {}
    for word in words.keys():
        total[word] = 0
        for things in [word_to_examples, word_to_whatsapp, word_to_una_fraza, word_to_afish]:
            total[word] += len(things.get(word, []))

    os.makedirs(os.path.join(words_dir, language), exist_ok=True)
    render(
        template="ladino_words.html",
        filename=os.path.join('words', language, 'index.html'),

        title=f"{language}",
        words=words,
        examples=word_to_examples,
        whatsapp=word_to_whatsapp,
        una_fraza=word_to_una_fraza,
        afishes=word_to_afish,
        total=total,
    )

    render(
        template="dictionary_languages.html",
        filename=os.path.join('words', 'index.html'),

        title=f"Languages",
        languages=sorted(languages),
    )
    return total

def export_static_pages(html_dir):
    logging.info("Export static pages")

    tmpl = "echar-lashon.html"
    render(
        template=tmpl,
        filename=tmpl,
    )

    tmpl = "404.html"
    render(
        template=tmpl,
        filename=tmpl,
    )


def export_statistics_html_page(count, html_dir):
    logging.info("Export statistics html page")
    render(
        template="statistika.html",
        filename="statistika.html",

        title=f"Statistika",
        page="statistika",
        count=count,
        start=str(ladino.common.start),
        languages=languages,
    )


def export_main_html_page(html_dir):
    logging.info("Export main html page")

    render(
        template="index.html",
        filename="index.html",

        title=f"El kantoniko de Ladino",
        page="index",
    )

def export_json(data, filename, pretty=False):
    with open(filename, "w") as fh:
        if pretty:
            json.dump(data, fh, indent=4, ensure_ascii=False, sort_keys=True)
        else:
            json.dump(data, fh, ensure_ascii=False, sort_keys=True)

def export_missing_words(yaml_files, missing_ladino_words, languages):
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dname = 'faltan'
    helper = os.path.join(html_path, dname)
    os.makedirs(helper, exist_ok=True)

    count = {
        'ladino': len(missing_ladino_words.keys())
    }

    for language in languages:
        missing_words = []
        missing_rows = []
        existing_rows = []
        for word in yaml_files:
            word_added = False
            for version in word['versions']:
                if 'translations' not in version:
                    continue
                translations = version['translations'].get(language)
                if translations:
                    existing_rows.append((version['ladino'], translations))
                    continue
                missing_rows.append(version['ladino'])
                if not word_added:
                    word_added = True
                    missing_words.append(word)

        count[language] = len(missing_words)
        with open(os.path.join(helper, f"{language}-missing.txt"), 'w') as fh:
            for row in sorted(missing_rows):
                print(f"{row:20} =", file=fh)

        with open(os.path.join(helper, f"{language}-has.txt"), 'w') as fh:
            for ladino, translations in sorted(existing_rows):
                print(f"{ladino:20} = {', '.join(translations)}", file=fh)

        render(
            template="missing_words.html",
            filename=os.path.join(dname, f"ladino.html"),

            title=f"Palavras ke mankan",
            words=missing_ladino_words,
       )

        render(
            template="category.html",
            filename=os.path.join(dname, f"{language.lower()}.html"),

            title=f"Palavras sin traduksione en {language}",
            words=sorted(missing_words, key=lambda words: words['versions'][0]['ladino']),
            languages=languages,
        )

    render(
        template="categories.html",
        filename=f"{dname}/index.html",
        dname=dname,

        title=f"Palavras sin traduksiones",
        values=languages,
    )

    return count

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

def export_books(books, words, html_dir):
    if books:
        processed = []
        for book in books:
            processed.append(export_book(book, words, html_dir))

        render(
            template="books_index_page.html",
            filename=os.path.join('livros', "index.html"),
            title=f"Livros",
            books=processed,
            )

def export_book(book, words, html_dir):
    with open(os.path.join(book, 'book.yaml')) as fh:
        data = safe_load(fh)

    pages = []
    done = False
    for chapter in data['chapters']:
        #print(chapter['titolo'])
        for page in chapter.get('pajinas', []):
            #print(page['numero'])
            pages.append({
                'numero': page['numero'],
                'teksto': link_words(page['teksto'], words),
                'chapter': chapter['titolo'],
            })
            #if page['numero'] == data['publish']:
            #    done = True
            #    break
        if done:
            break

    for idx, page in enumerate(pages):
        render(
            template="book_page.html",
            filename=os.path.join('livros', data['path'], str(page['numero']) + ".html"),
            html_text=page['teksto'].replace("\n", "<br>"),
            prev_page=(pages[idx-1]['numero'] if idx > 0 else "."),
            next_page=(pages[idx+1]['numero'] if idx < len(pages)-1 and idx != data['publish']-1 else "."),
            footer=data['footer'],
            title=f"{data['titolo']} - {page['chapter']} - {page['numero']}",
        )
    render(
        template="book_index_page.html",
        filename=os.path.join('livros', data['path'], "index.html"),
        title=f"{data['titolo']}",
        data=data,
        prev_page=data['publish'],
        next_page=pages[0]['numero'],
        )
    return {'path': data['path'], 'titolo': data['titolo']}


def export_whatsapp_and_update_dictionary(dictionary, whatsapp_dir, html_dir):
    word_to_whatsapp = {}
    if whatsapp_dir:
        messages = whatsapp.get_messages(whatsapp_dir) # list of dicts
        for message in messages:
            #print(message)
            page = message['page']

            # WhatsApp message that are ladino only have a 'text' field, messages with hebrew have a field called teksto
            words_in_message = re.findall(r'\w+', message['titulo'])
            if 'text' in messages:
                words_in_message += re.findall(r'\w+', message['text'])
            else:
                for sentence in message['teksto']:
                    words_in_message += re.findall(r'\w+', sentence['ladino'])
            for word in words_in_message:
                word = word.lower()
                if word not in word_to_whatsapp:
                    word_to_whatsapp[word] = {}
                word_to_whatsapp[word][page] = message['titulo']

        dictionary.count['whatsapp'] = {
            'all' : len(messages),
            'hebrew': len(list(filter(lambda msg: msg['teksto'][0].get('ebreo') != '', messages))),
            'images': len(list(filter(lambda msg: msg.get('img') is not None, messages))),
        }
        #print(messages)
        export_whatsapp(messages, dictionary.pages['ladino'].keys(), html_dir)
    return word_to_whatsapp


def get_words_from_una_fraza(unafraza, dictionary, html_dir):
    word_to_una_fraza = {}
    entries = []
    if unafraza:
        entries = load_ufad(unafraza)
        for entry in entries:
            words_in_message = re.findall(r'\w+', entry['Ladino'])
            for word in words_in_message:
                word = word.lower()
                if word not in word_to_una_fraza:
                    word_to_una_fraza[word] = {}
                page = entry['filename'][0:-5]
                word_to_una_fraza[word][page] = entry['Ladino']


        export_ufad(entries, dictionary.pages['ladino'].keys(), html_dir)
    return word_to_una_fraza, len(entries)

def get_separate_words(text):
    separate_words = set(word.lower() for word in re.findall(r'(\w+)', text))
    return separate_words

def get_missing_words(dictionary, examples):
    all_the_words = set(dictionary.pages['ladino'].keys())
    for word in dictionary.pages['ladino'].keys():
        for version in dictionary.pages['ladino'][word]:
            accented = version.get('accented')
            if accented is not None:
                all_the_words.add(accented)
    # print(all_the_words)

    # Exclude some names from the list of missing translations
    names = {'zoom', 'zevulun', 'yugoslavia', 'yosi', 'yosef', 'york', 'yaakov'}
    all_the_words.update(names)

    missing_words = {}

    for example in examples:
        separate_words = get_separate_words(example['ladino'])
        for word in (separate_words - all_the_words):
            if re.search(r'^[0-9]+$', word):
                continue
            # print(word)
            if word not in missing_words:
                missing_words[word] = []
            # print(example)
            missing_words[word].append(f"/egzempios/{example['url']}")

    # print(missing_words)
    return missing_words

def export_to_html(config, dictionary, examples, word_to_examples, sound_people, path_to_repo, html_dir, whatsapp_dir=None, unafraza=None, pages=None, books=None, ladinadores=None, enkontros=None, pretty=False):
    logging.info("Export to HTML")
    os.makedirs(html_dir, exist_ok=True)
    global html_path
    html_path = html_dir

    remove_previous_content_of(html_dir)

    export_json(dictionary.word_mapping, os.path.join(html_dir, "dictionary.json"), pretty=pretty)

    global sitemap
    sitemap = set()
    generate_main_page(html_dir)

    export_books(books, dictionary.pages['ladino'].keys(), html_dir)

    word_to_afish = {}
    if ladinadores is not None:
        afishes = load_ladinadores(ladinadores)
        export_ladinadores(dictionary.yaml_files, afishes)
        dictionary.count["afishes"] = len (afishes)
        for afish in afishes:
            for word in afish.get('palavras', []):
                if word not in word_to_afish:
                    word_to_afish[word] = {}
                filename = afish['filename']
                title = afish['titulo']
                word_to_afish[word][filename] = title
    if enkontros is not None:
        enkontros_videos, content, short, people = load_videos(enkontros)

        export_videos(enkontros_videos, content, short, people, 'enkontros-de-alhad')

    # Count audio files
    examples_with_audio = 0
    for example in examples:
        if "audio" in example:
            examples_with_audio += 1
    dictionary.count["examples_with_audio"] = examples_with_audio


    word_to_whatsapp = export_whatsapp_and_update_dictionary(dictionary, whatsapp_dir, html_dir)

    word_to_una_fraza, count_una_fraza = get_words_from_una_fraza(unafraza, dictionary, html_dir)
    dictionary.count["una_fraza_al_dia"] = count_una_fraza

    export_single_page_dictionaries(dictionary.word_mapping, html_dir)

    create_pdf_dictionaries(dictionary.yaml_files, languages)

    export_static_pages(html_dir)
    words_with_examples = export_dictionary_lists(dictionary.pages, word_to_examples, word_to_whatsapp, word_to_una_fraza, word_to_afish, html_dir)
    dictionary.count["words_with_examples"] = 0
    dictionary.count["words_without_examples"] = 0
    for word, count in words_with_examples.items():
        if count > 0:
            dictionary.count["words_with_examples"] += 1
        else:
            dictionary.count["words_without_examples"] += 1

    export_lists_html_page(config, html_dir)
    export_categories(config, dictionary.categories, html_dir)
    export_orijenes(config, dictionary.orijenes, html_dir)
    export_languages(config, dictionary.languages, html_dir)
    export_lists(config, dictionary.lists, html_dir)
    export_gramer(config, dictionary.gramer, html_dir)
    export_verbs(config, dictionary.gramer['verb'], html_dir)
    export_examples(copy.deepcopy(examples), dictionary.pages['ladino'].keys(), sound_people, html_dir)
    export_listed_pages(config, path_to_repo, html_dir)
    export_fixed_pages(pages)

    export_dictionary_pages(dictionary.pages, word_to_examples, word_to_whatsapp, word_to_una_fraza, word_to_afish, html_dir)
    export_to_hunspell(dictionary.word_mapping, html_dir)

    missing_ladino_words = get_missing_words(dictionary, examples)
    count_missing_words = export_missing_words(dictionary.yaml_files, missing_ladino_words, languages)

    dictionary.count["missing_words"] = count_missing_words
    export_json(dictionary.count, os.path.join(html_dir, "count.json"), pretty=pretty)
    export_statistics_html_page(dictionary.count, html_dir)

def export_videos(videos, content, short, people, path):
    logging.info(f"Export videos to {path}")

    render(
        template="videos_list.html",
        filename=os.path.join(path, "index.html"),

        title=f"Enkontros de Alhad",
        path=path,
        content=content,
        videos=videos,
    )

    render(
        template="video_personas_list.html",
        filename=os.path.join(path, "partisipantes.html"),

        title=f"Partisipantes en losEnkontros de Alhad",
        path=path,
        people=people,
    )

    for video in videos:
        render(
            template="video.html",
            filename=os.path.join(path, f"{video['filename']}.html"),

            title=f"Enkontros de Alhad",
            people=people,
            text=short,
            video=video,
        )

    for uid in people.keys():
        render(
            template="videos_list.html",
            filename=os.path.join(path, f"{uid}.html"),

            title=f"Enkontros de Alhad {people[uid]['name']}",
            path=path,
            content=f"Filmikos kon la parisipasion de {people[uid]['name']}",
            videos=people[uid]['videos'],
        )







def export_ladinadores(yaml_files, data):
    logging.info("Export Ladinadores")

    render(
        template="afishes.html",
        filename="afishes/index.html",

        title=f"Afishes de Los Ladinadores",
        data=data,
    )

    for entry in data:
        words = []
        missing_words = []
        if 'palavras' in entry:
            for palavra in sorted(entry['palavras']):
                # print(f"palavra: {palavra}")
                found = False
                for word in yaml_files:
                    # print(word)
                    for version in word['versions']:
                        if palavra == version['ladino']:
                            words.append(word)
                            found = True

                if not found:
                    missing_words.append(palavra)

        # print(words)
        render(
            template="afish.html",
            filename=os.path.join("afishes", entry['img'][0:-4] + '.html'),

            title=entry['titulo'],
            entry=entry,
            languages=languages,
            words=words,
            missing_words=missing_words,
        )


def export_fixed_pages(pages):
    logging.info("export_fixed_pages")
    if not pages:
        return

    with open(os.path.join(pages, 'mapping.json')) as fh:
        mapping = json.load(fh)
    for source, target in mapping.items():
        rtl = source == 'he'
        for filename in os.listdir(os.path.join(pages, source)):
            logging.info(f"Exporting {source}/{filename}")
            if filename.endswith('.md'):
                target_file = filename.replace('.md', '.html')
                export_markdown_page(os.path.join(pages, source, filename), os.path.join(target, target_file), rtl=rtl)

def export_lists_html_page(config, html_dir):
    logging.info("export_lists_html_page")
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

def export_listed_pages(config, path_to_repo, html_dir):
    logging.info("export_listed_pages")
    for source, target in config['pajinas'].items():
        export_markdown_page(os.path.join(path_to_repo, 'pajinas', source), target, rtl=False)

def export_markdown_page(path_to_md_file, target, rtl):
    logging.info(f"export_markdown_page: from {path_to_md_file} to {target} (rtl: {rtl})")

    with open(path_to_md_file) as fh:
        text = fh.read()

    title = 'Pajina'
    match = re.search(r'^#\s+(.*?)\s*$', text, re.MULTILINE)
    if match:
        title = match.group(1)
    content = markdown.markdown(text, extensions=['tables'])

    render(
        template="markdown_page.html",
        filename=target,
        rtl=rtl,

        title=title,
        page=target.replace('.html', ''),
        content=content,
    )

def export_individual_examples(examples, words, sound_people, target):
    logging.info(f"export_individual_examples {len(examples)}")

    sounds = {}
    for example in examples:
        logging.info(f"export example from {example['filename']} to {example['url']}")
        example['ladino_html'] = link_words(example['ladino'], words)
        for language in languages:
            # We have duplicate translations for some of the examples.
            if language in example:
                if example[language].__class__.__name__ == "str":
                    example[f"{language}_html"] = newline_to_br(example[language])
                elif example[language].__class__.__name__ == "list":
                    example[f"{language}_html"] = "<br>".join(map(newline_to_br, example[language]))
                else:
                    raise Exception(f"invalid type: {example[language].__class__.__name__}")
        if 'audio' in example:
            for sound in example['audio']:
                person = sound['person']
                if person in sound_people:
                    if person not in sounds:
                        sounds[person] = []
                    sounds[person].append(example)

        else:
            if 'silent' not in sounds:
                sounds['silent'] = []
            sounds['silent'].append(example)

        render(
            template="example.html",
            filename=os.path.join(target, example['url'] + '.html'),
            path='examples',

            title='Egzempio',
            example=example,
            people=sound_people,
        )

    return sounds

def export_examples(all_examples, words, sound_people, html_dir):
    logging.info(f"export_examples {len(all_examples)}")
    if not all_examples:
        return
    target = 'egzempios'
    examples_dir = os.path.join(html_dir, target)
    os.makedirs(examples_dir, exist_ok=True)
    all_examples.sort(key=lambda ex: ex['ladino'])
    sounds = {}
    for example in all_examples:
        example['ladino_html'] = link_words(example['ladino'], words)

    sounds = export_individual_examples(all_examples, words, sound_people, target)

    for person, examples in sounds.items():
        if person == 'silent':
            render(
                template="examples_with_sound.html",
                filename=os.path.join(target, person + '.html'),

                title=f'Egzempios sin audio',
                #sounds=sounds,
                person_titulo='',
                page=target,
                examples=examples,
                languages=languages,
            )

        else:
            render(
                template="examples_with_sound.html",
                filename=os.path.join(target, person + '.html'),

                title=f'Egzempios kon la boz de {sound_people[person]["nombre"]}',
                #sounds=sounds,
                person_titulo=sound_people[person]['titulo'],
                page=target,
                examples=examples,
                languages=languages,
            )

    #print(all_examples)
    sound_people['silent'] = {
        'nombre': 'Silent',
    }
    render(
        template="examples.html",
        filename=os.path.join(target, 'index.html'),

        title='Egzempios',
        sounds=sounds,
        people=sound_people,
        page=target,
        all_examples=all_examples,
        languages=languages,
    )

def export_ufad(messages, words, html_dir):
    ufad_dir = os.path.join(html_dir, 'ufad')
    os.makedirs(ufad_dir, exist_ok=True)

    for message in messages:
        message['id'] = message['audio'][0:-4].lower()

    for idx, message in enumerate(messages):
        message['ladino_html'] = link_words(message['Ladino'], words)
        next_idx = idx+1 if idx+1 < len(messages) else 0
        render(
            template="ufad_page.html",
            filename=os.path.join('ufad', f"{message['id']}.html"),

            title=message['Ladino'],
            message=message,
            prev_message=messages[idx-1]['id'],
            next_message=messages[next_idx]['id'],
        )

    render(
        template="ufad_list.html",
        filename=os.path.join('ufad', 'index.html'),

        title='Una fraza al diya',
        messages=messages,
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
        teksto = copy.deepcopy(message['teksto'])
        #print(teksto)
        for entry in teksto:
            text = link_words(entry['ladino'], words)
            text = text.replace("\n", "<br>")
            entry['ladino'] = text
            if 'ebreo' in entry:
                entry['ebreo'] = entry['ebreo'].replace("\n", "<br>")
        next_idx = idx+1 if idx+1 < len(messages) else 0
        #print(next_idx)
        render(
            template="whatsapeando_page.html",
            filename=os.path.join('whatsapeando', f"{message['page']}.html"),

            title=message['titulo'],
            sound_filename=message.get('ogg'),
            teksto=teksto,
            title_links=link_words(message['titulo'], words),
            prev_message=messages[idx-1]['page'],
            next_message=messages[next_idx]['page'],
            img_filename=message.get('img'),
            this=message,
        )

def copy_static_files(html_dir):
    root = os.path.dirname(os.path.abspath(__file__))

    shutil.copy(os.path.join(root, 'robots.txt'), os.path.join(html_dir, 'robots.txt'))
    for part in ["js", "css"]:
        source_dir = os.path.join(root, part)

        part_dir = os.path.join(html_dir, part)
        os.makedirs(part_dir, exist_ok=True)

        for filename in os.listdir(source_dir):
            if filename.endswith(".swp"):
                continue
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

def newline_to_br(text):
    return text.replace("\n", "<br>")

def link_words(sentence, words):
    # logging.info(f"link_words({sentence})")
    sentence = newline_to_br(sentence)
    return re.sub(r'(\w+)', lambda match:
        f'<a href="/words/ladino/{deaccent(match.group(0).lower())}">{match.group(0)}</a>' if deaccent(match.group(0).lower()) in words else match.group(0), sentence)

def export_languages(config, source_languages, html_dir):
    logging.info("export_languages")
    dname = 'linguas'
    os.makedirs(os.path.join(html_dir, dname), exist_ok=True)
    for language in source_languages.keys():
        render(
            template="category.html",
            filename=os.path.join(dname, f"{language.lower()}.html"),

            title=language,
            words=source_languages[language],
            languages=languages,
        )

    render(
        template="categories.html",
        filename=f"{dname}/index.html",
        dname=dname,

        title=f"Linguas",
        values=config['linguas'],
    )



def export_orijenes(config, orijenes, html_dir):
    logging.info("export_orijenes")
    dname = 'orijenes'
    os.makedirs(os.path.join(html_dir, dname), exist_ok=True)
    for orijen in orijenes.keys():
        render(
            template="category.html",
            filename=os.path.join(dname, f"{orijen.lower()}.html"),

            title=orijen,
            words=orijenes[orijen],
            languages=languages,
        )

    render(
        template="categories.html",
        filename=f"{dname}/index.html",
        dname=dname,

        title=f"Orijenes",
        values=config['orijenes'],
    )



def export_categories(config, categories, html_dir):
    logging.info("export_categories")
    dname = 'kategorias'
    os.makedirs(os.path.join(html_dir, 'kategorias'), exist_ok=True)
    for cat in categories.keys():
        render(
            template="category.html",
            filename=os.path.join('kategorias', f"{cat}.html"),

            title=cat,
            words=categories[cat],
            languages=languages,
        )
        # Text files for easier editing
        # TODO: shall weshall we  add links to them?
        for language in languages:
            render(
                template="dictionary.txt",
                filename=os.path.join('kategorias', f"{cat}-ladino-{language}.txt"),

                words=categories[cat],
                language=language,
            )

    render(
        template="categories.html",
        filename=f"{dname}/index.html",
        dname=dname,

        title=f"Kategorias",
        values=config['kategorias'],
    )

def export_lists(config, lists, html_dir):
    logging.info("export_lists")
    dname = 'listas'
    os.makedirs(os.path.join(html_dir, dname), exist_ok=True)
    for lst in lists.keys():
        render(
            template="category.html",
            filename=f"{dname}/{lst}.html",

            title=lst,
            words=lists[lst],
            languages=languages,
        )

    render(
        template="categories.html",
        filename=f"{dname}/index.html",
        dname=dname,

        title=f"Listas",
        values=config['listas'],
    )


def export_gramer(config, gramer, html_dir):
    logging.info("export_gramer")
    dname = 'gramer'
    os.makedirs(os.path.join(html_dir, dname), exist_ok=True)
    for name in gramer.keys():
        words = gramer[name]
        words.sort(key=lambda word: (word['versions'][0]['ladino'], word['versions'][0]['translations']['inglez']))
        render(
            template="category.html",
            filename=os.path.join(dname, f"{name.lower()}.html"),

            title=f"gramer: {name}",
            words=words,
            languages=languages,
        )

    render(
        template="categories.html",
        filename=f"{dname}/index.html",
        dname=dname,

        title=f"Gramers",
        values=config['gramatika'],
    )

def export_verbs(config, verbs, html_dir):
    logging.info("export_verbs")
    verbs_dir = os.path.join(html_dir, 'verbos')
    os.makedirs(verbs_dir, exist_ok=True)
    irregulars = config['verbos-iregolares']
    for verb in verbs:
        ladino = verb['versions'][0]['ladino']
        export_json(verb['conjugations'], os.path.join(verbs_dir, f'{ladino}.json'))
        render(
            template="verb.html",
            filename=os.path.join('verbos', f'{ladino}.html'),
            title=ladino,
            verb=verb,
            irregular = ladino in irregulars,
            tiempos=config['tiempos'],
            pronombres=config['pronombres'],
        )
# {'grammar': 'verb', 'id': '236', 'orijen': 'Jeneral', 'versions': [{'ladino': 'depender', 'translations': {'inglez': ['depend'], 'fransez': [], 'portugez': [], 'kasteyano': ['depender'], 'turko': ['bağımlı olmak']}, 'source': 'depender.yaml', 'orijen': 'Jeneral'}],
# 'conjugations': {'infinito': ('depender',), 'prezente': {'ladino': {'yo': 'dependo', 'tu': 'dependes', 'el': 'depende', 'moz': 'dependemos', 'voz': 'dependésh', 'eyos': 'dependen'}}}, 'examples': []}

    render(
        template="verbs.html",
        filename=os.path.join('verbos', "index.html"),
        title=f"Verbos",
        words=verbs,
        languages=languages,
    )


def create_sitemap(html_dir):
    #return
    xml = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd" xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
'''
    for entry in sorted(sitemap):
        xml += f'''<url><loc>https://kantoniko.com/{entry}</loc></url>\n'''
    xml += '</urlset>'
    with open(os.path.join(html_dir, 'sitemap.xml'), 'w') as fh:
        fh.write(xml)

