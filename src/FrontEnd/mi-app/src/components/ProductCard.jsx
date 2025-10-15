export default function ProductCard({ product }) {
  return (
    <div className="bg-white shadow rounded-lg overflow-hidden hover:shadow-lg transition">
      <img
        src={product.image_url}
        alt={product.name}
        className="w-full h-48 object-cover"
      />
      <div className="p-3">
        <h3 className="text-sm font-medium">{product.name}</h3>
        <p className="text-gray-500 text-xs">{product.category}</p>
        <p className="text-pink-600 font-semibold">{product.price ? `$${product.price}` : ""}</p>
      </div>
    </div>
  );
}
