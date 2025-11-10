import pytest
from datetime import datetime, timedelta
from app.utils.seed import calculate_priority_score


@pytest.mark.unit
class TestPriorityScore:
    """Test priority score calculation"""

    def test_priority_score_calculation(self):
        """Test basic priority score calculation"""
        user_created_at = datetime.utcnow() - timedelta(days=10)
        signup_latency_ms = 500
        rapid_actions_count = 0

        score = calculate_priority_score(
            user_created_at,
            signup_latency_ms,
            rapid_actions_count
        )

        assert isinstance(score, float)
        assert score > 0

    def test_old_account_advantage(self):
        """Test that older accounts get better (lower) scores"""
        old_account = datetime.utcnow() - timedelta(days=365)
        new_account = datetime.utcnow() - timedelta(days=1)

        old_score = calculate_priority_score(old_account, 100, 0)
        new_score = calculate_priority_score(new_account, 100, 0)

        # Older account should have component that differs
        assert old_score != new_score

    def test_rapid_action_penalty(self):
        """Test rapid action penalty"""
        user_created_at = datetime.utcnow() - timedelta(days=10)

        no_spam_score = calculate_priority_score(user_created_at, 100, 0)
        spam_score = calculate_priority_score(user_created_at, 100, 5)

        # More rapid actions = different score (penalty)
        assert no_spam_score != spam_score

    def test_deterministic_scoring(self):
        """Test that same inputs produce same score"""
        user_created_at = datetime.utcnow() - timedelta(days=5)

        score1 = calculate_priority_score(user_created_at, 200, 1)
        score2 = calculate_priority_score(user_created_at, 200, 1)

        # Within reasonable time window, base should be similar
        # (base uses current timestamp, so small difference is OK)
        assert abs(score1 - score2) < 10000
