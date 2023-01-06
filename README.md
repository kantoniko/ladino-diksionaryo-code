The code behind https://kantoniko.com/


## Development environment

Clone this project:

```
git clone https://github.com/kantoniko/ladino-diksionaryo-code.git
```

Clone https://github.com/kantoniko/ladino-diksionaryo-data/ using the following command:

```
git clone https://github.com/kantoniko/ladino-diksionaryo-data.git
```

Alternatively you can clone it in some other place and then add symbolic link so it will be accessible as
the subdirectory `ladino-diksionaryo-data` of this project.


```
pip install -r requirements.txt
PYTHONPATH=. python ladino/generate.py --dictionary ../ladino-diksionaryo-data/ --html docs --all --log
time PYTHONPATH=. python ladino/generate.py --dictionary ../ladino-diksionaryo-data/ --html docs --all --log --whatsapp ../ladino-estamos-whatsapeando/ --sounds ../ladino-diksionaryo-sounds/ --unafraza ../ladino-una-fraza-al-diya/ --pages ../ladino-pages --books ../ladino-salu-lulu/  --ladinadores ../ladino-los-ladinadores/ --limit 10
```

This will generate the static files in the `docs` subdrirectory.

Launch a static web server with the following command:

## Run locally

```
FLASK_DEBUG=1 flask run
```

## Testing

```
pytest -vvs tests/test_generate.py
pytest -vvs -rA -x --log-cli-level=DEBUG --random-order tests/test_generate.p
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

## Language considerations

* Verbs in Ladino have a lot of conjugations. (are there are many as in modern Spanish?)

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
                "english": "eats",
                "spanish": "come"
            }
        },
    },
    "english": {
        "eat": "komen",
        "eats": "kome"
    },

```

### Rashi fonts

https://fonts.google.com/noto/specimen/Noto+Rashi+Hebrew/about

