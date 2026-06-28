#!/usr/bin/env python3
"""
RAPTOR Chart Leva Fetch — GitHub Actions
Scarica 6 mesi OHLCV daily per tutti i ticker leva
Calcola KAMA fast/slow, SAR, AO, RSI14, RSI5, segnali, BAFF
Salva file separati data/charts/TICKER_YAHOO.json (stile scannerv2)
Gira 2 volte al giorno: 08:00 UTC e 14:00 UTC
"""

import json, time, datetime, os, math
import yfinance as yf

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
# VIX

# ═══════════════════════════════════════════════════════
# INDICATORI
# ═══════════════════════════════════════════════════════

def calc_kama(close, n=10, fast=2, slow=30):
    fast_sc = 2/(fast+1); slow_sc = 2/(slow+1)
    kama = [None]*len(close)
    if len(close) <= n: return kama
    kama[n] = close[n]
    for i in range(n+1, len(close)):
        direction = abs(close[i] - close[i-n])
        volatility = sum(abs(close[j]-close[j-1]) for j in range(i-n+1, i+1))
        er = direction/volatility if volatility else 0
        sc = (er*(fast_sc-slow_sc)+slow_sc)**2
        kama[i] = kama[i-1] + sc*(close[i]-kama[i-1])
    return kama

def calc_sar(high, low, step=0.03, max_af=0.25):
    n = len(high)
    sar = [None]*n
    if n < 5: return sar
    bull = high[1] > high[0]
    af = step
    ep = max(high[:2]) if bull else min(low[:2])
    sar[1] = min(low[:2]) if bull else max(high[:2])
    for i in range(2, n):
        ps = sar[i-1]
        if bull:
            sar[i] = min(ps + af*(ep-ps), low[i-1], low[i-2] if i>=2 else low[i-1])
            if low[i] < sar[i]:
                bull=False; af=step; sar[i]=ep; ep=low[i]
            else:
                if high[i] > ep: ep=high[i]; af=min(af+step, max_af)
        else:
            sar[i] = max(ps + af*(ep-ps), high[i-1], high[i-2] if i>=2 else high[i-1])
            if high[i] > sar[i]:
                bull=True; af=step; sar[i]=ep; ep=high[i]
            else:
                if low[i] < ep: ep=low[i]; af=min(af+step, max_af)
    return sar

def calc_ao(high, low):
    mid = [(h+l)/2 for h,l in zip(high,low)]
    if len(mid) < 13: return [0]*len(mid)
    def ema(arr, p):
        k=2/(p+1); e=arr[0]
        out=[e]
        for x in arr[1:]: e=x*k+e*(1-k); out.append(e)
        return out
    e3=ema(mid,3); e13=ema(mid,13)
    return [round(a-b,4) for a,b in zip(e3,e13)]

def calc_rsi(close, n=14):
    result = [None]*len(close)
    if len(close) < n+2: return result
    for i in range(n+1, len(close)):
        gains=[]; losses=[]
        for j in range(i-n, i+1):
            d = close[j]-close[j-1]
            gains.append(max(d,0)); losses.append(max(-d,0))
        ag=sum(gains)/n; al=sum(losses)/n
        result[i] = round(100-100/(1+ag/al),2) if al>0 else 100.0
    return result

def calc_baff(close, kama):
    """Barre consecutive sopra/sotto KAMA (per istogramma)"""
    result = []
    streak = 0
    for i, (c, k) in enumerate(zip(close, kama)):
        if k is None:
            result.append(0); continue
        if c > k:
            streak = streak+1 if streak>0 else 1
        else:
            streak = streak-1 if streak<0 else -1
        result.append(streak)
    return result

def get_zona(price, kf, ks):
    if kf is None or ks is None: return 'ND'
    if price > kf and kf > ks: return 'LONG_CONF'
    elif price > kf and price > ks: return 'LONG_EARLY'
    elif price > ks and price < kf: return 'GRIGIA'
    elif price < ks:
        gap = (ks-price)/ks*100 if ks>0 else 0
        return 'STOP' if gap>2 else 'USCITA'
    return 'GRIGIA'

def get_signal(zona, ao, vol_ratio, er, baf, kf, ks, sar_bull):
    kama_gap_ok = True
    if kf and ks and ks>0:
        kama_gap_ok = abs(kf-ks)/ks >= 0.003
    if zona=='LONG_CONF' and ao>0 and vol_ratio>=2.0 and baf>=3 and er>=0.35 and kama_gap_ok and sar_bull:
        return 'BUY3'
    elif zona=='LONG_EARLY' and ao>0 and vol_ratio>=1.5 and baf>=3 and er>=0.35 and kama_gap_ok:
        return 'BUY2'
    elif zona in ('LONG_CONF','LONG_EARLY'):
        return 'WATCH'
    elif zona=='STOP': return 'SELL'
    elif zona=='USCITA': return 'SELL'
    return None

