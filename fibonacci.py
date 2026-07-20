import pandas as pd
import numpy as np

def calculate_fibonacci_dip_score(df, lookback_period=100):
    """
    Belirlenen periyottaki Fibonacci seviyelerini hesaplar ve 
    fiyatın dip destek seviyelerine yakınlığını puanlar.
    """
    if len(df) < lookback_period:
        return 0, "Yetersiz Veri"
    
    # Son 'lookback_period' kadar mumu al (Örn: Son 100 saatlik mum)
    recent_df = df.iloc[-lookback_period:]
    
    highest_high = recent_df['high'].max()
    lowest_low = recent_df['low'].min()
    current_close = df.iloc[-1]['close']
    
    # Fiyat farkı (Mesafe)
    diff = highest_high - lowest_low
    if diff == 0:
        return 0, "Yatay Piyasa"
    
    # Fibonacci Seviyelerinin Fiyat Karşılıkları
    fib_0 = lowest_low
    fib_236 = highest_high - (diff * 0.764) # Alttan yukarı 0.236 seviyesi
    fib_382 = highest_high - (diff * 0.618) # Alttan yukarı 0.382 seviyesi
    fib_618 = highest_high - (diff * 0.382) # Altın Oran desteği
    fib_786 = highest_high - (diff * 0.214) # Derin düzeltme desteği
    
    score = 0
    status = "NEUTRAL"
    
    # ---- PUANLAMA MANTIĞI ----
    
    # 1. Fiyat mutlak dibe çok yakınsa (Erken Dip Arayışı)
    if lowest_low <= current_close <= fib_236:
        score = 85
        status = "FIB_BOTTOM_ZONE" # En dip bölgede akümülasyon
        
    # 2. Fiyat mutlak dipten kafayı kaldırıp 0.236'yı yukarı kırdıysa (Dönüş Onayı)
    elif fib_236 < current_close <= fib_382:
        score = 95  # En yüksek puanı buraya veriyoruz çünkü düşüş trendi kırılıyor olabilir
        status = "FIB_236_RECLAIM"
        
    # 3. Fiyat büyük düşüşün 0.618 veya 0.786 derin desteklerindeyse
    elif (fib_618 * 0.99) <= current_close <= (fib_618 * 1.01):
        score = 75
        status = "FIB_GOLDEN_RATIO_SUPPORT"
        
    elif current_close > fib_382:
        score = 40
        status = "FIB_MID_ZONE" # Dip kurgusundan uzaklaşmış
        
    return score, status