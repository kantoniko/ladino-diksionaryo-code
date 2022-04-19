from ladino.generate import main
import sys

repo_path = 'ladino-diksionaryo-data'

def test_all(tmpdir):
    print(tmpdir)
    sys.argv = [sys.argv[0], '--all', '--html',  str(tmpdir), '--dictionary', repo_path]
    main()
