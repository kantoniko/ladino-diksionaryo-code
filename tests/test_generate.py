import json
import os
import shutil
import pytest

from ladino.generate import load_dictionary, collect_data, LadinoError, load_config, export_examples, export_to_html


real_repo_path = 'ladino-diksionaryo-data'
data_path  = os.path.join(real_repo_path, 'words')
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
examples_path  = os.path.join(root, 'tests', 'files', 'good')

# Explanation why each word is included in the tests:
# andjinara: our first test word. noun. for now it does not have a plural.
# komer: verb
# komo: has several meanings
# biblia: word is capitalized
# klaro: has comments; has examples

@pytest.mark.parametrize("name", ['andjinara', 'komer', 'komo', 'biblia', 'klaro', 'all', 'minimal', 'capital_letters'])
def test_one_file(tmpdir, request, name):
    print(tmpdir)
    path_to_words = os.path.join(tmpdir, 'words')
    print(path_to_words)
    os.makedirs(path_to_words, exist_ok=True)

    shutil.copy(os.path.join(real_repo_path, 'config.yaml'), os.path.join(tmpdir, f'config.yaml'))
    example = os.path.join(examples_path, f"{name}.yaml")
    words = ['andjinara', 'komer', 'komo']
    if name == 'all':
        for word in words:
            shutil.copy(os.path.join(data_path, f'{word}.yaml'), os.path.join(tmpdir, 'words', f'{word}.yaml'))
    elif os.path.exists(example):
        shutil.copy(example, os.path.join(tmpdir, 'words', f'{name}.yaml'))
    else:
        shutil.copy(os.path.join(data_path, f'{name}.yaml'), os.path.join(tmpdir, 'words', f'{name}.yaml'))

    # export in case we would like to update the files in the tests/files/ directory
    save = request.config.getoption("--save")
    if save:
        html_dir = os.path.join(root, 'tests', 'files', name)
        os.makedirs(html_dir, exist_ok=True)
    else:
        html_dir = os.path.join(tmpdir, 'html')
    os.makedirs(html_dir, exist_ok=True)

    path_to_repo = str(tmpdir)
    config = load_config(path_to_repo)
    dictionary_source, all_examples = load_dictionary(config, os.path.join(path_to_repo, 'words'))
    dictionary, count, pages = collect_data(dictionary_source)
    export_to_html(dictionary, count, pages, html_dir, pretty=True)
    export_examples(all_examples, pages['ladino'], html_dir)
    os.unlink(os.path.join(html_dir, 'about.html'))
    os.unlink(os.path.join(html_dir, 'index.html'))
    shutil.rmtree(os.path.join(html_dir, 'css'))
    shutil.rmtree(os.path.join(html_dir, 'js'))


    if not save:
        cmd = f"diff -r {os.path.join(root, 'tests', 'files', name)} {os.path.join(tmpdir, 'html')}"
        print(cmd)
        assert os.system(cmd) == 0

@pytest.mark.parametrize("name,expected", [
    ('no_grammar', "The 'grammar' field is missing from file 'no_grammar.yaml'"),
    ('bad_grammar', "Invalid grammar 'Strange' in file 'bad_grammar.yaml'"),
    ('no_origen', "The 'origen' field is missing from file 'no_origen.yaml'"),
    ('bad_origen', "Invalid origen 'Strange' in file 'bad_origen.yaml'"),
    ('no_versions', "The 'versions' field is missing from file 'no_versions.yaml'"),
    ('noun_no_gender', "The 'gender' field is None in 'noun_no_gender.yaml' version {'ladino': 'klaro'}"),
    ('noun_bad_gender', "Invalid value 'droid' in 'gender' field in 'noun_bad_gender.yaml' version {'ladino': 'klaro', 'gender': 'droid'}"),
    ('verb_no_conjugation', "Grammar is 'verb', but there is NO 'conjugations' field in 'verb_no_conjugation.yaml'"),
])
def test_bad(tmpdir, name, expected):
    shutil.copy(os.path.join(root, 'tests', 'files', 'bad', f'{name}.yaml'), os.path.join(tmpdir, f'{name}.yaml'))
    with pytest.raises(Exception) as err:
        dictionary_source, all_examples = load_dictionary(load_config(real_repo_path), tmpdir)
    assert err.type == LadinoError
    assert str(err.value) == expected


