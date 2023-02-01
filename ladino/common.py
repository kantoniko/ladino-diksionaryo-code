import re
import logging

class LadinoError(Exception):
    pass

languages = ['english', 'french', 'hebrew', 'spanish', 'turkish', 'portuguese']

def words_to_url(words):
    plain = re.sub(r'[^a-z0-9]', ' ', words.lower())
    plain = plain.strip()
    plain = re.sub(r'\s+', '-', plain)
    # logging.info(f"path: {plain}")

    # Make sure the path is not too long and ends with a full word.
    if len(plain) > 50:
        plain = plain[0:50]
        plain = plain[:plain.rindex('-')]
    # logging.info(f"path: {plain}")

    return plain


