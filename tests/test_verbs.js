assert = require('assert');
const verbs = require('.././ladino/js/verbs');
let res = verbs.conjugations("komer");

komer = {
    to: "komer",
    prezente: {
      yo: 'komo',
      tu: 'komes',
      el: 'kome',
      moz: 'komemos',
      voz: 'komésh',
      eyos: 'komen'
    },
    imperfekto: {
      yo: 'komía',
      tu: 'komías',
      el: 'komía',
      moz: 'komíamos',
      voz: 'komíash',
      eyos: 'komían'
    },
    pasado: {
      yo: 'komí',
      tu: 'komites',
      el: 'komió',
      moz: 'komimos',
      voz: 'komitesh',
      eyos: 'komieron'
    },
    futuro: {
      yo: 'komeré',
      tu: 'komerás',
      el: 'komerá',
      moz: 'komeremos',
      voz: 'komerésh',
      eyos: 'komerán'
    },
    subjunktivo: {
      yo: 'koma',
      tu: 'komas',
      el: 'koma',
      moz: 'komamos',
      voz: 'komásh',
      eyos: 'koman'
    },
    subjunktivo_imperfekto: {
      yo: 'komiera',
      tu: 'komieras',
      el: 'komiera',
      moz: 'komiéramos',
      voz: 'komierash',
      eyos: 'komieran'
    },
    kondisional: {
      yo: 'komería',
      tu: 'komerías',
      el: 'komería',
      moz: 'komeríamos',
      voz: 'komeríash',
      eyos: 'komerían'
    },
    imperativo: {
      tu: 'kome',
      el: 'komas',
      voz: 'komed',
      eyos: 'komásh'
    },
    infinitivo: 'komer',
    djerundivo: 'komiendo',
    partisipio_pasado: 'komido'
};
//console.log(res)

assert.deepEqual(res, komer);
console.log("All good");

