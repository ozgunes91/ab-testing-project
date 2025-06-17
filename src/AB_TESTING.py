#####################################################
# AB Testi ile BiddingYöntemlerinin Dönüşümünün Karşılaştırılması
#####################################################

#####################################################
# İş Problemi
#####################################################

# Facebook kısa süre önce mevcut "maximumbidding" adı verilen teklif verme türüne alternatif
# olarak yeni bir teklif türü olan "average bidding"’i tanıttı. Müşterilerimizden biri olan bombabomba.com,
# bu yeni özelliği test etmeye karar verdi veaveragebidding'in maximumbidding'den daha fazla dönüşüm
# getirip getirmediğini anlamak için bir A/B testi yapmak istiyor.A/B testi 1 aydır devam ediyor ve
# bombabomba.com şimdi sizden bu A/B testinin sonuçlarını analiz etmenizi bekliyor.Bombabomba.com için
# nihai başarı ölçütü Purchase'dır. Bu nedenle, istatistiksel testler için Purchasemetriğine odaklanılmalıdır.




#####################################################
# Veri Seti Hikayesi
#####################################################

# Bir firmanın web site bilgilerini içeren bu veri setinde kullanıcıların gördükleri ve tıkladıkları
# reklam sayıları gibi bilgilerin yanı sıra buradan gelen kazanç bilgileri yer almaktadır.Kontrol ve Test
# grubu olmak üzere iki ayrı veri seti vardır. Bu veri setleriab_testing.xlsxexcel’ininayrı sayfalarında yer
# almaktadır. Kontrol grubuna Maximum Bidding, test grubuna AverageBiddinguygulanmıştır.

# impression: Reklam görüntüleme sayısı
# Click: Görüntülenen reklama tıklama sayısı
# Purchase: Tıklanan reklamlar sonrası satın alınan ürün sayısı
# Earning: Satın alınan ürünler sonrası elde edilen kazanç



#####################################################
# Proje Görevleri
#####################################################
import itertools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
#!pip install statsmodels
import statsmodels.stats.api as sms
from scipy.stats import ttest_1samp, shapiro, levene, ttest_ind, mannwhitneyu, \
    pearsonr, spearmanr, kendalltau, f_oneway, kruskal
from statsmodels.stats.proportion import proportions_ztest

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 10)
pd.set_option('display.float_format', lambda x: '%.5f' % x)

######################################################
# AB Testing (Bağımsız İki Örneklem T Testi)
######################################################

# 1. Hipotezleri Kur
# 2. Varsayım Kontrolü
#   - 1. Normallik Varsayımı (shapiro)
#   - 2. Varyans Homojenliği (levene)
# 3. Hipotezin Uygulanması
#   - 1. Varsayımlar sağlanıyorsa bağımsız iki örneklem t testi
#   - 2. Varsayımlar sağlanmıyorsa mannwhitneyu testi
# 4. p-value değerine göre sonuçları yorumla
# Not:
# - Normallik sağlanmıyorsa direkt 2 numara. Varyans homojenliği sağlanmıyorsa 1 numaraya arguman girilir.
# - Normallik incelemesi öncesi aykırı değer incelemesi ve düzeltmesi yapmak faydalı olabilir.

#####################################################
# Görev 1:  Veriyi Hazırlama ve Analiz Etme
#####################################################

# Adım 1:  ab_testing_data.xlsx adlı kontrol ve test grubu verilerinden oluşan veri setini okutunuz. Kontrol ve test grubu verilerini ayrı değişkenlere atayınız.

from pathlib import Path
BASE_DIR   = Path(__file__).resolve().parents[1]          # proje kökü
DATA_PATH  = BASE_DIR / "data" / "ab_testing.xlsx"
xls        = pd.ExcelFile(DATA_PATH)
control_df = pd.read_excel(xls, "Control Group")
test_df    = pd.read_excel(xls, "Test Group")
test_df.head()
control_df.head()

# Adım 2: Kontrol ve test grubu verilerini analiz ediniz.

# Kontrol ve test grubundaki temel metriklerin özet istatistikleri
desc_control = control_df.describe().T
desc_test    = test_df.describe().T

# Özet tabloyu yazdır
print(desc_control.loc[['mean','std','min','max'], ['Purchase','Impression','Click','Earning']])
print(desc_test.loc[['mean','std','min','max'], ['Purchase','Impression','Click','Earning']])

                  #Control (n = 40)	  Test (n = 40)
