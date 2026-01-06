import pandas as pd
import matplotlib.pyplot as plt

# 设置matplotlib支持中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
plt.rcParams['axes.unicode_minus'] = False    # 正确显示负号

# 读取数据
path = 'junyi/junyi_Exercise_table.csv'
df = pd.read_csv(path, encoding="utf-8", low_memory=False)

# 将area列中的空值填充为'unknown'
df['area'] = df['area'].fillna('unknown')

# 绘制散点图，用颜色区分不同的area
plt.figure(figsize=(7, 5))  # 调整图表大小
for area, group in df.groupby('area'):
    plt.scatter(group['h_position'], group['v_position'], label=area, s=20)  # 调整点的大小

plt.title('知识在领域上的分布')  # 设置中文标题
plt.xlabel('h_position')
plt.ylabel('v_position')

# 调整图例位置到图表外侧
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), title='Area')

# 保存图表到本地
plt.savefig('scatter_plot.png', dpi=300, bbox_inches='tight')  # 保存图表，dpi设置分辨率，bbox_inches='tight'确保图例不丢失

plt.show()