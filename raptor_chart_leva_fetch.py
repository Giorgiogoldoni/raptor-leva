#!/usr/bin/env python3
"""
RAPTOR Chart Leva Fetch — GitHub Actions
Scarica 3 mesi OHLCV daily per tutti i 537 ticker leva
Gira 2 volte al giorno: 08:00 UTC (10:00 IT) e 14:00 UTC (16:00 IT)
Salva raptor_chart_leva.json
"""

import json, time, datetime
import yfinance as yf

# ═══════════════════════════════════════════════════════
# TICKER LEVA (537)
# ═══════════════════════════════════════════════════════
TICKERS = [{"t":"MIB5","y":"MIB5.MI","provider":"Leverage Shares"},{"t":"MIBS","y":"MIBS.MI","provider":"Leverage Shares"},{"t":"5QQQ","y":"5QQQ.MI","provider":"Leverage Shares"},{"t":"SQQQ","y":"SQQQ.MI","provider":"Leverage Shares"},{"t":"5SPY","y":"5SPY.MI","provider":"Leverage Shares"},{"t":"SSPY","y":"SSPY.MI","provider":"Leverage Shares"},{"t":"FAAN","y":"FAAN.MI","provider":"Leverage Shares"},{"t":"MAGS","y":"MAGS.MI","provider":"Leverage Shares"},{"t":"GPT3","y":"GPT3.MI","provider":"Leverage Shares"},{"t":"GPTS","y":"GPTS.MI","provider":"Leverage Shares"},{"t":"SMCI","y":"SMCI.MI","provider":"Leverage Shares"},{"t":"BRENT","y":"BRENT.MI","provider":"Leverage Shares"},{"t":"WTI","y":"WTI.MI","provider":"Leverage Shares"},{"t":"GAS","y":"GAS.MI","provider":"Leverage Shares"},{"t":"CPER","y":"CPER.MI","provider":"Leverage Shares"},{"t":"SOXL","y":"SOXL.MI","provider":"Leverage Shares"},{"t":"SOXS","y":"SOXS.MI","provider":"Leverage Shares"},{"t":"3AMZ","y":"3AMZ.MI","provider":"Leverage Shares"},{"t":"3AAP","y":"3AAP.MI","provider":"Leverage Shares"},{"t":"3MSF","y":"3MSF.MI","provider":"Leverage Shares"},{"t":"3GOO","y":"3GOO.MI","provider":"Leverage Shares"},{"t":"3FB","y":"3FB.MI","provider":"Leverage Shares"},{"t":"3AMD","y":"3AMD.MI","provider":"Leverage Shares"},{"t":"3BAB","y":"3BAB.MI","provider":"Leverage Shares"},{"t":"3UBR","y":"3UBR.MI","provider":"Leverage Shares"},{"t":"3CON","y":"3CON.MI","provider":"Leverage Shares"},{"t":"3RAC","y":"3RAC.MI","provider":"Leverage Shares"},{"t":"3SRA","y":"3SRA.MI","provider":"Leverage Shares"},{"t":"3PLT","y":"3PLT.MI","provider":"Leverage Shares"},{"t":"3PYP","y":"3PYP.MI","provider":"Leverage Shares"},{"t":"3SQ","y":"3SQ.MI","provider":"Leverage Shares"},{"t":"3NFL","y":"3NFL.MI","provider":"Leverage Shares"},{"t":"ARM3","y":"ARM3.MI","provider":"Leverage Shares"},{"t":"3TSL","y":"3TSL.MI","provider":"Leverage Shares"},{"t":"3BID","y":"3BID.MI","provider":"Leverage Shares"},{"t":"3NVD","y":"3NVD.MI","provider":"Leverage Shares"},{"t":"3MST","y":"3MST.MI","provider":"Leverage Shares"},{"t":"SNV3","y":"SNV3.MI","provider":"Leverage Shares"},{"t":"SMST","y":"SMST.MI","provider":"Leverage Shares"},{"t":"3NIO","y":"3NIO.MI","provider":"Leverage Shares"},{"t":"3MRN","y":"3MRN.MI","provider":"Leverage Shares"},{"t":"SBA3","y":"SBA3.MI","provider":"Leverage Shares"},{"t":"LLY3","y":"LLY3.MI","provider":"Leverage Shares"},{"t":"LLYS","y":"LLYS.MI","provider":"Leverage Shares"},{"t":"INT3","y":"INT3.MI","provider":"Leverage Shares"},{"t":"INTS","y":"INTS.MI","provider":"Leverage Shares"},{"t":"AVG3","y":"AVG3.MI","provider":"Leverage Shares"},{"t":"AVOS","y":"AVOS.MI","provider":"Leverage Shares"},{"t":"HOD3","y":"HOD3.MI","provider":"Leverage Shares"},{"t":"ASL3","y":"ASL3.MI","provider":"Leverage Shares"},{"t":"ASMS","y":"ASMS.MI","provider":"Leverage Shares"},{"t":"HIM3","y":"HIM3.MI","provider":"Leverage Shares"},{"t":"UNH3","y":"UNH3.MI","provider":"Leverage Shares"},{"t":"RHM3","y":"RHM3.MI","provider":"Leverage Shares"},{"t":"FUT3","y":"FUT3.MI","provider":"Leverage Shares"},{"t":"S3CO","y":"S3CO.MI","provider":"Leverage Shares"},{"t":"TSLQ","y":"TSLQ.MI","provider":"Leverage Shares"},{"t":"HSC3L","y":"HSC3L.MI","provider":"SG"},{"t":"HSC3S","y":"HSC3S.MI","provider":"SG"},{"t":"ERIX","y":"ERIX.MI","provider":"SG"},{"t":"SX5E3S","y":"SX5E3S.MI","provider":"SG"},{"t":"SX5E3L","y":"SX5E3L.MI","provider":"SG"},{"t":"DAX3L","y":"DAX3L.MI","provider":"SG"},{"t":"DAX3S","y":"DAX3S.MI","provider":"SG"},{"t":"MIB3L","y":"MIB3L.MI","provider":"SG"},{"t":"MIBESG","y":"MIBESG.MI","provider":"SG"},{"t":"MIB3S","y":"MIB3S.MI","provider":"SG"},{"t":"NDQ3L","y":"NDQ3L.MI","provider":"SG"},{"t":"SPX3S","y":"SPX3S.MI","provider":"SG"},{"t":"NDQ3S","y":"NDQ3S.MI","provider":"SG"},{"t":"SPX3L","y":"SPX3L.MI","provider":"SG"},{"t":"DAX2S","y":"DAX2S.MI","provider":"SG"},{"t":"5MIB","y":"5MIB.MI","provider":"GraniteShares"},{"t":"5SIT","y":"5SIT.MI","provider":"GraniteShares"},{"t":"FANG","y":"FANG.MI","provider":"GraniteShares"},{"t":"SFNG","y":"SFNG.MI","provider":"GraniteShares"},{"t":"3FNG","y":"3FNG.MI","provider":"GraniteShares"},{"t":"3LPO","y":"3LPO.MI","provider":"GraniteShares"},{"t":"3LCR","y":"3LCR.MI","provider":"GraniteShares"},{"t":"3LSP","y":"3LSP.MI","provider":"GraniteShares"},{"t":"3LCO","y":"3LCO.MI","provider":"GraniteShares"},{"t":"3LSQ","y":"3LSQ.MI","provider":"GraniteShares"},{"t":"3LPP","y":"3LPP.MI","provider":"GraniteShares"},{"t":"3LMI","y":"3LMI.MI","provider":"GraniteShares"},{"t":"3LFB","y":"3LFB.MI","provider":"GraniteShares"},{"t":"3LTS","y":"3LTS.MI","provider":"GraniteShares"},{"t":"3LMS","y":"3LMS.MI","provider":"GraniteShares"},{"t":"3LUB","y":"3LUB.MI","provider":"GraniteShares"},{"t":"3SAP","y":"3SAP.MI","provider":"GraniteShares"},{"t":"3SAL","y":"3SAL.MI","provider":"GraniteShares"},{"t":"3SFB","y":"3SFB.MI","provider":"GraniteShares"},{"t":"3SZN","y":"3SZN.MI","provider":"GraniteShares"},{"t":"3LZN","y":"3LZN.MI","provider":"GraniteShares"},{"t":"3LAL","y":"3LAL.MI","provider":"GraniteShares"},{"t":"3SMS","y":"3SMS.MI","provider":"GraniteShares"},{"t":"3LAP","y":"3LAP.MI","provider":"GraniteShares"},{"t":"3LNV","y":"3LNV.MI","provider":"GraniteShares"},{"t":"3SSQ","y":"3SSQ.MI","provider":"GraniteShares"},{"t":"3SMO","y":"3SMO.MI","provider":"GraniteShares"},{"t":"3LAA","y":"3LAA.MI","provider":"GraniteShares"},{"t":"3SNV","y":"3SNV.MI","provider":"GraniteShares"},{"t":"3SAA","y":"3SAA.MI","provider":"GraniteShares"},{"t":"3SCR","y":"3SCR.MI","provider":"GraniteShares"},{"t":"3SSP","y":"3SSP.MI","provider":"GraniteShares"},{"t":"3LPA","y":"3LPA.MI","provider":"GraniteShares"},{"t":"3LNF","y":"3LNF.MI","provider":"GraniteShares"},{"t":"3SMI","y":"3SMI.MI","provider":"GraniteShares"},{"t":"3SPA","y":"3SPA.MI","provider":"GraniteShares"},{"t":"3LMO","y":"3LMO.MI","provider":"GraniteShares"},{"t":"3SNI","y":"3SNI.MI","provider":"GraniteShares"},{"t":"3LNI","y":"3LNI.MI","provider":"GraniteShares"},{"t":"3STS","y":"3STS.MI","provider":"GraniteShares"},{"t":"3LAM","y":"3LAM.MI","provider":"GraniteShares"},{"t":"3SNF","y":"3SNF.MI","provider":"GraniteShares"},{"t":"XSD2","y":"XSD2.MI","provider":"Xtrackers"},{"t":"XSDX","y":"XSDX.MI","provider":"Xtrackers"},{"t":"XS2L","y":"XS2L.MI","provider":"Xtrackers"},{"t":"XLDX","y":"XLDX.MI","provider":"Xtrackers"},{"t":"XSSX","y":"XSSX.MI","provider":"Xtrackers"},{"t":"LQQ","y":"LQQ.MI","provider":"Xtrackers"},{"t":"CL2","y":"CL2.MI","provider":"Xtrackers"},{"t":"DAXLEV","y":"DAXLEV.MI","provider":"Xtrackers"},{"t":"LEVMIB","y":"LEVMIB.MI","provider":"Xtrackers"},{"t":"DJLEV","y":"DJLEV.MI","provider":"Xtrackers"},{"t":"BXX","y":"BXX.MI","provider":"Xtrackers"},{"t":"5ITL","y":"5ITL.MI","provider":"WisdomTree"},{"t":"3DEL","y":"3DEL.MI","provider":"WisdomTree"},{"t":"QQQ3","y":"QQQ3.MI","provider":"WisdomTree"},{"t":"QS5L","y":"QS5L.MI","provider":"WisdomTree"},{"t":"3ITL","y":"3ITL.MI","provider":"WisdomTree"},{"t":"3EUL","y":"3EUL.MI","provider":"WisdomTree"},{"t":"3USL","y":"3USL.MI","provider":"WisdomTree"},{"t":"3USS","y":"3USS.MI","provider":"WisdomTree"},{"t":"3EUS","y":"3EUS.MI","provider":"WisdomTree"},{"t":"3GOL","y":"3GOL.MI","provider":"WisdomTree"},{"t":"3GOS","y":"3GOS.MI","provider":"WisdomTree"},{"t":"3SIL","y":"3SIL.MI","provider":"WisdomTree"},{"t":"3SIS","y":"3SIS.MI","provider":"WisdomTree"},{"t":"3OIL","y":"3OIL.MI","provider":"WisdomTree"},{"t":"3OIS","y":"3OIS.MI","provider":"WisdomTree"},{"t":"3BRL","y":"3BRL.MI","provider":"WisdomTree"},{"t":"3BRS","y":"3BRS.MI","provider":"WisdomTree"},{"t":"3TYL","y":"3TYL.MI","provider":"WisdomTree"},{"t":"3TYS","y":"3TYS.MI","provider":"WisdomTree"},{"t":"3MG7","y":"3MG7.MI","provider":"WisdomTree"},{"t":"3M7S","y":"3M7S.MI","provider":"WisdomTree"},{"t":"3DES","y":"3DES.MI","provider":"WisdomTree"},{"t":"3ITL","y":"3ITL.MI","provider":"WisdomTree"},{"t":"3ITS","y":"3ITS.MI","provider":"WisdomTree"},{"t":"5ITS","y":"5ITS.MI","provider":"WisdomTree"},{"t":"LOIL","y":"LOIL.MI","provider":"WisdomTree"},{"t":"LBUL","y":"LBUL.MI","provider":"WisdomTree"},{"t":"3HCL","y":"3HCL.MI","provider":"WisdomTree"},{"t":"3HCS","y":"3HCS.MI","provider":"WisdomTree"},{"t":"LSIL","y":"LSIL.MI","provider":"WisdomTree"},{"t":"LNGA","y":"LNGA.MI","provider":"WisdomTree"},{"t":"5EUL","y":"5EUL.MI","provider":"WisdomTree"},{"t":"5EUS","y":"5EUS.MI","provider":"WisdomTree"},{"t":"5USL","y":"5USL.MI","provider":"WisdomTree"},{"t":"5USS","y":"5USS.MI","provider":"WisdomTree"},{"t":"QS5S","y":"QS5S.MI","provider":"WisdomTree"},{"t":"3SEM","y":"3SEM.MI","provider":"WisdomTree"},{"t":"SC3S","y":"SC3S.MI","provider":"WisdomTree"},{"t":"3BAL","y":"3BAL.MI","provider":"WisdomTree"},{"t":"3BAS","y":"3BAS.MI","provider":"WisdomTree"},{"t":"3NGL","y":"3NGL.MI","provider":"WisdomTree"},{"t":"3NGS","y":"3NGS.MI","provider":"WisdomTree"},{"t":"3EML","y":"3EML.MI","provider":"WisdomTree"},{"t":"3EMS","y":"3EMS.MI","provider":"WisdomTree"},{"t":"3CFL","y":"3CFL.MI","provider":"WisdomTree"},{"t":"3BUL","y":"3BUL.MI","provider":"WisdomTree"},{"t":"3BUS","y":"3BUS.MI","provider":"WisdomTree"},{"t":"VIXL","y":"VIXL.MI","provider":"WisdomTree"},{"t":"3BTL","y":"3BTL.MI","provider":"WisdomTree"},{"t":"3BTS","y":"3BTS.MI","provider":"WisdomTree"},{"t":"5BTS","y":"5BTS.MI","provider":"WisdomTree"},{"t":"3CAC","y":"3CAC.PA","provider":"WisdomTree"},{"t":"3CAS","y":"3CAS.PA","provider":"WisdomTree"},{"t":"3GOL","y":"3GOL.MI","provider":"WisdomTree"},{"t":"3UKL","y":"3UKL.L","provider":"WisdomTree"},{"t":"3UKS","y":"3UKS.L","provider":"WisdomTree"},{"t":"2UKL","y":"2UKL.L","provider":"WisdomTree"},{"t":"2UKS","y":"2UKS.L","provider":"WisdomTree"}]

