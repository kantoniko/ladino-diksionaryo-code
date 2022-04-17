from ladino.generate import load_dictionary, collect_data, export_dictionary_pages, export_dictionary_lists, load_config

repo_path = 'ladino-diksionaryo-data'
data_path = 'ladino-diksionaryo-data/words'

def test_all(tmpdir):
    print(tmpdir)
    dictionary_source, all_examples = load_dictionary(load_config(repo_path), data_path)
    dictionary, count, pages = collect_data(dictionary_source)
    export_dictionary_pages(pages, tmpdir)
    export_dictionary_lists(pages, tmpdir)
