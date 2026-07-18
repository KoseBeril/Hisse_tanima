# ==========================================================
# BIST ENGINE PRO v1.0
# trend.py
# ==========================================================
import pandas as pd

# ==========================================================
# EMA LAYER
# ==========================================================
def ema_layer(df, mode="pullback"):
    last = df.iloc[-1]
    score = 0
    reasons = []

    if mode == "pullback":
        # ------------------------------------------------------
        # Pullback Modu: Boğa Dizilimi ve Yükselen EMA Eğilimleri
        # ------------------------------------------------------
        if last["EMA20"] > last["EMA50"]:
            score += 3
            reasons.append("EMA20 > EMA50")

        if last["EMA50"] > last["EMA100"]:
            score += 3
            reasons.append("EMA50 > EMA100")

        if last["EMA100"] > last["EMA200"]:
            score += 3
            reasons.append("EMA100 > EMA200")

        if last["EMA20"] > df["EMA20"].iloc[-5]:
            score += 2
            reasons.append("EMA20 Rising")

        if last["EMA50"] > df["EMA50"].iloc[-5]:
            score += 2
            reasons.append("EMA50 Rising")

        if last["EMA100"] > df["EMA100"].iloc[-5]:
            score += 2
            reasons.append("EMA100 Rising")

        gap1 = abs(last["EMA20"] - last["EMA50"]) / last["EMA50"] * 100
        if 0.5 < gap1 < 8:
            score += 2
            reasons.append("Healthy EMA20 Gap")

        gap2 = abs(last["EMA50"] - last["EMA100"]) / last["EMA100"] * 100
        if 0.5 < gap2 < 10:
            score += 2
            reasons.append("Healthy EMA50 Gap")

        if last["close"] > last["EMA200"]:
            score += 1
            reasons.append("Above EMA200")

    elif mode == "dip":
        # ------------------------------------------------------
        # Dip Modu: Düşüşün yavaşlaması ve EMA'ların birbirine yaklaşması
        # ------------------------------------------------------
        gap_20_50 = abs(last["EMA20"] - last["EMA50"]) / last["EMA50"] * 100
        if gap_20_50 < 3.0:
            score += 6
            reasons.append("EMA20 & EMA50 Squeezing (Dip Accumulation)")

        if last["EMA20"] > df["EMA20"].iloc[-3]:
            score += 4
            reasons.append("EMA20 Flattening/Rising at Bottom")
            
        dist_to_ema200 = (last["EMA200"] - last["close"]) / last["EMA200"] * 100
        if dist_to_ema200 > 15:
            score += 5
            reasons.append(f"Oversold: Deep Below EMA200 ({dist_to_ema200:.1f}%)")
        elif last["close"] > last["EMA200"]:
            score += 3
            reasons.append("Above EMA200 Support")

    return {
        "score": score,
        "reasons": reasons
    }
print("EMA Hazır")


