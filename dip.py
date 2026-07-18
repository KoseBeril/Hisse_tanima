# ==========================================================
# BIST ENGINE PRO v1.0
# dip.py
# ==========================================================
import numpy as np
import pandas as pd

# ----------------------------------------------------------
# RSI Katmanı
# Maksimum : 20 Puan
# ----------------------------------------------------------
def rsi_layer(df, mode="dip"):
    score = 0
    reasons = []
    last = df.iloc[-1]
    prev = df.iloc[-2]
    rsi = df["RSI"]

    # Son 80 barda dip görülmüş mü? #### bar sayısı düşürüldü.
    min_rsi = rsi.tail(50).min()

    if mode == "dip":
        if min_rsi < 30:
            score += 5
            reasons.append(f"RSI Çok Dip ({min_rsi:.1f})")
        elif min_rsi < 38:
            score += 4
            reasons.append(f"RSI Dip ({min_rsi:.1f})")
        elif min_rsi < 45:
            score += 2
            reasons.append(f"RSI Zayıf Dip ({min_rsi:.1f})")
    elif mode == "pullback":
        # Pullback modunda RSI'ın 80 bar önceki ağır dibinden ziyade, yakın zamanlı 40-50 seviyelerinden sekmesi aranır
        if 40 <= min_rsi <= 50:
            score += 4
            reasons.append(f"RSI Pullback Zone Support ({min_rsi:.1f})")

    # RSI yükseliyor mu?
    if last["RSI"] > prev["RSI"]:
        score += 2
        reasons.append("RSI Yükseliyor")

    # RSI EMA kesişimi
    if prev["RSI"] < prev["RSI_EMA"] and last["RSI"] > last["RSI_EMA"]:
        score += 5
        reasons.append("RSI EMA Yukarı Kesti")

    # RSI 50 altındayken dönüyor mu?
    if 30 <= last["RSI"] <= 50:
        score += 2
        reasons.append("RSI Erken Toparlanma")

    # RSI son 5 bardır yükseliyor mu?
    last5 = rsi.tail(5).values
    if all(np.diff(last5) > 0):
        score += 3
        reasons.append("RSI 5 Bardır Artıyor")

    # RSI eğimi pozitif mi?
    slope = last["RSI"] - rsi.iloc[-6]
    if slope > 5:
        score += 3
        reasons.append("RSI Güçlü Eğilim")
    elif slope > 2:
        score += 2
        reasons.append("RSI Pozitif Eğilim")

    return {
        "score": min(score, 20),
        "reasons": reasons,
        "min_rsi": round(min_rsi, 2),
        "current_rsi": round(last["RSI"], 2),
        "current_rsi_ema": round(last["RSI_EMA"], 2)
    }
print("RSI Hazır")


# ==========================================================
# MACD LAYER
# Maksimum Puan : 20
# ==========================================================
def macd_layer(df, mode="dip"):
    score = 0
    reasons = []
    last = df.iloc[-1]
    prev = df.iloc[-2]

    # 1) MACD Yukarı Kesişim
    if prev["MACD"] < prev["MACD_SIGNAL"] and last["MACD"] > last["MACD_SIGNAL"]:
        score += 6
        reasons.append("MACD Bullish Cross")

    # 2) Histogram Güçleniyor
    hist = df["MACD_HIST"].tail(5)
    if hist.iloc[-1] > hist.iloc[-2]:
        score += 3
        reasons.append("Histogram Rising")

    # 3) Histogram Negatiften Toparlanıyor
    if hist.min() < 0 and hist.iloc[-1] > hist.mean():
        score += 2
        reasons.append("Histogram Recovery")

    # 4) MACD Eğimi Yukarı
    if last["MACD"] > prev["MACD"]:
        score += 3
        reasons.append("MACD Rising")

    # 5) Signal Eğimi Yukarı
    if last["MACD_SIGNAL"] > prev["MACD_SIGNAL"]:
        score += 2
        reasons.append("Signal Rising")

    # 6) MACD Sıfıra Yaklaşıyor (Sadece Dip modunda negatiftir)
    if mode == "dip":
        if last["MACD"] < 0 and abs(last["MACD"]) < abs(prev["MACD"]):
            score += 2
            reasons.append("MACD Recovering")
    elif mode == "pullback":
        # Pullback modunda MACD'nin sıfır çizgisi üstünde kesmesi istenir
        if last["MACD"] > 0:
            score += 2
            reasons.append("MACD Positive Zone")

    # 7) Histogram Pozitife Geçti
    if prev["MACD_HIST"] < 0 and last["MACD_HIST"] > 0:
        score += 2
        reasons.append("Histogram Positive")

    return {
        "score": min(score, 20),
        "reasons": reasons
    }
