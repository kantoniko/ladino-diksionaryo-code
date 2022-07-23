import os

def pytest_addoption(parser):
    parser.addoption("--save", action='store_true')


def data_repo_path():
    for real_repo_path  in ['ladino-diksionaryo-data', '../ladino-diksionaryo-data']:
        if os.path.exists(real_repo_path):
            break
    else:
        raise Exception("Could not find path to ladino-diksionaryo-data")
    return real_repo_path

