import pandas as pd
from scipy import stats

# 读取 CSV 文件
df = pd.read_csv(r"E:/work/huadi/2.clean/项目数据.csv")

# 删除“住址”和“出生地”中的“**”
df["住址"] = df["住址"].str.replace(r"\*+", "", regex=True)
df["出生地"] = df["出生地"].str.replace(r"\*+", "", regex=True)

# 处理出生日期：清理 ** 并格式化
df["出生日期"] = df["出生日期"].str.replace(r"\*+", "", regex=True)
df["出生日期"] = pd.to_datetime(df["出生日期"], format="%Y%m", errors='coerce')
df["出生日期"] = df["出生日期"].apply(lambda x: x.strftime("%Y/%m") if pd.notnull(x) else None)

# 清除数值列异常值（排除方差接近0的列）
numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
valid_numeric_cols = [col for col in numeric_cols if df[col].std() > 1e-8]

z_scores = df[valid_numeric_cols].apply(stats.zscore, nan_policy='omit')
df_cleaned = df[(abs(z_scores) < 3).all(axis=1)]

# 导出清洗后的数据
df_cleaned.to_csv(r"E:/work/huadi/2.clean/项目数据_cleaned.csv", index=False)
