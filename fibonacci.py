import numpy as np
import pandas as pd


def calculate_fibonacci_dip_score(df, lookback_period=100):
    """Belirlenen periyottaki Fibonacci dip bölgelerini ve fiyata olan mesafesini puanlar."""
    if len(df) < lookback_period:
        return 0, "Yetersiz Veri"

    # Son 'lookback_period' mum verisi
    recent_df = df.iloc[-lookback_period:]

    highest_high = recent_df["high"].max()
    lowest_low = recent_df["low"].min()
    current_close = df.iloc[-1]["close"]

    diff = highest_high - lowest_low
    if diff == 0:
        return 0, "Yatay Piyasa"

    # ------------------------------------------------------
    # Doğru Fibonacci Seviyeleri (Dipten Yukarıya Yüzdelik Mesafe)
    # ------------------------------------------------------
    fib_0 = lowest_low  # %0 (Mutlak Dip)
    fib_236 = lowest_low + (diff * 0.236)  # Dipten %23.6 yukarıda
    fib_382 = lowest_low + (diff * 0.382)  # Dipten %38.2 yukarıda
    fib_500 = lowest_low + (diff * 0.500)  # Orta Nokta

    score = 0
    status = "NEUTRAL"

    # ------------------------------------------------------
    # YENİ "SADECE DİP" PUANLAMA MANTIĞI
    # ------------------------------------------------------

    # 1. MUTLAK TABAN / EN DERİN DİP BÖLGESİ (En Yüksek Puan!)
    # Fiyat en düşük dip ile dipten %23.6 tepki alanı arasındaysa (Tam Akümülasyon/Bıçak Yerde)
    if fib_0 <= current_close <= fib_236:
        score = 100
        status = "FIB_ABSOLUTE_BOTTOM"  # Tam Taban/Dip Alanı

    # 2. İLK ERKEN TEPKİ / DİPTEN HAFİF KAFASINI KALDIRAN BÖLGE
    # Fiyat dipten %23.6 ile %38.2 aralığına gelmişse
    elif fib_236 < current_close <= fib_382:
        score = 75
        status = "FIB_EARLY_REBOUND"  # Erken Tepki Alanı

    # 3. ORTA BÖLGE VEYA TEPEYE YAKIN
    # Dip alanından tamamen uzaklaşmış
    elif fib_382 < current_close <= fib_500:
        score = 40
        status = "FIB_MID_ZONE"
    else:
        score = 10
        status = "FIB_HIGH_ZONE"  # Tepeye yakın, dip değil

    return score, status