"""
Veritabanı İşlemleri — PostgreSQL (Supabase) / SQLite fallback
Kalıcı kullanıcı verileri için PostgreSQL önerilir.
SQLite yalnızca yerel geliştirme içindir (cloud platformlarda veriler kaybolur).
"""

import sqlite3
import hashlib
import os
import json
import streamlit as st
from datetime import datetime
from contextlib import contextmanager

# ─── Veritabanı Bağlantı Havuzu ─────────────────────────────────────────────

def _get_db_url():
    """Supabase DB URL'ini ortam değişkenleri veya Streamlit secrets'tan alır."""
    # Önce ortam değişkeninden dene
    db_url = os.environ.get("SUPABASE_DB_URL", "")
    if db_url:
        return db_url
    
    # Streamlit secrets'tan dene
    try:
        db_url = st.secrets.get("SUPABASE_DB_URL", "")
        if db_url:
            return db_url
    except Exception:
        pass
    
    return ""


try:
    @st.cache_resource
    def _get_pg_pool():
        """PostgreSQL bağlantı havuzu oluşturur (cache'lenir)."""
        db_url = _get_db_url()
        if not db_url:
            return None
        
        try:
            from psycopg2 import pool
            connection_pool = pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=5,
                dsn=db_url
            )
            return connection_pool
        except Exception as e:
            print(f"⚠️ PostgreSQL bağlantı havuzu oluşturulamadı: {e}")
            return None
except Exception:
    def _get_pg_pool():
        """Fallback — cache_resource yoksa."""
        db_url = _get_db_url()
        if not db_url:
            return None
        try:
            from psycopg2 import pool
            return pool.ThreadedConnectionPool(minconn=1, maxconn=5, dsn=db_url)
        except Exception:
            return None


@contextmanager
def get_connection():
    """
    Context manager: Veritabanı bağlantısı döndürür.
    Kullanım:
        with get_connection() as (conn, cursor, db_type):
            cursor.execute(...)
            conn.commit()
    """
    pg_pool = _get_pg_pool()
    
    if pg_pool:
        conn = None
        try:
            conn = pg_pool.getconn()
            conn.autocommit = False
            cursor = conn.cursor()
            yield conn, cursor, "postgresql"
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            raise e
        finally:
            if conn:
                try:
                    pg_pool.putconn(conn)
                except Exception:
                    pass
    else:
        # SQLite fallback (yalnızca yerel geliştirme)
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "okuma_analiz.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        try:
            cursor = conn.cursor()
            yield conn, cursor, "sqlite"
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()


def _rows_to_dicts(cursor, rows, db_type):
    """Sorgu sonuçlarını dict listesine çevirir."""
    if not rows:
        return []
    if db_type == "postgresql":
        cols = [desc[0] for desc in cursor.description]
        return [dict(zip(cols, row)) for row in rows]
    else:
        return [dict(row) for row in rows]


def _row_to_dict(cursor, row, db_type):
    """Tek satırı dict'e çevirir."""
    if not row:
        return None
    if db_type == "postgresql":
        cols = [desc[0] for desc in cursor.description]
        return dict(zip(cols, row))
    else:
        return dict(row)


def _param(db_type):
    """Veritabanı tipine göre parametre yer tutucusu döndürür."""
    return "%s" if db_type == "postgresql" else "?"


# ─── Tablo Oluşturma ────────────────────────────────────────────────────────

def init_db():
    """Veritabanı tablolarını oluşturur."""
    with get_connection() as (conn, cursor, db_type):
        if db_type == "postgresql":
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


# ─── Şifre Hash ──────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    """SHA-256 ile şifre hash'ler."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


# ─── Kullanıcı İşlemleri ─────────────────────────────────────────────────────

def register_user(name, age, grade, gender, email, password, recovery_word):
    """Yeni kullanıcı kaydı oluşturur."""
    try:
        with get_connection() as (conn, cursor, db_type):
            pw_hash = hash_password(password)
            p = _param(db_type)
            cursor.execute(
                f"INSERT INTO users (name, age, grade, gender, email, password_hash, recovery_word) VALUES ({p}, {p}, {p}, {p}, {p}, {p}, {p})",
                (name, int(age), int(grade), gender, email.lower().strip(), pw_hash, recovery_word.lower().strip())
            )
            conn.commit()
            return True, "Kayıt başarılı!"
    except Exception as e:
        err = str(e).upper()
        if "UNIQUE" in err or "DUPLICATE" in err:
            return False, "Bu e-posta adresi zaten kayıtlı."
        return False, f"Kayıt hatası: {e}"