#Purchase – Ortalama	   550.89	         582.11
#Standart Sapma            134.11	         161.15
#Minimum – Maksimum	    267 – 802	      312 – 890
#Impression – Ortalama    101 711	        120 512
#Click – Ortalama	        5 100	          3 968
#Earning – Ortalama (₺)	  1 908.6	        2 514.9

#özetle ;

#Daha fazla gösterim (impression) → fakat daha düşük tıklama oranı (CTR):
# Test varyasyonu kullanıcı akışında daha görünür olmuş ama çağrısına (CTA)
# yeterince yanıt alamamış.

#Daha fazla satın alma ve daha yüksek gelir: Tıklama sayısı az olsa da,
# tıklayan veya satın almaya yönelenlerin ortalama harcaması veya
# satın alma davranışı güçlenmiş.

#Değişkenlik artışı: Test grubundaki yüksek standart sapma ve uç değerler,
# varyasyonun bazı segmentlerde çok başarılı,
# bazılarında başarısız olabileceğini düşündürüyor.

# Adım 3: Analiz işleminden sonra concat metodunu kullanarak kontrol ve test grubu verilerini birleştiriniz.

df = pd.concat([control_df.assign(group="control"),
               test_df.assign(group="test")], ignore_index=True) 
                                                                
                                                                
df.info()
df.head(80)
df.shape
#####################################################
# Görev 2:  A/B Testinin Hipotezinin Tanımlanması
#####################################################

# Adım 1: Hipotezi tanımlayınız.

# H₀: µ_control = µ_test  #
# H₁: µ_control ≠ µ_test  #

#Odak metrik: Purchase (satın alma adedi).
#İki grubun ortalamalarının eşit olup olmadığını test edeceğiz.

# Adım 2: Kontrol ve test grubu için purchase(kazanç) ortalamalarını analiz ediniz
#ayrı dataframeler üzerinden;
control_mean = control_df["Purchase"].mean()
test_mean    = test_df["Purchase"].mean()
print(f"Control Purchase Mean: {control_mean:.5f}")
print(f"Test    Purchase Mean: {test_mean:.5f}")

#birleştirilmiş dataframe üzerinden;
purchase_means = df.groupby("group")["Purchase"].mean() 
print(purchase_means)

#####################################################
# GÖREV 3: Hipotez Testinin Gerçekleştirilmesi
#####################################################

######################################################
# AB Testing (Bağımsız İki Örneklem T Testi)
######################################################


# Adım 1: Hipotez testi yapılmadan önce varsayım kontrollerini yapınız.Bunlar Normallik Varsayımı ve Varyans Homojenliğidir.

# Kontrol ve test grubunun normallik varsayımına uyup uymadığını Purchase değişkeni üzerinden ayrı ayrı test ediniz
# Adım 1: Varsayım Kontrolleri
#   - Normallik (Shapiro–Wilk)
#   - Varyans Homojenliği (Levene)
# --------------------------------
sw_ctrl = shapiro(control_df['Purchase'])
sw_test = shapiro(test_df['Purchase'])
lv      = levene(control_df['Purchase'], test_df['Purchase'])

print("Shapiro p-control:", sw_ctrl.pvalue)
print("Shapiro p-test:   ", sw_test.pvalue)
print("Levene p-value:    ", lv.pvalue)

# Adım 2: Normallik Varsayımı ve Varyans Homojenliği sonuçlarına göre uygun testi seçiniz
# ------------------------------
# Adım 2: Uygun Testi Seçme
# ------------------------------
# Eğer her iki Shapiro p > 0.05 ve Levene p > 0.05 ise:
#     ==>> Bağımsız İki Örneklem t-Testi (equal_var=True)
# Eğer normallik var ama varyans farklı ise:
#     ==>> t-Testi (equal_var=False)
# Eğer normallik sağlanmıyorsa:
#     ==>> Mann-Whitney U Testi
if sw_ctrl.pvalue > 0.05 and sw_test.pvalue > 0.05:
    if lv.pvalue > 0.05:
        print("Seçim: t-Test (equal_var=True)")
        test_res = ttest_ind(control_df['Purchase'],
                             test_df['Purchase'],
                             equal_var=True)
    else:
        print("Seçim: t-Test (equal_var=False)")
        test_res = ttest_ind(control_df['Purchase'],
                             test_df['Purchase'],
                             equal_var=False)
else:
    print("Seçim: Mann-Whitney U Testi")
    test_res = mannwhitneyu(control_df['Purchase'],
                            test_df['Purchase'],
                            alternative='two-sided')

# Adım 3: Test sonucunda elde edilen p_value değerini göz önünde bulundurarak kontrol ve test grubu satın alma
# ortalamaları arasında istatistiki olarak anlamlı bir fark olup olmadığını yorumlayınız.

