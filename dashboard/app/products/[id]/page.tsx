import { fetchProduct } from "../../../lib/api";
import type { BusinessDecisionReport } from "../../../lib/api";
import { formatProductName } from "../../../lib/productNames";
import { LifecycleBadge } from "../../../components/LifecycleBadge";
import { ProductImage } from "../../../components/ProductImage";
import { ScoreBars } from "../../../components/ScoreBars";

export default async function ProductDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const product = await fetchProduct(id);
  const score = product.score;
  const explanation = product.decision.explanation_bundle;
  const businessReport = explanation.ai_decision_engine?.business_report;

  return (
    <main className="shell">
      <header className="topbar">
        <div className="brand">
          <strong>{formatProductName(product.product_name)}</strong>
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
              <h2>AI商业决策报告</h2>
              <LifecycleBadge product={product} />
            </div>
            <ProductImage productName={product.product_name} large />
            {businessReport ? (
              <BusinessDecisionReportView report={businessReport} />
            ) : (
              <LegacyReport product={product} />
            )}
          </section>

          <section className="panel">
            <h2>评分可视化</h2>
            <ScoreBars
              items={[
                { label: "增长评分", value: score.growth_score },
                { label: "趋势评分", value: score.trend_score },
                { label: "竞争评分", value: score.competition_score },
                { label: "利润评分", value: score.profit_score },
                { label: "评论评分", value: score.review_score },
                { label: "生命周期", value: score.lifecycle_score },
                { label: "供应评分", value: score.supply_score },
                { label: "复制难度", value: score.copy_difficulty_score },
                { label: "内容评分", value: score.content_score },
                { label: "病毒传播", value: score.viral_score },
                { label: "风险评分", value: score.risk_score }
              ]}
            />
          </section>
        </div>
      </section>
    </main>
  );
}

function BusinessDecisionReportView({ report }: { report: BusinessDecisionReport }) {
  return (
    <div className="decision-report">
      <div className="decision-hero">
        <span>{report.decision_header.objective}</span>
        <strong>{report.decision_header.recommendation}</strong>
        <p>{report.decision_header.operator_view}</p>
      </div>

      <div className="report-block">
        <span>1. 是否推出？</span>
        <p><strong>{report.should_launch.answer}</strong></p>
        <p>{report.should_launch.why_now}</p>
        <TagList items={report.should_launch.supporting_signals} />
      </div>

      <div className="report-block">
        <span>2. 如何销售？</span>
        <p><strong>定位：</strong>{report.how_to_sell.positioning}</p>
        <p><strong>人群：</strong>{report.how_to_sell.target_audience.join("、")}</p>
        <p><strong>场景：</strong>{report.how_to_sell.usage_scenarios.join("、")}</p>
        <p><strong>情绪卖点：</strong>{report.how_to_sell.emotional_selling_point}</p>
        <p><strong>落地页话术：</strong>{report.how_to_sell.landing_message}</p>
        <TagList items={report.how_to_sell.offer_strategy} />
      </div>

      <div className="report-block">
        <span>3. 如何定价？</span>
        <p><strong>建议售价：</strong>{report.pricing.recommended_range_usd}</p>
        <p><strong>主测价格：</strong>${report.pricing.main_test_price_usd}</p>
        <p><strong>采购成本：</strong>{report.pricing.procurement_cost_range_usd}；<strong>目标毛利：</strong>{report.pricing.target_margin_pct}</p>
        <TagList items={report.pricing.test_ladder} />
      </div>

      <div className="report-block">
        <span>4. 如何创作热门TikTok内容？</span>
        <p><strong>内容难度：</strong>{report.tiktok_content.content_difficulty}</p>
        <p><strong>核心角度：</strong>{report.tiktok_content.primary_angle}</p>
        <ScriptList scripts={report.tiktok_content.first_video_batch} />
        <TagList items={report.tiktok_content.creator_brief} />
        <p><strong>成功指标：</strong>{report.tiktok_content.success_metric}</p>
      </div>

      <div className="report-block">
        <span>5. 供应链可行吗？</span>
        <p><strong>可行性：</strong>{report.supply_chain.feasibility}；<strong>MOQ：</strong>{report.supply_chain.moq}；<strong>上线周期：</strong>{report.supply_chain.time_to_launch}</p>
        <TagList items={[...report.supply_chain.marks, ...report.supply_chain.procurement_action]} />
        <p><strong>供应风险：</strong>{report.supply_chain.risk}</p>
      </div>

      <div className="report-block">
        <span>6. 可以复制吗？</span>
        <p><strong>结论：</strong>{report.copyability.can_copy}；<strong>复制难度：</strong>{report.copyability.copy_difficulty}</p>
        <p><strong>法律风险：</strong>{report.copyability.legal_risk}；<strong>复杂性风险：</strong>{report.copyability.complexity_risk}；<strong>达人依赖：</strong>{report.copyability.influencer_dependency}</p>
        <TagList items={report.copyability.replication_path} />
      </div>

      <div className="report-block">
        <span>7. 7-30天快测计划</span>
        <p><strong>预算：</strong>{report.test_plan.recommended_budget}；<strong>胜率：</strong>{report.test_plan.expected_win_rate}；<strong>ROI：</strong>{report.test_plan.expected_roi_range}</p>
        <TagList items={report.test_plan.first_72h_actions} />
        <p><strong>放量规则：</strong>{report.test_plan.scale_rule}</p>
        <p><strong>停止规则：</strong>{report.test_plan.kill_rule}</p>
      </div>

      <div className="report-block">
        <span>8. 风险控制</span>
        <p><strong>风险等级：</strong>{report.risk_control.risk_level}；<strong>风险分：</strong>{report.risk_control.risk_score}</p>
        <TagList items={report.risk_control.watch_items} />
        <p>{report.risk_control.operator_note}</p>
      </div>
    </div>
  );
}

