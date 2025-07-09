
import pandas as pd
import os
from scipy import stats

# 检查文件是否存在
file_path = r"E:\work\huadi\2.clean\项目数据_.xlsx"
if not os.path.exists(file_path):
    print(f"错误：文件 {file_path} 不存在")
    exit(1)

# 尝试读取文件（优先 XLSX/XLS，再尝试 CSV）
try:
    df = pd.read_excel(file_path, engine="openpyxl")
    print("成功读取 XLSX 文件")
except Exception as e:
    print(f"读取 XLSX 文件失败：{e}")
    print("尝试使用 xlrd 引擎（适用于 .xls 文件）")
    try:
        df = pd.read_excel(file_path, engine="xlrd")
        print("成功读取 XLS 文件")
    except Exception as e2:
        print(f"读取 XLS 文件失败：{e2}")
        print("尝试作为 CSV 文件读取（可能错误命名为 .xlsx）")
        try:
            df = pd.read_csv(file_path, encoding="utf-8-sig")
            print("成功读取 CSV 文件")
        except Exception as e3:
            print(f"读取 CSV 文件失败：{e3}")
            print("请确认文件格式：")
            print("1. 用 Excel 打开确认是否为有效 XLSX/XLS 文件")
            print("2. 若为 CSV，改后缀为 .csv 并重试")
            print("3. 确保已安装 openpyxl, xlrd, pandas（pip install openpyxl xlrd>=2.0.1 pandas）")
            exit(1)

# 删除“出生地”和“住址”列
if "出生地" in df.columns and "住址" in df.columns:
    df.drop(columns=["出生地", "住址"], inplace=True)
else:
    print("警告：'出生地' 或 '住址' 列不存在，请检查列名")

# 处理出生日期：清理 ** 并格式化
df["出生日期"] = df["出生日期"].str.replace(r"\*+", "", regex=True)
df["出生日期"] = pd.to_datetime(df["出生日期"], format="%Y%m", errors='coerce')
df["出生日期"] = df["出生日期"].apply(lambda x: x.strftime("%Y/%m") if pd.notnull(x) else None)

# 导出清洗后的数据（无异常值筛选）
df.to_excel(r"E:\work\huadi\2.clean\项目数据_初清洗.xlsx", engine="openpyxl", index=False)

# 读取清洗后的 XLSX 文件
df_cleaned = pd.read_excel(r"E:\work\huadi\2.clean\项目数据_初清洗.xlsx", engine="openpyxl")

# 筛选老年人（年龄 > 65）
if "年龄" in df_cleaned.columns:
    df_seniors = df_cleaned[df_cleaned["年龄"] > 65]
else:
    print("错误：'年龄' 列不存在，无法筛选老年人")
    exit(1)

# 对老年人数据进行异常值筛选
numeric_cols = df_seniors.select_dtypes(include=['float64', 'int64']).columns
valid_numeric_cols = [col for col in numeric_cols if df_seniors[col].std() > 1e-8]
z_scores = df_seniors[valid_numeric_cols].apply(stats.zscore, nan_policy='omit')
df_seniors_cleaned = df_seniors[(abs(z_scores) < 3).all(axis=1)]

# 导出筛选后的老年人数据
df_seniors_cleaned.to_excel(r"E:\work\huadi\2.clean\项目数据_老人.xlsx", engine="openpyxl", index=False)

