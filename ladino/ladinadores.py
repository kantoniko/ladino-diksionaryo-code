import os
import sys
from yaml import safe_load

def load_ladinadores(root):
    with open(os.path.join(root, 'afishes.yaml')) as fh:
        data = safe_load(fh)
    images_dir = os.path.join(root, 'docs', 'afishes')
    yaml_dir = os.path.join(root, 'afishes')
    for filename in os.listdir(yaml_dir):
        # print(filename)
        img_filename = filename[0:-4] + 'jpg'
        # print(img_filename)
        img_path = os.path.join(images_dir, img_filename)
        if not os.path.exists(img_path):
            exit(f"Missing image from {img_path}")
        with open(os.path.join(yaml_dir, filename)) as fh:
            this = safe_load(fh)
            this["img"] = img_filename
            if (list(filter(lambda entry: entry["img"] == img_filename, data))):
                exit(f"File {img_filename} should be removed from afishes.yaml")
            data.append(this)

    images = set(os.listdir(images_dir))

    images_in_yaml = set()

    for entry in data:
        assert 'titulo' in entry
        assert len(entry['titulo']) > 5
        assert 'img' in entry
        assert os.path.exists(os.path.join(images_dir, entry['img']))
        images_in_yaml.add(entry['img'])

    if images != images_in_yaml:
        print(images-images_in_yaml)
        exit(1)

    return data

if __name__ == "__main__":
    if len(sys.argv) != 2:
        exit(f"Usage: {sys.argv[0]} path_to_los_ladinadores")
    data = load_ladinadores(sys.argv[1])
    print("Everything looks fine")
    #print(data)

