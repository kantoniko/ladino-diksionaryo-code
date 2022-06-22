import re

class LadinoError(Exception):
    pass

languages = ['english', 'french', 'hebrew', 'spanish', 'turkish', 'portuguese']

def words_to_url(words):
    plain = re.sub(r'[^a-z0-9]', ' ', words.lower())
    plain = plain.strip()
    plain = re.sub(r'\s+', '-', plain)
    return plain