def login_user(email, password):
    """Kullanıcı girişi doğrular."""
    try:
        with get_connection() as (conn, cursor, db_type):
            pw_hash = hash_password(password)
            p = _param(db_type)
            cursor.execute(
                f"SELECT * FROM users WHERE email = {p} AND password_hash = {p}",
                (email.lower().strip(), pw_hash)
            )
            row = cursor.fetchone()
            return _row_to_dict(cursor, row, db_type)
    except Exception as e:
        print(f"Giriş hatası: {e}")
        return None


def reset_password(email, recovery_word, new_password):
    """Kurtarma kelimesi ile şifre sıfırlar."""
    try:
        with get_connection() as (conn, cursor, db_type):
            p = _param(db_type)
            cursor.execute(
                f"SELECT id FROM users WHERE email = {p} AND recovery_word = {p}",
                (email.lower().strip(), recovery_word.lower().strip())
            )
            row = cursor.fetchone()
            if not row:
                return False, "E-posta veya kurtarma kelimesi hatalı."
            
            new_hash = hash_password(new_password)
            cursor.execute(
                f"UPDATE users SET password_hash = {p} WHERE email = {p}",
                (new_hash, email.lower().strip())
            )
            conn.commit()
            return True, "Şifre başarıyla güncellendi."
    except Exception as e:
        return False, f"Şifre sıfırlama hatası: {e}"


def get_user_by_id(user_id):
    """ID ile kullanıcı bilgisi döndürür."""
    try:
        with get_connection() as (conn, cursor, db_type):
            p = _param(db_type)
            cursor.execute(f"SELECT * FROM users WHERE id = {p}", (user_id,))
            row = cursor.fetchone()
            return _row_to_dict(cursor, row, db_type)
    except Exception as e:
        print(f"Kullanıcı sorgulama hatası: {e}")
        return None


def get_all_students():
    """Tüm öğrenci listesini döndürür."""
    try:
        with get_connection() as (conn, cursor, db_type):
            cursor.execute("SELECT id, name, age, grade, gender, email, created_at FROM users ORDER BY grade, name")
            rows = cursor.fetchall()
            return _rows_to_dicts(cursor, rows, db_type)
    except Exception as e:
        print(f"Öğrenci listesi hatası: {e}")
        return []


# ─── Ses Kaydı İşlemleri ─────────────────────────────────────────────────────

def save_audio_recording(user_id, audio_base64, text_id, original_text, duration_seconds=None):
    """Ses kaydını veritabanına kaydeder."""
    try:
        with get_connection() as (conn, cursor, db_type):
            p = _param(db_type)
            cursor.execute(
                f"INSERT INTO audio_recordings (user_id, audio_base64, text_id, original_text, duration_seconds) VALUES ({p}, {p}, {p}, {p}, {p})",
                (user_id, audio_base64, text_id, original_text, duration_seconds)
            )
            conn.commit()
            return True
    except Exception as e:
        print(f"Ses kayıt hatası: {e}")
        return False


def get_recordings_by_user(user_id):
    """Bir öğrencinin ses kayıtlarını döndürür."""
    try:
        with get_connection() as (conn, cursor, db_type):
            p = _param(db_type)
            cursor.execute(
                f"SELECT id, text_id, original_text, duration_seconds, created_at FROM audio_recordings WHERE user_id = {p} ORDER BY created_at DESC",
                (user_id,)
            )
            rows = cursor.fetchall()
            return _rows_to_dicts(cursor, rows, db_type)
    except Exception as e:
        print(f"Kayıt sorgulama hatası: {e}")
        return []


def get_recording_by_id(recording_id):
    """Ses kaydını ID ile döndürür (base64 dahil)."""
    try:
        with get_connection() as (conn, cursor, db_type):
            p = _param(db_type)
            cursor.execute(f"SELECT * FROM audio_recordings WHERE id = {p}", (recording_id,))
            row = cursor.fetchone()
            return _row_to_dict(cursor, row, db_type)
    except Exception as e:
        print(f"Kayıt sorgulama hatası: {e}")
        return None


