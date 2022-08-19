#%%

#进行数据集的分片
import warnings
warnings.filterwarnings('ignore')

import csv
import pandas as pd
import time

#%%

begin_time = time.time()
print(f'Begin Time : {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(begin_time))}')

file = './out_put/encode_data_sample.csv'
df = pd.read_csv(file, index_col=0)

end_time = time.time()
print(f'End Time : {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_time))}')

#%%

#对编码之后的数据进行分片
begin_time = time.time()
print(f'Begin Time : {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(begin_time))}')

#将数据分为train/validata/testdata三部分
df_1 = df[df['click'] == 1]
df_0 = df[df['click'] == 0]

df_1_test = df_1.sample(frac=0.3, random_state=100)
df_0_test = df_0.sample(frac=0.3, random_state=100)

df_1_other = df_1[~df_1.index.isin(df_1_test.index)]  # 剩下的
df_0_other = df_0[~df_0.index.isin(df_0_test.index)]

df_1_vali = df_1_other.sample(frac=0.2, random_state=100)  # 取到vali的数据
df_0_vali = df_0_other.sample(frac=0.2, random_state=100)  # 取到vali的数据

df_1_train = df_1_other[~df_1_other.index.isin(df_1_vali.index)]  # 取到剩下的训练的数据
df_0_train = df_0_other[~df_0_other.index.isin(df_0_vali.index)]  # 取到剩下的训练的数据

#合并1/0
df_train = pd.concat([df_1_train, df_0_train], ignore_index=True)
df_vali = pd.concat([df_1_vali, df_0_vali], ignore_index=True)
df_test = pd.concat([df_1_test, df_0_test], ignore_index=True)

print(f'--split data : {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))}')

nums_train = df_train['click'].count()
nums_vali = df_vali['click'].count()
nums_test = df_test['click'].count()

print(f'--split rate train VS vali VS test: {nums_train}:{nums_vali}:{nums_test}')

df_train.to_csv('./out_put/encode_data_train.csv')
df_vali.to_csv('./out_put/encode_data_vali.csv')
df_test.to_csv('./out_put/encode_data_test.csv')

end_time = time.time()
print(f'End Time : {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_time))}')

#%%

df_1_other.head()

#%%

df_1.head()

#%%


