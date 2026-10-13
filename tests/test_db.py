

def test_database_tables_and_seeds(db_conn):
    """
    [ARCH-2663-AC1] Verifies database tables and baseline enterprise seeds exist.
    """
    cursor = db_conn.cursor()

    # Verify users
    cursor.execute("SELECT COUNT(*) as count FROM users")
    user_count = cursor.fetchone()["count"]
    assert user_count >= 2, f"Expected at least 2 seed users, found {user_count}"

    # Verify timecards
    cursor.execute("SELECT COUNT(*) as count FROM timecards")
    tc_count = cursor.fetchone()["count"]
    assert tc_count >= 1, "Expected seeded timecards"

    # Verify leave balances
    cursor.execute("SELECT COUNT(*) as count FROM leave_balances")
    lb_count = cursor.fetchone()["count"]
    assert lb_count >= 1, "Expected seeded leave balances"

    # Verify audit ledger
    cursor.execute("SELECT COUNT(*) as count FROM audit_ledger")
    aud_count = cursor.fetchone()["count"]
    assert aud_count >= 1, "Expected seeded genesis audit block"
