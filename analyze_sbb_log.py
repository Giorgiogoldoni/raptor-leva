#!/usr/bin/env python3
"""
RAPTOR — Analisi log Super Best Buy (SBB / SBB2)

Legge sbb_flip_log.json (+ sbb2_flip_log.json se presente)
Calcola: win rate, P/L medio, profit factor, max drawdown, breakdown per leva,
trade con NaN (bug), durata media, distribuzione rendimenti.

Output:
  - sbb_report.json  (per dashboard)
  - sbb_report.txt   (leggibile)
"""

import json
import math
import statistics
import datetime
import os
from collections import defaultdict


SBB_FILES = [
    ('SBB',  'sbb_flip_log.json'),
    ('SBB2', 'sbb2_flip_log.json'),
]
REPORT_JSON = 'sbb_report.json'
REPORT_TXT  = 'sbb_report.txt'


def _is_number(x):
    return isinstance(x, (int, float)) and math.isfinite(x)


def _parse_ts(ts_iso):
    try:
        return datetime.datetime.fromisoformat(ts_iso)
    except Exception:
        return None


def _duration_days(entry):
    t0 = _parse_ts(entry.get('flip_ts'))
    if t0 is None:
        return None
    t1 = entry.get('chiusura_ts_it')
    if not t1:
        return None
    try:
        t1 = datetime.datetime.strptime(t1, '%d/%m/%Y %H:%M')
    except Exception:
        return None
    return (t1 - t0).total_seconds() / 86400.0


def stats_from_returns(returns):
    n = len(returns)
    if n == 0:
        return {
            'trades': 0, 'win_rate': None, 'avg_return': None,
            'median_return': None, 'best': None, 'worst': None,
            'profit_factor': None, 'cum_return_simple': None,
            'std_dev': None,
        }
    wins   = [r for r in returns if r > 0]
    losses = [r for r in returns if r < 0]
    gross_win  = sum(wins)
    gross_loss = abs(sum(losses))
    pf = (gross_win / gross_loss) if gross_loss > 0 else (float('inf') if gross_win > 0 else None)
    return {
        'trades':            n,
        'wins':              len(wins),
        'losses':            len(losses),
        'win_rate':          round(100 * len(wins) / n, 2),
        'avg_return':        round(statistics.mean(returns), 2),
        'median_return':     round(statistics.median(returns), 2),
        'best':              round(max(returns), 2),
        'worst':             round(min(returns), 2),
        'profit_factor':     round(pf, 2) if pf is not None and math.isfinite(pf) else pf,
        'cum_return_simple': round(sum(returns), 2),
        'std_dev':           round(statistics.pstdev(returns), 2) if n > 1 else 0,
    }


def equity_curve(entries_sorted):
    curve = []
    cum = 0.0
    peak = 0.0
    max_dd = 0.0
    for e in entries_sorted:
        r = e.get('rendimento_pct')
        if not _is_number(r):
            continue
        cum += r
        peak = max(peak, cum)
        dd = peak - cum
        max_dd = max(max_dd, dd)
        curve.append({
            'ticker':     e.get('ticker'),
            'chiusura':   e.get('chiusura_ts_it'),
            'rendimento': round(r, 2),
            'cumulato':   round(cum, 2),
        })
    return curve, round(max_dd, 2)