def calc_rsi_crosses(rsi14, rsi5, dates):
    """Ritorna lista di {date, dir} per ogni incrocio RSI5/RSI14"""
    crosses = []
    for i in range(1, len(rsi14)):
        r14 = rsi14[i]; r5 = rsi5[i]
        r14p = rsi14[i-1]; r5p = rsi5[i-1]
        if r14 is None or r5 is None or r14p is None or r5p is None:
            continue
        if r5p <= r14p and r5 > r14:
            crosses.append({'d': dates[i] if i<len(dates) else '', 'dir': 1})
        elif r5p >= r14p and r5 < r14:
            crosses.append({'d': dates[i] if i<len(dates) else '', 'dir': -1})
    return crosses[-10:]  # ultime 10

# ═══════════════════════════════════════════════════════
# PROCESS TICKER
# ═══════════════════════════════════════════════════════
def process_ticker(info):
    symbol = info['y']
    try:
        tk = yf.Ticker(symbol)
        hist = tk.history(period='6mo', interval='1d', timeout=15)
        if hist.empty or len(hist) < 30: return None

        closes  = [round(float(x),4) for x in hist['Close'].values]
        highs   = [round(float(x),4) for x in hist['High'].values]
        lows    = [round(float(x),4) for x in hist['Low'].values]
        volumes = [int(x) for x in hist['Volume'].values]
        dates   = [ts.strftime('%Y-%m-%d') for ts in hist.index]

        kf_arr = calc_kama(closes, n=5,  fast=3, slow=20)
        ks_arr = calc_kama(closes, n=20, fast=2, slow=40)
        sar_arr = calc_sar(highs, lows, 0.03, 0.25)
        ao_arr  = calc_ao(highs, lows)
        r14_arr = calc_rsi(closes, 14)
        r5_arr  = calc_rsi(closes, 5)
        baff_arr = calc_baff(closes, kf_arr)

        # Segnali per ogni barra
        signals = []
        avg_vol = sum(volumes[-21:-1])/20 if len(volumes)>21 else 1
        for i in range(len(closes)):
            kf=kf_arr[i]; ks=ks_arr[i]; sar=sar_arr[i]
            if kf is None or ks is None:
                signals.append(None); continue
            zona = get_zona(closes[i], kf, ks)
            vol_r = volumes[i]/avg_vol if avg_vol>0 else 1
            baf = baff_arr[i]
            er_val = 0
            if i>=10:
                d=abs(closes[i]-closes[i-10])
                v=sum(abs(closes[j]-closes[j-1]) for j in range(i-9,i+1))
                er_val=d/v if v>0 else 0
            sar_bull = sar is not None and closes[i]>sar
            ao = ao_arr[i] if i<len(ao_arr) else 0
            sig = get_signal(zona, ao, vol_r, er_val, baf, kf, ks, sar_bull)
            signals.append(sig)

        # RSI cross storici
        rsi_crosses = calc_rsi_crosses(r14_arr, r5_arr, dates)

        # Ultimo cross RSI
        last_cross = rsi_crosses[-1] if rsi_crosses else None

        def fmt(arr):
            return [round(v,4) if v is not None else None for v in arr]

        return {
            'ticker':  info['t'],
            'yahoo':   symbol,
            'nome':    info.get('n',''),
            'provider':info.get('provider',''),
            'leva':    info.get('leva',1),
            'dates':   dates,
            'closes':  fmt(closes),
            'highs':   fmt(highs),
            'lows':    fmt(lows),
            'volumes': volumes,
            'kama_fast': fmt(kf_arr),
            'kama_slow': fmt(ks_arr),
            'sar':       fmt(sar_arr),
            'ao':        fmt(ao_arr),
            'rsi14':     fmt(r14_arr),
            'rsi5':      fmt(r5_arr),
            'baff':      baff_arr,
            'signals':   signals,
            'rsi_crosses': rsi_crosses,
            'last_cross': last_cross,
        }
    except Exception as e:
        print(f"  ERR {symbol}: {e}")
        return None

# ═══════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════
def main():
    now = datetime.datetime.now()
    print(f"RAPTOR Chart Leva Fetch — {now.strftime('%Y-%m-%d %H:%M')}")
    print(f"Ticker: {len(TICKERS)}")

    os.makedirs('data/charts', exist_ok=True)

    # Deduplica per yahoo symbol
    seen = set(); unique = []
    for t in TICKERS:
        if t['y'] not in seen:
            seen.add(t['y']); unique.append(t)
    print(f"Ticker unici: {len(unique)}")

    ok=0; errors=0
    index = []

    for i, info in enumerate(unique):
        result = process_ticker(info)
        if result:
            fname = info['y'].replace('.','_') + '.json'
            with open(f"data/charts/{fname}", 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, separators=(',',':'))
            index.append({'t': info['t'], 'y': info['y'], 'f': fname,
                          'leva': info.get('leva',1), 'provider': info.get('provider','')})
            ok += 1
        else:
            errors += 1
        if (i+1) % 30 == 0:
            print(f"  {i+1}/{len(unique)} — ok:{ok} err:{errors}")
        time.sleep(0.35)

    # Index file per la dashboard
    meta = {
        'timestamp': now.isoformat(),
        'timestamp_it': now.strftime('%d/%m/%Y %H:%M'),
        'ok': ok, 'errors': errors,
        'index': index
    }
    with open('data/charts/index.json','w',encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, separators=(',',':'))

    print(f"\nSalvati {ok} file JSON in data/charts/ — {errors} errori")

if __name__ == '__main__':
    main()
