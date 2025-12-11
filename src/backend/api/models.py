from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(String, primary_key=True, index=True)
    FN = Column(Boolean, default=False)
    Active = Column(Boolean, default=True)
    club_member_status = Column(String(50))
    fashion_news_frequency = Column(String(50))
    age = Column(Integer)
    postal_code = Column(String(20))

    interactions = relationship("Interaction", back_populates="customer")


class Article(Base):
    __tablename__ = "articles"

    article_id = Column(Integer, primary_key=True, index=True)
    product_code = Column(String(50))
    prod_name = Column(String(255))
    product_type_no = Column(Integer)
    product_type_name = Column(String(100))
    product_group_name = Column(String(100))
    graphical_appearance_no = Column(Integer)
    graphical_appearance_name = Column(String(100))
    colour_group_code = Column(Integer)
    colour_group_name = Column(String(50))
    perceived_colour_value_id = Column(Integer)
    perceived_colour_value_name = Column(String(50))
    perceived_colour_master_id = Column(Integer)
    perceived_colour_master_name = Column(String(50))
    department_no = Column(Integer)
    department_name = Column(String(50))
    index_code = Column(Integer)
    index_name = Column(String(50))
    index_group_no = Column(Integer)
    index_group_name = Column(String(50))
    section_no = Column(Integer)
    section_name = Column(String(50))
    garment_group_no = Column(Integer)
    garment_group_name = Column(String(50))
    detail_desc = Column(String(255))

    interactions = relationship("Interaction", back_populates="article")


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String, ForeignKey("customers.customer_id", ondelete="CASCADE"))
    article_id = Column(Integer, ForeignKey("articles.article_id", ondelete="CASCADE"))
    rating = Column(Float, nullable=True)  # opcional

    customer = relationship("Customer", back_populates="interactions")
    article = relationship("Article", back_populates="interactions")