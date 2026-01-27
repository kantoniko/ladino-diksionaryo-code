from yaml import safe_load
import datetime
import re
import os
import sys
import logging

LANGUAGES = ["ebreo", "inglez", "ladino"]

def get_messages(root):
    logging.info(f"WhatsApp: get_messages({root})")
    #print(root)
    with open(os.path.join(root, 'skip_image.yaml')) as fh:
        skip_image = safe_load(fh)
    with open(os.path.join(root, 'skip_sound.yaml')) as fh:
        skip_sound = safe_load(fh)
    with open(os.path.join(root, 'skip_source.yaml')) as fh:
        skip_source = safe_load(fh)

    entries = []
    yaml_files = os.listdir(os.path.join(root, 'text'))
    #print(yaml_files)
    ogg_files = set(os.listdir(os.path.join(root, 'sound')))
    #print(ogg_files)
    img_files = set(os.listdir(os.path.join(root, 'img')))
    pubs = {}
    for yaml_filename in yaml_files:
        if yaml_filename.endswith(".swp"):
            continue
        logging.info(f"Load text/{yaml_filename}")
        with open(os.path.join(root, 'text', yaml_filename)) as fh:
            data = safe_load(fh)

        data['yaml_filename'] = yaml_filename

        ogg_filename = yaml_filename.replace('.yaml', '.ogg')
        if ogg_filename in ogg_files:
            data['ogg'] = ogg_filename
            ogg_files.remove(ogg_filename)
        elif ogg_filename not in skip_sound:
            raise Exception(f"sound file {ogg_filename} does not exist in collected ogg_files and it is not listed in the skip_sound.yaml file either")

        data['page'] = yaml_filename.replace('.yaml', '')

        img_filename = yaml_filename.replace('.yaml', '.jpeg')
        if img_filename in img_files:
            data['img'] = img_filename
            img_files.remove(img_filename)
        elif img_filename not in skip_image:
            raise Exception(f"img file {img_filename} does not exist and it is not listed in the skip_image.yaml file either")
            #print(f"img file {img_filename} does not exist")

        if 'source' not in data:
            exit(f"Missing source in text/{yaml_filename}")
        if data['source'] is None or data['source'] == "":
            if yaml_filename not in skip_source:
                exit(f"Empty source in text/{yaml_filename}")
        elif data['source'] != "WhatsApp":
            if not re.search(r'^https://ladinokomunita.groups.io/g/main/message/\d+$', data['source'], flags=re.ASCII):
                exit(f"Invalid source='{data['source']}' in text/{yaml_filename}")

        if 'text' in data and 'teksto' in data:
            raise Exception(f"Both text and texto in text/{yaml_filename}")
        #print(data['text'])
        if 'text' in data:
            data['teksto'] = [{
                'ladino': data['text'].strip(),
                'ebreo': '',
            }]
            entries.append(data)
        elif 'teksto' in data:
            for entry in data['teksto']:
                for language in entry.keys():
                    if language not in LANGUAGES:
                        exit(f"Invalid language '{language}' in file text/{yaml_filename}")
                assert 'ladino' in entry, f"ladino field is missing in file text/{yaml_filename}"
                assert 'ebreo' in entry, f"ebreo field is missing in file text/{yaml_filename}"
                assert entry['ebreo'] is not None, f"ebreo field None in file text/{yaml_filename}"
                #assert entry['ladino'] != "", f"ladino field is empty in file text/{yaml_filename} where ebreo field is {entry['ebreo']}"
                #assert entry['ebreo'] != "", f"ebreo field is empty in file text/{yaml_filename}"
                assert re.search(r'^[äàüãéèâáöğçşıíÉéóúÇ`💐 a-zA-Z0-9()/=,;%&?!:."\'-]*$', entry['ladino']), f"The ladino field contains an invalid character in file text/{yaml_filename} '{entry['ladino']}'"
                #assert re.search(r'^[`Ia-zA-Z💐 0-9.,!?:;()%"/\' \u05D0-\u05EA-]*$', entry['ebreo']), f"The ebreo field contains an invalid character in file text/{yaml_filename} '{entry['ebreo']}'"
            entries.append(data)
        else:
            raise Exception('No text and no teksto')

        check_date(data['pub'], yaml_filename)

        if data['pub'] in pubs:
            other = pubs[data['pub']]
            raise Exception(f"Duplicate publication date {data['pub']} in text/{yaml_filename} and in text/{other}")
        pubs[data['pub']] = yaml_filename

        assert len(data['titulo']) > 4
    if ogg_files:
        raise Exception(f"Some sound files {ogg_files} are not in use")
    if img_files:
        raise Exception(f"Some img files {img_files} are not in use")

    return sorted(entries, key=lambda entry: entry['pub'])

def check_date(pub, yaml_filename):
    cases = {
            r'^\d\d\d\d\.\d\d\.\d\d \d\d:\d\d:\d\d$' : '%Y.%m.%d %H:%M:%S',
            r'^\d\d\d\d\.\d\d\.\d\d \d\d:\d\d$'      : '%Y.%m.%d %H:%M',
            r'^\d\d\d\d\.\d\d\.\d\d$'                : '%Y.%m.%d',
    }
    date_parsing_format = None
    for regex, date_format in cases.items():
        match = re.search(regex, pub, flags=re.ASCII)
        if match:
            date_parsing_format = date_format

    if date_parsing_format is None:
        exit(f"Incorrectly formatted date '{pub}' in text/{yaml_filename}")

    try:
        datetime.datetime.strptime(pub, date_parsing_format)
    except ValueError:
        exit(f"Invalid date '{pub}' in text/{yaml_filename}")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        exit(f"Usage: {sys.argv[0]} path_to_whatsapeando")
    logging.basicConfig(level=logging.INFO)
    entries = get_messages(sys.argv[1])
    #print(entries)
    print(f"All read properly.")
    print(f"Last published:   {entries[-1]['pub']} - {entries[-1]['titulo']} {entries[-1]['yaml_filename']}")
    print(f"Today is          {str(datetime.date.today()).replace('-', '.')}")

