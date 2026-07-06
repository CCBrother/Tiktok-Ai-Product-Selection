export type ProductRow = {
  id: number;
  product_key: string;
  product_name: string;
  category: string;
  gross_margin_pct: number;
  landed_profit_usd: number;
  score: {
    ai_score: number;
    growth_score: number;
    trend_score: number;
    competition_score: number;
    profit_score: number;
    review_score: number;
    lifecycle_score: number;
    supply_score: number;
    copy_difficulty_score: number;
    content_score: number;
    viral_score: number;
    explanation: string;
  };
  decision: {
    recommendation_level: "S" | "A" | "B" | "C";
    reasoning: string;
    risk_analysis: string;
    suggested_price_min_usd: number;
    suggested_price_max_usd: number;
    suggested_procurement_cost_usd: number;
    explanation_bundle: {
      gpt_explanation: string;
      risk_explanation: string;
      recommendation_text: string;
      pricing_suggestion: string;
      sourcing_suggestion: string;
      competition_explanation: string;
      lifecycle_explanation: string;
      virality_explanation: string;
      summary: string;
      alerts: string[];
    };
  };
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export async function fetchTopProducts(limit = 20): Promise<ProductRow[]> {
  const res = await fetch(`${API_BASE}/top-products?limit=${limit}`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error("Failed to load top products");
  }
  const data = await res.json();
  return data.items;
}

export async function fetchProduct(id: string): Promise<ProductRow> {
  const res = await fetch(`${API_BASE}/product/${id}`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error("Failed to load product");
  }
  return res.json();
}
