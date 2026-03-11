# ============================================================
# db_utils.py — Veritabanı İşlemleri (SQLite / PostgreSQL)
# ============================================================

import json
import hashlib
from datetime import datetime
import os
import streamlit as st

try:
    import psycopg2
    DB_ENGINE = "postgresql"
except ImportError:
    DB_ENGINE = "sqlite"
    import sqlite3

SQLITE_DB_NAME = "okuma_analizi.db"
_db_initialized = False


def get_db_url():
    try:
        if "SUPABASE_DB_URL" in st.secrets:
            return st.secrets["SUPABASE_DB_URL"]
    except Exception:
        pass
    return os.getenv("SUPABASE_DB_URL")


class _PgConnWrapper:
    def __init__(self, real_conn):
        self._conn = real_conn
    def cursor(self): return self._conn.cursor()
    def commit(self): self._conn.commit()
    def rollback(self):
        try: self._conn.rollback()
        except: pass
    def close(self):
        try: self._conn.rollback()
        except: pass
    @property
    def autocommit(self): return self._conn.autocommit
    @autocommit.setter
    def autocommit(self, val): self._conn.autocommit = val


@st.cache_resource
def _get_cached_pg_conn():
    db_url = get_db_url()
    if db_url and DB_ENGINE == "postgresql":
        try:
            conn = psycopg2.connect(db_url, connect_timeout=10)
            return conn
        except Exception as e:
            print(f"PostgreSQL bağlantı hatası: {e}")
    return None


def get_connection():
    if DB_ENGINE == "postgresql":
        raw_conn = _get_cached_pg_conn()
        if raw_conn is not None:
            try:
                raw_conn.cursor().execute("SELECT 1")
                raw_conn.rollback()
                raw_conn.autocommit = False
                return _PgConnWrapper(raw_conn), "postgresql"
            except:
                _get_cached_pg_conn.clear()
                raw_conn = _get_cached_pg_conn()
                if raw_conn:
                    raw_conn.autocommit = False
                    return _PgConnWrapper(raw_conn), "postgresql"
    try:
        conn = sqlite3.connect(SQLITE_DB_NAME)
        return conn, "sqlite"
    except NameError:
        import sqlite3 as sq3
        conn = sq3.connect(SQLITE_DB_NAME)
        return conn, "sqlite"


def is_using_sqlite():
    return get_db_url() is None


def get_placeholder(engine):
    return "%s" if engine == "postgresql" else "?"


def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


# ============================================================
# VERİTABANI OLUŞTURMA
# ============================================================

def init_db():
    global _db_initialized
    if _db_initialized:
        return
    conn, engine = get_connection()
    c = conn.cursor()
    try:
        if engine == "postgresql":
            c.execute('''CREATE TABLE IF NOT EXISTS students (
                id SERIAL PRIMARY KEY, name TEXT, username TEXT UNIQUE,
                password TEXT, age INTEGER, gender TEXT, grade INTEGER,
                login_count INTEGER DEFAULT 0, secret_word TEXT
            )''')
            c.execute('''CREATE TABLE IF NOT EXISTS results (
                id SERIAL PRIMARY KEY,
                student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
                test_name TEXT, raw_answers TEXT, scores TEXT,
                report TEXT, date TIMESTAMP DEFAULT NOW()
            )''')
            c.execute('''CREATE TABLE IF NOT EXISTS analysis_history (
                id SERIAL PRIMARY KEY,
                student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
                combination TEXT, ai_report TEXT, date TIMESTAMP DEFAULT NOW()
            )''')
        else:
            c.execute('''CREATE TABLE IF NOT EXISTS students
                (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, username TEXT,
                 password TEXT, age INTEGER, gender TEXT, grade INTEGER,
                 login_count INTEGER DEFAULT 0, secret_word TEXT)''')
            c.execute('''CREATE TABLE IF NOT EXISTS results
                (id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER,
                 test_name TEXT, raw_answers TEXT, scores TEXT,
                 report TEXT, date TIMESTAMP)''')
            c.execute('''CREATE TABLE IF NOT EXISTS analysis_history
                (id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER,
                 combination TEXT, ai_report TEXT, date TIMESTAMP)''')
        conn.commit()
        _db_initialized = True
    except Exception as e:
        conn.rollback()
        print(f"init_db hatası: {e}")
    finally:
        conn.close()


