#!/usr/bin/env python3
"""
RAPTOR — Backtest SAR OTTIMIZZATO (Solo ETF 1x)

Filtra solo i ticker con leva == 1.
Testa la griglia di uscite per trovare la combinazione migliore su ETF non a leva.
"""

import json, math, statistics, datetime, os
from collections import defaultdict

CHARTS_DIR = 'data/charts'
INDEX_FILE = os.path.join(CHARTS_DIR, 'index.json')

SAR_STEP   = 0.03
SAR_MAX_AF = 0.25

# Filtri entrata (selettivi)
ENTRY_AO_MIN          = 0.0
ENTRY_VOL_MIN         = 1.5
ENTRY_PERFOGGI_MAX    = 4.0
ENTRY_KAMA_SLOPE_MIN  = 0.0

# Griglia uscite da testare
EXIT_STRATEGIES = [
    ('SAR_only',          None,  None,  None,  None),
    ('SL5_TP15',          -5.0,  None,  None,  15.0),
    ('SL7_TP20',          -7.0,  None,  None,  20.0),
    ('SL10_TP30',        -10.0,  None,  None,  30.0),
    ('Trail5_a10',        None,  10.0,   5.0,  None),
    ('Trail3_a7',         None,   7.0,   3.0,  None),
    ('Trail5_a10_TP25',   None,  10.0,   5.0,  25.0),
    ('SL7_Trail5_a10',    -7.0,  10.0,   5.0,  None),
    ('SL7_Trail5_a10_TP20',-7.0, 10.0,   5.0,  20.0),
]

def calc_sar(high, low, step=SAR_STEP, max_af=SAR_MAX_AF):
    n = len(high)
    sar = [None] * n
    if n < 5: return sar
    bull = high[1] > high[0]
    af = step
    ep = max(high[:2]) if bull else min(low[:2])
    sar[1] = min(low[:2]) if bull else max(high[:2])
    for i in range(2, n):
        ps = sar[i-1]
        if bull:
            sar[i] = min(ps + af * (ep - ps), low[i-1], low[i-2] if i >= 2 else low[i-1])
            if low[i] < sar[i]:
                bull = False; af = step; sar[i] = ep; ep = low[i]
            else:
                if high[i] > ep: ep = high[i]; af = min(af + step, max_af)
        else:
            sar[i] = max(ps + af * (ep - ps), high[i-1], high[i-2] if i >= 2 else high[i-1])
            if high[i] > sar[i]:
                bull = True; af = step; sar[i] = ep; ep = high[i]
            else:
                if low[i] < ep: ep = low[i]; af = min(af + step, max_af)
    return sar

def calc_kama(close, n=10, fast=2, slow=30):
    fast_sc = 2 / (fast + 1)
    slow_sc = 2 / (slow + 1)
    kama = [None] * len(close)
    if len(close) <= n: return kama
    kama[n] = close[n]
    for i in range(n + 1, len(close)):
        direction = abs(close[i] - close[i-n])
        volatility = sum(abs(close[j] - close[j-1]) for j in range(i-n+1, i+1))
        er = direction / volatility if volatility else 0
        sc = (er * (fast_sc - slow_sc) + slow_sc) ** 2
        kama[i] = kama[i-1] + sc * (close[i] - kama[i-1])
    return kama

def calc_ao_fast(high, low):
    n = len(high)
    mid = [(h + l) / 2 for h, l in zip(high, low)]
    out = [0.0] * n
    if n < 13: return out
    def ema_series(arr, p):
        k = 2 / (p + 1)
        e = arr[0]
        s = [e]
        for x in arr[1:]:
            e = x * k + e * (1 - k)
            s.append(e)
        return s
    e3 = ema_series(mid, 3)
    e13 = ema_series(mid, 13)
    return [round(a - b, 6) for a, b in zip(e3, e13)]

def vol_ratio_at(volumes, i, lookback=20):
    if i < lookback + 1: return 1.0
    window = volumes[i - lookback:i]
    avg = sum(window) / len(window) if window else 0
    return volumes[i] / avg if avg > 0 else 1.0

