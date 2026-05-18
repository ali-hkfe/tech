from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime

# ==========================================
# 1. نماذج المصادقة والمستخدمين (Authentication)
# ==========================================
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, description="اسم المستخدم")
    email: Optional[EmailStr] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="كلمة المرور")

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class User(UserBase):
    id: int
    is_admin: bool = False
    
    class Config:
        from_attributes = True

# ==========================================
# 2. نماذج المدخلات للتحليل (Analysis Inputs)
# ==========================================
class FullAnalysisInput(BaseModel):
    country_iso3: str = Field(..., min_length=3, max_length=3, description="كود الدولة (مثال: IRQ)")
    analysis_date: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))

    # --- المؤشرات السياسية (مع التحقق من القيم) ---
    polity_score: float = Field(..., ge=-10, le=10, description="مؤشر الديمقراطية (-10 إلى 10)")
    
    # جميع النسب المئوية يجب أن تكون بين 0.0 و 1.0
    election_integrity: float = Field(..., ge=0.0, le=1.0, description="نزاهة الانتخابات (0-1)")
    civil_liberties: float = Field(..., ge=0.0, le=1.0, description="الحريات المدنية (0-1)")
    repression_capacity: float = Field(..., ge=0.0, le=1.0, description="القدرة القمعية (0-1)")
    
    # --- المتغيرات الاقتصادية والسيادية ---
    economic_diversification: float = Field(0.5, ge=0.0, le=1.0)
    resource_dependence: float = Field(0.5, ge=0.0, le=1.0, description="الاعتماد على الريع")
    fragility_index: float = Field(0.5, ge=0.0, le=1.0, description="مؤشر الهشاشة")
    
    # --- المتغيرات الأمنية ---
    coup_threat: float = Field(0.2, ge=0.0, le=1.0, description="تهديد الانقلاب")
    rev_threat: float = Field(0.2, ge=0.0, le=1.0, description="تهديد الثورة")
    
    # --- حقول إضافية للنموذج العميق (Sovereign Logic) ---
    institutional_independence: Optional[float] = Field(0.5, ge=0.0, le=1.0, description="استقلال القضاء والمؤسسات")
    state_bias: Optional[float] = Field(0.3, ge=0.0, le=1.0, description="انحياز الدولة لفئة معينة")
    
    class Config:
        json_schema_extra = {
            "example": {
                "country_iso3": "IRQ",
                "polity_score": 6.0,
                "election_integrity": 0.7,
                "civil_liberties": 0.5,
                "repression_capacity": 0.4
            }
        }

# ==========================================
# 3. نماذج المخرجات والتقارير (Outputs)
# ==========================================

# نموذج السيناريو الواحد
class Scenario(BaseModel):
    title: str
    prob: int
    type: str # positive, negative, neutral
    condition: str
    impact: str

# نموذج التقرير الكامل (مطابق لما يرسله main.py)
class FinalReportOutput(BaseModel):
    rsi_score: float
    regime_label: str
    hci_score: float
    ethical_alert: bool
    
    dimensions: Dict[str, float] # political, economic, etc.
    integrity: Dict[str, Any]
    ai_narrative: str
    
    scenarios: List[Scenario]
    recommendations: List[Dict[str, Any]]
    swot_analysis: Dict[str, List[str]]
    
    human_impact: Optional[Dict[str, Any]] = None
    math_analysis: Optional[Dict[str, Any]] = None
    
    # بيانات إضافية للرسوم البيانية
    pestel_data: Optional[Dict[str, float]] = None
    sensitivity: Optional[List[Dict[str, Any]]] = None

# ==========================================
# 4. نماذج الأرشفة والمشاريع
# ==========================================
class SaveReportInput(BaseModel):
    project_id: Optional[int] = 1
    final_title: str
    content_json: Dict[str, Any] # تخزين المدخلات والمخرجات كـ JSON

class ChapterResponse(BaseModel):
    id: int
    title: str
    date: str
    type: str

class ProjectResponse(BaseModel):
    chapters: List[ChapterResponse]

# ==========================================
# 5. نماذج المساعدة والذكاء الاصطناعي
# ==========================================
class AIReportRequest(BaseModel):
    country: str
    data: Dict[str, Any]

class TermRequest(BaseModel):
    term: str

class CompareRequest(BaseModel):
    input_a: Dict[str, Any]
    input_b: Dict[str, Any]
    label_a: str
    label_b: str

# أضف هذا النموذج في قسم نماذج المدخلات
class SystemSettings(BaseModel):
    ai_provider: str = "openai"  # openai, deepseek, local
    ai_model: str = "gpt-4"
    language: str = "ar"
    theme: str = "navy"
    
    class Config:
        from_attributes = True