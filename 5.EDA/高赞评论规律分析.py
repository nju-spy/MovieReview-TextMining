# 依赖：pip install pandas matplotlib seaborn scipy
# 输出：
#   图9 - 高赞vs普通评论评分分布（箱线图，保存为 图9_高赞评分分布.png）
#   图10 - 高赞vs普通评论字数分布（箱线图，保存为 图10_高赞字数分布.png）
#   图11 - 高赞评论情感倾向对比（分组柱状图，保存为 图11_高赞情感倾向.png）
#   统计检验结果（控制台输出）

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# ── 0. 全局设置 ────────────────────────────────────────────────
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

MOVIES = {
    '飞驰人生3': '../2.预处理/飞驰人生3_cleaned.csv',
    '镖人_风起大漠': '../2.预处理/镖人_风起大漠_cleaned.csv',
    '惊蛰无声': '../2.预处理/惊蛰无声_cleaned.csv'
}

COLORS = {
    '高赞': '#FF6B6B',
    '普通': '#95A5A6'
}

# ── 1. 读取并合并数据 ──────────────────────────────────────────
all_data = []
for movie_name, path in MOVIES.items():
    df = pd.read_csv(path)
    df['movie_name'] = movie_name.replace('_', '：')
    # 创建高赞标签（1=高赞, 0=普通）
    df['vote_category'] = df['is_high_vote'].map({1: '高赞', 0: '普通'})
    all_data.append(df)

df_all = pd.concat(all_data, ignore_index=True)

# ── 2. 图9：高赞 vs 普通评论的评分分布 ──────────────────────────
fig9, ax = plt.subplots(figsize=(10, 6))

# 准备数据
data_to_plot = [
    df_all[df_all['vote_category'] == '高赞']['rating'].values,
    df_all[df_all['vote_category'] == '普通']['rating'].values
]

bp = ax.boxplot(data_to_plot, labels=['高赞评论', '普通评论'], patch_artist=True,
                showfliers=False,
                medianprops=dict(color='white', linewidth=2))

bp['boxes'][0].set_facecolor(COLORS['高赞'])
bp['boxes'][1].set_facecolor(COLORS['普通'])
for box in bp['boxes']:
    box.set_alpha(0.8)

ax.set_title('高赞评论 vs 普通评论的评分分布', fontsize=16, fontweight='bold', pad=15)
ax.set_ylabel('评分星级', fontsize=14)
ax.set_ylim(0.5, 5.5)
ax.set_yticks(range(1, 6))

plt.tight_layout()
fig9.savefig("图9_高赞评分分布.png", dpi=150, bbox_inches="tight")
plt.show()

# ── 3. 图10：高赞 vs 普通评论的字数分布 ───────────────────────
fig10, ax = plt.subplots(figsize=(10, 6))

data_to_plot = [
    df_all[df_all['vote_category'] == '高赞']['comment_length'].values,
    df_all[df_all['vote_category'] == '普通']['comment_length'].values
]

bp = ax.boxplot(data_to_plot, labels=['高赞评论', '普通评论'], patch_artist=True,
                showfliers=False,
                medianprops=dict(color='white', linewidth=2))

bp['boxes'][0].set_facecolor(COLORS['高赞'])
bp['boxes'][1].set_facecolor(COLORS['普通'])
for box in bp['boxes']:
    box.set_alpha(0.8)

ax.set_title('高赞评论 vs 普通评论的字数分布', fontsize=16, fontweight='bold', pad=15)
ax.set_ylabel('评论字数', fontsize=14)

plt.tight_layout()
fig10.savefig("图10_高赞字数分布.png", dpi=150, bbox_inches="tight")
plt.show()

# ── 4. 统计检验 ────────────────────────────────────────────────
print("=" * 60)
print("【统计检验结果】")
print("=" * 60)

# 4.1 评分差异检验
high_vote_ratings = df_all[df_all['vote_category'] == '高赞']['rating']
normal_ratings = df_all[df_all['vote_category'] == '普通']['rating']

stat_rating, p_rating = stats.mannwhitneyu(high_vote_ratings, normal_ratings, alternative='two-sided')

print("\n1. 评分差异检验 (Mann-Whitney U)")
print(f"   高赞评论平均评分: {high_vote_ratings.mean():.3f} (中位数: {high_vote_ratings.median()})")
print(f"   普通评论平均评分: {normal_ratings.mean():.3f} (中位数: {normal_ratings.median()})")
print(f"   统计量: {stat_rating:.2f}, p值: {p_rating:.6f}")
print(f"   结论: {'差异显著' if p_rating < 0.05 else '差异不显著'} (α=0.05)")

# 4.2 字数差异检验
high_vote_len = df_all[df_all['vote_category'] == '高赞']['comment_length']
normal_len = df_all[df_all['vote_category'] == '普通']['comment_length']

stat_len, p_len = stats.mannwhitneyu(high_vote_len, normal_len, alternative='two-sided')