print("MACD Hazır")


# ==========================================================
# MOMENTUM LAYER
# Maksimum : 20 Puan
# ==========================================================
def momentum_layer(df):
    score = 0
    reasons = []
    last = df.iloc[-1]
    prev = df.iloc[-2]

    # MOM
    if last["MOM"] > 0:
        score += 4
        reasons.append("Momentum Positive")
    if last["MOM"] > prev["MOM"]:
        score += 4
        reasons.append("Momentum Rising")

    # ROC
    if last["ROC"] > 0:
        score += 4
        reasons.append("ROC Positive")
    if last["ROC"] > prev["ROC"]:
        score += 4
        reasons.append("ROC Rising")

    # Güçlenme
    if last["ROC"] > 0 and last["MOM"] > 0:
        score += 4
        reasons.append("Momentum Confirmed")

    return {
        "score": min(score, 20),
        "reasons": reasons
    }
print("Momentum Hazır")


# ==========================================================
# OSCILLATOR LAYER
# Maksimum : 20 Puan
# ==========================================================
def oscillator_layer(df, mode="dip"):
    score = 0
    reasons = []
    last = df.iloc[-1]
    prev = df.iloc[-2]

    # CCI
    if mode == "dip":
        if last["CCI"] > -100:
            score += 5
            reasons.append("CCI Recovery")
    elif mode == "pullback":
        # Pullback modunda CCI'ın +100 referans çizgisini kırması istenir
        if last["CCI"] > 100:
            score += 5
            reasons.append("CCI Bullish Breakout (>100)")

    if last["CCI"] > prev["CCI"]:
        score += 2
        reasons.append("CCI Rising")

    # Williams
    if mode == "dip":
        if last["WILLR"] > -80:
            score += 3
            reasons.append("Williams Recovery")
    elif mode == "pullback":
        # Pullback modunda Williams'ın -20 aşırı alım bölgesine girmesi istenir
        if last["WILLR"] > -20:
            score += 3
            reasons.append("Williams Momentum (> -20)")

    # Stochastic
    if prev["STOCH_K"] < prev["STOCH_D"] and last["STOCH_K"] > last["STOCH_D"]:
        score += 5
        reasons.append("Stochastic Bullish Cross")

    # Money Flow
    if last["MFI"] > 50:
        score += 3
        reasons.append("Money Flow Positive")
    if last["MFI"] > prev["MFI"]:
        score += 2
        reasons.append("Money Flow Rising")

    return {
        "score": min(score, 20),
        "reasons": reasons
    }
print("Oscillator Hazır")


# ==========================================================
# VOLUME LAYER
# Maksimum Puan : 20
# ==========================================================
def volume_layer(df, mode="dip"):
    score = 0
    reasons = []
    last = df.iloc[-1]
    prev = df.iloc[-2]

    # RVOL
    if last["RVOL"] > 1.20:
        score += 5
        reasons.append("RVOL > 1.20")
    elif last["RVOL"] > 1:
        score += 3
        reasons.append("RVOL > 1")

    # Hacim Artıyor
    if last["volume"] > prev["volume"]:
        score += 2
        reasons.append("Volume Rising")

    # 5 Bar Ortalama
    if last["volume"] > df["volume"].tail(5).mean():
        score += 2
        reasons.append("Above 5 Bar Volume")

    # 20 Bar Ortalama
    if last["volume"] > df["VOL20"].iloc[-1]:
        score += 3
        reasons.append("Above VOL20")

    # OBV
    if last["OBV"] > df["OBV"].iloc[-2]:
        score += 3
        reasons.append("OBV Rising")

    # CMF
    if last["CMF"] > 0:
        score += 3
        reasons.append("Positive CMF")

    # Hacim Patlaması
    if mode == "dip":
        # Dip bölgelerinde hacim patlaması toplanma emaresidir
        if last["volume"] > df["volume"].tail(20).max() * 0.90:
            score += 2
            reasons.append("Volume Spike")
    elif mode == "pullback":
        # Pullback dönüşlerinde hacmin kuruması ve dönüşte patlaması istenir
        if last["volume"] > df["volume"].tail(5).max() * 0.95:
            score += 2
            reasons.append("Pullback Volume Trigger")

    return {
        "score": min(score, 20),
        "reasons": reasons
    }
