import json
import os
import shutil
import pytest

from librelingo_yaml_loader.yaml_loader import load_course
from generate import load_dictionary, collect_data, export_json


data_path = 'ladino-diksionaryo-data/words'
path_to_course = 'LibreLingo-Judeo-Spanish-from-English/course'

@pytest.mark.parametrize("name", ['andjinara'])
def test_one_file(tmpdir, name):
    print(tmpdir)
    shutil.copy(os.path.join(data_path, f'{name}.yaml'), os.path.join(tmpdir, f'{name}.yaml'))
    course = load_course(path_to_course)
    dictionary_source = load_dictionary(tmpdir)
    target, source, dictionary, count = collect_data(course, dictionary_source)
    export_json(dictionary_source, os.path.join(tmpdir, "dictionary_source.json"), pretty=True)
    export_json(dictionary, os.path.join(tmpdir, "dictionary.json"), pretty=True)
    export_json(count, os.path.join(tmpdir, "count.json"), pretty=True)

    with open (os.path.join('tests', name, 'dictionary_source.json')) as fh:
        expected = json.load(fh)
    assert dictionary_source == expected

    with open (os.path.join('tests', name, 'dictionary.json')) as fh:
        expected = json.load(fh)
    assert dictionary == expected
    with open (os.path.join('tests', name, 'count.json')) as fh:
        expected_count = json.load(fh)
    assert count == expected_count