# ═══════════════════════════════════════════════════════
# FETCH OHLCV — 3 mesi daily
# ═══════════════════════════════════════════════════════
def fetch_ticker(symbol):
    try:
        tk = yf.Ticker(symbol)
        hist = tk.history(period='3mo', interval='1d', timeout=15)
        if hist.empty or len(hist) < 10:
            return None
        bars = []
        for ts, row in hist.iterrows():
            bars.append([
                int(ts.timestamp()),
                round(float(row['Open']),  4),
                round(float(row['High']),  4),
                round(float(row['Low']),   4),
                round(float(row['Close']), 4),
                int(row['Volume'])
            ])
        return bars
    except Exception:
        return None

# ═══════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════
def main():
    now = datetime.datetime.now()
    print(f"RAPTOR Chart Leva Fetch — {now.strftime('%Y-%m-%d %H:%M')}")
    print(f"Ticker: {len(TICKERS)}")

    data = {}
    ok = 0; errors = 0

    # Deduplica per symbol Yahoo
    seen = set()
    unique = []
    for t in TICKERS:
        if t['y'] not in seen:
            seen.add(t['y'])
            unique.append(t)

    print(f"Ticker unici: {len(unique)}")

    for i, info in enumerate(unique):
        bars = fetch_ticker(info['y'])
        if bars:
            data[info['y']] = bars
            ok += 1
        else:
            errors += 1
        if (i+1) % 30 == 0:
            print(f"  {i+1}/{len(unique)} — ok:{ok} err:{errors}")
        time.sleep(0.35)

    output = {
        'timestamp':    now.isoformat(),
        'timestamp_it': now.strftime('%d/%m/%Y %H:%M'),
        'total':   len(unique),
        'ok':      ok,
        'errors':  errors,
        'data':    data
    }

    with open('raptor_chart_leva.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, separators=(',', ':'))

    print(f"\nSalvato raptor_chart_leva.json — {ok} OK, {errors} errori")

if __name__ == '__main__':
    main()
