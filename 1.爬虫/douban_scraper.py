# ============================================================
# 豆瓣短评爬虫 —— 春节档三部影片（好评/中评/差评）
# ============================================================
# 依赖库安装：
#   pip install requests beautifulsoup4 tqdm
# Cookie 从 Network 面板复制，保持最新有效，过期后需重新获取
# 输出文件：
#   三部电影各自生成一个 CSV，合并后也可用于后续分析
#   （UTF-8-BOM 编码，可直接用 Excel 打开）
# ============================================================

import requests
from bs4 import BeautifulSoup
import csv
import time
import random
from tqdm import tqdm

# ────────────────────────────────────────────────────────────
# 【配置区】— 所有可修改参数集中在此
# ────────────────────────────────────────────────────────────

# 三部影片配置：名称 + 豆瓣 Subject ID
MOVIES = [
    {"name": "飞驰人生3",     "subject_id": "37311135"},
    {"name": "镖人：风起大漠", "subject_id": "36474027"},
    {"name": "惊蛰无声",      "subject_id": "37242440"},
]

PERCENT_TYPE = ["h", "m", "l"]      # h=好评 / m=中评 / l=差评
TARGET_COUNT = 400                   # 每种类型目标爬取条数
PAGE_SIZE    = 20                    # 豆瓣每页固定20条

# 评价类型 → 中文名称映射（用于日志显示）
TYPE_NAME_MAP = {
    "h": "好评",
    "m": "中评",
    "l": "差评",
}

# 评价类型 → 数字映射（写入 comment_type 字段）
TYPE_VALUE_MAP = {
    "h":  1,   # 好评
    "m":  0,   # 中评
    "l": -1,   # 差评
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/146.0.0.0 Safari/537.36"
    ),
    "Cookie": (
        """bid=gSdd4iJrenw; _pk_id.100001.4cf6=13484670a3c7f642.1776081080.; __utmc=30149280; __utmz=30149280.1776081080.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmc=223695111; __utmz=223695111.1776081080.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); ap_v=0,6.0; __yadk_uid=gVJU7Nr9REYdgGafOtJB08COE8U38Bej; dbcl2="294327412:Dn7O6T9SoQ8"; ck=igwV; push_noty_num=0; push_doumail_num=0; ll="118159"; frodotk_db="b8b52c3977f73e3d2a1f84ac67e5bab7"; _vwo_uuid_v2=DDA98CB4F21B6AD0AF9B750A9548B42EF|de62fb909ee7d816c0d95adb63151ebb; __utmv=30149280.29432; _pk_ses.100001.4cf6=1; __utma=30149280.73280191.1776081080.1776081080.1776086772.2; __utmb=30149280.1.10.1776086772; __utma=223695111.1965576466.1776081080.1776081080.1776086772.2; __utmb=223695111.0.10.1776086772"""
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
    ),
    "Accept-Language": "zh-CN,zh;q=0.9",
}

# 星级 class 名称 → 数字评分映射
RATING_MAP = {
    "allstar10": 1,
    "allstar20": 2,
    "allstar30": 3,
    "allstar40": 4,
    "allstar50": 5,
}

# ────────────────────────────────────────────────────────────
# 函数：爬取单页评论，返回评论列表
# ────────────────────────────────────────────────────────────

def fetch_page(subject_id, movie_name, start, page_num, percent_type):
    """
    爬取豆瓣短评页面的一页数据。
    :param subject_id:   影片豆瓣 Subject ID
    :param movie_name:   影片名称（写入 movie_name 字段）
    :param start:        该页起始序号（0, 20, 40, ...）
    :param page_num:     页码（用于记录 source_page 字段）
    :param percent_type: 评价类型（h/m/l）
    :return:             该页所有评论的字典列表
    """
    url = (
        f"https://movie.douban.com/subject/{subject_id}/comments"
        f"?percent_type={percent_type}&start={start}"
        f"&limit={PAGE_SIZE}&status=P&sort=new_score"
    )

    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.encoding = "utf-8"
    except requests.RequestException as e:
        tqdm.write(f"  ⚠️  第{page_num}页请求失败：{e}")
        return []

    # 检查是否被重定向到登录页
    if "accounts.douban.com" in response.url or response.status_code == 403:
        tqdm.write("  ⚠️  Cookie 已失效或被拦截，请重新获取！")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    comment_items = soup.find_all("div", class_="comment-item")

    if not comment_items:
        tqdm.write(f"  ⚠️  第{page_num}页未找到评论，可能已到末页或被限流。")
        return []

    type_label = TYPE_NAME_MAP.get(percent_type, percent_type)
    page_data = []
    for idx, item in enumerate(comment_items, start=1):

        # ── 评论文本 ──────────────────────────────────────────
        span = item.find("span", class_="short")
        comment_text = span.get_text(strip=True) if span else ""

        # ── 评分 ─────────────────────────────────────────────
        rating_span = item.find("span", class_=lambda c: c and c.startswith("allstar"))
        rating = RATING_MAP.get(rating_span["class"][0], None) if rating_span else None

        # ── 发布时间 ──────────────────────────────────────────
        time_span = item.find("span", class_="comment-time")
        created_at = time_span.get_text(strip=True) if time_span else ""

        # ── 获赞数 ────────────────────────────────────────────
        votes_span = item.find("span", class_="votes")
        try:
            votes_count = int(votes_span.get_text(strip=True)) if votes_span else 0
        except ValueError:
            votes_count = 0

        # ── 评论字数（程序计算）──────────────────────────────
        comment_length = len(comment_text)

        page_data.append({
            "movie_name":     movie_name,
            "comment_type":   TYPE_VALUE_MAP.get(percent_type, 0),  # 好评=1 / 中评=0 / 差评=-1
            "comment_text":   comment_text,
            "rating":         rating,
            "votes_count":    votes_count,
            "created_at":     created_at,
            "comment_length": comment_length,
            "source_page":    page_num,
        })

    return page_data


