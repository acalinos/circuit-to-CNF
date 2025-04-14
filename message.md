Sto lavorando all'implementazione DES in Python (con inversione dei bit nei byte prima dell'IP e dopo la FP), ma non riesco a ottenere il ciphertext atteso dal test vector (plaintext "0123456789ABCDEF", chiave "0000000000000000", ciphertext atteso "95F8A5E5DD31D900"). Nonostante abbia controllato permutazioni, sottochiavi, S-Box, ecc., il risultato finale è sempre sbagliato (ad esempio ottengo "8D5C961AA0B30044"). Sembra un problema nell'ordine dei bit o nella gestione delle inversioni, e non riesco a capirlo.

Potrebbe darmi qualche dritta per capire cosa non va?

Grazie mille,

[Il Tuo Nome]