def perf_at(closes, i, lookback):
    if i < lookback: return 0.0
    base = closes[i - lookback]
    if base == 0: return 0.0
    return (closes[i] / base - 1) * 100

def simulate(dates, closes, highs, lows, volumes, leva, ticker,
             hard_sl=None, trail_after=None, trail_dist=None, take_profit=None):
    n = len(closes)
    if n < 30: return []
    sar = calc_sar(highs, lows)
    ao_arr = calc_ao_fast(highs, lows)
    kama_slow = calc_kama(closes, n=20, fast=2, slow=40)

    trades = []
    open_t = None

    for i in range(2, n):
        if sar[i] is None or sar[i-1] is None: continue
        prev_bull = closes[i-1] > sar[i-1]
        curr_bull = closes[i] > sar[i]
        flip_bull = (not prev_bull) and curr_bull
        flip_bear = prev_bull and (not curr_bull)
        price = closes[i]

        if open_t is not None:
            open_t['peak'] = max(open_t['peak'], price)
            peak_pnl = (open_t['peak'] / open_t['entry_price'] - 1) * 100
            pnl_now = (price / open_t['entry_price'] - 1) * 100
            exit_reason = None

            if hard_sl is not None and pnl_now <= hard_sl: exit_reason = 'SL'
            elif take_profit is not None and pnl_now >= take_profit: exit_reason = 'TP'
            elif (trail_after is not None and trail_dist is not None and peak_pnl >= trail_after):
                if pnl_now <= peak_pnl - trail_dist: exit_reason = 'TRAIL'
            elif flip_bear: exit_reason = 'SAR'

            if exit_reason:
                open_t['exit_idx'] = i
                open_t['exit_date'] = dates[i]
                open_t['exit_price'] = price
                open_t['exit_reason'] = exit_reason
                open_t['pnl_pct'] = round(pnl_now, 2)
                open_t['bars_held'] = i - open_t['entry_idx']
                open_t['peak_pnl'] = round(peak_pnl, 2)
                trades.append(open_t)
                open_t = None
            continue

        if flip_bull:
            ao = ao_arr[i]
            ao_imp = (i >= 3 and ao_arr[i] > ao_arr[i-1] > ao_arr[i-2])
            vr = vol_ratio_at(volumes, i)
            perf = perf_at(closes, i, 1)
            kama_slope_ok = True
            if kama_slow[i] is not None and kama_slow[i - 10] is not None:
                kama_slope_ok = (kama_slow[i] - kama_slow[i - 10]) > ENTRY_KAMA_SLOPE_MIN

            if (ao > ENTRY_AO_MIN and ao_imp and vr >= ENTRY_VOL_MIN
                    and abs(perf) <= ENTRY_PERFOGGI_MAX and kama_slope_ok):
                open_t = {
                    'ticker': ticker, 'leva': leva, 'entry_idx': i,
                    'entry_date': dates[i], 'entry_price': price, 'peak': price,
                }
    return trades

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
        'std_dev': round(statistics.pstdev(returns), 2) if n > 1 else 0,
        'profit_factor': round(pf, 3) if math.isfinite(pf) else None,
        'cum_return': round(sum(returns), 2), 'max_dd': round(max_dd, 2),
    }

