#!/usr/bin/env python3
"""
valida_nodi.py - controllo qualita' e pulizia di un estratto di nodi elettrici
(cabine primarie e-distribuzione, stazioni Terna, sottostazioni RFI).

Nasce da un caso reale: l'estratto "30 km da Castagnaro" conteneva distanze
misurate dal centro del paese invece che dal terreno, province sbagliate su
1 nodo su 5, coordinate duplicate e un layer Terna al 25% della densita' attesa.
Questi controlli servono a non ripetere quegli errori sul prossimo estratto.

USO
  python3 valida_nodi.py ESTRATTO.json --kml TERRENO.kml
  python3 valida_nodi.py ESTRATTO.json --lat 45.097205 --lon 11.387268 --raggio 30

CONTROLLI
  1. distanze ricalcolate dal punto vero (il terreno), con scarto rispetto al file
  2. duplicati per coordinate e per nome
  3. campo 'prov' incoerente con 'comune'
  4. record senza coordinate / senza dati di saturazione
  5. densita' CP e SE confrontata con quella nazionale del file sorgente,
     piu' il rapporto SE/CP: e' il test che scopre i layer incompleti
  6. fascia cieca, se l'estratto e' stato centrato altrove rispetto al punto vero
  7. buchi di copertura CP su griglia

OUTPUT  <nome>_pulito.json, <nome>_pulito.csv, <nome>_report.txt
"""
import argparse, csv, json, math, os, re, sys
import xml.etree.ElementTree as ET

# Densita' di riferimento.
# NAZIONALE: conteggi del file stato_cabine.json completo. E' un confronto DEBOLE:
#   la collezione 'terna' e' eterogenea (stazioni RTN, impianti di terzi, progetti in iter),
#   quindi il rapporto nazionale sovrastima quante stazioni RTN aspettarsi in una zona.
# UFFICIALE: conteggi dichiarati da Terna per regione (documenti statistici di rete).
#   E' il confronto FORTE: usalo con --regione quando la zona ricade in una regione coperta.
CP_NAZ, SE_NAZ, AREA_IT = 1912, 1685, 302073.0
RIFERIMENTI_REGIONALI = {
    # regione: (stazioni RTN totali, cabine primarie, superficie km2, fonte)
    'veneto': (65, 136, 18345.0, 'Terna: 10 SE a 380 kV + 21 a 220 kV + 34 a 150/132 kV; 136 CP'),
}
# nomi di collezione accettati -> etichetta
COLLEZIONI = {
    'cp_edistribuzione': 'CP', 'e-distribuzione': 'CP',
    'terna_SE': 'SE', 'terna': 'SE',
    'rfi': 'RFI', 'altri_distributori': 'ALTRI', 'custom': 'CUSTOM',
}
ROSA = ['N', 'NE', 'E', 'SE', 'S', 'SO', 'O', 'NO']


def haversine(a, b):
    R = 6371.0
    dla, dlo = math.radians(b[0] - a[0]), math.radians(b[1] - a[1])
    x = (math.sin(dla / 2) ** 2 +
         math.cos(math.radians(a[0])) * math.cos(math.radians(b[0])) * math.sin(dlo / 2) ** 2)
    return 2 * R * math.asin(min(1, math.sqrt(x)))


