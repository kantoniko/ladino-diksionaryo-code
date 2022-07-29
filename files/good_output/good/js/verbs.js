function conjugations(verb) {
    let data = {
        "to": verb
    };
    if (verb.endsWith('er')) {
        let root = verb.slice(0, -2);
        data['prezente'] = {
            'yo': root + 'o',
            'tu': root + 'es',
            'el': root + 'e',
            'moz': root + 'emos',
            'voz': root + 'ésh',
            'eyos': root + 'en',
        }
        data['imperfekto'] = {
            'yo': root + 'ía',
            'tu': root + 'ías',
            'el': root + 'ía',
            'moz': root + 'íamos',
            'voz': root + 'íash',
            'eyos': root + 'ían',
        }
        data['pasado'] = {
            'yo': root + 'í',
            'tu': root + 'ites',
            'el': root + 'ió',
            'moz': root + 'imos',
            'voz': root + 'itesh',
            'eyos': root + 'ieron',
        }
        data['futuro'] = {
            'yo': root + 'eré',
            'tu': root + 'erás',
            'el': root + 'erá',
            'moz': root + 'eremos',
            'voz': root + 'erésh',
            'eyos': root + 'erán',
        }
        data['subjunktivo'] = {
            'yo': root + 'a',
            'tu': root + 'as',
            'el': root + 'a',
            'moz': root + 'amos',
            'voz': root + 'ásh',
            'eyos': root + 'an',
        }
        data['subjunktivo_imperfekto'] = {
            'yo': root + 'iera',
            'tu': root + 'ieras',
            'el': root + 'iera',
            'moz': root + 'iéramos',
            'voz': root + 'ierash',
            'eyos': root + 'ieran',
        }
        data['kondisional'] = {
            'yo': root + 'ería',
            'tu': root + 'erías',
            'el': root + 'ería',
            'moz': root + 'eríamos',
            'voz': root + 'eríash',
            'eyos': root + 'erían',
        }
        data['imperativo'] = {
            'tu': root + 'e',
            'el': root + 'as',
            'voz': root + 'ed',
            'eyos': root + 'ásh',
        }
        data['infinitivo'] = root + "er",
        data['djerundivo'] = root + "iendo",
        data['partisipio_pasado'] = root + "ido"
    }

    return data
}
