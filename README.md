# AI产品雷达

一个本地运行的选品雷达，用来发现未来 7 到 30 天内可能在美国 TikTok Shop 走红的产品。

它不是通用分析仪表盘。它每天只回答五个问题：

- 前20名高潜力产品
- 蓝海产品
- 快速增长产品
- 易复制产品
- 高利润产品

核心原则：不追求完整市场数据，只追踪能影响短期病毒式传播的信号。

## 架构

1. 爬虫层（Playwright）
   - 收集 TikTok Shop 美国站产品、视频、店铺页面信号
   - 原始数据只写入 JSONL 事件，不在爬虫里做商业判断
2. 数据管道层
   - 标准化 raw events
   - 按产品名/链接生成 `product_key` 去重
   - 构建产品历史时间线
3. 数据库层（PostgreSQL）
   - `products`
   - `product_history`
   - `videos`
   - `creators`
   - `shops`
4. AI评分引擎
   - 增长评分
   - 趋势评分
   - 竞争评分
   - 利润评分
   - 评价评分
   - 生命周期评分
   - 供应评分
   - 复制难度评分
   - 病毒式传播评分
5. 决策引擎
   - 推荐等级 S/A/B/C
   - 推理说明文本
   - 风险分析
   - 建议价格区间
   - 建议采购成本
6. API 层（FastAPI）
   - `/products`
   - `/top-products`
   - `/product/{id}`
7. 仪表盘（Next.js）
   - 顶级商机
   - 趋势排名
   - 产品详情AI报告

## 快速开始

生成日报：

```bash
python3 -m ai_product_radar report --input data/sample_products.csv
```

运行后会生成：

- `reports/radar_YYYY-MM-DD.md`
- `reports/radar_YYYY-MM-DD.json`

启动 API：

```bash
python3 -m uvicorn ai_product_radar.api:app --reload
```

启动仪表盘：

```bash
cd dashboard
npm install
npm run dev
```

默认仪表盘读取 `http://localhost:8000`。

## 采集与数据管道

先用 dry-run 验证链路：

```bash
python3 -m ai_product_radar crawl --dry-run --output raw_events/tiktok_shop.jsonl
python3 -m ai_product_radar normalize --input raw_events/tiktok_shop.jsonl --output data/normalized_product_facts.csv
python3 -m ai_product_radar timeline --facts data/normalized_product_facts.csv --output data/product_history.csv
```

安装 Playwright 后可尝试真实采集：

```bash
pip install -e ".[crawler]"
playwright install chromium
python3 -m ai_product_radar crawl --term "pet hair remover" --term "viral kitchen gadget"
```

注意：TikTok Shop 页面可能需要登录态、地区、Cookie 或页面结构适配。爬虫层只保存原始事件，选择器变化时只需要调整 `ai_product_radar/crawler/tiktok_shop.py`。

## PostgreSQL

目标 schema 在：

- `sql/schema.sql`

示例：

```bash
createdb ai_product_radar
psql "$DATABASE_URL" -f sql/schema.sql
```

开发时如果没有 PostgreSQL，也可以先用默认 SQLite 初始化 ORM 表：

```bash
python3 -m ai_product_radar.db.init_db
```

## H组调度系统

已注册 10 个本地调度任务：

- `daily_crawler_job`
- `hourly_update_job`
- `score_recalculation_job`
- `cleanup_job`
- `snapshot_generator`
- `trend_recalculation`
- `alert_trigger`
- `report_generator`
- `system_monitor`
- `failure_recovery_job`

查看任务：

```bash
python3 -m ai_product_radar jobs
```

执行单个任务：

```bash
python3 -m ai_product_radar job report_generator
```

执行全部任务：

```bash
python3 -m ai_product_radar job all --json
```

默认调度任务使用 dry-run 爬虫，适合本地验证。要让爬虫任务尝试真实 Playwright 采集：

```bash
python3 -m ai_product_radar job daily_crawler_job --live
```

## 输入数据

默认输入是 CSV。每行代表一个产品候选，字段如下：