print("Volume Hazır")


# ==========================================================
# STRUCTURE LAYER
# Maksimum Puan : 20
# ==========================================================
def structure_layer_dip(df, mode="dip"):
    score = 0
    reasons = []
    highs = df["high"].tail(20).reset_index(drop=True)
    lows = df["low"].tail(20).reset_index(drop=True)
    last = df.iloc[-1]

    # Higher Low
    if lows.iloc[-1] > lows.iloc[-5]:
        score += 4
        reasons.append("Higher Low")

    # Higher High
    if highs.iloc[-1] > highs.iloc[-5]:
        score += 4
        reasons.append("Higher High")

    # Son 10 Barın Dibi Korunmuş
    if last["low"] > lows.min():
        score += 2
        reasons.append("Lowest Low Protected")

    # Son Kapanış Son 10 Bar Ortalamasının Üzerinde
    if last["close"] > df["close"].tail(10).mean():
        score += 3
        reasons.append("Above 10 Bar Average")

    # Son Dipten %3 Yukarı
    recent_low = lows.min()
    gain = ((last["close"] - recent_low) / recent_low * 100)

    if mode == "dip":
        if gain > 3:
            score += 3
            reasons.append("Recovered From Bottom")
    elif mode == "pullback":
        # Pullback modunda %3 değil %1.5-2 gibi yakın bir dönüş de yeterli olabilir
        if gain > 1.5:
            score += 3
            reasons.append("Pullback Pivot Confirmed")

    # Swing Low Oluşmuş
    if lows.iloc[-3] < lows.iloc[-4] and lows.iloc[-3] < lows.iloc[-2]:
        score += 2
        reasons.append("Swing Low")

    # Son Mum Güçlü
    body = abs(last["close"] - last["open"])
    candle = last["high"] - last["low"]
    if candle > 0 and body / candle > 0.60:
        score += 2
        reasons.append("Strong Bull Candle")

    return {
        "score": min(score, 20),
        "reasons": reasons
    }
print("Structure Hazır")


# ==========================================================
# VOLATILITY LAYER
# Maksimum Puan : 20
# ==========================================================

def volatility_layer_dip(df, mode="dip"):
    score = 0
    reasons = []
    last = df.iloc[-1]

    # 1. Bollinger Bant Genişliği (BB Width) ile Sıkışma Kontrolü (YENİ)
    if "BBU" in df.columns and "BBL" in df.columns and "BBM" in df.columns:
        bb_width = (last["BBU"] - last["BBL"]) / last["BBM"] * 100
        bb_width_mean = ((df["BBU"] - df["BBL"]) / df["BBM"] * 100).tail(20).mean()

        # Son bant genişliği 20 barlık ortalama genişliğin belirgin şekilde altındaysa
        if bb_width < bb_width_mean * 0.80:
            score += 6
            reasons.append(f"BB Squeeze Confirmed (Width: {bb_width:.1f}%)")
        elif bb_width < bb_width_mean * 0.95:
            score += 3
            reasons.append("BB Squeezing")

    # ATR küçülüyor mu? (Mevcut Mantık)
    atr_old = df["ATR"].tail(20).head(10).mean()
    atr_new = df["ATR"].tail(10).mean()
    if atr_new < atr_old:
        score += 4  # (Dengelemek için puanı 5'ten 4'e çektik, limit 20)
        reasons.append("ATR Contracting")

    # Mum aralıkları daralıyor mu? (Mevcut Mantık)
    ranges = df["high"] - df["low"]
    old_range = ranges.tail(20).head(10).mean()
    new_range = ranges.tail(10).mean()
    if new_range < old_range:
        score += 3
        reasons.append("Range Contracting")

    # Son 5 mum daha sakin mi? (Mevcut Mantık)
    std_old = df["close"].tail(20).head(10).std()
    std_new = df["close"].tail(10).std()
    if std_new < std_old:
        score += 3
        reasons.append("Price Stabilizing")

    # ATR fiyatın çok altında mı? (Mevcut Mantık)
    atr_percent = last["ATR"] / last["close"] * 100
    if mode == "dip":
        if atr_percent < 3:
            score += 4
            reasons.append("Low ATR")
    elif mode == "pullback":
        if atr_percent < 4.5:
            score += 4
            reasons.append("Low ATR (Squeeze for Pullback)")

    return {
        "score": min(score, 20), # 20 Puan limiti korunuyor
        "reasons": reasons
    }
