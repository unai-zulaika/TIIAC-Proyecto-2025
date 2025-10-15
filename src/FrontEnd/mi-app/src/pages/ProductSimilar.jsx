import { useState, useEffect } from "react";
import RecommendationGrid from "../components/RecommendationGrid";
import LoadingSpinner from "../components/LoadingSpinner";

export default function ProductSimilar() {
  const [productId, setProductId] = useState(1);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetch(`http://localhost:5000/similar?product_id=${productId}`)
      .then(res => res.json())
      .then(data => {
        setRecommendations(data);
        setLoading(false);
      })
      .catch(() => {
        setRecommendations([]);
        setLoading(false);
      });
  }, [productId]);

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">Productos similares</h2>
      {loading ? <LoadingSpinner /> : <RecommendationGrid items={recommendations} />}
    </div>
  );
}
