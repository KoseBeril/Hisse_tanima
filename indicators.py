# ==========================================================
# BIST ENGINE PRO
# indicators.py
# Tüm gelişmiş ve standart teknik indikatörler burada hesaplanır.
# ==========================================================

import pandas as pd
import pandas_ta as ta
import numpy as np
from config import *

def calculate_indicators(df):
    df = df.copy()

    # =====================================================
    # EMA & SMA
    # =====================================================
    for length in EMA_LIST:
        df[f"EMA{length}"] = ta.ema(df["close"], length=length)

    for length in SMA_LIST:
        df[f"SMA{length}"] = ta.sma(df["close"], length=length)

    # =====================================================
    # RSI & RSI_EMA
    # =====================================================
    df["RSI"] = ta.rsi(df["close"], length=RSI_LENGTH)
    df["RSI_EMA"] = ta.ema(df["RSI"], length=RSI_EMA)

    # =====================================================
    # MACD
    # =====================================================
    macd = ta.macd(df["close"], fast=MACD_FAST, slow=MACD_SLOW, signal=MACD_SIGNAL)
    if macd is not None:
        col_macd = f"MACD_{MACD_FAST}_{MACD_SLOW}_{MACD_SIGNAL}"
        col_signal = f"MACDs_{MACD_FAST}_{MACD_SLOW}_{MACD_SIGNAL}"
        col_hist = f"MACDh_{MACD_FAST}_{MACD_SLOW}_{MACD_SIGNAL}"
        df["MACD"] = macd[col_macd] if col_macd in macd.columns else macd.iloc[:, 0]
        df["MACD_SIGNAL"] = macd[col_signal] if col_signal in macd.columns else macd.iloc[:, 1]
        df["MACD_HIST"] = macd[col_hist] if col_hist in macd.columns else macd.iloc[:, 2]
    else:
        df["MACD"] = np.nan
        df["MACD_SIGNAL"] = np.nan
        df["MACD_HIST"] = np.nan

    # =====================================================
    # ADX
    # =====================================================
    adx = ta.adx(high=df["high"], low=df["low"], close=df["close"], length=ADX_LENGTH)
    if adx is not None:
        df["ADX"] = adx[f"ADX_{ADX_LENGTH}"] if f"ADX_{ADX_LENGTH}" in adx.columns else adx.iloc[:, 0]
        df["DI+"] = adx[f"DMP_{ADX_LENGTH}"] if f"DMP_{ADX_LENGTH}" in adx.columns else adx.iloc[:, 1]
        df["DI-"] = adx[f"DMN_{ADX_LENGTH}"] if f"DMN_{ADX_LENGTH}" in adx.columns else adx.iloc[:, 2]
    else:
        df["ADX"] = np.nan
        df["DI+"] = np.nan
        df["DI-"] = np.nan

    # =====================================================
    # ATR & CCI & ROC & MOMENTUM & WILLIAMS %R
    # =====================================================
    df["ATR"] = ta.atr(df["high"], df["low"], df["close"], length=ATR_LENGTH)
    df["CCI"] = ta.cci(df["high"], df["low"], df["close"], length=CCI_LENGTH)
    df["ROC"] = ta.roc(df["close"], length=ROC_LENGTH)
    df["MOM"] = ta.mom(df["close"], length=MOMENTUM_LENGTH)
    df["WILLR"] = ta.willr(df["high"], df["low"], df["close"], length=14)

    # =====================================================
    # STOCHASTIC
    # =====================================================
    stoch_k_length = 14 
    stoch_d_smooth = 3
    stoch_k_smooth = 3
    stoch = ta.stoch(high=df["high"], low=df["low"], close=df["close"], k=stoch_k_length, d=stoch_d_smooth, smooth_k=stoch_k_smooth)
    if stoch is not None:
        col_k = f"STOCHk_{stoch_k_length}_{stoch_d_smooth}_{stoch_k_smooth}"
        col_d = f"STOCHd_{stoch_k_length}_{stoch_d_smooth}_{stoch_k_smooth}"
        df["STOCH_K"] = stoch[col_k] if col_k in stoch.columns else stoch.iloc[:, 0]
        df["STOCH_D"] = stoch[col_d] if col_d in stoch.columns else stoch.iloc[:, 1]
    else:
        df["STOCH_K"] = np.nan
        df["STOCH_D"] = np.nan

    # =====================================================
    # HACİM TABANLI (MFI, OBV, CMF, RVOL, A/D)
    # =====================================================
    df["MFI"] = ta.mfi(df["high"], df["low"], df["close"], volume=df["volume"])
    df["OBV"] = ta.obv(df["close"], df["volume"])
    df["CMF"] = ta.cmf(df["high"], df["low"], df["close"], volume=df["volume"])
    
    df[f"VOL{VOL_MA}"] = df["volume"].rolling(VOL_MA).mean()
    df["RVOL"] = df["volume"] / df[f"VOL{VOL_MA}"]
    df["AD"] = ta.ad(df["high"], df["low"], df["close"], volume=df["volume"])

    # Safe VWAP
    try:
        vwap_series = ta.vwap(high=df["high"], low=df["low"], close=df["close"], volume=df["volume"])
        if vwap_series is not None and not vwap_series.isnull().all():
            df["VWAP"] = vwap_series
        else:
            raise ValueError()
    except Exception:
        typical_price = (df["high"] + df["low"] + df["close"]) / 3
        df["VWAP"] = (typical_price * df["volume"]).cumsum() / df["volume"].cumsum()

    # =====================================================
    # YENİ EKLENEN ENDEKS VE YARDIMCI İNDİKATÖRLER
    # =====================================================

    # 1) BOLLINGER BANDS (DİNAMİK KOLON BULUCU ENTEGRASYONU)
    bb = ta.bbands(df["close"], length=20, std=2)
    if bb is not None:
        col_bbl = [c for c in bb.columns if c.startswith("BBL")][0]
        col_bbm = [c for c in bb.columns if c.startswith("BBM")][0]
        col_bbu = [c for c in bb.columns if c.startswith("BBU")][0]
        col_bbb = [c for c in bb.columns if c.startswith("BBB")][0]

        df["BB_LOWER"] = bb[col_bbl]
        df["BB_MIDDLE"] = bb[col_bbm]
        df["BB_UPPER"] = bb[col_bbu]
        df["BB_WIDTH"] = bb[col_bbb]
        
        df["BBL"] = df["BB_LOWER"]
        df["BBM"] = df["BB_MIDDLE"]
        df["BBU"] = df["BB_UPPER"]
    else:
        df["BB_LOWER"] = df["BB_MIDDLE"] = df["BB_UPPER"] = df["BB_WIDTH"] = np.nan
        df["BBL"] = df["BBM"] = df["BBU"] = np.nan

    # 2) SUPERTREND
    supertrend = ta.supertrend(df["high"], df["low"], df["close"], period=10, multiplier=3)
    if supertrend is not None:
        df["SUPERTREND"] = supertrend.iloc[:, 0]
        df["SUPERT_DIR"] = supertrend.iloc[:, 1]
    else:
        df["SUPERTREND"] = np.nan
        df["SUPERT_DIR"] = np.nan

    # 3) PARABOLIC SAR
    psar = ta.psar(df["high"], df["low"], df["close"], af=0.02, max_af=0.2)
    if psar is not None:
        df["PSAR"] = psar.iloc[:, 0].fillna(psar.iloc[:, 1])
    else:
        df["PSAR"] = np.nan

    # 4) VWMA
    df["VWMA"] = ta.vwma(df["close"], df["volume"], length=20)

    # 5) KELTNER CHANNEL
    kc = ta.kc(df["high"], df["low"], df["close"], length=20, scalar=2)
    if kc is not None:
        df["KC_LOWER"] = kc.iloc[:, 0]
        df["KC_MIDDLE"] = kc.iloc[:, 1]
        df["KC_UPPER"] = kc.iloc[:, 2]
    else:
        df["KC_LOWER"] = df["KC_MIDDLE"] = df["KC_UPPER"] = np.nan

    # 6) DONCHIAN CHANNEL
    donchian = ta.donchian(df["high"], df["low"], lower_length=20, upper_length=20)
    if donchian is not None:
        df["DC_LOWER"] = donchian.iloc[:, 0]
        df["DC_MIDDLE"] = donchian.iloc[:, 1]
        df["DC_UPPER"] = donchian.iloc[:, 2]
    else:
        df["DC_LOWER"] = df["DC_MIDDLE"] = df["DC_UPPER"] = np.nan

    # 7) ICHIMOKU CLOUD
    ichimoku, _ = ta.ichimoku(df["high"], df["low"], df["close"])
    if ichimoku is not None:
        df["ICH_TENKAN"] = ichimoku.iloc[:, 0]
        df["ICH_KIJUN"] = ichimoku.iloc[:, 1]
        df["ICH_SENKOU_A"] = ichimoku.iloc[:, 2]
        df["ICH_SENKOU_B"] = ichimoku.iloc[:, 3]
    else:
        df["ICH_TENKAN"] = df["ICH_KIJUN"] = df["ICH_SENKOU_A"] = df["ICH_SENKOU_B"] = np.nan

    # 8) MFI EMA
    df["MFI_EMA"] = ta.ema(df["MFI"], length=8)

    # 9) PVT
    df["PVT"] = ta.pvt(df["close"], df["volume"])

    # 10) NVI / PVI (GÜVENLİ DATA FRAME KONTROLÜ)
    nvi_data = ta.nvi(df["close"], df["volume"])
    pvi_data = ta.pvi(df["close"], df["volume"])

    if nvi_data is not None:
        # Eğer DataFrame dönmüşse ilk kolonu (NVI değerlerini) seç
        df["NVI"] = nvi_data.iloc[:, 0] if isinstance(nvi_data, pd.DataFrame) else nvi_data
    else:
        df["NVI"] = np.nan

    if pvi_data is not None:
        # Eğer DataFrame dönmüşse ilk kolonu (PVI değerlerini) seç
        df["PVI"] = pvi_data.iloc[:, 0] if isinstance(pvi_data, pd.DataFrame) else pvi_data
    else:
        df["PVI"] = np.nan

    # 11) CHAIKIN OSCILLATOR
    df["CHAIKIN"] = ta.adosc(df["high"], df["low"], df["close"], df["volume"])

    # 12) EASE OF MOVEMENT (EOM)
    df["EOM"] = ta.eom(df["high"], df["low"], df["close"], df["volume"])

    # 13) FORCE INDEX
    df["FORCE"] = ta.efi(df["close"], df["volume"])

    # 14) ULTIMATE OSCILLATOR (UO)
    df["UO"] = ta.uo(df["high"], df["low"], df["close"])

    # 15) FISHER TRANSFORM
    fisher = ta.fisher(df["high"], df["low"])
    if fisher is not None:
        df["FISHER"] = fisher.iloc[:, 0]
        df["FISHER_SIG"] = fisher.iloc[:, 1]
    else:
        df["FISHER"] = df["FISHER_SIG"] = np.nan

    # 16) COPPOCK CURVE
    df["COPPOCK"] = ta.coppock(df["close"])

    # 17) TRIX
    trix = ta.trix(df["close"])
    if trix is not None:
        df["TRIX"] = trix.iloc[:, 0]
        df["TRIX_SIG"] = trix.iloc[:, 1]
    else:
        df["TRIX"] = df["TRIX_SIG"] = np.nan

    # 18) PPO
    ppo = ta.ppo(df["close"])
    if ppo is not None:
        df["PPO"] = ppo.iloc[:, 0]
        df["PPO_SIGNAL"] = ppo.iloc[:, 1]
    else:
        df["PPO"] = df["PPO_SIGNAL"] = np.nan
    
    # =====================================================
    # 19) FIBONACCI LEVELS (DİNAMİK PENCERE ENTEGRASYONU)
    # =====================================================
    # Config dosyasından veya varsayılan 100 barlık pencereyi alıyoruz
    fib_window = FIB_LOOKBACK if 'FIB_LOOKBACK' in globals() else 100
    
    # Son penceredeki en yüksek ve en düşük fiyatları yuvarlanan (rolling) pencere ile hesapla
    # Bu sayede her satır (bar) için geriye dönük fib seviyeleri oluşur
    df["FIB_HIGH"] = df["high"].rolling(window=fib_window).max()
    df["FIB_LOW"] = df["low"].rolling(window=fib_window).min()
    
    # Fiyat farkı
    df["FIB_DIFF"] = df["FIB_HIGH"] - df["FIB_LOW"]
    
    # İlgili Fibonacci geri çekilme seviyelerinin fiyat karşılıkları
    df["FIB_236"] = df["FIB_HIGH"] - (df["FIB_DIFF"] * 0.764)
    df["FIB_382"] = df["FIB_HIGH"] - (df["FIB_DIFF"] * 0.618)
    df["FIB_618"] = df["FIB_HIGH"] - (df["FIB_DIFF"] * 0.382)
    df["FIB_786"] = df["FIB_HIGH"] - (df["FIB_DIFF"] * 0.214)

    return df
    
if __name__ == "__main__":
    print("Genişletilmiş İndikatör Motoru Tamamlandı.")