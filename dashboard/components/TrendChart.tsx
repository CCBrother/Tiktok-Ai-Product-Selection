import type { ProductRow } from "../lib/api";

export function TrendChart({ products }: { products: ProductRow[] }) {
  const rows = [...products].sort((a, b) => b.score.growth_score - a.score.growth_score).slice(0, 8);
  const max = Math.max(...rows.map((item) => item.score.growth_score), 1);

  return (
    <div className="trend-chart">
      {rows.map((product, index) => (
        <div className="trend-row" key={product.id}>
          <span>{index + 1}</span>
          <strong title={product.product_name}>{product.product_name}</strong>
          <div className="trend-track">
            <div style={{ width: `${(product.score.growth_score / max) * 100}%` }} />
          </div>
          <em>{product.score.growth_score}</em>
        </div>
      ))}
    </div>
  );
}
