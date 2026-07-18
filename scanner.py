# ==========================================================
# BIST ENGINE PRO
# scanner.py
# TradingView Screener + tvDatafeed
# ==========================================================

from tradingview_screener import Query
from tvDatafeed import TvDatafeed
from config import *

# ----------------------------------------------------------
# TradingView
# ----------------------------------------------------------

tv = TvDatafeed()

# ----------------------------------------------------------
# BIST Hisse Listesi
# ----------------------------------------------------------

def get_bist_symbols():

    rows, df = (
        Query()
        .set_markets("turkey")
        .set_property("interval", "1D")
        .select(

            "name",

            "close",

            "volume",

            "RSI",

            "ADX",

            "EMA20",

            "EMA50",

            "relative_volume_10d_calc"

        )
        .limit(1000)
        .get_scanner_data()
    )

    return df


# ----------------------------------------------------------
# Ön Eleme
# ----------------------------------------------------------

def pre_filter(df, mode = "dip"): # trendden gelen dinsmik mod eklenecek
    
    """
    Hisseleri temel teknik kriterlere göre ön elemeye tabi tutar.
    Modlar:
      - 'pullback' : Yükselen trendde geri çekilip toparlanan hisseler (Mevcut mantık)
      - 'dip'      : Düşüş trendini tamamlamış, erken dönüş sinyali veren dip hisseler
    """
    print("pre_filter başladı")

    df = df.copy()

    # --------------------------------------------------
    # Ortak Kriter: Relative Volume (Hacim Canlılığı)
    # Her iki modda da tahtanın tamamen ölü olmamasını istiyoruz.
    # --------------------------------------------------
    df = df[
        df["relative_volume_10d_calc"] > 0.70 ### volume kısmına mı eklenecek
    ]

    # sadece gerçek dip istiyrsan bu kısmı komple atabilirsin (pullback mode)
    # bu durumda dip moduna volume sınıını eklemeyi unutma
    if mode == "pullback":
        # Yükselen trend korunduğu için EMA20, EMA50'nin üzerinde olmalı
        df = df[df["EMA20"] > df["EMA50"]]
        
        # RSI aşırı satımda olmamalı, trend yönü yukarı olmalı
        df = df[df["RSI"] > 35] # RSI da değiştirilebilir
        
        # ADX güçlü bir trend olduğunu doğrulamalı
        df = df[df["ADX"] > 15] # daha yükseltilebilir, 20 daha güvenli olabilir

    elif mode == "dip":
        # 1. EMA Çelişkisi Çözümü: 
        # Erken dipte EMA20 > EMA50 şartı aranmaz. Hatta genellikle EMA20 < EMA50 durumundadır.
        df = df[
            df["EMA20"] < df["EMA50"] # dip için ema20 < ema50 olmalı 
        # tam tersinde ise yükseliş olur
        ]
        
        # 2. RSI Çelişkisi Çözümü:
        # rsi_layer() fonksiyonunun son 80 barda <25 veya <30 dip puanlarını yakalayabilmesi için
        # ön elemedeki alt sınırı 20'ye çekiyoruz. Üst sınırı ise 50-55 yaparak aşırı yükselmişleri eliyoruz.
        df = df[
            (df["RSI"] >= 20) & (df["RSI"] <= 55)
        ]
        
        # 3. ADX Çelişkisi Çözümü:
        # Dip bölgelerinde trend gücü (ADX) zayıflamıştır (yatay/akümülasyon evresi).
        # ADX'in çok yüksek olmamasını (örneğin ADX < 30) tercih ederiz. ADX > 12 şartını kaldırıyoruz.
        df = df[df["ADX"] < 30]

    print(f"Filtre sonrası : {len(df)} hisse")

    return df.reset_index(drop=True)


# ----------------------------------------------------------
# Veri Kalitesi
# ----------------------------------------------------------
# kodda kullanılmıyor gerekirse sonradan eklenebilir

def quality_filter(df):

    if df is None:
        return False

    if len(df) < 200:
        return False

    if df.isnull().sum().sum() > 0:
        return False

    return True


# ----------------------------------------------------------
# Mum Verisi
# ----------------------------------------------------------

def get_history(symbol):

    try:

        data = tv.get_hist(

            symbol=symbol,

            exchange="BIST",

            interval=TIMEFRAME,

            n_bars=BARS

        )

        if data is None:
            return None

        if data.empty:
            return None

        return data

    except Exception:

        return None