# ────────────────────────────────────────────────────────────
# 函数：爬取某一类型的全部评论，返回列表
# ────────────────────────────────────────────────────────────

def crawl_by_type(subject_id, movie_name, percent_type):
    """
    按评价类型爬取指定数量的评论。
    :param subject_id:   影片豆瓣 Subject ID
    :param movie_name:   影片名称
    :param percent_type: 评价类型（h/m/l）
    :return:             该类型的评论字典列表
    """
    type_label = TYPE_NAME_MAP.get(percent_type, percent_type)
    total_pages = TARGET_COUNT // PAGE_SIZE

    type_data = []

    # 使用 tqdm 进度条
    with tqdm(
        total=TARGET_COUNT,
        desc=f"📥 {type_label}",
        unit="条",
        bar_format="{l_bar}{bar:30}{r_bar}",
        colour={
            "h": "green",
            "m": "yellow",
            "l": "red",
        }.get(percent_type, None),
    ) as pbar:

        for page_num in range(1, total_pages + 1):
            start = (page_num - 1) * PAGE_SIZE

            page_data = fetch_page(subject_id, movie_name, start, page_num, percent_type)

            if not page_data:
                tqdm.write(f"  ⛔ 【{type_label}】第{page_num}页无数据，终止本类型爬取。")
                break

            type_data.extend(page_data)
            pbar.update(len(page_data))
            pbar.set_postfix(页=f"{page_num}/{total_pages}", 累计=len(type_data))

            # 随机延迟 2—4 秒，避免被豆瓣限流
            if page_num < total_pages:
                delay = random.uniform(2, 4)
                time.sleep(delay)

    tqdm.write(f"  ✅ 【{type_label}】爬取完成，共 {len(type_data)} 条")
    return type_data

# ────────────────────────────────────────────────────────────
# 主流程：循环三部影片 × 三种评价类型，每部影片输出一个 CSV
# ────────────────────────────────────────────────────────────

def crawl_movie(movie):
    """
    爬取单部影片的全部评价类型评论，写入独立 CSV。
    :param movie: {"name": ..., "subject_id": ...}
    """
    movie_name = movie["name"]
    subject_id = movie["subject_id"]
    output_file = f"{movie_name}.csv"
    total_target = TARGET_COUNT * len(PERCENT_TYPE)

    print(f"\n{'═' * 55}")
    print(f"🎬 开始爬取《{movie_name}》短评")
    print(f"   Subject ID：{subject_id}")
    print(f"   每类目标：{TARGET_COUNT} 条，总计 {total_target} 条")
    print(f"   输出文件：{output_file}")
    print(f"{'═' * 55}")

    all_data = []

    for percent_type in PERCENT_TYPE:
        type_label = TYPE_NAME_MAP.get(percent_type, percent_type)
        print(f"\n{'─' * 55}")
        print(f"▶ 正在爬取【{type_label}】...")
        print(f"{'─' * 55}")

        type_data = crawl_by_type(subject_id, movie_name, percent_type)
        all_data.extend(type_data)

        # 不同评价类型之间额外间隔 5—8 秒
        if percent_type != PERCENT_TYPE[-1]:
            gap = random.uniform(5, 8)
            print(f"  ⏳ 切换评价类型，等待 {gap:.1f} 秒...")
            time.sleep(gap)

    # ── 写入 CSV ──────────────────────────────────────────────
    fieldnames = [
        "movie_name", "comment_type", "comment_text",
        "rating", "votes_count", "created_at",
        "comment_length", "source_page"
    ]

    with open(output_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_data)

    print(f"\n✅ 《{movie_name}》已保存至：{output_file}，共 {len(all_data)} 条")
    for t in PERCENT_TYPE:
        label = TYPE_NAME_MAP[t]
        count = sum(1 for d in all_data if d["comment_type"] == TYPE_VALUE_MAP[t])
        print(f"     {label}：{count} 条")


def main():
    print("🚀 豆瓣春节档三部影片短评爬虫启动")
    print(f"   影片列表：{'、'.join(m['name'] for m in MOVIES)}")
    print(f"   每类每部目标：{TARGET_COUNT} 条\n")

    for i, movie in enumerate(MOVIES):
        crawl_movie(movie)

        # 不同影片之间额外间隔 8—12 秒
        if i < len(MOVIES) - 1:
            gap = random.uniform(8, 12)
            print(f"\n⏳ 切换影片，等待 {gap:.1f} 秒...\n")
            time.sleep(gap)

    print(f"\n{'═' * 55}")
    print("🎉 全部影片爬取完毕！")
    print(f"{'═' * 55}")


if __name__ == "__main__":
    main()