def delete_recording(recording_id):
    """Ses kaydını ve ilişkili analiz raporlarını siler."""
    try:
        with get_connection() as (conn, cursor, db_type):
            p = _param(db_type)
            # Önce ilişkili analiz raporlarını sil
            cursor.execute(f"DELETE FROM analysis_reports WHERE recording_id = {p}", (recording_id,))
            # Sonra ses kaydını sil
            cursor.execute(f"DELETE FROM audio_recordings WHERE id = {p}", (recording_id,))
            conn.commit()
            return True
    except Exception as e:
        print(f"Kayıt silme hatası: {e}")
        return False


# ─── Analiz Raporu İşlemleri ──────────────────────────────────────────────────

def save_analysis_report(recording_id, user_id, report_markdown, error_summary=None):
    """Analiz raporunu veritabanına kaydeder."""
    try:
        with get_connection() as (conn, cursor, db_type):
            p = _param(db_type)
            cursor.execute(
                f"INSERT INTO analysis_reports (recording_id, user_id, report_markdown, error_summary) VALUES ({p}, {p}, {p}, {p})",
                (recording_id, user_id, report_markdown, error_summary)
            )
            conn.commit()
            return True
    except Exception as e:
        print(f"Rapor kayıt hatası: {e}")
        return False


def get_reports_by_user(user_id):
    """Bir öğrencinin analiz raporlarını döndürür."""
    try:
        with get_connection() as (conn, cursor, db_type):
            p = _param(db_type)
            cursor.execute(
                f"SELECT ar.id, ar.recording_id, ar.report_markdown, ar.error_summary, ar.created_at FROM analysis_reports ar WHERE ar.user_id = {p} ORDER BY ar.created_at DESC",
                (user_id,)
            )
            rows = cursor.fetchall()
            return _rows_to_dicts(cursor, rows, db_type)
    except Exception as e:
        print(f"Rapor sorgulama hatası: {e}")
        return []


def get_report_by_recording(recording_id):
    """Bir ses kaydına ait raporu döndürür."""
    try:
        with get_connection() as (conn, cursor, db_type):
            p = _param(db_type)
            cursor.execute(
                f"SELECT * FROM analysis_reports WHERE recording_id = {p} ORDER BY created_at DESC LIMIT 1",
                (recording_id,)
            )
            row = cursor.fetchone()
            return _row_to_dict(cursor, row, db_type)
    except Exception as e:
        print(f"Rapor sorgulama hatası: {e}")
        return None


# ─── Hızlı Okuma Sonuçları ───────────────────────────────────────────────────

def save_speed_reading_result(user_id, grade, wpm, comprehension_pct, effective_speed, duration_seconds, correct_answers, total_questions):
    """Hızlı okuma test sonucunu kaydeder."""
    try:
        with get_connection() as (conn, cursor, db_type):
            p = _param(db_type)
            cursor.execute(
                f"INSERT INTO speed_reading_results (user_id, grade, wpm, comprehension_pct, effective_speed, duration_seconds, correct_answers, total_questions) VALUES ({p}, {p}, {p}, {p}, {p}, {p}, {p}, {p})",
                (user_id, int(grade), float(wpm), float(comprehension_pct), float(effective_speed), float(duration_seconds), int(correct_answers), int(total_questions))
            )
            conn.commit()
            return True
    except Exception as e:
        print(f"Hızlı okuma kayıt hatası: {e}")
        return False


def get_speed_reading_results(user_id):
    """Öğrencinin hızlı okuma sonuçlarını döndürür."""
    try:
        with get_connection() as (conn, cursor, db_type):
            p = _param(db_type)
            cursor.execute(
                f"SELECT * FROM speed_reading_results WHERE user_id = {p} ORDER BY created_at DESC",
                (user_id,)
            )
            rows = cursor.fetchall()
            return _rows_to_dicts(cursor, rows, db_type)
    except Exception as e:
        print(f"Hızlı okuma sorgulama hatası: {e}")
        return []


# ─── Bağlantı Durum Kontrolü ────────────────────────────────────────────────

def check_db_status():
    """Veritabanı bağlantı durumunu kontrol eder. Debug amaçlı."""
    db_url = _get_db_url()
    info = {
        "db_type": "postgresql" if db_url else "sqlite (⚠️ veriler kalıcı değil!)",
        "connected": False,
        "user_count": 0
    }
    try:
        with get_connection() as (conn, cursor, db_type):
            info["db_type"] = db_type
            cursor.execute("SELECT COUNT(*) FROM users")
            count = cursor.fetchone()
            info["user_count"] = count[0] if count else 0
            info["connected"] = True
    except Exception as e:
        info["error"] = str(e)
    return info