# ============================================================
# ÖĞRENCİ İŞLEMLERİ
# ============================================================

class Student:
    def __init__(self, data, login_count):
        self.id = data[0]; self.name = data[1]; self.username = data[2]
        self.password = data[3]; self.age = data[4]; self.gender = data[5]
        self.grade = data[6]; self.login_count = login_count

class StudentInfo:
    def __init__(self, data):
        self.id = data[0]; self.name = data[1]; self.username = data[2]
        self.password = data[3]; self.age = data[4]; self.gender = data[5]
        self.grade = data[6]; self.login_count = data[7]


def register_student(name, username, password, age, gender, secret_word="", grade=None):
    conn, engine = get_connection()
    c = conn.cursor()
    ph = get_placeholder(engine)
    try:
        c.execute(f"SELECT id FROM students WHERE username={ph}", (username,))
        if c.fetchone():
            return False, "Bu e-posta adresi zaten kayıtlı."
        hashed_pw = hash_password(password)
        hashed_secret = hash_password(secret_word) if secret_word else ""
        c.execute(
            f"INSERT INTO students (name, username, password, age, gender, grade, secret_word) VALUES ({ph},{ph},{ph},{ph},{ph},{ph},{ph})",
            (name, username, hashed_pw, age, gender, grade, hashed_secret))
        conn.commit()
        return True, "Kayıt Başarılı"
    except Exception as e:
        conn.rollback()
        return False, f"Kayıt hatası: {e}"
    finally:
        conn.close()


def login_student(username, password):
    conn, engine = get_connection()
    c = conn.cursor()
    ph = get_placeholder(engine)
    try:
        hashed_pw = hash_password(password)
        c.execute(f"SELECT id,name,username,password,age,gender,grade,login_count FROM students WHERE username={ph} AND password={ph}", (username, hashed_pw))
        user = c.fetchone()
        if user:
            new_count = (user[7] or 0) + 1
            c.execute(f"UPDATE students SET login_count={ph} WHERE id={ph}", (new_count, user[0]))
            conn.commit()
            return True, Student(user, new_count)
        return False, None
    except Exception as e:
        conn.rollback()
        return False, None
    finally:
        conn.close()


def reset_student_password(username, secret_word, new_password):
    conn, engine = get_connection()
    c = conn.cursor()
    ph = get_placeholder(engine)
    try:
        c.execute(f"SELECT id, secret_word FROM students WHERE username={ph}", (username,))
        user_data = c.fetchone()
        if not user_data:
            return False, "E-posta bulunamadı."
        hashed_input = hash_password(secret_word.lower().strip())
        if user_data[1] != hashed_input:
            return False, "Kurtarma kelimesi yanlış!"
        c.execute(f"UPDATE students SET password={ph} WHERE id={ph}", (hash_password(new_password), user_data[0]))
        conn.commit()
        return True, "Şifre güncellendi."
    except Exception as e:
        conn.rollback()
        return False, f"Hata: {e}"
    finally:
        conn.close()


def save_test_result_to_db(student_id, test_name, raw_answers, scores, report_text):
    conn, engine = get_connection()
    c = conn.cursor()
    ph = get_placeholder(engine)
    try:
        c.execute(f"DELETE FROM results WHERE student_id={ph} AND test_name={ph}", (student_id, test_name))
        c.execute(
            f"INSERT INTO results (student_id, test_name, raw_answers, scores, report, date) VALUES ({ph},{ph},{ph},{ph},{ph},{ph})",
            (student_id, test_name, json.dumps(raw_answers, ensure_ascii=False),
             json.dumps(scores, ensure_ascii=False), report_text, datetime.now()))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Kayıt hatası: {e}")
        return False
    finally:
        conn.close()


