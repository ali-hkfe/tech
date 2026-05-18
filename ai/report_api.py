from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import json
import logging
import re

try:
    from ai_client import call_ai_engine
except ImportError:
    from ai.ai_client import call_ai_engine

logger = logging.getLogger("Equilens_API")
router = APIRouter()

# ✅ الإصلاح الحرج الثالث: جعل المفتاح اختيارياً
class AISettings(BaseModel):
    api_key: Optional[str] = None
    ai_provider: str = "gemini"
    model_name: str = "gemini-2.0-flash"
    ai_tier: str = "free"

class ReportRequest(BaseModel):
    ai_payload: dict
    settings: AISettings

def build_master_prompt(payload: dict) -> str:
    context = payload.get("context", {})
    country = context.get("country", "الدولة المحددة")

    score = context.get("overall_capacity_score_100", context.get("overall_capacity_score", "0"))
    confidence = context.get("data_confidence_pct", context.get("data_confidence", "0"))
    margin = context.get("margin_of_error_pct", context.get("margin_of_error", "0"))

    drivers = "\n".join([
        f"- {d.get('layer', 'مؤشر')}: {d.get('contribution_percentage_pct', d.get('contribution_percentage', 0))}%"
        for d in payload.get("drivers", [])
    ])

    layers = "\n".join([
        f"- {l.get('layer', 'طبقة')}: {l.get('score_out_of_100', 0)}/100 (الوزن: {l.get('weight_in_model_pct', l.get('weight_in_model', 0))}%)"
        for l in payload.get("layer_scores", [])
    ])

    return f"""
أنت مستشار استراتيجي سيادي رفيع المستوى في منصة (EQUILENS).
مهمتك كتابة تقرير تحليلي معمق عن دولة [{country}].

⚠️ [أوامر سيادية صارمة]:
1) يُمنع منعاً باتاً تأليف أي أرقام من خارج هذا الموجه.
2) التزم بالأرقام حرفياً:
   - الدرجة الكلية: {score}/100
   - مستوى الثقة: {confidence}% بهامش خطأ ±{margin}%

📊 [بيانات الطبقات]:
{layers}

🚀 [محركات التأثير]:
{drivers}

🎯 [المخرج المطلوب]:
أعد JSON فقط (بدون Markdown، بدون ```، بدون نص خارجي).
الهيكل:
{{
  "ai_narrative": "<p>...</p><p>...</p><p>...</p>",
  "swot_full": {{
    "strengths": ["..."],
    "weaknesses": ["..."],
    "opportunities": ["..."],
    "threats": ["..."]
  }},
  "recommendations": [
    {{"title":"...", "bullets":["...","..."]}}
  ]
}}
"""

@router.post("/api/generate/strategic_report")
def generate_strategic_report(request: ReportRequest):
    raw_response = ""
    try:
        prompt = build_master_prompt(request.ai_payload)
        logger.info(f"إرسال طلب التحليل لدولة: {request.ai_payload.get('context', {}).get('country')}")
        
        raw_response = call_ai_engine(request.settings, prompt, json_mode=True)
        
        # ✅ الإصلاح الحرج الثاني: قراءة JSON على 3 مراحل (المحكمة)
        try:
            parsed_data = json.loads(raw_response)
        except Exception:
            fence = re.search(r"```json\s*(\{.*?\})\s*```", raw_response, re.DOTALL)
            if fence:
                parsed_data = json.loads(fence.group(1))
            else:
                match = re.search(r"\{.*?\}", raw_response, re.DOTALL)
                if not match:
                    raise ValueError("لم يتم العثور على JSON في رد الذكاء الاصطناعي.")
                parsed_data = json.loads(match.group(0))
        
        return {
            "status": "success",
            "data": parsed_data
        }

    except Exception as e:
        error_msg = str(e)
        logger.error(f"فشل الاتصال بمحرك AI، تفعيل خطة الطوارئ: {error_msg}")
        
        # 🛡️ خطة الطوارئ (التدهور الرشيق)
        fallback_data = {
            "ai_narrative": f"""
            <div style='background: #fff1f2; padding: 15px; border-radius: 8px; border: 1px solid #fecdd3; margin-bottom: 15px;'>
                <strong style='color: #e11d48;'>⚠️ وضع المحاكاة (Offline Mode):</strong> تعذر الاتصال بسيرفرات الذكاء الاصطناعي الحقيقية. 
                <br><small style='color: #9f1239;'>السبب التقني: {error_msg}</small>
            </div>
            <p><strong>(سردية افتراضية لاختبار النظام):</strong> تُظهر المؤشرات الحالية تحديات هيكلية في بنية النظام، مما يتطلب تفعيل سياسات احتواء سريعة لمنع تمدد الأزمات الأمنية والاقتصادية...</p>
            """,
            "swot_full": {
                "strengths": ["(افتراضي) تماسك نسبي في بعض المؤسسات السيادية."],
                "weaknesses": ["(افتراضي) ضعف في كفاءة الحوكمة."],
                "opportunities": ["(افتراضي) إمكانية تفعيل إصلاحات هيكلية سريعة."],
                "threats": ["(افتراضي) تصاعد احتمالات الارتداد المؤسسي."]
            },
            "recommendations": [
                {
                    "title": "توجيه استراتيجي عاجل (نموذج افتراضي)",
                    "bullets": ["تأكد من وضع مفتاح API حقيقي في إعدادات السيرفر."]
                }
            ]
        }
        
        return {
            "status": "success",
            "data": fallback_data
        }