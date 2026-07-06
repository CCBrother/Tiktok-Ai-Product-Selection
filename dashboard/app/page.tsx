import { ProductExplorer } from "../components/ProductExplorer";
import { fetchTopProducts } from "../lib/api";

export default async function HomePage() {
  const products = await fetchTopProducts(20);
  const sCount = products.filter((item) => item.decision.recommendation_level === "S").length;
  const avgScore = Math.round(products.reduce((sum, item) => sum + item.score.ai_score, 0) / Math.max(products.length, 1));
  const topGrowth = Math.max(...products.map((item) => item.score.growth_score));

  return (
    <main className="shell">
      <header className="topbar">
        <div className="brand">
          <strong>AI产品雷达</strong>
          <span>美国 TikTok Shop 7-30天病毒潜力</span>
        </div>
        <nav className="nav">
          <a href="/">顶级商机</a>
          <a href="#trends">趋势排名</a>
        </nav>
      </header>

      <section className="content">
        <div className="metrics">
          <div className="metric"><span>候选产品</span><strong>{products.length}</strong></div>
          <div className="metric"><span>S级商机</span><strong>{sCount}</strong></div>
          <div className="metric"><span>平均AI分</span><strong>{avgScore}</strong></div>
          <div className="metric"><span>最高增长分</span><strong>{topGrowth}</strong></div>
        </div>

        <ProductExplorer products={products} />
      </section>
    </main>
  );
}
