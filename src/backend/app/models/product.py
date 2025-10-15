from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import BigInteger, String, Text, TIMESTAMP, func


class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = "items"
    # alineado con vuestra ETL (id compartido con imágenes)
    item_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    product_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    category: Mapped[str | None] = mapped_column(String(64), nullable=True)
    brand: Mapped[str | None] = mapped_column(String(64), nullable=True)
    color: Mapped[str | None] = mapped_column(String(64), nullable=True)
    season: Mapped[str | None] = mapped_column(String(32), nullable=True)
    image_s3_key: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str | None] = mapped_column(
        TIMESTAMP(timezone=False),
        server_default=func.now(),
        nullable=True,
    )
