$(document).ready(function(){
    var dictionary = null;
    var loaded = 0;
    const available_languages = ['english', 'french', 'hebrew', 'portuguese', 'spanish', 'turkish'];
    //console.log(window.innerWidth, window.innerHeight);
    const language_names = {
        'english'    : 'Inglez',
        'french'     : 'Fransez',
        'hebrew'     : 'Ebreo',
        'portuguese' : 'Portugez',
        'spanish'    : 'Kasteyano',
        'turkish'    : 'Turko'
    };
    // We save the text in local storage and restore it when the user visits next time.
    // especially useful when people click on words and than get back to the main page.
    $("#input-text").val(localStorage.getItem('original'));

    var try_translate = function() {
        if (loaded == 1) {
            translate();
        }
    };

    function get_languages() {
        let languages = [];
        const config = get_config();
        for (let ix=0; ix < available_languages.length; ix++) {
            const language = available_languages[ix];
            if (config['lashon'][ language ] == '1') {
                languages.push(language);
            }
        }
        //console.log(languages)
        return languages;
    }


    function get_config() {
        const config_str = localStorage.getItem('config');

        let config;
        if (config_str) {
            config = JSON.parse(config_str);
        } else {
            config = {
                'lashon': {
                    'english': '1',
                    'spanish': '1',
                    'turkish': '1',
                    'french' : '0',
                    'hebrew' : '0',
                    'portuguese' : '0',
                }
            };
        }
        //console.log(config);
        return config;
    }

    function onlyUnique(value, index, self) {
        return self.indexOf(value) === index;
    }
    function word_links(words, language) {
        words = words.filter(onlyUnique);
        if (language != 'ladino') {
            return words;
        }
        let links = Array();
        for (let tx=0; tx < words.length; tx++) {
            links.push(`<a href="/words/${language}/${words[tx]}.html">${words[tx]}</a>`);
        }
        return links;
    }

    var translate = function() {
        const original = $("#input-text").val();
        localStorage.setItem('original', original);
        if (/^\s*$/.exec(original)) {
            $('#welcome-message').removeClass('is-hidden');
            $('#output').addClass('is-hidden');
            return;
        }
        $('#welcome-message').addClass('is-hidden');
        $('#output').removeClass('is-hidden');

        const cleaned = original.replace(/[<>,;.:!?"'\n*()=\[\]\/\s]/g, " ");
        const words = cleaned.split(" ");
        var html = `<table class="table">`;
        html += '<thead>';
        html += '<tr>';
        html += `<th>biervo</th><th>Ladino</th>`;
        const languages = get_languages();
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
            const original_word = words[ix];
            const word = original_word.toLowerCase();
            //console.log(word);

            let source_language = 'ladino';
            let dictionary_word = dictionary['ladino'][word];
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
            //console.log('dictionary word', dictionary_word)

            html += '<tr>';
            // original word
            if (source_language == 'ladino' && dictionary_word) {
                html += `<td class="has-background-success-light">${original_word}</td>`;
            } else {
                html += `<td class="has-background-danger-light">${original_word}</td>`;
            }

            // ladino column
            if (dictionary_word) {
                if (source_language == 'ladino') {
                    html += `<td><a href="/words/ladino/${word}.html">${dictionary_word['ladino']}</a></td>`;
                } else {
                    let links = word_links(ladino_from_source_language, "ladino");
                    html += `<td>${links}</td>`;
                }
            } else {
                html += "<td></td>";
            }

            // all the other languages
            for (var jx=0; jx < languages.length; jx++) {
                //console.log('show language', languages[jx]);
                if (dictionary_word) {
                    let links = Array();
                    let translated_words = dictionary_word[languages[jx]];
                    //console.log('translated_words', translated_words);
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
                    html += `<td></td>`;
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

    $('#input-text').bind('input propertychange', translate);
    $('#show-config').click(function () {
        //console.log('show config');
        $(".navbar-burger").toggleClass("is-active");
        $(".navbar-menu").toggleClass("is-active");

        const config = get_config();
        for (let ix=0; ix < available_languages.length; ix++) {
            const language = available_languages[ix];
            const checked = config['lashon'][ language ] == "1";
            $(`#enable-${language}`).prop("checked", checked);
        }

        $("#config").addClass('is-active');
        //$("#config").addClass('is-clipped');
        //console.log('added');
    });
    $('#cancel-config').click(function (event) {
        $("#config").removeClass('is-active');
        event.stopPropagation();
    });
    $('#save-config').click(function (event) {
        $("#config").removeClass('is-active');
        let config = get_config();
        for (let ix=0; ix < available_languages.length; ix++) {
            const language = available_languages[ix];
            config['lashon'][ language ] = $(`#enable-${language}`).is(":checked") ? "1" : "0";
        }

        localStorage.setItem('config', JSON.stringify(config))
        translate();
        event.stopPropagation();
    });

    const get_words = function() {
        let stored = {
            "ok": [],
            "failed" : [],
        };
        const stored_words_json = localStorage.getItem('ladino_words');
        if (stored_words_json) {
            stored = JSON.parse(stored_words_json)
        }
        return stored;
    }

    const start_game = function(status="") {
        //console.log("status: ", status);

        let stored = get_words();

        if (status != "") {
            const old_word = $('#game-text').html();
            const word_type = $('#game-text').attr("word-type");
            //console.log(old_word);
            //console.log(word_type);
            if (word_type != "") {
                stored[word_type].shift();
            }
            if (status != "later") {
                stored[status].push(old_word);
            }
            localStorage.setItem('ladino_words', JSON.stringify(stored));
        }

        const words = Object.keys(dictionary["ladino"]);

        let word = words[Math.floor(Math.random() * words.length)];
        $('#game-text').attr("word-type", "");
        const which = Math.random();
        if (stored["ok"].length + stored["failed"].length > 10) {
            if (stored["ok"].length > 0 && which > 0.75) {
                word = stored["ok"][0];
                $('#game-text').attr("word-type", "ok");
            }
            if (stored["failed"].length > 0 && 0.75 > which && which > 0.5) {
                $('#game-text').attr("word-type", "failed");
                word = stored["failed"][0];
            }
        }
        //console.log(words.length);
        console.log($('#game-text').attr("word-type"));
        const translations = dictionary["ladino"][word]["english"].join(", ");

        $("#game-translation").addClass('is-hidden')
        $('#game-text').html(word);

        $('#game-translation').html(translations);
        $("#game-reveal").removeClass('is-hidden');
        $("#game-ok").addClass('is-hidden')
        $("#game-fail").addClass('is-hidden')
        $("#game-later").addClass('is-hidden')
    };

    $('#show-game').click(function () {
        $(".navbar-burger").toggleClass("is-active");
        $(".navbar-menu").toggleClass("is-active");
        $("#game").addClass('is-active');
        start_game();
    });
    $("#game-reveal").click(function(event) {
        $('#game-translation').removeClass('is-hidden');
        $("#game-reveal").addClass('is-hidden');
        $("#game-ok").removeClass('is-hidden');
        $("#game-fail").removeClass('is-hidden');
        $("#game-later").removeClass('is-hidden');
    });
    $("#game-ok").click(function(event) {
        start_game("ok");
    });
    $("#game-fail").click(function(event) {
        start_game("failed");
    });
    $("#game-later").click(function(event) {
        start_game("later");
    });


    $('#game-close').click(function () {
        $("#game").removeClass('is-active');
    });
});

