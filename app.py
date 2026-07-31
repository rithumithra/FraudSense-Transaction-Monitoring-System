from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from database import engine, Base, SessionLocal
from models import Transaction
from schemas import TransactionCreate, TransactionResponse
from fraud_engine import calculate_risk

Base.metadata.create_all(bind=engine)

app = FastAPI(title="FraudSense Transaction Monitoring System")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home():
    return {"message": "FraudSense API Running"}


@app.post("/transaction", response_model=TransactionResponse)
def create_transaction(transaction: TransactionCreate,
                       db: Session = Depends(get_db)):

    
    score, fraud, reason = calculate_risk(transaction, db)

    db_transaction = Transaction(
        user_id=transaction.user_id,
        amount=transaction.amount,
        merchant=transaction.merchant,
        location=transaction.location,
        device=transaction.device,
        risk_score=score,
        is_fraud=fraud,
        fraud_reason=reason
    )

    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)

    return db_transaction

@app.get("/transactions")
def get_transactions(db: Session = Depends(get_db)):
    return db.query(Transaction).all()

@app.get("/frauds")
def get_frauds(db: Session = Depends(get_db)):
    return db.query(Transaction).filter(
        Transaction.is_fraud == True
    ).all()

@app.get("/transaction/{transaction_id}")
def get_transaction(transaction_id: int,
                    db: Session = Depends(get_db)):

    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id
    ).first()

    if transaction is None:
        return {"message": "Transaction not found"}

    return transaction

@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):

    total_transactions = db.query(Transaction).count()

    fraud_transactions = db.query(Transaction).filter(
        Transaction.is_fraud == True
    ).count()

    genuine_transactions = total_transactions - fraud_transactions

    fraud_percentage = (
        (fraud_transactions / total_transactions) * 100
        if total_transactions > 0
        else 0
    )

    return {
        "total_transactions": total_transactions,
        "fraud_transactions": fraud_transactions,
        "genuine_transactions": genuine_transactions,
        "fraud_percentage": round(fraud_percentage, 2)
    }

@app.get("/high-risk-transactions")
def high_risk_transactions(db: Session = Depends(get_db)):

    return (
        db.query(Transaction)
        .filter(Transaction.risk_score >= 50)
        .order_by(Transaction.risk_score.desc())
        .all()
    )

@app.get("/user/{user_id}/history")
def user_history(user_id: int,
                 db: Session = Depends(get_db)):

    return (
        db.query(Transaction)
        .filter(Transaction.user_id == user_id)
        .order_by(Transaction.timestamp.desc())
        .all()
    )