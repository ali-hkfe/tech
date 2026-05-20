import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# جلب رابط قاعدة البيانات السحابية من إعدادات Railway
SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL")

# تهيئة الرابط ليتوافق مع أحدث إصدارات SQLAlchemy
if SQLALCHEMY_DATABASE_URL and SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

# إنشاء محرك الاتصال: إذا كان في السحابة سيستخدم Postgres، وإذا كان في حاسبتك سيستخدم SQLite كاحتياط
if SQLALCHEMY_DATABASE_URL:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
else:
    SQLALCHEMY_DATABASE_URL = "sqlite:///./equilens.db"
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# الدالة الأساسية لتمرير الاتصال لبقية ملفات المنصة (FastAPI)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
