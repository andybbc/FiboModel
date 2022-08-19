# %%

import warnings

warnings.filterwarnings("ignore")
import pandas as pd

# 序列化用
import pickle

# %%

file = './data/train_subset_1000000_sample.csv'
df = pd.read_csv(file)
print(df)  # [999999 rows x 24 columns]
print(123)

# %%

print(f'--All data:{df.id.count()}')
y_1_nums = df[df["click"] == 1].id.count()
y_0_nums = df[df["click"] == 0].id.count()
print(f'--1 data:{y_1_nums}')
print(f'--0 data:{y_0_nums}')
print(f'--0 VS 1 => {round(y_0_nums / y_1_nums, 2)}:1')

# %%

# df.describe().T

# %%

df.info()

# %%

# 存放label和名称的映射
label_dict = {}

##接下来对特征进行处理，先将类别特征进行编码
# 针对类型类的特征，先进行编码，编码之前构建字典
from sklearn import preprocessing


def label_encode(field, df):
    dic = []
    df_field = df[field]
    list_field = df_field.tolist()

    # 构建field字典
    for i in list_field:
        if i not in dic:
            dic.append(i)

    label_field = preprocessing.LabelEncoder()
    label_field.fit(dic)

    # 保存label
    label_dict[field] = label_field

    df_field_enconde_tmp = label_field.transform(df_field)
    df_field_enconde = pd.DataFrame(df_field_enconde_tmp, index=df.index, columns=[(field + '_enconde')])
    return df_field_enconde


# %%

# site_id             999999 non-null object
# site_domain         999999 non-null object
# site_category       999999 non-null object
# app_id              999999 non-null object
# app_domain          999999 non-null object
# app_category        999999 non-null object
# device_id                     999999 non-null object
# device_ip           999999 non-null object
# device_model        999999 non-null object
df_site_id_enconde = label_encode('site_id', df)
df_site_domain_enconde = label_encode('site_domain', df)
df_site_category_enconde = label_encode('site_category', df)
df_app_id_enconde = label_encode('app_id', df)
df_app_domain_enconde = label_encode('app_domain', df)
df_app_category_enconde = label_encode('app_category', df)
df_device_id_enconde = label_encode('device_id', df)
df_device_ip_enconde = label_encode('device_ip', df)
df_device_model_enconde = label_encode('device_model', df)

# 把label_dict导入到文件
with open('dict_label', 'wb') as f:
    pickle.dump(label_dict, f)

# %%

# 拼接特征回去
# id                  999999 non-null float64
# click               999999 non-null int64
# hour                999999 non-null int64
# C1                  999999 non-null int64
# banner_pos          999999 non-null int64
# site_id             999999 non-null object
# site_domain         999999 non-null object
# site_category       999999 non-null object
# app_id              999999 non-null object
# app_domain          999999 non-null object
# app_category        999999 non-null object
# device_id           999999 non-null object
# device_ip           999999 non-null object
# device_model        999999 non-null object
# device_type         999999 non-null int64
# device_conn_type    999999 non-null int64
# C14                 999999 non-null int64
# C15                 999999 non-null int64
# C16                 999999 non-null int64
# C17                 999999 non-null int64
# C18                 999999 non-null int64,
# C19                 999999 non-null int64
# C20                 999999 non-null int64
# C21                 999999 non-null int64
pd_input = pd.concat([df[['click', 'banner_pos', 'device_type', 'device_conn_type'
    , 'C1', 'C14', 'C15', 'C16', 'C17', 'C18', 'C19', 'C20', 'C21']]
                         , df_site_id_enconde
                         , df_site_domain_enconde
                         , df_site_category_enconde
                         , df_app_id_enconde
                         , df_app_domain_enconde
                         , df_app_category_enconde
                         , df_device_id_enconde
                         , df_device_ip_enconde
                         , df_device_model_enconde], axis=1)  # axis横向拼接(join)
# pd_input

# %%

# 进行特征的简单分析
import matplotlib.pyplot as plt


# 特征与y的分布，构建一个散点分布函数
def draw_scatter(x, y, xLabel):
    plt.figure(figsize=(10, 5))
    plt.scatter(x, y)
    plt.title('%s VS Gender' % xLabel)
    plt.xlabel(xLabel)
    plt.ylabel('Gender')
    plt.yticks(range(0, 2, 1))  # 纵轴起点，最大值，间隔, 对应的就是gender
    plt.grid()
    plt.show()


# %%

# pd_input.describe().T

# %%

##处理过的数据保存下来
pd_input.to_csv('./out_put/encode_data_sample.csv', header=True, index=True)

with open('dict_label','rb')as f:
    a = pickle.load(f)

print(a,type(a))
print("===========")
print(a['site_domain'])
print("===========")

print(a['site_domain'].transform(['f3845767']))