function ScriptList({ scripts }: { scripts: Array<Record<string, string>> }) {
  const scriptLabels: Record<string, string> = {
    hook_0_3s: "开场钩子",
    problem_3_6s: "痛点",
    solution_6_12s: "解决方案",
    demo_12_20s: "演示",
    reaction_20_25s: "反应",
    cta_25_30s: "行动引导"
  };

  return (
    <div className="script-list">
      {scripts.map((script, index) => (
        <div className="script-card" key={`${script.angle}-${index}`}>
          <strong>{script.angle}</strong>
          <p><span>{scriptLabels.hook_0_3s}</span>{script.hook_0_3s}</p>
          <p><span>{scriptLabels.problem_3_6s}</span>{script.problem_3_6s}</p>
          <p><span>{scriptLabels.solution_6_12s}</span>{script.solution_6_12s}</p>
          <p><span>{scriptLabels.demo_12_20s}</span>{script.demo_12_20s}</p>
          <p><span>{scriptLabels.reaction_20_25s}</span>{script.reaction_20_25s}</p>
          <p><span>{scriptLabels.cta_25_30s}</span>{script.cta_25_30s}</p>
        </div>
      ))}
    </div>
  );
}

function TagList({ items }: { items: string[] }) {
  if (!items.length) {
    return null;
  }
  return (
    <ul>
      {items.map((item) => <li key={item}>{item}</li>)}
    </ul>
  );
}

function LegacyReport({ product }: { product: Awaited<ReturnType<typeof fetchProduct>> }) {
  const explanation = product.decision.explanation_bundle;
  return (
    <>
      <p>{product.decision.reasoning}</p>
      <p>{product.score.explanation}</p>
      <div className="report-block">
        <span>总结</span>
        <p>{explanation.summary}</p>
      </div>
      <div className="report-block">
        <span>风险分析</span>
        <p>{explanation.risk_explanation}</p>
      </div>
      <div className="report-block">
        <span>定价建议</span>
        <p>{explanation.pricing_suggestion}</p>
      </div>
      <div className="report-block">
        <span>供应链建议</span>
        <p>{explanation.sourcing_suggestion}</p>
      </div>
    </>
  );
}
