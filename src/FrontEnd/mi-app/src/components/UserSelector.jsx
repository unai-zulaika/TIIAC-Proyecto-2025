export default function UserSelector({ users, selectedUser, onChange }) {
  return (
    <select
      value={selectedUser}
      onChange={e => onChange(e.target.value)}
      className="border p-2 rounded"
    >
      {users.map(user => (
        <option key={user.user_id} value={user.user_id}>
          {user.name || user.user_id}
        </option>
      ))}
    </select>
  );
}
