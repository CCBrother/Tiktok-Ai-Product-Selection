import type { ProductRow } from "../lib/api";

export function getLifecycleStage(product: ProductRow) {
  const stage = product.decision.lifecycle;
  if (stage) {
    return {
      NEW: "新兴",
      RISING: "上升",
      HOT: "爆发",
      PEAK: "高峰",
      DECLINING: "下降",
      DEAD: "死亡"
    }[stage];
  }
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
