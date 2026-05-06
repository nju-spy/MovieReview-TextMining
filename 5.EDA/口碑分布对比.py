# 依赖：pip install pandas matplotlib seaborn
# 输出：
#   图3 - 三部影片评分分布对比（分组柱状图，保存为 图3_评分分布对比.png）
#   图4 - 三部影片评论字数分布对比（箱线图，保存为 图4_字数分布对比.png）
#   图5 - 三部影片高赞评论占比对比（柱状图，保存为 图5_高赞占比对比.png）

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# ── 0. 全局设置 ────────────────────────────────────────────────
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 定义文件路径
MOVIES = {
    '飞驰人生3': '../2.预处理/飞驰人生3_cleaned.csv',
    '镖人_风起大漠': '../2.预处理/镖人_风起大漠_cleaned.csv',
    '惊蛰无声': '../2.预处理/惊蛰无声_cleaned.csv'
}

COLORS = ['#FF6B6B', '#4ECDC4', '#45B7D1']

# ── 1. 读取数据 ────────────────────────────────────────────────
all_data = []
for movie_name, path in MOVIES.items():
    df = pd.read_csv(path)
    df['movie_name'] = movie_name.replace('_', '：')
    all_data.append(df)

df_all = pd.concat(all_data, ignore_index=True)

# ── 2. 图3：三部影片评分分布对比 ─────────────────────────────────
fig3, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)

for idx, (movie_name, _) in enumerate(MOVIES.items()):
    movie_df = df_all[df_all['movie_name'] == movie_name.replace('_', '：')]
    rating_counts = movie_df['rating'].value_counts().sort_index()
    
    # 确保所有评分1-5都有数据
    for r in range(1, 6):
        if r not in rating_counts.index:
            rating_counts[r] = 0
    rating_counts = rating_counts.sort_index()
    
    ax = axes[idx]
    bars = ax.bar(rating_counts.index, rating_counts.values, color=COLORS[idx], edgecolor='white', linewidth=1.5)
    ax.set_title(f'{movie_name.replace("_", "：")}', fontsize=14, fontweight='bold')
    ax.set_xlabel('评分星级', fontsize=12)
    if idx == 0:
        ax.set_ylabel('评论数量', fontsize=12)
    ax.set_xticks(range(1, 6))
    
    # 添加数值标签
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            ax.annotate(f'{int(height)}',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3), textcoords="offset points",
                       ha='center', va='bottom', fontsize=10)

fig3.suptitle('三部影片评分分布对比', fontsize=16, fontweight='bold', y=1.02)
plt.tight_layout()
fig3.savefig("图3_评分分布对比.png", dpi=150, bbox_inches="tight")
plt.show()

print("【图3】评分分布统计：")
for movie_name, _ in MOVIES.items():
    movie_df = df_all[df_all['movie_name'] == movie_name.replace('_', '：')]
    avg_rating = movie_df['rating'].mean()
    print(f"  {movie_name.replace('_', '：')}: 平均评分 = {avg_rating:.2f}")

# ── 3. 图4：三部影片评论字数分布对比 ─────────────────────────────
fig4, ax = plt.subplots(figsize=(10, 6))

movie_order = [name.replace('_', '：') for name in MOVIES.keys()]
data_to_plot = [df_all[df_all['movie_name'] == name]['comment_length'].values for name in movie_order]

bp = ax.boxplot(data_to_plot, labels=movie_order, patch_artist=True,
                showfliers=False,  # 不显示离群点
                medianprops=dict(color='red', linewidth=2))

for patch, color in zip(bp['boxes'], COLORS):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)

ax.set_title('三部影片评论字数分布对比', fontsize=16, fontweight='bold', pad=15)
ax.set_ylabel('评论字数', fontsize=14)
ax.set_xlabel('影片', fontsize=14)

plt.tight_layout()
fig4.savefig("图4_字数分布对比.png", dpi=150, bbox_inches="tight")
plt.show()

print("\n【图4】评论字数统计：")
for movie_name, _ in MOVIES.items():
    movie_df = df_all[df_all['movie_name'] == movie_name.replace('_', '：')]
    print(f"  {movie_name.replace('_', '：')}: 平均字数 = {movie_df['comment_length'].mean():.1f}, 中位数 = {movie_df['comment_length'].median():.1f}")

# ── 4. 图5：三部影片高赞评论占比对比 ────────────────────────────
fig5, ax = plt.subplots(figsize=(8, 6))

high_vote_ratios = []
for movie_name, _ in MOVIES.items():
    movie_df = df_all[df_all['movie_name'] == movie_name.replace('_', '：')]
    ratio = movie_df['is_high_vote'].mean() * 100
    high_vote_ratios.append(ratio)

bars = ax.bar([name.replace('_', '：') for name in MOVIES.keys()], high_vote_ratios, color=COLORS, edgecolor='white', linewidth=2)
ax.set_title('三部影片高赞评论占比对比', fontsize=16, fontweight='bold', pad=15)
ax.set_ylabel('高赞评论占比 (%)', fontsize=14)
ax.set_xlabel('影片', fontsize=14)
ax.set_ylim(0, max(high_vote_ratios) * 1.2)

# 添加数值标签
for bar in bars:
    height = bar.get_height()
    ax.annotate(f'{height:.1f}%',
               xy=(bar.get_x() + bar.get_width() / 2, height),
               xytext=(0, 3), textcoords="offset points",
               ha='center', va='bottom', fontsize=11, fontweight='bold')

plt.tight_layout()
fig5.savefig("图5_高赞占比对比.png", dpi=150, bbox_inches="tight")
plt.show()

print("\n【图5】高赞评论占比：")
for movie_name, ratio in zip(MOVIES.keys(), high_vote_ratios):
    print(f"  {movie_name.replace('_', '：')}: {ratio:.1f}%")

print("\n【结论参考】")
print("1. 通过评分分布可观察各影片的口碑集中趋势与离散程度")
print("2. 评论字数反映观众表达意愿，字数越长通常情感投入越深")
print("3. 高赞评论占比反映评论整体质量与社区活跃度")
