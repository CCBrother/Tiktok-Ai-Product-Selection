import { ProductExplorer } from "../components/ProductExplorer";
import { fetchTopProducts } from "../lib/api";

export default async function HomePage() {
  const products = await fetchTopProducts(20);

  return (
    <main className="shell">
      <ProductExplorer products={products} />
    </main>
  );
}
