#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rb.ftv — server di supporto per la piattaforma integrata (index.html).

Cosa fa:
  1. Serve la piattaforma rb.ftv sulla rete locale/server:  http://<server>:8765/
  2. Controlla la casella mail dedicata X-Elio via IMAP (a intervalli o su
     richiesta POST /api/mail/controlla) e salva ogni nuova mail con i suoi
     allegati in  <archivio>/inbox/<data>_<oggetto>/  — pronta per essere
     protocollata dal tool (scheda Archivio & Registro → Posta in arrivo).

Uso:
  1. copia config.esempio.ini in config.ini e compila i parametri
  2. python server.py
  3. apri http://localhost:8765/  (o l'IP del server dagli altri PC)

Solo libreria standard: nessuna dipendenza da installare.
"""

import configparser
import email
import imaplib
import json
import re
import sys
import threading
from datetime import datetime
from email.header import decode_header, make_header
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

BASE = Path(__file__).resolve().parent
CONFIG_FILE = BASE / "config.ini"

cfg = configparser.ConfigParser()
if CONFIG_FILE.exists():
    cfg.read(CONFIG_FILE, encoding="utf-8")

ARCHIVIO = Path(cfg.get("archivio", "percorso", fallback=str(BASE / "analisi")))
INBOX = ARCHIVIO / "inbox"
PORTA = cfg.getint("server", "porta", fallback=8765)
INTERVALLO_MIN = cfg.getint("mail", "intervallo_minuti", fallback=0)

_lock = threading.Lock()
_ultimo_controllo = {"quando": None, "esito": "mai eseguito", "nuove": 0}


def _slug(testo, max_len=60):
    s = re.sub(r"[^A-Za-z0-9àèéìòù ._-]+", " ", testo or "").strip()
    s = re.sub(r"\s+", "-", s).lower()
    return (s or "senza-nome")[:max_len].strip("-.")


def _decodifica(intestazione):
    try:
        return str(make_header(decode_header(intestazione or "")))
    except Exception:
        return intestazione or ""


def salva_messaggio(raw_bytes):
    """Salva una mail (bytes RFC822) in <archivio>/inbox/: .eml + allegati.
    Restituisce un dizionario riassuntivo."""
    msg = email.message_from_bytes(raw_bytes)
    oggetto = _decodifica(msg.get("Subject", "(senza oggetto)"))
    mittente = _decodifica(msg.get("From", ""))
    try:
        data = email.utils.parsedate_to_datetime(msg.get("Date"))
    except Exception:
        data = datetime.now()
    cartella = INBOX / "{}_{}".format(data.strftime("%Y%m%d-%H%M"), _slug(oggetto, 40))
    contatore = 1
    base_cartella = cartella
    while cartella.exists():
        contatore += 1
        cartella = base_cartella.with_name(base_cartella.name + "_" + str(contatore))
    cartella.mkdir(parents=True)
    (cartella / "mail-richiesta.eml").write_bytes(raw_bytes)
    allegati = []
    for parte in msg.walk():
        nome = parte.get_filename()
        if not nome:
            continue
        if parte.get_content_disposition() not in ("attachment", "inline"):
            continue
        contenuto = parte.get_payload(decode=True)
        if contenuto is None:
            continue
        nome_pulito = _slug(_decodifica(nome), 80) or "allegato"
        # conserva l'estensione originale
        est = Path(_decodifica(nome)).suffix
        if est and not nome_pulito.endswith(est.lower()):
            nome_pulito += est.lower()
        (cartella / nome_pulito).write_bytes(contenuto)
        allegati.append(nome_pulito)
    return {
        "oggetto": oggetto,
        "mittente": mittente,
        "data": data.strftime("%Y-%m-%d %H:%M"),
        "cartella": str(cartella),
        "allegati": allegati,
    }


def controlla_posta():
    """Scarica i messaggi non letti dalla casella IMAP configurata."""
    if not cfg.has_section("mail") or not cfg.get("mail", "imap_host", fallback=""):
        return {"errore": "mail non configurata: compila config.ini (sezione [mail])"}
    host = cfg.get("mail", "imap_host")
    utente = cfg.get("mail", "imap_utente")
    password = cfg.get("mail", "imap_password")
    filtro = cfg.get("mail", "filtro_mittente", fallback="").lower().strip()

    with _lock:
        nuovi = []
        M = imaplib.IMAP4_SSL(host)
        try:
            M.login(utente, password)
            M.select("INBOX")
            typ, dati = M.search(None, "UNSEEN")
            for num in (dati[0].split() if dati and dati[0] else []):
                typ, msg_data = M.fetch(num, "(BODY.PEEK[])")
                raw = msg_data[0][1]
                mitt = _decodifica(email.message_from_bytes(raw).get("From", "")).lower()
                if filtro and filtro not in mitt:
                    continue  # non nostro: resta non letto
                nuovi.append(salva_messaggio(raw))
                M.store(num, "+FLAGS", "\\Seen")
        finally:
            try:
                M.logout()
            except Exception:
                pass
        _ultimo_controllo.update(
            quando=datetime.now().strftime("%d/%m/%Y %H:%M"),
            esito="ok",
            nuove=len(nuovi),
        )
        return {"nuove": nuovi, "totale": len(nuovi)}


def _ciclo_automatico():
    if INTERVALLO_MIN <= 0:
        return
    def giro():
        while True:
            try:
                esito = controlla_posta()
                n = esito.get("totale", 0)
                if n:
                    print("[mail] {} nuove richieste salvate in {}".format(n, INBOX))
            except Exception as e:  # rete giù, credenziali, ecc.: riprova al giro dopo
                print("[mail] errore controllo posta:", e)
                _ultimo_controllo.update(esito="errore: " + str(e))
            threading.Event().wait(INTERVALLO_MIN * 60)
    threading.Thread(target=giro, daemon=True).start()


class Gestore(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(BASE), **kw)

    def _json(self, dati, codice=200):
        corpo = json.dumps(dati, ensure_ascii=False).encode("utf-8")
        self.send_response(codice)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def do_GET(self):
        if self.path == "/api/stato":
            self._json({
                "servizio": "rb.ftv server",
                "archivio": str(ARCHIVIO),
                "inbox": str(INBOX),
                "mail_configurata": bool(cfg.get("mail", "imap_host", fallback="")),
                "controllo_automatico_minuti": INTERVALLO_MIN,
                "ultimo_controllo": _ultimo_controllo,
            })
            return
        if self.path in ("/", ""):
            self.path = "/index.html"
        super().do_GET()

    def do_POST(self):
        if self.path == "/api/mail/controlla":
            try:
                self._json(controlla_posta())
            except Exception as e:
                self._json({"errore": str(e)}, 500)
            return
        self._json({"errore": "endpoint sconosciuto"}, 404)

    def log_message(self, fmt, *args):
        pass  # niente rumore in console; restano i messaggi [mail]


def main():
    ARCHIVIO.mkdir(parents=True, exist_ok=True)
    INBOX.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.exists():
        print("ATTENZIONE: config.ini non trovato — la posta è disattivata.")
        print("Copia config.esempio.ini in config.ini e compilalo.")
    _ciclo_automatico()
    server = ThreadingHTTPServer(("0.0.0.0", PORTA), Gestore)
    print("rb.ftv server avviato:")
    print("  piattaforma:  http://localhost:{}/".format(PORTA))
    print("  archivio:     {}".format(ARCHIVIO))
    print("  posta in arrivo automatica: {}".format(
        "ogni {} minuti".format(INTERVALLO_MIN) if INTERVALLO_MIN > 0 and cfg.get("mail", "imap_host", fallback="")
        else "disattivata (config.ini)"))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\narresto.")


if __name__ == "__main__":
    main()
