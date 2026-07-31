from datetime import datetime, timedelta
from models import Transaction


def calculate_risk(transaction, db):

    score = 0
    reasons = []

    # Rule 1: High Amount
    if transaction.amount > 50000:
        score += 40
        reasons.append("High Amount")

    # Rule 2: Night Transaction
    hour = datetime.now().hour
    if hour >= 23 or hour <= 5:
        score += 20
        reasons.append("Late Night Transaction")

    # Rule 3: More than 3 transactions in last 10 minutes
    ten_minutes_ago = datetime.now() - timedelta(minutes=10)

    recent_transactions = (
        db.query(Transaction)
        .filter(
            Transaction.user_id == transaction.user_id,
            Transaction.timestamp >= ten_minutes_ago
        )
        .count()
    )

    if recent_transactions >= 3:
        score += 25
        reasons.append("Frequent Transactions")

    # Rule 4 & 5: Previous transaction
    previous = (
        db.query(Transaction)
        .filter(Transaction.user_id == transaction.user_id)
        .order_by(Transaction.timestamp.desc())
        .first()
    )

    if previous:

        if previous.location != transaction.location:
            score += 15
            reasons.append("New Location")

        if previous.device != transaction.device:
            score += 10
            reasons.append("New Device")

    fraud = score >= 50

    return score, fraud, ", ".join(reasons)