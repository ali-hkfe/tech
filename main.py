from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import sys
import json

import hashlib
import uuid
import os
os.system("python create_admin.py")
from pydantic import BaseModel
from typing import Optional
from fastapi import Request 
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from security import verify_password, get_password_hash, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta
from data_sources.osint_news import fetch_real_news
import re
# 1. الاستيراد الصحيح: نخبر السيرفر أن يدخل لمجلد ai ويجلب دالة call_ai_engine
from ai.ai_client import call_ai_engine
from datetime import datetime
# --- مكتبات قاعدة البيانات ---
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from database_models import Base, User, Role, SystemSetting, AuditLog, ArchiveDB, Country, Source, ModelWeights
import uuid
from typing import Any, Dict, List
import google.generativeai as genai
from typing import Literal

# استيراد الراوتر الجديد للذكاء الاصطناعي
from ai.report_api import router as report_router

# --- استيراد المحركات بأمان ---
try: from intelligence.deep_state_engine import DeepStateCoreEngine
except ImportError: DeepStateCoreEngine = None
# 🌟 تحديد اسم ملف قاعدة البيانات السيادية
ARCHIVE_FILE = "equilens_archive.json"

# تهيئة الملف فور تشغيل السيرفر إذا لم يكن موجوداً
if not os.path.exists(ARCHIVE_FILE):
    with open(ARCHIVE_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)

# هيكل البيانات القادمة للحفظ
class ArchiveSaveRequest(BaseModel):
    country: str
    type: str
    score: float
    data: dict
# إعداد المسارات
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, "data_sources"))
sys.path.append(os.path.join(current_dir, "intelligence"))

# ==========================================
# 💾 إعداد قاعدة البيانات 
# ==========================================
SQLALCHEMY_DATABASE_URL = "sqlite:///./equilens_v2.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

