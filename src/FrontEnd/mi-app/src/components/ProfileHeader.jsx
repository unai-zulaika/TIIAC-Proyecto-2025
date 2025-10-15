export default function ProfileHeader({ user }) {
  return (
    <div className="profile-header">
      <img src={user.image} alt="profile" className="profile-img" />
      <span className="profile-name">{user.name}</span>
    </div>
  );
}
