import os
from yaml import safe_load
import logging

from ladino.common import LadinoError, languages, words_to_url

def load_examples(path_to_examples):
    logging.info(f"load_examples({path_to_examples})")
    all_examples = []
    if os.path.exists(path_to_examples):
        for filename in os.listdir(path_to_examples):
            logging.info(f"load_examples from '{filename}'")
            try:
                with open(os.path.join(path_to_examples, filename)) as fh:
                    example = safe_load(fh)
            except Exception as err:
                raise LadinoError(f"The example file '{filename}' is not a valid YAML file.")

            # logging.info(f'example: {example}')
            if example.__class__.__name__ == 'str':
                raise LadinoError(f"The example '{example}' is a string instead of a dictionary in '{filename}'")
            for language in example.keys():
                if language not in ['ladino', 'audio', 'words', 'source'] and language not in languages:
                    raise LadinoError(f"Incorrect language '{language}' in example in '{filename}'")
            example['filename'] = filename
            if 'ladino' not in example:
                # print(example)
                raise LadinoError(f"Key 'ladino' is missing from example in '{filename}'")
            example['url'] = words_to_url(example['ladino'])
            all_examples.append(example)

    return all_examples

