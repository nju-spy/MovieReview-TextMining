# 依赖：pip install pandas matplotlib
# 输出：
#   图1 - 不同发布时段的用户星级比例分布（堆叠条形图，保存为 图1_时段→星级分布.png）
#   图2 - 不同星级用户的发布时段比例分布（堆叠条形图，保存为 图2_星级→时段分布.png）

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# ── 0. 全局设置 ────────────────────────────────────────────────
plt.rcParams['font.sans-serif'] = ['SimHei']   # Windows 中文字体
# plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # Mac 用户取消注释
plt.rcParams['axes.unicode_minus'] = False

DATA_PATH = "../1.爬虫/合并数据.csv"
TIME_ORDER = ["上午", "下午", "晚上", "深夜"]   # 时段排列顺序（从早到晚）

# ── 1. 读取并清洗数据 ──────────────────────────────────────────
df = pd.read_csv(DATA_PATH)
df["created_at"] = pd.to_datetime(df["created_at"], errors='coerce')
df = df.dropna(subset=['rating', 'created_at'])
df['rating'] = df['rating'].astype(int)

def get_time_period(dt):
    """将 datetime 映射为一天四个时段"""
    hour = dt.hour
    if   6  <= hour < 12: return "上午"
    elif 12 <= hour < 18: return "下午"
    elif 18 <= hour < 24: return "晚上"
    else:                  return "深夜"

df["time_period"] = df["created_at"].apply(get_time_period)

# ── 2. 图1：各时段内星级比例（行=时段，列=rating） ──────────────
cross1 = pd.crosstab(df['time_period'], df['rating'], normalize='index')
cross1 = cross1.reindex(TIME_ORDER)

print("【图1】各时段内星级分布比例（%）：")
print((cross1 * 100).round(2))

fig1, ax1 = plt.subplots(figsize=(10, 6))
cross1.plot(
    kind='bar', stacked=True, ax=ax1,
    color=['#c94c4c', '#4a7a9b', '#579670', '#d8957e', '#8c7cac'],
    edgecolor='white'
)
ax1.set_title("不同发布时段的用户星级 (Rating) 比例分布", fontsize=16, pad=15)
ax1.set_xlabel("发布时段", fontsize=14)
ax1.set_ylabel("占该时段评论总数的比例", fontsize=14)
ax1.xaxis.set_tick_params(rotation=0, labelsize=12)
ax1.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
ax1.legend(title="星级 (Rating)", bbox_to_anchor=(1.02, 1), loc='upper left')

for c in ax1.containers:
    labels = [f"{w*100:.1f}%" if (w := v.get_height()) > 0.02 else '' for v in c]
    ax1.bar_label(c, labels=labels, label_type='center',
                  color='white', fontsize=10, fontweight='bold')

fig1.tight_layout()
fig1.savefig("图1_时段→星级分布.png", dpi=150, bbox_inches="tight")
plt.show()

# ── 3. 图2：各星级内时段比例（行=rating，列=时段） ──────────────
cross2 = pd.crosstab(df['rating'], df['time_period'], normalize='index')
cross2 = cross2[TIME_ORDER]

print("\n【图2】各星级内时段分布比例（%）：")
print((cross2 * 100).round(2))

fig2, ax2 = plt.subplots(figsize=(10, 6))
cross2.plot(
    kind='bar', stacked=True, ax=ax2,
    colormap='Set2', edgecolor='white'
)
ax2.set_title("不同星级 (Rating) 用户的发布时段比例分布", fontsize=16, pad=15)
ax2.set_xlabel("用户打分星级 (1-5星)", fontsize=14)
ax2.set_ylabel("该星级内各时段评论的占比", fontsize=14)
ax2.xaxis.set_tick_params(rotation=0, labelsize=12)
ax2.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
ax2.legend(title="发布时段", bbox_to_anchor=(1.02, 1), loc='upper left')

for c in ax2.containers:
    labels = [f"{w*100:.1f}%" if (w := v.get_height()) > 0.03 else '' for v in c]
    ax2.bar_label(c, labels=labels, label_type='center', color='black', fontsize=10)

fig2.tight_layout()
fig2.savefig("图2_星级→时段分布.png", dpi=150, bbox_inches="tight")
plt.show()

# ── 结论参考 ──────────────────────────────────────────────────
# 1.约 80% 的评论集中在下午和晚上（12:00-24:00），上午和深夜较少。
# 2.深夜差评比例最高，好评比例最低；上午好评比例最高