def direzione(a, b):
    p1, p2 = math.radians(a[0]), math.radians(b[0])
    dl = math.radians(b[1] - a[1])
    y = math.sin(dl) * math.cos(p2)
    x = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    gradi = (math.degrees(math.atan2(y, x)) + 360) % 360
    return ROSA[int((gradi + 22.5) // 45) % 8]


def centroide_kml(path):
    """Centroide pesato sull'area di tutti i poligoni del KML."""
    ns = {'k': 'http://www.opengis.net/kml/2.2'}
    sx = sy = sa = 0.0
    for pm in ET.parse(path).getroot().findall('.//k:Placemark', ns):
        nodo = pm.find('.//k:coordinates', ns)
        if nodo is None or not nodo.text:
            continue
        punti = []
        for tok in nodo.text.split():
            p = tok.split(',')
            if len(p) >= 2:
                punti.append((float(p[0]), float(p[1])))
        if len(punti) < 3:
            continue
        lat0 = sum(p[1] for p in punti) / len(punti)
        kx, ky = 111320 * math.cos(math.radians(lat0)), 110540
        xy = [(lo * kx, la * ky) for lo, la in punti]
        area = cx = cy = 0.0
        for i in range(len(xy) - 1):
            x1, y1 = xy[i]
            x2, y2 = xy[i + 1]
            cr = x1 * y2 - x2 * y1
            area += cr
            cx += (x1 + x2) * cr
            cy += (y1 + y2) * cr
        area /= 2
        if area == 0:
            continue
        sx += (cx / (6 * area) / kx) * abs(area)
        sy += (cy / (6 * area) / ky) * abs(area)
        sa += abs(area)
    if sa == 0:
        sys.exit(f"KML senza poligoni validi: {path}")
    return sy / sa, sx / sa


def numero(v):
    try:
        f = float(str(v).replace(',', '.'))
        return f if math.isfinite(f) else None
    except (TypeError, ValueError):
        return None


def normalizza(nome):
    return re.sub(r'[^a-z0-9]', '', (nome or '').lower())


def carica_nodi(dati):
    """Accetta sia lo schema snello (liste) sia quello completo (dict per nome)."""
    fuori = []
    for chiave, etichetta in COLLEZIONI.items():
        blocco = dati.get(chiave)
        if isinstance(blocco, list):
            righe = [(r.get('nome'), r) for r in blocco if isinstance(r, dict)]
        elif isinstance(blocco, dict):
            righe = [(r.get('nome') or k, r) for k, r in blocco.items() if isinstance(r, dict)]
        else:
            continue
        for nome, r in righe:
            rec = dict(r)
            rec['_layer'] = etichetta
            rec['_collezione'] = chiave
            rec['_nome'] = nome or '(senza nome)'
            fuori.append(rec)
    return fuori


def esistente(rec):
    """True solo se lo stato dice esplicitamente che il nodo e' in esercizio.
    Stato assente = ignoto: non va contato tra gli esistenti, altrimenti gonfia
    la densita' e nasconde proprio i buchi che stiamo cercando."""
    stato = (rec.get('stato_iter') or '').strip().lower()
    if not stato:
        return False
    return not any(k in stato for k in ('in iter', 'pianificat', 'nuova cp', 'pds'))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('estratto')
    ap.add_argument('--kml', help='KML del terreno: il punto di riferimento e\' il centroide delle particelle')
    ap.add_argument('--lat', type=float)
    ap.add_argument('--lon', type=float)
    ap.add_argument('--raggio', type=float, default=30.0)
    ap.add_argument('--regione', help="regione per il confronto di densita' ufficiale, es. Veneto")
    ap.add_argument('--comuni', default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'comuni_provincia.json'))
    ap.add_argument('--out-dir', default='.')
    args = ap.parse_args()

    if args.kml:
        punto = centroide_kml(args.kml)
    elif args.lat is not None and args.lon is not None:
        punto = (args.lat, args.lon)
    else:
        sys.exit('serve --kml oppure --lat/--lon: senza il punto vero le distanze non valgono nulla')

    dati = json.load(open(args.estratto, encoding='utf-8'))
    nodi = carica_nodi(dati)
    if not nodi:
        sys.exit('nessuna collezione riconosciuta nel file')
    try:
        comuni = {k: v for k, v in json.load(open(args.comuni, encoding='utf-8')).items() if not k.startswith('_')}
    except OSError:
        comuni = {}

    centro_file = dati.get('_centro') or {}
    centro = (numero(centro_file.get('lat')), numero(centro_file.get('lon')))
    centro = centro if None not in centro else None

    righe, senza_coord = [], []
    for rec in nodi:
        la, lo = numero(rec.get('lat')), numero(rec.get('lon'))
        if la is None or lo is None:
            senza_coord.append(rec)
            continue
        rec['_km'] = round(haversine(punto, (la, lo)), 2)
        rec['_dir'] = direzione(punto, (la, lo))
        dichiarata = numero(rec.get('dist_km') or rec.get('_distanza_km'))
        rec['_scarto_km'] = round(rec['_km'] - dichiarata, 2) if dichiarata is not None else None
        rec['_esistente'] = esistente(rec)
        righe.append(rec)
    righe.sort(key=lambda r: r['_km'])

    R = []
    P = R.append
    P('=' * 100)
    P(f"VALIDAZIONE {os.path.basename(args.estratto)}")
    P(f"punto di riferimento: {punto[0]:.6f} N, {punto[1]:.6f} E" + (f"  (da {os.path.basename(args.kml)})" if args.kml else ''))
    if centro:
        P(f"centro dichiarato nel file: {centro[0]:.6f} N, {centro[1]:.6f} E  -> dista {haversine(centro, punto):.2f} km dal punto vero")
    P('=' * 100)

    conteggi = {}
    for r in righe:
        conteggi.setdefault(r['_layer'], []).append(r)
    P('\n[0] CONSISTENZA')
    for lay, lst in sorted(conteggi.items()):
        viv = sum(1 for r in lst if r['_esistente'])
        ign = sum(1 for r in lst if not (r.get('stato_iter') or '').strip())
        P(f"    {lay:<7} {len(lst):>4} con coordinate   ({viv} esistenti, {len(lst)-viv-ign} in iter/pianificati, {ign} stato ignoto)")
    if senza_coord:
        P(f"    SENZA COORDINATE, esclusi da ogni calcolo: {len(senza_coord)}")
        for r in senza_coord[:10]:
            P(f"        - {r['_nome']} [{r['_layer']}] comune={r.get('comune')}")

    # 1 - distanze
    scarti = [r for r in righe if r.get('_scarto_km') is not None]
    P('\n[1] DISTANZE dichiarate nel file vs distanza reale dal punto')
    if not scarti:
        P('    il file non dichiara distanze: nulla da confrontare')
    else:
        peggio = sorted(scarti, key=lambda r: -abs(r['_scarto_km']))
        P(f"    scarto massimo {abs(peggio[0]['_scarto_km']):.1f} km, medio {sum(abs(r['_scarto_km']) for r in scarti)/len(scarti):.1f} km")
        for r in peggio[:8]:
            P(f"        {r['_nome'][:44]:<44} file {numero(r.get('dist_km') or r.get('_distanza_km')):5.1f} -> reale {r['_km']:5.1f} ({r['_scarto_km']:+.1f})")
        riordino = [r['_nome'] for r in sorted(scarti, key=lambda r: r['_km'])[:5]]
        P(f"    prime 5 posizioni dopo il ricalcolo: {', '.join(n[:28] for n in riordino)}")

    # 2 - duplicati
    P('\n[2] DUPLICATI')
    per_coord, per_nome = {}, {}
    for r in righe:
        per_coord.setdefault((round(numero(r['lat']), 3), round(numero(r['lon']), 3)), []).append(r)
        per_nome.setdefault(normalizza(r['_nome']), []).append(r)
    dup_c = {k: v for k, v in per_coord.items() if len(v) > 1}
    dup_n = {k: v for k, v in per_nome.items() if len(v) > 1}
    for k, v in dup_c.items():
        P(f"    coordinate {k}: " + ' || '.join(f"{r['_nome']} [{r['_layer']}]" for r in v))
    for k, v in dup_n.items():
        P(f"    stesso nome '{k}': " + ' || '.join(f"{r['lat']},{r['lon']}" for r in v))
    if not dup_c and not dup_n:
        P('    nessuno')
    P(f"    record {len(righe)} -> punti distinti {len(per_coord)}")

    # 3 - province
    P('\n[3] CAMPO prov INCOERENTE COL COMUNE')
    corretti = 0
    for r in righe:
        c = r.get('comune')
        if c and c in comuni and comuni[c] != r.get('prov') and r.get('prov'):
            P(f"    {r['_nome'][:38]:<38} comune={c:<24} file={r['prov']} -> {comuni[c]}")
            r['prov_corretta'] = comuni[c]
            corretti += 1
        else:
            r['prov_corretta'] = comuni.get(c or '', r.get('prov'))
    verificabili = sum(1 for r in righe if (r.get('comune') or '') in comuni and r.get('prov'))
    if verificabili:
        P(f"    {corretti} errati su {verificabili} verificabili ({100*corretti/verificabili:.0f}%)")
    P('    NB: i nodi senza comune non sono verificabili. Non filtrare mai per provincia: filtrare per distanza.')

    # 4 - saturazione
    P('\n[4] SATURAZIONE (solo CP)')
    cp = [r for r in righe if r['_layer'] == 'CP']
    muti = [r for r in cp if not (r.get('stato_peggiore') or '')]
    semafori = {}
    for r in cp:
        semafori[(r.get('stato_peggiore') or 'n.d.').upper()] = semafori.get((r.get('stato_peggiore') or 'n.d.').upper(), 0) + 1
    P(f"    {semafori}")
    if muti:
        P(f"    senza dato di saturazione: {len(muti)} -> " + ', '.join(r['_nome'] for r in muti[:8]))
    libere = [r for r in cp if (r.get('stato_peggiore') or '').upper() in ('VERDE', 'GIALLO')]
    P('    CP non rosse/arancioni: ' + (', '.join(f"{r['_nome']} ({r['_km']:.1f} km, {r['stato_peggiore']})" for r in libere) or 'NESSUNA'))

    # 5 - densita': il test che scopre i layer incompleti
    P('\n[5] DENSITA')
    area = math.pi * args.raggio ** 2
    n_cp = len([r for r in righe if r['_layer'] == 'CP'])
    n_se = len([r for r in righe if r['_layer'] == 'SE'])
    cp_viv = sum(1 for r in righe if r['_layer'] == 'CP' and r['_esistente'])
    se_viv = sum(1 for r in righe if r['_layer'] == 'SE' and r['_esistente'])
    P(f"    disco r={args.raggio:g} km = {area:.0f} km2   osservati: {n_cp} CP ({cp_viv} esistenti), {n_se} SE ({se_viv} esistenti)")

    rif = RIFERIMENTI_REGIONALI.get((args.regione or '').strip().lower())
    if rif:
        se_r, cp_r, area_r, fonte = rif
        cp_att, se_att = cp_r * area / area_r, se_r * area / area_r
        P(f"    [FORTE] confronto col dato ufficiale Terna per {args.regione}: {fonte}")
        P(f"            CP attese {cp_att:5.1f} -> osservate {n_cp:3d}   {'in linea' if n_cp >= 0.8*cp_att else 'SOTTO ATTESA'}")
        P(f"            SE attese {se_att:5.1f} -> osservate {n_se:3d}   {'in linea' if n_se >= 0.8*se_att else 'SOTTO ATTESA'}")
        if n_se < 0.6 * se_att:
            P("            ALLARME: mancano stazioni rispetto al conteggio ufficiale della regione.")
        P("            NB: se il disco sconfina in altre regioni il riferimento vale solo come ordine di grandezza.")
    else:
        P(f"    [DEBOLE] nessun riferimento ufficiale per --regione '{args.regione or ''}': uso il file nazionale")
        P(f"            CP attese {CP_NAZ*area/AREA_IT:5.1f} -> osservate {n_cp:3d}")
        P(f"            SE attese {SE_NAZ*area/AREA_IT:5.1f} -> osservate {n_se:3d}")
        P("            Questo confronto NON e' una prova: la collezione 'terna' del file nazionale e' eterogenea")
        P("            (stazioni RTN, impianti di terzi, progetti in iter) e sovrastima le stazioni attese in zona.")
        P("            Per un giudizio valido serve il conteggio ufficiale Terna della regione: vedi RIFERIMENTI_REGIONALI.")
    if n_cp and cp_viv:
        P(f"    rapporto SE/CP  file nazionale {SE_NAZ/CP_NAZ:.2f} | locale {n_se/n_cp:.2f} | locale solo esistenti {se_viv/cp_viv:.2f}")
        P("    Un rapporto locale basso NON basta a dichiarare un buco: in pianura molte CP sono alimentate da linee")
        P("    e non da una stazione vicina. Confermare sempre col conteggio regionale ufficiale prima di allarmarsi.")

    # 6 - fascia cieca
    if centro and haversine(centro, punto) > 0.5:
        P('\n[6] FASCIA CIECA da centratura sbagliata')
        passo, dentro, celle = 0.004, 0, 0
        kx, ky = 111.320 * math.cos(math.radians(punto[0])), 110.54
        area_cella = (passo * kx) * (passo * ky)
        direzioni = {}
        la = punto[0] - args.raggio / 100
        while la < punto[0] + args.raggio / 100:
            lo = punto[1] - args.raggio / 70
            while lo < punto[1] + args.raggio / 70:
                if haversine(punto, (la, lo)) <= args.raggio:
                    celle += 1
                    if haversine(centro, (la, lo)) > args.raggio:
                        dentro += 1
                        d = direzione(punto, (la, lo))
                        direzioni[d] = direzioni.get(d, 0) + 1
                lo += passo
            la += passo
        af = dentro * area_cella
        P(f"    superficie mai guardata: {af:.0f} km2 verso {', '.join(k for k, _ in sorted(direzioni.items(), key=lambda x: -x[1])[:3])}")
        P(f"    nodi attesi la dentro: {n_cp/area*af:.1f} CP e {n_se/area*af:.1f} SE -> assenti per costruzione")
        P('    RIMEDIO: rigenerare l estratto centrato sul terreno, non sul comune')

    # 7 - buchi
    P('\n[7] BUCHI DI COPERTURA CP (soglia 12 km)')
    cp_viventi = [r for r in righe if r['_layer'] == 'CP' and r['_esistente']]
    buchi = []
    if cp_viventi:
        passo = 0.006
        la = punto[0] - args.raggio / 130
        while la < punto[0] + args.raggio / 130:
            lo = punto[1] - args.raggio / 90
            while lo < punto[1] + args.raggio / 90:
                if haversine(punto, (la, lo)) <= args.raggio * 0.85:
                    dmin = min(haversine((la, lo), (numero(r['lat']), numero(r['lon']))) for r in cp_viventi)
                    if dmin > 12:
                        buchi.append((dmin, la, lo))
                lo += passo
            la += passo
        buchi.sort(reverse=True)
    for dm, la, lo in buchi[:5]:
        P(f"    {la:.4f},{lo:.4f}  CP piu vicina a {dm:.1f} km  ({haversine(punto,(la,lo)):.1f} km dal punto, {direzione(punto,(la,lo))})")
    if not buchi:
        P('    nessuno: ogni punto ha una CP entro 12 km')
    vicine = sorted(cp_viventi, key=lambda r: r['_km'])[:3]
    P('    CP in esercizio piu vicine al punto: ' + ', '.join(f"{r['_nome']} {r['_km']:.1f} km" for r in vicine))

    P('\n' + '=' * 100)
    P('CLASSIFICA DAL PUNTO VERO')
    P('=' * 100)
    for r in righe:
        extra = ''
        if r['_layer'] == 'SE':
            extra = f"{r.get('kV') or r.get('tensione_kv') or '?'} kV  {r.get('stato_iter') or ''} [{r.get('operatore') or ''}]"
        elif r['_layer'] == 'CP':
            extra = f"SAT={r.get('stato_peggiore') or '-'}  {r.get('stato_iter') or ''}"
        P(f"{r['_km']:6.1f} {r['_dir']:<3} {r['_layer']:<6} {r['_nome'][:42]:<42} {str(r.get('comune') or '-')[:20]:<20} {r.get('prov_corretta') or '-':<3} {extra}")

    testo = '\n'.join(R)
    print(testo)
    base = os.path.join(args.out_dir, os.path.splitext(os.path.basename(args.estratto))[0])
    os.makedirs(args.out_dir, exist_ok=True)
    open(base + '_report.txt', 'w', encoding='utf-8').write(testo + '\n')
    json.dump({'_punto': {'lat': punto[0], 'lon': punto[1]},
               '_generato_da': 'valida_nodi.py',
               'nodi': righe, 'senza_coordinate': senza_coord},
              open(base + '_pulito.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    campi = ['_km', '_dir', '_layer', '_nome', 'comune', 'prov', 'prov_corretta', 'lat', 'lon',
             'kV', 'tensione_kv', 'MVA', 'potenza_mva', 'stato_iter', '_esistente',
             'stato_peggiore', 'rosso', 'arancio', 'giallo', 'verde', 'n_sez', 'operatore', '_scarto_km']
    with open(base + '_pulito.csv', 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f, delimiter=';')
        w.writerow(campi)
        for r in righe:
            w.writerow([r.get(c, '') for c in campi])
    print(f"\nScritti: {base}_report.txt | {base}_pulito.json | {base}_pulito.csv")


if __name__ == '__main__':
    main()