# ==========================================================
# STRUCTURE LAYER
# ==========================================================
def structure_layer(df, mode="pullback"):
    last = df.iloc[-1]
    score = 0
    reasons = []

    highs = df["high"].tail(10).values
    lows = df["low"].tail(10).values

    # 1. Higher High / Lower High Kontrolü
    if highs[-1] > highs[-3]:
        score += 3
        reasons.append("Higher High")
    elif highs[-1] < highs[-3]:
        if mode == "pullback":
            score -= 2
            reasons.append("Lower High")

    # 2. Higher Low / Lower Low Kontrolü
    if lows[-1] > lows[-3]:
        score += 3
        reasons.append("Higher Low")
    elif lows[-1] < lows[-3]:
        if mode == "pullback":
            score -= 2
            reasons.append("Lower Low")

    # 3. Son 20 Barın En Yükseği / En Düşüğü Kontrolü
    highest20 = df["high"].tail(20).max()
    lowest20 = df["low"].tail(20).min()

    if last["close"] >= highest20 * 0.98:
        score += 3
        reasons.append("Near 20-Bar High")

    if last["close"] <= lowest20 * 1.02:
        if mode == "pullback":
            score -= 3
            reasons.append("Near 20-Bar Low")
        elif mode == "dip":
            score += 4
            reasons.append("At 20-Bar Support (Dip Zone)")

    # 4. EMA20 Üzerinde Kalma Süresi
    ema20_count = (df["close"].tail(10) > df["EMA20"].tail(10)).sum()
    if ema20_count >= 8:
        score += 3
        reasons.append("Holding EMA20")
    elif ema20_count <= 3:
        if mode == "pullback":
            score -= 3
            reasons.append("Below EMA20")
        elif mode == "dip":
            if ema20_count >= 1:
                score += 2
                reasons.append("First Signs Above EMA20")

    # 5. Mum Renkleri (Son 5 Bar)
    green = (df["close"].tail(5) > df["open"].tail(5)).sum()
    if green >= 4:
        score += 2
        reasons.append("Bullish Candles")
    elif green <= 1:
        if mode == "pullback":
            score -= 2
            reasons.append("Bearish Candles")

    # 6. Son Dipten Uzaklaşma
    recent_low = df["low"].tail(15).min()
    distance = ((last["close"] - recent_low) / recent_low * 100)

    if distance > 5:
        score += 3
        reasons.append("Recovered From Low")
    elif distance < 1:
        if mode == "pullback":
            score -= 2
            reasons.append("Still At Bottom")
        elif mode == "dip":
            score += 4
            reasons.append("Perfect Entry: Tight at Bottom")

    return {
        "score": score,
        "reasons": reasons
    }
print("Structure Hazır")


# ==========================================================
# MOMENTUM LAYER
# ==========================================================
def momentum_layer(df):
    last = df.iloc[-1]
    prev = df.iloc[-2]
    score = 0
    reasons = []

    # Gecikmeli (Lagging) İndikatörler yerine "Eğim" (Slope) önceliği veriyoruz:
    if last["RSI"] > prev["RSI"]:
        score += 3  # Puan artırıldı
        reasons.append("RSI Rising")

    # MACD Cross henüz olmasa bile histogramın büyümesi erken dönüş sinyalidir!
    if last["MACD_HIST"] > prev["MACD_HIST"]:
        score += 4  # Gecikmeyi önlemek için histogram eğimine yüksek puan verdik
        reasons.append("MACD Histogram Turning Up (Early Momentum)")

    if last["MACD"] > last["MACD_SIGNAL"]:
        score += 2; reasons.append("MACD Bullish Cross")

    if last["ROC"] > prev["ROC"]:
        score += 2; reasons.append("ROC Rising")
        
    if last["CCI"] > prev["CCI"]:
        score += 2; reasons.append("CCI Rising")

    if last["STOCH_K"] > last["STOCH_D"]:
        score += 2; reasons.append("Stoch Bullish Cross")

    # Sıfır çizgisi üstü onaylar (Gecikmeli onaylar - daha düşük puan)
    if last["RSI"] > 50: score += 1
    if last["ROC"] > 0: score += 1
    if last["MOM"] > 0: score += 1

    return {
        "score": min(score, 20),
        "reasons": reasons
    }
print("Momentum Hazır")


# ==========================================================
# STRENGTH LAYER (Trend Gücü)
# ==========================================================
# trend.py -> strength_layer fonksiyonunun güncellenmiş hali:

