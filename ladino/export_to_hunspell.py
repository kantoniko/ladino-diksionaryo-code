import os
import json
import datetime

def export_to_hunspell(dictionary, html_dir):
    hun_dir = os.path.join(html_dir, 'hunspell')
    os.makedirs(hun_dir, exist_ok=True)
    now = datetime.datetime.now()

    with open(os.path.join(hun_dir, "lad.dic"), "w") as fh:
        print(len(dictionary["ladino"].keys()), file=fh)
        for word in sorted(dictionary["ladino"].keys()):
            print(word, file=fh)

    with open(os.path.join(hun_dir, "lad.aff"), "w") as fh:
        print("SET UTF-8", file=fh)
        print("FLAG UTF-8", file=fh)
        rows = []
        for word in dictionary['spanish'].keys():
            if ' ' in word:
                continue
            for ladino in dictionary['spanish'][word]:
                if ' ' in ladino:
                    continue
                if word == ladino:
                    continue
                rows.append(f"REP {word} {ladino}")
        print(f"REP {len(rows)}", file=fh)
        for row in rows:
            print(row, file=fh)

if __name__ == "__main__":
    export()
