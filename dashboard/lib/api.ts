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
    risk_score: number;
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
      ai_decision_engine?: AIDecisionEngine;
    };
  };
};

export type AIDecisionEngine = {
  go_no_go: {
    status: "GO" | "TEST" | "SKIP";
    reasons: string[];
  };
  positioning: {
    positioning: string;
    target_audience: string[];
    usage_scenarios: string[];
    emotional_selling_point: string;
  };
  pricing: {
    price_min_usd: number;
    price_anchor_usd: number;
    price_max_usd: number;
    cost_min_usd: number;
    cost_max_usd: number;
    multiplier: number;
    rationale: string;
  };
  video_scripts: Array<Record<string, string>>;
  supply: {
    supplier_availability: string;
    moq: string;
    risk: string;
    time_to_launch_days: string;
    marks: string[];
  };
  final_decision: {
    launch_or_not: string;
    why_now: string;
    expected_win_rate: string;
    expected_lifecycle_days: string;
    recommended_budget: string;
    expected_roi_range: string;
  };
  business_report?: BusinessDecisionReport;
};

export type BusinessDecisionReport = {
  decision_header: {
    product: string;
    ai_score: number;
    recommendation: "GO" | "TEST" | "SKIP";
    operator_view: string;
    objective: string;
    viral_test_window: string;
  };
  should_launch: {
    decision: "GO" | "TEST" | "SKIP";
    answer: string;
    why_now: string;
    supporting_signals: string[];
    decision_rules: string[];
  };
  how_to_sell: {
    positioning: string;
    target_audience: string[];
    usage_scenarios: string[];
    emotional_selling_point: string;
    offer_strategy: string[];
    landing_message: string;
  };
  pricing: {
    recommended_range_usd: string;
    main_test_price_usd: number;
    procurement_cost_range_usd: string;
    multiplier: number;
    target_margin_pct: string;
    test_ladder: string[];
    rationale: string;
  };
  tiktok_content: {
    content_difficulty: string;
    primary_angle: string;
    first_video_batch: Array<Record<string, string>>;
    creator_brief: string[];
    success_metric: string;
  };
  supply_chain: {
    feasibility: string;
    supplier_availability: string;
    moq: string;
    time_to_launch: string;
    marks: string[];
    procurement_action: string[];
    risk: string;
  };
  copyability: {
    can_copy: string;
    copy_difficulty: string;
    legal_risk: string;
    complexity_risk: string;
    influencer_dependency: string;
    replication_path: string[];
  };
  test_plan: {
    window: string;
    recommended_budget: string;
    expected_win_rate: string;
    expected_lifecycle: string;
    expected_roi_range: string;
    first_72h_actions: string[];
    scale_rule: string;
    kill_rule: string;
  };
  risk_control: {
    risk_level: string;
    risk_score: number;
    watch_items: string[];
    operator_note: string;
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
  const data = await res.json();
  return data.data ?? data;
}
