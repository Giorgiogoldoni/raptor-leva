#!/usr/bin/env python3
"""
RAPTOR — Backtest SAR su 3 timeframe (daily / weekly / 15-day)

Legge data/charts/index.json + data/charts/*.json
Per ogni ticker e ogni timeframe simula:
  ENTRY: flip SAR BULL + filtri SBB (ao>0, ao_improving, vol>=1.5, |perfOggi|<=4)
  EXIT:  flip SAR BEAR
Confronta WR, PF, cum, DD, trade, breakdown per leva.

Output:
  - backtest_sar_multi.json
  - backtest_sar_multi.txt
"""

import json, math, statistics, datetime, os
from collections import defaultdict


CHARTS_DIR = 'data/charts'
INDEX_FILE = os.path.join(CHARTS_DIR, 'index.json')

TIMEFRAMES = {
    'daily':  1,   # baseline
    'weekly': 5,   # 1 barra = ~5 giorni
    'd15':    15,  # 1 barra = 15 giorni
}

# Filtri SBB (uguali al live)
SBB_AO_MIN       = 0.0    # ao > 0
SBB_VOL_MIN      = 1.5    # vol_ratio >= 1.5
SBB_PERFOGGI_MAX = 4.0    # |perfOggi| <= 4%

# Parametri SAR
SAR_STEP   = 0.03
SAR_MAX_AF = 0.25


# ─────────────────────────────────────────────
# Indicatori (ricopiati dal live, ma su barre generiche)
# ─────────────────────────────────────────────
def calc_sar(high, low, step=SAR_STEP, max_af=SAR_MAX_AF):
    n = len(high)
    sar = [None] * n
    if n < 5:
        return sar
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
                if high[i] > ep:
                    ep = high[i]; af = min(af + step, max_af)
        else:
            sar[i] = max(ps + af * (ep - ps), high[i-1], high[i-2] if i >= 2 else high[i-1])
            if high[i] > sar[i]:
                bull = True; af = step; sar[i] = ep; ep = high[i]
            else:
                if low[i] < ep:
                    ep = low[i]; af = min(af + step, max_af)
    return sar


def calc_ao_fast(high, low):
    """AO veloce EMA3 - EMA13 sul midpoint. Ritorna serie."""
    n = len(high)
    mid = [(h + l) / 2 for h, l in zip(high, low)]
    out = [0.0] * n
    if n < 13:
        return out

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
    for i in range(n):
        out[i] = round(e3[i] - e13[i], 6)
    return out


def vol_ratio_at(volumes, i, lookback=20):
    if i < lookback + 1:
        return 1.0
    window = volumes[i - lookback:i]
    avg = sum(window) / len(window) if window else 0
    return volumes[i] / avg if avg > 0 else 1.0


def perf_at(closes, i, lookback):
    if i < lookback:
        return 0.0
    base = closes[i - lookback]
    if base == 0:
        return 0.0
    return (closes[i] / base - 1) * 100


