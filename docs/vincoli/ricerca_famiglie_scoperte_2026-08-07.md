# Ricerca famiglie di vincolo scoperte — 07/08/2026

Ricognizione delle fonti per le 5 famiglie ancora scoperte (punto 4 della lista
DA FARE): rete ecologica, carsismo, DOP/IGP, geositi, alberi monumentali.
Prodotta da 5 ricerche parallele su fonti pubbliche.

## ⚠ LIMITE DI QUESTA RICOGNIZIONE — leggere prima di usare

La sessione che ha prodotto questo documento gira in un ambiente cloud il cui
proxy **blocca l'uscita verso tutti gli host non-GitHub** (403 CONNECT dal
proxy, non dal server di destinazione). Quindi:

- **Tutti gli endpoint sotto sono NON VERIFICATI dal vivo**, salvo dove
  indicato esplicitamente «VERIFICATO». L'identificazione viene da ricerca web
  (pagine e cataloghi indicizzati, incluse directory ArcGIS REST e URL WFS
  complete apparse negli indici — forte indizio di esistenza, non una prova).
- **Prima di scaricare qualsiasi cosa, rifare da C:\analisi la verifica**:
  per WFS `GetCapabilities` + `GetFeature count=1 outputFormat=json`;
  per ArcGIS REST `?f=json` + `query?where=1=1&resultRecordCount=1&outFields=*&f=json`.
- Vale sempre la regola della casa: **aprire gli attributi del campione e
  filtrare il positivo** (più sotto, per ogni fonte, il filtro atteso), e
  controllare la copertura come rapporto sull'area regionale.

---

## 1. RETE ECOLOGICA — Abruzzo, Basilicata, Calabria, Molise

Quadro d'insieme (ISPRA, rapporto 2025 sulle reti ecologiche regionali):
il **Molise non ha mai adottato una RER**; l'Abruzzo ha solo uno schema
1:500.000; la Basilicata ce l'ha dentro il PPR.

### BASILICATA — TROVATO ✔ (la fonte migliore delle quattro)
- **Dato**: Rete Ecologica del **PPR Basilicata** (elaborati feb. 2025:
  relazione 7.1.1, linee guida 7.5.1). Metadati RNDT
  `r_basili:79e7d67a:16b2bd8f80f:-2c23` e `...:16b2cde2cf0:155b`, con
  **WFS e download shapefile**.
- **Endpoint**:
  - `https://rsdi.regione.basilicata.it/geoserver/ows?service=WFS&request=GetCapabilities`
  - `https://rsdi.regione.basilicata.it/rbgeoserver2016/ows?service=WFS&version=2.0.0&request=GetCapabilities`
  - WebGIS: `https://ppr.regione.basilicata.it/webgis/` · catalogo GeoNetwork: `https://rsdi.regione.basilicata.it/Catalogo/`
- **CRS atteso**: EPSG:32633 (standard RSDI). Cercare nel capabilities i layer
  con `ecolog|pprb`.
- **Scarico**: `ogr2ogr -f GPKG rete_ecologica_basilicata.gpkg WFS:"https://rsdi.regione.basilicata.it/geoserver/ows?service=WFS" WORKSPACE:LAYER`
- **Filtro positivo**: articolazione tipica core/corridoi/stepping stones —
  se il layer contiene classi di «matrice antropizzata» o «conflitto»,
  escluderle. Se un unico layer copre ~100% della regione è la carta di
  analisi, non la rete di progetto: cercare il layer di progetto.
- **Caveat giuridico**: il PPRB feb. 2025 è una **proposta di piano** (iter in
  corso): verificare lo stato prima di trattarlo come vincolo.

### ABRUZZO — INCERTO (solo schema 1:500.000)
- Nel PPR esistono tavole «Rete ecologica – Orso, lupo, capriolo» e «core
  areas», ma **nessuno shapefile/WFS pubblico** trovato (né Cartanet, né open
  data, né RNDT). Scala 1:500.000 comunque inadatta ad analisi per terreno.
- Da provare comunque: WMS ERDAS `http://geocatalogo.regione.abruzzo.it/erdas-iws/ogc/wms/?service=WMS&request=GetCapabilities&version=1.3.0`
  (grep `ecolog`); albero SHP `http://opendata.regione.abruzzo.it/opengeodata/Dati_vettoriali/`.
