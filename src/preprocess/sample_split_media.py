import pandas as pd

origin_df = pd.read_csv("../../data/xgboost/etl/merge_sample_data_2021-10-21.txt", header=None, sep='#', encoding=u'utf-8', dtype=str)
# print(origin_df)

media = origin_df.groupby([7]).size()
# print(media)

# 筛选点击样本并且指定媒体
df = origin_df[(origin_df[0] == '1') & (origin_df[7] == '31283')]
print(df)

# 对有点击，但转化类型为空值的填充0
df.iloc[:, 3:7].fillna(0, inplace=True)

# 保存筛选后的样本
df.to_csv("../../data/xgboost/etl/train_31283_1021.txt", header=False, index=False, sep='#', encoding=u'utf-8')

# 打印样本比例
df1 = df[df[3] == '1']
df0 = df[df[3] == '0']
print(df1.shape[0])
print(df0.shape[0])
print(df0.shape[0]/df1.shape[0])

# df1.to_csv("../../data/xgboost/etl/train_31283_0929_1.txt", header=False, index=False, sep='#', encoding=u'utf-8')
# df0.to_csv("../../data/xgboost/etl/train_31283_0929_0.txt", header=False, index=False, sep='#', encoding=u'utf-8')

print("save success !")
