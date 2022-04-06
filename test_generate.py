import json
import os
import shutil
import pytest

from librelingo_yaml_loader.yaml_loader import load_course
from generate import load_dictionary, collect_data, export_to_html, export_json, export_dictionary_pages


data_path = 'ladino-diksionaryo-data/words'
path_to_course = 'LibreLingo-Judeo-Spanish-from-English/course'

@pytest.mark.parametrize("name", ['andjinara', 'komer', 'komo', 'all'])
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