def main():
    now = datetime.datetime.now()
    print(f"Backtest SAR 1x ONLY — {now.strftime('%d/%m/%Y %H:%M')}")
    if not os.path.exists(INDEX_FILE): return
    
    with open(INDEX_FILE, 'r', encoding='utf-8') as f: idx = json.load(f)
    tickers = idx.get('index', [])

    datasets = []
    for t in tickers:
        # Filtro 1x ONLY
        if t.get('leva', 1) != 1:
            continue

        fname = t.get('f')
        if not fname: continue
        fpath = os.path.join(CHARTS_DIR, fname)
        if not os.path.exists(fpath): continue
        try:
            with open(fpath, 'r', encoding='utf-8') as f: data = json.load(f)
        except Exception: continue
        dates = data.get('dates', []); opens = data.get('opens', [])
        closes = data.get('closes', []); highs = data.get('highs', [])
        lows = data.get('lows', []); volumes = data.get('volumes', [])
        if len(dates) < 30 or len(closes) != len(dates): continue
        clean = [(d, o, c, h, l, v) for d, o, c, h, l, v in zip(dates, opens, closes, highs, lows, volumes) if c is not None and h is not None and l is not None and v is not None]
        if len(clean) < 30: continue
        d_c, o_c, c_c, h_c, l_c, v_c = zip(*clean)
        datasets.append({
            'ticker': t.get('t', ''), 'leva': t.get('leva', 1),
            'dates': list(d_c), 'opens': list(o_c), 'closes': list(c_c),
            'highs': list(h_c), 'lows': list(l_c), 'volumes': list(v_c),
        })

    print(f"Ticker 1x caricati: {len(datasets)}")

    results = {}
    for strat_name, hard_sl, trail_after, trail_dist, tp in EXIT_STRATEGIES:
        all_trades = []
        for ds in datasets:
            trades = simulate(ds['dates'], ds['closes'], ds['highs'], ds['lows'], ds['volumes'], ds['leva'], ds['ticker'], hard_sl, trail_after, trail_dist, tp)
            all_trades.extend(trades)
        returns = [t['pnl_pct'] for t in all_trades]
        s = stats(returns)
        reasons = defaultdict(int)
        for t in all_trades: reasons[t.get('exit_reason', '?')] += 1
        results[strat_name] = {
            'config': {'hard_sl': hard_sl, 'trail_after': trail_after, 'trail_dist': trail_dist, 'take_profit': tp},
            'stats': s, 'exit_reasons': dict(reasons),
        }

    with open('backtest_sar_1x.json', 'w', encoding='utf-8') as f:
        json.dump({'generated_at': now.isoformat(), 'results': results}, f, ensure_ascii=False, indent=2)

    lines = []
    lines.append('=' * 100)
    lines.append('RAPTOR — SAR ENTRATA SELETTIVA + USCITA OTTIMIZZATA (ETF 1x ONLY)')
    lines.append(f"Generato: {now.strftime('%d/%m/%Y %H:%M')} | Ticker 1x: {len(datasets)}")
    lines.append('=' * 100 + '\n')
    header = f"{'Strategia':<24} {'Trade':>6} {'WR%':>7} {'Avg%':>7} {'Med%':>7} {'PF':>7} {'Cum%':>10} {'DD%':>9}"
    lines.append(header)
    lines.append('-' * len(header))
    
    sorted_strats = sorted(results.items(), key=lambda x: -(x[1]['stats'].get('profit_factor') or 0))
    for name, r in sorted_strats:
        s = r['stats']
        if s.get('trades', 0) == 0: lines.append(f"{name:<24} {'0':>6}"); continue
        pf = s['profit_factor'] if s['profit_factor'] is not None else 0
        lines.append(f"{name:<24} {s['trades']:>6} {s['win_rate']:>7.1f} {s['avg_return']:>+7.2f} {s['median']:>+7.2f} {pf:>7.3f} {s['cum_return']:>+10.2f} {s['max_dd']:>9.2f}")

    lines.append('\n' + '=' * 100 + '\nDETTAGLIO PER STRATEGIA (top 3 per PF)\n' + '=' * 100)
    for name, r in sorted_strats[:3]:
        s = r['stats']
        lines.append(f"\n── {name} ──\nConfig: {r['config']}")
        if s.get('trades', 0) == 0: lines.append('Nessun trade'); continue
        lines.append(f"Trade: {s['trades']} | WR: {s['win_rate']}% | PF: {s['profit_factor']} | Cum: {s['cum_return']:+.1f}% | DD: {s['max_dd']:.1f}%")
        lines.append(f"Exit reasons: {r['exit_reasons']}")
        lines.append(f"Migliore: {s['best']:+.2f}% | Peggiore: {s['worst']:+.2f}% | Mediana: {s['median']:+.2f}%")

    txt = '\n'.join(lines)
    with open('backtest_sar_1x.txt', 'w', encoding='utf-8') as f: f.write(txt)
    print(txt)

if __name__ == '__main__':
    main()
