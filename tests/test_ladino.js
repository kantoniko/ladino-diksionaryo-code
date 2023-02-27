assert = require('assert');
const ladino = require('.././ladino/js/ladino');
const fs = require('fs');


const dict_path = process.env.LADINO_DIR + '/dictionary.json';

const komer = [
  {
    dictionary_word: {
      accented: [
        'komér'
      ],
      inglez: [
        'eat'
      ],
      fransez: [
        'manger'
      ],
      ladino: [
        'komer'
      ],
      portugez: [],
      kasteyano: [
        'comer'
      ],
      turko: [
        'yemek yemek'
      ]
    },
    ladino_from_source_language: null,
    original_word: 'komer',
    source_language: 'ladino',
    word: 'komer'
  }
];

fs.readFile(dict_path, 'utf8', (err, data) => {
    if (err) {
        console.log(`Error reading file from disk: ${err}`);
    } else {
        dictionary = JSON.parse(data);

        let res = ladino.translate("komer", ['inglez'], dictionary);
        //console.log(res);

        assert.deepEqual(res, komer);
        console.log("All good");
    }
});


