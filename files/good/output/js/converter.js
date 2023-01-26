$(document).ready(function(){
    var dictionary = null;
    var loaded = 0;
    const site = {
        'available_languages': ['english', 'french', 'hebrew', 'portuguese', 'spanish', 'turkish'],
        'language_names': {
            'english'    : 'inglez',
            'french'     : 'fransez',
            'hebrew'     : 'ebreo',
            'portuguese' : 'portugez',
            'spanish'    : 'kasteyano',
            'turkish'    : 'turko'
        }
    };
    //console.log(window.innerWidth, window.innerHeight);
    // We save the text in local storage and restore it when the user visits next time.
    // especially useful when people click on words and than get back to the main page.
    $("#input-text").val(localStorage.getItem('original'));

    var try_translate = function() {
        if (loaded == 1) {
            display_translate();
        }
    };

    function get_languages() {
        let languages = [];
        const config = get_config();
        for (let ix=0; ix < site.available_languages.length; ix++) {
            const language = site.available_languages[ix];
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
                },
                'search-type': 'multi-search',
            };
        }
        //console.log(config);
        return config;
    }

    function show_input(idx) {
        $('#input-text').addClass('is-hidden');
        $('#input-expression').addClass('is-hidden');
        $('#input-lucky').addClass('is-hidden');
        $(idx).removeClass('is-hidden');
        save_config_search_type();
        try_translate();
    };

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
            links.push(`<a href="/words/${language}/${words[tx]}">${words[tx]}</a>`);
        }
        return links;
    }

    const display_lucky = function() {
        const words = Object.keys(dictionary["ladino"]);
        const word = words[Math.floor(Math.random() * words.length)];
        console.log(word);
        console.log(dictionary['ladino'][word])
        let html = '';
        html += '<div>Kada vez tu klikas en el boton de Mazal, vas a ver otra palavra. Tu puedes ambezarte la palavra o tu puedes eskrivir frazas i kontribuir al diksionaryo.</div>';
        html += `<h3><a href="/words/ladino/${word}">${word}</a></h3>`;
        $("#output").html(html);
    }

    function show_welcome() {
        $('#welcome-message').removeClass('is-hidden');
        $('#output').addClass('is-hidden');
    }

    function hide_welcome() {
        $('#welcome-message').addClass('is-hidden');
        $('#output').removeClass('is-hidden');
    }

    var display_translate = function() {
        let original;
        const languages = get_languages();

        if ($('#single-search').prop('checked')) {
            original = $("#input-expression").val().toLowerCase();
            save_config_search_text();
        } else if ($('#multi-search').prop('checked')) {
            original = $("#input-text").val();
            localStorage.setItem('original', original);
        } else if ($('#lucky-search').prop('checked')) {
            hide_welcome();
            display_lucky();
            return;
        } else {
            console.log('ohoh');
        }
        if (/^\s*$/.exec(original)) {
            show_welcome();
            return;
        }
        hide_welcome();

        let rows = [];
        let count;
        const row_limit = 20;
        if ($('#single-search').prop('checked')) {
            rows = lookup(original, languages, dictionary);
            count = rows.length;
            rows = rows.slice(0, row_limit);
            //console.log(count);
        } else if ($('#multi-search').prop('checked')) {
            rows = translate(original, languages, dictionary);
        //} else if ($('#lucky-search').prop('checked')) {
        } else {
            console.log('ohoh');
        }
        //console.log(rows);

        var html = '';
        if (count) {
            html += `<span>Mostramos ${rows.length} ekspresiones de un total de ${count} ke topamos.</span>`;
        }
        html += `<table class="table">`;
        html += '<thead>';
        html += '<tr>';
        html += `<th>biervo</th><th>Ladino</th>`;
        for (var ix=0; ix < languages.length; ix++) {
            html += `<th>${site.language_names[languages[ix]]}</th>`;
        }
        html += '</tr>';
        html += '</thead>';
        html += '<tbody>';


        for (var ix = 0; ix < rows.length; ix++) {
            let row = rows[ix];
            html += '<tr>';
            // original word
            if (row.source_language == 'ladino' && row.dictionary_word) {
                html += `<td class="has-background-success-light">${row.original_word}</td>`;
            } else {
                html += `<td class="has-background-danger-light">${row.original_word}</td>`;
            }

            // ladino column
            if (row.dictionary_word) {
                if (row.source_language == 'ladino') {
                    html += `<td><a href="/words/ladino/${row.word}">${row.dictionary_word['ladino']}</a></td>`;
                } else {
                    let links = word_links(row.ladino_from_source_language, "ladino");
                    html += `<td>${links}</td>`;
                }
            } else {
                html += "<td></td>";
            }

            // all the other languages
            for (var jx=0; jx < languages.length; jx++) {
                //console.log('show language', languages[jx]);
                if (row.dictionary_word) {
                    let links = Array();
                    let translated_words = row.dictionary_word[languages[jx]];
                    //console.log('translated_words', translated_words);
                    if (translated_words) {
                        links = word_links(translated_words, languages[jx]);
                    }
                    const subhtml = links.join(", ");
                    if (row.source_language == languages[jx]) {
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

    $('#input-text').bind('input propertychange', display_translate);
    $('#show-config').click(function () {
        //console.log('show config');
        $(".navbar-burger").toggleClass("is-active");
        $(".navbar-menu").toggleClass("is-active");

        const config = get_config();
        for (let ix=0; ix < site.available_languages.length; ix++) {
            const language = site.available_languages[ix];
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
        for (let ix=0; ix < site.available_languages.length; ix++) {
            const language = site.available_languages[ix];
            config['lashon'][ language ] = $(`#enable-${language}`).is(":checked") ? "1" : "0";
        }

        localStorage.setItem('config', JSON.stringify(config))
        display_translate();
        event.stopPropagation();
    });

    function save_config_search_text() {
        let config = get_config();
        config['search-text'] = $("#input-expression").val();
        localStorage.setItem('config', JSON.stringify(config));
    }

    function save_config_search_type() {
        let config = get_config();
        config['search-type'] = 'multi-search';
        if ($('#single-search').prop('checked')) {
            config['search-type'] = 'single-search';
        }
        if ($('#multi-search').prop('checked')) {
            config['search-type'] = 'multi-search';
        }
        if ($('#lucky-search').prop('checked')) {
            config['search-type'] = 'lucky-search';
        }
        localStorage.setItem('config', JSON.stringify(config));
    }

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

    $('#multi-search').change(function() {
        show_input('#input-text');
    });

    $('#single-search').change(function() {
        show_input('#input-expression');
    });
    $('#input-expression').on('input', display_translate)

    $('#lucky-search').change(function() {
        show_input('#input-lucky');
    });

    $('#input-lucky').click(function () {
        try_translate();
    });

    const config = get_config();
    if ('search-text' in config) {
        $("#input-expression").val(config['search-text']);
    }
    if (! 'search-type' in config) {
        config['search-type'] = 'multi-search';
    }
    if (config['search-type'] == 'single-search') {
        $('#single-search').prop('checked', 'true');
        show_input('#input-expression');
    } else if (config['search-type'] == 'multi-search') {
        $('#multi-search').prop('checked', 'true');
        show_input('#input-text');
    } else if (config['search-type'] == 'lucky-search') {
        $('#lucky-search').prop('checked', 'true');
        show_input('#input-lucky');
    }

});