print("Volatility Hazır")


# ==========================================================
# RECOVERY LAYER
# Maksimum Puan : 20
# ==========================================================
def recovery_layer_dip(df, mode="dip"):
    score = 0
    reasons = []
    last = df.iloc[-1]

    # Son 5 barın en yükseğine yakın mı?
    high5 = df["high"].tail(5).max()
    if last["close"] >= high5 * 0.98:
        score += 4
        reasons.append("Near 5-Bar High")

    # EMA20 üzerine çıktı mı?
    if last["close"] > last["EMA20"]:
        score += 4
        reasons.append("Above EMA20")

    # EMA20 yukarı dönüyor mu?
    if df["EMA20"].iloc[-1] > df["EMA20"].iloc[-2]:
        score += 4
        reasons.append("EMA20 Rising")

    # Son 3 mum yükseliş yönlü mü?
    closes = df["close"].tail(3).values
    if closes[2] > closes[1] > closes[0]:
        score += 4
        reasons.append("3 Higher Closes")

    # Son mum yeşil mi?
    if last["close"] > last["open"]:
        score += 4
        reasons.append("Bullish Candle")

    return {
        "score": min(score, 20),
        "reasons": reasons
    }
print("Recovery Hazır")


# ==========================================================
# SUPPORT LAYER
# Maksimum : 20
# ==========================================================
# dip.py -> support_layer_dip fonksiyonunun güncellenmiş hali:

def support_layer_dip(df, mode="dip"):
    score = 0
    reasons = []
    last = df.iloc[-1]
    prev = df.iloc[-2]

    low20 = df["low"].tail(20).min()
    low50 = df["low"].tail(50).min()

    dist20 = (last["close"] - low20) / low20 * 100
    dist50 = (last["close"] - low50) / low50 * 100

    if mode == "dip":
        if dist20 <= 8: # toleransı arttırdı 
            score += 6
            reasons.append("Near 20-Bar Support")
        if dist50 <= 12:
            score += 6
            reasons.append("Near 50-Bar Support")
            
        # Bollinger Alt Bant Desteği (YENİ)
        if "BBL" in df.columns:
            if last["close"] <= last["BBL"] * 1.015:
                score += 8
                reasons.append("At Bollinger Lower Band Support")
            elif prev["close"] < prev["BBL"] and last["close"] > last["BBL"]:
                score += 10
                reasons.append("Bollinger Lower Band Fakeout & Reclaim")

    elif mode == "pullback":
        if abs(last["close"] - last["EMA50"]) / last["EMA50"] * 100 <= 2:
            score += 6
            reasons.append("EMA50 Pullback Support")
        if abs(last["close"] - last["EMA100"]) / last["EMA100"] * 100 <= 3:
            score += 6
            reasons.append("EMA100 Pullback Support")
            
        # Bollinger Orta Bant Desteği (YENİ)
        if "BBM" in df.columns:
            if abs(last["close"] - last["BBM"]) / last["BBM"] * 100 <= 1.5:
                score += 8
                reasons.append("Bollinger Middle Band Pullback Support")

    # EMA20 desteği
    if last["close"] > last["EMA20"]:
        score += 4
        reasons.append("Above EMA20")

    return {
        "score": min(score, 20), # 20 Puan limiti korunuyor
        "reasons": reasons
    }
print("Support Hazır")


