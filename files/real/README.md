# What do we test with each file?


* The past tense of `venir` is `vino` and there is a noun which is also `vino`. We wanted to make sure the both appear in the search and both are listed on the page of the word 'vino'.
* The example that starts with `Ospital.` has a link to the word `opsital` but not in the other direction. The parsing of the sentence in the `word to example` mapping was incorrect.
* files/real/estamos-whatsapeando/text/akel-tyempo-ya-vino-la-ora-1.yaml was added as it has the word 'vino' in it and we have that word in two different meanings so we would like to make sure the whatsapp messages is only listed once. It also has both Hebrew and Ladino text.
* aftaha.yaml has the field `origen-lingua`.
