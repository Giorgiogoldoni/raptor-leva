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
TICKERS = [{"t":"MIB5","y":"MIB5.MI","n":"Leverage Shares 5x Long Ftse Mib Etp","c":"Azioni Italia","provider":"Leverage Shares"},{"t":"MIBS","y":"MIBS.MI","n":"Leverage Shares -5x Short Ftse Mib Etp","c":"Azioni Italia","provider":"Leverage Shares"},{"t":"5QQQ","y":"5QQQ.MI","n":"Leverage Shares 5x Long Nasdaq 100 Etp","c":"Azioni Stati Uniti","provider":"Leverage Shares"},{"t":"SQQQ","y":"SQQQ.MI","n":"Leverage Shares -5x Short Nasdaq 100 Etp","c":"Azioni Stati Uniti","provider":"Leverage Shares"},{"t":"5SPY","y":"5SPY.MI","n":"Leverage Shares 5x Long S&P 500 Etp","c":"Azioni Stati Uniti","provider":"Leverage Shares"},{"t":"SSPY","y":"SSPY.MI","n":"Leverage Shares -5x Short S&P 500 Etp","c":"Azioni Stati Uniti","provider":"Leverage Shares"},{"t":"FAAN","y":"FAAN.MI","n":"Leverage Shares Faang+ Etp","c":"Azioni Stati Uniti","provider":"Leverage Shares"},{"t":"2007-05-01 00:00:00","y":"2007-05-01 00:00:00.MI","n":"Leverage Shares 5x Long Magnificent 7 Etp","c":"Azioni Stati Uniti","provider":"Leverage Shares"},{"t":"MAGS","y":"MAGS.MI","n":"Leverage Shares -3x Short Magnificent 7 Etp","c":"Azioni Stati Uniti","provider":"Leverage Shares"},{"t":"GPT3","y":"GPT3.MI","n":"Leverage Shares 3x Long Artificial Intelligence (AI) Etp","c":"Azioni Stati Uniti","provider":"Leverage Shares"},{"t":"GPTS","y":"GPTS.MI","n":"Leverage Shares -3x Short Artificial Intelligence (AI) Etp","c":"Azioni Stati Uniti","provider":"Leverage Shares"},{"t":"SMCI","y":"SMCI.MI","n":"Leverage Shares 2x Super Micro Computer Etp","c":"Azioni Stati Uniti","provider":"Leverage Shares"},{"t":"BRENT","y":"BRENT.MI","n":"Leverage Shares Brent Oil Etc","c":"Energia","provider":"Leverage Shares"},{"t":"WTI","y":"WTI.MI","n":"Leverage Shares Wti Oil Etc","c":"Energia","provider":"Leverage Shares"},{"t":"GAS","y":"GAS.MI","n":"Leverage Shares Natural Gas Etc","c":"Energia","provider":"Leverage Shares"},{"t":"CPER","y":"CPER.MI","n":"Leverage Shares Copper Etc","c":"Metalli industriali","provider":"Leverage Shares"},{"t":"SOXL","y":"SOXL.MI","n":"Leverage Shares 4x Long Semiconductors Etp","c":"Paniere di azioni","provider":"Leverage Shares"},{"t":"SOXS","y":"SOXS.MI","n":"Leverage Shares -4x Short Semiconductors Etp","c":"Paniere di azioni","provider":"Leverage Shares"},{"t":"3AMZ","y":"3AMZ.MI","n":"Leverage Shares 3x Amazon Etp Securities","c":"Singole azioni","provider":"Leverage Shares"},{"t":"3AAP","y":"3AAP.MI","n":"Leverage Shares 3x Apple Etp Securities","c":"Singole azioni","provider":"Leverage Shares"},{"t":"3MSF","y":"3MSF.MI","n":"Leverage Shares 3x Microsoft Etp Securities","c":"Singole azioni","provider":"Leverage Shares"},{"t":"3GOO","y":"3GOO.MI","n":"Leverage Shares 3x Alphabet Etp Securities","c":"Singole azioni","provider":"Leverage Shares"},{"t":"3FB","y":"3FB.MI","n":"Leverage Shares 3x Facebook Etp Securities","c":"Singole azioni","provider":"Leverage Shares"},{"t":"3AMD","y":"3AMD.MI","n":"Leverage Shares 3x AMD Etp Securities","c":"Singole azioni","provider":"Leverage Shares"},{"t":"3BAB","y":"3BAB.MI","n":"Leverage Shares 3x Alibaba Etp Securities","c":"Singole azioni","provider":"Leverage Shares"},{"t":"3UBR","y":"3UBR.MI","n":"Leverage Shares 3x Uber Etp Securities","c":"Singole azioni","provider":"Leverage Shares"},{"t":"3CON","y":"3CON.MI","n":"Leverage Shares 3x Long Coinbase Etp Securities","c":"Singole azioni","provider":"Leverage Shares"},{"t":"3RAC","y":"3RAC.MI","n":"Leverage Shares 3x Long Ferrari (RACE) Etp","c":"Singole azioni","provider":"Leverage Shares"},{"t":"3SRA","y":"3SRA.MI","n":"Leverage Shares 3x Short Ferrari (RACE) Etp","c":"Singole azioni","provider":"Leverage Shares"},{"t":"3PLT","y":"3PLT.MI","n":"Leverage Shares 3x Palantir Etp Securities","c":"Singole azioni","provider":"Leverage Shares"},{"t":"3PYP","y":"3PYP.MI","n":"Leverage Shares 3x PayPal Etp Securities","c":"Singole azioni","provider":"Leverage Shares"},{"t":"3SQ","y":"3SQ.MI","n":"Leverage Shares 3x Square Etp Securities","c":"Singole azioni","provider":"Leverage Shares"},{"t":"3NFL","y":"3NFL.MI","n":"Leverage Shares 3x Netflix Etp Securities","c":"Singole azioni","provider":"Leverage Shares"},{"t":"ARM3","y":"ARM3.MI","n":"Leverage Shares 3x Arm Etp Securities","c":"Singole azioni","provider":"Leverage Shares"},{"t":"3TSL","y":"3TSL.MI","n":"Leverage Shares 3x Tesla Etp","c":"Singole azioni","provider":"Leverage Shares"},{"t":"3BID","y":"3BID.MI","n":"Leverage Shares 3x Baidu Etp","c":"Singole azioni","provider":"Leverage Shares"},{"t":"3NVD","y":"3NVD.MI","n":"Leverage Shares 3x NVIDIA Etp Securities","c":"Singole azioni","provider":"Leverage Shares"},{"t":"3MST","y":"3MST.MI","n":"Leverage Shares 3x Long MicroStrategy Etp","c":"Singole azioni","provider":"Leverage Shares"},{"t":"SNV3","y":"SNV3.MI","n":"Leverage Shares -3x Short NVIDIA Etp Securities","c":"Singole azioni","provider":"Leverage Shares"},{"t":"SMST","y":"SMST.MI","n":"Leverage Shares -3x Short MicroStrategy Etp","c":"Singole azioni","provider":"Leverage Shares"},{"t":"3NIO","y":"3NIO.MI","n":"Leverage Shares 3x NIO Etp Securities","c":"Singole azioni","provider":"Leverage Shares"},{"t":"3MRN","y":"3MRN.MI","n":"Leverage Shares 3x Long Moderna Etp Securities","c":"Singole azioni","provider":"Leverage Shares"},{"t":"SBA3","y":"SBA3.MI","n":"Leverage Shares -3x Short Alibaba Etp Securities","c":"Singole azioni","provider":"Leverage Shares"},{"t":"LLY3","y":"LLY3.MI","n":"Leverage Shares 3x Long Eli Lilly (Lly) Etp Securities","c":"Singole azioni","provider":"Leverage Shares"},{"t":"LLYS","y":"LLYS.MI","n":"Leverage Shares -3x Short Eli Lilly (Lly) Etp Securities","c":"Singole azioni","provider":"Leverage Shares"},{"t":"INT3","y":"INT3.MI","n":"Leverage Shares 3x Long Intel (Intc) Etp Securities","c":"Singole azioni","provider":"Leverage Shares"},{"t":"INTS","y":"INTS.MI","n":"Leverage Shares -3x Short Intel (Intc) Etp Securities","c":"Singole azioni","provider":"Leverage Shares"},{"t":"AVG3","y":"AVG3.MI","n":"Leverage Shares 3x Long Broadcom (Avgo) Etp Securities","c":"Singole azioni","provider":"Leverage Shares"},{"t":"AVOS","y":"AVOS.MI","n":"Leverage Shares -3x Short Broadcom (Avgo) Etp Securities","c":"Singole azioni","provider":"Leverage Shares"},{"t":"HOD3","y":"HOD3.MI","n":"Leverage Shares 3x Long Robinhood (Hood) Etp Securities","c":"Singole azioni","provider":"Leverage Shares"},{"t":"ASL3","y":"ASL3.MI","n":"Leverage Shares 3x Long Asml Etp Securities","c":"Singole azioni","provider":"Leverage Shares"},{"t":"ASMS","y":"ASMS.MI","n":"Leverage Shares -3x Short Asml Etp Securities","c":"Singole azioni","provider":"Leverage Shares"},{"t":"HIM3","y":"HIM3.MI","n":"Leverage Shares 3x Long Hims & Hers Health Etp","c":"Singole azioni","provider":"Leverage Shares"},{"t":"UNH3","y":"UNH3.MI","n":"Leverage Shares 3x Long Unitedhealth (Unh) Etp Securities","c":"Singole azioni","provider":"Leverage Shares"},{"t":"RHM3","y":"RHM3.MI","n":"Leverage Shares 3x Long Rheinmetall (Rhm) Etp Securities","c":"Singole azioni","provider":"Leverage Shares"},{"t":"FUT3","y":"FUT3.MI","n":"Leverage Shares 3x Long Futu Etp Securities","c":"Singole azioni","provider":"Leverage Shares"},{"t":"S3CO","y":"S3CO.MI","n":"Leverage Shares -3x Short Coinbase Etp","c":"Singole azioni","provider":"Leverage Shares"},{"t":"TSLQ","y":"TSLQ.MI","n":"Leverage Shares -3x Short Tesla Etp Securities","c":"Singole azioni","provider":"Leverage Shares"},{"t":"HSC3L","y":"HSC3L.MI","n":"Sg Etn Daily Long 3x Hang Seng China Enterprises","c":"Azioni Cina (Hong Kong)","provider":"SG"},{"t":"HSC3S","y":"HSC3S.MI","n":"Sg Etn Daily Short -3x Hang Seng China Enterprises","c":"Azioni Cina (Hong Kong)","provider":"SG"},{"t":"ERIX","y":"ERIX.MI","n":"Sg Etn European Renewable Energy","c":"Azioni Europa","provider":"SG"},{"t":"SX5E3S","y":"SX5E3S.MI","n":"Sg Etc Euro Stoxx 50 -3x Daily Short Collateral","c":"Azioni Eurozona","provider":"SG"},{"t":"SX5E3L","y":"SX5E3L.MI","n":"Sg Etc Euro Stoxx 50 +3x Daily Leverage Collateral","c":"Azioni Eurozona","provider":"SG"},{"t":"DAX3L","y":"DAX3L.MI","n":"Sg Etc Dax +3x Daily Leverage Collateral","c":"Azioni Germania","provider":"SG"},{"t":"DAX3S","y":"DAX3S.MI","n":"Sg Etc Dax -3x Daily Short Collateral","c":"Azioni Germania","provider":"SG"},{"t":"MIB3L","y":"MIB3L.MI","n":"Sg Etc Ftse Mib +3x Daily Leverage Collateral","c":"Azioni Italia","provider":"SG"},{"t":"MIBESG","y":"MIBESG.MI","n":"Sg Etn Mib Esg","c":"Azioni Italia","provider":"SG"},{"t":"MIB3S","y":"MIB3S.MI","n":"Sg Etc Ftse Mib -3x Daily Short Collateral","c":"Azioni Italia","provider":"SG"},{"t":"H1DRO","y":"H1DRO.MI","n":"Sg Etn World Hydrogen","c":"Azioni mondo","provider":"SG"},{"t":"METAV","y":"METAV.MI","n":"Sg Etn Metaverse","c":"Azioni mondo","provider":"SG"},{"t":"URAM","y":"URAM.MI","n":"Sg Etn Uranium Mining","c":"Azioni mondo","provider":"SG"},{"t":"INFLA","y":"INFLA.MI","n":"Sg Etn Inflation Proxy","c":"Azioni mondo sviluppato","provider":"SG"},{"t":"ECARS","y":"ECARS.MI","n":"Sg Etn Smart Mobility","c":"Azioni mondo sviluppato","provider":"SG"},{"t":"NDQ3L","y":"NDQ3L.MI","n":"Sg Etn Daily Long +3X Nasdaq 100","c":"Azioni Stati Uniti","provider":"SG"},{"t":"SPX3S","y":"SPX3S.MI","n":"Sg Etn Daily Short -3X S&P 500","c":"Azioni Stati Uniti","provider":"SG"},{"t":"NDQ3S","y":"NDQ3S.MI","n":"Sg Etn Daily Short -3X Nasdaq 100","c":"Azioni Stati Uniti","provider":"SG"},{"t":"SPX3L","y":"SPX3L.MI","n":"Sg Etn Daily Long +3X S&P 500","c":"Azioni Stati Uniti","provider":"SG"},{"t":"CO2L1","y":"CO2L1.MI","n":"Sg Etn Carbon Future","c":"Diritti di emissione di CO2","provider":"SG"},{"t":"NGA3L","y":"NGA3L.MI","n":"Sg Etc Daily Long +3x Natural Gas Future","c":"Energia","provider":"SG"},{"t":"NGA1L","y":"NGA1L.MI","n":"Sg Etc Natural Gas Future","c":"Energia","provider":"SG"},{"t":"NGA3S","y":"NGA3S.MI","n":"Sg Etc Daily Short -3x Natural Gas Future","c":"Energia","provider":"SG"},{"t":"GAS1S","y":"GAS1S.MI","n":"Sg Etc Daily Short -1x Natural Gas Future","c":"Energia","provider":"SG"},{"t":"WTI2L","y":"WTI2L.MI","n":"Sg Etc Daily Long +2x Wti Oil Future","c":"Energia","provider":"SG"},{"t":"WTI2S","y":"WTI2S.MI","n":"Sg Etc Daily Short -2x Wti Oil Future","c":"Energia","provider":"SG"},{"t":"BRE2S","y":"BRE2S.MI","n":"Sg Etc Daily Short -2X Brent Oil Future","c":"Energia","provider":"SG"},{"t":"BRE1L","y":"BRE1L.MI","n":"Sg Etc Brent Oil Future","c":"Energia","provider":"SG"},{"t":"WTIS1","y":"WTIS1.MI","n":"Sg Etc Daily Short -1X Wti Oil Future","c":"Energia","provider":"SG"},{"t":"BRE3S","y":"BRE3S.MI","n":"Sg Etc Daily Long -3X Brent Oil Future","c":"Energia","provider":"SG"},{"t":"BRE3L","y":"BRE3L.MI","n":"Sg Etc Daily Long +3X Brent Oil Future","c":"Energia","provider":"SG"},{"t":"BRE2L","y":"BRE2L.MI","n":"Sg Etc Daily Long +2X Brent Oil Future","c":"Energia","provider":"SG"},{"t":"WTI1L","y":"WTI1L.MI","n":"Sg Etc Wti Oil Future","c":"Energia","provider":"SG"},{"t":"NGA2L","y":"NGA2L.MI","n":"Sg Etc Daily Long +2x Natural Gas Future","c":"Energia","provider":"SG"},{"t":"GAS2S","y":"GAS2S.MI","n":"Sg Etc Daily Short -2x Natural Gas Future","c":"Energia","provider":"SG"},{"t":"BRES1","y":"BRES1.MI","n":"Sg Etc Daily Short -1X Brent Oil Future","c":"Energia","provider":"SG"},{"t":"WTI3S","y":"WTI3S.MI","n":"Sg Etc Daily Long -3X Wti Oil Future","c":"Energia","provider":"SG"},{"t":"WTI3L","y":"WTI3L.MI","n":"Sg Etc Daily Long +3X Wti Oil Future","c":"Energia","provider":"SG"},{"t":"RAM3S","y":"RAM3S.MI","n":"Sg Etc Daily Long -3X Copper Future","c":"Metalli industriali","provider":"SG"},{"t":"RAM3L","y":"RAM3L.MI","n":"Sg Etc Daily Long +3X Copper Future","c":"Metalli industriali","provider":"SG"},{"t":"GOL3S","y":"GOL3S.MI","n":"Sg Etc Daily Long -3X Gold Future","c":"Metalli preziosi","provider":"SG"},{"t":"GOL1S","y":"GOL1S.MI","n":"Sg Etc Daily Short -1X Gold Future","c":"Metalli preziosi","provider":"SG"},{"t":"SIL1S","y":"SIL1S.MI","n":"Sg Etc Daily Short -1X Silver Future","c":"Metalli preziosi","provider":"SG"},{"t":"GOL3L","y":"GOL3L.MI","n":"Sg Etc Daily Long +3X Gold Future","c":"Metalli preziosi","provider":"SG"},{"t":"GOL1L","y":"GOL1L.MI","n":"Sg Etc Gold Future","c":"Metalli preziosi","provider":"SG"},{"t":"SIL3S","y":"SIL3S.MI","n":"Sg Etc Daily Long -3X Silver Future","c":"Metalli preziosi","provider":"SG"},{"t":"SIL3L","y":"SIL3L.MI","n":"Sg Etc Daily Long +3X Silver Future","c":"Metalli preziosi","provider":"SG"},{"t":"BTPS5","y":"BTPS5.MI","n":"Sg Etn Daily Short -5X BTp Future","c":"Obbligazioni governative italiane","provider":"SG"},{"t":"BTPS1","y":"BTPS1.MI","n":"Sg Etn Daily Short -1X BTp Future","c":"Obbligazioni governative italiane","provider":"SG"},{"t":"BTPL5","y":"BTPL5.MI","n":"Sg Etn Daily Long 5X BTp Future","c":"Obbligazioni governative italiane","provider":"SG"},{"t":"OATS5","y":"OATS5.MI","n":"Sg Etn Daily Short -5x Oat Futures","c":"Obbligazioni governative tedesche","provider":"SG"},{"t":"OATL5","y":"OATL5.MI","n":"Sg Etn Daily Long +5x Oat Futures","c":"Obbligazioni governative tedesche","provider":"SG"},{"t":"BUNDS5","y":"BUNDS5.MI","n":"Sg Etn Daily Short -5X Bund Future","c":"Obbligazioni governative tedesche","provider":"SG"},{"t":"BUNDL5","y":"BUNDL5.MI","n":"Sg Etn Daily Long +5x Bund Futures","c":"Obbligazioni governative tedesche","provider":"SG"},{"t":"UST5S","y":"UST5S.MI","n":"Sg Etn Daily Short -5X Us Treasury 10Y Future","c":"Obbligazioni governative U.S.","provider":"SG"},{"t":"UST5L","y":"UST5L.MI","n":"Sg Etn Daily Long +5X Us Treasury 10Y Future","c":"Obbligazioni governative U.S.","provider":"SG"},{"t":"VIX1L","y":"VIX1L.MI","n":"Sg Etn Vix Future","c":"Volatilità","provider":"SG"},{"t":"5MIB","y":"5MIB.MI","n":"GraniteShares 5x Long Mib Daily Etp","c":"Azioni Italia","provider":"GraniteShares"},{"t":"5SIT","y":"5SIT.MI","n":"GraniteShares 5x Short Mib Daily Etp","c":"Azioni Italia","provider":"GraniteShares"},{"t":"FANG","y":"FANG.MI","n":"GraniteShares Faang Etp","c":"Azioni Stati Uniti","provider":"GraniteShares"},{"t":"SFNG","y":"SFNG.MI","n":"GraniteShares 1x Short Faang Etp","c":"Azioni Stati Uniti","provider":"GraniteShares"},{"t":"3FNG","y":"3FNG.MI","n":"GraniteShares 3x Long Faang Etp","c":"Azioni Stati Uniti","provider":"GraniteShares"},{"t":"3LPO","y":"3LPO.MI","n":"GraniteShares 3x Long Spotify Daily Etp","c":"Singole azioni","provider":"GraniteShares"},{"t":"3LCR","y":"3LCR.MI","n":"GraniteShares 3x Long Unicredit Daily Etp","c":"Singole azioni","provider":"GraniteShares"},{"t":"3LSP","y":"3LSP.MI","n":"GraniteShares 3x Long Intesa Sanpaolo Daily Etp","c":"Singole azioni","provider":"GraniteShares"},{"t":"3LCO","y":"3LCO.MI","n":"GraniteShares 3x Long Coinbase Daily Etp","c":"Singole azioni","provider":"GraniteShares"},{"t":"3LSQ","y":"3LSQ.MI","n":"GraniteShares 3x Long Square Daily Etp","c":"Singole azioni","provider":"GraniteShares"},{"t":"3LPP","y":"3LPP.MI","n":"GraniteShares 3x Long PayPal Daily Etp","c":"Singole azioni","provider":"GraniteShares"},{"t":"3LMI","y":"3LMI.MI","n":"GraniteShares 3x Long MicroStrategy Daily Etp","c":"Singole azioni","provider":"GraniteShares"},{"t":"3LFB","y":"3LFB.MI","n":"GraniteShares 3x Long Facebook Daily Etp","c":"Singole azioni","provider":"GraniteShares"},{"t":"3LTS","y":"3LTS.MI","n":"GraniteShares 3x Long Tesla Daily Etp","c":"Singole azioni","provider":"GraniteShares"},{"t":"3LMS","y":"3LMS.MI","n":"GraniteShares 3x Long Microsoft Daily Etp","c":"Singole azioni","provider":"GraniteShares"},{"t":"3LUB","y":"3LUB.MI","n":"GraniteShares 3x Long Uber Daily Etp","c":"Singole azioni","provider":"GraniteShares"},{"t":"3SAP","y":"3SAP.MI","n":"GraniteShares 3x Short Apple Daily Etp","c":"Singole azioni","provider":"GraniteShares"},{"t":"3SAL","y":"3SAL.MI","n":"GraniteShares 3x Short Alphabet Daily Etp","c":"Singole azioni","provider":"GraniteShares"},{"t":"3SFB","y":"3SFB.MI","n":"GraniteShares 3x Short Facebook Daily Etp","c":"Singole azioni","provider":"GraniteShares"},{"t":"3SZN","y":"3SZN.MI","n":"GraniteShares 3x Short Amazon Daily Etp","c":"Singole azioni","provider":"GraniteShares"},{"t":"3LZN","y":"3LZN.MI","n":"GraniteShares 3x Long Amazon Daily Etp","c":"Singole azioni","provider":"GraniteShares"},{"t":"3LAL","y":"3LAL.MI","n":"GraniteShares 3x Long Alphabet Daily Etp","c":"Singole azioni","provider":"GraniteShares"},{"t":"3SMS","y":"3SMS.MI","n":"GraniteShares 3x Short Microsoft Daily Etp","c":"Singole azioni","provider":"GraniteShares"},{"t":"3LAP","y":"3LAP.MI","n":"GraniteShares 3x Long Apple Daily Etp","c":"Singole azioni","provider":"GraniteShares"},{"t":"3LNV","y":"3LNV.MI","n":"GraniteShares 3x Long NVIDIA Daily Etp","c":"Singole azioni","provider":"GraniteShares"},{"t":"3SSQ","y":"3SSQ.MI","n":"GraniteShares 3x Short Square Daily Etp","c":"Singole azioni","provider":"GraniteShares"},{"t":"3SMO","y":"3SMO.MI","n":"GraniteShares 3x Short Moderna Daily Etp","c":"Singole azioni","provider":"GraniteShares"},{"t":"3LAA","y":"3LAA.MI","n":"GraniteShares 3x Long Alibaba Daily Etp","c":"Singole azioni","provider":"GraniteShares"},{"t":"3SNV","y":"3SNV.MI","n":"GraniteShares 3x Short NVIDIA Daily Etp","c":"Singole azioni","provider":"GraniteShares"},{"t":"3SAA","y":"3SAA.MI","n":"GraniteShares 3x Short Alibaba Daily Etp","c":"Singole azioni","provider":"GraniteShares"},{"t":"3SCR","y":"3SCR.MI","n":"GraniteShares 3x Short Unicredit Daily Etp","c":"Singole azioni","provider":"GraniteShares"},{"t":"3SSP","y":"3SSP.MI","n":"GraniteShares 3x Short Intesa Sanpaolo Daily Etp","c":"Singole azioni","provider":"GraniteShares"},{"t":"3LPA","y":"3LPA.MI","n":"GraniteShares 3x Long Palantir Daily Etp","c":"Singole azioni","provider":"GraniteShares"},{"t":"3LNF","y":"3LNF.MI","n":"GraniteShares 3x Long Netflix Daily Etp","c":"Singole azioni","provider":"GraniteShares"},{"t":"3SMI","y":"3SMI.MI","n":"GraniteShares 3x Short MicroStrategy Daily Etp","c":"Singole azioni","provider":"GraniteShares"},{"t":"3SPA","y":"3SPA.MI","n":"GraniteShares 3x Short Palantir Daily Etp","c":"Singole azioni","provider":"GraniteShares"},{"t":"3LMO","y":"3LMO.MI","n":"GraniteShares 3x Long Moderna Daily Etp","c":"Singole azioni","provider":"GraniteShares"},{"t":"3SNI","y":"3SNI.MI","n":"GraniteShares 3x Short NIO Daily Etp","c":"Singole azioni","provider":"GraniteShares"},{"t":"3LNI","y":"3LNI.MI","n":"GraniteShares 3x Long NIO Daily Etp","c":"Singole azioni","provider":"GraniteShares"},{"t":"3STS","y":"3STS.MI","n":"GraniteShares 3x Short Tesla Daily Etp","c":"Singole azioni","provider":"GraniteShares"},{"t":"3LAM","y":"3LAM.MI","n":"GraniteShares 3x Long AMD Daily Etp","c":"Singole azioni","provider":"GraniteShares"},{"t":"3SNF","y":"3SNF.MI","n":"GraniteShares 3x Short Netflix Daily Etp","c":"Singole azioni","provider":"GraniteShares"},{"t":"DEMR","y":"DEMR.MI","n":"WisdomTree Emerging Markets Equity Income UCITS ETF - Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"DHS","y":"DHS.MI","n":"WisdomTree US Equity Income UCITS ETF","c":"WisdomTree","provider":"WisdomTree"},{"t":"DHSF","y":"DHSF.MI","n":"WisdomTree US Equity Income UCITS ETF - EUR Hedged Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"DHSG","y":"DHSG.L","n":"WisdomTree US Equity Income UCITS ETF - GBP Hedged Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"WNER","y":"WNER.MI","n":"WisdomTree New Economy Real Estate UCITS ETF - USD","c":"WisdomTree","provider":"WisdomTree"},{"t":"WBLK","y":"WBLK.MI","n":"WisdomTree Blockchain UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"WRNW","y":"WRNW.MI","n":"WisdomTree Renewable Energy UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"GGRA","y":"GGRA.MI","n":"WisdomTree Global Quality Dividend Growth UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"DGSE","y":"DGSE.MI","n":"WisdomTree Emerging Markets SmallCap Dividend UCITS ETF","c":"WisdomTree","provider":"WisdomTree"},{"t":"WCOM","y":"WCOM.L","n":"WisdomTree Enhanced Commodity UCITS ETF - GBP Hedged Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"EXAG","y":"EXAG.DE","n":"WisdomTree Enhanced Commodity ex-Agriculture UCITS ETF - EUR Hedged Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"PCOM","y":"PCOM.MI","n":"WisdomTree Broad Commodities UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"WSDG","y":"WSDG.MI","n":"WisdomTree Global Sustainable Equity UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"NTSG","y":"NTSG.MI","n":"WisdomTree Global Efficient Core UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"DEM","y":"DEM.MI","n":"WisdomTree Emerging Markets Equity Income UCITS ETF","c":"WisdomTree","provider":"WisdomTree"},{"t":"DHSA","y":"DHSA.MI","n":"WisdomTree US Equity Income UCITS ETF - Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"WCOE","y":"WCOE.MI","n":"WisdomTree Enhanced Commodity UCITS ETF - EUR Hedged Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"WCOG","y":"WCOG.L","n":"WisdomTree Enhanced Commodity UCITS ETF USD","c":"WisdomTree","provider":"WisdomTree"},{"t":"WTAI","y":"WTAI.MI","n":"WisdomTree Artificial Intelligence UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"USFR","y":"USFR.L","n":"WisdomTree USD Floating Rate Treasury Bond UCITS ETF - USD","c":"WisdomTree","provider":"WisdomTree"},{"t":"QGRW","y":"QGRW.MI","n":"WisdomTree US Quality Growth UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"DXJF","y":"DXJF.MI","n":"WisdomTree Japan Equity UCITS ETF - EUR Hedged Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"HEDD","y":"HEDD.SW","n":"WisdomTree Europe Equity UCITS ETF - CHF Hedged Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"WCOA","y":"WCOA.MI","n":"WisdomTree Enhanced Commodity UCITS ETF USD Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"GGRE","y":"GGRE.MI","n":"WisdomTree Global Quality Dividend Growth UCITS ETF - EUR Hedged Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"GGRB","y":"GGRB.L","n":"WisdomTree Global Quality Dividend Growth UCITS ETF - GBP Hedged","c":"WisdomTree","provider":"WisdomTree"},{"t":"DGRB","y":"DGRB.L","n":"WisdomTree US Quality Dividend Growth UCITS ETF - GBP Hedged","c":"WisdomTree","provider":"WisdomTree"},{"t":"NTSX","y":"NTSX.MI","n":"WisdomTree US Efficient Core UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"HEDP","y":"HEDP.L","n":"WisdomTree Europe Equity UCITS ETF - GBP Hedged","c":"WisdomTree","provider":"WisdomTree"},{"t":"EGRP","y":"EGRP.L","n":"WisdomTree Eurozone Quality Dividend Growth UCITS ETF - EUR","c":"WisdomTree","provider":"WisdomTree"},{"t":"EGRW","y":"EGRW.L","n":"WisdomTree Eurozone Quality Dividend Growth UCITS ETF - EUR","c":"WisdomTree","provider":"WisdomTree"},{"t":"UGRW","y":"UGRW.L","n":"WisdomTree UK Quality Dividend Growth UCITS ETF - GBP","c":"WisdomTree","provider":"WisdomTree"},{"t":"WMGT","y":"WMGT.MI","n":"WisdomTree Megatrends UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"RARE","y":"RARE.MI","n":"WisdomTree Strategic Metals and Rare Earths Miners UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"WENG","y":"WENG.L","n":"WisdomTree Strategic Metals UCITS ETF - GBP Hedged Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"COGO","y":"COGO.L","n":"WisdomTree AT1 CoCo Bond UCITS ETF - GBP Hedged","c":"WisdomTree","provider":"WisdomTree"},{"t":"WCLD","y":"WCLD.MI","n":"WisdomTree Cloud Computing UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"WTVG","y":"WTVG.MI","n":"WisdomTree Global Value UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"WTVU","y":"WTVU.MI","n":"WisdomTree US Value UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"WTVE","y":"WTVE.MI","n":"WisdomTree Europe Value UCITS ETF - EUR Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"WENP","y":"WENP.L","n":"WisdomTree Strategic Metals UCITS ETF - GBP Hedged","c":"WisdomTree","provider":"WisdomTree"},{"t":"EPI","y":"EPI.MI","n":"WisdomTree India Earnings UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"CCBO","y":"CCBO.MI","n":"WisdomTree AT1 CoCo Bond UCITS ETF - USD","c":"WisdomTree","provider":"WisdomTree"},{"t":"WTIG","y":"WTIG.DE","n":"WisdomTree AT1 CoCo Bond UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"GGRW","y":"GGRW.MI","n":"WisdomTree Global Quality Dividend Growth UCITS ETF - USD","c":"WisdomTree","provider":"WisdomTree"},{"t":"WEAT","y":"WEAT.MI","n":"WisdomTree Wheat","c":"WisdomTree","provider":"WisdomTree"},{"t":"EHEN","y":"EHEN.DE","n":"WisdomTree Energy - EUR Daily Hedged","c":"WisdomTree","provider":"WisdomTree"},{"t":"5ITL","y":"5ITL.MI","n":"WisdomTree FTSE MIB 5x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree"},{"t":"3DEL","y":"3DEL.MI","n":"WisdomTree DAX 3x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree"},{"t":"WENU","y":"WENU.MI","n":"WisdomTree Strategic Metals UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"NTSZ","y":"NTSZ.MI","n":"WisdomTree Eurozone Efficient Core UCITS ETF - EUR Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"WQTM","y":"WQTM.MI","n":"WisdomTree Quantum Computing UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"XUSA","y":"XUSA.MI","n":"WisdomTree Global Ex-USA Quality Dividend Growth UCITS ETF - EUR Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"EUS5","y":"EUS5.MI","n":"WisdomTree Long USD Short EUR 5x Daily","c":"WisdomTree","provider":"WisdomTree"},{"t":"00XK","y":"00XK.DE","n":"WisdomTree Broad Commodities - EUR Daily Hedged","c":"WisdomTree","provider":"WisdomTree"},{"t":"SJP3","y":"SJP3.L","n":"WisdomTree Short JPY Long USD 3x Daily","c":"WisdomTree","provider":"WisdomTree"},{"t":"AIGE","y":"AIGE.MI","n":"WisdomTree Energy","c":"WisdomTree","provider":"WisdomTree"},{"t":"3EDF","y":"3EDF.MI","n":"WisdomTree STOXX Europe Aerospace & Defence 3x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree"},{"t":"AIGL","y":"AIGL.MI","n":"WisdomTree Livestock","c":"WisdomTree","provider":"WisdomTree"},{"t":"3UKS","y":"3UKS.L","n":"WisdomTree FTSE 100 3x Daily Short","c":"WisdomTree","provider":"WisdomTree"},{"t":"LEAD","y":"LEAD.MI","n":"WisdomTree Lead","c":"WisdomTree","provider":"WisdomTree"},{"t":"EUGB","y":"EUGB.MI","n":"WisdomTree Long GBP Short EUR","c":"WisdomTree","provider":"WisdomTree"},{"t":"ECTN","y":"ECTN.MI","n":"WisdomTree Cotton - EUR Daily Hedged","c":"WisdomTree","provider":"WisdomTree"},{"t":"2UKS","y":"2UKS.L","n":"WisdomTree FTSE 100 2x Daily Short","c":"WisdomTree","provider":"WisdomTree"},{"t":"DGRE","y":"DGRE.MI","n":"WisdomTree US Quality Dividend Growth UCITS ETF - EUR Hedged Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"LSIL","y":"LSIL.MI","n":"WisdomTree Silver 2x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree"},{"t":"3HCS","y":"3HCS.MI","n":"WisdomTree Copper 3x Daily Short","c":"WisdomTree","provider":"WisdomTree"},{"t":"AIGP","y":"AIGP.MI","n":"WisdomTree Precious Metals","c":"WisdomTree","provider":"WisdomTree"},{"t":"COTN","y":"COTN.MI","n":"WisdomTree Cotton","c":"WisdomTree","provider":"WisdomTree"},{"t":"ECOF","y":"ECOF.MI","n":"WisdomTree Coffee - EUR Daily Hedged","c":"WisdomTree","provider":"WisdomTree"},{"t":"3UBS","y":"3UBS.MI","n":"WisdomTree Bund 30Y 3x Daily Short","c":"WisdomTree","provider":"WisdomTree"},{"t":"WS5X","y":"WS5X.MI","n":"WisdomTree EURO STOXX 50","c":"WisdomTree","provider":"WisdomTree"},{"t":"QQQ3","y":"QQQ3.MI","n":"WisdomTree NASDAQ 100 3x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree"},{"t":"WSPX","y":"WSPX.MI","n":"WisdomTree S&P 500","c":"WisdomTree","provider":"WisdomTree"},{"t":"ALTC","y":"ALTC.MI","n":"WisdomTree Physical Crypto Altcoins","c":"WisdomTree","provider":"WisdomTree"},{"t":"COPR","y":"COPR.L","n":"WisdomTree Copper IE","c":"WisdomTree","provider":"WisdomTree"},{"t":"JPE3","y":"JPE3.MI","n":"WisdomTree Short JPY Long EUR 3x Daily","c":"WisdomTree","provider":"WisdomTree"},{"t":"3WHL","y":"3WHL.MI","n":"WisdomTree Wheat 3x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree"},{"t":"QS5L","y":"QS5L.MI","n":"WisdomTree NASDAQ 100 5x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree"},{"t":"LOIL","y":"LOIL.MI","n":"WisdomTree WTI Crude Oil 2x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree"},{"t":"EEI","y":"EEI.MI","n":"WisdomTree Europe Equity Income UCITS ETF","c":"WisdomTree","provider":"WisdomTree"},{"t":"DFE","y":"DFE.MI","n":"WisdomTree Europe SmallCap Dividend UCITS ETF","c":"WisdomTree","provider":"WisdomTree"},{"t":"DFEA","y":"DFEA.MI","n":"WisdomTree Europe SmallCap Dividend UCITS ETF Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"COMS","y":"COMS.SW","n":"WisdomTree Enhanced Commodity UCITS ETF - CHF Hedged Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"3EUS","y":"3EUS.MI","n":"WisdomTree EURO STOXX 50® 3x Daily Short","c":"WisdomTree","provider":"WisdomTree"},{"t":"EUSE","y":"EUSE.MI","n":"WisdomTree Long SEK Short EUR","c":"WisdomTree","provider":"WisdomTree"},{"t":"3CAS","y":"3CAS.PA","n":"WisdomTree CAC 40 3x Daily Short","c":"WisdomTree","provider":"WisdomTree"},{"t":"EEIA","y":"EEIA.MI","n":"WisdomTree Europe Equity Income UCITS ETF Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"DXJ","y":"DXJ.MI","n":"WisdomTree Japan Equity UCITS ETF - USD Hedged","c":"WisdomTree","provider":"WisdomTree"},{"t":"WAXG","y":"WAXG.DE","n":"WisdomTree Enhanced Commodity ex-Agriculture UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"XSOE","y":"XSOE.MI","n":"WisdomTree Emerging Markets ex-State-Owned Enterprises UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"WDNA","y":"WDNA.MI","n":"WisdomTree BioRevolution UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"3GOS","y":"3GOS.MI","n":"WisdomTree Gold 3x Daily Short","c":"WisdomTree","provider":"WisdomTree"},{"t":"SOYO","y":"SOYO.MI","n":"WisdomTree Soybean Oil","c":"WisdomTree","provider":"WisdomTree"},{"t":"URGB","y":"URGB.L","n":"WisdomTree Short EUR Long GBP","c":"WisdomTree","provider":"WisdomTree"},{"t":"GBUS","y":"GBUS.L","n":"WisdomTree Long USD Short GBP","c":"WisdomTree","provider":"WisdomTree"},{"t":"5TYS","y":"5TYS.MI","n":"WisdomTree US Treasuries 10Y 5x Daily Short","c":"WisdomTree","provider":"WisdomTree"},{"t":"SJPY","y":"SJPY.L","n":"WisdomTree Short JPY Long USD","c":"WisdomTree","provider":"WisdomTree"},{"t":"WGLD","y":"WGLD.MI","n":"WisdomTree Core Physical Gold","c":"WisdomTree","provider":"WisdomTree"},{"t":"AIGC","y":"AIGC.MI","n":"WisdomTree Broad Commodities","c":"WisdomTree","provider":"WisdomTree"},{"t":"HOGS","y":"HOGS.MI","n":"WisdomTree Lean Hogs","c":"WisdomTree","provider":"WisdomTree"},{"t":"SC3S","y":"SC3S.MI","n":"WisdomTree PHLX Semiconductor 3x Daily Short","c":"WisdomTree","provider":"WisdomTree"},{"t":"HEDJ","y":"HEDJ.MI","n":"WisdomTree Europe Equity UCITS ETF - USD Hedged","c":"WisdomTree","provider":"WisdomTree"},{"t":"DGRA","y":"DGRA.MI","n":"WisdomTree US Quality Dividend Growth UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"COBO","y":"COBO.MI","n":"WisdomTree AT1 CoCo Bond UCITS ETF - EUR Hedged","c":"WisdomTree","provider":"WisdomTree"},{"t":"TFRN","y":"TFRN.MI","n":"WisdomTree USD Floating Rate Treasury Bond UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"VOLT","y":"VOLT.MI","n":"WisdomTree Battery Solutions UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"WCBR","y":"WCBR.MI","n":"WisdomTree Cybersecurity UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"PHPT","y":"PHPT.MI","n":"WisdomTree Physical Platinum","c":"WisdomTree","provider":"WisdomTree"},{"t":"WNRG","y":"WNRG.DE","n":"WisdomTree Energy Enhanced - EUR Daily Hedged","c":"WisdomTree","provider":"WisdomTree"},{"t":"3EDS","y":"3EDS.MI","n":"WisdomTree STOXX Europe Aerospace & Defence 3x Daily Short","c":"WisdomTree","provider":"WisdomTree"},{"t":"LGBP","y":"LGBP.L","n":"WisdomTree Long GBP Short USD","c":"WisdomTree","provider":"WisdomTree"},{"t":"LCOR","y":"LCOR.MI","n":"WisdomTree Corn 2x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree"},{"t":"9GAF","y":"9GAF.DE","n":"WisdomTree Broad Commodities Longer Dated","c":"WisdomTree","provider":"WisdomTree"},{"t":"3M7S","y":"3M7S.MI","n":"WisdomTree Magnificent 7 3x Daily Short","c":"WisdomTree","provider":"WisdomTree"},{"t":"3DES","y":"3DES.MI","n":"WisdomTree DAX 3x Daily Short","c":"WisdomTree","provider":"WisdomTree"},{"t":"3CFL","y":"3CFL.MI","n":"WisdomTree Coffee 3x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree"},{"t":"DXJD","y":"DXJD.SW","n":"WisdomTree Japan Equity UCITS ETF - CHF Hedged Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"HEDS","y":"HEDS.L","n":"WisdomTree Europe Equity UCITS ETF - USD Hedged Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"HEDK","y":"HEDK.L","n":"WisdomTree Europe Equity UCITS ETF - USD Hedged Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"EGRA","y":"EGRA.MI","n":"WisdomTree Eurozone Quality Dividend Growth UCITS ETF - EUR Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"WTRE","y":"WTRE.MI","n":"WisdomTree New Economy Real Estate UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"PCRD","y":"PCRD.L","n":"WisdomTree WTI Crude Oil - GBP Daily Hedged","c":"WisdomTree","provider":"WisdomTree"},{"t":"WBTC","y":"WBTC.MI","n":"WisdomTree Physical Bitcoin","c":"WisdomTree","provider":"WisdomTree"},{"t":"QS5S","y":"QS5S.MI","n":"WisdomTree NASDAQ 100 5x Daily Short","c":"WisdomTree","provider":"WisdomTree"},{"t":"9GAL","y":"9GAL.DE","n":"WisdomTree Agriculture Longer Dated","c":"WisdomTree","provider":"WisdomTree"},{"t":"ENGS","y":"ENGS.MI","n":"WisdomTree Natural Gas - EUR Daily Hedged","c":"WisdomTree","provider":"WisdomTree"},{"t":"BRND","y":"BRND.MI","n":"WisdomTree Bloomberg Brent Crude Oil","c":"WisdomTree","provider":"WisdomTree"},{"t":"LNGA","y":"LNGA.MI","n":"WisdomTree Natural Gas 2x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree"},{"t":"3UKL","y":"3UKL.L","n":"WisdomTree FTSE 100 3x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree"},{"t":"3BTS","y":"3BTS.MI","n":"WisdomTree BTP 10Y 3x Daily Short","c":"WisdomTree","provider":"WisdomTree"},{"t":"LEU3","y":"LEU3.L","n":"WisdomTree Long EUR Short USD 3x Daily","c":"WisdomTree","provider":"WisdomTree"},{"t":"OOEC","y":"OOEC.DE","n":"WisdomTree Broad Commodities Ex-Agriculture and Livestock","c":"WisdomTree","provider":"WisdomTree"},{"t":"USE5","y":"USE5.MI","n":"WisdomTree Short USD Long EUR 5x Daily","c":"WisdomTree","provider":"WisdomTree"},{"t":"3ITS","y":"3ITS.MI","n":"WisdomTree FTSE MIB 3x Daily Short","c":"WisdomTree","provider":"WisdomTree"},{"t":"LPLA","y":"LPLA.MI","n":"WisdomTree Platinum 2x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree"},{"t":"EUAU","y":"EUAU.MI","n":"WisdomTree Long AUD Short EUR","c":"WisdomTree","provider":"WisdomTree"},{"t":"EWAT","y":"EWAT.MI","n":"WisdomTree Wheat - EUR Daily Hedged","c":"WisdomTree","provider":"WisdomTree"},{"t":"TINM","y":"TINM.MI","n":"WisdomTree Tin","c":"WisdomTree","provider":"WisdomTree"},{"t":"FCRU","y":"FCRU.MI","n":"WisdomTree WTI Crude Oil Longer Dated","c":"WisdomTree","provider":"WisdomTree"},{"t":"ALUM","y":"ALUM.MI","n":"WisdomTree Aluminium","c":"WisdomTree","provider":"WisdomTree"},{"t":"WSPE","y":"WSPE.MI","n":"WisdomTree S&P 500 EUR Daily Hedged","c":"WisdomTree","provider":"WisdomTree"},{"t":"3TYL","y":"3TYL.MI","n":"WisdomTree US Treasuries 10Y 3x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree"},{"t":"5BUS","y":"5BUS.MI","n":"WisdomTree Bund 10Y 5x Daily Short","c":"WisdomTree","provider":"WisdomTree"},{"t":"EUCH","y":"EUCH.MI","n":"WisdomTree Long CHF Short EUR","c":"WisdomTree","provider":"WisdomTree"},{"t":"XBJF","y":"XBJF.DE","n":"WisdomTree Short CNY Long USD","c":"WisdomTree","provider":"WisdomTree"},{"t":"LALU","y":"LALU.MI","n":"WisdomTree Aluminium 2x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree"},{"t":"LJPY","y":"LJPY.L","n":"WisdomTree Long JPY Short USD","c":"WisdomTree","provider":"WisdomTree"},{"t":"GBEU","y":"GBEU.MI","n":"WisdomTree Short GBP Long EUR","c":"WisdomTree","provider":"WisdomTree"},{"t":"3EML","y":"3EML.MI","n":"WisdomTree Emerging Markets 3x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree"},{"t":"LEUR","y":"LEUR.L","n":"WisdomTree Long EUR Short USD","c":"WisdomTree","provider":"WisdomTree"},{"t":"UL3S","y":"UL3S.MI","n":"WisdomTree US Treasuries 30Y 3x Daily Short","c":"WisdomTree","provider":"WisdomTree"},{"t":"SEUR","y":"SEUR.L","n":"WisdomTree Short EUR Long USD","c":"WisdomTree","provider":"WisdomTree"},{"t":"EUUS","y":"EUUS.MI","n":"WisdomTree Long USD Short EUR","c":"WisdomTree","provider":"WisdomTree"},{"t":"SUP3","y":"SUP3.L","n":"WisdomTree Short EUR Long GBP 3x Daily","c":"WisdomTree","provider":"WisdomTree"},{"t":"BLOC","y":"BLOC.PA","n":"WisdomTree Physical Crypto Mega Cap","c":"WisdomTree","provider":"WisdomTree"},{"t":"DGRP","y":"DGRP.L","n":"WisdomTree US Quality Dividend Growth UCITS ETF - USD","c":"WisdomTree","provider":"WisdomTree"},{"t":"DGRW","y":"DGRW.L","n":"WisdomTree US Quality Dividend Growth UCITS ETF - USD","c":"WisdomTree","provider":"WisdomTree"},{"t":"9GAK","y":"9GAK.DE","n":"WisdomTree Industrial Metals Longer Dated","c":"WisdomTree","provider":"WisdomTree"},{"t":"QQQS","y":"QQQS.MI","n":"WisdomTree NASDAQ 100 3x Daily Short","c":"WisdomTree","provider":"WisdomTree"},{"t":"3SUL","y":"3SUL.MI","n":"WisdomTree Sugar 3x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree"},{"t":"EBRT","y":"EBRT.MI","n":"WisdomTree Brent Crude Oil - EUR Daily Hedged","c":"WisdomTree","provider":"WisdomTree"},{"t":"NOEU","y":"NOEU.MI","n":"WisdomTree Short NOK Long EUR","c":"WisdomTree","provider":"WisdomTree"},{"t":"1PAS","y":"1PAS.MI","n":"WisdomTree Palladium 1x Daily Short","c":"WisdomTree","provider":"WisdomTree"},{"t":"3SEM","y":"3SEM.MI","n":"WisdomTree PHLX Semiconductor 3x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree"},{"t":"VIXL","y":"VIXL.MI","n":"WisdomTree S&P 500 VIX Short-Term Futures 2.25x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree"},{"t":"GBUR","y":"GBUR.L","n":"WisdomTree Long EUR Short GBP","c":"WisdomTree","provider":"WisdomTree"},{"t":"2MCL","y":"2MCL.L","n":"WisdomTree FTSE 250 2x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree"},{"t":"3BUL","y":"3BUL.MI","n":"WisdomTree Bund 10Y 3x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree"},{"t":"OD7K","y":"OD7K.DE","n":"WisdomTree Live Cattle","c":"WisdomTree","provider":"WisdomTree"},{"t":"WATT","y":"WATT.MI","n":"WisdomTree Battery Metals","c":"WisdomTree","provider":"WisdomTree"},{"t":"WRTY","y":"WRTY.MI","n":"WisdomTree Russell 2000","c":"WisdomTree","provider":"WisdomTree"},{"t":"WENH","y":"WENH.DE","n":"WisdomTree Strategic Metals UCITS ETF - EUR Hedged Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"WGRO","y":"WGRO.MI","n":"WisdomTree Global Quality Growth UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"NCLR","y":"NCLR.MI","n":"WisdomTree Uranium and Nuclear Energy UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"WDEF","y":"WDEF.MI","n":"WisdomTree Europe Defence UCITS ETF - EUR Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"COBA","y":"COBA.MI","n":"WisdomTree AT1 CoCo Bond UCITS ETF - EUR Hedged Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"3NGS","y":"3NGS.MI","n":"WisdomTree Natural Gas 3x Daily Short","c":"WisdomTree","provider":"WisdomTree"},{"t":"GBS","y":"GBS.MI","n":"Gold Bullion Securities","c":"WisdomTree","provider":"WisdomTree"},{"t":"NICK","y":"NICK.MI","n":"WisdomTree Nickel","c":"WisdomTree","provider":"WisdomTree"},{"t":"PIMT","y":"PIMT.L","n":"WisdomTree Industrial Metals - GBP Daily Hedged","c":"WisdomTree","provider":"WisdomTree"},{"t":"SEU3","y":"SEU3.L","n":"WisdomTree Short EUR Long USD 3x Daily","c":"WisdomTree","provider":"WisdomTree"},{"t":"JPGB","y":"JPGB.L","n":"WisdomTree Short JPY Long GBP","c":"WisdomTree","provider":"WisdomTree"},{"t":"3ITL","y":"3ITL.MI","n":"WisdomTree FTSE MIB 3x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree"},{"t":"2OIG","y":"2OIG.MI","n":"WisdomTree STOXX Europe Oil & Gas 2x Daily Short","c":"WisdomTree","provider":"WisdomTree"},{"t":"SALL","y":"SALL.MI","n":"WisdomTree Broad Commodities 1x Daily Short","c":"WisdomTree","provider":"WisdomTree"},{"t":"2UKL","y":"2UKL.L","n":"WisdomTree FTSE 100 2x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree"},{"t":"OOEB","y":"OOEB.DE","n":"WisdomTree Brent Crude Oil Longer Dated","c":"WisdomTree","provider":"WisdomTree"},{"t":"BENE","y":"BENE.MI","n":"WisdomTree Energy Enhanced","c":"WisdomTree","provider":"WisdomTree"},{"t":"3USS","y":"3USS.MI","n":"WisdomTree S&P 500 3x Daily Short","c":"WisdomTree","provider":"WisdomTree"},{"t":"WETH","y":"WETH.MI","n":"WisdomTree Physical Ethereum","c":"WisdomTree","provider":"WisdomTree"},{"t":"LWEA","y":"LWEA.MI","n":"WisdomTree Wheat 2x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree"},{"t":"CRRP","y":"CRRP.L","n":"WisdomTree Enhanced Commodity Carry - GBP Daily Hedged","c":"WisdomTree","provider":"WisdomTree"},{"t":"WCCA","y":"WCCA.MI","n":"WisdomTree California Carbon","c":"WisdomTree","provider":"WisdomTree"},{"t":"2PAL","y":"2PAL.MI","n":"WisdomTree Palladium 2x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree"},{"t":"SOLW","y":"SOLW.MI","n":"WisdomTree Physical Solana","c":"WisdomTree","provider":"WisdomTree"},{"t":"3CAC","y":"3CAC.PA","n":"WisdomTree CAC 40 3x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree"},{"t":"LGB3","y":"LGB3.L","n":"WisdomTree Long GBP Short USD 3x Daily","c":"WisdomTree","provider":"WisdomTree"},{"t":"NGAS","y":"NGAS.MI","n":"WisdomTree Natural Gas","c":"WisdomTree","provider":"WisdomTree"},{"t":"WXLM","y":"WXLM.MI","n":"WisdomTree Physical Stellar Lumens","c":"WisdomTree","provider":"WisdomTree"},{"t":"SOIL","y":"SOIL.MI","n":"WisdomTree WTI Crude Oil 1x Daily Short","c":"WisdomTree","provider":"WisdomTree"},{"t":"3NGL","y":"3NGL.MI","n":"WisdomTree Natural Gas 3x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree"},{"t":"LSTE","y":"LSTE.MI","n":"WisdomTree Physical Lido Staked Ether","c":"WisdomTree","provider":"WisdomTree"},{"t":"LPET","y":"LPET.MI","n":"WisdomTree Petroleum 2x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree"},{"t":"EUNO","y":"EUNO.MI","n":"WisdomTree Long NOK Short EUR","c":"WisdomTree","provider":"WisdomTree"},{"t":"PBRT","y":"PBRT.L","n":"WisdomTree Brent Crude Oil - GBP Daily Hedged","c":"WisdomTree","provider":"WisdomTree"},{"t":"EUP3","y":"EUP3.L","n":"WisdomTree Long EUR Short GBP 3x Daily","c":"WisdomTree","provider":"WisdomTree"},{"t":"AIGS","y":"AIGS.MI","n":"WisdomTree Softs","c":"WisdomTree","provider":"WisdomTree"},{"t":"EZNC","y":"EZNC.MI","n":"WisdomTree Zinc - EUR Daily Hedged","c":"WisdomTree","provider":"WisdomTree"},{"t":"COPA","y":"COPA.MI","n":"WisdomTree Copper","c":"WisdomTree","provider":"WisdomTree"},{"t":"ECOP","y":"ECOP.MI","n":"WisdomTree Copper - EUR Daily Hedged","c":"WisdomTree","provider":"WisdomTree"},{"t":"5ITS","y":"5ITS.MI","n":"WisdomTree FTSE MIB 5x Daily Short","c":"WisdomTree","provider":"WisdomTree"},{"t":"ECH3","y":"ECH3.MI","n":"WisdomTree Long CHF Short EUR 3x Daily","c":"WisdomTree","provider":"WisdomTree"},{"t":"BULL","y":"BULL.MI","n":"WisdomTree Gold","c":"WisdomTree","provider":"WisdomTree"},{"t":"3GOL","y":"3GOL.MI","n":"WisdomTree Gold 3x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree"},{"t":"EFCM","y":"EFCM.MI","n":"WisdomTree Broad Commodities Longer Dated - EUR Daily Hedged","c":"WisdomTree","provider":"WisdomTree"},{"t":"ESVR","y":"ESVR.MI","n":"WisdomTree Silver - EUR Daily Hedged","c":"WisdomTree","provider":"WisdomTree"},{"t":"BRNT","y":"BRNT.MI","n":"WisdomTree Brent Crude Oil","c":"WisdomTree","provider":"WisdomTree"},{"t":"3SIS","y":"3SIS.MI","n":"WisdomTree Silver 3x Daily Short","c":"WisdomTree","provider":"WisdomTree"},{"t":"SIMT","y":"SIMT.MI","n":"WisdomTree Industrial Metals 1x Daily Short","c":"WisdomTree","provider":"WisdomTree"},{"t":"EUS3","y":"EUS3.MI","n":"WisdomTree Long USD Short EUR 3x Daily","c":"WisdomTree","provider":"WisdomTree"},{"t":"WCRX","y":"WCRX.MI","n":"WisdomTree Physical CoinDesk 20","c":"WisdomTree","provider":"WisdomTree"},{"t":"LSUG","y":"LSUG.MI","n":"WisdomTree Sugar 2x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree"},{"t":"EJP3","y":"EJP3.MI","n":"WisdomTree Long JPY Short EUR 3x Daily","c":"WisdomTree","provider":"WisdomTree"},{"t":"SCOP","y":"SCOP.MI","n":"WisdomTree Copper 1x Daily Short","c":"WisdomTree","provider":"WisdomTree"},{"t":"AIGO","y":"AIGO.MI","n":"WisdomTree Petroleum","c":"WisdomTree","provider":"WisdomTree"},{"t":"DXJA","y":"DXJA.L","n":"WisdomTree Japan Equity UCITS ETF - USD Hedged Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"DXJP","y":"DXJP.L","n":"WisdomTree Japan Equity UCITS ETF - GBP Hedged","c":"WisdomTree","provider":"WisdomTree"},{"t":"DXJZ","y":"DXJZ.MI","n":"WisdomTree Japan Equity UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"HEDF","y":"HEDF.MI","n":"WisdomTree Europe Equity UCITS ETF - EUR Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"LNIK","y":"LNIK.MI","n":"WisdomTree Nickel 2x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree"},{"t":"3HCL","y":"3HCL.MI","n":"WisdomTree Copper 3x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree"},{"t":"OD7I","y":"OD7I.DE","n":"WisdomTree Heating Oil","c":"WisdomTree","provider":"WisdomTree"},{"t":"ZINC","y":"ZINC.MI","n":"WisdomTree Zinc","c":"WisdomTree","provider":"WisdomTree"},{"t":"CRUD","y":"CRUD.MI","n":"WisdomTree WTI Crude Oil","c":"WisdomTree","provider":"WisdomTree"},{"t":"LBUL","y":"LBUL.MI","n":"WisdomTree Gold 2x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree"},{"t":"USEU","y":"USEU.MI","n":"WisdomTree Short USD Long EUR","c":"WisdomTree","provider":"WisdomTree"},{"t":"LAGR","y":"LAGR.MI","n":"WisdomTree Agriculture 2x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree"},{"t":"AUEU","y":"AUEU.MI","n":"WisdomTree Short AUD Long EUR","c":"WisdomTree","provider":"WisdomTree"},{"t":"3EMS","y":"3EMS.MI","n":"WisdomTree Emerging Markets 3x Daily Short","c":"WisdomTree","provider":"WisdomTree"},{"t":"AIGA","y":"AIGA.MI","n":"WisdomTree Agriculture","c":"WisdomTree","provider":"WisdomTree"},{"t":"5EUL","y":"5EUL.MI","n":"WisdomTree EURO STOXX 50 5x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree"},{"t":"3BUS","y":"3BUS.MI","n":"WisdomTree Bund 10Y 3x Daily Short","c":"WisdomTree","provider":"WisdomTree"},{"t":"USGB","y":"USGB.L","n":"WisdomTree Short USD Long GBP","c":"WisdomTree","provider":"WisdomTree"},{"t":"00XQ","y":"00XQ.DE","n":"WisdomTree Precious Metals - EUR Daily Hedged","c":"WisdomTree","provider":"WisdomTree"},{"t":"SGBP","y":"SGBP.L","n":"WisdomTree Short GBP Long USD","c":"WisdomTree","provider":"WisdomTree"},{"t":"SOYB","y":"SOYB.MI","n":"WisdomTree Soybeans","c":"WisdomTree","provider":"WisdomTree"},{"t":"3BAL","y":"3BAL.MI","n":"WisdomTree EURO STOXX Banks 3x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree"},{"t":"3SIL","y":"3SIL.MI","n":"WisdomTree Silver 3x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree"},{"t":"3OIS","y":"3OIS.MI","n":"WisdomTree WTI Crude Oil 3x Daily Short","c":"WisdomTree","provider":"WisdomTree"},{"t":"LCFE","y":"LCFE.MI","n":"WisdomTree Coffee 2x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree"},{"t":"1GIS","y":"1GIS.L","n":"WisdomTree Gilts 10Y 1x Daily Short","c":"WisdomTree","provider":"WisdomTree"},{"t":"ESOY","y":"ESOY.MI","n":"WisdomTree Soybeans - EUR Daily Hedged","c":"WisdomTree","provider":"WisdomTree"},{"t":"CARB","y":"CARB.MI","n":"WisdomTree Carbon","c":"WisdomTree","provider":"WisdomTree"},{"t":"COCO","y":"COCO.MI","n":"WisdomTree Cocoa","c":"WisdomTree","provider":"WisdomTree"},{"t":"SNIK","y":"SNIK.MI","n":"WisdomTree Nickel 1x Daily Short","c":"WisdomTree","provider":"WisdomTree"},{"t":"2TRV","y":"2TRV.MI","n":"WisdomTree STOXX Europe Travel & Leisure 2x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree"},{"t":"GBSP","y":"GBSP.L","n":"WisdomTree Physical Gold - GBP Daily Hedged","c":"WisdomTree","provider":"WisdomTree"},{"t":"USP3","y":"USP3.L","n":"WisdomTree Long USD Short GBP 3x Daily","c":"WisdomTree","provider":"WisdomTree"},{"t":"GBSE","y":"GBSE.MI","n":"WisdomTree Physical Gold - EUR Daily Hedged","c":"WisdomTree","provider":"WisdomTree"},{"t":"EUJP","y":"EUJP.MI","n":"WisdomTree Long JPY Short EUR","c":"WisdomTree","provider":"WisdomTree"},{"t":"SUGA","y":"SUGA.MI","n":"WisdomTree Sugar","c":"WisdomTree","provider":"WisdomTree"},{"t":"TTFW","y":"TTFW.MI","n":"WisdomTree European Natural Gas","c":"WisdomTree","provider":"WisdomTree"},{"t":"SNGA","y":"SNGA.MI","n":"WisdomTree Natural Gas 1x Daily Short","c":"WisdomTree","provider":"WisdomTree"},{"t":"SBUL","y":"SBUL.MI","n":"WisdomTree Gold 1x Daily Short","c":"WisdomTree","provider":"WisdomTree"},{"t":"EGB3","y":"EGB3.MI","n":"WisdomTree Long GBP Short EUR 3x Daily","c":"WisdomTree","provider":"WisdomTree"},{"t":"3BRL","y":"3BRL.MI","n":"WisdomTree Brent Crude Oil 3x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree"},{"t":"PHAG","y":"PHAG.MI","n":"WisdomTree Physical Silver","c":"WisdomTree","provider":"WisdomTree"},{"t":"EGB5","y":"EGB5.MI","n":"WisdomTree Long GBP Short EUR 5x Daily","c":"WisdomTree","provider":"WisdomTree"},{"t":"WMIB","y":"WMIB.MI","n":"WisdomTree FTSE MIB","c":"WisdomTree","provider":"WisdomTree"},{"t":"PUS3","y":"PUS3.L","n":"WisdomTree Short USD Long GBP 3x Daily","c":"WisdomTree","provider":"WisdomTree"},{"t":"CHE3","y":"CHE3.MI","n":"WisdomTree Short CHF Long EUR 3x Daily","c":"WisdomTree","provider":"WisdomTree"},{"t":"ENIK","y":"ENIK.MI","n":"WisdomTree Nickel - EUR Daily Hedged","c":"WisdomTree","provider":"WisdomTree"},{"t":"00XJ","y":"00XJ.DE","n":"WisdomTree Agriculture - EUR Daily Hedged","c":"WisdomTree","provider":"WisdomTree"},{"t":"LBRT","y":"LBRT.MI","n":"WisdomTree Brent Crude Oil 2x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree"},{"t":"SBRT","y":"SBRT.MI","n":"WisdomTree Brent Crude Oil 1x Daily Short","c":"WisdomTree","provider":"WisdomTree"},{"t":"3GIL","y":"3GIL.L","n":"WisdomTree Gilts 10Y 3x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree"},{"t":"3OIL","y":"3OIL.MI","n":"WisdomTree WTI Crude Oil 3x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree"},{"t":"GBCH","y":"GBCH.L","n":"WisdomTree Long CHF Short GBP","c":"WisdomTree","provider":"WisdomTree"},{"t":"WADA","y":"WADA.AS","n":"WisdomTree Physical Cardano","c":"WisdomTree","provider":"WisdomTree"},{"t":"ADAW","y":"ADAW.PA","n":"WisdomTree Physical Cardano","c":"WisdomTree","provider":"WisdomTree"},{"t":"PHPD","y":"PHPD.MI","n":"WisdomTree Physical Palladium","c":"WisdomTree","provider":"WisdomTree"},{"t":"WENT","y":"WENT.MI","n":"WisdomTree Energy Transition Metals","c":"WisdomTree","provider":"WisdomTree"},{"t":"3BRS","y":"3BRS.MI","n":"WisdomTree Brent Crude Oil 3x Daily Short","c":"WisdomTree","provider":"WisdomTree"},{"t":"3GIS","y":"3GIS.L","n":"WisdomTree Gilts 10Y 3x Daily Short","c":"WisdomTree","provider":"WisdomTree"},{"t":"3BAS","y":"3BAS.MI","n":"WisdomTree EURO STOXX Banks 3x Daily Short","c":"WisdomTree","provider":"WisdomTree"},{"t":"WXRP","y":"WXRP.MI","n":"WisdomTree Physical XRP","c":"WisdomTree","provider":"WisdomTree"},{"t":"3MG7","y":"3MG7.MI","n":"WisdomTree Magnificent 7 3x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree"},{"t":"SSIL","y":"SSIL.MI","n":"WisdomTree Silver 1x Daily Short","c":"WisdomTree","provider":"WisdomTree"},{"t":"3BTL","y":"3BTL.MI","n":"WisdomTree BTP 10Y 3x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree"},{"t":"9GAG","y":"9GAG.DE","n":"WisdomTree Energy Longer Dated","c":"WisdomTree","provider":"WisdomTree"},{"t":"WWRD","y":"WWRD.MI","n":"WisdomTree World","c":"WisdomTree","provider":"WisdomTree"},{"t":"GBJP","y":"GBJP.L","n":"WisdomTree Long JPY Short GBP","c":"WisdomTree","provider":"WisdomTree"},{"t":"ITBL","y":"ITBL.MI","n":"WisdomTree FTSE MIB Banks","c":"WisdomTree","provider":"WisdomTree"},{"t":"WDOT","y":"WDOT.AS","n":"WisdomTree Physical Polkadot","c":"WisdomTree","provider":"WisdomTree"},{"t":"DOTW","y":"DOTW.PA","n":"WisdomTree Physical Polkadot","c":"WisdomTree","provider":"WisdomTree"},{"t":"PHAU","y":"PHAU.MI","n":"WisdomTree Physical Gold","c":"WisdomTree","provider":"WisdomTree"},{"t":"UGAS","y":"UGAS.MI","n":"WisdomTree Gasoline","c":"WisdomTree","provider":"WisdomTree"},{"t":"SGB3","y":"SGB3.L","n":"WisdomTree Short GBP Long USD 3x Daily","c":"WisdomTree","provider":"WisdomTree"},{"t":"SUK1","y":"SUK1.L","n":"WisdomTree FTSE 100 1x Daily Short","c":"WisdomTree","provider":"WisdomTree"},{"t":"SGBS","y":"SGBS.MI","n":"WisdomTree Physical Swiss Gold","c":"WisdomTree","provider":"WisdomTree"},{"t":"3TYS","y":"3TYS.MI","n":"WisdomTree US Treasuries 10Y 3x Daily Short","c":"WisdomTree","provider":"WisdomTree"},{"t":"ECRN","y":"ECRN.MI","n":"WisdomTree Corn - EUR Daily Hedged","c":"WisdomTree","provider":"WisdomTree"},{"t":"AIGI","y":"AIGI.MI","n":"WisdomTree Industrial Metals","c":"WisdomTree","provider":"WisdomTree"},{"t":"5EUS","y":"5EUS.MI","n":"WisdomTree EURO STOXX 50 5x Daily Short","c":"WisdomTree","provider":"WisdomTree"},{"t":"GBE3","y":"GBE3.MI","n":"WisdomTree Short GBP Long EUR 3x Daily","c":"WisdomTree","provider":"WisdomTree"},{"t":"SEEU","y":"SEEU.MI","n":"WisdomTree Short SEK Long EUR","c":"WisdomTree","provider":"WisdomTree"},{"t":"XBJE","y":"XBJE.DE","n":"WisdomTree Long CNY Short USD","c":"WisdomTree","provider":"WisdomTree"},{"t":"5USL","y":"5USL.MI","n":"WisdomTree S&P 500 5x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree"},{"t":"2CAR","y":"2CAR.MI","n":"WisdomTree STOXX Europe Automobiles 2x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree"},{"t":"WSLV","y":"WSLV.MI","n":"WisdomTree Core Physical Silver","c":"WisdomTree","provider":"WisdomTree"},{"t":"GBE5","y":"GBE5.MI","n":"WisdomTree Short GBP Long EUR 5x Daily","c":"WisdomTree","provider":"WisdomTree"},{"t":"CRRE","y":"CRRE.MI","n":"WisdomTree Enhanced Commodity Carry - EUR Daily Hedged","c":"WisdomTree","provider":"WisdomTree"},{"t":"JPEU","y":"JPEU.MI","n":"WisdomTree Short JPY Long EUR","c":"WisdomTree","provider":"WisdomTree"},{"t":"3USL","y":"3USL.MI","n":"WisdomTree S&P 500 3x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree"},{"t":"EIMT","y":"EIMT.MI","n":"WisdomTree Industrial Metals - EUR Daily Hedged","c":"WisdomTree","provider":"WisdomTree"},{"t":"AIGG","y":"AIGG.MI","n":"WisdomTree Grains","c":"WisdomTree","provider":"WisdomTree"},{"t":"ESUG","y":"ESUG.MI","n":"WisdomTree Sugar - EUR Daily Hedged","c":"WisdomTree","provider":"WisdomTree"},{"t":"PHPM","y":"PHPM.MI","n":"WisdomTree Physical Precious Metals","c":"WisdomTree","provider":"WisdomTree"},{"t":"LCOP","y":"LCOP.MI","n":"WisdomTree Copper 2x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree"},{"t":"CHEU","y":"CHEU.MI","n":"WisdomTree Short CHF Long EUR","c":"WisdomTree","provider":"WisdomTree"},{"t":"CHGB","y":"CHGB.L","n":"WisdomTree Short CHF Long GBP","c":"WisdomTree","provider":"WisdomTree"},{"t":"MEGA","y":"MEGA.AS","n":"WisdomTree Physical Crypto Mega Cap Equal Weight","c":"WisdomTree","provider":"WisdomTree"},{"t":"5BTS","y":"5BTS.MI","n":"WisdomTree BTP 10Y 5x Daily Short","c":"WisdomTree","provider":"WisdomTree"},{"t":"META","y":"META.MI","n":"WisdomTree Industrial Metals Enhanced","c":"WisdomTree","provider":"WisdomTree"},{"t":"1MCS","y":"1MCS.L","n":"WisdomTree FTSE 250 1x Daily Short","c":"WisdomTree","provider":"WisdomTree"},{"t":"SLVR","y":"SLVR.MI","n":"WisdomTree Silver","c":"WisdomTree","provider":"WisdomTree"},{"t":"2STR","y":"2STR.MI","n":"WisdomTree STOXX Europe Travel & Leisure 2x Daily Short","c":"WisdomTree","provider":"WisdomTree"},{"t":"CRRY","y":"CRRY.MI","n":"WisdomTree Enhanced Commodity Carry","c":"WisdomTree","provider":"WisdomTree"},{"t":"LCOC","y":"LCOC.MI","n":"WisdomTree Cocoa 2x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree"},{"t":"COFF","y":"COFF.MI","n":"WisdomTree Coffee","c":"WisdomTree","provider":"WisdomTree"},{"t":"EBUL","y":"EBUL.MI","n":"WisdomTree Gold - EUR Daily Hedged","c":"WisdomTree","provider":"WisdomTree"},{"t":"3EUL","y":"3EUL.MI","n":"WisdomTree EURO STOXX 50® 3x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree"},{"t":"5USS","y":"5USS.MI","n":"WisdomTree S&P 500 5x Daily Short","c":"WisdomTree","provider":"WisdomTree"},{"t":"USE3","y":"USE3.MI","n":"WisdomTree Short USD Long EUR 3x Daily","c":"WisdomTree","provider":"WisdomTree"},{"t":"ECRD","y":"ECRD.MI","n":"WisdomTree WTI Crude Oil - EUR Daily Hedged","c":"WisdomTree","provider":"WisdomTree"},{"t":"LJP3","y":"LJP3.L","n":"WisdomTree Long JPY Short USD 3x Daily","c":"WisdomTree","provider":"WisdomTree"},{"t":"WNAS","y":"WNAS.MI","n":"WisdomTree NASDAQ-100","c":"WisdomTree","provider":"WisdomTree"},{"t":"WTID","y":"WTID.MI","n":"WisdomTree Bloomberg WTI Crude Oil","c":"WisdomTree","provider":"WisdomTree"},{"t":"CODO","y":"CODO.L","n":"WisdomTree AT1 CoCo Bond UCITS ETF - USD Hedged","c":"WisdomTree","provider":"WisdomTree"},{"t":"EALU","y":"EALU.MI","n":"WisdomTree Aluminium - EUR Daily Hedged","c":"WisdomTree","provider":"WisdomTree"},{"t":"CORN","y":"CORN.MI","n":"WisdomTree Corn","c":"WisdomTree","provider":"WisdomTree"},{"t":"WPAI","y":"WPAI.MI","n":"WisdomTree Physical AI, Humanoids and Drones UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"WBLD","y":"WBLD.MI","n":"WisdomTree Europe Infrastructure UCITS ETF - EUR Acc","c":"WisdomTree","provider":"WisdomTree"},{"t":"XSD2","y":"XSD2.MI","n":"Xtrackers ShortDAX x2 Daily Swap UCITS ETF 1C","c":"","provider":"Xtrackers"},{"t":"XSDX","y":"XSDX.MI","n":"Xtrackers ShortDAX Daily Swap UCITS ETF 1C","c":"","provider":"Xtrackers"},{"t":"XSGL","y":"XSGL.MI","n":"Xtrackers Short iBoxx EUR Sovereigns Eurozone Daily Swap UCITS ETF 1C","c":"","provider":"Xtrackers"},{"t":"XSPS","y":"XSPS.MI","n":"Xtrackers S&P 500 Inverse Daily Swap UCITS ETF 1C","c":"","provider":"Xtrackers"},{"t":"XS2L","y":"XS2L.MI","n":"Xtrackers S&P 500 2x Leveraged Daily Swap UCITS ETF 1C","c":"","provider":"Xtrackers"},{"t":"XT21","y":"XT21.MI","n":"Xtrackers S&P 500 2x Inverse Daily Swap UCITS ETF 1C","c":"","provider":"Xtrackers"},{"t":"XLDX","y":"XLDX.MI","n":"Xtrackers LevDAX Daily Swap UCITS ETF 1C","c":"","provider":"Xtrackers"},{"t":"XTC5","y":"XTC5.MI","n":"Xtrackers iTraxx Crossover Short Daily Swap UCITS ETF 1C","c":"","provider":"Xtrackers"},{"t":"XUKS","y":"XUKS.MI","n":"Xtrackers FTSE 100 Short Daily Swap UCITS ETF 1C","c":"","provider":"Xtrackers"},{"t":"XSSX","y":"XSSX.MI","n":"Xtrackers EURO STOXX 50 Short Daily Swap UCITS ETF 1C","c":"","provider":"Xtrackers"},{"t":"UEQC","y":"UEQC.MI","n":"UBS CMCI Commodity Carry SF UCITS ETF USD acc","c":"","provider":"Xtrackers"},{"t":"UEQV","y":"UEQV.MI","n":"UBS CMCI Commodity Carry SF UCITS ETF hEUR acc","c":"","provider":"Xtrackers"},{"t":"UBF6","y":"UBF6.MI","n":"UBS CMCI Commodity Carry ex-Agriculture SF UCITS ETF USD acc","c":"","provider":"Xtrackers"},{"t":"UBF7","y":"UBF7.MI","n":"UBS CMCI Commodity Carry ex-Agriculture SF UCITS ETF hEUR acc","c":"","provider":"Xtrackers"},{"t":"TLT5","y":"TLT5.MI","n":"Leverage Shares 5x Long 20+ Year Treasury Bond ETP","c":"","provider":"Xtrackers"},{"t":"3CRE","y":"3CRE.MI","n":"Leverage Shares 3x Salesforce.com ETP Securities","c":"","provider":"Xtrackers"},{"t":"XOM3","y":"XOM3.MI","n":"Leverage Shares 3x Long Exxon (XOM) ETP Securities","c":"","provider":"Xtrackers"},{"t":"3DIE","y":"3DIE.MI","n":"Leverage Shares 3x Disney ETP Securities","c":"","provider":"Xtrackers"},{"t":"2BRE","y":"2BRE.MI","n":"Leverage Shares 2x Long Berkshire Hathaway (BRK-B) ETP","c":"","provider":"Xtrackers"},{"t":"COMN","y":"COMN.MI","n":"L&G Market Neutral Commodities UCITS ETF USD Acc","c":"","provider":"Xtrackers"},{"t":"DES2","y":"DES2.MI","n":"L&G DAX Daily 2x Short UCITS ETF","c":"","provider":"Xtrackers"},{"t":"DEL2","y":"DEL2.MI","n":"L&G DAX Daily 2x Long UCITS ETF","c":"","provider":"Xtrackers"},{"t":"STPU","y":"STPU.MI","n":"Amundi US Curve steepening 2-10Y UCITS ETF Acc","c":"","provider":"Xtrackers"},{"t":"DAX2S","y":"DAX2S.MI","n":"Amundi ShortDAX Daily (-2x) Inverse UCITS ETF Acc","c":"","provider":"Xtrackers"},{"t":"AHYK","y":"AHYK.MI","n":"Amundi ShortDAX Daily (-1x) Inverse UCITS ETF - Dist","c":"","provider":"Xtrackers"},{"t":"LQQ","y":"LQQ.MI","n":"Amundi Nasdaq-100 Daily (2x) Leveraged UCITS ETF Acc","c":"","provider":"Xtrackers"},{"t":"CL2","y":"CL2.MI","n":"Amundi MSCI USA Daily (2x) Leveraged UCITS ETF Acc","c":"","provider":"Xtrackers"},{"t":"SPX2S","y":"SPX2S.MI","n":"Amundi MSCI USA Daily (-1x) Inverse UCITS ETF Acc","c":"","provider":"Xtrackers"},{"t":"DAXLEV","y":"DAXLEV.MI","n":"Amundi LevDax Daily (2x) leveraged UCITS ETF Acc","c":"","provider":"Xtrackers"},{"t":"BTP2S","y":"BTP2S.MI","n":"Amundi Italy BTP Daily (-2x) Inverse UCITS ETF Acc","c":"","provider":"Xtrackers"},{"t":"BUND2S","y":"BUND2S.MI","n":"Amundi German Bund Daily (-2x) Inverse UCITS ETF Acc","c":"","provider":"Xtrackers"},{"t":"LEVMIB","y":"LEVMIB.MI","n":"Amundi FTSE MIB Daily (2x) Leveraged UCITS ETF Dist","c":"","provider":"Xtrackers"},{"t":"XBRMIB","y":"XBRMIB.MI","n":"Amundi FTSE MIB Daily (-2x) Inverse UCITS ETF Acc","c":"","provider":"Xtrackers"},{"t":"BERMIB","y":"BERMIB.MI","n":"Amundi FTSE MIB Daily (-1x) Inverse UCITS ETF Acc","c":"","provider":"Xtrackers"},{"t":"DJLEV","y":"DJLEV.MI","n":"Amundi EURO STOXX 50 Daily (2x) Leveraged UCITS ETF Acc","c":"","provider":"Xtrackers"},{"t":"BXX","y":"BXX.MI","n":"Amundi EURO STOXX 50 Daily (-2x) Inverse UCITS ETF Acc","c":"","provider":"Xtrackers"},{"t":"BSX","y":"BSX.MI","n":"Amundi EURO STOXX 50 Daily (-1x) Inverse UCITS ETF Acc","c":"","provider":"Xtrackers"}]

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

        # Data cambio zona (crossover KAMA)
        entry_date = '—'
        try:
            timestamps = [int(t.timestamp()) for t in hist.index]
            zona_series = []
            for ii in range(len(close)):
                kfi = kama_fast[ii]; ksi = kama_slow[ii]
                zona_series.append(get_zona(close[ii], kfi, ksi) if kfi and ksi else 'ND')
            current_z = zona_series[-1]
            for idx in range(len(zona_series)-2, max(0, len(zona_series)-60), -1):
                if zona_series[idx] != current_z:
                    dt = datetime.datetime.fromtimestamp(timestamps[idx+1])
                    entry_date = dt.strftime('%d/%m/%Y')
                    break
        except: pass

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
            'entryDate': entry_date,
        }
    except Exception:
        return None


