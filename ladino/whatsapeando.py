from yaml import safe_load
import datetime
import re
import os
import sys
import logging

skip_image = [
    'akel-tyempo-akeya-noche-en-izmir.jpeg',
    'akel-tyempo-yossi-banay.jpeg',
    'akel-tyempo-la-sinyatura-de-hitler.jpeg',
    'akel-tyempo-trikotar.jpeg',
    'akel-tyempo-ken-es.jpeg',
]

def get_messages(root):
    logging.info(f"WhatsApp: get_messages({root})")
    #print(root)
    entries = []
    yaml_files = os.listdir(os.path.join(root, 'text'))
    #print(yaml_files)
    ogg_files = set(os.listdir(os.path.join(root, 'sound')))
    #print(ogg_files)
    img_files = set(os.listdir(os.path.join(root, 'img')))
    pubs = set()
    for yaml_filename in yaml_files:
        if yaml_filename.endswith(".swp"):
            continue
        logging.info(f"Load {yaml_filename})")
        with open(os.path.join(root, 'text', yaml_filename)) as fh:
            data = safe_load(fh)

        ogg_filename = yaml_filename.replace('.yaml', '.ogg')
        if ogg_filename not in ogg_files:
            raise Exception(f"sound file {ogg_filename} does not exist")
        ogg_files.remove(ogg_filename)
        data['filename'] = ogg_filename

        data['page'] = yaml_filename.replace('.yaml', '')

        img_filename = yaml_filename.replace('.yaml', '.jpeg')
        if img_filename in img_files:
            data['img'] = img_filename
            img_files.remove(img_filename)
        elif img_filename not in skip_image:
            raise Exception(f"img file {img_filename} does not exist")
            #print(f"img file {img_filename} does not exist")

        #print(data['text'])
        if 'text' in data:
            data['teksto'] = [{
                'ladino': data['text'].strip(),
                'ebreo': '',
            }]
            entries.append(data)
        elif 'teksto' in data:
            for entry in data['teksto']:
                assert 'ladino' in entry, f"ladino field is missing in file {yaml_filename}"
                assert 'ebreo' in entry, f"ebreo field is missing in file {yaml_filename}"
                assert entry['ebreo'] is not None, f"ebreo field None in file {yaml_filename}"
            entries.append(data)
        else:
            raise Exception('No text and no teksto')

        assert re.search(r'^\d\d\d\d\.\d\d\.\d\d$', data['data'], re.ASCII)
        try:
            datetime.datetime.strptime(data['data'], '%Y.%m.%d')
        except ValueError:
            exit(f"Invalid date {data['data']}")

        match = re.search(r'^(\d\d\d\d\.\d\d\.\d\d)( \d\d:\d\d:\d\d)?$', data['pub'], re.ASCII)
        assert match
        data['date'] = match.group(1)

        try:
            datetime.datetime.strptime(data['date'], '%Y.%m.%d')
        except ValueError:
            exit(f"Invalid date {data['pub']}")


        if data['pub'] in pubs:
            raise Exception(f"Duplicate publication date {data['pub']}")
        pubs.add(data['pub'])

        assert len(data['titulo']) > 4
    if ogg_files:
        raise Exception(f"Some sound files {ogg_files} are not in use")
    if img_files:
        raise Exception(f"Some img files {img_files} are not in use")

    return sorted(entries, key=lambda entry: entry['pub'])


if __name__ == '__main__':
    if len(sys.argv) != 2:
        exit(f"Usage: {sys.argv[0]} path_to_whatsapeando")
    logging.basicConfig(level=logging.INFO)
    entries = get_messages(sys.argv[1])
    #print(entries)
    print(f"All read properly.")
    print(f"Last published:   {entries[-1]['pub']} - {entries[-1]['titulo']} {entries[-1]['filename'].replace('ogg','yaml')}")
    print(f"Today is          {str(datetime.date.today()).replace('-', '.')}")

