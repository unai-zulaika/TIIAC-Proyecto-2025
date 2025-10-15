import { Link } from "react-router-dom";

export default function Navbar() {
  return (
    <nav className="bg-white shadow p-4 flex justify-between items-center">
      <h1 className="font-bold text-xl text-pink-600">FashionAI Labs</h1>
      <div className="space-x-4">
        <Link to="/" className="text-gray-700 hover:text-pink-600">Home</Link>
        <Link to="/users" className="text-gray-700 hover:text-pink-600">Users</Link>
        <Link to="/products" className="text-gray-700 hover:text-pink-600">Products</Link>
        <Link to="/about" className="text-gray-700 hover:text-pink-600">About</Link>
      </div>
    </nav>
  );
}