def get_completed_tests(student_id):
    conn, engine = get_connection()
    c = conn.cursor()
    ph = get_placeholder(engine)
    try:
        c.execute(f"SELECT DISTINCT test_name FROM results WHERE student_id={ph}", (student_id,))
        return {row[0] for row in c.fetchall()}
    except:
        return set()
    finally:
        conn.close()


def get_all_students_with_results():
    conn, engine = get_connection()
    c = conn.cursor()
    ph = get_placeholder(engine)
    try:
        c.execute("SELECT id,name,username,password,age,gender,grade,login_count FROM students ORDER BY name")
        students_raw = c.fetchall()
        all_data = []
        for s in students_raw:
            c.execute(f"SELECT test_name,scores,raw_answers,date,report FROM results WHERE student_id={ph} ORDER BY date DESC", (s[0],))
            tests = []
            for t in c.fetchall():
                try: score_json = json.loads(t[1]) if t[1] else {}
                except: score_json = {}
                tests.append({"test_name": t[0], "scores": score_json, "raw_answers": t[2], "date": str(t[3]) if t[3] else "", "report": t[4]})
            all_data.append({"info": StudentInfo(s), "tests": tests})
        return all_data
    except Exception as e:
        print(f"Veri çekme hatası: {e}")
        return []
    finally:
        conn.close()


def save_holistic_analysis(student_id, combination_list, report_text):
    conn, engine = get_connection()
    c = conn.cursor()
    ph = get_placeholder(engine)
    try:
        c.execute(f"INSERT INTO analysis_history (student_id, combination, ai_report, date) VALUES ({ph},{ph},{ph},{ph})",
                  (student_id, " + ".join(combination_list), report_text, datetime.now()))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Analiz kayıt hatası: {e}")
    finally:
        conn.close()


def get_student_analysis_history(student_id):
    conn, engine = get_connection()
    c = conn.cursor()
    ph = get_placeholder(engine)
    try:
        c.execute(f"SELECT combination, ai_report, date FROM analysis_history WHERE student_id={ph} ORDER BY date DESC", (student_id,))
        return [{"combination": r[0], "report": r[1], "date": str(r[2]) if r[2] else ""} for r in c.fetchall()]
    except:
        return []
    finally:
        conn.close()


def delete_specific_students(names_list):
    conn, engine = get_connection()
    c = conn.cursor()
    ph = get_placeholder(engine)
    try:
        for name in names_list:
            c.execute(f"SELECT id FROM students WHERE name={ph}", (name,))
            sid = c.fetchone()
            if sid:
                c.execute(f"DELETE FROM analysis_history WHERE student_id={ph}", (sid[0],))
                c.execute(f"DELETE FROM results WHERE student_id={ph}", (sid[0],))
                c.execute(f"DELETE FROM students WHERE id={ph}", (sid[0],))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        return False
    finally:
        conn.close()


def reset_database():
    global _db_initialized
    conn, engine = get_connection()
    c = conn.cursor()
    try:
        if engine == "postgresql":
            c.execute("DROP TABLE IF EXISTS analysis_history CASCADE")
            c.execute("DROP TABLE IF EXISTS results CASCADE")
            c.execute("DROP TABLE IF EXISTS students CASCADE")
            conn.commit()
        else:
            conn.close()
            conn = None
            if os.path.exists(SQLITE_DB_NAME):
                os.remove(SQLITE_DB_NAME)
        _db_initialized = False
        init_db()
        return True
    except Exception as e:
        if conn:
            try: conn.rollback()
            except: pass
        return False
    finally:
        if conn:
            try: conn.close()
            except: pass


def repair_database():
    global _db_initialized
    try:
        _db_initialized = False
        init_db()
        return True
    except:
        return False
