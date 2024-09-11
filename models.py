from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class Subscriber(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(120), unique=True)
    referral_code: Mapped[str] = mapped_column(String(20), unique=True)
    referrer_id: Mapped[int] = mapped_column(Integer, ForeignKey('subscriber.id'), nullable=True)
    referral_count: Mapped[int] = mapped_column(Integer, default=0)

    referrer = relationship("Subscriber", remote_side=[id], backref="referrals")
