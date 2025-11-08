from datetime import datetime
from app.config import settings


def calculate_priority_score(
        user_created_at: datetime,
        signup_latency_ms: int,
        rapid_actions_count: int
) -> float:
    """
    Seed-based priority score hesaplama

    Formula:
    priority_score = base + (signup_latency_ms % A) + (account_age_days % B) - (rapid_actions_count % C)

    Daha düşük score = daha yüksek öncelik
    """
    # Account age in days
    account_age_days = (datetime.utcnow() - user_created_at).days

    # Base position (şu anki timestamp'i kullanarak deterministic base)
    base = int(datetime.utcnow().timestamp() * 1000) % 10000

    # Seed katsayıları
    A = settings.seed_a
    B = settings.seed_b
    C = settings.seed_c

    # Priority score
    score = base + (signup_latency_ms % A) + (account_age_days % B) - (rapid_actions_count % C)

    return float(score)


def generate_claim_code() -> str:
    """Benzersiz claim code üret"""
    import secrets
    import string

    # DROPSPOT-ABC123XYZ formatında
    random_part = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(9))
    return f"DROPSPOT-{random_part}"
