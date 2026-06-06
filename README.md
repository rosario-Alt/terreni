# terreni

Raccolta di strumenti web.

## Mappa Stazioni Elettriche — `mappa-stazioni.html`

App che mostra su **un'unica mappa** le sottostazioni elettriche delle Ferrovie (SSE FS),
e le stazioni di **Terna** ed **Enel**, per capire le **distanze tra loro**.

### Come si usa
1. Apri `mappa-stazioni.html` nel browser (doppio clic sul file).
2. Trascina nella pagina i tuoi file Excel (es. `Elenco SSE.xlsx` e `stazioni.xlsx`).
   Sono accettati `.xlsx`, `.xls`, `.csv`.
3. L'app legge i file **nel browser** (nessun dato viene caricato online) e rileva
   automaticamente le colonne di latitudine/longitudine.

### File supportati
Puoi caricare più file insieme. Esempi testati:
- **`catasto_stazioni_*.xlsx`** — catasto completo Terna + e-distribuzione (Enel) con
  coordinate, `Gestore`, `Categoria` e **`Saturazione`** dei TR.
- **`Elenco SSE.xlsx`** — sottostazioni elettriche delle Ferrovie (FS), con `Latitudine`/`Longitudine`.

### Cosa fa
- **Mappa unica** con marker colorati per fonte (SSE FS = rosso, Terna = blu, Enel = verde).
  Se in un file c'è una colonna "Gestore/Tipo" (es. Terna/Enel) viene usata per dividere e colorare i punti.
- **Stato di saturazione dei TR**: ogni nodo mostra un badge colorato (🟢 Verde / 🟡 Giallo /
  🟠 Arancio / 🔴 Rosso) nel popup. Quando un file ha sia il gestore sia la saturazione, l'app
  usa di default la modalità **Auto**: 🔵 Terna in blu, 🟢🟡🟠🔴 Enel colorati per saturazione.
  Dal menu "Colora per colonna" puoi passare a Gestore, Categoria o Saturazione semplici.
- **Distanze automatiche**: cliccando un punto vedi subito la stazione più vicina di ogni altra rete, con i km.
- **Misura manuale** punto-punto sulla mappa.
- **Analisi "più vicini"**: per ogni stazione di un livello trova la più vicina di un altro
  livello, con tabella riassuntiva ed **export CSV**.
- **Ricerca** per nome, base satellitare, e **risoluzione delle righe senza coordinate**
  (inserimento manuale o geocodifica automatica da indirizzo via OpenStreetMap/Nominatim).

> Nota: latitudine/longitudine sono riconosciute in formato decimale (con punto o virgola)
> o gradi-minuti-secondi. Se i tuoi file non contengono coordinate ma solo nomi/indirizzi,
> usa il pulsante "Risolvi posizioni".

## Ricerca Terreni — `index.html`
Pagina di partenza per cercare terreni in vendita sui principali portali italiani.
