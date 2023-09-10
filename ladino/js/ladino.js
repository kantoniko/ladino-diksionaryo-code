function translate(text, languages, dictionary) {
    const cleaned = text.replace(/[<>,;.:!?"'\n*()=\[\]\/\s]/g, " ");
    const words = cleaned.split(" ");
    let rows = [];
    for (var ix = 0; ix < words.length; ix++) {
        if (words[ix] == "") {
            continue;
        }
        let result = translate_word(words[ix], languages, dictionary);
        rows.push(result);
    }
    return rows;
}

function translate_word(original_word, languages, dictionary) {
    //console.log(word);
    const word = original_word.toLowerCase();

    let response = from_ladino(word, dictionary);
    if (response["dictionary_word"]) {
        response["original_word"] = original_word;
        return response;
    }

    let source_language = 'ladino';
    let dictionary_word = '';
    // console.log(`try '${word}' in translations`);
    for (var jx=0; jx < languages.length; jx++) {
        //console.log("check language:", languages[jx]);
        source_language = languages[jx];
        ladino_from_source_language = dictionary[source_language][word];
        //console.log('ladino', ladino_from_source_language);
        if (ladino_from_source_language) {
            // TODO: shall we include the dictionary entry of all the words?
            // TODO: should be select a different one not necessarily the first one?
            dictionary_word = dictionary['ladino'][ladino_from_source_language[0]];
            break;
        }
    }

    //console.log('dictionary word', dictionary_word)
    return {
        'source_language': source_language,
        'original_word': original_word,
        'dictionary_word': dictionary_word,
        'word': word,
        'ladino_from_source_language': ladino_from_source_language
    }
}

function from_ladino(word, dictionary) {
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
        'dictionary_word': dictionary_word,
        'word': word,
        'ladino_from_source_language': ladino_from_source_language,
    }
}


function lookup(text, languages, dictionary) {
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
