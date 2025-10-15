import { useState, useEffect } from "react";
import RecommendationGrid from "../components/RecommendationGrid";
import LoadingSpinner from "../components/LoadingSpinner";
import UserSelector from "../components/UserSelector";

export default function UserRecommendations() {
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const mockUsers = [
      { user_id: 1, name: "Usuario 1" },
      { user_id: 2, name: "Usuario 2" },
    ];
    setUsers(mockUsers);
    setSelectedUser(mockUsers[0].user_id);
  }, []);

  useEffect(() => {
    if (!selectedUser) return;
    setLoading(true);
    fetch(`http://localhost:5000/recommendations?user_id=${selectedUser}`)
      .then(res => res.json())
      .then(data => {
        setRecommendations(data);
        setLoading(false);
      })
      .catch(() => {
        setRecommendations([]);
        setLoading(false);
      });
  }, [selectedUser]);

  return (
    <div>
      <div className="mb-6">
        <UserSelector
          users={users}
          selectedUser={selectedUser}
          onChange={setSelectedUser}
        />
      </div>
      {loading ? <LoadingSpinner /> : <RecommendationGrid items={recommendations} />}
    </div>
  );
}
