from ladino.generate import main
import sys
import os

for real_repo_path  in ['ladino-diksionaryo-data', '../ladino-diksionaryo-data']:
    if os.path.exists(real_repo_path):
        break
else:
    raise Exception("Could not find path to ladino-diksionaryo-data")


def test_all(tmpdir):
    print(tmpdir)
    sys.argv = [sys.argv[0], '--all', '--html',  str(tmpdir), '--dictionary', real_repo_path]
    main()
    os.environ["LADINO_DIR"] = str(tmpdir)
    assert os.system("node tests/test_verbs.js") == 0
