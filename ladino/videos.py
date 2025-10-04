import os
import re
import sys
import logging


import markdown


def load_videos(path):
    logging.info(f"load_videos from  '{path}'")
    path_to_md_file = os.path.join(path, 'README.md')
    with open(path_to_md_file) as fh:
        text = fh.read()
    readme = markdown.markdown(text, extensions=['tables'])

    path_to_md_file = os.path.join(path, 'kurto.md')
    with open(path_to_md_file) as fh:
        text = fh.read()
    short = markdown.markdown(text, extensions=['tables'])

    videos = []

    for filename in os.listdir(os.path.join(path, 'videos')):
        logging.info(f"video: '{filename}'")
        with open(os.path.join(path, 'videos', filename)) as fh:
            header = {}
            in_header = False
            for line in fh:
                line = line.rstrip("\n")
                if line == '---':
                    if header:
                        break
                    in_header = True
                    continue
                field, value = line.split(':', 1)
                field = field.strip()
                value = value.strip()
                header[field] = value
            header['text'] = convert(fh.read())
            header['filename'] = filename[:-4]

            match = re.search(r'^https://www.youtube.com/watch\?v=(.*)$', header['url'])
            if not match:
                raise Exception(f"Invalid URL {header['url']}")
            header["embed"] = "https://www.youtube.com/embed/" + match.group(1)
            videos.append(header)

    videos.sort(key=lambda video: video['data'], reverse=True)

    people = collect_people(videos)

    return videos, readme, short, people

def convert(text):
    text = re.sub(r'\[([\d:]+)\]', r'<p><b>\1</b>', text)
    text = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', text)
    text = re.sub(r'^$', '<p>\n', text, flags=re.MULTILINE)
    return text

def name_to_uid(name):
    name = name.strip()
    return name.lower().replace(' ', '-')

def collect_people(videos):
    people = {}
    for video in videos:
        video['people'] = {}
        for field in ['balabaya', 'musafires']:
            uids = []
            if not video[field]:
                continue
            for name in video[field].split(','):
                uid = name_to_uid(name)
                uids.append(uid)
                if uid not in people:
                    people[uid] = {
                        "name": name,
                        "videos": [],
                    }
                people[uid]["videos"].append(video)
            video['people'][field] = uids
    return people


