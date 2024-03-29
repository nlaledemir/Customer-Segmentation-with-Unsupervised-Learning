
###############################################################
# Gözetimsiz Öğrenme ile Müşteri Segmentasyonu (Customer Segmentation with Unsupervised Learning)
###############################################################

###############################################################
# İş Problemi (Business Problem)
###############################################################

# Unsupervised Learning yöntemleriyle (Kmeans, Hierarchical Clustering )  müşteriler kümelere ayrılıp ve davranışları gözlemlenmek istenmektedir.
#######
###############################################################
# Veri Seti Hikayesi
###############################################################

# Veri seti son alışverişlerini 2020 - 2021 yıllarında OmniChannel(hem online hem offline) olarak yapan müşterilerin geçmiş alışveriş davranışlarından
# elde edilen bilgilerden oluşmaktadır.

# 20.000 gözlem, 13 değişken

# master_id: Eşsiz müşteri numarası
# order_channel : Alışveriş yapılan platforma ait hangi kanalın kullanıldığı (Android, ios, Desktop, Mobile, Offline)
# last_order_channel : En son alışverişin yapıldığı kanal
# first_order_date : Müşterinin yaptığı ilk alışveriş tarihi
# last_order_date : Müşterinin yaptığı son alışveriş tarihi
# last_order_date_online : Muşterinin online platformda yaptığı son alışveriş tarihi
# last_order_date_offline : Muşterinin offline platformda yaptığı son alışveriş tarihi
# order_num_total_ever_online : Müşterinin online platformda yaptığı toplam alışveriş sayısı
# order_num_total_ever_offline : Müşterinin offline'da yaptığı toplam alışveriş sayısı
# customer_value_total_ever_offline : Müşterinin offline alışverişlerinde ödediği toplam ücret
# customer_value_total_ever_online : Müşterinin online alışverişlerinde ödediği toplam ücret
# interested_in_categories_12 : Müşterinin son 12 ayda alışveriş yaptığı kategorilerin listesi
# store_type : 3 farklı companyi ifade eder. A company'sinden alışveriş yapan kişi B'dende yaptı ise A,B şeklinde yazılmıştır.

#########
###############################################################
# GÖREVLER
###############################################################

# GÖREV 1: Veriyi Hazırlama
           # 1. flo_data_20K.csv.csv verisini okuyunuz.
           # 2. Müşterileri segmentlerken kullanacağınız değişkenleri seçiniz. Tenure(Müşterinin yaşı), Recency (en son kaç gün önce alışveriş yaptığı) gibi yeni değişkenler oluşturabilirsiniz.

# GÖREV 2: K-Means ile Müşteri Segmentasyonu
           # 1. Değişkenleri standartlaştırınız.
           # 2. Optimum küme sayısını belirleyiniz.
           # 3. Modelinizi oluşturunuz ve müşterilerinizi segmentleyiniz.
           # 4. Herbir segmenti istatistiksel olarak inceleyeniz.

# GÖREV 3: Hierarchical Clustering ile Müşteri Segmentasyonu
           # 1. Görev 2'de standırlaştırdığınız dataframe'i kullanarak optimum küme sayısını belirleyiniz.
           # 2. Modelinizi oluşturunuz ve müşterileriniz segmentleyiniz.
           # 3. Herbir segmenti istatistiksel olarak inceleyeniz.


#####
###############################################################
# GÖREV 1: Veri setini okutunuz ve müşterileri segmentlerken kullanıcağınız değişkenleri seçiniz.
###############################################################
#pip install yellowbrick
import pandas as pd
from scipy import stats
import datetime as dt
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
from scipy.cluster.hierarchy import dendrogram
from scipy.cluster.hierarchy import linkage
from yellowbrick.cluster import KElbowVisualizer  #Dirsek yöntemi için uygulanır
from sklearn.cluster import AgglomerativeClustering   #Birleştirici cluster metotu
import seaborn as sns
import numpy as np

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.2f' % x)
pd.set_option('display.width', 1000)
import warnings
warnings.filterwarnings("ignore")

df_ = pd.read_csv(r"FLO/flo_data_20K.csv")
df= df_.copy()

def check_df(dataframe):
    print("##################### Shape #####################")
    print(dataframe.shape)
    print("##################### Types #####################")
    print(dataframe.dtypes)
    print("##################### Head #####################")
    print(dataframe.head(3))
    print("##################### NA #####################")
    print(dataframe.isnull().sum())
    print("##################### Quantiles #####################")
    print(dataframe.quantile([0, 0.05, 0.50, 0.95, 0.99, 1]).T)

check_df(df)
df.info()
# tarih değişkenine çevirme
date_columns = df.columns[df.columns.str.contains("date")]
df[date_columns] = df[date_columns].apply(pd.to_datetime)

df["last_order_date"].max() # 2021-05-30

analysis_date = dt.datetime(2021, 6, 1)

df["recency"] = (analysis_date - df["last_order_date"]).astype('timedelta64[D]') # en son kaç gün önce alışveriş yaptı
df["tenure"] = (df["last_order_date"]-df["first_order_date"]).astype('timedelta64[D]')

