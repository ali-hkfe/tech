@app.on_event("startup")
def initialize_admin_on_startup():
    from database import SessionLocal, engine
    from database_models import Base, User, Role
    from security import get_password_hash
    
    try:
        print("⏳ [Equilens] Starting auto-initialization...")
        # بناء الجداول
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        
        # التأكد من الصلاحية
        admin_role = db.query(Role).filter(Role.name == "Admin").first()
        if not admin_role:
            admin_role = Role(name="Admin", permissions={"all": True})
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)
        
        # التأكد من الحساب
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
            print("✅ [Equilens] Admin account created successfully! (admin / admin123)")
        else:
            print("ℹ️ [Equilens] Admin account already exists.")
        db.close()
        os
    except Exception as e:
        print(f"⚠️ [Equilens] Startup Error: {e}")
