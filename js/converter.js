$(document).ready(function(){
    var english_to_ladino = null;
    var ladino_to_english = null;
    var dictionary = null;
    var course_data = null;
    var loaded = 0;
    var direction = 'ladino-to-english';

    // const update_direction_selector = function() {
    //     $('#ladino-to-english').removeClass('is-warning');
    //     $('#english-to-ladino').removeClass('is-warning');
    //     $('#' + direction).addClass('is-warning');
    // };

    var try_translate = function() {
        if (loaded == 4) {
            // update_direction_selector();
            translate();
        }
    };
    var translate = function() {
        const original = $("#input-text").val();
        //const cleaned = original.replace(/["';,!?.:]/g, " ");
        //const cleaned = original.replace(/[^a-zA-Z-]/g, " ");
        const cleaned = original.replace(/[<>,.:!?"'\n*()=\[\]]/g, " ");
        const words = cleaned.split(" ");
        let languages = Object.keys(dictionary).filter(function(name) { return name != 'ladino'}) ;
        languages.sort();
        // console.log(languages);
        var html = `<table class="table">`;
        html += '<thead>';
        html += '<tr>';
        html += `<th>?</th><th>ladino</th>`;
        for (var ix=0; ix < languages.length; ix++) {
            html += `<th>${languages[ix]}</th>`;
        }
        html += '</tr>';
        html += '</thead>';
        html += '<tbody>';
        for (var ix = 0; ix < words.length; ix++) {
            if (words[ix] == "") {
                continue;
            }
            let word = words[ix].toLowerCase()
            const english_from_ladino = ladino_to_english[word];
            const ladino_from_english = english_to_ladino[word];

            html += '<tr>';
            let source_language = 'ladino';
            let dict_word = dictionary['ladino'][word];
            if (! dict_word) {
                for (var jx=0; jx < languages.length; jx++) {
                    source_language = languages[jx];
                    ladino_from_source_language = dictionary[source_language][word];
                    //console.log(ladino_from_source_language);
                    if (ladino_from_source_language) {
                        dict_word = dictionary['ladino'][ladino_from_source_language];
                        break;
                    }
                }
            }

            // original word
            if ((source_language == 'ladino' && dict_word) || english_from_ladino) {
                html += `<td class="has-background-success-light">${word}</td>`;
            } else {
                html += `<td class="has-background-danger-light">${word}</td>`;
            }

            // ladino column
            if (dict_word) {
                // console.log(dict_word);
                if (source_language == 'ladino') {
                    html += `<td>${word}</td>`;
                } else {
                    html += `<td>${ladino_from_source_language}</td>`;
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
                if (dict_word) {
                    if (source_language == languages[jx]) {
                        html += '<td class="has-background-success-light">' + (dict_word[languages[jx]] || '') + '</td>';
                    } else {
                        html += '<td>' + (dict_word[languages[jx]] || '') + '</td>';
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
    $.getJSON("course.json", function(data){
        course_data = data;
        loaded++;
        try_translate();
    }).fail(function(){
        console.log("An error has occurred.");
    });

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
        console.log("An error has occurred.");
    });

    $.getJSON("target-to-source.json", function(data){
        ladino_to_english = data;
        loaded++;
        try_translate();
    }).fail(function(){
        console.log("An error has occurred.");
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

