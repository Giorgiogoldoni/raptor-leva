#!/usr/bin/env python3
"""
RAPTOR Leva Fetch — GitHub Actions
Scarica dati per ETF leva/short/inverse + VIX/VSTOXX
Doppia KAMA (veloce=entrata, lenta=uscita) + AO veloce (EMA3-EMA13) + volume
Gira ogni 30 min 7-19 lun-ven
"""

import json, time, datetime
import yfinance as yf

# ═══════════════════════════════════════════════════════
# TICKER LEVA (243 ticker)
# ═══════════════════════════════════════════════════════
TICKERS = [{"t":"XSD2","y":"XSD2.MI","n":"Xtrackers ShortDAX x2 Daily Swap UCITS ETF 1C","provider":"Xtrackers"},{"t":"XSDX","y":"XSDX.MI","n":"Xtrackers ShortDAX Daily Swap UCITS ETF 1C","provider":"Xtrackers"},{"t":"XSGL","y":"XSGL.MI","n":"Xtrackers Short iBoxx EUR Sovereigns Eurozone Daily Swap UCITS ETF 1C","provider":"Xtrackers"},{"t":"XSPS","y":"XSPS.MI","n":"Xtrackers S&P 500 Inverse Daily Swap UCITS ETF 1C","provider":"Xtrackers"},{"t":"XS2L","y":"XS2L.MI","n":"Xtrackers S&P 500 2x Leveraged Daily Swap UCITS ETF 1C","provider":"Xtrackers"},{"t":"XT21","y":"XT21.MI","n":"Xtrackers S&P 500 2x Inverse Daily Swap UCITS ETF 1C","provider":"Xtrackers"},{"t":"XLDX","y":"XLDX.MI","n":"Xtrackers LevDAX Daily Swap UCITS ETF 1C","provider":"Xtrackers"},{"t":"XTC5","y":"XTC5.MI","n":"Xtrackers iTraxx Crossover Short Daily Swap UCITS ETF 1C","provider":"Xtrackers"},{"t":"DBPG","y":"DBPG.MI","n":"Xtrackers iBoxx EUR Sovereigns Eurozone 25+ Daily Swap UCITS ETF 1C","provider":"Xtrackers"},{"t":"XT2D","y":"XT2D.MI","n":"Xtrackers iBoxx EUR Sovereigns Eurozone 7-10 Daily Swap UCITS ETF 1C","provider":"Xtrackers"},{"t":"DBXG","y":"DBXG.MI","n":"Xtrackers iBoxx EUR Sovereigns Eurozone Daily Swap UCITS ETF 1C","provider":"Xtrackers"},{"t":"XSTU","y":"XSTU.MI","n":"Xtrackers Euro Stoxx 50 Short Daily Swap UCITS ETF 1C","provider":"Xtrackers"},{"t":"DX2Z","y":"DX2Z.MI","n":"Xtrackers Euro Stoxx 50 Double Short Daily Swap UCITS ETF 1C","provider":"Xtrackers"},{"t":"DX2S","y":"DX2S.MI","n":"Xtrackers DAX Double Short Daily Swap UCITS ETF 1C","provider":"Xtrackers"},{"t":"DXSN","y":"DXSN.MI","n":"Xtrackers MSCI World Swap UCITS ETF","provider":"Xtrackers"},{"t":"MIB5","y":"MIB5.MI","n":"Leverage Shares 5x Long Ftse Mib Etp","provider":"LEVERAGE SHARES"},{"t":"MIBS","y":"MIBS.MI","n":"Leverage Shares -5x Short Ftse Mib Etp","provider":"LEVERAGE SHARES"},{"t":"5QQQ","y":"5QQQ.MI","n":"Leverage Shares 5x Long Nasdaq 100 Etp","provider":"LEVERAGE SHARES"},{"t":"SQQQ","y":"SQQQ.MI","n":"Leverage Shares -3x Short Nasdaq 100 Etp","provider":"LEVERAGE SHARES"},{"t":"3QQQ","y":"3QQQ.MI","n":"Leverage Shares 3x Long Nasdaq 100 Etp","provider":"LEVERAGE SHARES"},{"t":"3SPY","y":"3SPY.MI","n":"Leverage Shares 3x Long S&P 500 Etp","provider":"LEVERAGE SHARES"},{"t":"SSPX","y":"SSPX.MI","n":"Leverage Shares -3x Short S&P 500 Etp","provider":"LEVERAGE SHARES"},{"t":"3TSL","y":"3TSL.MI","n":"Leverage Shares 3x Long Tesla Etp","provider":"LEVERAGE SHARES"},{"t":"3NVD","y":"3NVD.MI","n":"Leverage Shares 3x Long Nvidia Etp","provider":"LEVERAGE SHARES"},{"t":"3APP","y":"3APP.MI","n":"Leverage Shares 3x Long Apple Etp","provider":"LEVERAGE SHARES"},{"t":"3MSF","y":"3MSF.MI","n":"Leverage Shares 3x Long Microsoft Etp","provider":"LEVERAGE SHARES"},{"t":"3AMZ","y":"3AMZ.MI","n":"Leverage Shares 3x Long Amazon Etp","provider":"LEVERAGE SHARES"},{"t":"3GOO","y":"3GOO.MI","n":"Leverage Shares 3x Long Alphabet Etp","provider":"LEVERAGE SHARES"},{"t":"3MET","y":"3MET.MI","n":"Leverage Shares 3x Long Meta Etp","provider":"LEVERAGE SHARES"},{"t":"HSC3L","y":"HSC3L.MI","n":"Sg Etn Daily Long 3x Hang Seng China Enterprises","provider":"SG"},{"t":"HSC3S","y":"HSC3S.MI","n":"Sg Etn Daily Short -3x Hang Seng China Enterprises","provider":"SG"},{"t":"SX5E3S","y":"SX5E3S.MI","n":"Sg Etc Euro Stoxx 50 -3x Daily Short Collateral","provider":"SG"},{"t":"SX5E3L","y":"SX5E3L.MI","n":"Sg Etc Euro Stoxx 50 +3x Daily Leverage Collateral","provider":"SG"},{"t":"DAX3L","y":"DAX3L.MI","n":"Sg Etc Dax +3x Daily Leverage Collateral","provider":"SG"},{"t":"DAX3S","y":"DAX3S.MI","n":"Sg Etc Dax -3x Daily Short Collateral","provider":"SG"},{"t":"5MIB","y":"5MIB.MI","n":"GraniteShares 5x Long Mib Daily Etp","provider":"GRANITIS"},{"t":"5SIT","y":"5SIT.MI","n":"GraniteShares 5x Short Mib Daily Etp","provider":"GRANITIS"},{"t":"3FNG","y":"3FNG.MI","n":"GraniteShares 3x Long Faang Etp","provider":"GRANITIS"},{"t":"3LCR","y":"3LCR.MI","n":"GraniteShares 3x Long Unicredit Daily Etp","provider":"GRANITIS"},{"t":"3LEN","y":"3LEN.MI","n":"GraniteShares 3x Long Enel Daily Etp","provider":"GRANITIS"},{"t":"3LNV","y":"3LNV.MI","n":"GraniteShares 3x Long Nvidia Daily Etp","provider":"GRANITIS"},{"t":"3LTS","y":"3LTS.MI","n":"GraniteShares 3x Long Tesla Daily Etp","provider":"GRANITIS"}]

