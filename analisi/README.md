# analisi/ — controllo qualità degli elenchi di nodi elettrici

Strumenti per verificare un estratto di **cabine primarie e-distribuzione**, **stazioni Terna** e
**sottostazioni RFI** prima di usarlo per decidere dove connettere un impianto.

## Perché esiste

Nato da un caso reale: ricerca del punto di connessione per 50,2 ha a **Castagnaro (VR)**,
Fg.11 particelle 11-238 + Fg.12 particelle 257-270, centroide `45.097205, 11.387268`.

L'estratto "41 nodi entro 30 km" usato per quella ricerca conteneva quattro difetti, tutti
invisibili a occhio e tutti capaci di far sbagliare la scelta della stazione:

| Difetto | Effetto misurato |
|---|---|
| Distanze calcolate dal **centro del comune** invece che dal terreno (3,18 km di scarto) | scarto fino a **3,2 km**, medio 1,9 km — cambia l'ordine della classifica: Castelmassa passa da 13,0 a 9,8 km e scavalca |
| Campo `prov` incoerente col `comune` | **8 nodi su 32 verificabili = 25%** (Legnago dato in PD, Torricella in MN, Lonigo in VR…) |
| Coordinate duplicate | 41 record → **38 punti distinti**; una SE in iter (Polesella) ha le coordinate esatte di un'altra stazione (Canaro) |
| Sospetto layer stazioni Terna incompleto | **non confermato**: vedi sotto |

### Il quarto sospetto, e perché è rientrato

Il rapporto stazioni/cabine locale è 0,20 contro lo 0,88 del file nazionale: sembrava un layer
incompleto. **Il confronto era sbagliato.** La collezione `terna` del file nazionale è eterogenea
(stazioni RTN, impianti di terzi, progetti in iter), quindi sovrastima quante stazioni RTN
aspettarsi in una zona.

Il metro giusto è il conteggio ufficiale Terna per regione. In **Veneto**: 10 stazioni a 380 kV,
21 a 220 kV, 34 a 150/132 kV (**65 in totale**) e 136 cabine primarie. Rapportato a un disco di
30 km si attendono **~10 stazioni e ~21 cabine**: nell'estratto ce ne sono **11 e 25**. In linea.

Resta vero che le stazioni esistenti arrivano da OpenStreetMap (`osm_id`, `"Esistente (OSM)"`) e
quelle nuove da un registro ufficiale (codici VIP, `In iter MASE`): due fonti di qualità diversa,
da tenere d'occhio. Ma **il buco non è dimostrato**, e il rapporto SE/CP da solo non basta a
dichiararlo: in pianura molte cabine sono alimentate da linee, non da una stazione vicina.

Per questo il controllo di densità ora distingue un confronto **FORTE** (`--regione Veneto`, contro
il dato ufficiale) da uno **DEBOLE** (contro il file stesso), e il secondo dice a chiare lettere
di non trarne conclusioni.

## Uso

```bash
python3 analisi/valida_nodi.py ESTRATTO.json --kml TERRENO.kml --regione Veneto
python3 analisi/valida_nodi.py ESTRATTO.json --lat 45.097205 --lon 11.387268 --raggio 30 --regione Veneto
```

Accetta sia lo schema "snello" (`terna_SE` / `cp_edistribuzione` / `rfi` come liste) sia quello
completo di `stato_cabine.json` (`e-distribuzione` / `terna` / `rfi` / `altri_distributori` /
`custom` come dizionari indicizzati per nome).

Produce `<nome>_report.txt`, `<nome>_pulito.json` e `<nome>_pulito.csv` (separatore `;`, UTF-8 BOM:
si apre in Excel e si trascina in `mappa-stazioni.html`).

## I sette controlli

0. **Consistenza** — conteggi per layer, distinguendo esistenti / in iter / **stato ignoto**
   (lo stato assente non va contato tra gli esistenti: gonfia la densità e nasconde i buchi).
1. **Distanze** — ricalcolo dal punto vero, con scarto rispetto a quelle dichiarate nel file.
2. **Duplicati** — per coordinate (arrotondate a ~100 m) e per nome normalizzato.
3. **Provincia** — `prov` confrontato con `comune` tramite `comuni_provincia.json`.
   Regola operativa: **mai filtrare per provincia, filtrare per distanza.**
4. **Saturazione** — semaforo delle CP e elenco di quelle senza dato.
5. **Densità** — CP e SE attese nel disco. Con `--regione` il confronto è col **conteggio ufficiale
   Terna** della regione (giudizio valido); senza, è col file sorgente stesso e vale solo come
   ordine di grandezza — il report lo dichiara esplicitamente.
6. **Fascia cieca** — se l'estratto è centrato altrove rispetto al punto vero, calcola la
   superficie mai guardata e quanti nodi ci si aspetta lì dentro.
7. **Buchi di copertura** — griglia sul raggio, punti la cui CP più vicina supera i 12 km.

## Note sui dati

I file di dati (`stato_cabine*.json`, estratti, output) **non sono versionati**: restano locali,
come nel progetto di origine. Qui c'è solo lo strumento e la mappa comune→provincia.

`comuni_provincia.json` è volutamente parziale (44 comuni dell'area Verona-Rovigo-Padova-Mantova-
Ferrara): va esteso quando si lavora su altre zone. I comuni non mappati non vengono verificati,
e il report lo dice.