- **Surrogato**: ISPRA **Carta della Natura Abruzzo 1:50.000** (2011) —
  wall-to-wall per costruzione: filtrare Valore Ecologico Alto/Molto alto
  (campo atteso `VALORE_ECO`, da confermare).
- **Da contattare**: Ufficio SIT Regione Abruzzo + servizio PPR per i
  vettoriali delle tavole.

### CALABRIA — NON PUBBLICATO open (esiste ma è riservato)
- La rete ecologica/rete polivalente sta nel **QTRP** (DCR 134/2016), ma il
  download del Quadro Conoscitivo dal geoportale regionale **richiede
  credenziali** (riservato di norma a enti). Nessun open data trovato.
- **Alternativa pubblica** (parziale): PTCP/PTCM **Città Metropolitana di
  Reggio Calabria**, GeoNode `https://geoportale.cittametropolitana.rc.it/`
  con WFS. ⚠ I layer `geonode:aree_di_espansione_su_rete_ecologica` e
  `geonode:cave_su_rete_ecologica` sono layer di **CONFLITTO** (il negativo):
  cercare il layer base della rete nel catalogo (`/layers/?q=rete+ecologica`).
- **Da contattare**: Centro Cartografico Regionale (credenziali QTRP).

### MOLISE — NON ESISTE (chiuso, non ricercare oltre)
- **La RER del Molise non è mai stata adottata** (ISPRA 2025; conferme in PAF
  Molise 2021-27). Non è un effetto del geoportale sparito: il dato non esiste.
- **Surrogati**: Carta della Natura Molise 1:25.000 (agg. 2021, CC-BY-4.0,
  RNDT `ispra_rm:0012CNATHB_DT`) filtrata su Valore Ecologico Alto/Molto alto;
  Natura 2000 + EUAP dal PCN
  (`http://wms.pcn.minambiente.it/ogc?map=/ms_ogc/wfs/Natura2000.map&service=WFS&request=GetCapabilities`,
  in migrazione verso gn.mase.gov.it).
- **Da contattare** (se si vuole la RER in costruzione): Regione Molise,
  Servizio Valutazione Prevenzione e Tutela dell'Ambiente (DA4).

---

## 2. CARSISMO — Basilicata, Calabria, Lazio, Marche, Piemonte, Umbria

### LAZIO — TROVATO ✔ (con caveat sulla geometria)
- **Layer**: `geonode:catasto_delle_cavita_naturali` sul GeoNode regionale
  (RNDT `r_lazio:80238b32-25e0-11ec-abb2-0242`; dati Federazione Speleologica
  del Lazio ex L.R. 20/1999).
- ⚠ **Geometria: POLIGONI a griglia 250 m** (densità di cavità per cella),
  NON i punti d'ingresso. Va bene come screening di presenza, non per
  localizzazione puntuale. Verificare se include celle a valore zero
  (filtrare n. cavità > 0).
- **WFS**: `https://geoportale.regione.lazio.it/geoserver/ows?service=WFS` —
  negli indici compare servito in EPSG:25833.
- **Scarico**: `ogr2ogr -f GPKG lazio_cavita_250m.gpkg WFS:"https://geoportale.regione.lazio.it/geoserver/ows" geonode:catasto_delle_cavita_naturali`
- In più: `geonode:geositi_puntuali` e `geonode:geositi_areali` (Catasto
  Geositi Lazio, DGR 120 del 5/3/2026) — subset carsico da filtrare su
  tipologia/interesse.
- Punti esatti degli ingressi: solo FSL (`speleo.lazio.it`), su richiesta.

### MARCHE — catasto ufficiale non open; surrogato PPAR ✔
- Il catasto ex **L.R. 12/2000** (aree carsiche, grotte, forre, gravine) è
  tenuto dalla Federazione Speleologica Marchigiana su OpenSpeleo, **accesso
  riservato**.
- **Surrogato open**: «**Emergenze geologiche e geomorfologiche 1:10.000
  (art. 64 punto h NTA PPAR)**» su CKAN GOODPA (licenza open, DGR 783/2017):
  `curl -s "http://goodpa.regione.marche.it/api/3/action/package_show?id=emergenze-geologiche-e-geomorfologiche-1-10000-art-64-punto-h-delle-nta-del-ppar"`
  → scaricare la resource zip indicata. Geometrie miste punti+poligoni attese.
