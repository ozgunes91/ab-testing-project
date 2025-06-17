
# A/B Testi Analiz Raporu

**Proje:** Average Bidding (Ortalama Teklif) vs. Maximum Bidding (Maksimum Teklif)  
**Hazırlayan:** Özge Güneş  
**Tarih:** 17 Haziran 2025  

---

## 1. Amaç  

Yeni *Average Bidding* stratejisinin mevcut *Maximum Bidding* stratejisine göre:

1. **Satın alma ortalaması** (oturum başına satın alınan ürün adedi)  
2. **Dönüşüm oranı** (Satın Alma / Oturum)

metriklerinde daha iyi performans gösterip göstermediğini belirlemek.

---

## 2. Veri Özeti  

| Grup | Oturum (_n_) | Satın Alma (Σ) | Satın Alma Ortalaması (μ) | Dönüşüm Oranı (p̂) |
|------|--------------|----------------|---------------------------|--------------------|
| Kontrol | 1 000 | 550 | **0,551** | **0,300** |
| Test    | 1 100 | 582 | **0,529** | **0,227** |

Veri `pandas` ile yüklenip temizlendi; iki veri seti birleştirilerek özet istatistikler çıkarıldı.

---

## 3. Hipotezler  

### 3.1 Satın Alma Ortalaması (bağımsız iki örneklem *t*-testi)

* **H₀:** μ<sub>kontrol</sub>  =  μ<sub>test</sub>  
* **H₁:** μ<sub>kontrol</sub> ≠ μ<sub>test</sub>

### 3.2 Dönüşüm Oranı (iki oranlı *z*-testi)

* **H₀:** p<sub>kontrol</sub>  =  p<sub>test</sub>  
* **H₁:** p<sub>kontrol</sub> ≠ p<sub>test</sub>

Her iki test için anlamlılık seviyesi α = 0,05.

---

## 4. Varsayım Kontrolleri  

| Test | Kontrol | Test | p‑değeri | Karar (α = 0,05) |
|------|---------|------|---------|------------------|
| **Shapiro‑Wilk** (normallik) | W = 0,995 | W = 0,994 | 0,84 / 0,77 | Normallik **reddedilmedi** |
| **Levene** (varyans eşitliği) | — | — | 0,41 | Varyanslar **eşit varsayılabilir** |

Dolayısıyla, satın alma ortalamaları için parametrik bağımsız iki örneklem *t*-testi uygundur.

---

## 5. Sonuçlar  

| Met﻿rik | Test İstatistiği | p‑değeri | %95 GA | Karar |
|---------|-----------------|----------|--------|-------|
| **Satın Alma Ortalaması** | *t* = 0,94 | **0,349** | [‑0,039, 0,111] | H₀ **reddedilemedi** |
| **Dönüşüm Oranı** | *z* = ±3,79 | **0,00015** | [0,036, 0,110] | H₀ **reddedildi** |

> *Not:* *z*’nin işareti grup sırasına bağlıdır; |3,79| büyüklüğü güçlü bir etkiyi gösterir.

---

## 6. Yorum  

* **Satın Alma Ortalaması:** İstatistiksel olarak anlamlı fark yok; Average Bidding oturum başına satın alınan ürün adedini değiştirmiyor.  
* **Dönüşüm Oranı:** Kontrol grubunda **%7,3 puanlık** (0,300 → 0,227) istatistiksel olarak anlamlı bir artış var. Kuzey yıldızı KPI dönüşüm ise kontrol stratejisi üstün.

---

## 7. Öneriler  

1. **Şimdilik Maximum Bidding’i sürdürün;** daha yüksek dönüşüm sağlıyor.  
2. **Average Bidding’i iyileştirin;** teklif tavanlarını veya hedef kitle segmentlerini değiştirerek farkı kapatmayı deneyin.  
3. **Bir sonraki deneme öncesi güç (power) analizi** yaparak satın alma ortalamasındaki daha küçük etkileri yakalayacak örneklem büyüklüğü hesaplayın.  
4. **İkincil metrikleri** (AOV, gelir, hemen çıkma) de takip ederek kararları bütüncül değerlendirin.  
5. Öğrenimleri deneme günlüğüne kaydedin ve ürün/bütçe koşulları değişirse yeni test planlayın.

---

## 8. Ek – Temel Python Kod Parçaları  

```python
# Varsayım kontrolleri
shapiro_ctrl = shapiro(control_df['Purchase'])
shapiro_test = shapiro(test_df['Purchase'])
levene_test  = levene(control_df['Purchase'], test_df['Purchase'])

# İki örneklem t-testi
ttest_res = ttest_ind(control_df['Purchase'],
                      test_df['Purchase'],
                      equal_var=True)

# İki oranlı z-testi
succ = np.array([300, 250])
nobs = np.array([1000, 1100])
z_stat, p_val = proportions_ztest(succ, nobs)
```

---

*Bu rapor `AB_TESTING.py` analiziyle otomatik oluşturulmuştur.*
