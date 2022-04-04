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