def strength_layer(df, mode="pullback"):
    last = df.iloc[-1]
    prev = df.iloc[-2]
    score = 0
    reasons = []

    if mode == "pullback":
        if last["ADX"] >= 40: score += 6; reasons.append("ADX Very Strong")
        elif last["ADX"] >= 30: score += 5; reasons.append("ADX Strong")
        elif last["ADX"] >= 20: score += 3; reasons.append("ADX Moderate")
        if last["ADX"] > prev["ADX"]: score += 2; reasons.append("ADX Rising")
        else: score -= 1; reasons.append("ADX Falling")

    elif mode == "dip":
        # YENİ MANTIK: ADX mutlak değerinden ziyade yönüne bakıyoruz
        if last["ADX"] < 20:
            score += 6
            reasons.append("ADX Quiet (Accumulation Zone)")
        elif last["ADX"] < prev["ADX"]: # ADX yüksek olsa bile DÜŞÜYORSA düşüş trendi bitiyordur!
            score += 5
            reasons.append("ADX Falling (Bear Trend Exhaustion)")
        elif last["ADX"] >= 30 and last["ADX"] > prev["ADX"]:
            # Eğer ADX hala yükseliyorsa ve 30 üstüyse, düşüş hala serttir. Puan vermiyoruz.
            pass
    # ------------------------------------------------------
    # 2. DI+/- DAĞILIMI (Mevcut Mantık)
    # ------------------------------------------------------
    diff = last["DI+"] - last["DI-"]
    if diff > 15:
        score += 4
        reasons.append("DI Bullish")
    elif diff > 5:
        score += 2
        reasons.append("DI Positive")
    elif diff < -15:
        if mode == "pullback":
            score -= 4
            reasons.append("DI Bearish")
    elif diff < -5:
        if mode == "pullback":
            score -= 2
            reasons.append("DI Negative")

        # ------------------------------------------------------
        # 3. BOLLINGER BANDS ENTEGRASYONU (YENİ)
        # ------------------------------------------------------
    if "BBU" in df.columns and "BBL" in df.columns and "BBM" in df.columns:
        bb_width = (last["BBU"] - last["BBL"]) / last["BBM"] * 100
        bb_width_mean = ((df["BBU"] - df["BBL"]) / df["BBM"] * 100).tail(20).mean()

        if mode == "pullback":
            # Fiyat Üst Banta yapışık mı (Sürünme/Güçlü Trend)?
            if last["close"] >= last["BBU"] * 0.98:
                score += 4
                reasons.append("Bollinger Upper Band Ride (Strong Trend)")
            # Fiyat Orta Banttan (EMA20/SMA20) sekmiş mi (Pullback Dönüşü)?
            elif prev["low"] <= last["BBM"] and last["close"] > last["BBM"]:
                score += 3
                reasons.append("Bollinger Middle Band Support Rebound")
                
        elif mode == "dip":
            # Bollinger Bantları sıkışmış mı (Squeeze - Fırtına öncesi sessizlik)?
            if bb_width < bb_width_mean * 0.80:
                score += 5
                reasons.append(f"Bollinger Squeeze (Width: {bb_width:.1f}%)")
            # Fiyat alt banta yakın/değmiş ve tepki alıyor mu?
            if last["close"] <= last["BBL"] * 1.02:
                score += 4
                reasons.append("Bollinger Lower Band Support (Oversold)")

    # ATR & RVOL Değerlendirmeleri (Mevcut Mantık)
    atr_mean = df["ATR"].tail(20).mean()
    if last["ATR"] > atr_mean * 1.20:
        score += 2
        reasons.append("ATR Expansion")
    elif last["ATR"] < atr_mean * 0.80:
        if mode == "pullback":
            score -= 1
            reasons.append("ATR Contracting")
        elif mode == "dip":
            score += 3
            reasons.append("ATR Tightening (Volatility Squeeze)")

    if "RVOL" in df.columns:
        if last["RVOL"] >= 2:
            score += 4
            reasons.append("Very High Volume")
        elif last["RVOL"] >= 1.2:
            score += 3
            reasons.append("High Volume")

    score = max(min(score, 20), 0) # 20 puanlık limit korunuyor
    return {
        "score": score,
        "reasons": reasons
    }
print("Strength Hazır")


