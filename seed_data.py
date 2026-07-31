from faker import Faker
from database import SessionLocal
from models import Transaction
from fraud_engine import calculate_risk
import random

fake = Faker()

db = SessionLocal()

transactions = []

for _ in range(5000):

    amount = random.randint(100, 100000)

    transaction_data = type("TransactionData", (), {
        "user_id": random.randint(1, 200),
        "amount": amount,
        "merchant": fake.company(),
        "location": fake.city(),
        "device": random.choice(["Android", "iPhone", "Web"])
    })

    score, fraud, reason = calculate_risk(transaction_data, db)

    transactions.append(
        Transaction(
            user_id=transaction_data.user_id,
            amount=transaction_data.amount,
            merchant=transaction_data.merchant,
            location=transaction_data.location,
            device=transaction_data.device,
            risk_score=score,
            is_fraud=fraud,
            fraud_reason=reason
        )
    )

db.bulk_save_objects(transactions)
db.commit()

print("5000 transactions inserted successfully!")