- ⚠ Contiene il proprio negativo (emergenze non carsiche: frane, calanchi…):
  filtrare sul campo tipologia. Copertura comunale incompleta, base 1978.
  NOTA: è un dataset DIVERSO da `MARCHE_Fasce_Morfologiche_PPAR89` (escluso
  con motivo) — non confonderli.

### UMBRIA — geositi ✔, catasto grotte non open
- **Geositi e singolarità geologiche, DGR 575 del 19/6/2024**: la Regione
  dichiara la disponibilità **shapefile** dalla pagina
  `https://www.regione.umbria.it/paesaggio-urbanistica/geositi`. Subset
  carsico da filtrare su tipologia.
- Catasto Cavità Umbria (FUGS, >1.000 grotte): `https://catasto.fugs.it/`,
  solo consultazione web → richiedere a `catasto@fugs.it`.
- SIAT REST: `https://siat.regione.umbria.it/arcgis/rest/services/public?f=pjson`
  (MapServer `public/PST_ETRS89`). ⚠ Licenza servizi SIAT: liberi solo per
  studio/ricerca, uso commerciale previa autorizzazione.

### PIEMONTE — INCERTO (candidato: geositi Arpa)
- **Catasto Speleologico Piemontese e Valdostano (AGSP)**, ~2.800 cavità +
  aree e sistemi carsici: `https://catastogrotte-piemonte.net/`, nessun open
  geodata → richiedere a `info@catastogrotte-piemonte.net`.
- **Arpa Piemonte**: il Portale Geositi
  (`https://webgis.arpa.piemonte.it/geositi-piemonte/`) è alimentato da un
  servizio puntuale che include le **grotte** tra le tipologie. Nome servizio
  da trovare enumerando `https://webgis.arpa.piemonte.it/ags/rest/services?f=json`
  e `.../server/rest/services?f=json` (cartelle `geologia`, `rischi_naturali`).
  ⚠ Contiene geositi non carsici: filtrare tipologia.

### BASILICATA — NON PUBBLICATO
- Nessun layer carsico su RSDI (geoserver, rbgeoserver2016, WebGis TUTELE) né
  RNDT. Nessuna legge regionale su speleologia/catasto risulta approvata.
- Il catasto (~350 cavità, 6 aree carsiche) è della **Federazione Speleologica
  Lucana** dentro il catasto nazionale SSI/WISH (`speleo.it/catastogrotte/`,
  solo tabellare a livello comunale).
- **Da contattare**: Fed. Speleologica Lucana; SSI Commissione Catasto
  (`catasto@speleo.it`); Regione Basilicata Ufficio Difesa del Suolo.
- Verifica residua: GetCapabilities RSDI con grep `grott|carsic|cavit|dolin|geosit`.

### CALABRIA — NON PUBBLICATO
- Solo proposte di legge sul catasto grotte, mai approvate. L'elenco più
  completo (codici «Cb») è del CRS «Enzo dei Medici» (HTML, non geodato).
- **Da contattare**: CRS Enzo dei Medici / Fed. Speleologica Calabrese;
  Regione Calabria Dip. Territorio e Ambiente; SSI Catasto.

### Fonti nazionali integrative
- **ISPRA sinkholes** (>900 casi, punti): WFS
  `https://sgi2.isprambiente.it/geoserver/ows?service=WFS&request=GetCapabilities`,
  record `ispra_rm:Sinkholes_DT`. ⚠ Include sprofondamenti **antropogenici**
  (es. voragini di Roma): filtrare sul campo genesi.
- **SSI/WISH**: >30.000 cavità ma solo tabellare; i punti restano alle
  federazioni regionali.

---

## 3. DOP/IGP

**Esito principale: il dataset vettoriale nazionale NON esiste.** Nessun
«GeoDOP» (nessuna evidenza su Masaf/SIAN/RNDT); eAmbrosia non è georiferito;
EUIPO GIview ha solo mappe per scheda. Strategia: vettoriali regionali dove
esistono + dissolve dei comuni per il resto.

