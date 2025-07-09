
import pandas as pd
import os

# 文件路径
file_path = r"E:\work\huadi\2.clean\项目数据_老人.xlsx"
output_path = r"E:\work\huadi\2.clean\项目数据_老人_with_id.xlsx"

# 检查文件是否存在
if not os.path.exists(file_path):
    print(f"错误：文件 {file_path} 不存在")
    exit(1)

# 读取老年人数据
try:
    df = pd.read_excel(file_path, engine="openpyxl")
    print("成功读取 XLSX 文件")
except Exception as e:
    print(f"读取 XLSX 文件失败：{e}")
    print("请确认文件是有效的 XLSX 文件，且未损坏")
    print("确保已安装 openpyxl, pandas（pip install openpyxl pandas）")
    exit(1)

# 添加顺序编号列（ID）作为主码
df.insert(0, "ID", range(1, len(df) + 1))

# 删除“比重”列（若存在）
if "比重" in df.columns:
    df.drop(columns=["比重"], inplace=True)
else:
    print("警告：'比重' 列不存在，请检查列名")

# 导出修改后的数据
try:
    df.to_excel(output_path, engine="openpyxl", index=False)
    print(f"成功保存到 {output_path}")
except Exception as e:
    print(f"保存文件失败：{e}")
    exit(1)

