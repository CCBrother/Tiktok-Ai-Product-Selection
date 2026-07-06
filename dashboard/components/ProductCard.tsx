import Link from "next/link";
import { ArrowUpRight, TrendingUp } from "lucide-react";
import type { ProductRow } from "../lib/api";
import { LifecycleBadge } from "./LifecycleBadge";

export function ProductCard({ product, rank }: { product: ProductRow; rank?: number }) {
  const level = product.decision.recommendation_level;
  return (
    <Link className="product-card" href={`/products/${product.id}`}>
      <div>
        <div className="product-card-top">
          {rank ? <span className="rank">#{rank}</span> : null}
          <LifecycleBadge product={product} />
          <span className={`level level-${level}`}>{level}</span>
        </div>
        <h3>{product.product_name}</h3>
        <div className="muted">{product.category}</div>
        <p>{product.score.explanation}</p>
        <div className="product-signals">
          <span><TrendingUp size={14} /> Growth {product.score.growth_score}</span>
          <span>Profit {product.score.profit_score}</span>
          <span>Viral {product.score.viral_score}</span>
        </div>
      </div>
      <div className="score" aria-label={`AI score ${product.score.ai_score}`}>
        {product.score.ai_score}
        <ArrowUpRight size={18} />
      </div>
    </Link>
  );
}
