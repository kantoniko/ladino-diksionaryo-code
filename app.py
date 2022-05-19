import os
from flask import Flask, send_file

app = Flask(__name__)
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'docs')

@app.route("/")
def main():
    return send_file(os.path.join(root, 'index.html'))

@app.route("/<path:fullpath>")
def all(fullpath):
    extensions = ['.js', '.css', '.json', '.ico']
    for ext in extensions:
        if fullpath.endswith(ext):
            path = os.path.join(root, fullpath)
            if os.path.exists(path):
                return send_file(path)
            else:
                #print(f"No file {path}")
                return '', 404

    return send_file(os.path.join(root, f"{fullpath}.html"))
