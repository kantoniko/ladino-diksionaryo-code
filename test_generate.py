import json
import os
import shutil
import pytest

from librelingo_yaml_loader.yaml_loader import load_course
from generate import load_dictionary, collect_data, export_to_html, export_json, export_dictionary_pages, LadinoError


data_path = 'ladino-diksionaryo-data/words'
path_to_course = 'LibreLingo-Judeo-Spanish-from-English/course'


# Explanation why each word is included in the tests:
# andjinara: our first test word. noun. for now it does not have a plural.
# komer: verb
# komo: has several meanings
# biblia: word is capitalized
# klaro: has comments; has examples

@pytest.mark.parametrize("name", ['andjinara', 'komer', 'komo', 'biblia', 'klaro', 'all'])
def test_one_file(tmpdir, request, name):
    print(tmpdir)
    words = ['andjinara', 'komer', 'komo']
    if name == 'all':
        for word in words:
            shutil.copy(os.path.join(data_path, f'{word}.yaml'), os.path.join(tmpdir, f'{word}.yaml'))
    else:
        shutil.copy(os.path.join(data_path, f'{name}.yaml'), os.path.join(tmpdir, f'{name}.yaml'))

    course = load_course(path_to_course)
    #course = None
    dictionary_source = load_dictionary(tmpdir)
    target, source, dictionary, count, pages = collect_data(course, dictionary_source)
    # export in case we would like to update the files in the tests/ directory
    save = request.config.getoption("--save")
    if save:
        html_dir = os.path.join('tests', name)
        os.makedirs(html_dir, exist_ok=True)
    else:
        html_dir = tmpdir
    #export_to_html(course, target, source, dictionary, count, html_dir, pretty=True)
    export_json(dictionary, os.path.join(html_dir, "dictionary.json"), pretty=True)
    export_json(count, os.path.join(html_dir, "count.json"), pretty=True)
    export_dictionary_pages(pages, html_dir)

    if name == 'all':
        for word in words:
            os.unlink(os.path.join(tmpdir, f'{word}.yaml'))
    else:
        os.unlink(os.path.join(tmpdir, f'{name}.yaml'))

    if not save:
        cmd = f"diff -r {os.path.join('tests', name)} {tmpdir}"
        print(cmd)
        assert os.system(cmd) == 0
    #with open (os.path.join('tests', name, 'dictionary.json')) as fh:
    #    expected_dictionary = json.load(fh)
    #assert dictionary == expected_dictionary
    #with open (os.path.join('tests', name, 'count.json')) as fh:
    #    expected_count = json.load(fh)
    #assert count == expected_count

def test_all(tmpdir):
    print(tmpdir)
    course = load_course(path_to_course)
    #course = None
    dictionary_source = load_dictionary(data_path)
    target, source, dictionary, count, pages = collect_data(course, dictionary_source)
    export_dictionary_pages(pages, tmpdir)

def test_minimal(tmpdir):
    name = 'minimal'
    shutil.copy(os.path.join('tests', 'bad', f'{name}.yaml'), os.path.join(tmpdir, f'{name}.yaml'))
    dictionary_source = load_dictionary(tmpdir)

@pytest.mark.parametrize("name,expected", [
    ('no_grammar', "The 'grammar' field is missing from file 'no_grammar.yaml'"),
    ('bad_grammar', "Invalid grammar 'Strange' in file 'bad_grammar.yaml'"),
    ('no_origen', "The 'origen' field is missing from file 'no_origen.yaml'"),
    ('bad_origen', "Invalid origen 'Strange' in file 'bad_origen.yaml'"),
    ('no_versions', "The 'versions' field is missing from file 'no_versions.yaml'"),
    ('noun_no_gender', "The 'gender' field is None in 'noun_no_gender.yaml' version {'ladino': 'klaro'}"),
    ('noun_bad_gender', "Invalid value 'droid' in 'gender' field in 'noun_bad_gender.yaml' version {'ladino': 'klaro', 'gender': 'droid'}"),
])
def test_bad(tmpdir, name, expected):
    shutil.copy(os.path.join('tests', 'bad', f'{name}.yaml'), os.path.join(tmpdir, f'{name}.yaml'))
    with pytest.raises(Exception) as err:
        dictionary_source = load_dictionary(tmpdir)
    assert err.type == LadinoError
    assert str(err.value) == expected