# ─────────────────────────────────────────────
# Aggregazione barre
# ─────────────────────────────────────────────
def aggregate(dates, opens, closes, highs, lows, volumes, n_bars):
    """Aggrega ogni n_bars barre daily in una sola barra."""
    if n_bars == 1:
        return dates, opens, closes, highs, lows, volumes

    agg_d, agg_o, agg_c, agg_h, agg_l, agg_v = [], [], [], [], [], []
    for i in range(0, len(dates), n_bars):
        chunk_idx = list(range(i, min(i + n_bars, len(dates))))
        if len(chunk_idx) < max(2, n_bars // 2):
            # salta chunk troppo piccoli (ultimo pezzo parziale)
            continue
        agg_d.append(dates[chunk_idx[-1]])   # data dell'ultima barra del chunk
        agg_o.append(opens[chunk_idx[0]])
        agg_c.append(closes[chunk_idx[-1]])
        agg_h.append(max(highs[j] for j in chunk_idx))
        agg_l.append(min(lows[j] for j in chunk_idx))
        agg_v.append(sum(volumes[j] for j in chunk_idx))
    return agg_d, agg_o, agg_c, agg_h, agg_l, agg_v


# ─────────────────────────────────────────────
# Simulazione SBB su un ticker / timeframe
# ─────────────────────────────────────────────
def simulate(dates, opens, closes, highs, lows, volumes, leva, ticker):
    n = len(closes)
    if n < 30:
        return []

    sar = calc_sar(highs, lows)
    ao_arr = calc_ao_fast(highs, lows)

    trades = []
    open_trade = None

    for i in range(2, n):
        if sar[i] is None or sar[i-1] is None:
            continue

        # Rileva flip
        prev_bull = closes[i-1] > sar[i-1]
        curr_bull = closes[i] > sar[i]
        flip_bull = (not prev_bull) and curr_bull
        flip_bear = prev_bull and (not curr_bull)

        # Apertura su flip BULL con filtri SBB
        if flip_bull and open_trade is None:
            ao = ao_arr[i]
            ao_imp = (i >= 3 and ao_arr[i] > ao_arr[i-1] > ao_arr[i-2])
            vr = vol_ratio_at(volumes, i)
            perf = perf_at(closes, i, 1)

            if (ao > SBB_AO_MIN
                    and ao_imp
                    and vr >= SBB_VOL_MIN
                    and abs(perf) <= SBB_PERFOGGI_MAX):
                open_trade = {
                    'ticker': ticker,
                    'leva': leva,
                    'entry_idx': i,
                    'entry_date': dates[i],
                    'entry_price': closes[i],
                }

        # Chiusura su flip BEAR
        elif flip_bear and open_trade is not None:
            open_trade['exit_idx'] = i
            open_trade['exit_date'] = dates[i]
            open_trade['exit_price'] = closes[i]
            pnl = (open_trade['exit_price'] / open_trade['entry_price'] - 1) * 100
            open_trade['pnl_pct'] = round(pnl, 2)
            open_trade['bars_held'] = i - open_trade['entry_idx']
            trades.append(open_trade)
            open_trade = None

    return trades


# ─────────────────────────────────────────────
# Statistiche
# ─────────────────────────────────────────────
def stats(returns):
    n = len(returns)
    if n == 0:
        return {'trades': 0}
    wins = [r for r in returns if r > 0]
    losses = [r for r in returns if r < 0]
    gw = sum(wins)
    gl = abs(sum(losses))
    pf = gw / gl if gl > 0 else (float('inf') if gw > 0 else 0)

    # Equity curve + max drawdown
    cum = 0.0
    peak = 0.0
    max_dd = 0.0
    for r in returns:
        cum += r
        peak = max(peak, cum)
        dd = peak - cum
        max_dd = max(max_dd, dd)

    return {
        'trades':      n,
        'wins':        len(wins),
        'losses':      len(losses),
        'win_rate':    round(100 * len(wins) / n, 2),
        'avg_return':  round(statistics.mean(returns), 2),
        'median':      round(statistics.median(returns), 2),
        'best':        round(max(returns), 2),
        'worst':       round(min(returns), 2),
        'std_dev':     round(statistics.pstdev(returns), 2) if n > 1 else 0,
        'profit_factor': round(pf, 3) if math.isfinite(pf) else None,
        'cum_return':  round(sum(returns), 2),
        'max_dd':      round(max_dd, 2),
    }


def group_by_leva(trades):
    by_leva = defaultdict(list)
    for t in trades:
        by_leva[t['leva']].append(t['pnl_pct'])
    return {k: stats(v) for k, v in sorted(by_leva.items())}


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    now = datetime.datetime.now()
    print(f"Backtest SAR multi-TF — {now.strftime('%d/%m/%Y %H:%M')}")

    if not os.path.exists(INDEX_FILE):
        print(f"ERRORE: {INDEX_FILE} non trovato")
        return

    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        idx = json.load(f)
    tickers = idx.get('index', [])
    print(f"Ticker nell'indice: {len(tickers)}")

    # trades per timeframe
    all_trades = {tf: [] for tf in TIMEFRAMES}

    ok = errors = 0
    for i, t in enumerate(tickers):
        fname = t.get('f')
        if not fname:
            continue
        fpath = os.path.join(CHARTS_DIR, fname)
        if not os.path.exists(fpath):
            errors += 1
            continue
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            errors += 1
            continue

        dates = data.get('dates', [])
        opens = data.get('opens', [])
        closes = data.get('closes', [])
        highs = data.get('highs', [])
        lows = data.get('lows', [])
        volumes = data.get('volumes', [])
        leva = t.get('leva', 1)
        ticker = t.get('t', '')

        # Pulisci null
        if len(dates) < 30 or len(closes) != len(dates):
            errors += 1
            continue

        # Rimuovi barre con None (Yahoo a volte li mette)
        clean = [(d, o, c, h, l, v) for d, o, c, h, l, v in
                 zip(dates, opens, closes, highs, lows, volumes)
                 if c is not None and h is not None and l is not None and v is not None]
        if len(clean) < 30:
            errors += 1
            continue
        d_c, o_c, c_c, h_c, l_c, v_c = zip(*clean)
        dates, opens, closes, highs, lows, volumes = map(
            list, (d_c, o_c, c_c, h_c, l_c, v_c))

        for tf_name, nb in TIMEFRAMES.items():
            if nb == 1:
                ag = (dates, opens, closes, highs, lows, volumes)
            else:
                ag = aggregate(dates, opens, closes, highs, lows, volumes, nb)
            trades = simulate(*ag, leva=leva, ticker=ticker)
            all_trades[tf_name].extend(trades)

        ok += 1
        if (i + 1) % 30 == 0:
            print(f"  {i+1}/{len(tickers)} — ok:{ok} err:{errors}")

    print(f"\nProcessati: {ok} ok, {errors} errori\n")

    # Report per timeframe
    report = {}
    for tf_name, trades in all_trades.items():
        returns = [t['pnl_pct'] for t in trades]
        s = stats(returns)
        leva_stats = group_by_leva(trades)
        # distribuzione per ticker
        per_ticker = defaultdict(list)
        for t in trades:
            per_ticker[t['ticker']].append(t['pnl_pct'])
        top_tickers = sorted(
            [(k, len(v), round(sum(v), 2)) for k, v in per_ticker.items()],
            key=lambda x: -x[1]
        )[:10]

        report[tf_name] = {
            'timeframe':         tf_name,
            'bars_per_trade':    TIMEFRAMES[tf_name],
            'stats':             s,
            'by_leva':           leva_stats,
            'top_tickers':       top_tickers,
        }

    # Output JSON
    out_json = {
        'generated_at': now.isoformat(),
        'config': {
            'SAR_STEP': SAR_STEP, 'SAR_MAX_AF': SAR_MAX_AF,
            'SBB_AO_MIN': SBB_AO_MIN, 'SBB_VOL_MIN': SBB_VOL_MIN,
            'SBB_PERFOGGI_MAX': SBB_PERFOGGI_MAX,
            'timeframes': TIMEFRAMES,
        },
        'report': report,
    }
    with open('backtest_sar_multi.json', 'w', encoding='utf-8') as f:
        json.dump(out_json, f, ensure_ascii=False, indent=2)

    # Output TXT
    lines = []
    lines.append('=' * 78)
    lines.append('RAPTOR — Backtest SAR multi-timeframe')
    lines.append(f"Generato: {now.strftime('%d/%m/%Y %H:%M')}")
    lines.append(f"Ticker processati: {ok}  |  errori: {errors}")
    lines.append('=' * 78)

    for tf_name in ['daily', 'weekly', 'd15']:
        r = report[tf_name]
        s = r['stats']
        lines.append('')
        lines.append(f'═══ {tf_name.upper()} (1 barra = {r["bars_per_trade"]} gg) ═══')
        if s.get('trades', 0) == 0:
            lines.append('  Nessun trade')
            continue
        lines.append(f"  Trade:        {s['trades']}  ({s['wins']}W / {s['losses']}L)")
        lines.append(f"  Win rate:     {s['win_rate']}%")
        lines.append(f"  Rend. medio:  {s['avg_return']:+.2f}%")
        lines.append(f"  Mediana:      {s['median']:+.2f}%")
        lines.append(f"  Best:         {s['best']:+.2f}%")
        lines.append(f"  Worst:        {s['worst']:+.2f}%")
        lines.append(f"  Std dev:      {s['std_dev']:.2f}")
        lines.append(f"  Profit factor:{s['profit_factor']}")
        lines.append(f"  Cum return:   {s['cum_return']:+.2f}%")
        lines.append(f"  Max DD:       -{s['max_dd']:.2f}%")
        lines.append('')
        lines.append('  BREAKDOWN PER LEVA:')
        for lev, ls in r['by_leva'].items():
            if ls.get('trades', 0) == 0:
                continue
            lines.append(f"    {lev}x  {ls['trades']:>4} trade | WR {ls['win_rate']:>5.1f}% | "
                         f"avg {ls['avg_return']:+6.2f}% | cum {ls['cum_return']:+8.2f}%")
        lines.append('')
        lines.append('  TOP TICKER (per numero trade):')
        for k, n, cum in r['top_tickers']:
            lines.append(f"    {k:<8} {n:>3}x  cum {cum:+8.2f}%")

    lines.append('')
    lines.append('=' * 78)
    lines.append('FINE')
    lines.append('=' * 78)

    txt = '\n'.join(lines)
    with open('backtest_sar_multi.txt', 'w', encoding='utf-8') as f:
        f.write(txt)

    print(txt)
    print()
    print('Salvato backtest_sar_multi.json + backtest_sar_multi.txt')


if __name__ == '__main__':
    main()
