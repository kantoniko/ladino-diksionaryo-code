The code behind https://kantoniko.com/


## Development environment

Create a folder called `kantoniko`. Inside that folder clone the repositories of https://github.com/kantoniko/

Clone this project that contains the code. This is enought to run the tests and develop the code.

```
git clone https://github.com/kantoniko/ladino-diksionaryo-code.git
```

In order to work with the real data of the dictionary clone https://github.com/kantoniko/ladino-diksionaryo-data/ using the following command:

```
git clone https://github.com/kantoniko/ladino-diksionaryo-data.git
```


### Install the dependencies.

```
pip install -r requirements.txt -c constraints.txt
```

### Testing

```
pytest -vvs tests/test_generate.py
pytest -vvs -rA -x --log-cli-level=DEBUG --random-order tests/test_generate.py
```

the expected output files are in the `tests` subdirectory.

When the expected output changes we can update the files with the following command:

```
pytest -vvs tests/test_generate.py --save
```

Generate test coverage report:

```
pytest -vvs -rA -x --log-cli-level=DEBUG --random-order --cov=ladino --cov-report html --cov-report term --cov-branch tests/test_generate.py
```

## Generate the site locally

These commands will generate the static files in the `docs` subdrirectory. Below you'll find the command to start a local web server to view the results.

### Generate test pages

Some selected pieces of data (words, examples, etc.) that we stored in the repository of the code to serve us for testing.

./generate_sample.sh

### Generate only the dictionary

For this we need the data repository cloned.

```
PYTHONPATH=. python ladino/generate.py --dictionary ../ladino-diksionaryo-data/ --html docs --all --log
```

This took 3.20 on my computer wheren there were 3321 words and 1556 example in the `ladino-diksionaryo-data` repository.


### Generate the whole site locally

For this we need all the repositories to be cloned.

```
./generate_all.sh
```

```
time PYTHONPATH=. python ladino/generate.py --dictionary ../ladino-diksionaryo-data/ --html docs --all --log --whatsapp ../ladino-estamos-whatsapeando/ --sounds ../ladino-diksionaryo-sounds/ --unafraza ../ladino-una-fraza-al-diya/ --pages ../ladino-pages --books ../ladino-salu-lulu/  --ladinadores ../ladino-los-ladinadores/ --limit 10
```


Launch a static web server with the following command:

## Run locally

```
./app.py
```

or

```
FLASK_DEBUG=1 flask run
```

## Language considerations

* Verbs in Ladino have a lot of conjugations. (are there as many as in modern Spanish?)

* Several forms of the same verb translate to the same form in English:
  yo komo     I eat
  to komes    you eat

* On the other hand they translate to both feminine and masculine in Hebrew
  yo komo     אני אוכל / אני אוכלת

* "komo" has other meanings as well, for exampl "like" and "how?"

* Some nouns, such as "meza" = "table" have a single gender but they have both singular (meza) and plural form ("mezas").
* Some nouns, such as "elevo" =  "student" have both masculine (elevo) and feminine (eleva) form in singular and (elevos, elevas) in plural.
* Some words, such as "klaro" = "clear" can act noun, adjective, or adverb (at least in modern Spanish).
  The English translation (clear) can also act as verb which then translates back to aklarar.

## Design

From the yaml files we generate several json files and several static html files.

* `dictionary.json`

```
    "ladino": {
        "kome": {
            "ladino": "kome",
            "translations": {
                "inglez": "eats",
                "kasteyano": "come"
            }
        },
    },
    "inglez": {
        "eat": "komen",
        "eats": "kome"
    },

```

### Rashi fonts

https://fonts.google.com/noto/specimen/Noto+Rashi+Hebrew/about

