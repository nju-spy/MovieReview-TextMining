# 依赖：pip install pandas matplotlib
# 输出：
#   图6 - 每日评论数量趋势（三线折线图，保存为 图6_每日评论数趋势.png）
#   图7 - 每日平均评分趋势（三线折线图，保存为 图7_每日平均评分趋势.png）
#   图8 - 每日好评差评比例趋势（堆叠面积图，保存为 图8_每日情感比例趋势.png）

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# ── 0. 全局设置 ────────────────────────────────────────────────
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

MOVIES = {
    '飞驰人生3': '../2.预处理/飞驰人生3_cleaned.csv',
    '镖人_风起大漠': '../2.预处理/镖人_风起大漠_cleaned.csv',
    '惊蛰无声': '../2.预处理/惊蛰无声_cleaned.csv'
}

COLORS = {
    '飞驰人生3': '#FF6B6B',
    '镖人_风起大漠': '#4ECDC4',
    '惊蛰无声': '#45B7D1'
}

# ── 1. 读取并合并数据 ──────────────────────────────────────────
all_data = []
for movie_name, path in MOVIES.items():
    df = pd.read_csv(path)
    df['movie_name'] = movie_name
    df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
    df['comment_date'] = pd.to_datetime(df['comment_date'], errors='coerce')
    all_data.append(df)

df_all = pd.concat(all_data, ignore_index=True)
df_all = df_all.dropna(subset=['comment_date'])

# ── 2. 图6：每日评论数量趋势 ───────────────────────────────────
fig6, ax = plt.subplots(figsize=(12, 6))

for movie_name in MOVIES.keys():
    movie_df = df_all[df_all['movie_name'] == movie_name]
    daily_counts = movie_df.groupby('comment_date').size()
    ax.plot(daily_counts.index, daily_counts.values, 
            marker='o', markersize=4, linewidth=2, 
            label=movie_name.replace('_', '：'), 
            color=COLORS[movie_name])

ax.set_title('每日评论数量趋势', fontsize=16, fontweight='bold', pad=15)
ax.set_xlabel('日期', fontsize=14)
ax.set_ylabel('评论数量', fontsize=14)
ax.legend(loc='upper right', fontsize=11)
ax.grid(True, alpha=0.3)

# 格式化x轴日期
ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
plt.xticks(rotation=45)

plt.tight_layout()
fig6.savefig("图6_每日评论数趋势.png", dpi=150, bbox_inches="tight")
plt.show()

print("【图6】每日评论数量峰值：")
for movie_name in MOVIES.keys():
    movie_df = df_all[df_all['movie_name'] == movie_name]
    daily_counts = movie_df.groupby('comment_date').size()
    peak_date = daily_counts.idxmax()
    peak_count = daily_counts.max()
    print(f"  {movie_name.replace('_', '：')}: {peak_date.strftime('%m-%d')} ({peak_count}条)")

# ── 3. 图7：每日平均评分趋势 ───────────────────────────────────
fig7, ax = plt.subplots(figsize=(12, 6))

for movie_name in MOVIES.keys():
    movie_df = df_all[df_all['movie_name'] == movie_name]
    daily_avg_rating = movie_df.groupby('comment_date')['rating'].mean()
    ax.plot(daily_avg_rating.index, daily_avg_rating.values, 
            marker='s', markersize=4, linewidth=2, 
            label=movie_name.replace('_', '：'), 
            color=COLORS[movie_name])

ax.axhline(y=3, color='gray', linestyle='--', alpha=0.5, label='中性线(3分)')
ax.set_title('每日平均评分趋势', fontsize=16, fontweight='bold', pad=15)
ax.set_xlabel('日期', fontsize=14)
ax.set_ylabel('平均评分', fontsize=14)
ax.set_ylim(1, 5)
ax.legend(loc='best', fontsize=11)
ax.grid(True, alpha=0.3)

ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
plt.xticks(rotation=45)

plt.tight_layout()
fig7.savefig("图7_每日平均评分趋势.png", dpi=150, bbox_inches="tight")
plt.show()

print("\n【图7】平均评分波动范围：")
for movie_name in MOVIES.keys():
    movie_df = df_all[df_all['movie_name'] == movie_name]
    daily_avg = movie_df.groupby('comment_date')['rating'].mean()
    print(f"  {movie_name.replace('_', '：')}: {daily_avg.min():.2f} ~ {daily_avg.max():.2f}")

# ── 4. 图8：每日好评差评比例趋势 ───────────────────────────────
fig8, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)

for idx, movie_name in enumerate(MOVIES.keys()):
    movie_df = df_all[df_all['movie_name'] == movie_name]
    
    # 创建情感标签（好评=1, 中评=0, 差评=-1）
    movie_df['sentiment'] = movie_df['comment_type'].map({1: '好评', 0: '中评', -1: '差评'})
    
    # 按日期和情感分组计数
    daily_sentiment = movie_df.groupby(['comment_date', 'sentiment']).size().unstack(fill_value=0)
    
    # 计算比例
    daily_sentiment_pct = daily_sentiment.div(daily_sentiment.sum(axis=1), axis=0)
    
    ax = axes[idx]
    daily_sentiment_pct.plot(kind='area', stacked=True, ax=ax,
                              color={'好评': '#52c41a', '中评': '#faad14', '差评': '#f5222d'},
                              alpha=0.8)
    ax.set_title(f'{movie_name.replace("_", "：")}', fontsize=13, fontweight='bold')
    ax.set_xlabel('日期', fontsize=11)
    if idx == 0:
        ax.set_ylabel('占比', fontsize=12)
    ax.set_ylim(0, 1)
    ax.legend(loc='upper right', fontsize=9)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    
fig8.suptitle('每日好评/中评/差评比例趋势', fontsize=16, fontweight='bold', y=1.02)
plt.tight_layout()
fig8.savefig("图8_每日情感比例趋势.png", dpi=150, bbox_inches="tight")
plt.show()

# ── 5. 打印时间范围信息 ────────────────────────────────────────
print("\n【数据时间范围】")
for movie_name in MOVIES.keys():
    movie_df = df_all[df_all['movie_name'] == movie_name]
    start_date = movie_df['comment_date'].min()
    end_date = movie_df['comment_date'].max()
    print(f"  {movie_name.replace('_', '：')}: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")

print("\n【结论参考】")
print("1. 上映初期（1月29日-1月31日）评论量通常最高，随后逐渐回落")
print("2. 观察评分趋势可发现口碑发酵规律：是否出现'高开低走'或'逆袭'现象")
print("3. 情感比例趋势揭示观众情绪演化：假期后期差评比例是否上升（审美疲劳）")