# ==========================================================
# DIVERGENCE LAYER
# Maksimum : 20
# ==========================================================
def divergence_layer_dip(df, mode="dip"):
    score = 0
    reasons = []

    # Son 10-5 bar arası ile son 5 barın en düşüklerini kıyaslıyoruz
    price_low1 = df["low"].iloc[-10:-5].min()
    price_low2 = df["low"].iloc[-5:].min()

    rsi_low1 = df["RSI"].iloc[-10:-5].min()
    rsi_low2 = df["RSI"].iloc[-5:].min()

    if mode == "dip":
        # A) KLASİK POZİTİF UYUMSUZLUK (Fiyat düşüyor, RSI yükseliyor)
        if price_low2 < price_low1 and rsi_low2 > rsi_low1:
            score += 20
            reasons.append("Bullish RSI Divergence (Classic)")

        # B) GİZLİ POZİTİF UYUMSUZLUK (Fiyat yükseliyor/HL, RSI düşüyor/LL)
        elif price_low2 > price_low1 and rsi_low2 < rsi_low1:
            score += 20  # En az klasik kadar değerlidir
            reasons.append("Hidden Bullish RSI Divergence (Strong Rebound)")

        # C) UYUMSUZLUK YOK AMA TREND BAŞLANGICI (Fiyat da RSI da yükseliyor)
        elif price_low2 > price_low1 and rsi_low2 > rsi_low1:
            score += 12  # Uyumsuzluk yok ama yapı pozitif
            reasons.append("Healthy Higher Low Structure (Price & RSI)")

    return {
        "score": min(score, 20),
        "reasons": reasons
    }
print("Divergence Hazır")


# ==========================================================
# DIP CLASSIFICATION
# ==========================================================
def dip_classification_label(score, mode="dip"):
    if mode == "dip":
        if score >= 85: return "PERFECT_DIP"
        elif score >= 70: return "STRONG_DIP"
        elif score >= 55: return "EARLY_RECOVERY"
        elif score >= 40: return "WATCH"
        elif score >= 20: return "WEAK"
        return "NO_DIP"
    else:
        # Pullback modunda Dip Engine'in yakaladığı skorlar konsolidasyonu temsil eder
        if score >= 80: return "HEALTHY_CONSOLIDATION_PULLBACK"
        elif score >= 60: return "STABLE_PULLBACK"
        return "WEAK_PULLBACK"


# ==========================================================
# DIP ENGINE
# ==========================================================
def analyze_dip(df, mode="dip"):
    rsi = rsi_layer(df, mode=mode)
    macd = macd_layer(df, mode=mode)
    momentum = momentum_layer(df)
    osc = oscillator_layer(df, mode=mode)
    volume = volume_layer(df, mode=mode)
    structure = structure_layer_dip(df, mode=mode)
    vola = volatility_layer_dip(df, mode=mode)
    recovery = recovery_layer_dip(df, mode=mode)
    support = support_layer_dip(df, mode=mode)
    div = divergence_layer_dip(df, mode=mode)

    total = (
        rsi["score"]
        + macd["score"]
        + momentum["score"]
        + osc["score"]
        + volume["score"]
        + structure["score"]
        + vola["score"]
        + recovery["score"]
        + support["score"]
        + div["score"]
    )

    total = max(0, total)

    reasons = (
        rsi["reasons"]
        + macd["reasons"]
        + momentum["reasons"]
        + osc["reasons"]
        + volume["reasons"]
        + structure["reasons"]
        + vola["reasons"]
        + recovery["reasons"]
        + support["reasons"]
        + div["reasons"]
    )

    return {
        "score": total,
        "max_score": 200,
        "class": dip_classification_label(total, mode=mode),
        "reasons": reasons,
        "layers": {
            "RSI": rsi["score"],
            "MACD": macd["score"],
            "MOMENTUM": momentum["score"],
            "OSC": osc["score"],
            "VOLUME": volume["score"],
            "STRUCTURE": structure["score"],
            "VOLATILITY": vola["score"],
            "RECOVERY": recovery["score"],
            "SUPPORT": support["score"],
            "DIVERGENCE": div["score"]
        }
    }

if __name__ == "__main__":
    print("Dip Motoru Hazır")