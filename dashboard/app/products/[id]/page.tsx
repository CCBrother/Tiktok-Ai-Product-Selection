import { fetchProduct } from "../../../lib/api";
import { formatProductName } from "../../../lib/productNames";
import { LifecycleBadge } from "../../../components/LifecycleBadge";
import { ProductImage } from "../../../components/ProductImage";
import { ScoreBars } from "../../../components/ScoreBars";

export default async function ProductDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const product = await fetchProduct(id);
  const score = product.score;
  const explanation = product.decision.explanation_bundle;
  const blenderReport = product.product_name === "Portable Mini Blender";

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
              <h2>{blenderReport ? "S级测试报告" : "AI Report"}</h2>
              <LifecycleBadge product={product} />
            </div>
            <ProductImage productName={product.product_name} large />
            {blenderReport ? <PortableMiniBlenderReport /> : (
              <>
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
              </>
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
                { label: "Virality", value: score.viral_score },
                { label: "Risk", value: score.risk_score }
              ]}
            />
          </section>
        </div>
      </section>
    </main>
  );
}

function PortableMiniBlenderReport() {
  return (
    <div className="decision-report">
      <div className="decision-hero">
        <span>决策等级</span>
        <strong>S</strong>
        <p>建议立即测试，48小时内进入快测打法。</p>
      </div>

      <div className="report-block">
        <span>1. 是否做？</span>
        <p><strong>建议做。</strong> 48小时内完成上架和首轮素材测试。</p>
      </div>

      <div className="report-block">
        <span>2. 为什么做？</span>
        <ul>
          <li>7天增长 +320%</li>
          <li>达人数量 +180%</li>
          <li>竞争店铺仅 26 家</li>
          <li>正在进入主升浪</li>
          <li>评论正向率 93%</li>
          <li>供应链成熟，1688 可一键复制</li>
        </ul>
      </div>

      <div className="report-block">
        <span>3. 怎么卖</span>
        <p><strong>定位：</strong>便携健康果昔神器</p>
        <p><strong>人群：</strong>健身人群、减脂人群、上班族</p>
        <p><strong>场景：</strong>办公室、健身房、出差</p>
      </div>

      <div className="report-block">
        <span>4. 定价策略</span>
        <p><strong>建议售价：</strong>$19.99 - $29.99</p>
        <p><strong>心理锚点：</strong>低于 $20 引流；$24.99 主推款；$29.99 套装款</p>
        <p><strong>预计成本：</strong>$6 - $9；<strong>利润率：</strong>40% - 60%</p>
      </div>

      <div className="report-block">
        <span>5. 视频脚本</span>
        <p><strong>爆款UGC：</strong>“我以为这只是个普通榨汁机，结果...”</p>
        <p>镜头：开箱、放水果、5秒搅拌、倒出成品、喝一口反应。</p>
        <p><strong>对比型：</strong>传统榨汁机 vs 便携款。</p>
      </div>

      <div className="report-block">
        <span>6. 供应链建议</span>
        <p>1688 已有成熟同款，单价约 ¥25 - ¥45，可定制 Logo，MOQ 50-200。</p>
        <p><strong>风险：</strong>注意电池认证和美国运输要求。</p>
      </div>

      <div className="report-block">
        <span>7. 风险提示</span>
        <p>竞争可能在 2-3 周内上升，需 3 天内快速上架测试。</p>
      </div>

      <div className="report-block">
        <span>8. AI最终建议</span>
        <p><strong>可以做，但必须快测。</strong> 1天上架，3条视频测试，7天内判断是否放量。</p>
      </div>
    </div>
  );
}