### Vettoriali regionali individuati (tutti da verificare live)
| Regione | Dataset | Accesso |
|---|---|---|
| Piemonte | Aree DOC/DOCG vini + aree DOP/IGP agroalimentari (su mosaicatura catastale) | GeoNetwork `r_piemon:bb722e24-...da67` (vini), `r_piemon:201a4664-...23bc` (agroalim.) |
| Veneto | Zone DOC (CC BY, agg. 2014) | record `r_veneto:c1016231_DOC`; WFS `https://idt2.regione.veneto.it/geoservizi/wfs` |
| Toscana | **Zone DOP/IGP agroalimentari 1:10.000 + vitivinicolo** (il modello) | `https://dati.toscana.it/dataset/zonedopigp` (shp); GEOscopio `vinidopigp.html` |
| Lombardia | Aree di pregio vitivinicolo (DOC/DOCG/IGT) | record `r_lombar:18cbd828-...1aa0`; download-dati geoportale |
| Lazio | Vini DOCG su CTRN 1:5.000 (ARSIAL) — cercare anche DOC/IGT | GeoNode `geonode:Vini_DOCG_Regione_Lazio` (shp/WFS) |
| Campania | Aree DOC/DOCG vini | `https://sit2.regione.campania.it/content/aree-di-produzione-dei-vini-doc-e-docg-della-campania` |
| Umbria | Shapefile **per singola denominazione** (Assisi, Orvieto, Montefalco…) — da unire | CKAN: `curl -sS "https://dati.regione.umbria.it/api/3/action/package_search?q=zona+di+produzione+vini&rows=50"` |
| Abruzzo | Carta zone vitivinicole DOC | `http://opendata.regione.abruzzo.it/content/carta-delle-zone-vitivinicole-denominazione-origine-controllata-doc` |
| Bolzano | Zone DOC e IGT (WMS 1.3.0 + WFS 2.0.0) | `p_bz:Agriculture:DOCAndIGTZones`; GeoServer `https://geoservices.buergernetz.bz.it/geoserver/ows` |
| FVG | Probabile in Eagle/IRDAT (nome layer da cercare) | catalogo `https://irdat.regione.fvg.it/`; GeoServer `serviziogc.regione.fvg.it/geoserver` |

Nessun layer emerso per: Emilia-Romagna (interrogare minERva direttamente),
Marche, Puglia, Sicilia, Sardegna, Basilicata, Calabria, Molise, Liguria,
VdA, Trentino.

### Via alternativa per le regioni scoperte — dissolve dei comuni ✔
I disciplinari delimitano quasi sempre per elenco di comuni. Perimetro
approssimato = dissolve dei limiti comunali, con campo `metodo="comuni"`
per distinguerlo dai perimetri ufficiali.
- **Tabella denominazione→comuni**: scraping del portale Masaf
  `https://dopigp.politicheagricole.gov.it/` (823 schede: 299 agroalimentari
  + 524 vini — la fonte ufficiale più omogenea); in subordine disciplinari
  PDF (pagine Masaf 4625 vini, 15453 agroalimentari) e dati.sian.it.
- **Limiti comunali** — unico endpoint **VERIFICATO** in questa sessione
  (HTTP 200/206): mirror ISTAT
  `https://raw.githubusercontent.com/openpolis/geojson-italy/master/geojson/limits_IT_municipalities.geojson`
  (EPSG:4326; attributi `name`, `com_istat_code`, `com_catasto_code`,
  `prov_name`, `reg_name`, …). Per la versione millesimata: ISTAT «Confini
  delle unità amministrative».
- **Attributi minimi del layer unificato**: denominazione, tipo
  (DOCG/DOC/IGT/DOP/IGP), categoria (vino/olio/agroalimentare), regione,
  metodo (perimetro ufficiale vs comuni), riferimento disciplinare.
- ⚠ I disciplinari possono includere solo porzioni di comune: il dissolve è
  un'approssimazione per eccesso, da dichiarare come tale.

---

## 4. GEOSITI — Abruzzo, Marche, Veneto

### Fonte nazionale ISPRA (copre tutte e 3) — candidato principale
- **Inventario Nazionale dei Geositi** (~3.700 siti), oggi su ArcGIS
  Enterprise «SINACloud». Contatto: `geositi@isprambiente.it`.
- **FeatureServer candidati** (esistenti perché indicizzati):
  - `https://sinacloud.isprambiente.it/arcgisadv/rest/services/Hosted/Rilevamento_Geosito_Areale_New_view/FeatureServer`
    → **geositi AREALI (poligoni)** — quello utile per il vincolo
  - gemello puntuale `Rilevamento_Geosito_Puntuale_*` da trovare in
    `.../rest/services/Hosted?f=json`