print("\n2. 字数差异检验 (Mann-Whitney U)")
print(f"   高赞评论平均字数: {high_vote_len.mean():.1f} (中位数: {high_vote_len.median():.1f})")
print(f"   普通评论平均字数: {normal_len.mean():.1f} (中位数: {normal_len.median():.1f})")
print(f"   统计量: {stat_len:.2f}, p值: {p_len:.6f}")
print(f"   结论: {'差异显著' if p_len < 0.05 else '差异不显著'} (α=0.05)")

# ── 5. 图11：各影片高赞评论的情感倾向对比 ─────────────────────
fig11, ax = plt.subplots(figsize=(10, 6))

# 按影片和高赞类型分组统计情感倾向
sentiment_data = []
for movie in df_all['movie_name'].unique():
    movie_df = df_all[df_all['movie_name'] == movie]
    for vote_cat in ['高赞', '普通']:
        subset = movie_df[movie_df['vote_category'] == vote_cat]
        sentiment_counts = subset['comment_type'].value_counts()
        
        # 计算各类情感占比
        total = len(subset)
        if total > 0:
            pos_pct = sentiment_counts.get(1, 0) / total * 100
            neu_pct = sentiment_counts.get(0, 0) / total * 100
            neg_pct = sentiment_counts.get(-1, 0) / total * 100
            sentiment_data.append({
                'movie': movie,
                'vote_category': vote_cat,
                '好评': pos_pct,
                '中评': neu_pct,
                '差评': neg_pct
            })

sentiment_df = pd.DataFrame(sentiment_data)

# 绘制分组柱状图
movies = sentiment_df['movie'].unique()
x = range(len(movies))
width = 0.35

# 好评占比对比
fig11, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# 左图：好评占比
high_vote_pos = sentiment_df[sentiment_df['vote_category'] == '高赞']['好评'].values
normal_pos = sentiment_df[sentiment_df['vote_category'] == '普通']['好评'].values

ax1.bar([i - width/2 for i in x], high_vote_pos, width, label='高赞评论', color=COLORS['高赞'], edgecolor='white')
ax1.bar([i + width/2 for i in x], normal_pos, width, label='普通评论', color=COLORS['普通'], edgecolor='white')
ax1.set_title('好评占比对比', fontsize=14, fontweight='bold')
ax1.set_ylabel('好评占比 (%)', fontsize=12)
ax1.set_xticks(x)
ax1.set_xticklabels(movies, rotation=15, ha='right')
ax1.legend()
ax1.set_ylim(0, 100)

# 右图：差评占比
high_vote_neg = sentiment_df[sentiment_df['vote_category'] == '高赞']['差评'].values
normal_neg = sentiment_df[sentiment_df['vote_category'] == '普通']['差评'].values

ax2.bar([i - width/2 for i in x], high_vote_neg, width, label='高赞评论', color=COLORS['高赞'], edgecolor='white')
ax2.bar([i + width/2 for i in x], normal_neg, width, label='普通评论', color=COLORS['普通'], edgecolor='white')
ax2.set_title('差评占比对比', fontsize=14, fontweight='bold')
ax2.set_ylabel('差评占比 (%)', fontsize=12)
ax2.set_xticks(x)
ax2.set_xticklabels(movies, rotation=15, ha='right')
ax2.legend()
ax2.set_ylim(0, 100)

fig11.suptitle('高赞 vs 普通评论的情感倾向对比', fontsize=16, fontweight='bold')
plt.tight_layout()
fig11.savefig("图11_高赞情感倾向.png", dpi=150, bbox_inches="tight")
plt.show()

print("\n3. 情感倾向对比")
for movie in movies:
    movie_data = sentiment_df[sentiment_df['movie'] == movie]
    high_data = movie_data[movie_data['vote_category'] == '高赞'].iloc[0]
    normal_data = movie_data[movie_data['vote_category'] == '普通'].iloc[0]
    print(f"\n   {movie}:")
    print(f"     高赞评论 - 好评: {high_data['好评']:.1f}%, 中评: {high_data['中评']:.1f}%, 差评: {high_data['差评']:.1f}%")
    print(f"     普通评论 - 好评: {normal_data['好评']:.1f}%, 中评: {normal_data['中评']:.1f}%, 差评: {normal_data['差评']:.1f}%")

# ── 6. 高赞评论特征总结 ─────────────────────────────────────────
print("\n" + "=" * 60)
print("【高赞评论特征总结】")
print("=" * 60)

# 高赞阈值统计
print(f"\n高赞阈值判定标准: is_high_vote = 1")
print(f"总评论数: {len(df_all)}")
print(f"高赞评论数: {len(df_all[df_all['vote_category'] == '高赞'])} ({len(df_all[df_all['vote_category'] == '高赞'])/len(df_all)*100:.1f}%)")
print(f"普通评论数: {len(df_all[df_all['vote_category'] == '普通'])} ({len(df_all[df_all['vote_category'] == '普通'])/len(df_all)*100:.1f}%)")

print("\n【结论参考】")
print("1. 高赞评论是否显著更长？→ 长文通常更有价值")
print("2. 高赞评论评分是否更极端？→ 极端评价更容易引发共鸣")
print("3. 高赞评论情感倾向分布？→ 正面/负面哪类更容易获赞")
