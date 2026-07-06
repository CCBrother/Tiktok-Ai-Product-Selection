"use client";

import { Search, SlidersHorizontal } from "lucide-react";
import { useMemo, useState } from "react";
import type { ProductRow } from "../lib/api";
import { ProductCard } from "./ProductCard";
import { TrendChart } from "./TrendChart";

type Level = "全部" | "S" | "A" | "B" | "C";

export function ProductExplorer({ products }: { products: ProductRow[] }) {
  const [query, setQuery] = useState("");
  const [level, setLevel] = useState<Level>("全部");
  const [category, setCategory] = useState("全部");
  const [minScore, setMinScore] = useState(0);

  const categories = useMemo(
    () => ["全部", ...Array.from(new Set(products.map((item) => item.category))).sort()],
    [products]
  );

  const filtered = useMemo(() => {
    return products
      .filter((item) => item.product_name.toLowerCase().includes(query.toLowerCase()))
      .filter((item) => level === "全部" || item.decision.recommendation_level === level)
      .filter((item) => category === "全部" || item.category === category)
      .filter((item) => item.score.ai_score >= minScore)
      .sort((a, b) => b.score.ai_score - a.score.ai_score);
  }, [category, level, minScore, products, query]);

  return (
    <div className="dashboard-grid">
      <section className="panel main-panel">
        <div className="panel-head">
          <h2>Opportunity Ranking</h2>
          <span>{filtered.length} products</span>
        </div>

        <div className="filters">
          <label className="search-box">
            <Search size={17} />
            <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search products" />
          </label>

          <label>
            <SlidersHorizontal size={16} />
            <select value={level} onChange={(event) => setLevel(event.target.value as Level)}>
              {["全部", "S", "A", "B", "C"].map((item) => <option key={item}>{item}</option>)}
            </select>
          </label>

          <label>
            <span>Category</span>
            <select value={category} onChange={(event) => setCategory(event.target.value)}>
              {categories.map((item) => <option key={item}>{item}</option>)}
            </select>
          </label>

          <label>
            <span>Min score</span>
            <input type="number" min="0" max="100" value={minScore} onChange={(event) => setMinScore(Number(event.target.value))} />
          </label>
        </div>

        <div className="product-list">
          {filtered.slice(0, 16).map((product, index) => (
            <ProductCard key={product.id} product={product} rank={index + 1} />
          ))}
        </div>
      </section>

      <aside className="side-stack">
        <section className="panel">
          <div className="panel-head">
            <h2>Trend Chart</h2>
            <span>Growth score</span>
          </div>
          <TrendChart products={products} />
        </section>

        <section className="panel">
          <div className="panel-head">
            <h2>Score Visualization</h2>
            <span>Top opportunity</span>
          </div>
          <MiniScore product={products[0]} />
        </section>
      </aside>
    </div>
  );
}

function MiniScore({ product }: { product: ProductRow }) {
  const scores = [
    ["Growth", product.score.growth_score],
    ["Trend", product.score.trend_score],
    ["Competition", product.score.competition_score],
    ["Profit", product.score.profit_score],
    ["Virality", product.score.viral_score]
  ];

  return (
    <div className="mini-score">
      <strong>{product.product_name}</strong>
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
