from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from database import Base
import datetime


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, nullable=False, index=True)

    amount = Column(Float, nullable=False)

    merchant = Column(String)

    location = Column(String)

    device = Column(String)

    timestamp = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        index=True
    )

    risk_score = Column(Integer, default=0)

    is_fraud = Column(Boolean, default=False)

    fraud_reason = Column(String)