# ==========================================================
# BIST ENGINE PRO
# main.py
# ==========================================================

from scanner import get_bist_symbols, pre_filter, get_history
from indicators import calculate_indicators
from trend import analyze_trend
from dip import analyze_dip
from volume import analyze_volume
from ai_score import calculate_ai_score
import pandas as pd


print("=" * 70)
print("              BIST ENGINE PRO v1.0")
print("=" * 70)

# ----------------------------------------------------------
# Tarama Modu Seçimi
# ----------------------------------------------------------
print("\nTarama Modunu Seçin:")
print("1 - Yükselen Trendde Geri Çekilme (PULLBACK)")
print("2 - Erken Dip Dönüşü (DIP)")
secim = input("Seçiminiz (1 veya 2): ").strip()

if secim == "2":
    TARAMA_MODU = "dip"
else:
    TARAMA_MODU = "pullback"

print(f"\nSeçilen Mod: {TARAMA_MODU.upper()}\n")

# ----------------------------------------------------------
# Ön Eleme
# ----------------------------------------------------------
symbols = get_bist_symbols()
print(f"Toplam Hisse : {len(symbols)}")

# Ön elemeyi seçtiğimiz moda göre çalıştırıyoruz
symbols = pre_filter(symbols, mode=TARAMA_MODU)
print(f"Ön Eleme Sonucu : {len(symbols)} hisse\n")

results = []

# ----------------------------------------------------------
# Tarama
# ----------------------------------------------------------
for _, row in symbols.iterrows():
    symbol = row["name"]
    print(f"\nAnaliz ediliyor : {symbol}")

    try:
        # Veri Çekme Kontrolü
        df = get_history(symbol)
        if df is None or len(df) < 200:
            print(f"--> {symbol} yetersiz veri veya tvDatafeed sunucu hatası nedeniyle atlandı.")
            continue

        # İndikatör Hesaplama
        df = calculate_indicators(df)

        # --------------------------------------------------
        # Analiz Motorları (Mod Destekli)
        # --------------------------------------------------
        trend = analyze_trend(df, mode=TARAMA_MODU)
        dip = analyze_dip(df, mode=TARAMA_MODU) 
        volume = analyze_volume(df, mode=TARAMA_MODU)

        # AI Score (Mod Ağırlıklarıyla)
        ai = calculate_ai_score(trend, dip, volume, mode=TARAMA_MODU)

        # Ekran Çıktısı
        print(
            f"Trend : {trend['score']}/{trend['max_score']} "
            f"({trend['trend']})"
        )
        print(
            f"Dip   : {dip['score']}/{dip['max_score']} "
            f"({dip['class']})"
        )
        print(
            f"Volume: {volume['score']}/{volume['max_score']} "
            f"({volume['class']})"
        )
        print(
            f"AI    : {ai['score']}  --> {ai['signal']}"
        )

        # Sonuç Listesi
        results.append({
            "Hisse": symbol,
            "Trend": trend["score"],
            "Dip": dip["score"],
            "Volume": volume["score"],
            "Trend100": ai["normalized"]["Trend"],
            "Dip100": ai["normalized"]["Dip"],
            "Volume100": ai["normalized"]["Volume"],
            "AI Score": ai["score"],
            "Sinyal": ai["signal"],
            "Trend Durumu": trend["trend"],
            "Dip Durumu": dip["class"],
            "Volume Durumu": volume["class"]
        })

    except Exception as e:
        print(f"{symbol} HATA -> {type(e).__name__}: {e}")

# ----------------------------------------------------------
# Sonuçlar
# ----------------------------------------------------------
if len(results):
    sonuc = pd.DataFrame(results)
    sonuc = sonuc.sort_values(
        by="AI Score",
        ascending=False
    )

    print("\n")
    print("=" * 110)
    print(sonuc.to_string(index=False))
    print("=" * 110)

    # Mod ismine göre CSV kaydetme
    filename = f"BIST_ENGINE_PRO_{TARAMA_MODU.upper()}.csv"
    sonuc.to_csv(
        filename,
        index=False,
        encoding="utf-8-sig"
    )
    print(f"\nSonuçlar {filename} dosyasına kaydedildi.")
else:
    print("\nUygun hisse bulunamadı.")