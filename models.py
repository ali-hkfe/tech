from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
from datetime import datetime  # ✅ هذا هو السطر الناقص الذي سبب المشكلة


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="user")

class Country(Base):
    __tablename__ = "countries"
    id = Column(Integer, primary_key=True, index=True)
    iso_code = Column(String, unique=True, index=True)
    name_ar = Column(String)
    name_en = Column(String)

# ✅ هذا هو الجدول المفقود الذي سبب الخطأ
class Source(Base):
    __tablename__ = "sources"
    id = Column(Integer, primary_key=True, index=True)
    title_ar = Column(String)
    title_en = Column(String)
    url = Column(String)
    type = Column(String) # Political, Security, Economic

class ModelWeights(Base):
    __tablename__ = "model_weights"
    id = Column(Integer, primary_key=True, index=True)
    version = Column(Integer, unique=True, index=True)
    w_json = Column(JSON)
    metrics_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AnalysisRun(Base):
    __tablename__ = "analysis_runs"
    id = Column(Integer, primary_key=True, index=True)
    country_iso3 = Column(String, index=True)
    weights_version = Column(Integer)
    features_json = Column(JSON)
    ddsi_score = Column(Float)
    predicted_prob = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analysis_runs.id"))
    user_rating = Column(Integer)
    outcome = Column(Integer, nullable=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ThesisProject(Base):
    __tablename__ = "thesis_projects"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    researcher_name = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ThesisChapter(Base):
    __tablename__ = "thesis_chapters"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("thesis_projects.id"))
    final_title = Column(String)
    status = Column(String, default="draft")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ContentBlock(Base):
    __tablename__ = "content_blocks"
    id = Column(Integer, primary_key=True, index=True)
    chapter_id = Column(Integer, ForeignKey("thesis_chapters.id"))
    text_content = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # ✅ جدول إعدادات النظام (الخزنة الرقمية)
class SystemSettings(Base):
    __tablename__ = "system_settings"
    id = Column(Integer, primary_key=True, index=True)
    ai_provider = Column(String, default="gemini") # 'gemini' or 'openai'
    api_key = Column(String, nullable=True)        # المفتاح السري
    model_name = Column(String, default="gemini-pro") # اسم الموديل
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    version = Column(Integer)
    w_json = Column(JSON)

class ArchivedReport(Base):
    __tablename__ = "archived_reports"

    id = Column(String, primary_key=True, index=True)  # UUID
    title = Column(String)
    country = Column(String)
    type = Column(String)  # تقرير رسمي، دراسة، إلخ
    classification = Column(String)
    author = Column(String)
    content_html = Column(Text)  # محتوى التقرير
    created_at = Column(DateTime, default=datetime.utcnow)