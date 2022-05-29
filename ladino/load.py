from yaml import safe_load
import os
import logging
import json
import copy

from ladino.common import LadinoError, languages

class Dictionary():
    def __init__(self, config):
        self.yaml_files = []  # each entry as loaded from the yaml files of words
        self.words = []
        self.all_examples = []
        self.lists = {lst:[] for lst in config['listas'] }
        self.categories = {cat:[] for cat in config['kategorias'] }
        self.gramer = {name:[] for name in config['gramatika'] }
        self.origenes = {name:[] for name in config['origenes'] }

        self.count = {}
        self.word_mapping = {}
        self.pages = {}

        self.count['dictionary'] = {}
        for language in ['ladino'] + languages:
            self.count['dictionary'][language] = {
                'words': 0,
                'examples': 0,
            }
            self.word_mapping[language] = {}
            self.pages[language] = {}

def load_config(path_to_repo):
    with open(os.path.join(path_to_repo, 'config.yaml')) as fh:
        return safe_load(fh)

def check_and_collect_grammar(config, data, dictionary, filename):
    if 'grammar' not in data:
        raise LadinoError(f"The 'grammar' field is missing from file '{filename}'")

    grammar = data['grammar']

    if grammar not in config['gramatika']:
        raise LadinoError(f"Invalid grammar '{grammar}' in file '{filename}'")

    if grammar == 'verb' and 'conjugations' not in data:
        raise LadinoError(f"Grammar is 'verb', but there is NO 'conjugations' field in '{filename}'")
    if grammar != 'verb' and 'conjugations' in data:
        raise LadinoError(f"Grammar is NOT a 'verb', but there are conjugations in '{filename}'")

    if grammar in ['noun']: # 'adjective',
        for version in data['versions']:
            gender = version.get('gender')
            if gender is None:
                raise LadinoError(f"The 'gender' field is None in '{filename}' version {version}")
            if gender not in config['gender']:
                raise LadinoError(f"Invalid value '{gender}' in 'gender' field in '{filename}' version {version}")
            number = version.get('number')
            if number is None:
                raise LadinoError(f"The 'number' field is None in '{filename}' version {version}")
            if number not in config['numero']:
                raise LadinoError(f"The 'number' field is '{number}' in '{filename}' version {version}")

    dictionary.gramer[grammar].append(data)


def check_and_collect_origen(config, data, filename, dictionary):
    if 'origen' not in data:
        raise LadinoError(f"The 'origen' field is missing from file '{filename}'")
    origen  = data['origen']
    if origen not in config['origenes']:
        raise LadinoError(f"Invalid origen '{origen}' in file '{filename}'")

    dictionary.origenes[origen].append(data)

    return origen

def check_and_collect_categories(config, data, filename, dictionary):
    if 'kategorias' not in data:
        return
    for cat in data['kategorias']:
        if cat not in config['kategorias']:
            raise LadinoError(f"Invalid category '{cat}' in file '{filename}'")
        dictionary.categories[cat].append(data)

def make_them_list(translations, filename):
    for language in languages:
        if language not in translations:
            continue
        translations[language] = make_it_list(translations, language, filename)

def make_it_list(translations, language, filename):
    target_words = translations[language]
    if target_words.__class__.__name__ == 'str':
        if target_words == '':
            return []
        else:
            return [target_words]
    elif target_words.__class__.__name__ == 'list':
        return target_words
    else:
        raise LadinoError(f"bad type {target_words.__class__.__name__} for {language} in {translations} in '{filename}'")

def check_and_collect_lists(config, data, dictionary):
    for lst, listed_words in config['listas'].items():
        #print(data['versions'][0]['ladino'])
        #print(listed_words)
        if 'versions' in data and 'ladino' in data['versions'][0] and data['versions'][0]['ladino'] in listed_words:
            dictionary.lists[lst].append(data)
        # TODO: include also words from the lists that don't appear in our dictionaries (without a link)
        # TODO: add these words to the list of missing words


