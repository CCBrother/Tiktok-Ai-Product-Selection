import { fetchProduct } from "../../../lib/api";
import { LifecycleBadge } from "../../../components/LifecycleBadge";
import { ScoreBars } from "../../../components/ScoreBars";

export default async function ProductDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const product = await fetchProduct(id);
  const score = product.score;
  const explanation = product.decision.explanation_bundle;

  return (
    <main className="shell">
      <header className="topbar">
        <div className="brand">
          <strong>{product.product_name}</strong>
          <span>{product.category}</span>
        </div>
        <nav className="nav">
          <a href="/">返回</a>
        </nav>
      </header>

      <section className="content">
        <div className="metrics">
          <div className="metric"><span>AI评分</span><strong>{score.ai_score}</strong></div>
          <div className="metric"><span>推荐等级</span><strong>{product.decision.recommendation_level}</strong></div>
          <div className="metric"><span>建议售价</span><strong>${product.decision.suggested_price_min_usd}-${product.decision.suggested_price_max_usd}</strong></div>
          <div className="metric"><span>建议采购</span><strong>${product.decision.suggested_procurement_cost_usd}</strong></div>
        </div>

        <div className="detail-grid">
          <section className="panel">
            <div className="panel-head">
              <h2>AI Report</h2>
              <LifecycleBadge product={product} />
            </div>
            <p>{product.decision.reasoning}</p>
            <p>{product.score.explanation}</p>
            <div className="report-block">
              <span>Summary</span>
              <p>{explanation.summary}</p>
            </div>
            <div className="report-block">
              <span>Risk analysis</span>
              <p>{explanation.risk_explanation}</p>
            </div>
            <div className="report-block">
              <span>Price guidance</span>
              <p>{explanation.pricing_suggestion}</p>
            </div>
            <div className="report-block">
              <span>Sourcing</span>
              <p>{explanation.sourcing_suggestion}</p>
            </div>
            <div className="report-block">
              <span>Competition</span>
              <p>{explanation.competition_explanation}</p>
            </div>
            <div className="report-block">
              <span>Lifecycle</span>
              <p>{explanation.lifecycle_explanation}</p>
            </div>
            <div className="report-block">
              <span>Virality</span>
              <p>{explanation.virality_explanation}</p>
            </div>
            {explanation.alerts.length > 0 && (
              <div className="report-block">
                <span>Alerts</span>
                <p>{explanation.alerts.join("；")}</p>
              </div>
            )}
          </section>

          <section className="panel">
            <h2>Score Visualization</h2>
            <ScoreBars
              items={[
                { label: "Growth", value: score.growth_score },
                { label: "Trend", value: score.trend_score },
                { label: "Competition", value: score.competition_score },
                { label: "Profit", value: score.profit_score },
                { label: "Review", value: score.review_score },
                { label: "Lifecycle", value: score.lifecycle_score },
                { label: "Supply", value: score.supply_score },
                { label: "Copy", value: score.copy_difficulty_score },
                { label: "Content", value: score.content_score },
                { label: "Virality", value: score.viral_score }
              ]}
            />
          </section>
        </div>
      </section>
    </main>
  );
}
