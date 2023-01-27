import sys
import json
import os
import shutil
import pytest
import glob

from ladino.generate import main
from ladino.load.dictionary import load_dictionary, load_config
from ladino.load.examples import load_examples
from ladino.common import LadinoError

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Explanation why each word is included in the tests:
# andjinara: our first test word. noun. for now it does not have a plural.
# komer: verb
# komo: has several meanings
# biblia: word is capitalized
# klaro: has comments; has examples

def test_no_params():
    sys.argv = [sys.argv[0]]
    main()

@pytest.mark.parametrize("name", ['good', 'real'])
def test_one(tmpdir, request, name):
    print(tmpdir)

    # export in case we would like to update the files in the files/good_output/ directory
    save = request.config.getoption("--save")
    if save:
        html_dir = os.path.join(root, 'files', name, 'output')
    else:
        html_dir = os.path.join(tmpdir, 'html')
    os.makedirs(html_dir, exist_ok=True)

    sys.argv = [sys.argv[0], '--all', '--html',  html_dir, '--dictionary', os.path.join(root, 'files', name, 'data'), '--pretty']
    if name == 'real':
        sys.argv.extend(['--whatsapp', 'files/real/estamos-whatsapeando/'])
        sys.argv.extend(['--unafraza', 'files/real/una-fraza-al-diya/'])
    print(sys.argv)
    main()

    if len(os.listdir(os.path.join(html_dir, 'verbos'))) == 0:
        os.rmdir(os.path.join(html_dir, 'verbos'))
    shutil.rmtree(os.path.join(html_dir, 'hunspell'))
    shutil.rmtree(os.path.join(html_dir, 'he'))
    os.unlink(os.path.join(html_dir, 'statistika.html')) # has the date of generation in it
    os.unlink(os.path.join(html_dir, 'dictionaries.html')) # has changing link in it
    os.unlink(os.path.join(html_dir, 'echar-lashon.html')) # has changing date in it
    #if name != 'good':
    #    for filepath in glob.glob(f'{html_dir}/*-*.html'):
    #        os.unlink(filepath)
    #    for cat in config['kategorias']:
    #        os.unlink(os.path.join(html_dir, 'kategorias', f'{cat}.html'))

    if not save:
        cmd = f"diff -r {os.path.join(root, 'files', name, 'output')} {os.path.join(tmpdir, 'html')}"
        print(cmd)
        assert os.system(cmd) == 0

@pytest.mark.parametrize("name,expected", [
    ('has_examples_field', "There was an 'examples' field 'has_examples_field.yaml' (it is deprecated)"),
    ('no_grammar', "The 'grammar' field is missing from file 'no_grammar.yaml'"),
    ('bad_grammar', "Invalid grammar 'Strange' in file 'bad_grammar.yaml'"),
    ('no_origen', "The 'origen' field is missing from file 'no_origen.yaml'"),
    ('bad_origen', "Invalid origen 'Strange' in file 'bad_origen.yaml'"),
    ('no_versions', "The 'versions' field is missing from file 'no_versions.yaml'"),
    ('noun_no_gender', "The 'gender' field is None in 'noun_no_gender.yaml' version {'ladino': 'klaro'}"),
    ('noun_bad_gender', "Invalid value 'droid' in 'gender' field in 'noun_bad_gender.yaml' version {'ladino': 'klaro', 'gender': 'droid'}"),
    ('noun_no_number', "The 'number' field is None in 'noun_no_number.yaml' version {'ladino': 'klaro', 'gender': 'masculine'}"),
    ('noun_bad_number', "The 'number' field is 'countless' in 'noun_bad_number.yaml' version {'ladino': 'klaro', 'gender': 'masculine', 'number': 'countless'}"),
    ('verb_no_conjugation', "Grammar is 'verb', but there is NO 'conjugations' field in 'verb_no_conjugation.yaml'"),
    ('non_verb_with_conjugation', "Grammar is NOT a 'verb', but there are conjugations in 'non_verb_with_conjugation.yaml'"),
    ('version_without_ladino', "The ladino 'version' is missing from file 'version_without_ladino.yaml'"),
    ('verb_wrong_conjugation_time', "Verb conjugation time 'other' is no recogrnized in 'verb_wrong_conjugation_time.yaml'"),
    ('verb_wrong_pronoun', "Incorrect pronoun 'you' in verb time 'prezente' in 'verb_wrong_pronoun.yaml'"),
    ('verb_conjugation_missing_ladino', "The field 'ladino' is missing from verb time: 'prezente' pronoun 'yo' in file 'verb_conjugation_missing_ladino.yaml'"),
])
def test_bad_word(tmpdir, name, expected):
    bad_input_dir = os.path.join(root, 'files', 'bad_input')
    shutil.copy(os.path.join(bad_input_dir, f'{name}.yaml'), os.path.join(tmpdir, f'{name}.yaml'))
    with pytest.raises(Exception) as err:
        dictionary_source, all_examples = load_dictionary(load_config(bad_input_dir), None, tmpdir)
    assert err.type == LadinoError
    assert str(err.value) == expected


@pytest.mark.parametrize("name,expected", [
    ('example_without_language', "The example 'Una palavra i un biervo.' is a string instead of a dictionary in 'example_without_language.yaml'"),
    ('example_with_incorrect_language', "Incorrect language 'klingon' in example in 'example_with_incorrect_language.yaml'"),
])
def test_bad_examples(tmpdir, name, expected):
    bad_input_dir = os.path.join(root, 'files', 'bad_input')
    shutil.copy(os.path.join(bad_input_dir, f'{name}.yaml'), os.path.join(tmpdir, f'{name}.yaml'))
    with pytest.raises(Exception) as err:
        examples = load_examples(tmpdir)
    assert err.type == LadinoError
    assert str(err.value) == expected

