The code behind https://diksionaryo.szabgab.com/


## Development environment

Clone this project:

```
git clone https://github.com/szabgab/ladino-diksionaryo-code.git
```

Clone https://github.com/szabgab/LibreLingo-Judeo-Spanish-from-English and https://github.com/szabgab/ladino-diksionaryo-data/ using
the following commands:

```
git clone https://github.com/szabgab/LibreLingo-Judeo-Spanish-from-English.git
git clone https://github.com/szabgab/ladino-diksionaryo-data.git
```

Alternatively you can clone them in some other place and then add symbolic links so they will be accessible as
the subdirectories `LibreLingo-Judeo-Spanish-from-English` and `ladino-diksionaryo-data` of this project.


```
pip install -r requirements.txt
git python generate.py --course LibreLingo-Judeo-Spanish-from-English/course/ --html html --dictionary ladino-diksionaryo-data/words/ --log
```

This will generate the static files in the `html` subdrirectory.

Launch a static web server in the `html` subdirectory.

## Testing

```
pytest -sv test_generate.py
```

the expected output files are in the `tests` subdirectory.

When the expected output changes we can update the files with the following command:

```
pytest -sv test_generate.py --save
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