def analyze_log(path, label):
    if not os.path.exists(path):
        return None, f"[{label}] file non trovato: {path}"

    with open(path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except Exception as e:
            return None, f"[{label}] JSON invalido: {e}"

    if not isinstance(data, list):
        return None, f"[{label}] formato inatteso (non lista)"

    total     = len(data)
    aperti    = [e for e in data if e.get('stato') == 'aperto']
    chiusi    = [e for e in data if e.get('stato') == 'chiuso']
    chiusi_ok = [e for e in chiusi if _is_number(e.get('rendimento_pct'))]
    chiusi_nan = [e for e in chiusi if not _is_number(e.get('rendimento_pct'))]

    returns = [e['rendimento_pct'] for e in chiusi_ok]

    def _key(e):
        t = e.get('chiusura_ts_it')
        if not t:
            return datetime.datetime.min
        try:
            return datetime.datetime.strptime(t, '%d/%m/%Y %H:%M')
        except Exception:
            return datetime.datetime.min
    chiusi_ok_sorted = sorted(chiusi_ok, key=_key)
    curve, max_dd = equity_curve(chiusi_ok_sorted)

    by_leva = defaultdict(list)
    for e in chiusi_ok:
        by_leva[e.get('leva', 1)].append(e['rendimento_pct'])
    leva_stats = {k: stats_from_returns(v) for k, v in sorted(by_leva.items())}

    durations = [_duration_days(e) for e in chiusi_ok]
    durations = [d for d in durations if d is not None and d >= 0]

    ticker_count = defaultdict(int)
    for e in data:
        ticker_count[e.get('ticker')] += 1
    top_tickers = sorted(ticker_count.items(), key=lambda x: -x[1])[:10]

    nan_tickers = [{
        'ticker':        e.get('ticker'),
        'flip_ts_it':    e.get('flip_ts_it'),
        'chiusura_ts_it': e.get('chiusura_ts_it'),
        'ultimo_prezzo': e.get('ultimo_prezzo'),
        'prezzo_ingresso': e.get('prezzo_ingresso'),
    } for e in chiusi_nan]

    return {
        'label':            label,
        'file':             path,
        'total_records':    total,
        'aperti':           len(aperti),
        'chiusi':           len(chiusi),
        'chiusi_validi':    len(chiusi_ok),
        'chiusi_nan':       len(chiusi_nan),
        'pct_nan_su_chiusi': round(100 * len(chiusi_nan) / len(chiusi), 1) if chiusi else 0,
        'stats':            stats_from_returns(returns),
        'by_leva':          leva_stats,
        'max_drawdown':     max_dd,
        'avg_duration_days': round(statistics.mean(durations), 2) if durations else None,
        'median_duration_days': round(statistics.median(durations), 2) if durations else None,
        'top_tickers':      top_tickers,
        'nan_details':      nan_tickers[:20],
        'equity_curve':     curve,
    }, None


def render_txt(reports):
    lines = []
    lines.append('=' * 70)
    lines.append('RAPTOR — Report Super Best Buy')
    lines.append(datetime.datetime.now().strftime('Generato: %d/%m/%Y %H:%M'))
    lines.append('=' * 70)

    for r in reports:
        if r is None:
            continue
        lines.append('')
        lines.append(f'── {r["label"]}  ({r["file"]}) ──')
        lines.append(f'  Record totali:       {r["total_records"]}')
        lines.append(f'  Aperti:              {r["aperti"]}')
        lines.append(f'  Chiusi:              {r["chiusi"]}')
        lines.append(f'    - con rendimento:  {r["chiusi_validi"]}')
        lines.append(f'    - con NaN:         {r["chiusi_nan"]}  ({r["pct_nan_su_chiusi"]}%)')
        lines.append('')

        s = r['stats']
        if s['trades'] == 0:
            lines.append('  Nessun trade con rendimento valido.')
            continue

        lines.append(f'  PERFORMANCE (su {s["trades"]} trade chiusi validi)')
        lines.append(f'    Win rate:          {s["win_rate"]}%   ({s["wins"]}W / {s["losses"]}L)')
        lines.append(f'    Rendimento medio:  {s["avg_return"]:+.2f}%')
        lines.append(f'    Rendimento mediano:{s["median_return"]:+.2f}%')
        lines.append(f'    Migliore:          {s["best"]:+.2f}%')
        lines.append(f'    Peggiore:          {s["worst"]:+.2f}%')
        lines.append(f'    Std dev:           {s["std_dev"]:.2f}')
        lines.append(f'    Profit factor:     {s["profit_factor"]}')
        lines.append(f'    P/L cumulato:      {s["cum_return_simple"]:+.2f}%')
        lines.append(f'    Max drawdown:      -{r["max_drawdown"]:.2f}%')
        if r['avg_duration_days'] is not None:
            lines.append(f'    Durata media:      {r["avg_duration_days"]} gg (mediana {r["median_duration_days"]} gg)')
        lines.append('')

        lines.append('  BREAKDOWN PER LEVA')
        for lev, st in r['by_leva'].items():
            if st['trades'] == 0:
                continue
            lines.append(f'    {lev}x  ->  {st["trades"]:>3} trade | '
                         f'WR {st["win_rate"]:>5.1f}% | '
                         f'avg {st["avg_return"]:+6.2f}% | '
                         f'cum {st["cum_return_simple"]:+7.2f}%')
        lines.append('')

        lines.append('  TICKER PIU FREQUENTI')
        for t, c in r['top_tickers']:
            lines.append(f'    {t:<8} {c}x')
        lines.append('')

        if r['nan_details']:
            lines.append(f'  TRADE CHIUSI CON NaN (primi {len(r["nan_details"])})')
            for e in r['nan_details']:
                lines.append(f'    {e["ticker"]:<8} flip {e["flip_ts_it"]} -> chiuso {e["chiusura_ts_it"]} '
                             f'(ingresso {e["prezzo_ingresso"]}, ultimo {e["ultimo_prezzo"]})')
            lines.append('')

    lines.append('=' * 70)
    lines.append('FINE REPORT')
    lines.append('=' * 70)
    return '\n'.join(lines)


def main():
    reports = []
    errors  = []
    for label, path in SBB_FILES:
        r, err = analyze_log(path, label)
        if r:
            reports.append(r)
        if err:
            errors.append(err)

    for e in errors:
        print(e)

    if not reports:
        print('Nessun report generato.')
        return

    with open(REPORT_JSON, 'w', encoding='utf-8') as f:
        json.dump({
            'generated_at': datetime.datetime.now().isoformat(),
            'reports': reports,
        }, f, ensure_ascii=False, indent=2)

    txt = render_txt(reports)
    with open(REPORT_TXT, 'w', encoding='utf-8') as f:
        f.write(txt)

    print(txt)
    print()
    print(f'Salvato {REPORT_JSON} e {REPORT_TXT}')


if __name__ == '__main__':
    main()
