import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
from config import DB_CONFIG

def get_conn():
    return psycopg2.connect(**DB_CONFIG)


# --- USERS ---------------------------------------------------

def get_user(user_id):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM tg WHERE id=%s", (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user

def set_lang(user_id, lang):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE tg SET lang=%s, updated_at=NOW() WHERE id=%s", (lang, user_id))
    conn.commit()
    cur.close()
    conn.close()

# --- PROGRAMS & OPTIONS --------------------------------------

def get_all_programs():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM program ORDER BY id")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def get_all_tariffs():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM subscription_options ORDER BY id")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def get_tariffs_for_program(program_id):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM subscription_options WHERE program_id=%s ORDER BY id", (program_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def get_tariff_by_id(tariff_id):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM subscription_options WHERE id=%s", (tariff_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row

def get_program_by_id(pid):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM program WHERE id=%s", (pid,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row

# --- LICENSES -----------------------------------------------

def get_licenses_for_user(user_id):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT l.*, p.name as program_name, so.name as tariff_name, so.price as tariff_price
        FROM licenses l
        JOIN program p ON l.program_id = p.id
        JOIN subscription_options so ON l.option_id = so.id
        WHERE l.tg_id=%s
        ORDER BY l.valid_until DESC
    """, (user_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def add_license(user_id, program_id, hwid, valid_until, option_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO licenses (tg_id, program_id, hwid, valid_until, created_at, updated_at, option_id)
        VALUES (%s, %s, %s, %s, NOW(), NOW(), %s)
    """, (user_id, program_id, hwid, valid_until, option_id))
    conn.commit()
    cur.close()
    conn.close()

def renew_license(license_id, days):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE licenses SET valid_until = valid_until + interval '%s days', updated_at = NOW() WHERE id=%s",
        (days, license_id)
    )
    conn.commit()
    cur.execute("SELECT valid_until FROM licenses WHERE id=%s", (license_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return row[0]
    return None


def set_hwid(license_id, new_hwid):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE licenses SET hwid=%s, hwid_updated=NOW(), updated_at=NOW() WHERE id=%s",
        (new_hwid, license_id)
    )
    conn.commit()
    cur.close()
    conn.close()

# --- PAYMENTS -----------------------------------------------

def add_payment(user_id, amount, status, currency, payment_id, pay_url):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO payments (user_id, amount, status, currency, payment_id, pay_url, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, NOW())
    """, (user_id, amount, status, currency, payment_id, pay_url))
    conn.commit()
    cur.close()
    conn.close()

def get_payments_for_user(user_id):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM payments WHERE user_id=%s ORDER BY created_at DESC", (user_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

# --- LOGS ---------------------------------------------------

def add_admin_log(admin_id, user_id, old_value, new_value):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO admin_log (admin_id, user_id, old_value, new_value, created_at)
        VALUES (%s, %s, %s, %s, NOW())
    """, (admin_id, user_id, old_value, new_value))
    conn.commit()
    cur.close()
    conn.close()

def update_balance(user_id, new_balance):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE tg SET balance=%s, updated_at=NOW() WHERE id=%s",
        (new_balance, user_id)
    )
    conn.commit()
    cur.close()
    conn.close()
    
def get_balance(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT balance FROM tg WHERE id=%s", (user_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return row[0]
    return 0
    
def get_user_by_id(user_id):
    return get_user(user_id)
    
def get_users_page(offset=0, limit=50):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM tg ORDER BY id LIMIT %s OFFSET %s", (limit, offset))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows
    
def set_balance(user_id, balance):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE tg SET balance=%s WHERE id=%s", (balance, user_id))
    conn.commit()
    cur.close()
    conn.close()
    
def get_all_licenses():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT l.*, p.name as program_name, so.name as tariff_name, so.price as tariff_price
        FROM licenses l
        JOIN program p ON l.program_id = p.id
        JOIN subscription_options so ON l.option_id = so.id
        ORDER BY l.id DESC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows
    
def block_user_by_id(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE tg SET status='blocked', updated_at=NOW() WHERE id=%s", (user_id,))
    conn.commit()
    cur.close()
    conn.close()
    
def unblock_user_by_id(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE tg SET status='active', updated_at=NOW() WHERE id=%s", (user_id,))
    conn.commit()
    cur.close()
    conn.close()
    
def log_admin_action(admin_id, user_id, old_value, new_value):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO admin_log (admin_id, user_id, old_value, new_value, created_at)
        VALUES (%s, %s, %s, %s, NOW())
    """, (admin_id, user_id, old_value, new_value))
    conn.commit()
    cur.close()
    conn.close()
    
def get_stats(days):
    conn = get_conn()
    cur = conn.cursor()
    since = datetime.now() - timedelta(days=days)
    cur.execute(
        "SELECT COUNT(*), COALESCE(SUM(amount),0) FROM payments WHERE status='success' AND created_at > %s",
        (since,)
    )
    count, money = cur.fetchone()
    cur.close()
    conn.close()
    return count, money
    
def update_tariff_price(tariff_id, new_price):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE subscription_options SET price=%s WHERE id=%s",
        (new_price, tariff_id)
    )
    conn.commit()
    cur.close()
    conn.close()
    
def get_licenses_for_user(user_id, only_active=False):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    sql = """
        SELECT l.*, p.name as program_name, so.name as tariff_name
        FROM licenses l
        JOIN program p ON l.program_id = p.id
        JOIN subscription_options so ON l.option_id = so.id
        WHERE l.tg_id=%s
    """
    params = [user_id]
    if only_active:
        sql += " AND l.valid_until > NOW()"
    sql += " ORDER BY l.valid_until DESC"
    cur.execute(sql, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows
    
def get_total_users():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM tg")
    total = cur.fetchone()[0]
    cur.close()
    conn.close()
    return total

def get_active_subscribers():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(DISTINCT tg_id) FROM licenses WHERE valid_until > NOW()")
    active = cur.fetchone()[0]
    cur.close()
    conn.close()
    return active