# VIX e VSTOXX
VIX_TICKERS = [
    {"t": "VIX_USA",    "y": "^VIX",  "nome": "CBOE VIX USA"},
    {"t": "VSTOXX_EU",  "y": "^V2TX", "nome": "VSTOXX Europa"},
]

# ═══════════════════════════════════════════════════════
# INDICATORI — PARAMETRI LEVA
# ═══════════════════════════════════════════════════════

def calc_kama(close, n=10, fast=2, slow=30):
    """KAMA generica — parametri variabili"""
    fast_sc = 2/(fast+1)
    slow_sc = 2/(slow+1)
    kama = [None]*len(close)
    if len(close) <= n: return kama
    kama[n] = close[n]
    for i in range(n+1, len(close)):
        direction = abs(close[i] - close[i-n])
        volatility = sum(abs(close[j]-close[j-1]) for j in range(i-n+1,i+1))
        er = direction/volatility if volatility else 0
        sc = (er*(fast_sc-slow_sc)+slow_sc)**2
        kama[i] = kama[i-1] + sc*(close[i]-kama[i-1])
    return kama

def calc_ao_fast(high, low):
    """AO veloce: EMA3 - EMA13 dei midpoint (più reattivo per leva)"""
    mid = [(h+l)/2 for h,l in zip(high,low)]
    if len(mid) < 13: return 0
    def ema(arr, p):
        k=2/(p+1); e=arr[0]
        for x in arr[1:]: e=x*k+e*(1-k)
        return e
    return round(ema(mid,3) - ema(mid,13), 4)

