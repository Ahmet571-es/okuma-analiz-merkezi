"""
Veritabanı İşlemleri — SQLite / PostgreSQL
"""

import sqlite3
import hashlib
import os
import json
from datetime import datetime

# ─── Veritabanı Bağlantısı ───────────────────────────────────────────────────

def get_connection():
    """Veritabanı bağlantısı döndürür (SQLite veya PostgreSQL)."""
    db_url = os.environ.get("SUPABASE_DB_URL", "")
    
    if db_url and db_url.startswith("postgresql"):
        try:
            import psycopg2
            conn = psycopg2.connect(db_url)
            conn.autocommit = False
            return conn, "postgresql"
        except Exception:
            pass
    
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "okuma_analiz.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn, "sqlite"


def init_db():
    """Veritabanı tablolarını oluşturur."""
    conn, db_type = get_connection()
    cursor = conn.cursor()
    
    if db_type == "postgresql":
        # PostgreSQL
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                age INTEGER NOT NULL,
                grade INTEGER NOT NULL CHECK (grade BETWEEN 1 AND 8),
                gender VARCHAR(10) NOT NULL,
                email VARCHAR(200) UNIQUE NOT NULL,
                password_hash VARCHAR(64) NOT NULL,
                recovery_word VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audio_recordings (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                audio_base64 TEXT NOT NULL,
                text_id VARCHAR(50) NOT NULL,
                original_text TEXT NOT NULL,
                duration_seconds REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_reports (
                id SERIAL PRIMARY KEY,
                recording_id INTEGER REFERENCES audio_recordings(id),
                user_id INTEGER REFERENCES users(id),
                report_markdown TEXT NOT NULL,
                error_summary TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS speed_reading_results (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                grade INTEGER NOT NULL,
                wpm REAL NOT NULL,
                comprehension_pct REAL NOT NULL,
                effective_speed REAL NOT NULL,
                duration_seconds REAL NOT NULL,
                correct_answers INTEGER NOT NULL,
                total_questions INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    else:
        # SQLite
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                grade INTEGER NOT NULL CHECK (grade BETWEEN 1 AND 8),
                gender TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                recovery_word TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now', 'localtime'))
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audio_recordings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER REFERENCES users(id),
                audio_base64 TEXT NOT NULL,
                text_id TEXT NOT NULL,
                original_text TEXT NOT NULL,
                duration_seconds REAL,
                created_at TEXT DEFAULT (datetime('now', 'localtime'))
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recording_id INTEGER REFERENCES audio_recordings(id),
                user_id INTEGER REFERENCES users(id),
                report_markdown TEXT NOT NULL,
                error_summary TEXT,
                created_at TEXT DEFAULT (datetime('now', 'localtime'))
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS speed_reading_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER REFERENCES users(id),
                grade INTEGER NOT NULL,
                wpm REAL NOT NULL,
                comprehension_pct REAL NOT NULL,
                effective_speed REAL NOT NULL,
                duration_seconds REAL NOT NULL,
                correct_answers INTEGER NOT NULL,
                total_questions INTEGER NOT NULL,
                created_at TEXT DEFAULT (datetime('now', 'localtime'))
            )
        """)
    
    conn.commit()
    conn.close()


# ─── Şifre Hash ──────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    """SHA-256 ile şifre hash'ler."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


# ─── Kullanıcı İşlemleri ─────────────────────────────────────────────────────

def register_user(name, age, grade, gender, email, password, recovery_word):
    """Yeni kullanıcı kaydı oluşturur."""
    conn, db_type = get_connection()
    cursor = conn.cursor()
    try:
        pw_hash = hash_password(password)
        if db_type == "postgresql":
            cursor.execute(
                "INSERT INTO users (name, age, grade, gender, email, password_hash, recovery_word) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (name, age, grade, gender, email.lower().strip(), pw_hash, recovery_word.lower().strip())
            )
        else:
            cursor.execute(
                "INSERT INTO users (name, age, grade, gender, email, password_hash, recovery_word) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (name, age, grade, gender, email.lower().strip(), pw_hash, recovery_word.lower().strip())
            )
        conn.commit()
        return True, "Kayıt başarılı!"
    except Exception as e:
        conn.rollback()
        if "UNIQUE" in str(e).upper() or "unique" in str(e).lower():
            return False, "Bu e-posta adresi zaten kayıtlı."
        return False, f"Kayıt hatası: {e}"
    finally:
        conn.close()


def login_user(email, password):
    """Kullanıcı girişi doğrular."""
    conn, db_type = get_connection()
    cursor = conn.cursor()
    pw_hash = hash_password(password)
    
    if db_type == "postgresql":
        cursor.execute("SELECT * FROM users WHERE email = %s AND password_hash = %s", (email.lower().strip(), pw_hash))
    else:
        cursor.execute("SELECT * FROM users WHERE email = ? AND password_hash = ?", (email.lower().strip(), pw_hash))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        if db_type == "postgresql":
            cols = [desc[0] for desc in cursor.description]
            return dict(zip(cols, row))
        else:
            return dict(row)
    return None


def reset_password(email, recovery_word, new_password):
    """Kurtarma kelimesi ile şifre sıfırlar."""
    conn, db_type = get_connection()
    cursor = conn.cursor()
    
    if db_type == "postgresql":
        cursor.execute("SELECT id FROM users WHERE email = %s AND recovery_word = %s", (email.lower().strip(), recovery_word.lower().strip()))
    else:
        cursor.execute("SELECT id FROM users WHERE email = ? AND recovery_word = ?", (email.lower().strip(), recovery_word.lower().strip()))
    
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False, "E-posta veya kurtarma kelimesi hatalı."
    
    new_hash = hash_password(new_password)
    if db_type == "postgresql":
        cursor.execute("UPDATE users SET password_hash = %s WHERE email = %s", (new_hash, email.lower().strip()))
    else:
        cursor.execute("UPDATE users SET password_hash = ? WHERE email = ?", (new_hash, email.lower().strip()))
    
    conn.commit()
    conn.close()
    return True, "Şifre başarıyla güncellendi."


def get_all_students():
    """Tüm öğrenci listesini döndürür."""
    conn, db_type = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, age, grade, gender, email, created_at FROM users ORDER BY grade, name")
    rows = cursor.fetchall()
    conn.close()
    
    if db_type == "postgresql":
        cols = [desc[0] for desc in cursor.description]
        return [dict(zip(cols, row)) for row in rows]
    else:
        return [dict(row) for row in rows]


def get_user_by_id(user_id):
    """ID ile kullanıcı bilgisi döndürür."""
    conn, db_type = get_connection()
    cursor = conn.cursor()
    
    if db_type == "postgresql":
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    else:
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        if db_type == "postgresql":
            cols = [desc[0] for desc in cursor.description]
            return dict(zip(cols, row))
        return dict(row)
    return None


# ─── Ses Kaydı İşlemleri ─────────────────────────────────────────────────────

def save_audio_recording(user_id, audio_base64, text_id, original_text, duration_seconds=None):
    """Ses kaydını veritabanına kaydeder."""
    conn, db_type = get_connection()
    cursor = conn.cursor()
    try:
        if db_type == "postgresql":
            cursor.execute(
                "INSERT INTO audio_recordings (user_id, audio_base64, text_id, original_text, duration_seconds) VALUES (%s, %s, %s, %s, %s)",
                (user_id, audio_base64, text_id, original_text, duration_seconds)
            )
        else:
            cursor.execute(
                "INSERT INTO audio_recordings (user_id, audio_base64, text_id, original_text, duration_seconds) VALUES (?, ?, ?, ?, ?)",
                (user_id, audio_base64, text_id, original_text, duration_seconds)
            )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Ses kayıt hatası: {e}")
        return False
    finally:
        conn.close()


def get_recordings_by_user(user_id):
    """Bir öğrencinin ses kayıtlarını döndürür."""
    conn, db_type = get_connection()
    cursor = conn.cursor()
    
    if db_type == "postgresql":
        cursor.execute(
            "SELECT id, text_id, original_text, duration_seconds, created_at FROM audio_recordings WHERE user_id = %s ORDER BY created_at DESC",
            (user_id,)
        )
    else:
        cursor.execute(
            "SELECT id, text_id, original_text, duration_seconds, created_at FROM audio_recordings WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        )
    
    rows = cursor.fetchall()
    conn.close()
    
    if db_type == "postgresql":
        cols = [desc[0] for desc in cursor.description]
        return [dict(zip(cols, row)) for row in rows]
    return [dict(row) for row in rows]


def get_recording_by_id(recording_id):
    """Ses kaydını ID ile döndürür (base64 dahil)."""
    conn, db_type = get_connection()
    cursor = conn.cursor()
    
    if db_type == "postgresql":
        cursor.execute("SELECT * FROM audio_recordings WHERE id = %s", (recording_id,))
    else:
        cursor.execute("SELECT * FROM audio_recordings WHERE id = ?", (recording_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        if db_type == "postgresql":
            cols = [desc[0] for desc in cursor.description]
            return dict(zip(cols, row))
        return dict(row)
    return None


# ─── Analiz Raporu İşlemleri ──────────────────────────────────────────────────

def save_analysis_report(recording_id, user_id, report_markdown, error_summary=None):
    """Analiz raporunu veritabanına kaydeder."""
    conn, db_type = get_connection()
    cursor = conn.cursor()
    try:
        if db_type == "postgresql":
            cursor.execute(
                "INSERT INTO analysis_reports (recording_id, user_id, report_markdown, error_summary) VALUES (%s, %s, %s, %s)",
                (recording_id, user_id, report_markdown, error_summary)
            )
        else:
            cursor.execute(
                "INSERT INTO analysis_reports (recording_id, user_id, report_markdown, error_summary) VALUES (?, ?, ?, ?)",
                (recording_id, user_id, report_markdown, error_summary)
            )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Rapor kayıt hatası: {e}")
        return False
    finally:
        conn.close()


def get_reports_by_user(user_id):
    """Bir öğrencinin analiz raporlarını döndürür."""
    conn, db_type = get_connection()
    cursor = conn.cursor()
    
    if db_type == "postgresql":
        cursor.execute(
            "SELECT ar.id, ar.recording_id, ar.report_markdown, ar.error_summary, ar.created_at FROM analysis_reports ar WHERE ar.user_id = %s ORDER BY ar.created_at DESC",
            (user_id,)
        )
    else:
        cursor.execute(
            "SELECT ar.id, ar.recording_id, ar.report_markdown, ar.error_summary, ar.created_at FROM analysis_reports ar WHERE ar.user_id = ? ORDER BY ar.created_at DESC",
            (user_id,)
        )
    
    rows = cursor.fetchall()
    conn.close()
    
    if db_type == "postgresql":
        cols = [desc[0] for desc in cursor.description]
        return [dict(zip(cols, row)) for row in rows]
    return [dict(row) for row in rows]


def get_report_by_recording(recording_id):
    """Bir ses kaydına ait raporu döndürür."""
    conn, db_type = get_connection()
    cursor = conn.cursor()
    
    if db_type == "postgresql":
        cursor.execute("SELECT * FROM analysis_reports WHERE recording_id = %s ORDER BY created_at DESC LIMIT 1", (recording_id,))
    else:
        cursor.execute("SELECT * FROM analysis_reports WHERE recording_id = ? ORDER BY created_at DESC LIMIT 1", (recording_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        if db_type == "postgresql":
            cols = [desc[0] for desc in cursor.description]
            return dict(zip(cols, row))
        return dict(row)
    return None


# ─── Hızlı Okuma Sonuçları ───────────────────────────────────────────────────

def save_speed_reading_result(user_id, grade, wpm, comprehension_pct, effective_speed, duration_seconds, correct_answers, total_questions):
    """Hızlı okuma test sonucunu kaydeder."""
    conn, db_type = get_connection()
    cursor = conn.cursor()
    try:
        if db_type == "postgresql":
            cursor.execute(
                "INSERT INTO speed_reading_results (user_id, grade, wpm, comprehension_pct, effective_speed, duration_seconds, correct_answers, total_questions) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (user_id, grade, wpm, comprehension_pct, effective_speed, duration_seconds, correct_answers, total_questions)
            )
        else:
            cursor.execute(
                "INSERT INTO speed_reading_results (user_id, grade, wpm, comprehension_pct, effective_speed, duration_seconds, correct_answers, total_questions) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (user_id, grade, wpm, comprehension_pct, effective_speed, duration_seconds, correct_answers, total_questions)
            )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Hızlı okuma kayıt hatası: {e}")
        return False
    finally:
        conn.close()


def get_speed_reading_results(user_id):
    """Öğrencinin hızlı okuma sonuçlarını döndürür."""
    conn, db_type = get_connection()
    cursor = conn.cursor()
    
    if db_type == "postgresql":
        cursor.execute(
            "SELECT * FROM speed_reading_results WHERE user_id = %s ORDER BY created_at DESC",
            (user_id,)
        )
    else:
        cursor.execute(
            "SELECT * FROM speed_reading_results WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        )
    
    rows = cursor.fetchall()
    conn.close()
    
    if db_type == "postgresql":
        cols = [desc[0] for desc in cursor.description]
        return [dict(zip(cols, row)) for row in rows]
    return [dict(row) for row in rows]
