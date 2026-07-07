"use client";

import { Search, SlidersHorizontal } from "lucide-react";
import { useMemo, useState } from "react";
import type { ProductRow } from "../lib/api";
import { formatProductName } from "../lib/productNames";
import { ProductCard } from "./ProductCard";
import { TrendChart } from "./TrendChart";

type Level = "全部" | "S" | "A" | "B" | "C";

export function ProductExplorer({ products }: { products: ProductRow[] }) {
  const [query, setQuery] = useState("");
  const [level, setLevel] = useState<Level>("全部");
  const [category, setCategory] = useState("全部");
  const [minScore, setMinScore] = useState(0);
  const sCount = products.filter((item) => item.decision.recommendation_level === "S").length;
  const aCount = products.filter((item) => item.decision.recommendation_level === "A").length;
  const avgScore = Math.round(products.reduce((sum, item) => sum + item.score.ai_score, 0) / Math.max(products.length, 1));
  const topGrowth = Math.max(...products.map((item) => item.score.growth_score));
  const topProduct = products[0];

  const categories = useMemo(
    () => ["全部", ...Array.from(new Set(products.map((item) => item.category))).sort()],
    [products]
  );

  const filtered = useMemo(() => {
    return products
      .filter((item) => formatProductName(item.product_name).toLowerCase().includes(query.toLowerCase()))
      .filter((item) => level === "全部" || item.decision.recommendation_level === level)
      .filter((item) => category === "全部" || item.category === category)
      .filter((item) => item.score.ai_score >= minScore)
      .sort((a, b) => b.score.ai_score - a.score.ai_score);
  }, [category, level, minScore, products, query]);

  return (
    <div className="radar-layout">
      <aside className="radar-left">
        <div className="brand-block">
          <span>AI PRODUCT RADAR</span>
          <h1>AI产品雷达</h1>
          <p>美国 TikTok Shop 7-30天病毒潜力</p>
        </div>

        <nav className="side-nav" aria-label="Dashboard sections">
          <a href="/">顶级商机</a>
          <a href="#ranking">趋势排名</a>
          <a href="#signals">评分信号</a>
        </nav>

        <div className="data-status" aria-label="data source status">
          <strong>PostgreSQL 数据</strong>
          <span>产品、历史快照和AI评分来自后端数据库。</span>
        </div>

        <div className="metrics">
          <div className="metric"><span>候选产品</span><strong>{products.length}</strong></div>
          <div className="metric"><span>S/A级商机</span><strong>{sCount + aCount}</strong></div>
          <div className="metric"><span>平均AI分</span><strong>{avgScore}</strong></div>
          <div className="metric"><span>最高增长分</span><strong>{topGrowth}</strong></div>
        </div>
      </aside>

      <section className="radar-center panel main-panel" id="ranking">
        <div className="panel-head">
          <div>
            <span className="eyebrow">商机排名</span>
            <h2>顶级商机</h2>
          </div>
          <span>{filtered.length} 个产品</span>
        </div>

        <div className="filters">
          <label className="search-box">
            <Search size={17} />
            <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="搜索产品" />
          </label>

          <label>
            <SlidersHorizontal size={16} />
            <select value={level} onChange={(event) => setLevel(event.target.value as Level)}>
              {["全部", "S", "A", "B", "C"].map((item) => <option key={item}>{item}</option>)}
            </select>
          </label>

          <label>
            <span>分类</span>
            <select value={category} onChange={(event) => setCategory(event.target.value)}>
              {categories.map((item) => <option key={item}>{item}</option>)}
            </select>
          </label>

          <label>
            <span>最低分</span>
            <input type="number" min="0" max="100" value={minScore} onChange={(event) => setMinScore(Number(event.target.value))} />
          </label>
        </div>

        <div className="product-list">
          {filtered.slice(0, 16).map((product, index) => (
            <ProductCard key={product.id} product={product} rank={index + 1} />
          ))}
        </div>
      </section>

      <aside className="radar-right side-stack" id="signals">
        <section className="panel hero-signal">
          <div className="panel-head">
            <div>
              <span className="eyebrow">重点信号</span>
              <h2>今日重点</h2>
            </div>
            <span>{topProduct?.decision.recommendation_level}</span>
          </div>
          <strong>{topProduct ? formatProductName(topProduct.product_name) : "暂无产品"}</strong>
          <p>{topProduct?.score.explanation}</p>
          <div className="signal-strip">
            <span>AI {topProduct?.score.ai_score ?? 0}</span>
            <span>增长 {topProduct?.score.growth_score ?? 0}</span>
            <span>病毒传播 {topProduct?.score.viral_score ?? 0}</span>
          </div>
        </section>

        <section className="panel">
          <div className="panel-head">
            <div>
              <span className="eyebrow">趋势图</span>
              <h2>增长趋势</h2>
            </div>
            <span>增长</span>
          </div>
          <TrendChart products={products} />
        </section>

        <section className="panel">
          <div className="panel-head">
            <div>
              <span className="eyebrow">评分结构</span>
              <h2>评分结构</h2>
            </div>
            <span>最高</span>
          </div>
          <MiniScore product={products[0]} />
        </section>
      </aside>
    </div>
  );
}

function MiniScore({ product }: { product: ProductRow }) {
  const scores = [
    ["增长", product.score.growth_score],
    ["趋势", product.score.trend_score],
    ["竞争", product.score.competition_score],
    ["利润", product.score.profit_score],
    ["病毒传播", product.score.viral_score]
  ];

  return (
    <div className="mini-score">
      <strong>{formatProductName(product.product_name)}</strong>
      {scores.map(([label, value]) => (
        <div className="mini-score-row" key={label}>
          <span>{label}</span>
          <div><i style={{ width: `${value}%` }} /></div>
          <em>{value}</em>
        </div>
      ))}
    </div>
  );
}
