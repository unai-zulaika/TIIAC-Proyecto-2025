import ProductCard from "./ProductCard";

export default function RecommendationGrid({ items }) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
      {items.map(item => (
        <ProductCard key={item.article_id} product={item} />
      ))}
    </div>
  );
}
