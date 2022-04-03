import json
import os
import shutil

from librelingo_yaml_loader.yaml_loader import load_course
from generate import load_dictionary, collect_data, export_json


data_path = 'ladino-diksionaryo-data/words'
path_to_course = 'LibreLingo-Judeo-Spanish-from-English/course'

def test_andjinara(tmpdir):
    print(tmpdir)
    shutil.copy(os.path.join(data_path, 'andjinara.yaml'), os.path.join(tmpdir, 'andjinara.yaml'))
    course = load_course(path_to_course)
    dictionary_source = load_dictionary(tmpdir)
    #print(dictionary_source)
    assert dictionary_source == [{
        'ladino': 'andjinara',
        'accented': 'andjinára',
        'gender': 'feminine',
        'number': 'singular',
        'alternative-spelling': [{'ladino': 'endjinara', 'accented': 'endjinára'}],
        'translations': {
            'english': 'artichoke',
            'french': 'artichaut',
            'hebrew': 'ארטישוק',
            'spanish': ['alcaucil', 'alcachofa'],
            'turkish': 'enginar'
        }
    }]
    target, source, dictionary, count = collect_data(course, dictionary_source)
    export_json(
        dictionary, "dictionary.json", tmpdir
    )
    export_json(
        count, "count.json", tmpdir
    )

    #print(target)
    #print(source)
    #print(dictionary)
    #print(count)
    with open (os.path.join('tests', 'andjinara', 'dictionary.json')) as fh:
        expected = json.load(fh)
    assert dictionary == expected
    with open (os.path.join('tests', 'andjinara', 'count.json')) as fh:
        expected_count = json.load(fh)
    assert count == expected_count