- **Sequenza di verifica**: enumerare Hosted → `FeatureServer/0?f=json`
  (schema) → query campione `outFields=*` → conteggio per regione
  (`where=REGIONE='Abruzzo'&returnCountOnly=true`, nome campo da confermare).
- ⚠ **Filtro positivo**: l'inventario distingue segnalati/proposti da
  validati — individuare il campo di stato prima di usarlo come vincolo.
- **Scarico**: `ogr2ogr -f GPKG geositi_ispra.gpkg ".../FeatureServer/0/query?where=1%3D1&outFields=*&f=geojson" -nln geositi_areali`
- Endpoint storici di riserva: `sgi2.isprambiente.it/arcgis/rest/services` e
  GeoServer `sgi2.isprambiente.it/geoserver/ows`.

### VENETO — TROVATO ✔ (catalogo regionale dedicato)
- **Catalogo regionale dei geositi** ex **DGR 221 del 28/02/2017**; layer
  classe **c0505** dell'IDT-RV 2.0 (tema Suolo e sottosuolo).
- WFS: `https://idt2-geoserver.regione.veneto.it/geoserver/ows` — typename dal
  GetCapabilities (grep `c0505|geosit`). CRS di pubblicazione atteso EPSG:3003.
- Downloader shapefile senza registrazione: `https://idt2.regione.veneto.it/idt/downloader/download`.
- Geometria attesa puntuale; verificare se esiste anche l'areale.

### MARCHE — nessun catalogo geositi proprio; surrogato PPAR
- Stesso dataset del carsismo: «Emergenze geologiche e geomorfologiche
  1:10.000 art. 64 h PPAR» (CKAN GOODPA, v. sez. 2 Marche) — **un solo
  scarico serve entrambe le famiglie**. Per i geositi veri: ISPRA filtrato
  regione Marche.

### ABRUZZO — NON PUBBLICATO a livello regionale
- Il sub-progetto «Geositi» del GIS regionale non è open data; la pagina sui
  geositi minerari (L.R. 7/2022) è solo informativa. 95 geositi del Geoparco
  UNESCO della Maiella: chiedere all'ente Parco.
- Copertura effettiva: solo ISPRA (filtrare regione Abruzzo).
- **Da contattare**: Servizio Geologico Regionale / SIT Abruzzo; ISPRA;
  Parco Nazionale della Maiella.

---

## 5. ALBERI MONUMENTALI — Lazio, Umbria

### Fonte primaria: elenco AMI Masaf (nazionale, ex L. 10/2013)
- Pagina elenco con allegati XLS per regione:
  `https://www.masaf.gov.it/flex/cm/pages/ServeBLOB.php/L/IT/IDPagina/11260`
- ⚠ **Il X aggiornamento è stato pubblicato proprio il 07/08/2026** (82 nuove
  iscrizioni, +3 in Umbria; 5.008 schede nazionali): gli URL `ServeAttachment`
  cambiano a ogni aggiornamento → **ripescare i link freschi dalla pagina
  11260**, non riusare estrazioni precedenti.
- **Formato**: XLS (BIFF, serve `xlrd`). Colonne chiave: `REGIONE`,
  `ID SCHEDA`, `COMUNE`, **`LATITUDINE SU GIS` / `LONGITUDINE SU GIS`** in
  **DMS sessagesimali con virgola** (es. `42° 17' 22,25''`), datum WGS84,
  precisione ≈30 m.
- **Filtro vigenti**: NON esiste colonna di stato — gli alberi rimossi
  spariscono dal file: usare sempre l'ultimo XLS. Per audit: allegati
  «rimozioni» dei decreti di aggiornamento.
- **Pipeline XLS→GPKG** (le DMS vanno pre-convertite, ogr2ogr non le legge):