| 字段 | 说明 |
| --- | --- |
| `product_name` | 产品名称 |
| `category` | 类目 |
| `signal_source` | 信号来源，例如 TikTok、Amazon Movers、Reddit、供应链、广告库 |
| `tiktok_mentions_7d` | 近7天相关短视频/帖子提及量 |
| `mention_growth_pct_7d` | 近7天提及增长率 |
| `creator_count_7d` | 近7天参与创作者数量 |
| `avg_video_engagement_pct` | 平均互动率 |
| `shop_competitor_count` | TikTok Shop 美国站同类竞品数量 |
| `amazon_review_count` | Amazon 同类成熟度参考 |
| `unit_cost_usd` | 预估采购成本 |
| `target_price_usd` | 预估售价 |
| `shipping_complexity` | 物流复杂度，1-5，越低越好 |
| `copy_difficulty` | 复制难度，1-5，越低越容易复制 |
| `problem_intensity` | 痛点强度，1-5 |
| `visual_demo_score` | 视频演示冲击力，1-5 |
| `impulse_buy_score` | 冲动购买强度，1-5 |
| `compliance_risk` | 合规风险，1-5，越低越好 |
| `rating_avg` | 当前评分均值，可为空 |
| `rating_count` | 当前评价数量，可为空 |
| `days_since_first_seen` | 首次发现至今天数，可为空 |
| `supplier_count` | 可找到供应商数量，可为空 |
| `inventory_depth` | 可估库存/供给深度，可为空 |
| `sales_growth_pct_7d` | 7天销售增长率，可为空；为空时用提及增长近似 |
| `seller_count` | 卖家数量，可为空；为空时用 TikTok Shop 竞品数量近似 |
| `review_sentiment_score` | 评论情感分，0-100，可为空 |
| `lifecycle_stage` | 生命周期：新兴 / 上升 / 高峰 / 下降，可为空 |
| `min_order_quantity` | 最小起订量，可为空 |
| `lead_time_days` | 交货周期天数，可为空 |
| `content_creation_ease` | TikTok 内容制作便捷度，1-5，可为空 |
| `interaction_velocity` | 互动速度，可为空；为空时用互动率和提及量估算 |
| `notes` | 备注 |

字段不需要完美精确。这个系统的定位是把零散信号转成每日行动清单。

## 评分逻辑

AI评分 0-100，重点偏向未来 7 到 30 天病毒传播潜力。当前权重按你定义的优先级执行；原始权重合计为 105%，代码会按相对权重归一化，确保最终得分仍为 0-100。

| 分项 | 原始权重 | 依据 |
| --- | ---: | --- |
| 成长评分 | 20% | 7天内销售增长率 |
| 趋势评分 | 15% | 视频及创作者成长情况 |
| 竞争得分 | 15% | 卖家数量的倒数 |
| 利润评分 | 10% | 成本后的预估利润率 |
| 评论评分 | 5% | 评论情感分析 |
| 生命周期评分 | 10% | AI分类：新兴 / 上升 / 高峰 / 下降 |
| 供应评分 | 10% | 供应商可用性、最小起订量、交货周期 |
| 复制得分 | 10% | 法律风险 + 复杂性风险 |
| 内容评分 | 5% | 制作 TikTok 内容的便捷程度 |
| 病毒传播评分 | 5% | 互动速度 |

你可以在 `ai_product_radar/scoring.py` 里调整权重。

## 使用真实数据

先用 `data/sample_products.csv` 的格式建立自己的每日信号文件，例如：

```bash
python3 -m ai_product_radar --input data/2026-07-06_signals.csv --date 2026-07-06
```

建议的数据来源：

- TikTok 搜索结果、话题、爆款视频评论区
- TikTok Shop 榜单和相似商品数量
- Amazon Movers & Shakers、评论数和价格
- Reddit、Instagram Reels、YouTube Shorts 的早期讨论
- 1688、Alibaba、Temu 等供应链成本参考

这个版本先做本地评分和报告生成；后续可以接入爬虫、API、OpenAI 解释生成、邮件/飞书每日推送。
