$(document).ready(function(){
    //const words = ['aki', 'ay', 'algunas', 'palavras', 'biervos', 'mas'];
    const dictionary = {
        'aki': 'here',
        'ay': 'there is',
        'algunas': 'some',
        'palavras': 'words',
        'biervos': 'words',
        'mas': 'more'
    };
    //$(".ladino").each(function() {
    //    const elem = $(this);
    //    var html = elem.html();
    //    console.log(html);
    //    html = html.replace(/(?<=^|[ >])([a-z]+)(?=[ <]|$)/g, `<span class="ladtr">$1</span>`);
    //    console.log(html);
    //    elem.html(html);
    //});

    $(".ladino").each(function() {
        const elem = $(this);
        var html = elem.html();
        console.log(html);
        html = html.replace(/(?<=^|[ >])([a-z]+)(?=[ <]|$)?/g, function (word) {
            var trans = dictionary[word];
            if (trans) {
                return `<span title="${trans}">${word}</span>`;
            } else {
                return word;
            }
        });
        console.log(html);
        elem.html(html);
    });

    //$(".ladtr").mouseenter(function (event) {
    //    console.log($(this).text());
    //});

    //    const words = elem.html().split(" ");
    //    for (var ix=0; ix<words.length; ix++) {
    //        console.log(words[ix]);
    //    }
    //    console.log('--');
    //})
    //let text = $(".ladino").html();
    //const words = text.split(" ");
    //    console.log(words[ix]);
    //}
    //    //$(".ladino").text($(".ladino").text().replace(words[ix], `<span class="ladtr">${words[ix]}</span>`));


    //console.log(text);
    //console.log(typeof(text));
    //$("
});