def load_dictionary(config, path_to_dictionary):
    logging.info(f"Path to dictionary: '{path_to_dictionary}'")
    dictionary = Dictionary(config)

    files = os.listdir(path_to_dictionary)
    for filename in files:
        path = os.path.join(path_to_dictionary, filename)
        logging.info(path)
        with open(path) as fh:
            data = safe_load(fh)

        dictionary.yaml_files.append(data)

        check_and_collect_grammar(config, data, dictionary, filename)
        origen = check_and_collect_origen(config, data, filename, dictionary)
        check_and_collect_categories(config, data, filename, dictionary)
        check_and_collect_lists(config, data, dictionary)

        if 'versions' not in data:
            raise LadinoError(f"The 'versions' field is missing from file '{filename}'")


        if 'examples' not in data:
            raise LadinoError(f"The 'examples' field is missing in '{filename}'")
        examples = data['examples']
        if examples == []:
            examples = None
        comments = data.get('comments')
        if comments == []:
            comments = None

        for version in data['versions']:
            if 'ladino' not in version:
                raise LadinoError(f"The ladino 'version' is missing from file '{filename}'")
            version['source'] = filename

            if 'translations' in version:
                make_them_list(version['translations'], filename)

            # Add examples and comments to the first version of the word.
            if examples is not None:
                version['examples'] = examples
                for example in examples:
                    if example.__class__.__name__ == 'str':
                        raise LadinoError(f"The example '{example}' is a string instead of a dictionary in '{filename}'")
                    for language in example.keys():
                        if language not in ['ladino', 'bozes'] and language not in languages:
                            raise LadinoError(f"Incorrect language '{language}' in example in '{filename}'")
                    dictionary.all_examples.append({
                        'example': example,
                        'word': version['ladino'].lower(),
                        'source':  filename,
                    })
                examples = None
            if comments is not None:
                version['comments'] = comments
                comments = None
            version['origen'] = origen
            dictionary.words.append(version)

        conjugations = config['tiempos']
        pronouns = config['pronombres']
        if 'conjugations' in data:
            for verb_time, conjugation in data['conjugations'].items():
                if verb_time not in conjugations:
                    raise LadinoError(f"Verb conjugation time '{verb_time}' is no recogrnized in '{filename}'")
                #print(conjugation)
                for pronoun, version in conjugation.items():
                    if pronoun not in pronouns:
                        raise LadinoError(f"Incorrect pronoun '{pronoun}' in verb time '{verb_time}' in '{filename}'")
                    if 'ladino' not in version:
                        raise LadinoError(f"The field 'ladino' is missing from verb time: '{verb_time}' pronoun '{pronoun}' in file '{filename}'")
                    version['source'] = filename
                    if 'translations' in version:
                        make_them_list(version['translations'], filename)
                    dictionary.words.append(version)
    #print(dictionary.words)
    #print(dictionary.all_examples[0])
    for cat in dictionary.categories.keys():
        dictionary.categories[cat].sort(key=lambda word: (word['versions'][0]['ladino'], word['versions'][0]['translations']['english']))
    for field in dictionary.origenes.keys():
        dictionary.origenes[field].sort(key=lambda word: (word['versions'][0]['ladino'], word['versions'][0]['translations']['english']))
    for lst in dictionary.lists.keys():
        lookup = {word:ix for ix, word in enumerate(config['listas'][lst])}
        dictionary.lists[lst].sort(key=lambda word: lookup[word['versions'][0]['ladino']])

    collect_data(dictionary)

    return dictionary

def add_word(word_mapping, source_language, target_language, source_word, target_words):
    if target_language not in word_mapping[source_language][source_word]:
        word_mapping[source_language][source_word][target_language] = []
    word_mapping[source_language][source_word][target_language].extend(target_words)
    word_mapping[source_language][source_word][target_language] = sorted(set(word_mapping[source_language][source_word][target_language]))

def add_ladino_word(original_word, accented_word, entry, dictionary):
    word = original_word.lower()
    logging.info(f"Add ladino word: '{original_word}' '{word}' '{accented_word}'")
    #print(entry)
    dictionary.count['dictionary']['ladino']['words'] += 1

    for example in entry.get('examples', []):
        if 'ladino' in example:
            dictionary.count['dictionary']['ladino']['examples'] += 1
    source_language = 'ladino'
    if word not in dictionary.word_mapping[source_language]:
        dictionary.word_mapping[source_language][word] = {}
    for target_language, target_words in entry['translations'].items():
        add_word(dictionary.word_mapping, source_language, target_language, word, target_words)
    add_word(dictionary.word_mapping, source_language, 'ladino', word, [original_word])

    if word not in dictionary.pages[source_language]:
        dictionary.pages[source_language][word] = []
    dictionary.pages[source_language][word].append(entry)
    dictionary.pages[source_language][word].sort(key=lambda x: (x['ladino'], x['translations']['english'][0] if x['translations']['english'] else ''))

    if accented_word and accented_word != word:
        add_word(dictionary.word_mapping, source_language, target_language='accented', source_word=word, target_words=[accented_word])

def add_translated_words(source_language, entry, dictionary):
    translations = entry['translations'].get(source_language)
    #print(f"{source_language}: {translations}")
    if translations is None:
        return

    for word in translations:
        word = word.lower()
        if word not in dictionary.word_mapping[source_language]:
            dictionary.word_mapping[source_language][word] = []
        dictionary.word_mapping[source_language][word].append(entry['ladino'])
        dictionary.word_mapping[source_language][word] = sorted(set(dictionary.word_mapping[source_language][word]))
        dictionary.count['dictionary'][source_language]['words'] += 1

        if word not in dictionary.pages[source_language]:
            dictionary.pages[source_language][word] = []
        dictionary.pages[source_language][word].append(entry)
        dictionary.pages[source_language][word].sort(key=lambda x: len(json.dumps(x, sort_keys=True)))



def collect_data(dictionary):
    logging.info("Collect more data")

    for entry in dictionary.words:
        add_ladino_word(entry['ladino'], entry.get('accented'), entry, dictionary)

        if 'alternative-spelling' in entry:
            for alt_entry in entry['alternative-spelling']:
                entry_copy = copy.deepcopy(entry)
                if 'bozes' in entry_copy:
                    del entry_copy['bozes']
                if 'bozes' in alt_entry:
                    entry_copy['bozes'] = alt_entry['bozes']
                if 'examples' in entry_copy:
                    entry_copy['examples'] = list(filter(lambda xyz: alt_entry['ladino'] in xyz['ladino'], entry['examples']))
                add_ladino_word(alt_entry['ladino'], alt_entry.get('accented'), entry_copy, dictionary)

        for language in languages:
            add_translated_words(language, entry, dictionary)


def load_examples(path_to_examples):
    extra_examples = []
    if os.path.exists(path_to_examples):
        for filename in os.listdir(path_to_examples):
            with open(os.path.join(path_to_examples, filename)) as fh:
                examples = safe_load(fh)
            #print(examples)
            for example in examples['examples']:
                extra_examples.append({
                    "example": example,
                    "source" : filename,
                })
    #print(extra_examples)
    return extra_examples


