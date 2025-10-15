import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import UserRecommendations from "./pages/UserRecommendations";
import ProductSimilar from "./pages/ProductSimilar";
import About from "./pages/About";

export default function App() {
  return (
    <Router>
      <Navbar />
      <main className="p-6 bg-gray-50 min-h-screen">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/users" element={<UserRecommendations />} />
          <Route path="/products" element={<ProductSimilar />} />
          <Route path="/about" element={<About />} />
        </Routes>
      </main>
    </Router>
  );
}
