import { productImagePath, translateProductName } from "../lib/productNames";

export function ProductImage({ productName, large = false }: { productName: string; large?: boolean }) {
  const label = translateProductName(productName) || productName;
  return (
    <div className={large ? "product-image product-image-large" : "product-image"}>
      <img src={productImagePath(productName)} alt={label} loading="lazy" />
    </div>
  );
}