# ==========================================================
# PERFORMANCE LAYER
# ==========================================================
def performance_layer(df, mode="pullback"):
    score = 0
    reasons = []
    last = df.iloc[-1]

    performances = {
        "5": ((last["close"] - df["close"].iloc[-5]) / df["close"].iloc[-5] * 100),
        "10": ((last["close"] - df["close"].iloc[-10]) / df["close"].iloc[-10] * 100),
        "20": ((last["close"] - df["close"].iloc[-20]) / df["close"].iloc[-20] * 100),
        "50": ((last["close"] - df["close"].iloc[-50]) / df["close"].iloc[-50] * 100)
    }

    if mode == "pullback":
        if performances["5"] > 2: score += 3; reasons.append("5 Bar Up")
        elif performances["5"] < -3: score -= 3; reasons.append("5 Bar Down")

        if performances["10"] > 4: score += 4; reasons.append("10 Bar Up")
        elif performances["10"] < -5: score -= 4; reasons.append("10 Bar Down")

        if performances["20"] > 8: score += 6; reasons.append("20 Bar Up")
        elif performances["20"] < -8: score -= 6; reasons.append("20 Bar Down")

        if performances["50"] > 15: score += 7; reasons.append("50 Bar Up")
        elif performances["50"] < -12: score -= 7; reasons.append("50 Bar Down")

    elif mode == "dip":
        if performances["50"] < -15:
            score += 8
            reasons.append("50 Bar Heavily Discounted")
        elif performances["50"] < -8:
            score += 4
            reasons.append("50 Bar Discounted")

        if performances["20"] < -10:
            score += 4
            reasons.append("20 Bar Down (Bottoming Base)")

        if performances["5"] > 1.5:
            score += 5
            reasons.append("5 Bar Early Bounce")

    return {
        "score": score,
        "reasons": reasons,
        "perf": performances
    }
print("Performance Hazır")


# ==========================================================
# TREND CLASSIFICATION & ANALYZE
# ==========================================================
def trend_classification(score, mode="pullback"):
    if mode == "pullback":
        if score >= 80: return "STRONG_UP"
        elif score >= 65: return "UP"
        elif score >= 45: return "RECOVERY"
        elif score >= 25: return "SIDEWAYS"
        elif score >= 10: return "EARLY_DOWN"
        return "STRONG_DOWN"
    else:
        if score >= 70: return "STRONG_ACCUMULATION_DIP"
        elif score >= 50: return "ACCUMULATION_DIP"
        elif score >= 35: return "EARLY_REBOUND"
        elif score >= 20: return "BOTTOM_SIDEWAYS"
        return "HEAVY_DOWN_TREND"


def analyze_trend(df, mode="pullback"):
    ema = ema_layer(df, mode=mode)
    structure = structure_layer(df, mode=mode)
    momentum = momentum_layer(df)
    strength = strength_layer(df, mode=mode)
    performance = performance_layer(df, mode=mode)

    total = (
        ema["score"]
        + structure["score"]
        + momentum["score"]
        + strength["score"]
        + performance["score"]
    )

    total = max(0, total)
    trend = trend_classification(total, mode=mode)

    reasons = (
        ema["reasons"]
        + structure["reasons"]
        + momentum["reasons"]
        + strength["reasons"]
        + performance["reasons"]
    )

    return {
        "score": total,
        "max_score": 100,
        "trend": trend,
        "strong": total >= (80 if mode == "pullback" else 65),
        "reasons": reasons,
        "layers": {
            "EMA": ema["score"],
            "STRUCTURE": structure["score"],
            "MOMENTUM": momentum["score"],
            "STRENGTH": strength["score"],
            "PERFORMANCE": performance["score"]
        },
        "details": {
            "EMA": ema,
            "STRUCTURE": structure,
            "MOMENTUM": momentum,
            "STRENGTH": strength,
            "PERFORMANCE": performance
        }
    }

if __name__ == "__main__":
    print("Trend Motoru Hazır")