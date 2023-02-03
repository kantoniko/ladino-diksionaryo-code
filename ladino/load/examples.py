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
            with open(os.path.join(path_to_examples, filename)) as fh:
                examples = safe_load(fh)
            if examples is None:
                raise LadinoError(f"The example file '{filename}' is empty.")
            # print('examples:', examples)
            for example in examples:
                # logging.info(f'example: {example}')
                if example.__class__.__name__ == 'str':
                    raise LadinoError(f"The example '{example}' is a string instead of a dictionary in '{filename}'")
                for language in example.keys():
                    if language not in ['ladino', 'bozes', 'words'] and language not in languages:
                        raise LadinoError(f"Incorrect language '{language}' in example in '{filename}'")
                example['source'] = filename
                example['url'] = words_to_url(example['ladino'])
                all_examples.append(example)

    # print('all_examples:', all_examples)
    return all_examples

