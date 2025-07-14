A. Supponi di avere un qualunque circuito costruito con la nuova libreria e supponi di fissare il valore di alcuni degli input (x) e di tutti gli output del circuito (y). Mì aspetto che il problema di determinare se esiste un valore dei rimanenti input del circuito che sia consistente con x e y possa diventare un problema SAT e che possa essere risolto in tal modo.
Verificherei prima di tutto che questo sia il caso.
B. Passere poi a DES. Costruirei un grande circuito che consiste in n copie del circuito
DES. Date n coppie (x_1,y_ 1),..,(x_n,y_n) di testo in chiaro e testo cifrato ottenute tramite il tuo programmino in Python per DES a partire dalla stessa chiave k, fisserei il valore degli input e output del "circuitone" a x_1,..,X_n e y_1,..,y_n, rispettivamente. A questo punto passerei il circuito a SAT e verificherei innanzitutto che SAT non riesca a forzare DES.
A questo punto proverei a rifare il lavoro con un numero di round molto più basso di 16, tipo
203...

Sia per il punto A che per il punto B, crea magari delle funzioni parametrizzate sul circuito, sul numero di round, etc.
