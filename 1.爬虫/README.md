# 豆瓣短评爬虫 `douban_scraper.py`

爬取豆瓣电影三部 2026 年春节档影片的用户短评：

| 影片 | Subject ID |
|---|---|
| 《飞驰人生3》 | 37311135 |
| 《镖人：风起大漠》 | 36474027 |
| 《惊蛰无声》 | 37242440 |

每部影片分别抓取**好评 / 中评 / 差评**三类，每类各 400 条，每部共约 1200 条，三部合计约 3600 条。

每部影片生成一个独立 CSV 文件（UTF-8-BOM 编码，可直接用 Excel 打开）：

```
飞驰人生3.csv
镖人：风起大漠.csv
惊蛰无声.csv
合并数据.csv        ← 手动或后续代码合并
```

每条记录包含以下字段：

| 字段 | 含义 |
|---|---|
| `movie_name` | 影片名称 |
| `comment_type` | 评价类型（好评=1 / 中评=0 / 差评=-1） |
| `comment_text` | 评论正文 |
| `rating` | 用户星级评分（1—5） |
| `votes_count` | 评论获赞数 |
| `created_at` | 评论发布时间 |
| `comment_length` | 评论字符数（程序自动计算） |
| `source_page` | 来源页码（便于追溯） |

---

## 工作原理

### 1. 构造请求 URL

豆瓣短评页面通过 `start` 参数翻页，每页固定 20 条：

```
https://movie.douban.com/subject/{subject_id}/comments
    ?percent_type={h/m/l}&start={0,20,40,...}&limit=20&status=P&sort=new_score
```

- `percent_type=h/m/l` 分别对应好评 / 中评 / 差评
- `sort=new_score` 按热度排序

### 2. 携带 Cookie 模拟登录状态

豆瓣从第 2 页起要求登录验证。脚本在请求头中携带浏览器登录后的 `Cookie`，绕过登录拦截。Cookie 有时效，过期后需从浏览器 Network 面板重新复制。

### 3. 解析 HTML（BeautifulSoup）

请求返回的 HTML 中，每条评论对应一个 `<div class="comment-item">`，从中提取：

- 评论文本：`<span class="short">`
- 星级评分：`<span class="allstar*">` 的 class 名映射到数字
- 发布时间：`<span class="comment-time">`
- 获赞数：`<span class="votes">`

### 4. 反爬策略

- 每翻一页随机等待 **2—4 秒**
- 切换评价类型时额外等待 **5—8 秒**
- 切换影片时额外等待 **8—12 秒**
- 请求头携带真实浏览器 `User-Agent`

### 5. 写出 CSV

所有评论汇总后，用 `csv.DictWriter` 写出，编码 `utf-8-sig`（即 UTF-8-BOM），确保 Excel 正确显示中文。

---

## 依赖

```bash
pip install requests beautifulsoup4 tqdm
```

## 使用前注意

运行前需将脚本中 `HEADERS["Cookie"]` 替换为自己账号的有效 Cookie：

1. 浏览器登录豆瓣
2. 按 F12 打开开发者工具 → Network 面板
3. 刷新任意短评页，找到 `comments` 请求
4. 复制 Request Headers 中的 `Cookie` 字段粘贴至脚本