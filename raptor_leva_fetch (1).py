#!/usr/bin/env python3
"""
RAPTOR Leva Fetch — GitHub Actions
Scarica dati per ETF leva/short/inverse + VIX/VSTOXX
Doppia KAMA (veloce=entrata, lenta=uscita) + AO veloce (EMA3-EMA13) + volume
Gira ogni 30 min 7-19 lun-ven
"""

import json, time, datetime, statistics
import yfinance as yf

# ═══════════════════════════════════════════════════════
# TICKER LEVA (243 ticker)
# ═══════════════════════════════════════════════════════
TICKERS = [
  {"t":"3SAA","y":"3SAA.MI","n":"GraniteShares 3x Short Alibaba Daily Etp","c":"Singole azioni","provider":"GraniteShares","leva":3},
  {"t":"2OIG","y":"2OIG.MI","n":"WisdomTree STOXX Europe Oil & Gas 2x Daily Short","c":"WisdomTree","provider":"WisdomTree","leva":2},
  {"t":"WDNA","y":"WDNA.MI","n":"WisdomTree BioRevolution UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"COCO","y":"COCO.MI","n":"WisdomTree Cocoa","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"AIGS","y":"AIGS.MI","n":"WisdomTree Softs","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"SEU3","y":"SEU3.L","n":"WisdomTree Short EUR Long USD 3x Daily","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"LCOC","y":"LCOC.MI","n":"WisdomTree Cocoa 2x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree","leva":2},
  {"t":"SBRT","y":"SBRT.MI","n":"WisdomTree Brent Crude Oil 1x Daily Short","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"MAGS","y":"MAGS.MI","n":"Leverage Shares -3x Short Magnificent 7 Etp","c":"Azioni Stati Uniti","provider":"Leverage Shares","leva":3},
  {"t":"3SMI","y":"3SMI.MI","n":"GraniteShares 3x Short MicroStrategy Daily Etp","c":"Singole azioni","provider":"GraniteShares","leva":3},
  {"t":"SOIL","y":"SOIL.MI","n":"WisdomTree WTI Crude Oil 1x Daily Short","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"UNH3","y":"UNH3.MI","n":"Leverage Shares 3x Long Unitedhealth (Unh) Etp Securities","c":"Singole azioni","provider":"Leverage Shares","leva":3},
  {"t":"3BRS","y":"3BRS.MI","n":"WisdomTree Brent Crude Oil 3x Daily Short","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"USP3","y":"USP3.L","n":"WisdomTree Long USD Short GBP 3x Daily","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"SMST","y":"SMST.MI","n":"Leverage Shares -3x Short MicroStrategy Etp","c":"Singole azioni","provider":"Leverage Shares","leva":3},
  {"t":"DHSA","y":"DHSA.MI","n":"WisdomTree US Equity Income UCITS ETF - Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3SMS","y":"3SMS.MI","n":"GraniteShares 3x Short Microsoft Daily Etp","c":"Singole azioni","provider":"GraniteShares","leva":3},
  {"t":"3TYL","y":"3TYL.MI","n":"WisdomTree US Treasuries 10Y 3x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"1PAS","y":"1PAS.MI","n":"WisdomTree Palladium 1x Daily Short","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3USS","y":"3USS.MI","n":"WisdomTree S&P 500 3x Daily Short","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"3SNV","y":"3SNV.MI","n":"GraniteShares 3x Short NVIDIA Daily Etp","c":"Singole azioni","provider":"GraniteShares","leva":3},
  {"t":"3SAP","y":"3SAP.MI","n":"GraniteShares 3x Short Apple Daily Etp","c":"Singole azioni","provider":"GraniteShares","leva":3},
  {"t":"3MRN","y":"3MRN.MI","n":"Leverage Shares 3x Long Moderna Etp Securities","c":"Singole azioni","provider":"Leverage Shares","leva":3},
  {"t":"SNV3","y":"SNV3.MI","n":"Leverage Shares -3x Short NVIDIA Etp Securities","c":"Singole azioni","provider":"Leverage Shares","leva":3},
  {"t":"DHS","y":"DHS.MI","n":"WisdomTree US Equity Income UCITS ETF","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3LSQ","y":"3LSQ.MI","n":"GraniteShares 3x Long Square Daily Etp","c":"Singole azioni","provider":"GraniteShares","leva":3},
  {"t":"AIGL","y":"AIGL.MI","n":"WisdomTree Livestock","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"XUSA","y":"XUSA.MI","n":"WisdomTree Global Ex-USA Quality Dividend Growth UCITS ETF - EUR Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"CHE3","y":"CHE3.MI","n":"WisdomTree Short CHF Long EUR 3x Daily","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"3LMO","y":"3LMO.MI","n":"GraniteShares 3x Long Moderna Daily Etp","c":"Singole azioni","provider":"GraniteShares","leva":3},
  {"t":"EUGB","y":"EUGB.MI","n":"WisdomTree Long GBP Short EUR","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"5USS","y":"5USS.MI","n":"WisdomTree S&P 500 5x Daily Short","c":"WisdomTree","provider":"WisdomTree","leva":5},
  {"t":"SEUR","y":"SEUR.L","n":"WisdomTree Short EUR Long USD","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"GPTS","y":"GPTS.MI","n":"Leverage Shares -3x Short Artificial Intelligence (AI) Etp","c":"Azioni Stati Uniti","provider":"Leverage Shares","leva":3},
  {"t":"GGRW","y":"GGRW.MI","n":"WisdomTree Global Quality Dividend Growth UCITS ETF - USD","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"NTSG","y":"NTSG.MI","n":"WisdomTree Global Efficient Core UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"ENGS","y":"ENGS.MI","n":"WisdomTree Natural Gas - EUR Daily Hedged","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"SBA3","y":"SBA3.MI","n":"Leverage Shares -3x Short Alibaba Etp Securities","c":"Singole azioni","provider":"Leverage Shares","leva":3},
  {"t":"3SNI","y":"3SNI.MI","n":"GraniteShares 3x Short NIO Daily Etp","c":"Singole azioni","provider":"GraniteShares","leva":3},
  {"t":"AIGA","y":"AIGA.MI","n":"WisdomTree Agriculture","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"SGBP","y":"SGBP.L","n":"WisdomTree Short GBP Long USD","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3RAC","y":"3RAC.MI","n":"Leverage Shares 3x Long Ferrari (RACE) Etp","c":"Singole azioni","provider":"Leverage Shares","leva":3},
  {"t":"NGAS","y":"NGAS.MI","n":"WisdomTree Natural Gas","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3BUL","y":"3BUL.MI","n":"WisdomTree Bund 10Y 3x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"DGRA","y":"DGRA.MI","n":"WisdomTree US Quality Dividend Growth UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"CCBO","y":"CCBO.MI","n":"WisdomTree AT1 CoCo Bond UCITS ETF - USD","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3OIS","y":"3OIS.MI","n":"WisdomTree WTI Crude Oil 3x Daily Short","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"SFNG","y":"SFNG.MI","n":"GraniteShares 1x Short Faang Etp","c":"Azioni Stati Uniti","provider":"GraniteShares","leva":1},
  {"t":"EPI","y":"EPI.MI","n":"WisdomTree India Earnings UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"SEEU","y":"SEEU.MI","n":"WisdomTree Short SEK Long EUR","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"GAS","y":"GAS.MI","n":"Leverage Shares Natural Gas Etc","c":"Energia","provider":"Leverage Shares","leva":1},
  {"t":"CHGB","y":"CHGB.L","n":"WisdomTree Short CHF Long GBP","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"USFR","y":"USFR.L","n":"WisdomTree USD Floating Rate Treasury Bond UCITS ETF - USD","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"EUUS","y":"EUUS.MI","n":"WisdomTree Long USD Short EUR","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"EUS5","y":"EUS5.MI","n":"WisdomTree Long USD Short EUR 5x Daily","c":"WisdomTree","provider":"WisdomTree","leva":5},
  {"t":"SOYB","y":"SOYB.MI","n":"WisdomTree Soybeans","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"GGRB","y":"GGRB.L","n":"WisdomTree Global Quality Dividend Growth UCITS ETF - GBP Hedged","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"PCRD","y":"PCRD.L","n":"WisdomTree WTI Crude Oil - GBP Daily Hedged","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"SSIL","y":"SSIL.MI","n":"WisdomTree Silver 1x Daily Short","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"DHSG","y":"DHSG.L","n":"WisdomTree US Equity Income UCITS ETF - GBP Hedged Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"DHSF","y":"DHSF.MI","n":"WisdomTree US Equity Income UCITS ETF - EUR Hedged Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"EUS3","y":"EUS3.MI","n":"WisdomTree Long USD Short EUR 3x Daily","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"CODO","y":"CODO.L","n":"WisdomTree AT1 CoCo Bond UCITS ETF - USD Hedged","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"PBRT","y":"PBRT.L","n":"WisdomTree Brent Crude Oil - GBP Daily Hedged","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"QS5S","y":"QS5S.MI","n":"WisdomTree NASDAQ 100 5x Daily Short","c":"WisdomTree","provider":"WisdomTree","leva":5},
  {"t":"HEDF","y":"HEDF.MI","n":"WisdomTree Europe Equity UCITS ETF - EUR Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"TFRN","y":"TFRN.MI","n":"WisdomTree USD Floating Rate Treasury Bond UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3BTL","y":"3BTL.MI","n":"WisdomTree BTP 10Y 3x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"GBUS","y":"GBUS.L","n":"WisdomTree Long USD Short GBP","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"2UKL","y":"2UKL.L","n":"WisdomTree FTSE 100 2x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree","leva":2},
  {"t":"EJP3","y":"EJP3.MI","n":"WisdomTree Long JPY Short EUR 3x Daily","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"2TRV","y":"2TRV.MI","n":"WisdomTree STOXX Europe Travel & Leisure 2x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree","leva":2},
  {"t":"S3CO","y":"S3CO.MI","n":"Leverage Shares -3x Short Coinbase Etp","c":"Singole azioni","provider":"Leverage Shares","leva":3},
  {"t":"WTVE","y":"WTVE.MI","n":"WisdomTree Europe Value UCITS ETF - EUR Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3BAL","y":"3BAL.MI","n":"WisdomTree EURO STOXX Banks 3x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"SNIK","y":"SNIK.MI","n":"WisdomTree Nickel 1x Daily Short","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"ESOY","y":"ESOY.MI","n":"WisdomTree Soybeans - EUR Daily Hedged","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"CARB","y":"CARB.MI","n":"WisdomTree Carbon","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"LCFE","y":"LCFE.MI","n":"WisdomTree Coffee 2x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree","leva":2},
  {"t":"3SIS","y":"3SIS.MI","n":"WisdomTree Silver 3x Daily Short","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"COFF","y":"COFF.MI","n":"WisdomTree Coffee","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"HEDS","y":"HEDS.L","n":"WisdomTree Europe Equity UCITS ETF - USD Hedged Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"QQQS","y":"QQQS.MI","n":"WisdomTree NASDAQ 100 3x Daily Short","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"DGRP","y":"DGRP.L","n":"WisdomTree US Quality Dividend Growth UCITS ETF - USD","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"SJPY","y":"SJPY.L","n":"WisdomTree Short JPY Long USD","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"USGB","y":"USGB.L","n":"WisdomTree Short USD Long GBP","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3SAL","y":"3SAL.MI","n":"GraniteShares 3x Short Alphabet Daily Etp","c":"Singole azioni","provider":"GraniteShares","leva":3},
  {"t":"WTIG","y":"WTIG.DE","n":"WisdomTree AT1 CoCo Bond UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3CFL","y":"3CFL.MI","n":"WisdomTree Coffee 3x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"WRTY","y":"WRTY.MI","n":"WisdomTree Russell 2000","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"ECOF","y":"ECOF.MI","n":"WisdomTree Coffee - EUR Daily Hedged","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"COBO","y":"COBO.MI","n":"WisdomTree AT1 CoCo Bond UCITS ETF - EUR Hedged","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"GGRA","y":"GGRA.MI","n":"WisdomTree Global Quality Dividend Growth UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3HCS","y":"3HCS.MI","n":"WisdomTree Copper 3x Daily Short","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"SBUL","y":"SBUL.MI","n":"WisdomTree Gold 1x Daily Short","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"LSUG","y":"LSUG.MI","n":"WisdomTree Sugar 2x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree","leva":2},
  {"t":"CORN","y":"CORN.MI","n":"WisdomTree Corn","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"GBSP","y":"GBSP.L","n":"WisdomTree Physical Gold - GBP Daily Hedged","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3SPA","y":"3SPA.MI","n":"GraniteShares 3x Short Palantir Daily Etp","c":"Singole azioni","provider":"GraniteShares","leva":3},
  {"t":"SIMT","y":"SIMT.MI","n":"WisdomTree Industrial Metals 1x Daily Short","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"SUGA","y":"SUGA.MI","n":"WisdomTree Sugar","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"SCOP","y":"SCOP.MI","n":"WisdomTree Copper 1x Daily Short","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3GIL","y":"3GIL.L","n":"WisdomTree Gilts 10Y 3x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"XBJF","y":"XBJF.DE","n":"WisdomTree Short CNY Long USD","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3TYS","y":"3TYS.MI","n":"WisdomTree US Treasuries 10Y 3x Daily Short","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"EUJP","y":"EUJP.MI","n":"WisdomTree Long JPY Short EUR","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3GOS","y":"3GOS.MI","n":"WisdomTree Gold 3x Daily Short","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"WS5X","y":"WS5X.MI","n":"WisdomTree EURO STOXX 50","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3PYP","y":"3PYP.MI","n":"Leverage Shares 3x PayPal Etp Securities","c":"Singole azioni","provider":"Leverage Shares","leva":3},
  {"t":"3CAC","y":"3CAC.PA","n":"WisdomTree CAC 40 3x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"PIMT","y":"PIMT.L","n":"WisdomTree Industrial Metals - GBP Daily Hedged","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"SGB3","y":"SGB3.L","n":"WisdomTree Short GBP Long USD 3x Daily","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"TSLQ","y":"TSLQ.MI","n":"Leverage Shares -3x Short Tesla Etp Securities","c":"Singole azioni","provider":"Leverage Shares","leva":3},
  {"t":"DXJZ","y":"DXJZ.MI","n":"WisdomTree Japan Equity UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"PUS3","y":"PUS3.L","n":"WisdomTree Short USD Long GBP 3x Daily","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"GBJP","y":"GBJP.L","n":"WisdomTree Long JPY Short GBP","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3EMS","y":"3EMS.MI","n":"WisdomTree Emerging Markets 3x Daily Short","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"COGO","y":"COGO.L","n":"WisdomTree AT1 CoCo Bond UCITS ETF - GBP Hedged","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"LCOR","y":"LCOR.MI","n":"WisdomTree Corn 2x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree","leva":2},
  {"t":"3SFB","y":"3SFB.MI","n":"GraniteShares 3x Short Facebook Daily Etp","c":"Singole azioni","provider":"GraniteShares","leva":3},
  {"t":"3STS","y":"3STS.MI","n":"GraniteShares 3x Short Tesla Daily Etp","c":"Singole azioni","provider":"GraniteShares","leva":3},
  {"t":"SJP3","y":"SJP3.L","n":"WisdomTree Short JPY Long USD 3x Daily","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"3SZN","y":"3SZN.MI","n":"GraniteShares 3x Short Amazon Daily Etp","c":"Singole azioni","provider":"GraniteShares","leva":3},
  {"t":"LNGA","y":"LNGA.MI","n":"WisdomTree Natural Gas 2x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"COBA","y":"COBA.MI","n":"WisdomTree AT1 CoCo Bond UCITS ETF - EUR Hedged Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3NGL","y":"3NGL.MI","n":"WisdomTree Natural Gas 3x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"2MCL","y":"2MCL.L","n":"WisdomTree FTSE 250 2x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree","leva":2},
  {"t":"WSDG","y":"WSDG.MI","n":"WisdomTree Global Sustainable Equity UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3UBR","y":"3UBR.MI","n":"Leverage Shares 3x Uber Etp Securities","c":"Singole azioni","provider":"Leverage Shares","leva":3},
  {"t":"LAGR","y":"LAGR.MI","n":"WisdomTree Agriculture 2x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree","leva":2},
  {"t":"HEDJ","y":"HEDJ.MI","n":"WisdomTree Europe Equity UCITS ETF - USD Hedged","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3M7S","y":"3M7S.MI","n":"WisdomTree Magnificent 7 3x Daily Short","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"WCCA","y":"WCCA.MI","n":"WisdomTree California Carbon","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3SUL","y":"3SUL.MI","n":"WisdomTree Sugar 3x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"NOEU","y":"NOEU.MI","n":"WisdomTree Short NOK Long EUR","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"SALL","y":"SALL.MI","n":"WisdomTree Broad Commodities 1x Daily Short","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"NTSX","y":"NTSX.MI","n":"WisdomTree US Efficient Core UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"CRRE","y":"CRRE.MI","n":"WisdomTree Enhanced Commodity Carry - EUR Daily Hedged","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"WCBR","y":"WCBR.MI","n":"WisdomTree Cybersecurity UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"CRRY","y":"CRRY.MI","n":"WisdomTree Enhanced Commodity Carry","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3LPP","y":"3LPP.MI","n":"GraniteShares 3x Long PayPal Daily Etp","c":"Singole azioni","provider":"GraniteShares","leva":3},
  {"t":"SQQQ","y":"SQQQ.MI","n":"Leverage Shares -5x Short Nasdaq 100 Etp","c":"Azioni Stati Uniti","provider":"Leverage Shares","leva":5},
  {"t":"3SQ","y":"3SQ.MI","n":"Leverage Shares 3x Square Etp Securities","c":"Singole azioni","provider":"Leverage Shares","leva":3},
  {"t":"EGB3","y":"EGB3.MI","n":"WisdomTree Long GBP Short EUR 3x Daily","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"3CAS","y":"3CAS.PA","n":"WisdomTree CAC 40 3x Daily Short","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"3AMD","y":"3AMD.MI","n":"Leverage Shares 3x AMD Etp Securities","c":"Singole azioni","provider":"Leverage Shares","leva":3},
  {"t":"3SNF","y":"3SNF.MI","n":"GraniteShares 3x Short Netflix Daily Etp","c":"Singole azioni","provider":"GraniteShares","leva":3},
  {"t":"ESUG","y":"ESUG.MI","n":"WisdomTree Sugar - EUR Daily Hedged","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"DXJD","y":"DXJD.SW","n":"WisdomTree Japan Equity UCITS ETF - CHF Hedged Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"FANG","y":"FANG.MI","n":"GraniteShares Faang Etp","c":"Azioni Stati Uniti","provider":"GraniteShares","leva":1},
  {"t":"WTVG","y":"WTVG.MI","n":"WisdomTree Global Value UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"CHEU","y":"CHEU.MI","n":"WisdomTree Short CHF Long EUR","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"DXJA","y":"DXJA.L","n":"WisdomTree Japan Equity UCITS ETF - USD Hedged Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3LAM","y":"3LAM.MI","n":"GraniteShares 3x Long AMD Daily Etp","c":"Singole azioni","provider":"GraniteShares","leva":3},
  {"t":"3SCR","y":"3SCR.MI","n":"GraniteShares 3x Short Unicredit Daily Etp","c":"Singole azioni","provider":"GraniteShares","leva":3},
  {"t":"DXJP","y":"DXJP.L","n":"WisdomTree Japan Equity UCITS ETF - GBP Hedged","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"EEI","y":"EEI.MI","n":"WisdomTree Europe Equity Income UCITS ETF","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"WADA","y":"WADA.AS","n":"WisdomTree Physical Cardano","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3LSP","y":"3LSP.MI","n":"GraniteShares 3x Long Intesa Sanpaolo Daily Etp","c":"Singole azioni","provider":"GraniteShares","leva":3},
  {"t":"DXJ","y":"DXJ.MI","n":"WisdomTree Japan Equity UCITS ETF - USD Hedged","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3BAS","y":"3BAS.MI","n":"WisdomTree EURO STOXX Banks 3x Daily Short","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"3EUL","y":"3EUL.MI","n":"WisdomTree EURO STOXX 50® 3x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"HIM3","y":"HIM3.MI","n":"Leverage Shares 3x Long Hims & Hers Health Etp","c":"Singole azioni","provider":"Leverage Shares","leva":3},
  {"t":"DGRW","y":"DGRW.L","n":"WisdomTree US Quality Dividend Growth UCITS ETF - USD","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3EDS","y":"3EDS.MI","n":"WisdomTree STOXX Europe Aerospace & Defence 3x Daily Short","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"NTSZ","y":"NTSZ.MI","n":"WisdomTree Eurozone Efficient Core UCITS ETF - EUR Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"DXJF","y":"DXJF.MI","n":"WisdomTree Japan Equity UCITS ETF - EUR Hedged Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3LCR","y":"3LCR.MI","n":"GraniteShares 3x Long Unicredit Daily Etp","c":"Singole azioni","provider":"GraniteShares","leva":3},
  {"t":"WCLD","y":"WCLD.MI","n":"WisdomTree Cloud Computing UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"EGRP","y":"EGRP.L","n":"WisdomTree Eurozone Quality Dividend Growth UCITS ETF - EUR","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"EGRW","y":"EGRW.L","n":"WisdomTree Eurozone Quality Dividend Growth UCITS ETF - EUR","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"GGRE","y":"GGRE.MI","n":"WisdomTree Global Quality Dividend Growth UCITS ETF - EUR Hedged Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"WDOT","y":"WDOT.AS","n":"WisdomTree Physical Polkadot","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"2STR","y":"2STR.MI","n":"WisdomTree STOXX Europe Travel & Leisure 2x Daily Short","c":"WisdomTree","provider":"WisdomTree","leva":2},
  {"t":"EEIA","y":"EEIA.MI","n":"WisdomTree Europe Equity Income UCITS ETF Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"XSOE","y":"XSOE.MI","n":"WisdomTree Emerging Markets ex-State-Owned Enterprises UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"USEU","y":"USEU.MI","n":"WisdomTree Short USD Long EUR","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3NFL","y":"3NFL.MI","n":"Leverage Shares 3x Netflix Etp Securities","c":"Singole azioni","provider":"Leverage Shares","leva":3},
  {"t":"5EUL","y":"5EUL.MI","n":"WisdomTree EURO STOXX 50 5x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree","leva":5},
  {"t":"WTI","y":"WTI.MI","n":"Leverage Shares Wti Oil Etc","c":"Energia","provider":"Leverage Shares","leva":1},
  {"t":"HEDK","y":"HEDK.L","n":"WisdomTree Europe Equity UCITS ETF - USD Hedged Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"JPE3","y":"JPE3.MI","n":"WisdomTree Short JPY Long EUR 3x Daily","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"HEDP","y":"HEDP.L","n":"WisdomTree Europe Equity UCITS ETF - GBP Hedged","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"WAXG","y":"WAXG.DE","n":"WisdomTree Enhanced Commodity ex-Agriculture UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"HOGS","y":"HOGS.MI","n":"WisdomTree Lean Hogs","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"1GIS","y":"1GIS.L","n":"WisdomTree Gilts 10Y 1x Daily Short","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"SLVR","y":"SLVR.MI","n":"WisdomTree Silver","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3LAA","y":"3LAA.MI","n":"GraniteShares 3x Long Alibaba Daily Etp","c":"Singole azioni","provider":"GraniteShares","leva":3},
  {"t":"3LMI","y":"3LMI.MI","n":"GraniteShares 3x Long MicroStrategy Daily Etp","c":"Singole azioni","provider":"GraniteShares","leva":3},
  {"t":"EUAU","y":"EUAU.MI","n":"WisdomTree Long AUD Short EUR","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3UKL","y":"3UKL.L","n":"WisdomTree FTSE 100 3x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"ENIK","y":"ENIK.MI","n":"WisdomTree Nickel - EUR Daily Hedged","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"USE5","y":"USE5.MI","n":"WisdomTree Short USD Long EUR 5x Daily","c":"WisdomTree","provider":"WisdomTree","leva":5},
  {"t":"LJP3","y":"LJP3.L","n":"WisdomTree Long JPY Short USD 3x Daily","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"JPGB","y":"JPGB.L","n":"WisdomTree Short JPY Long GBP","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"WTRE","y":"WTRE.MI","n":"WisdomTree New Economy Real Estate UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3LMS","y":"3LMS.MI","n":"GraniteShares 3x Long Microsoft Daily Etp","c":"Singole azioni","provider":"GraniteShares","leva":3},
  {"t":"UGAS","y":"UGAS.MI","n":"WisdomTree Gasoline","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"ECRN","y":"ECRN.MI","n":"WisdomTree Corn - EUR Daily Hedged","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3MST","y":"3MST.MI","n":"Leverage Shares 3x Long MicroStrategy Etp","c":"Singole azioni","provider":"Leverage Shares","leva":3},
  {"t":"3BRL","y":"3BRL.MI","n":"WisdomTree Brent Crude Oil 3x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"INTS","y":"INTS.MI","n":"Leverage Shares -3x Short Intel (Intc) Etp Securities","c":"Singole azioni","provider":"Leverage Shares","leva":3},
  {"t":"WNER","y":"WNER.MI","n":"WisdomTree New Economy Real Estate UCITS ETF - USD","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"ZINC","y":"ZINC.MI","n":"WisdomTree Zinc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"WCOE","y":"WCOE.MI","n":"WisdomTree Enhanced Commodity UCITS ETF - EUR Hedged Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"LGB3","y":"LGB3.L","n":"WisdomTree Long GBP Short USD 3x Daily","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"3LNF","y":"3LNF.MI","n":"GraniteShares 3x Long Netflix Daily Etp","c":"Singole azioni","provider":"GraniteShares","leva":3},
  {"t":"DEMR","y":"DEMR.MI","n":"WisdomTree Emerging Markets Equity Income UCITS ETF - Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"URGB","y":"URGB.L","n":"WisdomTree Short EUR Long GBP","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"JPEU","y":"JPEU.MI","n":"WisdomTree Short JPY Long EUR","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3LNI","y":"3LNI.MI","n":"GraniteShares 3x Long NIO Daily Etp","c":"Singole azioni","provider":"GraniteShares","leva":3},
  {"t":"WWRD","y":"WWRD.MI","n":"WisdomTree World","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"SC3S","y":"SC3S.MI","n":"WisdomTree PHLX Semiconductor 3x Daily Short","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"3SSP","y":"3SSP.MI","n":"GraniteShares 3x Short Intesa Sanpaolo Daily Etp","c":"Singole azioni","provider":"GraniteShares","leva":3},
  {"t":"WCOM","y":"WCOM.L","n":"WisdomTree Enhanced Commodity UCITS ETF - GBP Hedged Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3ITL","y":"3ITL.MI","n":"WisdomTree FTSE MIB 3x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"2UKS","y":"2UKS.L","n":"WisdomTree FTSE 100 2x Daily Short","c":"WisdomTree","provider":"WisdomTree","leva":2},
  {"t":"FCRU","y":"FCRU.MI","n":"WisdomTree WTI Crude Oil Longer Dated","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"5ITL","y":"5ITL.MI","n":"WisdomTree FTSE MIB 5x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree","leva":5},
  {"t":"3BAB","y":"3BAB.MI","n":"Leverage Shares 3x Alibaba Etp Securities","c":"Singole azioni","provider":"Leverage Shares","leva":3},
  {"t":"WTAI","y":"WTAI.MI","n":"WisdomTree Artificial Intelligence UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"WENP","y":"WENP.L","n":"WisdomTree Strategic Metals UCITS ETF - GBP Hedged","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"WMIB","y":"WMIB.MI","n":"WisdomTree FTSE MIB","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"DGRB","y":"DGRB.L","n":"WisdomTree US Quality Dividend Growth UCITS ETF - GBP Hedged","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3DES","y":"3DES.MI","n":"WisdomTree DAX 3x Daily Short","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"EXAG","y":"EXAG.DE","n":"WisdomTree Enhanced Commodity ex-Agriculture UCITS ETF - EUR Hedged Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"LEUR","y":"LEUR.L","n":"WisdomTree Long EUR Short USD","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"WCOG","y":"WCOG.L","n":"WisdomTree Enhanced Commodity UCITS ETF USD","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3SIL","y":"3SIL.MI","n":"WisdomTree Silver 3x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"GBUR","y":"GBUR.L","n":"WisdomTree Long EUR Short GBP","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"DFE","y":"DFE.MI","n":"WisdomTree Europe SmallCap Dividend UCITS ETF","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"DGSE","y":"DGSE.MI","n":"WisdomTree Emerging Markets SmallCap Dividend UCITS ETF","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3OIL","y":"3OIL.MI","n":"WisdomTree WTI Crude Oil 3x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"HOD3","y":"HOD3.MI","n":"Leverage Shares 3x Long Robinhood (Hood) Etp Securities","c":"Singole azioni","provider":"Leverage Shares","leva":3},
  {"t":"USE3","y":"USE3.MI","n":"WisdomTree Short USD Long EUR 3x Daily","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"EGRA","y":"EGRA.MI","n":"WisdomTree Eurozone Quality Dividend Growth UCITS ETF - EUR Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"LJPY","y":"LJPY.L","n":"WisdomTree Long JPY Short USD","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"2CAR","y":"2CAR.MI","n":"WisdomTree STOXX Europe Automobiles 2x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree","leva":2},
  {"t":"LGBP","y":"LGBP.L","n":"WisdomTree Long GBP Short USD","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"GBE3","y":"GBE3.MI","n":"WisdomTree Short GBP Long EUR 3x Daily","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"1MCS","y":"1MCS.L","n":"WisdomTree FTSE 250 1x Daily Short","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"GBEU","y":"GBEU.MI","n":"WisdomTree Short GBP Long EUR","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"EALU","y":"EALU.MI","n":"WisdomTree Aluminium - EUR Daily Hedged","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"LPLA","y":"LPLA.MI","n":"WisdomTree Platinum 2x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree","leva":2},
  {"t":"AUEU","y":"AUEU.MI","n":"WisdomTree Short AUD Long EUR","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"LBRT","y":"LBRT.MI","n":"WisdomTree Brent Crude Oil 2x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree","leva":2},
  {"t":"3SSQ","y":"3SSQ.MI","n":"GraniteShares 3x Short Square Daily Etp","c":"Singole azioni","provider":"GraniteShares","leva":3},
  {"t":"WTVU","y":"WTVU.MI","n":"WisdomTree US Value UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"EFCM","y":"EFCM.MI","n":"WisdomTree Broad Commodities Longer Dated - EUR Daily Hedged","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"LALU","y":"LALU.MI","n":"WisdomTree Aluminium 2x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree","leva":2},
  {"t":"3NIO","y":"3NIO.MI","n":"Leverage Shares 3x NIO Etp Securities","c":"Singole azioni","provider":"Leverage Shares","leva":3},
  {"t":"CRRP","y":"CRRP.L","n":"WisdomTree Enhanced Commodity Carry - GBP Daily Hedged","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"BRENT","y":"BRENT.MI","n":"Leverage Shares Brent Oil Etc","c":"Energia","provider":"Leverage Shares","leva":1},
  {"t":"SOXS","y":"SOXS.MI","n":"Leverage Shares -4x Short Semiconductors Etp","c":"Paniere di azioni","provider":"Leverage Shares","leva":4},
  {"t":"EIMT","y":"EIMT.MI","n":"WisdomTree Industrial Metals - EUR Daily Hedged","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"LSIL","y":"LSIL.MI","n":"WisdomTree Silver 2x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree","leva":2},
  {"t":"AIGC","y":"AIGC.MI","n":"WisdomTree Broad Commodities","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"VOLT","y":"VOLT.MI","n":"WisdomTree Battery Solutions UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"SOYO","y":"SOYO.MI","n":"WisdomTree Soybean Oil","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"EUSE","y":"EUSE.MI","n":"WisdomTree Long SEK Short EUR","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"EUNO","y":"EUNO.MI","n":"WisdomTree Long NOK Short EUR","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"ALUM","y":"ALUM.MI","n":"WisdomTree Aluminium","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"PCOM","y":"PCOM.MI","n":"WisdomTree Broad Commodities UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"PHAG","y":"PHAG.MI","n":"WisdomTree Physical Silver","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"COMS","y":"COMS.SW","n":"WisdomTree Enhanced Commodity UCITS ETF - CHF Hedged Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"WENH","y":"WENH.DE","n":"WisdomTree Strategic Metals UCITS ETF - EUR Hedged Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"EUCH","y":"EUCH.MI","n":"WisdomTree Long CHF Short EUR","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"BRNT","y":"BRNT.MI","n":"WisdomTree Brent Crude Oil","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3SMO","y":"3SMO.MI","n":"GraniteShares 3x Short Moderna Daily Etp","c":"Singole azioni","provider":"GraniteShares","leva":3},
  {"t":"UGRW","y":"UGRW.L","n":"WisdomTree UK Quality Dividend Growth UCITS ETF - GBP","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"WENG","y":"WENG.L","n":"WisdomTree Strategic Metals UCITS ETF - GBP Hedged Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3AMZ","y":"3AMZ.MI","n":"Leverage Shares 3x Amazon Etp Securities","c":"Singole azioni","provider":"Leverage Shares","leva":3},
  {"t":"3GIS","y":"3GIS.L","n":"WisdomTree Gilts 10Y 3x Daily Short","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"GBSE","y":"GBSE.MI","n":"WisdomTree Physical Gold - EUR Daily Hedged","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"AIGG","y":"AIGG.MI","n":"WisdomTree Grains","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"WTID","y":"WTID.MI","n":"WisdomTree Bloomberg WTI Crude Oil","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3SEM","y":"3SEM.MI","n":"WisdomTree PHLX Semiconductor 3x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"3GOL","y":"3GOL.MI","n":"WisdomTree Gold 3x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"LBUL","y":"LBUL.MI","n":"WisdomTree Gold 2x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree","leva":2},
  {"t":"AIGI","y":"AIGI.MI","n":"WisdomTree Industrial Metals","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"5BTS","y":"5BTS.MI","n":"WisdomTree BTP 10Y 5x Daily Short","c":"WisdomTree","provider":"WisdomTree","leva":5},
  {"t":"EUP3","y":"EUP3.L","n":"WisdomTree Long EUR Short GBP 3x Daily","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"3MSF","y":"3MSF.MI","n":"Leverage Shares 3x Microsoft Etp Securities","c":"Singole azioni","provider":"Leverage Shares","leva":3},
  {"t":"5TYS","y":"5TYS.MI","n":"WisdomTree US Treasuries 10Y 5x Daily Short","c":"WisdomTree","provider":"WisdomTree","leva":5},
  {"t":"BLOC","y":"BLOC.PA","n":"WisdomTree Physical Crypto Mega Cap","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3EML","y":"3EML.MI","n":"WisdomTree Emerging Markets 3x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"WSLV","y":"WSLV.MI","n":"WisdomTree Core Physical Silver","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"LNIK","y":"LNIK.MI","n":"WisdomTree Nickel 2x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree","leva":2},
  {"t":"ESVR","y":"ESVR.MI","n":"WisdomTree Silver - EUR Daily Hedged","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"LCOP","y":"LCOP.MI","n":"WisdomTree Copper 2x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree","leva":2},
  {"t":"LEAD","y":"LEAD.MI","n":"WisdomTree Lead","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"5EUS","y":"5EUS.MI","n":"WisdomTree EURO STOXX 50 5x Daily Short","c":"WisdomTree","provider":"WisdomTree","leva":5},
  {"t":"LOIL","y":"LOIL.MI","n":"WisdomTree WTI Crude Oil 2x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree","leva":2},
  {"t":"UL3S","y":"UL3S.MI","n":"WisdomTree US Treasuries 30Y 3x Daily Short","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"PHPT","y":"PHPT.MI","n":"WisdomTree Physical Platinum","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"EBUL","y":"EBUL.MI","n":"WisdomTree Gold - EUR Daily Hedged","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3LPA","y":"3LPA.MI","n":"GraniteShares 3x Long Palantir Daily Etp","c":"Singole azioni","provider":"GraniteShares","leva":3},
  {"t":"5SPY","y":"5SPY.MI","n":"Leverage Shares 5x Long S&P 500 Etp","c":"Azioni Stati Uniti","provider":"Leverage Shares","leva":5},
  {"t":"HEDD","y":"HEDD.SW","n":"WisdomTree Europe Equity UCITS ETF - CHF Hedged Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"COPR","y":"COPR.L","n":"WisdomTree Copper IE","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"ECOP","y":"ECOP.MI","n":"WisdomTree Copper - EUR Daily Hedged","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"CPER","y":"CPER.MI","n":"Leverage Shares Copper Etc","c":"Metalli industriali","provider":"Leverage Shares","leva":1},
  {"t":"CRUD","y":"CRUD.MI","n":"WisdomTree WTI Crude Oil","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"BENE","y":"BENE.MI","n":"WisdomTree Energy Enhanced","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"EWAT","y":"EWAT.MI","n":"WisdomTree Wheat - EUR Daily Hedged","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"VIXL","y":"VIXL.MI","n":"WisdomTree S&P 500 VIX Short-Term Futures 2.25x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"WDEF","y":"WDEF.MI","n":"WisdomTree Europe Defence UCITS ETF - EUR Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"PHPD","y":"PHPD.MI","n":"WisdomTree Physical Palladium","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"WCOA","y":"WCOA.MI","n":"WisdomTree Enhanced Commodity UCITS ETF USD Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"PHPM","y":"PHPM.MI","n":"WisdomTree Physical Precious Metals","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"BRND","y":"BRND.MI","n":"WisdomTree Bloomberg Brent Crude Oil","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3HCL","y":"3HCL.MI","n":"WisdomTree Copper 3x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"3BUS","y":"3BUS.MI","n":"WisdomTree Bund 10Y 3x Daily Short","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"3AAP","y":"3AAP.MI","n":"Leverage Shares 3x Apple Etp Securities","c":"Singole azioni","provider":"Leverage Shares","leva":3},
  {"t":"COPA","y":"COPA.MI","n":"WisdomTree Copper","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"EBRT","y":"EBRT.MI","n":"WisdomTree Brent Crude Oil - EUR Daily Hedged","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3LCO","y":"3LCO.MI","n":"GraniteShares 3x Long Coinbase Daily Etp","c":"Singole azioni","provider":"GraniteShares","leva":3},
  {"t":"NICK","y":"NICK.MI","n":"WisdomTree Nickel","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"2PAL","y":"2PAL.MI","n":"WisdomTree Palladium 2x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree","leva":2},
  {"t":"3MG7","y":"3MG7.MI","n":"WisdomTree Magnificent 7 3x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"WGLD","y":"WGLD.MI","n":"WisdomTree Core Physical Gold","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"TTFW","y":"TTFW.MI","n":"WisdomTree European Natural Gas","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"AIGP","y":"AIGP.MI","n":"WisdomTree Precious Metals","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"SGBS","y":"SGBS.MI","n":"WisdomTree Physical Swiss Gold","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3TSL","y":"3TSL.MI","n":"Leverage Shares 3x Tesla Etp","c":"Singole azioni","provider":"Leverage Shares","leva":3},
  {"t":"TINM","y":"TINM.MI","n":"WisdomTree Tin","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3LTS","y":"3LTS.MI","n":"GraniteShares 3x Long Tesla Daily Etp","c":"Singole azioni","provider":"GraniteShares","leva":3},
  {"t":"AIGO","y":"AIGO.MI","n":"WisdomTree Petroleum","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"ECRD","y":"ECRD.MI","n":"WisdomTree WTI Crude Oil - EUR Daily Hedged","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3LNV","y":"3LNV.MI","n":"GraniteShares 3x Long NVIDIA Daily Etp","c":"Singole azioni","provider":"GraniteShares","leva":3},
  {"t":"3ITS","y":"3ITS.MI","n":"WisdomTree FTSE MIB 3x Daily Short","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"GBE5","y":"GBE5.MI","n":"WisdomTree Short GBP Long EUR 5x Daily","c":"WisdomTree","provider":"WisdomTree","leva":5},
  {"t":"AIGE","y":"AIGE.MI","n":"WisdomTree Energy","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"WATT","y":"WATT.MI","n":"WisdomTree Battery Metals","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3NVD","y":"3NVD.MI","n":"Leverage Shares 3x NVIDIA Etp Securities","c":"Singole azioni","provider":"Leverage Shares","leva":3},
  {"t":"WNRG","y":"WNRG.DE","n":"WisdomTree Energy Enhanced - EUR Daily Hedged","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3EUS","y":"3EUS.MI","n":"WisdomTree EURO STOXX 50® 3x Daily Short","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"BULL","y":"BULL.MI","n":"WisdomTree Gold","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"LPET","y":"LPET.MI","n":"WisdomTree Petroleum 2x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree","leva":2},
  {"t":"3CON","y":"3CON.MI","n":"Leverage Shares 3x Long Coinbase Etp Securities","c":"Singole azioni","provider":"Leverage Shares","leva":3},
  {"t":"3BTS","y":"3BTS.MI","n":"WisdomTree BTP 10Y 3x Daily Short","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"SUP3","y":"SUP3.L","n":"WisdomTree Short EUR Long GBP 3x Daily","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"3NGS","y":"3NGS.MI","n":"WisdomTree Natural Gas 3x Daily Short","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"WRNW","y":"WRNW.MI","n":"WisdomTree Renewable Energy UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"ECH3","y":"ECH3.MI","n":"WisdomTree Long CHF Short EUR 3x Daily","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"3UBS","y":"3UBS.MI","n":"WisdomTree Bund 30Y 3x Daily Short","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"WENT","y":"WENT.MI","n":"WisdomTree Energy Transition Metals","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"WPAI","y":"WPAI.MI","n":"WisdomTree Physical AI, Humanoids and Drones UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3FNG","y":"3FNG.MI","n":"GraniteShares 3x Long Faang Etp","c":"Azioni Stati Uniti","provider":"GraniteShares","leva":3},
  {"t":"3LPO","y":"3LPO.MI","n":"GraniteShares 3x Long Spotify Daily Etp","c":"Singole azioni","provider":"GraniteShares","leva":3},
  {"t":"QGRW","y":"QGRW.MI","n":"WisdomTree US Quality Growth UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"META","y":"META.MI","n":"WisdomTree Industrial Metals Enhanced","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3UKS","y":"3UKS.L","n":"WisdomTree FTSE 100 3x Daily Short","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"3FB","y":"3FB.MI","n":"Leverage Shares 3x Facebook Etp Securities","c":"Singole azioni","provider":"Leverage Shares","leva":3},
  {"t":"SNGA","y":"SNGA.MI","n":"WisdomTree Natural Gas 1x Daily Short","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"WSPE","y":"WSPE.MI","n":"WisdomTree S&P 500 EUR Daily Hedged","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3EDF","y":"3EDF.MI","n":"WisdomTree STOXX Europe Aerospace & Defence 3x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"3SRA","y":"3SRA.MI","n":"Leverage Shares 3x Short Ferrari (RACE) Etp","c":"Singole azioni","provider":"Leverage Shares","leva":3},
  {"t":"5BUS","y":"5BUS.MI","n":"WisdomTree Bund 10Y 5x Daily Short","c":"WisdomTree","provider":"WisdomTree","leva":5},
  {"t":"SUK1","y":"SUK1.L","n":"WisdomTree FTSE 100 1x Daily Short","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"WEAT","y":"WEAT.MI","n":"WisdomTree Wheat","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"5ITS","y":"5ITS.MI","n":"WisdomTree FTSE MIB 5x Daily Short","c":"WisdomTree","provider":"WisdomTree","leva":5},
  {"t":"WENU","y":"WENU.MI","n":"WisdomTree Strategic Metals UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"GBS","y":"GBS.MI","n":"Gold Bullion Securities","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"WSPX","y":"WSPX.MI","n":"WisdomTree S&P 500","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"WGRO","y":"WGRO.MI","n":"WisdomTree Global Quality Growth UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3LFB","y":"3LFB.MI","n":"GraniteShares 3x Long Facebook Daily Etp","c":"Singole azioni","provider":"GraniteShares","leva":3},
  {"t":"QS5L","y":"QS5L.MI","n":"WisdomTree NASDAQ 100 5x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree","leva":5},
  {"t":"ADAW","y":"ADAW.PA","n":"WisdomTree Physical Cardano","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"PHAU","y":"PHAU.MI","n":"WisdomTree Physical Gold","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3LAP","y":"3LAP.MI","n":"GraniteShares 3x Long Apple Daily Etp","c":"Singole azioni","provider":"GraniteShares","leva":3},
  {"t":"3DEL","y":"3DEL.MI","n":"WisdomTree DAX 3x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"5USL","y":"5USL.MI","n":"WisdomTree S&P 500 5x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree","leva":5},
  {"t":"GPT3","y":"GPT3.MI","n":"Leverage Shares 3x Long Artificial Intelligence (AI) Etp","c":"Azioni Stati Uniti","provider":"Leverage Shares","leva":3},
  {"t":"QQQ3","y":"QQQ3.MI","n":"WisdomTree NASDAQ 100 3x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"3USL","y":"3USL.MI","n":"WisdomTree S&P 500 3x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"FAAN","y":"FAAN.MI","n":"Leverage Shares Faang+ Etp","c":"Azioni Stati Uniti","provider":"Leverage Shares","leva":1},
  {"t":"COTN","y":"COTN.MI","n":"WisdomTree Cotton","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3GOO","y":"3GOO.MI","n":"Leverage Shares 3x Alphabet Etp Securities","c":"Singole azioni","provider":"Leverage Shares","leva":3},
  {"t":"DOTW","y":"DOTW.PA","n":"WisdomTree Physical Polkadot","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3WHL","y":"3WHL.MI","n":"WisdomTree Wheat 3x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"EGB5","y":"EGB5.MI","n":"WisdomTree Long GBP Short EUR 5x Daily","c":"WisdomTree","provider":"WisdomTree","leva":5},
  {"t":"SOXL","y":"SOXL.MI","n":"Leverage Shares 4x Long Semiconductors Etp","c":"Paniere di azioni","provider":"Leverage Shares","leva":4},
  {"t":"NCLR","y":"NCLR.MI","n":"WisdomTree Uranium and Nuclear Energy UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"5SIT","y":"5SIT.MI","n":"GraniteShares 5x Short Mib Daily Etp","c":"Azioni Italia","provider":"GraniteShares","leva":5},
  {"t":"ITBL","y":"ITBL.MI","n":"WisdomTree FTSE MIB Banks","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3LAL","y":"3LAL.MI","n":"GraniteShares 3x Long Alphabet Daily Etp","c":"Singole azioni","provider":"GraniteShares","leva":3},
  {"t":"ARM3","y":"ARM3.MI","n":"Leverage Shares 3x Arm Etp Securities","c":"Singole azioni","provider":"Leverage Shares","leva":3},
  {"t":"GBCH","y":"GBCH.L","n":"WisdomTree Long CHF Short GBP","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"LEU3","y":"LEU3.L","n":"WisdomTree Long EUR Short USD 3x Daily","c":"WisdomTree","provider":"WisdomTree","leva":3},
  {"t":"WQTM","y":"WQTM.MI","n":"WisdomTree Quantum Computing UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3LZN","y":"3LZN.MI","n":"GraniteShares 3x Long Amazon Daily Etp","c":"Singole azioni","provider":"GraniteShares","leva":3},
  {"t":"5QQQ","y":"5QQQ.MI","n":"Leverage Shares 5x Long Nasdaq 100 Etp","c":"Azioni Stati Uniti","provider":"Leverage Shares","leva":5},
  {"t":"ECTN","y":"ECTN.MI","n":"WisdomTree Cotton - EUR Daily Hedged","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"LWEA","y":"LWEA.MI","n":"WisdomTree Wheat 2x Daily Leveraged","c":"WisdomTree","provider":"WisdomTree","leva":2},
  {"t":"DEM","y":"DEM.MI","n":"WisdomTree Emerging Markets Equity Income UCITS ETF","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"WMGT","y":"WMGT.MI","n":"WisdomTree Megatrends UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"WNAS","y":"WNAS.MI","n":"WisdomTree NASDAQ-100","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"RARE","y":"RARE.MI","n":"WisdomTree Strategic Metals and Rare Earths Miners UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"DFEA","y":"DFEA.MI","n":"WisdomTree Europe SmallCap Dividend UCITS ETF Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"5MIB","y":"5MIB.MI","n":"GraniteShares 5x Long Mib Daily Etp","c":"Azioni Italia","provider":"GraniteShares","leva":5},
  {"t":"WBLK","y":"WBLK.MI","n":"WisdomTree Blockchain UCITS ETF - USD Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"DGRE","y":"DGRE.MI","n":"WisdomTree US Quality Dividend Growth UCITS ETF - EUR Hedged Acc","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"SMCI","y":"SMCI.MI","n":"Leverage Shares 2x Super Micro Computer Etp","c":"Azioni Stati Uniti","provider":"Leverage Shares","leva":2},
  {"t":"EZNC","y":"EZNC.MI","n":"WisdomTree Zinc - EUR Daily Hedged","c":"WisdomTree","provider":"WisdomTree","leva":1},
  {"t":"3LUB","y":"3LUB.MI","n":"GraniteShares 3x Long Uber Daily Etp","c":"Singole azioni","provider":"GraniteShares","leva":3}
]

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

def calc_sar(high, low, step=0.03, max_af=0.25):
    """Parabolic SAR — parametri aggressivi per leva"""
    if len(high) < 5: return [None]*len(high)
    sar = [None]*len(high)
    # Init: inizia bearish se prima barra è ribassista
    bull = high[1] > high[0]
    af = step
    ep = max(high[:2]) if bull else min(low[:2])
    sar[1] = min(low[:2]) if bull else max(high[:2])

    for i in range(2, len(high)):
        prev_sar = sar[i-1]
        if bull:
            sar[i] = prev_sar + af * (ep - prev_sar)
            sar[i] = min(sar[i], low[i-1], low[i-2] if i>=2 else low[i-1])
            if low[i] < sar[i]:
                bull = False; af = step
                sar[i] = ep; ep = low[i]
            else:
                if high[i] > ep:
                    ep = high[i]; af = min(af + step, max_af)
        else:
            sar[i] = prev_sar + af * (ep - prev_sar)
            sar[i] = max(sar[i], high[i-1], high[i-2] if i>=2 else high[i-1])
            if high[i] > sar[i]:
                bull = True; af = step
                sar[i] = ep; ep = high[i]
            else:
                if low[i] < ep:
                    ep = low[i]; af = min(af + step, max_af)
    return sar

def calc_sar_flip(close, sar_arr, window=2):
    """Rileva il primo pallino SAR (flip) entro le ultime `window` barre.
    Ritorna (direzione, barre_da_flip): direzione 'BULL'|'BEAR'|'';
    barre_da_flip: 0 = flip sulla barra corrente, 1 = barra precedente, ecc."""
    bull_series = []
    for i in range(len(close)):
        if sar_arr[i] is not None:
            bull_series.append(close[i] > sar_arr[i])
    if len(bull_series) < window + 1:
        return '', None
    last_state = bull_series[-1]
    for back in range(1, window + 1):
        if bull_series[-1 - back] != last_state:
            return ('BULL' if last_state else 'BEAR'), back - 1
    return '', None

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

# ── FILTRI QUALITÀ (v2) ─────────────────────────────────────────
VOL_MIN_CONF  = 2.0   # volume minimo per LONG_CONF
VOL_MIN_EARLY = 1.5   # volume minimo per LONG_EARLY
BAF_MIN_CONF  = 3     # baffetti minimi per LONG_CONF
BAF_MIN_EARLY = 3     # baffetti minimi per LONG_EARLY
ER_MIN        = 0.35  # efficiency ratio minimo
KAMA_GAP_MIN  = 0.003 # gap minimo KAMA fast/slow (0.3%)
SCORE_MIN     = 65    # score minimo per comparire come segnale
VIX_BLOCK     = 28    # sopra questa soglia: blocco totale Long
VIX_ONLY_CONF = 22    # tra 22 e 28: solo LONG_CONF (no EARLY)

# ── SUPER BEST BUY (flip SAR) ───────────────────────────────────
SAR_FLIP_WINDOW = 2     # barre entro cui il flip è considerato "fresco"
SBB_VOL_MIN     = 1.5   # volume minimo (livello alleggerito rispetto a Best Buy)
SANITY_PERFOGGI = 4.0   # cap unico perfOggi% per tutti i leva — evita ingressi dopo spike già avvenuto

def get_segnale_leva(zona, ao, vol_ratio, er, baf, kama_fast=None, kama_slow=None, regime='NORMALE', sar_bull=True):
    """Segnale leva v2 — filtri qualità stretti"""
    # Blocco VIX in STRESS/PAURA
    if regime in ('STRESS','PAURA'):
        if zona == 'STOP':   return 'STOP'
        if zona == 'USCITA': return 'USCITA'
        return ''  # nessun Long in regime di paura

    # Gap minimo tra le due KAMA
    kama_gap_ok = True
    if kama_fast and kama_slow and kama_slow > 0:
        kama_gap_ok = abs(kama_fast - kama_slow) / kama_slow >= KAMA_GAP_MIN

    if zona == 'LONG_CONF' and ao > 0 and vol_ratio >= VOL_MIN_CONF and baf >= BAF_MIN_CONF and er >= ER_MIN and kama_gap_ok and sar_bull:
        return 'LONG'
    elif zona == 'LONG_EARLY' and ao > 0 and vol_ratio >= VOL_MIN_EARLY and baf >= BAF_MIN_EARLY and er >= ER_MIN and kama_gap_ok and regime not in ('ATTENZIONE',):
        # In ATTENZIONE solo LONG_CONF
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
        except Exception as e:
            print(f"Errore fetch VIX {v['t']}: {e}")
        time.sleep(0.5)
    return vix_val, vstoxx_val

# ═══════════════════════════════════════════════════════
# PROCESS TICKER LEVA
# ═══════════════════════════════════════════════════════
def process_leva(info, regime_mult, regime_name='NORMALE'):
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
        rsi5     = calc_rsi(close, n=5)
        # RSI cross: +1 bullish (rsi5 supera rsi14 dal basso), -1 bearish
        rsi_cross = 0
        if len(close) > 16:
            r14p = calc_rsi(close[:-1])
            r5p  = calc_rsi(close[:-1], n=5)
            if r5p <= r14p and rsi5 > rsi:   rsi_cross = 1
            elif r5p >= r14p and rsi5 < rsi: rsi_cross = -1
        baf      = calc_baffetti_fast(high, low)

        # ── ZONA/SEGNALE (spostato PRIMA di pre_signal — bug fix: zona era usata non definita) ──
        zona     = get_zona(lc, kf, ks)

        # ── PRE-SIGNAL: AO miglioramento 3 barre + RSI cross bullish ──
        ao_history = []
        if len(high) >= 16:
            for ii in range(-4, 0):
                h_sl = high[:len(high)+ii+1] if ii < -1 else high
                l_sl = low[:len(low)+ii+1]   if ii < -1 else low
                ao_history.append(calc_ao_fast(h_sl, l_sl))
        ao_improving = (len(ao_history) >= 3 and
                       ao_history[-1] > ao_history[-2] > ao_history[-3])
        pre_signal = (ao_improving and
                      rsi_cross == 1 and
                      zona not in ('STOP', 'USCITA'))
        sar_arr  = calc_sar(high, low, step=0.03, max_af=0.25)
        sar_val  = sar_arr[-1] if sar_arr[-1] is not None else None
        sar_bull = sar_val is not None and lc > sar_val  # prezzo sopra SAR = rialzista
        segnale  = get_segnale_leva(zona, ao, vol_r, er, baf, kf, ks, regime_name, sar_bull)
        score    = calc_score_leva(zona, ao, vol_r, er, baf, regime_mult)

        perf1  = round((lc/close[-2]-1)*100,2)  if len(close)>2  else 0
        perf5  = round((lc/close[-6]-1)*100,2)  if len(close)>6  else 0
        perf20 = round((lc/close[-21]-1)*100,2) if len(close)>21 else 0

        # ── SUPER BEST BUY: primo pallino SAR rialzista + AO>0 + AO in miglioramento ──
        sar_flip, bars_since_flip = calc_sar_flip(close, sar_arr, window=SAR_FLIP_WINDOW)
        super_best_buy = (
            sar_flip == 'BULL' and
            ao > 0 and
            ao_improving and
            vol_r >= SBB_VOL_MIN and
            abs(perf1) <= SANITY_PERFOGGI
        )

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
                    entry_date = dt.strftime('%d/%m %H:%M')
                    break
        except Exception as e:
            print(f"Errore calcolo entry_date per {info.get('t','?')}: {e}")

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
            'perfOggi':  perf1,
            'perfSett':  perf5,
            'perfMese':  perf20,
            'entryDate': entry_date,
            'sar':       round(sar_val, 4) if sar_val else None,
            'sarBull':   sar_bull,
            'quality':   segnale in ('LONG','EARLY'),
            'rsi5':      round(rsi5, 2),
            'rsi_cross': rsi_cross,
            'leva':      info.get('leva', 1),
            'pre_signal': pre_signal,
            'ao_improving': ao_improving,
            'sar_flip': sar_flip,
            'bars_since_flip': bars_since_flip,
            'super_best_buy': super_best_buy,
        }
    except Exception:
        return None


# ═══════════════════════════════════════════════════════
# EMAIL ALERT
# ═══════════════════════════════════════════════════════
def send_alert_email(alerts, vix, vstoxx, regime, now, prev_regime=None):
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
    regime_banner = ''
    if prev_regime:
        r_icons = {'CALMA':'🟢','NORMALE':'🟡','ATTENZIONE':'🟠','STRESS':'🔴','PAURA':'⛔'}
        regime_banner = '<div style="background:#1a1a2e;border:2px solid #f59e0b;border-radius:8px;padding:10px 16px;margin-bottom:14px">' \
            '<b style="color:#f59e0b">⚠️ CAMBIO REGIME VIX</b>&nbsp;&nbsp;' \
            '{} {} &nbsp;→&nbsp; {} <b>{}</b></div>'.format(
                r_icons.get(prev_regime,''), prev_regime,
                r_icons.get(regime,''), regime)
        subj_prefix = "⚠️ REGIME {} →".format(regime)
    else:
        subj_prefix = "⚡ RAPTOR LEVA —"
    subj = "{} {} segnale/i · {}".format(subj_prefix, len(alerts), now.strftime('%d/%m/%Y %H:%M'))
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
            '<td style="padding:7px;color:#1a7f37;font-weight:700">{}x</td>' \
            '<td style="padding:7px">{}</td>' \
            '</tr>'.format(
                bg, a['ticker'], (a['nome'] or '')[:45],
                ICONS.get(a['old'],a['old']), ICONS.get(a['new'],a['new']),
                a['prezzo'], a['kf'], a['ks'], a['score'],
                round(a.get('vol',0),1), a['entry'])
    # Inserisci banner regime nel corpo HTML
    rows_html = regime_banner + rows_html if regime_banner else rows_html
    vix_c = '#1a7f37' if (vix or 20)<20 else '#bc4c00' if (vix or 20)<30 else '#cf222e'
    html = """<!DOCTYPE html><html><body style='font-family:"Segoe UI",sans-serif;background:#f5f7fa;padding:20px'>
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
# EXPLOSIVE MOVER — storico perf per z-score + fallback soglia assoluta
# ═══════════════════════════════════════════════════════
PERF_HISTORY_FILE   = 'perf_history.json'
ALERT_STATE_FILE    = 'explosive_alerted.json'
HIST_ROLLING_DAYS   = 120
MIN_HIST_DAYS       = 30     # sotto questa soglia si usa la soglia assoluta
Z_THRESH_SETT       = 3.0
Z_THRESH_MESE       = 2.5
ABS_THRESH_SETT     = 40.0   # % — fallback finché non c'è storico sufficiente
ABS_THRESH_MESE     = 70.0   # %
SANITY_CAP_PCT      = 500.0  # oltre questo valore è quasi certamente un rebase/reverse split ETP, non un vero movimento
COOLDOWN_DAYS       = 5

def update_perf_history(results, now):
    """Accumula un campione al giorno per ticker (perfSett/perfMese). Rolling window."""
    try:
        with open(PERF_HISTORY_FILE, 'r', encoding='utf-8') as f:
            hist = json.load(f)
    except Exception:
        hist = {}
    today = now.strftime('%Y-%m-%d')
    for r in results:
        t = r['ticker']
        entries = hist.setdefault(t, [])
        sample = [today, r.get('perfSett', 0), r.get('perfMese', 0)]
        if entries and entries[-1][0] == today:
            entries[-1] = sample  # ultima run della giornata vince
        else:
            entries.append(sample)
        if len(entries) > HIST_ROLLING_DAYS:
            hist[t] = entries[-HIST_ROLLING_DAYS:]
    try:
        with open(PERF_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(hist, f, ensure_ascii=False)
    except Exception as e:
        print(f"Errore salvataggio {PERF_HISTORY_FILE}: {e}")
    return hist

def _load_alert_state():
    try:
        with open(ALERT_STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def _save_alert_state(state):
    try:
        with open(ALERT_STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False)
    except Exception as e:
        print(f"Errore salvataggio {ALERT_STATE_FILE}: {e}")

def check_explosive_movers(results, hist, now):
    """Individua ticker con Sett%/Mese% anomali rispetto al proprio storico (z-score),
    con fallback a soglia assoluta se lo storico è insufficiente. Dedup con cooldown."""
    state = _load_alert_state()
    today = now.strftime('%Y-%m-%d')
    movers = []
    for r in results:
        t = r['ticker']
        past = [x for x in hist.get(t, []) if x[0] != today]
        reasons = []
        z_sett = z_mese = None

        if len(past) >= MIN_HIST_DAYS:
            sett_vals = [x[1] for x in past]
            mese_vals = [x[2] for x in past]
            mu_s, sd_s = statistics.mean(sett_vals), statistics.pstdev(sett_vals)
            mu_m, sd_m = statistics.mean(mese_vals), statistics.pstdev(mese_vals)
            if sd_s > 0:
                z_sett = (r.get('perfSett', 0) - mu_s) / sd_s
                if z_sett >= Z_THRESH_SETT:
                    reasons.append(f"z-sett {z_sett:.1f}")
            if sd_m > 0:
                z_mese = (r.get('perfMese', 0) - mu_m) / sd_m
                if z_mese >= Z_THRESH_MESE:
                    reasons.append(f"z-mese {z_mese:.1f}")
        else:
            if r.get('perfSett', 0) >= ABS_THRESH_SETT:
                reasons.append(f"Sett% {r['perfSett']:.1f} (soglia assoluta, storico insuff.: {len(past)}/{MIN_HIST_DAYS}gg)")
            if r.get('perfMese', 0) >= ABS_THRESH_MESE:
                reasons.append(f"Mese% {r['perfMese']:.1f} (soglia assoluta, storico insuff.: {len(past)}/{MIN_HIST_DAYS}gg)")

        if not reasons:
            continue

        # Valori assurdi (decine di migliaia di %) sono quasi sempre rebase/reverse split ETP, non veri mover
        if r.get('perfSett', 0) >= SANITY_CAP_PCT or r.get('perfMese', 0) >= SANITY_CAP_PCT:
            reasons = [f"⚠️ possibile REBASE/SPLIT (valore fuori scala) — verificare manualmente, non trattare come segnale di trading: " + ' · '.join(reasons)]

        method = 'z' if (z_sett is not None or z_mese is not None) else 'abs'
        metric = max([v for v in (z_sett, z_mese) if v is not None], default=None)
        if metric is None:
            metric = max(r.get('perfSett', 0), r.get('perfMese', 0))

        prev = state.get(t)
        if prev:
            days_since = (now.date() - datetime.datetime.strptime(prev['date'], '%Y-%m-%d').date()).days
            # confronto valido solo se stesso metodo di rilevazione (scale diverse altrimenti)
            same_method = prev.get('method') == method
            if days_since < COOLDOWN_DAYS and same_method and metric <= prev.get('metric', 0):
                continue  # in cooldown e non peggiorato ulteriormente

        movers.append({
            'ticker': t, 'nome': r.get('nome', ''), 'prezzo': r.get('prezzo', 0),
            'perfOggi': r.get('perfOggi', 0), 'perfSett': r.get('perfSett', 0), 'perfMese': r.get('perfMese', 0),
            'score': r.get('score', 0), 'reasons': reasons,
        })
        state[t] = {'date': today, 'metric': metric, 'method': method}

    _save_alert_state(state)
    return movers

def send_explosive_alert_email(movers, now):
    import smtplib, os
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    EMAIL_USER = os.environ.get('EMAIL_USER', '')
    EMAIL_PASS = os.environ.get('EMAIL_PASS', '')
    if not EMAIL_USER or not EMAIL_PASS:
        print("EMAIL non configurata — skip")
        return
    subj = "🚀 RAPTOR Leva — {} mover esplosivo/i · {}".format(len(movers), now.strftime('%d/%m/%Y %H:%M'))
    rows_html = ""
    for m in movers:
        rows_html += '<tr style="background:#fff7ed">' \
            '<td style="padding:7px;font-weight:700;font-family:monospace">{}</td>' \
            '<td style="padding:7px;font-size:11px;color:#57606a">{}</td>' \
            '<td style="padding:7px;font-family:monospace">{}</td>' \
            '<td style="padding:7px;font-family:monospace;color:{}">{:+.1f}%</td>' \
            '<td style="padding:7px;font-family:monospace;color:{}">{:+.1f}%</td>' \
            '<td style="padding:7px;font-family:monospace;color:{}">{:+.1f}%</td>' \
            '<td style="padding:7px;font-weight:700">{}</td>' \
            '<td style="padding:7px;font-size:11px;color:#bc4c00">{}</td>' \
            '</tr>'.format(
                m['ticker'], (m['nome'] or '')[:45], m['prezzo'],
                '#1a7f37' if m['perfOggi'] >= 0 else '#cf222e', m['perfOggi'],
                '#1a7f37' if m['perfSett'] >= 0 else '#cf222e', m['perfSett'],
                '#1a7f37' if m['perfMese'] >= 0 else '#cf222e', m['perfMese'],
                m['score'], ' · '.join(m['reasons']))
    html = """<!DOCTYPE html><html><body style='font-family:"Segoe UI",sans-serif;background:#f5f7fa;padding:20px'>
<div style="max-width:820px;margin:0 auto;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,.1)">
  <div style="background:#bc4c00;color:#fff;padding:14px 20px">
    <h2 style="margin:0;font-size:18px">🚀 RAPTOR Leva — Mover Esplosivo</h2>
    <p style="margin:4px 0 0;font-size:12px;opacity:.85">{ts} · movimento anomalo rispetto allo storico del singolo ticker (indipendente dal segnale KAMA/RSI)</p>
  </div>
  <div style="padding:16px">
    <table style="width:100%;border-collapse:collapse;font-size:12px">
      <thead><tr style="background:#f5f7fa">
        <th style="padding:6px;text-align:left;border-bottom:2px solid #d0d7de">Ticker</th>
        <th style="padding:6px;text-align:left;border-bottom:2px solid #d0d7de">Nome</th>
        <th style="padding:6px;border-bottom:2px solid #d0d7de">Prezzo</th>
        <th style="padding:6px;border-bottom:2px solid #d0d7de">Oggi%</th>
        <th style="padding:6px;border-bottom:2px solid #d0d7de">Sett%</th>
        <th style="padding:6px;border-bottom:2px solid #d0d7de">Mese%</th>
        <th style="padding:6px;border-bottom:2px solid #d0d7de">Score</th>
        <th style="padding:6px;text-align:left;border-bottom:2px solid #d0d7de">Motivo</th>
      </tr></thead>
      <tbody>{rows}</tbody>
    </table>
    <p style="margin-top:12px;font-size:11px;color:#57606a">
      ⚠️ Alert basato su z-score storico per ticker (min. {min_days}gg) o soglia assoluta se storico insufficiente.<br>
      ⚠️ Solo uso educativo.<br>
      📊 <a href="https://giorgiogoldoni.github.io/raptor-leva/">Apri RAPTOR Leva</a>
    </p>
  </div>
</div></body></html>""".format(ts=now.strftime('%d/%m/%Y %H:%M'), rows=rows_html, min_days=MIN_HIST_DAYS)
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subj
        msg['From'] = EMAIL_USER
        msg['To'] = EMAIL_USER
        msg.attach(MIMEText(html, 'html'))
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as srv:
            srv.login(EMAIL_USER, EMAIL_PASS)
            srv.sendmail(EMAIL_USER, EMAIL_USER, msg.as_string())
        print("Email mover esplosivo inviata: {} ticker".format(len(movers)))
    except Exception as e:
        print("Errore email mover esplosivo: {}".format(e))

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
        r = process_leva(info, regime['mult'], regime['regime'])
        if r: results.append(r)
        else: errors += 1
        if (i+1) % 20 == 0:
            print(f"  {i+1}/{len(TICKERS)} — ok:{len(results)} err:{errors}")
        time.sleep(0.3)

    # 3. Rileva cambi segnale e manda email
    prev_zones = {}
    prev_j = {}
    try:
        with open('raptor_leva.json','r',encoding='utf-8') as f:
            prev_j = json.load(f)
            for r in prev_j.get('data',[]):
                prev_zones[r['ticker']] = r.get('zona','')
    except Exception as e:
        print(f"Nessun raptor_leva.json precedente o errore lettura: {e}")

    # Cambio regime VIX — avviso indipendente
    prev_regime = prev_j.get('regime','')
    regime_changed = prev_regime and prev_regime != regime['regime']
    if regime_changed:
        print("REGIME CAMBIATO: {} → {}".format(prev_regime, regime['regime']))

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
        # Solo alert per ticker di qualità (rispettano tutti i filtri)
        if r.get('quality') and old_z and new_z and old_z != new_z and (old_z,new_z) in CAMBI:
            if r.get('score',0) >= SCORE_MIN:
                alert_list.append({'ticker':r['ticker'],'nome':r.get('nome',''),
                    'old':old_z,'new':new_z,'score':r['score'],'prezzo':r['prezzo'],
                    'kf':r.get('kama_fast','—'),'ks':r.get('kama_slow','—'),
                    'entry':r.get('entryDate','—'),'vol':r.get('volRatio',0),
                    'er':r.get('er',0),'baff':r.get('baff',0)})
    print("Alert qualità: {}".format(len(alert_list)))
    if alert_list or regime_changed:
        send_alert_email(alert_list, vix, vstoxx, regime['regime'], now,
                        prev_regime if regime_changed else None)

    # 3b. Mover esplosivo (z-score storico per ticker / soglia assoluta di fallback)
    perf_hist = update_perf_history(results, now)
    movers = check_explosive_movers(results, perf_hist, now)
    print("Mover esplosivi: {}".format(len(movers)))
    if movers:
        send_explosive_alert_email(movers, now)

    # 3c. Super Best Buy — log a console
    sbb_list = [r for r in results if r.get('super_best_buy')]
    print("Super Best Buy (flip SAR): {}".format(len(sbb_list)))

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
