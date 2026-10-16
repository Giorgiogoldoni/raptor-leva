# RAPTOR Leva

Sistema automatico di screening e alert per **ETF a leva** (WisdomTree, GraniteShares, Leverage Shares) con leva 1x–5x.

Gira su GitHub Actions ogni 30 minuti (lun-ven 8:00–20:30 ora italiana), scarica dati da Yahoo Finance, calcola indicatori tecnici, genera segnali e invia email di alert.

🔗 **Dashboard live:** https://giorgiogoldoni.github.io/raptor-leva/

---

## 📐 Come funziona

### Indicatori utilizzati

| Indicatore | Parametri | Scopo |
|------------|-----------|-------|
| **KAMA fast** | `n=5, fast=3, slow=20` | Entrata |
| **KAMA slow** | `n=20, fast=2, slow=40` | Uscita |
| **Awesome Oscillator** | `EMA3 - EMA13` midpoint | Conferma momentum |
| **Parabolic SAR** | `step=0.03, max_af=0.25` | Filtro trend + Super Best Buy |
| **RSI** | `14` e `5` | Rilevamento cross rialzisti |
| **Volume ratio** | `vol[-1] / media(vol[-21:-1])` | Conferma liquidità |
| **Baffetti** | barre consecutive crescenti | Monotonia del trend |
| **Efficiency Ratio** | `direction / volatility` (10 barre) | Qualità del trend |

### Zone operative (doppia KAMA)

- **LONG_CONF** — `prezzo > KAMA_fast > KAMA_slow` → entrata confermata
- **LONG_EARLY** — `prezzo > KAMA_fast` e `prezzo > KAMA_slow` → entrata anticipata
- **GRIGIA** — `KAMA_slow < prezzo < KAMA_fast` → ambigua
- **USCITA** — `prezzo < KAMA_slow` con gap ≤ 2%
- **STOP** — `prezzo < KAMA_slow` con gap > 2%

### Filtri di qualità

```python
VOL_MIN_CONF   = 2.0    # volume ratio minimo per LONG_CONF
VOL_MIN_EARLY  = 1.5    # volume ratio minimo per LONG_EARLY
BAF_MIN_CONF   = 3      # baffetti minimi
ER_MIN         = 0.35   # efficiency ratio minimo
KAMA_GAP_MIN   = 0.003  # gap minimo tra KAMA fast/slow
SCORE_MIN      = 65     # score minimo per alert
