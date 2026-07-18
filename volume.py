# ==========================================================
# BIST ENGINE PRO
# volume.py
# ==========================================================
import pandas as pd

# ----------------------------------------------------------
# RVOL Layer 
# ----------------------------------------------------------
def rvol_layer(df):
    score = 0
    reasons = []
    last = df.iloc[-1]
    if last["RVOL"] > 1.20 and last["RVOL"] < 2:
        score += 5
        reasons.append("RVOL > 1.2")
    elif last["RVOL"] > 2:
        score += 10
        reasons.append("RVOL > 2")
    return score, reasons

# ----------------------------------------------------------
# OBV Layer 
# ----------------------------------------------------------

def obv_layer(df):
    score = 0
    reasons = []
    last = df.iloc[-1]
    if last["OBV"] > df["OBV"].iloc[-10]:
        score += 5
        reasons.append("OBV Rising")
    if df["OBV"].iloc[-1] > df["OBV"].iloc[-2] > df["OBV"].iloc[-3]:
        score += 5
        reasons.append("OBV Momentum")
    return score, reasons
print("OBV hazır")

# ----------------------------------------------------------
# CMF Layer 
# ----------------------------------------------------------

def cmf_layer(df):
    score = 0
    reasons = []
    last = df.iloc[-1]
    if last["CMF"] > 0:
        score += 5
        reasons.append("CMF Positive")
    if last["CMF"] > 0.10:
        score += 2
        reasons.append("Strong CMF")
    if last["CMF"] > df["CMF"].iloc[-5]:
        score += 3
        reasons.append("CMF Rising")
    return score, reasons
print("CMF hazır")

# ----------------------------------------------------------
# A/D Layer
# ----------------------------------------------------------

def ad_layer(df):
    score = 0
    reasons = []
    last = df.iloc[-1]
    if last["AD"] > df["AD"].iloc[-10]:
        score += 5
        reasons.append("A/D Rising")
    if df["AD"].iloc[-1] > df["AD"].iloc[-2] > df["AD"].iloc[-3]:
        score += 5
        reasons.append("A/D Momentum")
    return score, reasons
print("A/D hazır")

# ----------------------------------------------------------
# VWAP Layer
# ----------------------------------------------------------

def vwap_layer(df):
    last = df.iloc[-1]
    score = 0
    reasons = []
    if last["close"] > last["VWAP"]:
        score += 5
        reasons.append("Close > VWAP")
    if len(df) >= 5:
        if df["VWAP"].iloc[-1] > df["VWAP"].iloc[-5]:
            score += 5
            reasons.append("VWAP Rising")
    return score, reasons
print("VWAP hazır")

# ----------------------------------------------------------
# Volume Spike
# ----------------------------------------------------------
def spike_layer(df):
    last = df.iloc[-1]
    score = 0
    reasons = []
    if last["RVOL"] >= 1.5:
        score += 5
        reasons.append("RVOL > 1.5")
    if last["RVOL"] >= 2:
        score += 3
        reasons.append("RVOL > 2")
    if last["RVOL"] >= 3:
        score += 2
        reasons.append("RVOL > 3")
    return score, reasons

# ----------------------------------------------------------
# Dry Volume Layer
# ----------------------------------------------------------
def dry_volume_layer(df):
    score = 0
    reasons = []
    if len(df) < 12:
        return 0, []
    vol_old = df["volume"].iloc[-10:-5].mean()
    vol_new = df["volume"].iloc[-5:].mean()
    if vol_new < vol_old:
        score += 5
        reasons.append("Volume Drying")
    price_change = (abs(df["close"].iloc[-1] - df["close"].iloc[-5]) / df["close"].iloc[-5]) * 100
    if price_change < 3:
        score += 5
        reasons.append("Price Stable")
    return score, reasons

# ------------------------------------------------------
# Hacim Genişlemesi
# ------------------------------------------------------
def expansion_layer(df):
    last = df.iloc[-1]
    prev = df.iloc[-2]
    score = 0
    reasons = []
    if last["volume"] > prev["volume"]:
        score += 5
        reasons.append("Volume Increasing")
    if last["RVOL"] > prev["RVOL"]:
        score += 5
        reasons.append("RVOL Increasing")
    if last["close"] > prev["close"] and last["volume"] > prev["volume"]:
        score += 10
        reasons.append("Price + Volume Expansion")
    return score, reasons

