import sqlite3
import os

# اسم قاعدة البيانات (تأكد أن هذا هو الاسم الموجود في مجلدك)
db_files = ["sql_app.db", "research.db", "test.db"]

found = False
for db_name in db_files:
    if os.path.exists(db_name):
        found = True
        print(f"✅ تم العثور على قاعدة البيانات: {db_name}")
        try:
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()
            
            # حذف جدول المشاريع القديم المسبب للمشكلة
            print("⏳ جاري حذف الجدول القديم (thesis_projects)...")
            cursor.execute("DROP TABLE IF EXISTS thesis_projects")
            
            # حذف جدول الفصول والمصادر لأنها مرتبطة به
            cursor.execute("DROP TABLE IF EXISTS thesis_chapters")
            cursor.execute("DROP TABLE IF EXISTS research_sources")
            cursor.execute("DROP TABLE IF EXISTS content_blocks")
            
            conn.commit()
            conn.close()
            print("🚀 تم الحذف بنجاح! عند تشغيل السيرفر سيقوم بإنشاء الجداول الجديدة تلقائياً.")
        except Exception as e:
            print(f"❌ حدث خطأ أثناء التعديل: {e}")

if not found:
    print("⚠️ لم يتم العثور على أي ملف قاعدة بيانات (.db). هذا جيد! السيرفر سينشئ واحداً جديداً.")

input("اضغط Enter للخروج...")