# ✅ إضافة Float إلى قائمة الاستيراد
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

# نستخدم Base موحد لجميع النماذج
Base = declarative_base()

# ==========================================
# 1. 👥 وحدة الهوية والصلاحيات (Identity & Access)
# ==========================================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # الصلاحيات: نربط المستخدم بدور (Role)
    role_id = Column(Integer, ForeignKey("roles.id"))
    role = relationship("Role", back_populates="users")
    
    # العلاقات
    audit_logs = relationship("AuditLog", back_populates="user")
    created_at = Column(DateTime, default=datetime.utcnow)

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False) # e.g., "Admin", "Analyst"
    
    # تخزين الصلاحيات كـ JSON لمرونة قصوى
    permissions = Column(JSON, default={})
    
    users = relationship("User", back_populates="role")

# ==========================================
# 2. ⚙️ وحدة إعدادات النظام (System Configuration)
# ==========================================
class SystemSetting(Base):
    __tablename__ = "system_settings"

    key = Column(String, primary_key=True, index=True) # e.g., "AI_PROVIDER"
    value = Column(JSON, nullable=False)               # e.g., {"provider": "openai", "model": "gpt-4"}
    description = Column(String)
    is_encrypted = Column(Boolean, default=False)      # للمفاتيح الحساسة
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)

# ==========================================
# 3. 👁️ وحدة الرقابة والتدقيق (Audit & Governance)
# ==========================================
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String, index=True)      # e.g., "GENERATE_REPORT"
    target = Column(String)                  # e.g., "Country: IRQ"
    
    # التفاصيل الكاملة (Snapshot)
    details = Column(JSON)                   # e.g., {"old_value": "gpt-3.5", "new_value": "gpt-4"}
    
    ip_address = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="audit_logs")

# ==========================================
# 4. 🤖 سجلات الذكاء الاصطناعي (AI Governance)
# ==========================================
class AIRequestLog(Base):
    __tablename__ = "ai_request_logs"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String, unique=True, index=True) # ID لتتبع الطلب
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    provider = Column(String) # "openai", "anthropic"
    model = Column(String)    # "gpt-4", "claude-3"
    
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    
    # ✅ هنا كان الخطأ، الآن تم إصلاحه بعد استيراد Float
    total_cost = Column(Float, default=0.0) 
    
    status = Column(String) # "SUCCESS", "FAILED"
    error_message = Column(Text, nullable=True)
    
    timestamp = Column(DateTime, default=datetime.utcnow)

# ==========================================
# 5. 🗄️ الأرشيف (القديم المحدث)
# ==========================================
class ArchiveDB(Base):
    __tablename__ = "archives"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    country = Column(String)
    type = Column(String)
    classification = Column(String)
    author = Column(String)
    date = Column(String)
    content_html = Column(Text)
    
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    # ... (بعد الكلاسات السابقة ArchiveDB وغيرها)

# ==========================================
# 6. 🌍 الدول والمصادر (Reference Data)
# ==========================================
class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, index=True)
    name_ar = Column(String, nullable=False)
    name_en = Column(String)
    iso_code = Column(String, unique=True, index=True) # e.g. IRQ, SAU

class Source(Base):
    __tablename__ = "sources"
    id = Column(Integer, primary_key=True, index=True)
    title_ar = Column(String)
    title_en = Column(String)
    url = Column(String)
    type = Column(String) # Political, Economic

class ModelWeights(Base):
    __tablename__ = "model_weights"
    id = Column(Integer, primary_key=True, index=True)
    version = Column(Integer)
    w_json = Column(JSON)
    # ... (بعد الكلاسات السابقة)

# ==========================================
# 7. 🕵️‍♂️ مرصد الدولة العميقة (Deep State Observatory)
# بناءً على مواصفات المستند: DeepStateActors & Indicators
# ==========================================

class DeepStateActor(Base):
    __tablename__ = "deep_state_actors"
    id = Column(Integer, primary_key=True, index=True)
    country_iso = Column(String, index=True)
    name = Column(String)  # مثلاً: الحرس الثوري، المجلس العسكري، لوبي البنوك
    type = Column(String)  # Military, Intelligence, Economic, Judiciary [cite: 26]
    power_score = Column(Float) # من 0 إلى 100
    visibility_score = Column(Float) # 0 = ظل كامل، 1 = وجه معروف [cite: 28]

class DeepStateEvent(Base):
    __tablename__ = "deep_state_events"
    id = Column(Integer, primary_key=True, index=True)
    country_iso = Column(String, index=True)
    event_type = Column(String) # Coup, Purge, Constitutional_Change [cite: 32]
    year = Column(Integer)
    impact_score = Column(Float) # +1 عزز الدولة العميقة، -1 أضعفها [cite: 33]

class DeepStateIndicator(Base):
    __tablename__ = "deep_state_indicators"
    id = Column(Integer, primary_key=True, index=True)
    country_iso = Column(String, index=True)
    date = Column(String)
    # المؤشرات الكامنة (Shadow Indicators) 
    unaccounted_funds = Column(Float) # الأموال السوداء
    elite_recycling = Column(Float) # تدوير النخبة
    judicial_independence = Column(Float)
    press_freedom_inverse = Column(Float) # مقلوب حرية الصحافة