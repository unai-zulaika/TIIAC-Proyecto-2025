import { Link } from "react-router-dom";

export default function Home() {
  return (
    <div className="text-center mt-20">
      <h2 className="text-3xl font-bold mb-4">Bienvenido a FashionAI Labs</h2>
      <p className="mb-6">Descubre recomendaciones personalizadas de moda al estilo Instagram Explore.</p>
      <Link to="/users" className="bg-pink-600 text-white px-6 py-3 rounded hover:bg-pink-700">
        Ver Recomendaciones
      </Link>
    </div>
  );
}
