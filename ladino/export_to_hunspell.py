import json
import datetime

def export_to_hunspell(dictionary):
    now = datetime.datetime.now()

    with open("lad.dic", "w") as fh:
        print(len(dictionary["ladino"].keys()), file=fh)
        for word in sorted(dictionary["ladino"].keys()):
            print(word, file=fh)

    with open("lad.aff", "w") as fh:
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
