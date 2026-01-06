import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

# 设置matplotlib支持中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
plt.rcParams['axes.unicode_minus'] = False    # 正确显示负号

# 读取数据
path = 'junyi/junyi_ProblemLog_original.csv'
df = pd.read_csv(path, encoding="utf-8", low_memory=False)

# 检查'points_earned'列是否存在
if 'points_earned' not in df.columns:
    raise ValueError("CSV文件中不存在'points_earned'列")

# 使用tqdm显示进度条
points_earned = df['points_earned'].dropna().tolist()

# 绘制直方图查看数据分布
plt.hist(points_earned, bins=30, edgecolor='black')
plt.title('Points Earned Distribution')
plt.xlabel('Points Earned')
plt.ylabel('Frequency')
plt.show()

bins = [0, 30, 100, 200, 225]
labels = ['不及格', '及格', '良', '优']

# 使用tqdm包装points_earned列表，显示进度条
for point in tqdm(points_earned, desc='正在处理'):
    pass

plt.figure(figsize=(8, 6))
hist, _ = np.histogram(points_earned, bins=bins)
plt.pie(hist, labels=labels, autopct=lambda p: '{:.1f}%'.format(p), textprops={'fontsize': 12})

# 保存图表到本地
plt.savefig('point_pic.png', dpi=300, bbox_inches='tight')  # 保存图表，dpi设置分辨率，bbox_inches='tight'确保图例不丢失

plt.show()