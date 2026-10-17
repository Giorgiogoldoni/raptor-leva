#!/usr/bin/env python3
"""
RAPTOR — Analisi Live 1x (SL10 / TP30)
"""
import json, math, statistics, datetime, os

FILE = 'live_trades_1x.json'
REPORT_TXT = 'live_1x_report.txt'

def stats(returns):
    n = len(returns)
    if n == 0: return {'trades': 0}
    wins = [r for r in returns if r > 0]
    losses = [r for r in returns if r < 0]
    gw = sum(wins)
    gl = abs(sum(losses))
    pf = gw / gl if gl > 0 else (float('inf') if gw > 0 else 0)
    cum = 0.0; peak = 0.0; max_dd = 0.0
    for r in returns:
        cum += r; peak = max(peak, cum); max_dd = max(max_dd, peak - cum)
    return {
        'trades': n, 'wins': len(wins), 'losses': len(losses),
        'win_rate': round(100 * len(wins) / n, 2),
        'avg_return': round(statistics.mean(returns), 2),
        'median': round(statistics.median(returns), 2),
        'best': round(max(returns), 2), 'worst': round(min(returns), 2),
        'profit_factor': round(pf, 2) if math.isfinite(pf) else None,
        'cum_return': round(sum(returns), 2), 'max_dd': round(max_dd, 2),
    }

def main():
    if not os.path.exists(FILE):
        print(f"ERRORE: {FILE} non trovato")
        return

    with open(FILE, 'r', encoding='utf-8') as f:
        log = json.load(f)

    total = len(log)
    aperti = [e for e in log if e.get('stato') == 'aperto']
    chiusi = [e for e in log if e.get('stato') == 'chiuso']
    chiusi_ok = [e for e in chiusi if isinstance(e.get('rendimento_pct'), (int, float)) and math.isfinite(e.get('rendimento_pct'))]

    returns = [e['rendimento_pct'] for e in chiusi_ok]
    s = stats(returns)

    reasons = {}
    for e in chiusi_ok:
        r = e.get('exit_reason', '?')
        reasons[r] = reasons.get(r, 0) + 1

    lines = []
    lines.append('=' * 70)
    lines.append('RAPTOR — Live 1x Report (SL10 / TP30)')
    lines.append(f"Generato: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}")
    lines.append('=' * 70)
    lines.append(f"Trade totali:   {total}")
    lines.append(f"  Aperti:       {len(aperti)}")
    lines.append(f"  Chiusi:       {len(chiusi)}  (validi: {len(chiusi_ok)})")
    lines.append('')

    if s.get('trades', 0) > 0:
        lines.append('PERFORMANCE')
        lines.append(f"  Win rate:        {s['win_rate']}%  ({s['wins']}W / {s['losses']}L)")
        lines.append(f"  Rend. medio:     {s['avg_return']:+.2f}%")
        lines.append(f"  Mediana:         {s['median']:+.2f}%")
        lines.append(f"  Migliore:        {s['best']:+.2f}%")
        lines.append(f"  Peggiore:        {s['worst']:+.2f}%")
        lines.append(f"  Profit factor:   {s['profit_factor']}")
        lines.append(f"  Cumulato:        {s['cum_return']:+.2f}%")
        lines.append(f"  Max DD:          -{s['max_dd']:.2f}%")
        lines.append('')
        lines.append('EXIT REASONS')
        for r, c in reasons.items():
            lines.append(f"  {r}: {c}")
    else:
        lines.append('Nessun trade chiuso.')

    txt = '\n'.join(lines)
    with open(REPORT_TXT, 'w', encoding='utf-8') as f:
        f.write(txt)
    print(txt)

if __name__ == '__main__':
    main()
