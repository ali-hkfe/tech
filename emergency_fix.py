import os
import glob
import subprocess
import sys
import time

print("🚨 --- بدء عملية الإنقاذ الشاملة ---")

# 1. محاولة قتل أي سيرفر بايثون يعمل حالياً (لتحرير ملف قاعدة البيانات)
try:
    print("🛑 إيقاف السيرفرات السابقة...")
    if os.name == 'nt': # Windows
        os.system("taskkill /F /IM python.exe")
        os.system("taskkill /F /IM uvicorn.exe")
except:
    pass

time.sleep(2) # انتظار إغلاق الملفات

# 2. حذف جميع قواعد البيانات القديمة/التالفة
db_files = glob.glob("*.db")
for db in db_files:
    try:
        os.remove(db)
        print(f"🗑️ تم حذف قاعدة البيانات القديمة: {db}")
    except Exception as e:
        print(f"⚠️ فشل حذف {db}: {e}")

# 3. إعادة بناء الجداول الجديدة (القديمة والجديدة)
print("🏗️ جاري بناء قاعدة بيانات نظيفة (equilens.db)...")
try:
    from database import engine
    import models
    models.Base.metadata.create_all(bind=engine)
    print("✅ تم بناء الهيكل الجديد بنجاح!")
except Exception as e:
    print(f"❌ خطأ في البناء: {e}")

print("\n🚀 جاري تشغيل النظام...")
print("ملاحظة: سيتم فتح السيرفر الآن. لا تغلق هذه النافذة.")
subprocess.run([sys.executable, "-m", "uvicorn", "main:app", "--reload"])