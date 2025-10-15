import ProfileHeader from "../components/ProfileHeader";

export default function Home() {
  const user = {
    name: "María Vivar",
    image: "https://i.pravatar.cc/80?img=47", // avatar de muestra
  };

  const purchasedItems = [
    { id: 1, img: "https://picsum.photos/id/1011/200", name: "Chaqueta beige" },
    { id: 2, img: "https://picsum.photos/id/1012/200", name: "Blusa blanca" },
    { id: 3, img: "https://picsum.photos/id/1013/200", name: "Pantalón negro" },
    { id: 4, img: "https://picsum.photos/id/1014/200", name: "Abrigo largo" },
    { id: 5, img: "https://picsum.photos/id/1015/200", name: "Falda midi" },
  ];

  const recommendedItems = [
    { id: 101, img: "https://picsum.photos/id/1020/200", name: "Vestido azul" },
    { id: 102, img: "https://picsum.photos/id/1021/200", name: "Camisa vaquera" },
    { id: 103, img: "https://picsum.photos/id/1022/200", name: "Pantalón beige" },
    { id: 104, img: "https://picsum.photos/id/1023/200", name: "Top lila" },
    { id: 105, img: "https://picsum.photos/id/1024/200", name: "Cazadora cuero" },
  ];

  return (
    <div className="home-container">
      <ProfileHeader user={user} />

      <section className="purchased-section">
        <h2>🛍️ Tus compras recientes</h2>
        <div className="scroll-container">
          {purchasedItems.map(item => (
            <a key={item.id} href={`/product/${item.id}`} className="item-card">
              <img src={item.img} alt={item.name} />
              <p>{item.name}</p>
            </a>
          ))}
        </div>
      </section>

      <section className="recommended-section">
        <h2>✨ Recomendados para ti</h2>
        <div className="recommend-grid">
          {recommendedItems.map(item => (
            <a key={item.id} href={`/product/${item.id}`} className="item-card">
              <img src={item.img} alt={item.name} />
              <p>{item.name}</p>
            </a>
          ))}
        </div>
      </section>
    </div>
  );
}