# ==========================================
# 🚀 بدء التطبيق
# ==========================================
app = FastAPI(title="EQUILENS Control Hub", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://www.equilens-core.com",
        "https://equilens-core.com",
        "http://localhost:3000",
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# تسجيل راوتر الذكاء الاصطناعي السيادي
app.include_router(report_router)
class ArchivePayload(BaseModel):
    country: str
    type: str
    score: Any  # استخدمنا Any لأن الواجهة قد ترسل الرقم كنص أو رقم
    data: Dict[str, Any]
# 1. خريطة استلام بيانات السيناريوهات

class ScenarioPayload(BaseModel):
    api_key: str
    model: str = "gemini-2.5-flash"
    focal_issue: Optional[str] = ""
    methodology: Optional[dict] = {}
    driving_forces: Optional[list] = []
    scenarios: Optional[list] = []
    tested_strategy: Optional[str] = ""
    prompt_instruction: Optional[str] = None  # 🌟 هذا هو السلك المفقود الذي تسبب في المشكلة!
    module: Optional[str] = None

# --- عقود البيانات (Models) ---
class MathAnalysis(BaseModel):
    risk_score: float = Field(default=0.0)
    bayesian_prob: float = 50.0
    ai_adjustment: float = 0.0

class SimulationWargameRequest(BaseModel):
    country: str
    timeframe: int
    risk_level: float
    shocks: dict
    metrics: dict
    api_key: str
    model: str = "gemini-1.5-flash-latest"

class StrategicReportSchema(BaseModel):
    country_iso3: str = "UNK"
    year: int = 2026
    ai_narrative: str = ""
    math_analysis: MathAnalysis = Field(default_factory=MathAnalysis)
    svolik: Dict[str, Any] = Field(default_factory=dict)
    resource_curse: Dict[str, Any] = Field(default_factory=dict)
    fsi: Dict[str, Any] = Field(default_factory=dict)
    dimensions: Dict[str, float] = Field(default_factory=dict)
    swot: Dict[str, List[str]] = Field(default_factory=dict)
    recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    deep_state: Optional[Dict[str, Any]] = None
    early_warnings: List[Dict[str, str]] = Field(default_factory=list)
    wgi: Dict[str, float] = Field(default_factory=dict)
    cinc: Dict[str, Any] = Field(default_factory=dict)
    overall: Dict[str, float] = Field(default_factory=dict)
    civil_war: Dict[str, Any] = Field(default_factory=dict)

class SimulationRequest(BaseModel):
    country_iso: str
    shocks: Dict[str, float]

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "Analyst"

class AcademicReportRequest(BaseModel):
    title: str = Field(..., max_length=150)
    author_name: str
    country_iso3: str
    report_type: str 
    data_snapshot: Dict[str, Any] 
# 1. خريطة استلام بيانات تقرير نظرية المباريات
class GameTheoryPayload(BaseModel):
    game_name: str
    description: str
    strategy_notes: Optional[str] = ""
    players: list
    strategies: dict
    payoff_matrix: dict
    analysis: dict
    api_key: str
    model: str = "gemini-1.5-flash-latest" # 🌟 التعديل هنا
    prompt_instruction: Optional[str] = ""

    # 2. خريطة استلام بيانات المولد السحري
class AutoMatrixRequest(BaseModel):
    conflict_description: str
    api_key: str
    model: str = "gemini-1.5-flash-latest"

# 3. خريطة استلام بيانات الجولة التالية (آلة الزمن)
class NextTurnRequest(BaseModel):
    current_game: dict
    ai_report: str
    api_key: str
    model: str = "gemini-1.5-flash-latest"
# ==========================================
# 📊 منطق التحليل الأساسي
# ==========================================
def ai_calculate_live_impact(iso):
    live_news = []
    try: live_news = fetch_real_news(iso)
    except: pass
    risk_mod = 0
    keywords = {"risk_up": ["مظاهرات", "قتلى", "أزمة", "انهيار", "انقلاب"], "risk_down": ["اتفاق", "نمو", "إصلاح"]}
    for news in live_news:
        title = news.get('title', '')
        if any(k in title for k in keywords["risk_up"]): risk_mod += 5
        if any(k in title for k in keywords["risk_down"]): risk_mod -= 3
    return max(-20, min(40, risk_mod))

def calculate_historical_correction(iso: str, db: Session):
    last_event = db.query(ArchiveDB).filter(ArchiveDB.country == iso).order_by(ArchiveDB.created_at.desc()).first()
    correction = 0.0
    if last_event:
        if "انقلاب" in last_event.title or "Coup" in last_event.title: correction = 0.15 
        elif "تطهير" in last_event.title or "Purge" in last_event.title: correction = 0.10
        elif "إصلاح" in last_event.title or "Reform" in last_event.title: correction = -0.05 
    return correction

# ==========================================
# 🧠 المحرك الاستراتيجي الشامل (الرياضي فقط)
# ==========================================
@app.post("/analyze/full_report", response_model=StrategicReportSchema)
async def analyze_full_report(payload: Dict[str, Any], db: Session = Depends(get_db)):
    iso = payload.get('country_iso3', 'UNK')
    ai_risk = ai_calculate_live_impact(iso)
    base_fragility = float(payload.get('fragility_index', 0.5) or 0.5)
    
    final_risk = max(10, min(95, (base_fragility * 100) + ai_risk))
    stability = 100 - final_risk
    dictator_power = (0.6 * 100) + ai_risk

    full_report = {
        "country_iso3": iso, "year": 2026,
        "ai_narrative": "", # تم تفريغه لكي يملأه الذكاء الاصطناعي لاحقاً
        "math_analysis": {"risk_score": final_risk, "bayesian_prob": stability, "ai_adjustment": ai_risk},
        "svolik": {"dictator_power": dictator_power/100, "elite_power": (100-dictator_power)/100, "survival_prob": stability},
        "resource_curse": {"oil_dependency": 80, "status": "دولة ريعية"},
        "fsi": {"total_score": final_risk},
        "dimensions": {"political": 50, "security": 50, "economic": 50, "social": 50},
        "wgi": {"rule_of_law": 0.3},
        "cinc": {"hard_power_score": 0.7},
        "overall": {"stability_score": stability},
        "civil_war": {"probability": final_risk / 1.5},
        "swot": {}, "recommendations": [],
        "early_warnings": []
    }

    current_press_score = payload.get('press_freedom_index', 50)
    if current_press_score < 40:
        full_report["early_warnings"].append({
            "level": "CRITICAL",
            "message": "⚠️ انحراف حاد: رصد انكماش في الحريات بنسبة 20%، مؤشر على تمهيد لتطهيرات سياسية."
        })

    security_growth = payload.get('security_budget_change', 0)
    if security_growth > 10:
        full_report["early_warnings"].append({
            "level": "WARNING",
            "message": "⚠️ تضخم مريب: زيادة ميزانية الأمن بنسبة 10%، احتمالية تعزيز الدولة العميقة."
        })

    if DeepStateCoreEngine:
        try:
            h_correction = calculate_historical_correction(iso, db)
            shadow_val = (final_risk / 100) * 0.8 + (h_correction)
            full_report["deep_state"] = {
                "dsi_score": round((final_risk + (h_correction * 100)), 1),
                "classification": "دولة عميقة مسيطرة" if final_risk > 70 else "دولة هجينة",
                "trend": "rising" if h_correction > 0 else "stable",
                "shadow_index": round(shadow_val * 100, 1),
                "breakdown": {
                    "institutional": 0.85, "economic": 0.78, "legal": 0.65,
                    "shadow": shadow_val, "historical": 0.70 + h_correction
                }
            }
        except Exception as e:
            print(f"DSO Engine Error: {e}")

    if full_report.get("deep_state") and full_report["deep_state"]["shadow_index"] > 80:
        full_report["early_warnings"].append({
            "level": "URGENT",
            "message": "⚠️ تحذير DSO: رصد تضخم في شبكات الظل غير الرسمية، احتمالية حدوث ارتداد سياسي (Pushback)."
        })
        
    return full_report

# ==========================================
# 🎮 محرك المحاكاة والأخبار والأرشفة
# ==========================================
@app.post("/simulate/shock")
def run_simulation(payload: SimulationRequest):
    sh = payload.shocks
    base = 50.0
    impact = (sh.get("oil_price_change", 0) * -0.5) + (sh.get("elite_loyalty_change", 0) * -0.8) + (sh.get("public_dissent_change", 0) * 0.6)
    new_risk = max(0, min(100, base + impact))
    narrative = "✅ التغيرات طفيفة"
    if impact > 10: narrative = "⚠️ الصدمة قد تؤدي لتصدع جبهة النظام الداخلية."
    return {"old_risk": base, "new_risk": new_risk, "impact_score": impact, "narrative": narrative}

# 2. المسار الجديد الذي يستخدم الخريطة
# ==========================================
# 🗄️ محرك الأرشيف السيادي (خزانة البيانات)
# ==========================================



@app.get("/countries")
def get_countries(db: Session = Depends(get_db)):
    countries = db.query(Country).all()
    if not countries: return [{"iso": "IRQ", "ar": "العراق (قاعدة البيانات فارغة)"}]
    return [{"iso": c.iso_code, "ar": c.name_ar} for c in countries]

@app.get("/api/osint/news/{country_iso}")
def get_live_news(country_iso: str):
    try:
        news = fetch_real_news(country_iso)
        if not news:
            return [
                {"source": "Intelligence System", "title": f"جاري رصد التحركات الميدانية في {country_iso}..."},
                {"source": "DSO Monitor", "title": "تنبيه: لا توجد مؤشرات احتجاجية نشطة في الساعات الـ 24 الأخيرة."}
            ]
        return news
    except Exception as e:
        return [{"source": "Error", "title": "عطل في الاتصال بمحرك OSINT"}]

@app.get("/api/osint/archive_search/{country_iso}")
def search_archive_news(country_iso: str, date: str = None, db: Session = Depends(get_db)):
    historical_reports = db.query(ArchiveDB).filter(ArchiveDB.country == country_iso, ArchiveDB.date == date).all()
    results = [{"source": "INTERNAL ARCHIVE", "title": f"تقرير مؤرشف: {r.title} - تصنيف: {r.classification}"} for r in historical_reports]
    if not results: results.append({"source": "HISTORY_ENGINE", "title": f"رصد الأنماط الاستراتيجية ليوم {date} في {country_iso}..."})
    return results

# ==========================================
# 🛡️ إدارة المستخدمين والرقابة
# ==========================================
@app.post("/auth/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="خطأ في الدخول")
    token = create_access_token(data={"sub": user.username, "role": user.role.name if user.role else "User"})
    return {"access_token": token, "token_type": "bearer", "role": user.role.name if user.role else "User"}

@app.get("/api/admin/users")
def get_users(db: Session = Depends(get_db)):
    return [{"id": u.id, "username": u.username, "role": u.role.name if u.role else "N/A"} for u in db.query(User).all()]

@app.post("/api/admin/users/create")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    role_db = db.query(Role).filter(Role.name == user.role).first() or db.query(Role).filter(Role.name == "Analyst").first()
    new_user = User(username=user.username, hashed_password=get_password_hash(user.password), role_id=role_db.id, is_active=True)
    db.add(new_user); db.commit()
    return {"status": "success"}

@app.get("/api/admin/audit-logs")
def get_logs(db: Session = Depends(get_db)):
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(50).all()
    return [{"action": l.action, "target": l.target, "timestamp": str(l.timestamp)} for l in logs]

# ==========================================
# ✍️ محرك صياغة التقارير الأكاديمية (PDF)
# ==========================================
AXES_CATALOG = [
    {"id": "military", "name_ar": "المؤسسة العسكرية", "default_keywords": ["جيش", "عسكر", "انقلاب", "ضباط", "سلاح"]},
    {"id": "security", "name_ar": "الأجهزة الأمنية", "default_keywords": ["مخابرات", "أمن", "قمع", "اعتقال", "تجسس"]},
    {"id": "economic_elite", "name_ar": "النخب الاقتصادية", "default_keywords": ["رجال أعمال", "احتجاز", "خصخصة", "احتكار", "عقود"]},
    {"id": "ideology_media", "name_ar": "الأيديولوجيا والإعلام", "default_keywords": ["فتوى", "منبر", "تعبئة", "إعلام", "تضليل"]},
    {"id": "bureaucracy", "name_ar": "الشبكات البيروقراطية", "default_keywords": ["قضاء", "إدارة", "لوائح", "تعيينات", "محسوبية"]},
    {"id": "external", "name_ar": "التأثير الخارجي", "default_keywords": ["سفارة", "معونة", "قرض", "ضغوط دولية", "اتفاقية"]}
]

def score_and_match(indicator_text: str, indicator_category: str):
    matches = []
    text_clean = indicator_text.strip().lower()
    words = text_clean.split()
    for axis in AXES_CATALOG:
        overlap = len(set(words) & set(axis["default_keywords"]))
        kw_score = (overlap / max(len(words), 1)) * 0.6
        cat_match = 0.3 if indicator_category == axis["id"] else 0
        boost = 0.1 if any(k in text_clean for k in axis["default_keywords"]) else 0
        total_score = kw_score + cat_match + boost
        if total_score >= 0.55: matches.append({"axis_id": axis["id"], "score": total_score})
    return sorted(matches, key=lambda x: x["score"], reverse=True)[:2]

def parse_title(title: str):
    years = re.findall(r'(\d{4})', title)
    time_range = f"الفترة {years[0]}" if years else "المرحلة الراهنة"
    study_type = "تقرير استراتيجي"
    if "موقف" in title: study_type = "تقدير موقف"
    elif "تحليل" in title: study_type = "تحليل سياساتي"
    elif "بحث" in title or "دراسة" in title: study_type = "دراسة أكاديمية"
    return {"time_range": time_range, "study_type": study_type, "is_academic": any(x in title for x in ["دراسة", "بحث", "دكتوراه"])}

@app.post("/api/archive/central_vault")
async def archive_to_central_vault(report_id: str, html_content: str, db: Session = Depends(get_db)):
    try:
        archive_entry = ArchiveDB(id=report_id, content=html_content, archived_at=datetime.datetime.now(), status="PERMANENT_RECORD")
        db.add(archive_entry)
        audit_log = AuditLog(action="REPORT_ARCHIVED", target_id=report_id, details=f"تم نقل التقرير {report_id} إلى الأرشيف المركزي بنجاح.")
        db.add(audit_log)
        db.commit()
        return {"status": "success", "message": "تمت الأرشفة بنجاح في المستودع المركزي."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"فشلت عملية الأرشفة: {str(e)}")




# 3. المسار لمعالجة المناورات الاستراتيجية
@app.post("/api/generate/simulation_scenario")
def generate_simulation_scenario(req: SimulationWargameRequest):
    try:
        print(f"--> بدء توليد المناورة لدولة: {req.country} باستخدام {req.model}")
        
        prompt = f"""
أنت مستشار أمن قومي وخبير في هندسة النظم السيادية (Sovereign Systems Engineering).
طُلب منك كتابة "سيناريو أزمة واقعي (Wargame Scenario)" لما سيحدث في ({req.country}) بعد ({req.timeframe}) أشهر من الآن، بناءً على هذه المعطيات الرقمية:

1. الصدمات النشطة: {req.shocks}
2. مؤشر الخطر الشامل: {req.risk_level}%
3. مؤشرات أداء النواة (Telemetry):
- ميزانية الظل: {req.metrics.get('loyaltyFund')}%
- تآكل ولاء النخبة: {req.metrics.get('vetoChurn')}%
- التدخل الخارجي: {req.metrics.get('externalApi')}%
- تآكل الردع الأمني: {req.metrics.get('securityLatency')}%

المطلوب: تقرير استخباراتي (3 فقرات كحد أقصى) يصف الشارع، تحركات القادة، وانشقاقات الأمن، ورد فعل السفارات. استخدم لغة استخباراتية مرعبة ودقيقة بدون ذكر الأرقام نصاً.
"""
        # تجهيز الإعدادات لتتناسب مع دالتك القوية
        ai_settings = {
            "api_key": req.api_key,
            "model_name": req.model,
            "ai_provider": "gemini"
        }

        # 👈 هنا التعديل الأهم: نستخدم call_ai_engine بدلاً من الكلمة القديمة
        response_text = call_ai_engine(settings=ai_settings, prompt=prompt)
        
        print("--> تم توليد السيناريو بنجاح!")
        return {"status": "success", "scenario": response_text}
    
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Error in Simulation AI: {error_msg}")
        return {"status": "error", "scenario": f"⚠️ تعذر الاتصال بمحرك الذكاء الاصطناعي. السبب التقني: {error_msg}"}


@app.post("/api/generate/academic_report")
async def generate_academic_report(payload: AcademicReportRequest, db: Session = Depends(get_db)):
    iso = payload.country_iso3
    data = payload.data_snapshot
    context = parse_title(payload.title)
    
    # 1. استخراج الأرقام من الهيكل الرياضي الجديد (المرسل من React)
    math_outputs = data.get("math_outputs", {})
    heatmap_rows = math_outputs.get("heatmap", {}).get("rows", [])
    inputs_data = data.get("inputs", {})

    # 🛡️ الدالة المساعدة (تم إضافة الدرع الواقي هنا or 0)
    def get_score(layer_id):
        for row in heatmap_rows:
            if row.get("id") == layer_id:
                return (row.get("score01") or 0) * 100
        return 0

    cinc_score = get_score("hard_power")
    shadow_idx = get_score("regime")
    elite_split = get_score("governance") / 10 
    legitimacy = get_score("fragility") / 10
    
    # المدخلات الخام (إن وجدت)
    mil_exp = inputs_data.get("military_expenditure", 0)
    steel = inputs_data.get("steel_production", 0)
    youth_bulge = inputs_data.get("youth_bulge", 0.30)
    unemployment = inputs_data.get("unemployment", 0.25)

    # 2. تفعيل محرك الربط الحتمي 
    raw_indicators = data.get("raw_indicators", [])
    axis_mappings = {}
    for ind in raw_indicators:
        matches = score_and_match(ind.get("text", ""), ind.get("category", ""))
        for m in matches:
            aid = m["axis_id"]
            if aid not in axis_mappings: axis_mappings[aid] = []
            axis_mappings[aid].append(ind)

    # 3. صياغة الفصول
    chapters = []
    prestige = "قوة متوازنة" if cinc_score > 40 else "نمر من ورق"
    
    chapters.append(f"""
    <section style="margin-bottom: 40px; border-right: 5px solid #0f172a; padding-right: 15px;">
        <h3 style="color: #0f172a;">أولاً: موازين القوى (CINC) وهشاشة البنية الاجتماعية</h3>
        <p style="text-align: justify; line-height: 1.8;">
        يُصنف الكيان ({iso}) استراتيجياً كـ <strong>'{prestige}'</strong>؛ حيث تعكس نسبة الإنفاق العسكري ({mil_exp}) وإنتاج الصلب ({steel}) فجوة في القدرة السيادية الصلبة. 
        والأخطر أكاديمياً هو تقاطع هذا الضعف مع <strong>تضخم شبابي بلغت نسبته {youth_bulge*100}%</strong> و <strong>بطالة بنسبة {unemployment*100}%</strong>، 
        مما يحول الكتلة الديموغرافية من مورد قوة إلى 'فتيل انفجار' اجتماعي يهدد تماسك الدولة.
        </p>
    </section>
    """)

    chapters.append(f"""
    <section style="margin-bottom: 40px; border-right: 5px solid #d97706; padding-right: 15px;">
        <h3 style="color: #d97706;">ثانياً: ديناميكيات الظل وانقسام النخبة (FSI Analysis)</h3>
        <p style="text-align: justify; line-height: 1.8;">
        يكشف 'مؤشر الظل' ({shadow_idx}%) عن سيطرة شبكات نفوذ غير رسمية على المفاصل الحيوية. 
        إن بلوغ <strong>انقسام النخبة درجة {elite_split}/10</strong> وتآكل الشرعية ({legitimacy}) يشير إلى أن الصراع الداخلي لم يعد سياسياً فحسب، 
        بل تحول إلى صراع بنيوي على 'شرعية البقاء'، مما يرفع من احتمالية 'الارتداد المؤسسي' ضد أي محاولة إصلاح.
        </p>
    </section>
    """)

    chart_url = f"https://quickchart.io/chart?c={{type:'radar',data:{{labels:['القوة الصلبة','الظل','التماسك','الشرعية'],datasets:[{{label:'الميزان الاستراتيجي',data:[{cinc_score},{shadow_idx},{100-(elite_split*10)},{100-(legitimacy*10)}]}}]}}}}"

    final_report_id = str(uuid.uuid4())
    final_html = f"""
    <div style="font-family: 'Times New Roman', serif; padding: 60px; direction: rtl; line-height: 1.9; color: #1e293b; background: white; max-width: 1000px; margin: auto; border: 1px solid #eee;">
        <div style="text-align: center; border-bottom: 5px double #0f172a; padding-bottom: 30px; margin-bottom: 50px;">
            <p style="font-weight: bold; color: red;">TOP SECRET // NOFORN</p>
            <h1 style="font-size: 2.5rem; color: #0f172a; margin-bottom: 15px;">{payload.title}</h1>
            <p style="font-size: 1.4rem;"><strong>إعداد الباحث: {payload.author_name}</strong></p>
            <p style="font-size: 1rem; color: #64748b; margin-top: 10px;">{context['study_type']} | إصدار: {datetime.datetime.now().strftime('%Y-%m-%d')}</p>
        </div>
        
        <div class="report-content">{"".join(chapters)}</div>

        <div style="text-align: center; margin: 40px 0;">
            <img src="{chart_url}" style="max-width: 450px; border: 1px solid #eee; padding: 15px; border-radius: 12px;">
            <p style="font-size: 0.9rem; color: #64748b;">شكل (1): ميزان القوى المركب وتحليل الصدمات لـ ({iso})</p>
        </div>

        <footer style="margin-top: 80px; text-align: center; font-size: 0.85rem; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 25px;">
            <p><strong>سري للغاية - يُحظر التداول لغير ذوي الاختصاص الأكاديمي</strong></p>
            <p>معرف الوثيقة: {final_report_id} | مطابقة لمعايير AC1-AC6 | EQUILENS 2026</p>
        </footer>
    </div>
    """
    
    return {"html_content": final_html, "report_id": final_report_id, "status": "ready"}


# 1. تعريف شكل البيانات القادمة من المختبر للبجعة السوداء
class BlackSwanRequest(BaseModel):
    scenario: str
    api_key: str
    model: str = "gemini-1.5-flash-latest"

# 2. مسار محقن البجعة السوداء (الذكاء الاصطناعي العكسي)
@app.post("/api/generate/black_swan_shocks")
def generate_black_swan_shocks(req: BlackSwanRequest):
    try:
        print(f"--> تحليل سيناريو البجعة السوداء: {req.scenario}")
        
        prompt = f"""
أنت خبير أمن قومي ومهندس نظم سيادية.
قام صانع القرار بإدخال سيناريو الأزمة المفاجئة التالي (Black Swan Event):
"{req.scenario}"

المطلوب:
ترجمة هذا النص فوراً إلى قيم رياضية للصدمات العشرة التالية. 
قم بإرجاع النتيجة بصيغة JSON فقط (بدون أي نص آخر)، بحيث تكون المفاتيح هي الأسماء أدناه، والقيم هي أرقام صحيحة:
- oil_price_change (من -80 للانهيار إلى 20 للزيادة)
- elite_loyalty_change (دائما من 0 إلى -100)
- public_dissent_change (غضب شعبي من 0 إلى 100)
- constitutional_vacuum (فراغ دستوري من 0 إلى 100)
- debt_default (صدمة ديون من 0 إلى 100)
- demographic_displacement (نزوح من 0 إلى 100)
- cyber_warfare (هجوم سيبراني من 0 إلى 100)
- currency_crash (انهيار عملة من 0 إلى 100)
- armed_insurgency (تمرد مسلح من 0 إلى 100)
- sanctions (عقوبات دولية من 0 إلى 100)

لا تكتب أي مقدمات أو شروحات، فقط كائن JSON يطابق هذه المفاتيح.
"""
        ai_settings = {
            "api_key": req.api_key,
            "model_name": req.model,
            "ai_provider": "gemini"
        }

        # نستخدم دالتك القوية مع تفعيل وضع JSON لضمان دقة الأرقام
        response_text = call_ai_engine(settings=ai_settings, prompt=prompt, json_mode=True)
        
        # تنظيف النص والتأكد من أنه JSON صالح
        cleaned_text = response_text.replace('```json', '').replace('```', '').strip()
        shocks_data = json.loads(cleaned_text)
        
        print("--> تم حقن الصدمات بنجاح!")
        return {"status": "success", "shocks": shocks_data}
    
    except Exception as e:
        print(f"❌ Error in Black Swan AI: {str(e)}")
        return {"status": "error", "message": str(e)}

    # 1. تعريف شكل البيانات لطلب الفريق الأحمر
class RedTeamRequest(BaseModel):
    country: str
    risk_level: float
    metrics: dict
    api_key: str
    model: str = "gemini-1.5-flash-latest"

# 2. مسار هجوم الفريق الأحمر (Zero-Day Scan)
@app.post("/api/generate/red_team_scan")
def generate_red_team_scan(req: RedTeamRequest):
    try:
        print(f"--> بدء محاكاة هجوم الفريق الأحمر على: {req.country}")
        
        prompt = f"""
أنت الآن قائد "الفريق الأحمر" (Red Team Commander) في جهاز استخبارات معادي.
هدفك هو تدمير النظام الحاكم في ({req.country}) واستغلال أزمته الحالية.

نقاط الضعف التي رصدها الرادار (Telemetry):
- الخطر الشامل للنظام: {req.risk_level}%
- رصيد ميزانية الظل: {req.metrics.get('loyaltyFund')}%
- تآكل ولاء النخبة: {req.metrics.get('vetoChurn')}%
- التدخل الخارجي: {req.metrics.get('externalApi')}%
- تآكل الردع الأمني: {req.metrics.get('securityLatency')}%

المطلوب:
اكتب تقريراً تكتيكياً قصيراً (فقرتين فقط) موجهاً لقيادتك.
الفقرة الأولى (The Vulnerability): حدد أضعف نقطة في النظام الحالي بناءً على الأرقام أعلاه.
الفقرة الثانية (Attack Vector): خطة الهجوم - ماذا ستفعل غداً لإسقاط هذا النظام نهائياً بناءً على هذه الثغرة (مثلاً: ضخ أموال للمعارضة، اختراق البنوك، شراء قادة أمنيين).
استخدم لغة عسكرية هجومية، مباشرة، ومرعبة كأنك تدير عملية إسقاط نظام.
"""
        ai_settings = {
            "api_key": req.api_key,
            "model_name": req.model,
            "ai_provider": "gemini"
        }

        # الاتصال بالذكاء الاصطناعي
        response_text = call_ai_engine(settings=ai_settings, prompt=prompt)
        
        print("--> تم توليد خطة الهجوم بنجاح!")
        return {"status": "success", "report": response_text}
    
    except Exception as e:
        print(f"❌ Error in Red Team AI: {str(e)}")
        return {"status": "error", "message": str(e)}

    # 1. تعريف شكل بيانات الفريق الأزرق (المدافع)
class BlueTeamRequest(BaseModel):
    country: str
    red_team_attack: str
    api_key: str
    model: str = "gemini-1.5-flash-latest"

# 2. مسار غرفة الحرب: خطة الفريق الأزرق المضادة
@app.post("/api/generate/blue_team_defense")
def generate_blue_team_defense(req: BlueTeamRequest):
    try:
        print(f"--> بدء استجابة الفريق الأزرق لدولة: {req.country}")
        
        prompt = f"""
أنت قائد "الفريق الأزرق" (Blue Team Commander) في مجلس الأمن القومي لدولة ({req.country}).
لقد اعترضنا للتو خطة الهجوم التالية من استخبارات معادية (الفريق الأحمر):
"{req.red_team_attack}"

المطلوب:
اكتب خطة مضادة عاجلة (Counter-Measure) لإحباط هذا الهجوم تحديداً وحماية النظام.
استخدم لغة استراتيجية، دفاعية، صارمة كأنك توجه أوامرك للجيش والأجهزة الأمنية. (فقرتين كحد أقصى).
"""
        ai_settings = {
            "api_key": req.api_key,
            "model_name": req.model,
            "ai_provider": "gemini"
        }

        # نستخدم دالتك القوية للاتصال بجوجل
        response_text = call_ai_engine(settings=ai_settings, prompt=prompt)
        
        print("--> تم توليد خطة الدفاع بنجاح!")
        return {"status": "success", "report": response_text}
    
    except Exception as e:
        print(f"❌ Error in Blue Team AI: {str(e)}")
        return {"status": "error", "message": str(e)}
# 1. تعريف شكل بيانات محرك الـ OSINT
class OsintRequest(BaseModel):
    country: str
    api_key: str
    model: str = "gemini-1.5-flash-latest"

# 2. مسار استخبارات المصادر المفتوحة (الواقع الفعلي)
@app.post("/api/generate/osint_shocks")
def generate_osint_shocks(req: OsintRequest):
    try:
        print(f"--> بدء مسح OSINT لدولة: {req.country}")
        
        prompt = f"""
أنت الآن محلل استخبارات مفتوحة المصدر (OSINT).
المطلوب منك إجراء مسح سريع للوضع الجيوسياسي، الاقتصادي، والأمني الفعلي حالياً لدولة ({req.country}).

بناءً على معطيات الواقع، قم بتقدير قيم الصدمات العشرة التالية لهذه الدولة اليوم.
أرجع النتيجة بصيغة JSON فقط (بدون أي نص إضافي) بالهيكلية التالية:
{{
  "summary": "اكتب هنا 3 أسطر تلخص أبرز الأحداث الواقعية الحالية (اقتصاد، سياسة، أمن) التي استندت إليها في التقييم.",
  "shocks": {{
    "oil_price_change": (رقم من -80 إلى 20),
    "elite_loyalty_change": (رقم من -100 إلى 0),
    "public_dissent_change": (رقم من 0 إلى 100),
    "constitutional_vacuum": (رقم من 0 إلى 100),
    "debt_default": (رقم من 0 إلى 100),
    "demographic_displacement": (رقم من 0 إلى 100),
    "cyber_warfare": (رقم من 0 إلى 100),
    "currency_crash": (رقم من 0 إلى 100),
    "armed_insurgency": (رقم من 0 إلى 100),
    "sanctions": (رقم من 0 إلى 100)
  }}
}}
"""
        ai_settings = {
            "api_key": req.api_key,
            "model_name": req.model,
            "ai_provider": "gemini"
        }

        # الاتصال بمحرك الذكاء الاصطناعي مع تفعيل وضع JSON
        response_text = call_ai_engine(settings=ai_settings, prompt=prompt, json_mode=True)
        
        # تنظيف وتحويل النص إلى بيانات
        cleaned_text = response_text.replace('```json', '').replace('```', '').strip()
        osint_data = json.loads(cleaned_text)
        
        print("--> تم سحب بيانات الواقع بنجاح!")
        return {"status": "success", "data": osint_data}
    
    except Exception as e:
        print(f"❌ Error in OSINT Engine: {str(e)}")
        return {"status": "error", "message": str(e)}
# 1. تعريف بيانات مجلس الأمن القومي
class WarCabinetRequest(BaseModel):
    country: str
    risk_level: float
    shocks: dict
    api_key: str
    model: str = "gemini-1.5-flash-latest"

# 2. مسار غرفة الأزمات المغلقة (Multi-Agent Debate)
@app.post("/api/generate/war_cabinet_debate")
def generate_war_cabinet_debate(req: WarCabinetRequest):
    try:
        print(f"--> بدء اجتماع مجلس الأمن القومي لدولة: {req.country}")
        
        prompt = f"""
أنت الآن تدير محاكاة لغرفة عمليات (مجلس الأمن القومي) لدولة ({req.country}).
مؤشر الخطر الحالي هو {req.risk_level}%.
الصدمات الحالية التي تضرب الدولة هي:
{req.shocks}

المطلوب:
توليد نقاش حي (Debate) وتجادل بين 3 شخصيات حول كيفية إنقاذ الدولة:
1. وزير الدفاع (يركز على الحسم الأمني والقوة العسكرية، لغته حازمة).
2. وزير الاقتصاد (مرعوب من الانهيار المالي، ويهتم بالبنوك والأسواق، يعارض الحلول الأمنية المكلفة).
3. وزير الخارجية (قلق من العقوبات والتدخل الخارجي، ويبحث عن تسويات دولية).

أرجع النتيجة بصيغة JSON فقط، كقائمة من الرسائل (بدون أي نص آخر)، بهذا الشكل تماماً:
{{
  "debate": [
    {{"role": "defense", "name": "وزير الدفاع", "text": "رسالة الوزير..."}},
    {{"role": "economy", "name": "وزير الاقتصاد", "text": "رسالة الوزير..."}},
    {{"role": "foreign", "name": "وزير الخارجية", "text": "رسالة الوزير..."}},
    {{"role": "defense", "name": "وزير الدفاع", "text": "رد الوزير على زملائه..."}}
  ]
}}
اجعل النقاش درامياً، واقعياً، ويعكس تضارب المصالح بين الوزراء في وقت الأزمات. (رسالتين لكل وزير على الأقل).
"""
        ai_settings = {
            "api_key": req.api_key,
            "model_name": req.model,
            "ai_provider": "gemini"
        }

        # الاتصال بمحرك الذكاء الاصطناعي مع تفعيل وضع JSON
        response_text = call_ai_engine(settings=ai_settings, prompt=prompt, json_mode=True)
        
        cleaned_text = response_text.replace('```json', '').replace('```', '').strip()
        debate_data = json.loads(cleaned_text)
        
        print("--> تم توليد نقاش الوزراء بنجاح!")
        return {"status": "success", "data": debate_data}
    
    except Exception as e:
        print(f"❌ Error in War Cabinet AI: {str(e)}")
        return {"status": "error", "message": str(e)}

    # 1. تعريف بيانات محرك العوالم المتعددة
class MultiverseRequest(BaseModel):
    country: str
    risk_level: float
    timeframe: int
    shocks: dict
    api_key: str
    model: str = "gemini-1.5-flash-latest"

# 2. مسار خوارزمية العوالم المتعددة
@app.post("/api/generate/multiverse")
def generate_multiverse(req: MultiverseRequest):
    try:
        print(f"--> بدء استشراف المسارات الزمنية لدولة: {req.country}")
        
        prompt = f"""
أنت حاسوب استشراف جيوسياسي كمّي (Quantum Trajectory Predictor).
معطيات الدولة الهدف ({req.country}) حالياً:
- مؤشر الخطر الحالي: {req.risk_level}%
- الإطار الزمني المستشرف: بعد {req.timeframe} أشهر
- الصدمات الفعالة: {req.shocks}

المطلوب:
توليد 3 مسارات مستقبلية محتملة (عوالم متعددة) بناءً على المعطيات أعلاه.
أرجع النتيجة بصيغة JSON فقط (بدون أي نصوص إضافية أو شروحات) بالشكل التالي:
{{
  "best_case": {{"title": "عنوان مسار النجاة", "risk": (رقم خطر أقل من الحالي), "desc": "وصف دقيق لكيفية انفراج الأزمة واستقرار النظام"}},
  "most_likely": {{"title": "المسار الحتمي", "risk": (رقم خطر متوقع ومقارب للحالي), "desc": "وصف واقعي للوضع الاستراتيجي المتوقع استمراره"}},
  "worst_case": {{"title": "سيناريو الكارثة (الانهيار)", "risk": (رقم خطر أعلى بكثير), "desc": "وصف مرعب لانهيار الدولة والمؤسسات الأمنية والاقتصادية"}}
}}
"""
        ai_settings = {
            "api_key": req.api_key,
            "model_name": req.model,
            "ai_provider": "gemini"
        }

        # الاتصال بجوجل مع تفعيل JSON
        response_text = call_ai_engine(settings=ai_settings, prompt=prompt, json_mode=True)
        cleaned_text = response_text.replace('```json', '').replace('```', '').strip()
        data = json.loads(cleaned_text)
        
        print("--> تم توليد العوالم المتعددة بنجاح!")
        return {"status": "success", "data": data}
    
    except Exception as e:
        print(f"❌ Error in Multiverse Predictor: {str(e)}")
        return {"status": "error", "message": str(e)}
# 1. طلب رادار البؤر المشتعلة
class HotzonesRequest(BaseModel):
    api_key: str
    model: str = "gemini-1.5-flash-latest"

# 2. مسار المسح العالمي الحي
@app.post("/api/generate/live_hotzones")
def generate_live_hotzones(req: HotzonesRequest):
    try:
        print("--> بدء المسح الاستخباراتي العالمي للبؤر المشتعلة...")
        
        prompt = """
أنت نظام إنذار مبكر (Global OSINT Radar).
قم بمسح الأحداث الجيوسياسية الحالية في العالم اليوم، وحدد أخطر 4 دول تشهد أزمات حادة (حروب، انهيار اقتصادي، فراغ سياسي).

أرجع النتيجة بصيغة JSON فقط (بدون أي نصوص إضافية) بالهيكلية التالية:
{
  "hotzones": [
    {
      "iso": "كود الدولة المكون من 3 أحرف مثل SYR أو YEM",
      "name": "اسم الدولة بالعربية",
      "risk": "كلمتين لوصف الخطر (مثل: انهيار مالي، حرب أهلية)",
      "desc": "جملة قصيرة تشرح الأزمة الحالية",
      "color": "اختر لونا سداسيا: #dc2626 للأحمر (خطر أقصى)، #f59e0b للبرتقالي، أو #991b1b للأحمر الداكن"
    }
  ]
}
يجب أن تحتوي القائمة على 4 دول بالضبط.
"""
        ai_settings = {
            "api_key": req.api_key,
            "model_name": req.model,
            "ai_provider": "gemini"
        }

        response_text = call_ai_engine(settings=ai_settings, prompt=prompt, json_mode=True)
        cleaned_text = response_text.replace('```json', '').replace('```', '').strip()
        data = json.loads(cleaned_text)
        
        print("--> تم تحديث رادار البؤر المشتعلة بنجاح!")
        return {"status": "success", "data": data["hotzones"]}
    
    except Exception as e:
        print(f"❌ Error in Live Hotzones: {str(e)}")
        return {"status": "error", "message": str(e)}

# 1. طلب استخراج التاريخ
class HistoricalEventsRequest(BaseModel):
    country: str
    api_key: str
    model: str = "gemini-1.5-flash-latest"

# 2. مسار آلة الزمن (Time-Machine AI)
@app.post("/api/generate/historical_events")
def generate_historical_events(req: HistoricalEventsRequest):
    try:
        print(f"--> ⏳ بدء استخراج السجل التاريخي لدولة: {req.country}")
        
        prompt = f"""
أنت مؤرخ استراتيجي وخبير في الأزمات الجيوسياسية.
مهمتك: استخرج أخطر 3 أزمات أو صدمات تاريخية حقيقية ومدمرة مرت بها دولة ({req.country}) في العصر الحديث.
ثم قم بتقدير قيم "الصدمات الاستراتيجية" التي رافقت تلك الأزمة من (-100 إلى 100).

المتغيرات المطلوب تقديرها هي:
oil_price_change, elite_loyalty_change, public_dissent_change, cyber_warfare, currency_crash, armed_insurgency, sanctions, constitutional_vacuum, debt_default, demographic_displacement

أرجع النتيجة بصيغة JSON فقط (بدون أي نصوص أخرى) وفق هذا الهيكل:
{{
  "events": [
    {{
      "id": "unique_short_id",
      "year": "سنة الأزمة (مثلا 2003 أو 1990)",
      "title": "اسم الأزمة (مثلا: الغزو، أو الانهيار المالي)",
      "desc": "وصف قصير من سطر واحد للتداعيات",
      "color": "اختر لونا سداسيا يعبر عن الأزمة (#dc2626 للأحمر، #f59e0b للبرتقالي.. الخ)",
      "shocks": {{
         "public_dissent_change": 80,
         "elite_loyalty_change": -50,
         // ... قم بإضافة بقية المتغيرات الـ 10 هنا مع قيمها المنطقية لتلك الأزمة
      }}
    }}
  ]
}}
"""
        ai_settings = {
            "api_key": req.api_key,
            "model_name": req.model,
            "ai_provider": "gemini"
        }

        response_text = call_ai_engine(settings=ai_settings, prompt=prompt, json_mode=True)
        cleaned_text = response_text.replace('```json', '').replace('```', '').strip()
        data = json.loads(cleaned_text)
        
        print("--> ✅ تم سحب البصمة التاريخية بنجاح!")
        return {"status": "success", "data": data["events"]}
    
    except Exception as e:
        print(f"❌ Error in Historical Time-Machine: {str(e)}")
        return {"status": "error", "message": str(e)}

# 1. تعريف هيكل البيانات القادمة من شات المستشار
class AdvisorChatRequest(BaseModel):
    user_query: str
    context_data: dict
    settings: dict
    # مسار الدردشة التفاعلية مع المستشار (الوعي المزدوج)
@app.post("/api/advisor/chat")
def advisor_chat(req: AdvisorChatRequest):
    try:
        print(f"--> 💬 استقبال سؤال للمستشار...")
        context_type = req.context_data.get("type", "dashboard")
        
        if context_type == "simulation":
            # 🚨 المستشار في حالة الطوارئ (مختبر المحاكاة)
            shocks = req.context_data.get("shocks", {})
            result = req.context_data.get("result", {})
            
            prompt = f"""
            أنت "مستشار الأمن القومي". القائد متواجد الآن داخل (مختبر المحاكاة الاستراتيجية).
            لقد قام القائد بحقن صدمات في المؤشرات العشرة للدولة، وهذه هي قيم الصدمات (من -100 إلى 100):
            {json.dumps(shocks, ensure_ascii=False)}
            
            ونتيجة لهذه الصدمات، ارتفع مؤشر الخطر الشامل إلى: {result.get('new_risk', 0)}%
            
            سؤال القائد: "{req.user_query}"
            
            التعليمات:
            1. أجب بطابع عسكري، صارم، وعاجل (بصفتك مدير أزمة).
            2. اربط إجابتك بالصدمات المحددة التي حقنها القائد (مثلاً إذا رفع صدمة الديون، تحدث عن الانهيار المالي).
            3. قدم توصيات سريعة للتدخل.
            """
        else:
            # 📊 المستشار في الحالة المستقرة (لوحة القيادة)
            report = req.context_data.get("report", {})
            math_data = req.context_data.get("math", {})
            
            prompt = f"""
            أنت "مستشار الأمن القومي". القائد متواجد في (لوحة القيادة).
            إليك التقرير الأكاديمي للدولة:
            {json.dumps(report, ensure_ascii=False)}
            
            سؤال القائد: "{req.user_query}"
            التعليمات: أجب باحترافية عسكرية بناءً على التقرير المرفق.
            """

        response_text = call_ai_engine(settings=req.settings, prompt=prompt, json_mode=False)
        return {"status": "success", "response": response_text}
    
    except Exception as e:
        print(f"❌ Error in Advisor Chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# 🧠 محرك تقرير القوة الوطنية (النسخة المدرعة)
# ==========================================
@app.post("/api/generate/national_power")
async def generate_national_power(payload: dict):
    try:
        api_key = payload.get("api_key")
        if not api_key:
            return {"status": "error", "message": "مفتاح API مفقود"}

        import google.generativeai as genai
        import json
        genai.configure(api_key=api_key)
        
        # 🌟 1. فلتر الأمان: تصحيح الموديل المرفوض
        raw_model_name = payload.get("model", "gemini-1.5-flash-latest")
# 🌟 التصحيح الحاسم: استخدام الجيل الثاني المتاح في مفتاحك
        safe_model_name = "gemini-3.1-flash-lite-preview" if "flash" in raw_model.lower() else "gemini-pro-latest"
        # سحب البيانات القادمة من الواجهة
        inputs = payload.get("inputs", {})
        score = payload.get("score")
        classification = payload.get("classification")

        # 🧠 هندسة الأوامر (Prompt Engineering) الصارمة
        prompt = f"""
        أنت خبير استراتيجي في العلاقات الدولية وتقييم القوة الشاملة للدول.
        بناءً على المعطيات التالية لدولة مستهدفة، قم بكتابة تقرير تحليلي سياسي احترافي.
        
        المؤشرات الحالية (من 100):
        - القوة الاقتصادية: {inputs.get('economic')}
        - القوة العسكرية: {inputs.get('military')}
        - القوة الديموغرافية: {inputs.get('demographic')}
        - القوة التكنولوجية: {inputs.get('technological')}
        - النفوذ الدولي: {inputs.get('influence')}
        
        النتيجة النهائية للقوة الوطنية: {score}/100
        التصنيف الاستراتيجي الآلي: {classification}
        
        المطلوب:
        قم بإنتاج تحليل سياسي احترافي ومقيد بالبيانات أعلاه. لا تختلق أرقاماً من عندك.
        يجب أن يكون الرد بصيغة JSON صحيحة وحصرياً، بنفس المفاتيح التالية:
        {{
            "executive_summary": "الملخص التنفيذي يوضح الدرجة العامة ومعناها (3-4 أسطر)",
            "strengths": "تحليل نقاط القوة الأساسية بناءً على أعلى المحاور (3-4 أسطر)",
            "weaknesses": "تحليل نقاط الضعف أو الاختلال الاستراتيجي بناءً على أدنى المحاور (3-4 أسطر)",
            "international_status": "تفسير الموقع الدولي وكيف تؤثر هذه البنية على مكانة الدولة (3-4 أسطر)",
            "strategic_conclusion": "خلاصة استراتيجية بلغة سياسية احترافية صارمة (3-4 أسطر)"
        }}
        """

        # 🌟 2. بروتوكول الكبح وإجبار الـ JSON النقي
        model = genai.GenerativeModel(
            model_name=safe_model_name,
            generation_config={
                "temperature": 0.2, # درجة حرارة منخفضة جداً للتحليل الجيوسياسي لكي يكون دقيقاً
                "max_output_tokens": 1500,
                "response_mime_type": "application/json" # 🌟 السلاح السري: جوجل لن تجرؤ على إرسال أي نص خارج الـ JSON!
            }
        )

        print(f"--> ⚙️ جاري تحليل القوة الوطنية (بواسطة {safe_model_name})...")
        response = model.generate_content(prompt)
        
        # 🌟 3. تحويل مباشر وآمن (لم نعد بحاجة للكود القديم المعقد الذي يبحث عن ```json)
        result_json = json.loads(response.text)

        print("--> ✅ تم توليد تقرير القوة الوطنية بنجاح!")
        return {"status": "success", "data": result_json}

    except Exception as e:
        print(f"\n❌ Error in national_power: {str(e)}\n")
        return {"status": "error", "message": str(e)}
@app.post("/api/data/fetch_osint")
async def fetch_osint_data(payload: dict):
    try:
        api_key = payload.get("api_key")
        country = payload.get("country")
        
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash-latest")

        # الـ Prompt الذي يحول المعلومات العامة إلى أرقام برمجية
        prompt = f"""
        أنت محلل بيانات استخباراتي (OSINT Specialist).
        المطلوب: تقديم تقدير رقمي دقيق من (0 إلى 100) لـ القوة الوطنية للدولة التالية: ({country}).
        بناءً على أحدث البيانات المتاحة (GDP، ميزانية الدفاع، السكان، براءات الاختراع، النفوذ الدبلوماسي).

        يجب أن يكون الرد بصيغة JSON حصرياً كما يلي:
        {{
            "economic": (رقم من 0-100),
            "military": (رقم من 0-100),
            "demographic": (رقم من 0-100),
            "technological": (رقم من 0-100),
            "influence": (رقم من 0-100)
        }}
        """

        response = model.generate_content(prompt)
        text_data = response.text
        
        # تنظيف الـ JSON
        if "```json" in text_data:
            text_data = text_data.split("```json")[1].split("```")[0].strip()
        
        osint_results = json.loads(text_data)
        return {"status": "success", "data": osint_results}

    except Exception as e:
        return {"status": "error", "message": str(e)}
   

# مسار وهمي/حقيقي للأرشيف لكي لا يظهر خطأ 404
# مسار الأرشيف مصحح ليتطابق مع واجهة React

@app.delete("/api/data/archive/delete/{doc_id}")
async def delete_from_archive(doc_id: str):
    try:
        archive_file = "archive_db.json"
        
        if not os.path.exists(archive_file):
            return {"status": "error", "message": "الأرشيف غير موجود"}
            
        with open(archive_file, "r", encoding="utf-8") as f:
            archive_data = json.load(f)
            
        # البحث عن التقرير وحذفه
        initial_length = len(archive_data)
        archive_data = [doc for doc in archive_data if doc.get("id") != doc_id]
        
        if len(archive_data) == initial_length:
            return {"status": "error", "message": "لم يتم العثور على الوثيقة"}
            
        # حفظ الملف بعد التعديل
        with open(archive_file, "w", encoding="utf-8") as f:
            json.dump(archive_data, f, ensure_ascii=False, indent=4)
            
        return {"status": "success", "message": "تم حذف الوثيقة بنجاح"}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}
# 2. مسار توليد السيناريوهات بالذكاء الاصطناعي
@app.post("/api/generate/scenarios")
async def generate_scenarios(payload: ScenarioPayload):
    try:
        if not payload.api_key:
            return {"status": "error", "message": "API Key is missing"}

        genai.configure(api_key=payload.api_key)
        
        generation_config = {
            "temperature": 0.7,
            "response_mime_type": "application/json",
        }
        
        model = genai.GenerativeModel(
            model_name=payload.model,
            generation_config=generation_config
        )

        # 🌟 السحر هنا: إذا أرسلت واجهة React أمراً مخصصاً (prompt_instruction)، نستخدمه فوراً!
        if payload.prompt_instruction:
            final_prompt = payload.prompt_instruction
            
        # 🌟 وإذا لم ترسل أمر مخصص، نستخدم الكود القديم الخاص بـ "تخطيط السيناريوهات الأربعة"
        else:
            strategy_text = f"\nالاستراتيجية الحالية المراد اختبارها: {payload.tested_strategy}\nالمطلوب تقييم دقيق لمدى صمود ونجاح هذه الاستراتيجية داخل هذا السيناريو المعين." if payload.tested_strategy else ""

            final_prompt = f"""
            أنت خبير استراتيجي ومحلل سياسي دولي. 
            القضية المحورية التي ندرسها هي: "{payload.focal_issue}"
            
            لقد قمنا ببناء 4 سيناريوهات مستقبلية بناءً على تقاطع القوى المحركة. 
            بيانات السيناريوهات هي:
            {payload.scenarios}
            
            المطلوب:
            اكتب تحليلاً استراتيجياً لكل سيناريو. يجب أن ترد بملف JSON يحتوي على مصفوفة (Array) فيها 4 كائنات (Objects)، واحد لكل سيناريو.
            كل كائن يجب أن يحتوي بالضبط على المفاتيح التالية:
            - "id": (نفس معرف السيناريو مثل S1, S2...)
            - "title": (عنوان جذاب وأكاديمي للسيناريو)
            - "summary": (ملخص تنفيذي من سطرين)
            - "narrative": (رواية تحليلية تشرح كيف سيحدث هذا السيناريو وما هي نتائجه السياسية والأمنية)
            - "key_actors": (أهم الفاعلين المستفيدين أو المتضررين)
            - "early_warnings": (3 مؤشرات إنذار مبكر تدل على أننا نتجه لهذا السيناريو)
            - "strategy_stress_test": (تقييم لمدى نجاح أو فشل الاستراتيجية المختبرة في هذا السيناريو. إذا لم يرسل المستخدم استراتيجية، اكتب: 'لم يتم إدراج استراتيجية لاختبارها')
            {strategy_text}
            """

        # إرسال الأمر للذكاء الاصطناعي
        response = model.generate_content(final_prompt)
        result_data = json.loads(response.text)

        return {"status": "success", "data": result_data}

    except Exception as e:
        print(f"Error in AI generation: {str(e)}")
        return {"status": "error", "message": str(e)}   
# ==========================================
    # ==========================================
# ⏱️ محرك الألعاب المتسلسلة (توليد الجولة الثانية Next Turn)
# ==========================================
# 🧠 محرك تطور الصراع (الجولة التالية - النسخة المدرعة بالكنز المجاني)
# ==========================================
@app.post("/api/generate/next_turn")
async def generate_next_turn(request: Request):
    try:
        payload = await request.json()
        api_key = payload.get("api_key", "")
        if not api_key:
            return {"status": "error", "message": "API Key is missing"}
            
        import google.generativeai as genai
        import json
        import re
        genai.configure(api_key=api_key)
        
        # 🌟 القوة القاهرة: تثبيت محرك الكنز المجاني لضمان العمل بدون مشاكل الحصص
        model = genai.GenerativeModel(
            model_name="gemini-3.1-flash-lite-preview", 
            generation_config={
                "temperature": 0.4, # حرارة متوسطة لضمان تطور منطقي للصراع
                "max_output_tokens": 1500,     
                "response_mime_type": "application/json"  # 🌟 إجبار الموديل على إرسال JSON نقي فقط
            }
        )
        
        current_game = payload.get("current_game", {})
        ai_report = payload.get("ai_report", "")
        
        prompt = f"""
        أنت خبير استراتيجي في نظرية المباريات (Game Theory).
        هذه هي اللعبة الحالية: {json.dumps(current_game, ensure_ascii=False)}
        وهذا هو التحليل السياسي الذي تم إنتاجه في الجولة الأولى: {ai_report}
        
        المطلوب: بناء "الجولة الثانية" (Next Turn) من هذا الصراع بناءً على المخرجات السابقة.
        كيف سيتغير سلوك الأطراف بعد هذه النتيجة؟
        
        أرجع النتيجة بصيغة JSON نقي فقط بنفس الهيكل التالي تماماً:
        {{
            "templateKey": "custom_ai_game",
            "game_name": "اسم الصراع (الجولة الثانية)",
            "description": "وصف كيف تطور الصراع وما هي المعطيات الجديدة",
            "strategy_notes": "ملاحظات حول التغيير الاستراتيجي للأطراف",
            "players": ["الطرف أ", "الطرف ب"],
            "strategies": {{"A": ["خيار جديد 1", "خيار جديد 2"], "B": ["خيار جديد 1", "خيار جديد 2"]}},
            "payoff_matrix": {{"خيار جديد 1_خيار جديد 1": [1, -1], "خيار جديد 1_خيار جديد 2": [2, -2], "خيار جديد 2_خيار جديد 1": [-1, 1], "خيار جديد 2_خيار جديد 2": [0, 0]}}
        }}
        """
        
        print(f"--> ⚙️ جاري توليد الجولة الثانية للصراع (بواسطة الكنز المجاني)...")
        response = model.generate_content(prompt)
        
        # تنظيف وتحويل آمن
        cleaned_text = re.sub(r'```json|```', '', response.text).strip()
        new_game_data = json.loads(cleaned_text)
        
        print("--> ✅ تم توليد الجولة التالية بنجاح!")
        return {"status": "success", "data": new_game_data}
        
    except Exception as e:
        print(f"\n❌ Error in Next Turn AI: {str(e)}\n")
        return {"status": "error", "message": str(e)}
    # ==========================================
# 🧠 محرك تقرير نظرية المباريات (النسخة المدرعة ضد الهلوسة والتوقف)
# ==========================================
# 🧠 محرك تقرير نظرية المباريات (النسخة المدرعة بالكنز المجاني)
# ==========================================
@app.post("/api/generate/game_theory")
async def analyze_game_theory(request: Request):
    try:
        payload = await request.json()
        api_key = payload.get("api_key", "")
        if not api_key: 
            return {"status": "error", "message": "API Key is missing"}
            
        import google.generativeai as genai
        import re
        genai.configure(api_key=api_key)
        
        # 🌟 القوة القاهرة: تثبيت محرك الكنز المجاني (500 طلب) مباشرة لتجنب أي أخطاء في المتغيرات
        model = genai.GenerativeModel(
            model_name="gemini-3.1-flash-lite-preview", 
            generation_config={
                "temperature": 0.7,
                "max_output_tokens": 1500,       
                "stop_sequences": ["[النهاية]"]  
            }
        )
        
        game_name = payload.get("game_name", "لعبة غير محددة")
        players = payload.get("players", ["الطرف الأول", "الطرف الثاني"])
        description = payload.get("description", "")
        strategy_notes = payload.get("strategy_notes", "")
        analysis = payload.get("analysis", {})
        prompt_instruction = payload.get("prompt_instruction", "")

        # استخراج البيانات بأمان
        classification_data = analysis.get('classification', {})
        conflict_type = classification_data.get('type', '') if isinstance(classification_data, dict) else ''
        nash_eq = analysis.get('nash', [])
        social_opt = analysis.get('social', {})

        # تجهيز السياق
        context_data = f"""
        معلومات الصراع (Game Theory):
        - اسم النموذج: {game_name}
        - الأطراف: {players[0]} ضد {players[1]}
        - وصف الحالة: {description}
        - الملاحظات الاستراتيجية: {strategy_notes}
        
        النتائج الرياضية:
        - تصنيف الصراع: {conflict_type}
        - توازن ناش: {nash_eq}
        - التوازن الاجتماعي: {social_opt}
        """

        # توجيه صارم في الـ Prompt للإغلاق
        final_prompt = f"""
        {context_data}
        التعليمات الصارمة: {prompt_instruction}
        IMPORTANT RULES:
        1. Write ONLY in valid HTML formatting (Use <p>, <b>, <ul>, <li>, <h4>).
        2. DO NOT use markdown code blocks. 3. Do not invent numbers.
        4. CRITICAL: When you finish the report, type exactly [النهاية] on a new line and stop generating.
        """
        
        print(f"--> ⚙️ جاري توليد التأويل السياسي لـ: {game_name} (بواسطة الكنز: gemini-3.1-flash-lite-preview)...")
        response = model.generate_content(final_prompt)
        
        # تنظيف النص النهائي من كلمة [النهاية] وأي علامات Markdown
        clean_html = re.sub(r'```html|```|\[النهاية\]', '', response.text).strip()
        
        print("--> ✅ تم توليد التأويل بنجاح وانقطع الاتصال بأمان!")
        return {"status": "success", "data": clean_html}

    except Exception as e:
        print(f"\n❌ Error in Game Theory AI: {str(e)}\n")
        return {"status": "error", "message": str(e)}
 
# ==========================================
# 🪄 محرك المولد السحري للصراعات (Auto-Matrix) - النسخة الموحدة
# ==========================================
@app.post("/api/generate/auto_matrix")
async def generate_auto_matrix(req: AutoMatrixRequest):
    try:
        import google.generativeai as genai
        import json
        import re
        
        if not req.api_key:
            return {"status": "error", "message": "API Key is missing"}
            
        # إعداد الاتصال بمحرك جيميناي
        genai.configure(api_key=req.api_key)
        
        # 🌟 السلاح السري: استخدام المحرك المضمون الذي يعمل معنا دائماً بنجاح
        model = genai.GenerativeModel(
            model_name="gemini-3.1-flash-lite-preview", 
            generation_config={
                "temperature": 0.2,            
                "max_output_tokens": 1000,     
                "response_mime_type": "application/json"  
            }
        )
        
        prompt = f"""
        أنت مهندس استراتيجي خبير في "نظرية المباريات" (Game Theory).
        قام صانع القرار بوصف الصراع التالي: "{req.conflict_description}"
        
        المطلوب: تحويل هذا الصراع إلى "لعبة رياضية" ثنائية دقيقة. 
        أرجع النتيجة بصيغة JSON فقط، والتزم بالهيكلية التالية بدقة:
        {{
            "templateKey": "custom_ai_game",
            "game_name": "اسم أكاديمي للصراع",
            "description": "وصف استراتيجي قصير",
            "strategy_notes": "تحليل أولي للاستراتيجيات المتاحة",
            "players": ["الطرف أ", "الطرف ب"],
            "strategies": {{"A": ["خيار 1", "خيار 2"], "B": ["خيار 1", "خيار 2"]}},
            "payoff_matrix": {{"خيار 1_خيار 1": [1, -1], "خيار 1_خيار 2": [2, -2], "خيار 2_خيار 1": [-1, 1], "خيار 2_خيار 2": [0, 0]}}
        }}
        """
        
        print(f"--> ⚙️ جاري تشييد المصفوفة بواسطة محرك: gemini-3.1-flash-lite-preview...")
        response = model.generate_content(prompt)
        
        # تحويل آمن
        cleaned_text = re.sub(r'```json|```', '', response.text).strip()
        matrix_data = json.loads(cleaned_text)
        
        print("✅ Auto-Matrix Success!")
        return {"status": "success", "data": matrix_data}
        
    except Exception as e:
        print(f"❌ Error in Auto-Matrix AI: {str(e)}")
        return {"status": "error", "message": str(e)}
    # ==========================================
# 🗄️ محرك الأرشيف السيادي المركزي (النسخة الموحدة والنهائية)
# ==========================================
ARCHIVE_FILE = "equilens_archive.json"

@app.get("/api/archive/list")
@app.get("/api/data/archive/list") # دمج المسارين لضمان الاستجابة لأي طلب من الواجهة
async def get_archive_list():
    try:
        if not os.path.exists(ARCHIVE_FILE):
            with open(ARCHIVE_FILE, "w", encoding="utf-8") as f:
                json.dump([], f)
            return {"status": "success", "data": []}
            
        with open(ARCHIVE_FILE, "r", encoding="utf-8") as f:
            archive_data = json.load(f)
            
        # قلب القائمة لتظهر الأحدث أولاً
        archive_data.reverse()
        return {"status": "success", "data": archive_data}
    except Exception as e:
        print(f"❌ Archive Read Error: {str(e)}")
        return {"status": "error", "message": str(e)}

@app.post("/api/data/archive/save")
async def save_to_archive(request: Request):
    try:
        payload = await request.json()
        
        if not os.path.exists(ARCHIVE_FILE):
            with open(ARCHIVE_FILE, "w", encoding="utf-8") as f:
                json.dump([], f)
                
        with open(ARCHIVE_FILE, "r", encoding="utf-8") as f:
            archive_data = json.load(f)
            
        new_record = {
            "id": f"EQ-{str(uuid.uuid4())[:6].upper()}",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "country": payload.get("country", payload.get("game_name", "صراع استراتيجي")),
            "type": payload.get("type", "نظرية المباريات"),
            "score": payload.get("score", 0),
            "data": payload.get("data", payload)
        }
        
        archive_data.append(new_record)
        
        with open(ARCHIVE_FILE, "w", encoding="utf-8") as f:
            json.dump(archive_data, f, ensure_ascii=False, indent=4)
            
        print(f"--> 💾 تم حفظ: {new_record['country']} في الأرشيف بنجاح!")
        return {"status": "success", "message": "تم الحفظ بنجاح", "id": new_record["id"]}
        
    except Exception as e:
        print(f"❌ Error saving to archive: {str(e)}")
        return {"status": "error", "message": str(e)}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
@app.get("/init-admin")
def initialize_database():
