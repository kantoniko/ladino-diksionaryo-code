from ladino.export import get_separate_words

def test_get_separate_words():
    assert get_separate_words("una palavra") == {'una', 'palavra'}
    assert get_separate_words("una. palavra!") == {'una', 'palavra'}
    assert get_separate_words("una palavra i otra Palavra") == {'una', 'i', 'otra', 'palavra'}