def calc_vol_ratio(volume):
    if len(volume) < 21: return 1.0
    avg = sum(volume[-21:-1])/20
    return round(volume[-1]/avg, 2) if avg > 0 else 1.0

def calc_er(close, n=10):
    if len(close) < n+1: return 0
    direction = abs(close[-1]-close[-n-1])
    vol = sum(abs(close[-i]-close[-i-1]) for i in range(1,n+1))
    return round(direction/vol, 4) if vol else 0

def calc_rsi(close, n=14):
    if len(close) < n+2: return 50
    gains, losses = [], []
    for i in range(1,len(close)):
        d = close[i]-close[i-1]
        gains.append(max(d,0)); losses.append(max(-d,0))
    ag = sum(gains[-n:])/n; al = sum(losses[-n:])/n
    if al == 0: return 100
    return round(100-100/(1+ag/al), 2)

def calc_baffetti_fast(high, low):
    """Baffetti AO veloce — conta consecutivi crescenti"""
    if len(high) < 3: return 0
    mid = [(h+l)/2 for h,l in zip(high,low)]
    n = 0
    for i in range(len(mid)-1,0,-1):
        if mid[i] > mid[i-1]: n += 1
        else: break
    return n

def get_zona(price, kama_fast, kama_slow):
    """
    Zona operativa doppia KAMA:
    LONG_CONF  = prezzo > kama_veloce > kama_lenta  (entrata confermata)
    LONG_EARLY = prezzo > kama_veloce, sotto kama_lenta (entrata anticipata)
    GRIGIA     = prezzo tra le due KAMA
    USCITA     = prezzo < kama_lenta (uscita definitiva)
    STOP       = prezzo < entrambe e distanza > 2%
    """
    if kama_fast is None or kama_slow is None: return 'ND'
    if price > kama_fast and kama_fast > kama_slow:
        return 'LONG_CONF'
    elif price > kama_fast and price > kama_slow:
        return 'LONG_EARLY'
    elif price > kama_slow and price < kama_fast:
        return 'GRIGIA'
    elif price < kama_slow:
        gap = (kama_slow-price)/kama_slow*100 if kama_slow > 0 else 0
        return 'STOP' if gap > 2 else 'USCITA'
    return 'GRIGIA'

def get_segnale_leva(zona, ao, vol_ratio, er, baf):
    """Segnale leva — più selettivo, richiede volume e momentum"""
    if zona == 'LONG_CONF' and ao > 0 and vol_ratio >= 1.5 and baf >= 2:
        return 'LONG'
    elif zona == 'LONG_EARLY' and ao > 0 and baf >= 2:
        return 'EARLY'
    elif zona == 'LONG_CONF' or zona == 'LONG_EARLY':
        return 'WATCH'
    elif zona == 'STOP':
        return 'STOP'
    elif zona == 'USCITA':
        return 'USCITA'
    elif zona == 'GRIGIA':
        return 'ATTENZIONE'
    return ''

def get_regime_vix(vix, vstoxx):
    """Regime di mercato basato su VIX e VSTOXX"""
    v = vix if vix else 20
    vs = vstoxx if vstoxx else 20
    avg = (v + vs) / 2
    if avg < 15:   return {'regime': 'CALMA',      'mult': 1.00, 'color': 'verde'}
    if avg < 20:   return {'regime': 'NORMALE',    'mult': 0.95, 'color': 'giallo'}
    if avg < 25:   return {'regime': 'ATTENZIONE', 'mult': 0.85, 'color': 'arancio'}
    if avg < 30:   return {'regime': 'STRESS',     'mult': 0.70, 'color': 'rosso'}
    return             {'regime': 'PAURA',         'mult': 0.50, 'color': 'rosso_scuro'}

def calc_score_leva(zona, ao, vol_ratio, er, baf, regime_mult):
    """Score leva — penalizza fortemente quando VIX è alto"""
    base = 0
    if zona == 'LONG_CONF':  base = 60
    elif zona == 'LONG_EARLY': base = 40
    elif zona == 'GRIGIA':   base = 20
    base += min(baf, 5) * 6
    base += (10 if ao > 0 else 0)
    base += min(vol_ratio, 3) * 5
    base += er * 20
    return round(base * regime_mult, 1)