model_df = df[["order_num_total_ever_online", "order_num_total_ever_offline", "customer_value_total_ever_offline", "customer_value_total_ever_online", "recency", "tenure"]]
model_df.head()
model_df.quantile([0, 0.05, 0.50, 0.95, 0.99, 1]).T
###############################################################
# GÖREV 2: K-Means ile Müşteri Segmentasyonu
###############################################################

# 1. Değişkenleri standartlaştırınız.
#SKEWNESS
#Burada ilk başta değişkenlerimizin çarpıklığına bakarız.
def check_skew(df_skew, column):
    skew = stats.skew(df_skew[column])
    skewtest = stats.skewtest(df_skew[column])
    plt.title('Distribution of ' + column)
    sns.distplot(df_skew[column], color="g")
    print("{}'s: Skew: {}, : {}".format(column, skew, skewtest))
    return

plt.figure(figsize=(9, 9))
plt.subplot(6, 1, 1);
check_skew(model_df, 'order_num_total_ever_online')
plt.subplot(6, 1, 2)
check_skew(model_df, 'order_num_total_ever_offline')
plt.subplot(6, 1, 3)
check_skew(model_df, 'customer_value_total_ever_offline')
plt.subplot(6, 1, 4)
check_skew(model_df, 'customer_value_total_ever_online')
plt.subplot(6, 1, 5)
check_skew(model_df, 'recency')
plt.subplot(6, 1, 6)
check_skew(model_df, 'tenure')
plt.tight_layout()
plt.savefig('before_transform.png', format='png', dpi=1000)
plt.show()


# Normal dağılımın sağlanması için Log transformation uygulanması

log_transfrom_list = ['order_num_total_ever_online',
                      'order_num_total_ever_offline',
                      'customer_value_total_ever_offline',
                      'customer_value_total_ever_online',
                      'recency',
                      'tenure']


for col in log_transfrom_list:
    model_df[col] = np.log1p(model_df[col])


model_df.head()

# Scaling
#uzaklık temelli ve gradient descent gibi yöntemlerin kullanımındaki süreçlerde değişkeni standartlaştırmak önemli.
sc = MinMaxScaler((0, 1))
model_scaling = sc.fit_transform(model_df)
model_df = pd.DataFrame(model_scaling, columns=model_df.columns)
model_df.head()


# 2. Optimum küme sayısını belirleyiniz.
kmeans = KMeans()
elbow = KElbowVisualizer(kmeans, k=(2, 20))
elbow.fit(model_df)
elbow.show()

model_df.shape

# 3. Modelinizi oluşturunuz ve müşterilerinizi segmentleyiniz.
k_means = KMeans(n_clusters=7, random_state=42).fit(model_df)
segments = k_means.labels_


pd.DataFrame(segments).value_counts()
'''
0    5448
4    3340
2    3269
6    3245
5    1974
1    1841
3     828

'''

final_df = df[["master_id","order_num_total_ever_online","order_num_total_ever_offline","customer_value_total_ever_offline","customer_value_total_ever_online","recency","tenure"]]

final_df["segment"] = segments
final_df.head()


# 4. Herbir segmenti istatistiksel olarak inceleyeniz.
final_df.groupby("segment").agg({"order_num_total_ever_online":["median","min","max"],
                                  "order_num_total_ever_offline":["median","min","max"],
                                  "customer_value_total_ever_offline":["median","min","max"],
                                  "customer_value_total_ever_online":["median","min","max"],
                                  "recency":["median", "min", "max"],
                                  "tenure":["median", "min", "max"]})

###############################################################
# GÖREV 3: Hierarchical Clustering ile Müşteri Segmentasyonu
###############################################################

# 1. Görev 2'de standarlaştırdığınız dataframe'i kullanarak optimum küme sayısını belirleyiniz.
hc_complete = linkage(model_df, 'ward') #birleştirici

plt.figure(figsize=(7, 5))
plt.title("Dendrograms")
dend = dendrogram(hc_complete,
           truncate_mode="lastp",
           p=5,
           show_contracted=True,
           leaf_font_size=10)
plt.axhline(y=10, color='r', linestyle='--')
plt.show()

#Aşağıdan yukarı doğru ilerle 5 küme olunca dur.
# 2. Modelinizi oluşturunuz ve müşterileriniz segmentleyiniz.

hc = AgglomerativeClustering(n_clusters=5) #birleştirici
segments = hc.fit_predict(model_df)
pd.DataFrame(segments).value_counts()
"""
0    8747
1    4994
4    2823
2    2396
3     985
"""

final_df = df[["master_id", "order_num_total_ever_online","order_num_total_ever_offline","customer_value_total_ever_offline","customer_value_total_ever_online","recency","tenure"]]
final_df["segment"] = segments
final_df.head()

# 3. Herbir segmenti istatistiksel olarak inceleyeniz.

final_df.groupby("segment").agg({"order_num_total_ever_online":["median","min","max"],
                                  "order_num_total_ever_offline":["median","min","max"],
                                  "customer_value_total_ever_offline":["median","min","max"],
                                  "customer_value_total_ever_online":["median","min","max"],
                                  "recency":["median","min","max"],
                                  "tenure":["median", "min", "max"]})

