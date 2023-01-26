function translate(text, languages, dictionary) {
    const cleaned = text.replace(/[<>,;.:!?"'\n*()=\[\]\/\s]/g, " ");
    const words = cleaned.split(" ");
    let rows = [];
    for (var ix = 0; ix < words.length; ix++) {
        if (words[ix] == "") {
            continue;
        }
        const original_word = words[ix];
        const word = original_word.toLowerCase();
        //console.log(word);

        let source_language = 'ladino';
        let dictionary_word = dictionary['ladino'][word];
        let ladino_from_source_language = null;
        if (! dictionary_word) {
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
        }
        rows.push(
            {
                'source_language': source_language,
                'original_word': original_word,
                'dictionary_word': dictionary_word,
                'word': word,
                'ladino_from_source_language': ladino_from_source_language
            }
        );
        //console.log('dictionary word', dictionary_word)
    }
    return rows;
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