# ------------------------------
# Adım 3: Test Sonucunu Yorumlama
# ------------------------------
# t-Testi veya Mann-Whitney'den dönen test_res içinde:
#   test_res.statistic  → test istatistiği
#   test_res.pvalue     → p-değeri

print("Test İstatistiği:", test_res.statistic)
print("p-value:         ", test_res.pvalue)

if test_res.pvalue < 0.05:
    print("→ p < 0.05: H₀ reddedilir (fark anlamlı).")
else:
    print("→ p ≥ 0.05: H₀ reddedilemez (anlamlı fark yok).")

##############################################################
# GÖREV 4 : Sonuçların Analizi
##############################################################

# Adım 1: Hangi testi kullandınız, sebeplerini belirtiniz.

# Normalite testi (Shapiro–Wilk) ve varyans testi (Levene) sonuçlarına baktık.
# Her ikisi de p > 0.05 verince equal_var=True ile klasik t-testi seçtik.
# Eğer varyans homojenliği sağlanmamış olsaydı equal_var=False, normallik bozulmuş olsaydı Mann–Whitney U Testi kullanılırdı.

# Adım 2: Elde ettiğiniz test sonuçlarına göre müşteriye tavsiyede bulununuz.

# Testin p-değeri ≈ 0.349 → 0.05’ten büyük, yani H₀ reddedilemedi.
# Bu, “average bidding” in “maximum bidding”e göre örneklem büyüklüğü ve süresi mevcut haliyle dönüşümü anlamlı artırmadığı anlamına gelir.

# Öneriler:

# 1.Örneklem Büyüklüğü ve Süreyi Artırmak
# Mevcut 40×2 örneklem küçük olduğu için %5–6’lık farkları yakalamak zor.
# Testi en az 2–3 kat daha fazla kullanıcıyla, veya 2 ay yerine 3–4 ay sürdürerek tekrarlardım.
# Böylece istatistiksel gücü yükseltir, gerçekçi bir sonuç elde edersin.

# 2.Kreatif ve CTA Optimizasyonu
# Test varyasyonunda CTR’in %5.36’dan %3.42’ye düştüğünü gördük.
# Bu, kullanıcıların “average bidding” reklamına daha az ilgi gösterdiğini işaret ediyor.
# Başlığı, buton rengini veya teklif metnini yeniden tasarlayıp A/B testleri yap.
# Farklı görsel, mesaj veya yerleşimler deneyerek tıklama oranını eski düzeye ya da daha yükseğe çıkar.

# 3.Segment Bazlı Analiz
# Tüm kullanıcıları tek havuzda görmek yerine; mobil vs. desktop, coğrafi bölge, yeni vs.
# geri dönen kullanıcı gibi segmentlerde “average bidding” performansını ayrı ayrı test et.
# Bazı segmentler “average bidding”den daha iyi dönüşüm alıyor olabilir.

# 4.ROI / CPA ve Ortalama Sepet Değeri İncelemesi
# Sadece “purchase adedi” değil, kullanıcı başına maliyet (CPA) ve ortalama satın alma değeri (AOV) de kritik.
# “Average bidding” geliri yükselttiyse bile tıklama maliyeti artmış olabilir.
# Kampanya maliyetini, tıklama başı maliyeti ve satın alma başı maliyetiyle dengele.
# AOV yükseliyorsa, dönüşüm kalitesinin arttığını yine de değerlendirebilirsin.

# 5.Alternatif Bidding Stratejileri
# “Maximum” ve “average” dışında “target CPA” veya “maximize conversions” gibi otomatik teklif stratejilerini de test et.
# Google/Facebook’ın kendi makine öğrenmeli teklif optimizasyonlarını devreye almak bazen klasik sabit bidding’den daha iyi sonuç verir.

#6.Canlı Çoklu Varyasyon (Multivariate) Testler
#Eğer sadece 2 varyasyon yeterince ayrışmıyorsa, reklamın başlığı, görseli ve teklif tipi gibi 3–4 öğeyi aynı anda değiştirip
# multivariate testlerle hangi kombinasyonun en iyi çalıştığını görmek mümkün.

# Özetle: Şu an “average bidding” net bir avantaj sunmuyor ve CTR’i düşürüyor.
# Ben öncelikle örneklem/süreyi artırır, sonra kreatif & segment optimizasyonu yapar;
# maliyet-performans metriklerini (CPA, ROI) de göz önüne alarak karar verirdim.
# Böylece hem dönüşüm adedini hem de kârlılığı en doğru şekilde ölçmüş olursun.


