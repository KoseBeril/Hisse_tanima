# ==========================================================
# BIST ENGINE PRO
# ai_score.py
# ==========================================================

# ----------------------------------------------------------
# Normalize
# ----------------------------------------------------------
def normalize(score, max_score):
    if max_score == 0:
        return 0
    return round((score / max_score) * 100, 2)

# ----------------------------------------------------------
# AI SINIFLANDIRMA
# ----------------------------------------------------------
def ai_classification(score):
    if score >= 80: return "AL"
    elif score >= 70: return "IZLE"
    elif score >= 55: return "ERKEN"
    elif score >= 40: return "BEKLE"
    return "ALMA"
'''
🟢 AL (Skor > 80) — "Tetiğe Basma Zamanı"Tüm sistemlerin (Trend, Dip ve Hacim) neredeyse kusursuz bir uyumla yükselişi onayladığı bölgedir.  Arka Plandaki Durum: Fiyat çok güçlü bir destekte tutunmuş, RSI ve MACD gibi osilatörler kafayı yukarı kaldırmış, hacim ortalamaların üzerine çıkmaya başlamış (yani kurumsal para girişi var) ve risk/ödül oranı alıcı için maksimum avantaja ulaşmıştır.  Trader Eylemi: Teknik olarak alım yönünde pozisyon açmak için en güvenli ve olasılığı en yüksek an burasıdır.
🟡 IZLE (Skor 70 - 79) — "Neredeyse Hazır, Gözün Üzerinde Olsun"Sinyal son derece güçlüdür ancak sistemlerden en az biri henüz tam olarak yeşil yakmamıştır.  Arka Plandaki Durum: Örneğin; dip formasyonu ve indikatör dönüşleri harikadır ama hacim henüz tam olarak patlamamıştır. Ya da fiyat dipten kalkmıştır ama hemen üzerindeki bir hareketli ortalama (EMA) direncini henüz kırmamıştır.  Trader Eylemi: Hisse hemen yakın takibe (Watchlist) alınır. Direnç kırılımı veya hacim desteği geldiği anda oyuna girmek üzere pusuya yatılır.
🔵 ERKEN (Skor 55 - 69) — "Risk Sevenler İçin Kademeli Alım"Fiyatın teknik olarak aşırı ucuzladığı ve ilk dönüş kıvılcımlarının başladığı bölgedir.  Arka Plandaki Durum: RSI aşırı satımdan dönmüştür, belki ufak bir pozitif uyumsuzluk vardır ama ana trend hala aşağı yönlüdür ve hareketli ortalamalar hala fiyatın tepesindedir. Yani "en dipten alma" potansiyeli vardır ama sinyal henüz olgunlaşmamış (teyit edilmemiş) olduğundan hata payı yüksektir.  Trader Eylemi: Agresif/risk seven trader'lar için bu bölge "kademeli (parça parça) alım" bölgesidir. Muhafazakar trader'lar ise teyit beklemeye devam eder.
🟠 BEKLE (Skor 40 - 54) — "Kararsız Bölge, Nakit Koruma"Hissede yön duygusunun tamamen kaybolduğu, piyasanın kararsız olduğu akümülasyon veya yatay bant bölgesidir.  Arka Plandaki Durum: Ne satıcılar fiyatı daha aşağı bastırabiliyordur ne de alıcılarda hisseyi yukarı kaldıracak güç (hacim) vardır. İndikatörler orta çizgilerde (RSI 40-50 arası gibi) yatay seyrediyordur.  Trader Eylemi: Pozisyona girmek için hiçbir sebep yoktur. Parayı bu kağıda bağlayıp zaman kaybetmek yerine nakitte beklemek veya başka fırsatlara bakmak en doğrusudur.
🔴 ALMA (Skor < 40) — "Düşen Bıçak Tutulmaz"Hissenin düşüş trendinin tam gaz devam ettiği ya da tahtanın tamamen kuruduğu/dağıtıldığı (distribution) en tehlikeli bölgedir.  Arka Plandaki Durum: Trend tamamen aşağı yönlüdür, indikatörlerde hiçbir dönüş emaresi yoktur, aksine hacimli satışlar (para çıkışı) gerçekleşiyordur.  Trader Eylemi: Hissenin grafiği her ne kadar "gözüne çok düşmüş ve ucuzlamış" görünse de kesinlikle uzak durulmalıdır. Çünkü düşüşün nerede duracağı matematiksel olarak tamamen belirsizdir.
'''
# ----------------------------------------------------------
# AI SCORE (DİNAMİK MOD DESTEKLİ)
# ----------------------------------------------------------
def calculate_ai_score(trend, dip, volume, mode="pullback"):
    # Normalize
    trend_score = normalize(trend["score"], trend["max_score"])
    dip_score = normalize(dip["score"], dip["max_score"])
    volume_score = normalize(volume["score"], volume["max_score"])

    # ------------------------------------------------------
    # Ağırlıklar (Moda Göre Dinamik Değişiyor)
    # ------------------------------------------------------
    if mode == "pullback":
        trend_weight = 0.40
        dip_weight = 0.35
        volume_weight = 0.25
    elif mode == "dip":
        trend_weight = 0.10     # Erken dipte ana trend yönü zayıftır, etkisi azaltıldı
        dip_weight = 0.65       # Dip puanı başrolü üstlendi
        volume_weight = 0.30    # Hacim akümülasyonu sabit korundu

    # AI SCORE Hesapla
    total = (
        trend_score * trend_weight +
        dip_score * dip_weight +
        volume_score * volume_weight
    )
    total = round(total, 2)

    return {
        "score": total,
        "signal": ai_classification(total),
        "normalized": {
            "Trend": trend_score,
            "Dip": dip_score,
            "Volume": volume_score
        },
        "weights": {
            "Trend": trend_weight,
            "Dip": dip_weight,
            "Volume": volume_weight
        },
        "layers": {
            "Trend": trend_score,
            "Dip": dip_score,
            "Volume": volume_score
        }
    }

if __name__ == "__main__":
    print("AI Score motoru hazır.")