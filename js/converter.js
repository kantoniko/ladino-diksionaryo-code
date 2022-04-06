$(document).ready(function(){
    var english_to_ladino = null;
    var ladino_to_english = null;
    var dictionary = null;
    var loaded = 0;
    var direction = 'ladino-to-english';
    const languages = ['english', 'french', 'hebrew', 'portuguese', 'spanish', 'turkish'];
    const language_names = {
        'english'    : 'Inglez',
        'french'     : 'Fransez',
        'hebrew'     : 'Ebreo',
        'portuguese' : 'Portugez',
        'spanish'    : 'Kasteyano',
        'turkish'    : 'Turko'
    };

    // const update_direction_selector = function() {
    //     $('#ladino-to-english').removeClass('is-warning');
    //     $('#english-to-ladino').removeClass('is-warning');
    //     $('#' + direction).addClass('is-warning');
    // };

    var try_translate = function() {
        if (loaded == 3) {
            // update_direction_selector();
            translate();
        }
    };
    function onlyUnique(value, index, self) {
        return self.indexOf(value) === index;
    }
    function word_links(words, language) {
        words = words.filter(onlyUnique);
        return words;
        let links = Array();
        for (let tx=0; tx < words.length; tx++) {
            links.push(`<a href="/words/${language}/${words[tx]}.html">${words[tx]}</a>`);
        }
        return links;
    }

    var translate = function() {
        const original = $("#input-text").val();
        //const cleaned = original.replace(/["';,!?.:]/g, " ");
        //const cleaned = original.replace(/[^a-zA-Z-]/g, " ");
        const cleaned = original.replace(/[<>,.:!?"'\n*()=\[\]]/g, " ");
        const words = cleaned.split(" ");
        var html = `<table class="table">`;
        html += '<thead>';
        html += '<tr>';
        html += `<th>biervo</th><th>Ladino</th>`;
        for (var ix=0; ix < languages.length; ix++) {
            html += `<th>${language_names[languages[ix]]}</th>`;
        }
        html += '</tr>';
        html += '</thead>';
        html += '<tbody>';
        for (var ix = 0; ix < words.length; ix++) {
            if (words[ix] == "") {
                continue;
            }
            let word = words[ix].toLowerCase()
            console.log(word);
            const english_from_ladino = ladino_to_english ? ladino_to_english[word] : null;
            const ladino_from_english = english_to_ladino ? english_to_ladino[word] : null;

            let source_language = 'ladino';
            let dictionary_word = dictionary['ladino'][word];
            if (! dictionary_word) {
                for (var jx=0; jx < languages.length; jx++) {
                    source_language = languages[jx];
                    ladino_from_source_language = dictionary[source_language][word];
                    console.log('ladino', ladino_from_source_language);
                    if (ladino_from_source_language) {
                        // TODO: shall we include the dictionary entry of all the words?
                        // TODO: should be select a different one not necessarily the first one?
                        dictionary_word = dictionary['ladino'][ladino_from_source_language[0]];
                        break;
                    }
                }
            }
            console.log('dictionary word', dictionary_word)

            html += '<tr>';
            // original word
            if ((source_language == 'ladino' && dictionary_word) || english_from_ladino) {
                html += `<td class="has-background-success-light">${word}</td>`;
            } else {
                html += `<td class="has-background-danger-light">${word}</td>`;
            }

            // ladino column
            if (dictionary_word) {
                if (source_language == 'ladino') {
                    html += `<td>${word}</td>`;
                    //html += `<td><a href="/words/ladino/${word}.html">${word}</a></td>`;
                } else {
                    let links = word_links(ladino_from_source_language, "ladino");
                    html += `<td>${links}</td>`;
                }
            } else if (english_from_ladino) {
                html += `<td><a href="target/${word}.html">${word}</a></td>`;
            } else if (ladino_from_english) {
                html += `<td>${ladino_from_english}</td>`;
            } else {
                html += "<td></td>";
            }
                //html += `<td><a href="target/${word}.html">${word}</a></td>`;

            // all the other languages
            for (var jx=0; jx < languages.length; jx++) {
                if (dictionary_word) {
                    let links = Array();
                    let translated_words = dictionary_word[languages[jx]];
                    console.log('translated_words', translated_words);
                    if (translated_words) {
                        links = word_links(translated_words, languages[jx]);
                    }
                    const subhtml = links.join(", ");
                    if (source_language == languages[jx]) {
                        html += `<td class="has-background-success-light">${subhtml}</td>`;
                    } else {
                        html += `<td>${subhtml}</td>`;
                    }
                } else if (languages[jx] == 'english') {
                    if (english_from_ladino) {
                        html += `<td>${english_from_ladino}</td>`;
                    } else if (ladino_from_english) {
                        html += `<td class="has-background-success-light"><a href="source/${word}.html">${word}</a></td>`;
                    } else {
                        html += `<td></td>`;
                    }
                } else {
                    html += `<td></td>`;
                }
            }

            html += '</tr>';
        }
        html += '</tbody>';
        html += "</table>";
        //console.log(html);

        $("#output").html(html);
    };
    $.getJSON("dictionary.json", function(data){
        dictionary = data;
        loaded++;
        try_translate();
    }).fail(function(){
        console.log("An error has occurred while loading dictionary.json");
    });


    $.getJSON("source-to-target.json", function(data){
        english_to_ladino = data;
        loaded++;
        try_translate();
    }).fail(function(){
        console.log("An error has occurred while loading source-to-target.json.");
    });

    $.getJSON("target-to-source.json", function(data){
        ladino_to_english = data;
        loaded++;
        try_translate();
    }).fail(function(){
        console.log("An error has occurred while loading target-to-source.json.");
    });

    $('#input-text').bind('input propertychange', translate);
    //$("#ladino-to-english").click(function() {
    //    direction = 'ladino-to-english';
    //    update_direction_selector();
    //    translate();
    //});
    //$("#english-to-ladino").click(function() {
    //    direction = 'english-to-ladino';
    //    update_direction_selector();
    //    translate();
    //});
    //update_direction_selector();
});

