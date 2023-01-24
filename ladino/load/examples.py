import os
from yaml import safe_load
import logging

from ladino.common import words_to_url

def load_examples(path_to_examples):
    logging.info(f"load_examples({path_to_examples})")
    extra_examples = []
    if os.path.exists(path_to_examples):
        for filename in os.listdir(path_to_examples):
            logging.info(f"load_examples from '{filename}'")
            with open(os.path.join(path_to_examples, filename)) as fh:
                examples = safe_load(fh)
            #print(examples)
            for example in examples['examples']:
                extra_examples.append({
                    "example": example,
                    "source" : filename,
                    'url': words_to_url(example['ladino']),
                })
    #print(extra_examples)
    return extra_examples


