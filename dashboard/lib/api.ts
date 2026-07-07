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
    business_decision?: "LAUNCH" | "TEST" | "WATCH" | "SKIP" | null;
    lifecycle?: "NEW" | "RISING" | "HOT" | "PEAK" | "DECLINING" | "DEAD" | null;
    lifecycle_confidence?: number | null;
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

type RadarItem = {
  product_id: string;
  product_name: string;
  opportunity_score: number;
  lifecycle: "NEW" | "RISING" | "HOT" | "PEAK" | "DECLINING" | "DEAD" | "N/A";
  decision: string;
  reason: string;
  action: string;
  supply_score?: number;
  creative_angle?: string;
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
  const radarRes = await fetch(`${API_BASE}/api/radar/today?limit=${limit}`, { cache: "no-store" });
  if (radarRes.ok) {
    const radarData = await radarRes.json();
    const radarItems = radarData.items ?? [];
    if (Array.isArray(radarItems) && radarItems.length > 0) {
      return radarItems.map((item: RadarItem, index: number) => normalizeRadarItem(item, index));
    }
  }

  const res = await fetch(`${API_BASE}/api/ranking?limit=${limit}`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error("Failed to load top products");
  }
  const data = await res.json();
  return Array.isArray(data) ? data : data.items;
}

function normalizeRadarItem(item: RadarItem, index: number): ProductRow {
  const score = Math.round(item.opportunity_score ?? 0);
  const level = score >= 90 ? "S" : score >= 80 ? "A" : score >= 70 ? "B" : "C";
  const lifecycle = item.lifecycle === "N/A" ? null : item.lifecycle;
  return {
    id: index + 1,
    product_key: item.product_id,
    product_name: item.product_name,
    category: "AI Daily Ranking",
    gross_margin_pct: 0,
    landed_profit_usd: 0,
    score: {
      ai_score: score,
      growth_score: score,
      trend_score: score,
      competition_score: score,
      profit_score: score,
      review_score: 0,
      lifecycle_score: lifecycle === "RISING" ? 88 : lifecycle === "HOT" ? 92 : lifecycle === "PEAK" ? 62 : 60,
      supply_score: Math.round(item.supply_score ?? 0),
      copy_difficulty_score: 0,
      content_score: 0,
      viral_score: score,
      risk_score: item.decision === "SKIP" ? 80 : item.decision === "WATCH" ? 55 : 30,
      explanation: item.reason
    },
    decision: {
      recommendation_level: level,
      business_decision: mapRadarDecision(item.decision),
      lifecycle,
      lifecycle_confidence: null,
      reasoning: item.reason,
      risk_analysis: item.action,
      suggested_price_min_usd: 0,
      suggested_price_max_usd: 0,
      suggested_procurement_cost_usd: 0,
      explanation_bundle: {
        gpt_explanation: item.reason,
        risk_explanation: item.action,
        recommendation_text: item.action,
        pricing_suggestion: "",
        sourcing_suggestion: "",
        competition_explanation: "",
        lifecycle_explanation: String(item.lifecycle),
        virality_explanation: item.creative_angle ?? "",
        summary: item.reason,
        alerts: []
      }
    }
  };
}

function mapRadarDecision(decision: string): "LAUNCH" | "TEST" | "WATCH" | "SKIP" | null {
  if (decision === "TEST NOW") return "TEST";
  if (decision === "TEST" || decision === "WATCH" || decision === "SKIP") return decision;
  return null;
}

export async function fetchProduct(id: string): Promise<ProductRow> {
  const res = await fetch(`${API_BASE}/api/products/${id}`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error("Failed to load product");
  }
  const data = await res.json();
  return normalizeProductDetail(data.data ?? data);
}

function normalizeProductDetail(data: any): ProductRow {
  if (data.product_name && data.decision) {
    return data;
  }
  const score = data.score ?? data.ai_scores?.[0] ?? {};
  const finalScore = Math.round(score.final_score ?? 0);
  const price = Number(data.price ?? 0);
  return {
    id: data.id,
    product_key: data.product_id,
    product_name: data.title,
    category: data.category ?? "Unknown",
    gross_margin_pct: 65,
    landed_profit_usd: Number((price * 0.65).toFixed(2)),
    score: {
      ai_score: finalScore,
      growth_score: Math.round(score.growth_score ?? 0),
      trend_score: Math.round(score.trend_score ?? 0),
      competition_score: Math.round(score.competition_score ?? 0),
      profit_score: Math.round(score.profit_score ?? 0),
      review_score: Math.round((data.rating ?? 0) * 20),
      lifecycle_score: Math.round(score.lifecycle_score ?? 0),
      supply_score: Math.round(score.supply_score ?? 0),
      copy_difficulty_score: Math.round(score.copy_score ?? 0),
      content_score: Math.round(((score.trend_score ?? 0) + (score.virality_score ?? 0)) / 2),
      viral_score: Math.round(score.virality_score ?? 0),
      risk_score: Math.max(0, 100 - Math.round(score.copy_score ?? 0)),
      explanation: score.ai_explanation ?? ""
    },
    decision: {
      recommendation_level: score.recommendation_level ?? "C",
      business_decision: null,
      lifecycle: null,
      lifecycle_confidence: null,
      reasoning: score.ai_explanation ?? "",
      risk_analysis: "上线前检查侵权、认证、履约成本和真实供应商交期。",
      suggested_price_min_usd: Number((price * 0.9).toFixed(2)),
      suggested_price_max_usd: Number((price * 1.15).toFixed(2)),
      suggested_procurement_cost_usd: Number((price * 0.35).toFixed(2)),
      explanation_bundle: {
        gpt_explanation: score.ai_explanation ?? "",
        risk_explanation: "上线前检查侵权、认证、履约成本和真实供应商交期。",
        recommendation_text: "按7-30天窗口进行小预算快测。",
        pricing_suggestion: "以主推价为中心做低价引流和套装锚点。",
        sourcing_suggestion: "询价3-5家供应商，确认MOQ和交期。",
        competition_explanation: "竞争得分越高代表销量信号和低卖家密度更好。",
        lifecycle_explanation: "生命周期以30天历史趋势估算。",
        virality_explanation: "病毒分由播放、点赞、评论和分享合成。",
        summary: score.ai_explanation ?? "",
        alerts: []
      }
    }
  };
}
