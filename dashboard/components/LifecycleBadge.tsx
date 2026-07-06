import type { ProductRow } from "../lib/api";

export function getLifecycleStage(product: ProductRow) {
  const score = product.score.lifecycle_score;
  if (score >= 88) return "新兴";
  if (score >= 76) return "上升";
  if (score >= 52) return "高峰";
  return "下降";
}

export function LifecycleBadge({ product }: { product: ProductRow }) {
  const stage = getLifecycleStage(product);
  return <span className={`lifecycle lifecycle-${stage}`}>{stage}</span>;
}