# ═══════════════════════════════════════════════════════
# FETCH VIX
# ═══════════════════════════════════════════════════════
def fetch_vix():
    vix_val = None; vstoxx_val = None
    for v in VIX_TICKERS:
        try:
            tk = yf.Ticker(v['y'])
            hist = tk.history(period='5d', interval='1d', timeout=15)
            if not hist.empty:
                val = float(hist['Close'].iloc[-1])
                if v['t'] == 'VIX_USA':   vix_val = round(val, 2)
                elif v['t'] == 'VSTOXX_EU': vstoxx_val = round(val, 2)
        except: pass
        time.sleep(0.5)
    return vix_val, vstoxx_val

# ═══════════════════════════════════════════════════════
# PROCESS TICKER LEVA
# ═══════════════════════════════════════════════════════
def process_leva(info, regime_mult):
    symbol = info['y']
    try:
        tk = yf.Ticker(symbol)
        hist = tk.history(period='1y', interval='1d', timeout=15)
        if hist.empty or len(hist) < 40: return None

        close  = [float(x) for x in hist['Close'].values]
        high   = [float(x) for x in hist['High'].values]
        low    = [float(x) for x in hist['Low'].values]
        volume = [float(x) for x in hist['Volume'].values]

        # Doppia KAMA
        kama_fast = calc_kama(close, n=5,  fast=3, slow=20)  # veloce → entrata
        kama_slow = calc_kama(close, n=20, fast=2, slow=40)  # lenta  → uscita

        kf = kama_fast[-1]; ks = kama_slow[-1]
        lc = close[-1]

        ao       = calc_ao_fast(high, low)
        vol_r    = calc_vol_ratio(volume)
        er       = calc_er(close)
        rsi      = calc_rsi(close)
        baf      = calc_baffetti_fast(high, low)
        zona     = get_zona(lc, kf, ks)
        segnale  = get_segnale_leva(zona, ao, vol_r, er, baf)
        score    = calc_score_leva(zona, ao, vol_r, er, baf, regime_mult)

        perf5  = round((lc/close[-6]-1)*100,2)  if len(close)>6  else 0
        perf20 = round((lc/close[-21]-1)*100,2) if len(close)>21 else 0

        return {
            'ticker':    info['t'],
            'yahoo':     symbol,
            'nome':      info.get('n',''),
            'provider':  info.get('provider',''),
            'segnale':   segnale,
            'zona':      zona,
            'score':     score,
            'prezzo':    round(lc, 4),
            'kama_fast': round(kf, 4) if kf else None,
            'kama_slow': round(ks, 4) if ks else None,
            'er':        er,
            'baff':      baf,
            'ao':        round(ao, 4),
            'rsi':       rsi,
            'volRatio':  vol_r,
            'perfSett':  perf5,
            'perfMese':  perf20,
        }
    except Exception:
        return None

# ═══════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════
def main():
    now = datetime.datetime.now()
    print(f"RAPTOR Leva Fetch — {now.strftime('%Y-%m-%d %H:%M')}")
    print(f"Ticker: {len(TICKERS)}")

    # 1. Fetch VIX
    print("Fetching VIX/VSTOXX...")
    vix, vstoxx = fetch_vix()
    print(f"  VIX={vix}  VSTOXX={vstoxx}")
    regime = get_regime_vix(vix, vstoxx)
    print(f"  Regime: {regime['regime']} (mult={regime['mult']})")

    # 2. Fetch ticker
    results = []; errors = 0
    for i, info in enumerate(TICKERS):
        r = process_leva(info, regime['mult'])
        if r: results.append(r)
        else: errors += 1
        if (i+1) % 20 == 0:
            print(f"  {i+1}/{len(TICKERS)} — ok:{len(results)} err:{errors}")
        time.sleep(0.3)

    # 3. Salva
    output = {
        'timestamp':    now.isoformat(),
        'timestamp_it': now.strftime('%d/%m/%Y %H:%M'),
        'total':   len(TICKERS),
        'ok':      len(results),
        'errors':  errors,
        'vix':     vix,
        'vstoxx':  vstoxx,
        'regime':  regime['regime'],
        'regime_mult': regime['mult'],
        'regime_color': regime['color'],
        'data':    results
    }

    with open('raptor_leva.json','w',encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, separators=(',',':'))

    print(f"\nSalvato raptor_leva.json — {len(results)} OK, {errors} errori")
    print(f"Regime: {regime['regime']} | VIX:{vix} VSTOXX:{vstoxx}")

if __name__ == '__main__':
    main()