# ------------------------------------------------------
# Kurumsal Akümülasyon
# ------------------------------------------------------
def accumulation_layer(df):
    last = df.iloc[-1]
    score = 0
    reasons = []
    if last["RVOL"] > 1.20:
        score += 5
        reasons.append("RVOL")
    if last["CMF"] > 0:
        score += 5
        reasons.append("CMF Positive")
    if last["OBV"] > df["OBV"].tail(20).mean():
        score += 5
        reasons.append("OBV Rising")
    if last["AD"] > df["AD"].tail(20).mean():
        score += 5
        reasons.append("A/D Rising")
    if last["close"] > last["VWAP"]:
        score += 5
        reasons.append("Above VWAP")
    return score, reasons

# ------------------------------------------------------
# Dağıtım Kontrolü
# ------------------------------------------------------
def distribution_layer(df):
    last = df.iloc[-1]
    score = 0
    reasons = []
    if last["CMF"] < 0:
        score -= 5
        reasons.append("CMF Negative")
    if last["OBV"] < df["OBV"].tail(20).mean():
        score -= 5
        reasons.append("OBV Falling")
    if last["AD"] < df["AD"].tail(20).mean():
        score -= 5
        reasons.append("A/D Falling")
    if last["close"] < df["close"].iloc[-2] and last["RVOL"] > 1.5:
        score -= 10
        reasons.append("High Volume Selling")
    return score, reasons

# ----------------------------------------------------------
# Volume Sınıflandırması
# ----------------------------------------------------------
def volume_classification(score):
    if score >= 90: return "HEAVY_ACCUMULATION"
    elif score >= 75: return "ACCUMULATION"
    elif score >= 60: return "EARLY_ACCUMULATION"
    elif score >= 45: return "NEUTRAL"
    elif score >= 30: return "DISTRIBUTION"
    return "HEAVY_DISTRIBUTION"

# ----------------------------------------------------------
# Volume Motoru (MOD DESTEKLİ)
# ----------------------------------------------------------
def analyze_volume(df, mode="pullback"):
    score = 0
    reasons = []
    layers = {}

    # Temel Hacim İndikatörleri (OBV, CMF, A/D, VWAP) standart hesaplanır
    s, r = rvol_layer(df); score += s; reasons.extend(r); layers["RVOL"] = s
    s, r = obv_layer(df); score += s; reasons.extend(r); layers["OBV"] = s
    s, r = cmf_layer(df); score += s; reasons.extend(r); layers["CMF"] = s
    s, r = ad_layer(df); score += s; reasons.extend(r); layers["AD"] = s
    s, r = vwap_layer(df); score += s; reasons.extend(r); layers["VWAP"] = s

    # DİNAMİK ÇATIŞMA ÇÖZÜMÜ:
    last = df.iloc[-1]
    prev = df.iloc[-2]

    # Eğer son barda belirgin bir canlanma varsa (EKOS'un yeşil mumu gibi) EXPANSION çalışsın
    if last["volume"] > prev["volume"] or last["RVOL"] > 1.0:
        s, r = expansion_layer(df)
        score += s; reasons.extend(r); layers["EXPANSION"] = s
        layers["DRY"] = 0 # Çatışmayı önlemek için kuruma puanını sıfırlıyoruz
    else:
        # Eğer tahta hala sessizce mal toplanma evresindeyse DRY VOLUME çalışsın
        s, r = dry_volume_layer(df)
        if mode == "dip" and s > 0:
            s += 5
            r.append("Dip Mode Dry Volume Bonus")
        score += s; reasons.extend(r); layers["DRY"] = s
        layers["EXPANSION"] = 0

    # Spike ve Accumulation katmanları eklenir
    s, r = spike_layer(df); score += s; reasons.extend(r); layers["SPIKE"] = s
    
    s, r = accumulation_layer(df)
    if mode == "dip" and s > 0:
        s += 5
        r.append("Dip Mode Accumulation Bonus")
    score += s; reasons.extend(r); layers["ACCUMULATION"] = s

    s, r = distribution_layer(df); score += s; reasons.extend(r); layers["DISTRIBUTION"] = s

    score = max(0, min(score, 100))
    return {
        "score": score,
        "max_score": 100,
        "class": volume_classification(score),
        "layers": layers,
        "reasons": reasons
    }
print("Volume Motoru hazır")