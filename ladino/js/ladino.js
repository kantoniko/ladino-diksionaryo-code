function translate(text, original_language, languages, dictionary) {
    //console.log("translate from original_language:", original_language);
    const cleaned = text.replace(/[<>,;.:!?"'\n*()=\[\]\/\s]/g, " ");
    const words = cleaned.split(" ");
    let rows = [];
    for (var ix = 0; ix < words.length; ix++) {
        if (words[ix] == "") {
            continue;
        }
        if (original_language == "automatik") {
            rows.push( translate_word(words[ix], languages, dictionary) );
        } else if (original_language == "ladino") {
            //console.log("ladino");
            rows.push( from_ladino(words[ix], dictionary) );
        } else {
            //console.log("language");
            rows.push( from_language(original_language, words[ix], dictionary) );
        }
    }
    return rows;
}

function translate_word(original_word, languages, dictionary) {
    //console.log(word);
    const word = original_word.toLowerCase();

    let response = from_ladino(original_word, dictionary);
    if (response["dictionary_word"]) {
        return response;
    }

    let source_language = 'ladino';
    let dictionary_word = '';
    // console.log(`try '${word}' in translations`);
    for (var jx=0; jx < languages.length; jx++) {
        if (languages[jx] == "rashi") {
            //console.log("skip rashi");
            continue;
        }
        response = from_language(languages[jx], original_word, dictionary);
        if (response["dictionary_word"]) {
            return response;
        }
    }

    //console.log('dictionary word', dictionary_word)
    return {
        'source_language': source_language,
        'original_word': original_word,
        'dictionary_word': '',
        'word': word,
        'ladino_from_source_language': ''
    }
}

function from_language(source_language, original_word, dictionary) {
    //console.log(`from_language: ${source_language} ${original_word}`);
    const word = original_word.toLowerCase();
    ladino_from_source_language = dictionary[source_language][word];
    //console.log('ladino', ladino_from_source_language);
    if (ladino_from_source_language) {
        // TODO: shall we include the dictionary entry of all the words?
        // TODO: should be select a different one not necessarily the first one?
        let dictionary_word = dictionary['ladino'][ladino_from_source_language[0]];
        if (dictionary_word) {
            return {
                'source_language': source_language,
                'original_word': original_word,
                'dictionary_word': dictionary_word,
                'word': word,
                'ladino_from_source_language': ladino_from_source_language
            }
        }
    }
    return {
        'source_language': source_language,
        'original_word': original_word,
        'dictionary_word': '',
        'word': word,
        'ladino_from_source_language': ladino_from_source_language
    }
}

function from_ladino(original_word, dictionary) {
    //console.log(`from_ladino(${original_word}, ...)`);
    const word = original_word.toLowerCase();
    let dictionary_word = dictionary['ladino'][word];
    let ladino_from_source_language = null;

    if (! dictionary_word) {
        // console.log(`try accented '${word}'`);
        // console.log(dictionary["accented"]);
        ladino_from_source_language = dictionary["accented"][word];
        // console.log("ladino_from_source_language:", ladino_from_source_language);
        if (ladino_from_source_language) {
            dictionary_word = ladino_from_source_language[0];
            // console.log(dictionary_word);
        }
    }
    return {
        'source_language': 'ladino',
        'original_word': original_word,
        'dictionary_word': dictionary_word,
        'word': word,
        'ladino_from_source_language': ladino_from_source_language,
    }
}


function lookup(text, dictionary) {
    const cleaned = text.replace(/[<>,;.:!?"'\n*()=\[\]\/\s]/g, " ");
    const ladino = Object.keys(dictionary["ladino"]);
    //console.log(cleaned);

    let source_language = 'ladino';
    let rows = [];
    for (let ix=0; ix < ladino.length; ix++) {
        let ladino_word = ladino[ix];
        if (ladino_word.includes(cleaned)) {
            let dictionary_word = dictionary['ladino'][ladino_word];
            rows.push(
                {
                    'source_language': source_language,
                    'original_word': '',
                    'dictionary_word': dictionary_word,
                    'word': ladino_word
                }
            );
        }
    }
    return rows;
}

module.exports.translate = translate;
module.exports.lookup = lookup;

