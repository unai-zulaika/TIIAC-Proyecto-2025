from sqlalchemy.orm import Session
import models, schemas

# --- CUSTOMERS ---
def get_customer(db: Session, customer_id: int):
    return db.query(models.Customer).filter(models.Customer.customer_id == customer_id).first()


# --- ARTÍCULOS ---
def get_article(db: Session, article_id: int):
    return db.query(models.Article).filter(models.Article.article_id == article_id).first()


# --- INTERACTIONS ---
def create_interaction(db: Session, interaction: schemas.Interaction):
    db_interaction = models.Interaction(
        customer_id=interaction.customer_id,
        article_id=interaction.article_id,
        rating=interaction.rating
    )
    db.add(db_interaction)
    db.commit()
    db.refresh(db_interaction)
    return db_interaction