```bash
pip install pandas xlrd
python - <<'EOF'
import pandas as pd, re
def dms(s):
    if pd.isna(s): return None
    m = re.match(r"(\d+)\s*[°º]\s*(\d+)\s*['’]\s*([\d,\.]+)", str(s))
    return float(m[1]) + float(m[2])/60 + float(m[3].replace(",","."))/3600 if m else None
df = pd.read_excel("ami_lazio.xls")
lat = [c for c in df.columns if "LATITUDINE" in c.upper()][0]
lon = [c for c in df.columns if "LONGITUDINE" in c.upper()][0]
df["LAT_DD"] = df[lat].map(dms); df["LON_DD"] = df[lon].map(dms)
df.dropna(subset=["LAT_DD","LON_DD"]).to_csv("ami_lazio.csv", index=False)
EOF
ogr2ogr -f GPKG ami_lazio.gpkg ami_lazio.csv \
  -oo X_POSSIBLE_NAMES=LON_DD -oo Y_POSSIBLE_NAMES=LAT_DD \
  -a_srs EPSG:4326 -nln ami_lazio
```

- Scorciatoia: plugin QGIS **`ami_masaf`** (repo GitHub `pigreco/ami_masaf`,
  **VERIFICATO** — clonato; agg. IX elenco) fa scarico+conversione+GPKG da solo.
- **Conteggi attesi**: Lazio 212 AMI (det. G14412/2025); Umbria ~55–70 (da
  contare sul file del X aggiornamento).
- ⚠ **Vincolo**: la tutela copre l'albero e l'area di pertinenza (proiezione
  chioma, D.M. 23/10/2014); il file non ha il diametro chioma → applicare
  **buffer di screening 20–50 m** sul punto (in CRS metrico) e approfondire
  caso per caso. Le schede possono rappresentare filari/gruppi.

### Fonti regionali
- **Lazio**: layer GeoNode `geonode:alberi_monumentali`
  (`https://geoportale.regione.lazio.it/layers/geosdiownr:geonode:alberi_monumentali`,
  shp/WFS). ⚠ Può includere piante solo *proposte*: allineare comunque
  all'elenco Masaf, l'unico giuridicamente vigente.
- **Umbria**: il dataset regionale «Gli alberi più belli dell'Umbria»
  (`https://dati.regione.umbria.it/dataset/gli-alberi-pi-belli-dell-umbria`)
  è l'elenco ex **L.R. 28/2001** (~174 alberi), **NON l'elenco AMI**: usarlo
  solo come screening complementare, per il vincolo nazionale fa fede l'XLS
  Masaf Umbria.

---

## Cose chiuse (per non rifare la ricerca)

- **Molise rete ecologica**: mai adottata — non esiste il dato, chiuso.
- **DOP/IGP nazionale vettoriale**: non esiste (niente GeoDOP; eAmbrosia e
  GIview non utilizzabili come layer).
- **Catasti speleologici** Piemonte/Marche/Umbria/Lazio(punti)/Basilicata/
  Calabria: tutti presso le federazioni, nessuno open → serve richiesta.
- Controllati senza esito: RNDT per `r_abruzz`/`r_calabr`/Molise (rete
  ecologica) e per il carsismo delle 6 regioni; open data Abruzzo, Basilicata
  (CKAN), Calabria, Umbria (grotte); INSPIRE Geoportal; GitHub (nessun mirror
  utile dei dati AMI né dei perimetri DOC/DOP).

## Prossimi passi in C:\analisi (ordine consigliato)

1. Verificare gli endpoint marcati NON VERIFICATO (curl come da comandi).
2. Scarichi «pronti»: Basilicata rete ecologica (WFS RSDI), Lazio carsismo
   (WFS GeoNode), Marche emergenze PPAR (CKAN — copre carsismo E geositi),
   Umbria geositi (shp DGR 575/2024), ISPRA geositi areali (FeatureServer),
   Veneto geositi (WFS c0505), AMI Masaf Lazio+Umbria (XLS X aggiornamento).
3. Per ogni file: aprire gli attributi, applicare il filtro positivo indicato,
   controllare la copertura in % dell'area regionale, poi voci indice con
   `applica_voci_indice.py` (root, poi copia in `data/`).
4. DOP/IGP: partire dalla Toscana come modello, poi le altre 9 fonti
   regionali; per le regioni scoperte costruire il dissolve comuni dal
   portale Masaf dopigp.
5. Aggiungere alla lista PEC/richieste enti (punto 3 della lista DA FARE):
   SIT Abruzzo (RER + geositi), Centro Cartografico Calabria (QTRP),
   federazioni speleologiche (AGSP, FUGS, FSM, FSL, CRS Enzo dei Medici, FSL
   Lazio per i punti), Parco Maiella (geositi).

*I dati scaricati restano fuori dal repository (`data/` non si committa).*
