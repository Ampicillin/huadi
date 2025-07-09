import pandas as pd
import os
import numpy as np

# 文件路径
input_file = r"E:\work\huadi\2.clean\项目数据_老人_with_id.xlsx"
output_dir = r"E:\work\huadi\2.clean"

# 检查输入文件是否存在
if not os.path.exists(input_file):
    print(f"错误：文件 {input_file} 不存在")
    exit(1)

# 读取数据
try:
    df = pd.read_excel(input_file, engine="openpyxl")
    print("成功读取输入文件")
except Exception as e:
    print(f"读取文件失败：{e}")
    print("请确认文件是有效的 XLSX 文件，且未损坏")
    print("确保已安装 openpyxl, pandas, numpy（pip install openpyxl pandas numpy）")
    exit(1)

# 定义字段
fixed_columns = ["ID", "姓名", "性别", "出生日期", "职业", "学历"]
health_columns = {
    "心电": ["正常", "T波异常", "ST改变", "房颤"],
    "葡萄糖": ["-", "+1", "+2", "+3"],
    "白细胞": ["-", "+1", "+2", "+3"],
    "亚硝酸盐": ["-", "+"],
    "尿胆原": ["-", "+"],
    "蛋白质": ["-", "+1", "+2", "+3"],
    "潜血": ["-", "+1", "+2", "+3"],
    "酮体": ["-", "+1", "+2", "+3"],
    "胆红素": ["-", "+"],
    "维生素C": ["-", "+"]
}
numeric_columns = [
    "身高", "体重", "BMI", "腰围", "臀围", "腰臀比", "收缩压", "舒张压", 
    "血氧(%)", "脉率", "血糖(mmol/L)", "脂肪(%)", "胆固醇", "用力肺活量(L)", 
    "尿酸", "骨密度", "睡眠总时长", "心率", "水分含量(%)", "基础代谢率", 
    "体温", "血红蛋白", "总胆固醇", "甘油三酯", "高密度脂蛋白", "低密度脂蛋白", 
    "PH值", "呼吸"
]

# 检查必要列
required_columns = fixed_columns + list(health_columns.keys()) + numeric_columns + ["年龄"]
missing_columns = [col for col in required_columns if col not in df.columns]
if missing_columns:
    print(f"错误：缺少以下列：{missing_columns}")
    exit(1)

# 转换数值列为 float64
for col in numeric_columns:
    df[col] = df[col].astype("float64")

# 模拟 2020-2025 年数据
current_df = df.copy()
for year in range(2020, 2026):
    # 复制数据
    year_df = current_df.copy()
    
    # 处理年龄
    if year == 2020:
        year_df["年龄"] = year_df["年龄"] - 6
    else:
        year_df["年龄"] = year_df["年龄"] + 1
    
    # 非数值字段突变（除 2020 年外）
    if year > 2020:
        for col, values in health_columns.items():
            mask = np.random.random(len(year_df)) < 0.04
            year_df.loc[mask, col] = np.random.choice(values, size=mask.sum())
    
    # 数值字段变化（除 2020 年外）
    if year > 2020:
        # 身高：10% 概率减少 0.1-0.5 厘米，90% 概率减少 0.05-0.2 厘米
        height_mask = np.random.random(len(year_df)) < 0.1
        year_df.loc[height_mask, "身高"] = year_df.loc[height_mask, "身高"] - np.random.uniform(-0.1, 0.5, size=height_mask.sum())
        year_df.loc[~height_mask, "身高"] = year_df.loc[~height_mask, "身高"] - np.random.uniform(-0.05, 0.2, size=(~height_mask).sum())
        year_df["身高"] = year_df["身高"].round(1)
        
        # 体重：10% 概率 ±5%，90% 概率 ±2%
        weight_mask = np.random.random(len(year_df)) < 0.1
        year_df.loc[weight_mask, "体重"] = year_df.loc[weight_mask, "体重"] * (1 + np.random.uniform(-0.15, 0.15, size=weight_mask.sum()))
        year_df.loc[~weight_mask, "体重"] = year_df.loc[~weight_mask, "体重"] * (1 + np.random.uniform(-0.05, 0.05, size=(~weight_mask).sum()))
        year_df["体重"] = year_df["体重"].round(1)
        
        # 其他数值字段：10% 概率 ±5%，90% 概率 ±2%
        for col in [c for c in numeric_columns if c not in ["身高", "体重", "BMI", "腰臀比"]]:
            mask = np.random.random(len(year_df)) < 0.1
            year_df.loc[mask, col] = (year_df.loc[mask, col] * (1 + np.random.uniform(-0.20, 0.20, size=mask.sum()))).round(1)
            year_df.loc[~mask, col] = (year_df.loc[~mask, col] * (1 + np.random.uniform(-0.05, 0.05, size=(~mask).sum()))).round(1)
        
        # 重新计算 BMI 和 腰臀比
        year_df["BMI"] = (year_df["体重"] / (year_df["身高"] / 100) ** 2).round(1)
        year_df["腰臀比"] = (year_df["腰围"] / year_df["臀围"]).round(1)
    
    # 保存文件
    output_file = os.path.join(output_dir, f"项目数据-{year}.xlsx")
    try:
        year_df.to_excel(output_file, engine="openpyxl", index=False)
        print(f"成功生成 {output_file}")
    except Exception as e:
        print(f"保存 {output_file} 失败：{e}")
        exit(1)
    
    # 更新当前数据为下一年的基础
    current_df = year_df.copy()

print("所有年份数据生成完成")