# ═══════════════════════════════════════════════════════
# EMAIL ALERT
# ═══════════════════════════════════════════════════════
def send_alert_email(alerts, vix, vstoxx, regime, now):
    import smtplib, os
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    EMAIL_USER = os.environ.get('EMAIL_USER','')
    EMAIL_PASS = os.environ.get('EMAIL_PASS','')
    if not EMAIL_USER or not EMAIL_PASS:
        print("EMAIL non configurata — skip")
        return
    ICONS = {'LONG_CONF':'🟢 LONG CONF','LONG_EARLY':'🔵 LONG EARLY',
             'GRIGIA':'🟡 GRIGIA','USCITA':'🔴 USCITA','STOP':'⛔ STOP'}
    subj = "⚡ RAPTOR LEVA — {} segnale/i · {}".format(len(alerts), now.strftime('%d/%m/%Y %H:%M'))
    rows_html = ""
    for a in alerts:
        bg = '#dafbe1' if 'LONG' in a['new'] else '#ffebe9'
        rows_html += '<tr style="background:{}">' \
            '<td style="padding:7px;font-weight:700;font-family:monospace">{}</td>' \
            '<td style="padding:7px;font-size:11px;color:#57606a">{}</td>' \
            '<td style="padding:7px">{}</td>' \
            '<td style="padding:7px">→</td>' \
            '<td style="padding:7px;font-weight:700">{}</td>' \
            '<td style="padding:7px;font-family:monospace">{}</td>' \
            '<td style="padding:7px;font-family:monospace;color:#dc2626">F:{}</td>' \
            '<td style="padding:7px;font-family:monospace;color:#7c3aed">S:{}</td>' \
            '<td style="padding:7px;font-weight:700">{}</td>' \
            '<td style="padding:7px">{}</td>' \
            '</tr>'.format(
                bg, a['ticker'], (a['nome'] or '')[:45],
                ICONS.get(a['old'],a['old']), ICONS.get(a['new'],a['new']),
                a['prezzo'], a['kf'], a['ks'], a['score'], a['entry'])
    vix_c = '#1a7f37' if (vix or 20)<20 else '#bc4c00' if (vix or 20)<30 else '#cf222e'
    html = """<!DOCTYPE html><html><body style="font-family:'Segoe UI',sans-serif;background:#f5f7fa;padding:20px">
<div style="max-width:860px;margin:0 auto;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,.1)">
  <div style="background:#dc2626;color:#fff;padding:14px 20px">
    <h2 style="margin:0;font-size:18px">⚡ RAPTOR LEVA — Nuovi Segnali</h2>
    <p style="margin:4px 0 0;font-size:12px;opacity:.85">{ts} · Regime: {reg} · VIX: {vx} / VSTOXX: {vs}</p>
  </div>
  <div style="padding:16px">
    <table style="width:100%;border-collapse:collapse;font-size:12px">
      <thead><tr style="background:#f5f7fa">
        <th style="padding:6px;text-align:left;border-bottom:2px solid #d0d7de">Ticker</th>
        <th style="padding:6px;text-align:left;border-bottom:2px solid #d0d7de">Nome</th>
        <th style="padding:6px;border-bottom:2px solid #d0d7de">Da</th>
        <th style="padding:6px;border-bottom:2px solid #d0d7de"></th>
        <th style="padding:6px;border-bottom:2px solid #d0d7de">A</th>
        <th style="padding:6px;border-bottom:2px solid #d0d7de">Prezzo</th>
        <th style="padding:6px;border-bottom:2px solid #d0d7de">KAMA F</th>
        <th style="padding:6px;border-bottom:2px solid #d0d7de">KAMA S</th>
        <th style="padding:6px;border-bottom:2px solid #d0d7de">Score</th>
        <th style="padding:6px;border-bottom:2px solid #d0d7de">Data</th>
      </tr></thead>
      <tbody>{rows}</tbody>
    </table>
    <p style="margin-top:12px;font-size:11px;color:#57606a">
      🌡️ VIX: <b style="color:{vc}">{vx}</b> · VSTOXX: {vs} · Regime: <b>{reg}</b><br>
      ⚠️ Solo uso educativo.<br>
      📊 <a href="https://giorgiogoldoni.github.io/raptor-leva/">Apri RAPTOR Leva</a>
    </p>
  </div>
</div></body></html>""".format(
        ts=now.strftime('%d/%m/%Y %H:%M'), reg=regime,
        vx=vix, vs=vstoxx, vc=vix_c, rows=rows_html)
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subj
        msg['From'] = EMAIL_USER
        msg['To'] = EMAIL_USER
        msg.attach(MIMEText(html,'html'))
        with smtplib.SMTP_SSL('smtp.gmail.com',465) as srv:
            srv.login(EMAIL_USER, EMAIL_PASS)
            srv.sendmail(EMAIL_USER, EMAIL_USER, msg.as_string())
        print("Email inviata: {} alert".format(len(alerts)))
    except Exception as e:
        print("Errore email: {}".format(e))

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

    # 3. Rileva cambi segnale e manda email
    prev_zones = {}
    try:
        with open('raptor_leva.json','r',encoding='utf-8') as f:
            prev_j = json.load(f)
            for r in prev_j.get('data',[]):
                prev_zones[r['ticker']] = r.get('zona','')
    except: pass

    CAMBI = {
        ('USCITA','LONG_CONF'),('STOP','LONG_CONF'),('GRIGIA','LONG_CONF'),('LONG_EARLY','LONG_CONF'),
        ('USCITA','LONG_EARLY'),('STOP','LONG_EARLY'),('GRIGIA','LONG_EARLY'),
        ('LONG_CONF','USCITA'),('LONG_EARLY','USCITA'),
        ('LONG_CONF','STOP'),('LONG_EARLY','STOP'),
    }
    alert_list = []
    for r in results:
        old_z = prev_zones.get(r['ticker'],'')
        new_z = r.get('zona','')
        if old_z and new_z and old_z != new_z and (old_z,new_z) in CAMBI:
            alert_list.append({'ticker':r['ticker'],'nome':r.get('nome',''),
                'old':old_z,'new':new_z,'score':r['score'],'prezzo':r['prezzo'],
                'kf':r.get('kama_fast','—'),'ks':r.get('kama_slow','—'),
                'entry':r.get('entryDate','—')})
    print("Alert rilevati: {}".format(len(alert_list)))
    if alert_list:
        send_alert_email(alert_list, vix, vstoxx, regime['regime'], now)

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
