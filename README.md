# rb.ftv — Piattaforma integrata servizi FER/BESS

Strumento di lavoro unico di **rb.ftv** per la gestione delle commesse X-Elio EMENA S.r.l.
(Accordo Quadro / SOW assistenza sviluppo rev. 2 firmata) e della parte tecnica dei
procedimenti autorizzativi FER & BESS.

Tutto sta in **un solo file**: `index.html`. Niente database, niente installazioni,
niente copie: si apre nel browser (doppio clic) o si serve dal server con `server.py`.

## Contenuto del repository

| File | Cosa è |
|---|---|
| `index.html` | La piattaforma completa (HTML self-contained, CSS/JS inline, in italiano) |
| `server.py` | Server opzionale: pubblica la piattaforma in rete e scarica da solo la posta X-Elio |
| `config.esempio.ini` | Modello di configurazione per `server.py` (da copiare in `config.ini`) |
| `templates/go-no-go_xelio.md` | Template compilabile della Relazione Go/No-Go (campi `[SEGNAPOSTO]`) |
| `templates/go-no-go_xelio.docx` | Stesso template in Word (tabelle anagrafica, matrice vincoli, criticità) |

## Le schede della piattaforma

- **Nuova pratica X-Elio (flusso guidato)** — piano di lavoro in 6 passi e link ai portali
  vincolistici (Vincoli in Rete, SITAP, Natura 2000, IdroGEO/PAI, geoportale regionale,
  Atlaimpianti, Econnextion…) generati su comune e regione dell'iniziativa.
- **Ricerca terreni (scouting)** — link ai portali di annunci con filtri prezzo/superficie.
- **Fattispecie 1, 2, A, B, C, D, E + TSO/DSO** — per ogni servizio della SOW: attività,
  tabella compensi firmata, checklist input dal cliente, template di risposta con i richiami
  ai paragrafi della Relazione (§2 vincoli, §3 aree idonee, §4 procedimento, §6 criticità, §7 esito).
- **AU Campania — Allegato A-02** — checklist in 23 punti dei contenuti minimi del progetto
  definitivo per Autorizzazione Unica ex art. 12 D.Lgs. 387/2003.
- **Relazione Go / No-Go** — struttura ufficiale §1–§7, step Export che genera la bozza
  compilata, autocontrollo pre-consegna in 11 punti (chiuso da: formato editabile art. 2.6 +
  richiesta attestazione entro 10 giorni art. 3.4).
- **Documenti & Export** — da un'unica anagrafica genera: report effetto cumulo, elenco
  tavole/matrice di revisione, dossier PAUR (art. 27-bis D.Lgs. 152/2006), matrice rilievi,
  report avanzamento, mail di trasmissione con elenco allegati, **KML del perimetro area**
  e **tavole A3 stampabili con cartiglio**.
- **Archivio & Registro** — gestione commessa: vedi sotto.

## Gestione commessa (scheda Archivio & Registro)

Ciclo pratica: **Ricevuta → Assegnata → Inviata → Chiusa**.

1. **Collega la cartella archivio** (es. `C:\analisi`) — un clic, Chrome/Edge.
   Registro e documenti vivono lì, non nel browser. Per lavorare in più persone
   (es. Flavia + tecnici) usare una cartella condivisa di rete.
2. **Posta in arrivo** — carichi la mail X-Elio `.eml`: il tool legge oggetto, data e
   allegati e precompila la richiesta.
3. **Registra richiesta** — protocollo automatico `ANNO-NNN`, importo precompilato dalle
   tariffe SOW (per D/E calcolo €/MW), creazione cartella pratica con scheda-avanzamento,
   archiviazione di mail e allegati.
4. **Scheda di controllo** — assegnazione al tecnico, data invio risposta, chiusura.
   Con una pratica attiva selezionata, **tutto ciò che generi si archivia da solo** nella
   sua cartella.
5. **Fine mese** — report avanzamento prestazioni e proforma fattura con le pratiche
   inviate nel mese (ricorda l'art. 3.4: fatturare solo con attestazione ricevuta;
   pagamento 30 gg d.f. f.m.).

Struttura archivio risultante:

```
C:\analisi\
├── registro_rbftv.json            ← registro (fonte di verità)
├── registro_prestazioni.csv       ← per Excel / fatturazione
├── report-avanzamento_2026-07.md
├── proforma-fattura_2026-07.md
├── inbox\                         ← mail scaricate da server.py
└── 2026-001_ftv-capaccio-02\
    ├── scheda-avanzamento.md
    ├── mail-richiesta.eml
    ├── go-no-go_ftv-capaccio-02.md
    ├── perimetro_ftv-capaccio-02.kml
    └── ...allegati e documenti analizzati
```

## server.py (opzionale)

Pubblica la piattaforma sulla rete e automatizza la posta in arrivo:

```bash
cp config.esempio.ini config.ini   # e compila IMAP + cartella archivio
python server.py
# piattaforma:  http://<ip-server>:8765/
```

Ogni N minuti scarica le mail non lette della casella dedicata (filtro mittente
configurabile, es. "x-elio") e le salva con gli allegati in `<archivio>/inbox/`,
pronte per il protocollo. Endpoints: `GET /api/stato`, `POST /api/mail/controlla`.
Solo libreria standard Python 3.

## Note contrattuali incorporate nel tool

- consegna deliverable in **formato editabile** (art. 2.6);
- rb.ftv **revisiona** elaborati di terzi, non fa progettazione/ingegneria (art. 4);
- il compenso matura con milestone + **attestazione di regolare esecuzione** (art. 3.4) —
  richiesta entro 10 giorni inserita in ogni mail e checklist;
- compensi allineati alla **SOW firmata rev. 2**.
