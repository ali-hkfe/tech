from database import SessionLocal, engine
from database_models import Base, User, Role
from security import get_password_hash

def create_first_admin():
    # هذا هو السطر السحري الذي كان ينقصنا لبناء الجداول أولاً!
    print("⏳ جاري بناء جداول قاعدة البيانات...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        print("⏳ جاري التحقق من الصلاحيات...")
        admin_role = db.query(Role).filter(Role.name == "Admin").first()
        if not admin_role:
            admin_role = Role(name="Admin", permissions={"all": True})
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)
            print("✅ تم إنشاء صلاحية Admin")

        print("⏳ جاري التحقق من حساب الإدارة...")
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if not existing_admin:
            new_admin = User(
                username="admin",
                email="admin@equilens.com",
                hashed_password=get_password_hash("admin123"),
                is_active=True,
                role_id=admin_role.id
            )
            db.add(new_admin)
            db.commit()
            print("✅ تم إنشاء حساب الإدمن بنجاح! (admin / admin123)")
        else:
            print("⚠️ الحساب موجود بالفعل.")
    except Exception as e:
        print(f"❌ حدث خطأ: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_first_admin()
