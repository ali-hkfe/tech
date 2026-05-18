import google.generativeai as genai
import logging
import time

logger = logging.getLogger("Equilens_AI")

def call_ai_engine(settings, prompt: str, json_mode: bool = False) -> str:
    # 1) استخراج الإعدادات بأمان
    api_key = getattr(settings, "api_key", None)
    if not api_key and isinstance(settings, dict):
        api_key = settings.get("api_key")

    model_name = getattr(settings, "model_name", None)
    if not model_name and isinstance(settings, dict):
        model_name = settings.get("model_name")
    model_name = model_name or "gemini-2.0-flash"

    ai_tier = getattr(settings, "ai_tier", None)
    if not ai_tier and isinstance(settings, dict):
        ai_tier = settings.get("ai_tier")
    ai_tier = ai_tier or "free"

    ai_provider = getattr(settings, "ai_provider", None)
    if not ai_provider and isinstance(settings, dict):
        ai_provider = settings.get("ai_provider")
    ai_provider = (ai_provider or "gemini").lower()

    # حماية السيرفر: حالياً ندعم Gemini فقط
    if ai_provider != "gemini":
        raise ValueError("مزود الذكاء الاصطناعي غير مدعوم حالياً. المتاح: gemini فقط.")

    # 🛡️ استخدام مفتاح المنصة في الوضع المجاني
    if (not api_key) and ai_tier == "free":
        # ⚠️ ضع مفتاحك الحقيقي هنا (بدون مسافات)
        api_key = "AIzaSy...ضع_مفتاحك_هنا..."  

    if not api_key:
        raise ValueError("مفتاح API مفقود! الرجاء إدخاله في مركز التحكم.")

    # ✅ الإصلاح الحرج الأول: تنظيف المفتاح واستخدامه!
    clean_key = str(api_key).strip()
    if not clean_key:
        raise ValueError("مفتاح API غير صالح (فارغ بعد التنظيف).")

    genai.configure(api_key=clean_key)

    # 2) إعدادات توليد صارمة لمنع الهلوسة
    generation_config = {"temperature": 0.2}
    if json_mode:
        generation_config["response_mime_type"] = "application/json"

    model = genai.GenerativeModel(model_name=model_name, generation_config=generation_config)

    max_retries = 2 if ai_tier == "paid" else 5
    base_delay = 1 if ai_tier == "paid" else 5
    last_error = ""

    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"🚀 محاولة الاتصال ({attempt}/{max_retries}) - Model: {model_name}")
            response = model.generate_content(prompt)
            text = getattr(response, "text", "") or ""
            logger.info("✅ تم جلب الاستجابة بنجاح.")
            return text

        except Exception as e:
            last_error = str(e)
            logger.warning(f"⚠️ خطأ في المحاولة {attempt}: {last_error}")

            is_quota = ("429" in last_error) or ("Quota" in last_error) or ("RESOURCE_EXHAUSTED" in last_error)
            if is_quota:
                sleep_time = base_delay * (2 ** attempt)
                logger.info(f"⏳ انتظار {sleep_time} ثانية لتجاوز قيود المفتاح...")
                time.sleep(sleep_time)
                continue

            break

    raise RuntimeError(f"فشل الاتصال بمحرك الذكاء الاصطناعي: {last_error}")