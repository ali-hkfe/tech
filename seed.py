import models
from database import SessionLocal, engine
from passlib.context import CryptContext

# إعداد تشفير كلمة المرور
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

# --- قائمة الدول الكاملة (بيانات مرجعية) ---
ALL_COUNTRIES = [
    {"iso": "IND", "ar": "الهند", "en": "India"},
    {"iso": "CHN", "ar": "الصين", "en": "China"},
    {"iso": "USA", "ar": "الولايات المتحدة", "en": "United States"},
    {"iso": "IDN", "ar": "إندونيسيا", "en": "Indonesia"},
    {"iso": "PAK", "ar": "باكستان", "en": "Pakistan"},
    {"iso": "NGA", "ar": "نيجيريا", "en": "Nigeria"},
    {"iso": "BRA", "ar": "البرازيل", "en": "Brazil"},
    {"iso": "BGD", "ar": "بنغلاديش", "en": "Bangladesh"},
    {"iso": "RUS", "ar": "روسيا", "en": "Russia"},
    {"iso": "ETH", "ar": "إثيوبيا", "en": "Ethiopia"},
    {"iso": "MEX", "ar": "المكسيك", "en": "Mexico"},
    {"iso": "JPN", "ar": "اليابان", "en": "Japan"},
    {"iso": "EGY", "ar": "مصر", "en": "Egypt"},
    {"iso": "PHL", "ar": "الفلبين", "en": "Philippines"},
    {"iso": "COD", "ar": "جمهورية الكونغو الديمقراطية", "en": "DR Congo"},
    {"iso": "VNM", "ar": "فيتنام", "en": "Vietnam"},
    {"iso": "IRN", "ar": "إيران", "en": "Iran"},
    {"iso": "TUR", "ar": "تركيا", "en": "Turkey"},
    {"iso": "DEU", "ar": "ألمانيا", "en": "Germany"},
    {"iso": "THA", "ar": "تايلاند", "en": "Thailand"},
    {"iso": "GBR", "ar": "المملكة المتحدة", "en": "United Kingdom"},
    {"iso": "TZA", "ar": "تنزانيا", "en": "Tanzania"},
    {"iso": "FRA", "ar": "فرنسا", "en": "France"},
    {"iso": "ZAF", "ar": "جنوب أفريقيا", "en": "South Africa"},
    {"iso": "ITA", "ar": "إيطاليا", "en": "Italy"},
    {"iso": "KEN", "ar": "كينيا", "en": "Kenya"},
    {"iso": "MMR", "ar": "ميانمار", "en": "Myanmar"},
    {"iso": "COL", "ar": "كولومبيا", "en": "Colombia"},
    {"iso": "KOR", "ar": "كوريا الجنوبية", "en": "South Korea"},
    {"iso": "UGA", "ar": "أوغندا", "en": "Uganda"},
    {"iso": "SDN", "ar": "السودان", "en": "Sudan"},
    {"iso": "ESP", "ar": "إسبانيا", "en": "Spain"},
    {"iso": "DZA", "ar": "الجزائر", "en": "Algeria"},
    {"iso": "IRQ", "ar": "العراق", "en": "Iraq"},
    {"iso": "ARG", "ar": "الأرجنتين", "en": "Argentina"},
    {"iso": "AFG", "ar": "أفغانستان", "en": "Afghanistan"},
    {"iso": "POL", "ar": "بولندا", "en": "Poland"},
    {"iso": "CAN", "ar": "كندا", "en": "Canada"},
    {"iso": "MAR", "ar": "المغرب", "en": "Morocco"},
    {"iso": "UKR", "ar": "أوكرانيا", "en": "Ukraine"},
    {"iso": "AGO", "ar": "أنغولا", "en": "Angola"},
    {"iso": "SAU", "ar": "المملكة العربية السعودية", "en": "Saudi Arabia"},
    {"iso": "UZB", "ar": "أوزبكستان", "en": "Uzbekistan"},
    {"iso": "YEM", "ar": "اليمن", "en": "Yemen"},
    {"iso": "MOZ", "ar": "موزمبيق", "en": "Mozambique"},
    {"iso": "GHA", "ar": "غانا", "en": "Ghana"},
    {"iso": "PER", "ar": "بيرو", "en": "Peru"},
    {"iso": "MYS", "ar": "ماليزيا", "en": "Malaysia"},
    {"iso": "NPL", "ar": "نيبال", "en": "Nepal"},
    {"iso": "MDG", "ar": "مدغشقر", "en": "Madagascar"},
    {"iso": "CIV", "ar": "كوت ديفوار", "en": "Ivory Coast"},
    {"iso": "VEN", "ar": "فنزويلا", "en": "Venezuela"},
    {"iso": "CMR", "ar": "الكاميرون", "en": "Cameroon"},
    {"iso": "NER", "ar": "النيجر", "en": "Niger"},
    {"iso": "AUS", "ar": "أستراليا", "en": "Australia"},
    {"iso": "PRK", "ar": "كوريا الشمالية", "en": "North Korea"},
    {"iso": "TWN", "ar": "تايوان", "en": "Taiwan"},
    {"iso": "MLI", "ar": "مالي", "en": "Mali"},
    {"iso": "BFA", "ar": "بوركينا فاسو", "en": "Burkina Faso"},
    {"iso": "SYR", "ar": "سوريا", "en": "Syria"},
    {"iso": "LKA", "ar": "سريلانكا", "en": "Sri Lanka"},
    {"iso": "MWI", "ar": "مالاوي", "en": "Malawi"},
    {"iso": "ZMB", "ar": "زامبيا", "en": "Zambia"},
    {"iso": "ROU", "ar": "رومانيا", "en": "Romania"},
    {"iso": "CHL", "ar": "تشيلي", "en": "Chile"},
    {"iso": "KAZ", "ar": "كازاخستان", "en": "Kazakhstan"},
    {"iso": "TCD", "ar": "تشاد", "en": "Chad"},
    {"iso": "ECU", "ar": "الإكوادور", "en": "Ecuador"},
    {"iso": "SOM", "ar": "الصومال", "en": "Somalia"},
    {"iso": "GTM", "ar": "غواتيمالا", "en": "Guatemala"},
    {"iso": "SEN", "ar": "السنغال", "en": "Senegal"},
    {"iso": "NLD", "ar": "هولندا", "en": "Netherlands"},
    {"iso": "KHM", "ar": "كمبوديا", "en": "Cambodia"},
    {"iso": "ZWE", "ar": "زيمبابوي", "en": "Zimbabwe"},
    {"iso": "GIN", "ar": "غينيا", "en": "Guinea"},
    {"iso": "RWA", "ar": "رواندا", "en": "Rwanda"},
    {"iso": "BEN", "ar": "بنين", "en": "Benin"},
    {"iso": "BDI", "ar": "بوروندي", "en": "Burundi"},
    {"iso": "TUN", "ar": "تونس", "en": "Tunisia"},
    {"iso": "BOL", "ar": "بوليفيا", "en": "Bolivia"},
    {"iso": "HTI", "ar": "هايتي", "en": "Haiti"},
    {"iso": "BEL", "ar": "بلجيكا", "en": "Belgium"},
    {"iso": "JOR", "ar": "الأردن", "en": "Jordan"},
    {"iso": "DOM", "ar": "جمهورية الدومينيكان", "en": "Dominican Republic"},
    {"iso": "CUB", "ar": "كوبا", "en": "Cuba"},
    {"iso": "SSD", "ar": "جنوب السودان", "en": "South Sudan"},
    {"iso": "SWE", "ar": "السويد", "en": "Sweden"},
    {"iso": "HND", "ar": "هندوراس", "en": "Honduras"},
    {"iso": "CZE", "ar": "جمهورية التشيك", "en": "Czech Republic"},
    {"iso": "AZE", "ar": "أذربيجان", "en": "Azerbaijan"},
    {"iso": "GRC", "ar": "اليونان", "en": "Greece"},
    {"iso": "PNG", "ar": "بابوا غينيا الجديدة", "en": "Papua New Guinea"},
    {"iso": "PRT", "ar": "البرتغال", "en": "Portugal"},
    {"iso": "HUN", "ar": "المجر", "en": "Hungary"},
    {"iso": "TJK", "ar": "طاجيكستان", "en": "Tajikistan"},
    {"iso": "ARE", "ar": "الإمارات العربية المتحدة", "en": "United Arab Emirates"},
    {"iso": "BLR", "ar": "بيلاروسيا", "en": "Belarus"},
    {"iso": "ISR", "ar": "إسرائيل", "en": "Israel"},
    {"iso": "TGO", "ar": "توغو", "en": "Togo"},
    {"iso": "AUT", "ar": "النمسا", "en": "Austria"},
    {"iso": "CHE", "ar": "سويسرا", "en": "Switzerland"},
    {"iso": "SLE", "ar": "سيراليون", "en": "Sierra Leone"},
    {"iso": "LAO", "ar": "لاوس", "en": "Laos"},
    {"iso": "HKG", "ar": "هونغ كونغ", "en": "Hong Kong"},
    {"iso": "SRB", "ar": "صربيا", "en": "Serbia"},
    {"iso": "NIC", "ar": "نيكاراغوا", "en": "Nicaragua"},
    {"iso": "LBY", "ar": "ليبيا", "en": "Libya"},
    {"iso": "PRY", "ar": "باراغواي", "en": "Paraguay"},
    {"iso": "KGZ", "ar": "قيرغيزستان", "en": "Kyrgyzstan"},
    {"iso": "BGR", "ar": "بلغاريا", "en": "Bulgaria"},
    {"iso": "TKM", "ar": "تركمانستان", "en": "Turkmenistan"},
    {"iso": "SLV", "ar": "السلفادور", "en": "El Salvador"},
    {"iso": "COG", "ar": "الكونغو", "en": "Republic of the Congo"},
    {"iso": "SGP", "ar": "سنغافورة", "en": "Singapore"},
    {"iso": "DNK", "ar": "الدنمارك", "en": "Denmark"},
    {"iso": "SVK", "ar": "سلوفاكيا", "en": "Slovakia"},
    {"iso": "CAF", "ar": "جمهورية أفريقيا الوسطى", "en": "Central African Republic"},
    {"iso": "FIN", "ar": "فنلندا", "en": "Finland"},
    {"iso": "LBR", "ar": "ليبيريا", "en": "Liberia"},
    {"iso": "NOR", "ar": "النرويج", "en": "Norway"},
    {"iso": "PSE", "ar": "دولة فلسطين", "en": "Palestine"},
    {"iso": "LBN", "ar": "لبنان", "en": "Lebanon"},
    {"iso": "CRI", "ar": "كوستاريكا", "en": "Costa Rica"},
    {"iso": "NZL", "ar": "نيوزيلندا", "en": "New Zealand"},
    {"iso": "IRL", "ar": "أيرلندا", "en": "Ireland"},
    {"iso": "OMN", "ar": "عُمان", "en": "Oman"},
    {"iso": "MRT", "ar": "موريتانيا", "en": "Mauritania"},
    {"iso": "PAN", "ar": "بنما", "en": "Panama"},
    {"iso": "KWT", "ar": "الكويت", "en": "Kuwait"},
    {"iso": "HRV", "ar": "كرواتيا", "en": "Croatia"},
    {"iso": "GEO", "ar": "جورجيا", "en": "Georgia"},
    {"iso": "ERI", "ar": "إريتريا", "en": "Eritrea"},
    {"iso": "URY", "ar": "أوروغواي", "en": "Uruguay"},
    {"iso": "MNG", "ar": "منغوليا", "en": "Mongolia"},
    {"iso": "BIH", "ar": "البوسنة والهرسك", "en": "Bosnia and Herzegovina"},
    {"iso": "PRI", "ar": "بورتوريكو", "en": "Puerto Rico"},
    {"iso": "ARM", "ar": "أرمينيا", "en": "Armenia"},
    {"iso": "NAM", "ar": "ناميبيا", "en": "Namibia"},
    {"iso": "LTU", "ar": "ليتوانيا", "en": "Lithuania"},
    {"iso": "JAM", "ar": "جامايكا", "en": "Jamaica"},
    {"iso": "QAT", "ar": "قطر", "en": "Qatar"},
    {"iso": "ALB", "ar": "ألبانيا", "en": "Albania"},
    {"iso": "MDA", "ar": "مولدوفا", "en": "Moldova"},
    {"iso": "GMB", "ar": "غامبيا", "en": "Gambia"},
    {"iso": "BWA", "ar": "بوتسوانا", "en": "Botswana"},
    {"iso": "GAB", "ar": "الغابون", "en": "Gabon"},
    {"iso": "LSO", "ar": "ليسوتو", "en": "Lesotho"},
    {"iso": "GNB", "ar": "غينيا بيساو", "en": "Guinea-Bissau"},
    {"iso": "SVN", "ar": "سلوفينيا", "en": "Slovenia"},
    {"iso": "GNQ", "ar": "غينيا الاستوائية", "en": "Equatorial Guinea"},
    {"iso": "LVA", "ar": "لاتفيا", "en": "Latvia"},
    {"iso": "MKD", "ar": "مقدونيا الشمالية", "en": "North Macedonia"},
    {"iso": "BHR", "ar": "البحرين", "en": "Bahrain"},
    {"iso": "TTO", "ar": "ترينيداد وتوباغو", "en": "Trinidad and Tobago"},
    {"iso": "TLS", "ar": "تيمور الشرقية", "en": "East Timor"},
    {"iso": "EST", "ar": "إستونيا", "en": "Estonia"},
    {"iso": "MUS", "ar": "موريشيوس", "en": "Mauritius"},
    {"iso": "CYP", "ar": "قبرص", "en": "Cyprus"},
    {"iso": "SWZ", "ar": "إسواتيني", "en": "Eswatini"},
    {"iso": "DJI", "ar": "جيبوتي", "en": "Djibouti"},
    {"iso": "REU", "ar": "ريونيون", "en": "Réunion"},
    {"iso": "FJI", "ar": "فيجي", "en": "Fiji"},
    {"iso": "COM", "ar": "جزر القمر", "en": "Comoros"},
    {"iso": "GUY", "ar": "غيانا", "en": "Guyana"},
    {"iso": "BTN", "ar": "بوتان", "en": "Bhutan"},
    {"iso": "SLB", "ar": "جزر سليمان", "en": "Solomon Islands"},
    {"iso": "MAC", "ar": "ماكاو", "en": "Macau"},
    {"iso": "LUX", "ar": "لوكسمبورغ", "en": "Luxembourg"},
    {"iso": "MNE", "ar": "الجبل الأسود", "en": "Montenegro"},
    {"iso": "ESH", "ar": "الصحراء الغربية", "en": "Western Sahara"},
    {"iso": "SUR", "ar": "سورينام", "en": "Suriname"},
    {"iso": "CPV", "ar": "الرأس الأخضر", "en": "Cape Verde"},
    {"iso": "MLT", "ar": "مالطا", "en": "Malta"},
    {"iso": "BLZ", "ar": "بليز", "en": "Belize"},
    {"iso": "BRN", "ar": "بروناي", "en": "Brunei"},
    {"iso": "BHS", "ar": "جزر البهاما", "en": "Bahamas"},
    {"iso": "MDV", "ar": "جزر المالديف", "en": "Maldives"},
    {"iso": "ISL", "ar": "آيسلندا", "en": "Iceland"},
    {"iso": "GLP", "ar": "غوادلوب", "en": "Guadeloupe"},
    {"iso": "MTQ", "ar": "مارتينيك", "en": "Martinique"},
    {"iso": "VUT", "ar": "فانواتو", "en": "Vanuatu"},
    {"iso": "GUF", "ar": "غويانا الفرنسية", "en": "French Guiana"},
    {"iso": "BRB", "ar": "باربادوس", "en": "Barbados"},
    {"iso": "NCL", "ar": "كاليدونيا الجديدة", "en": "New Caledonia"},
    {"iso": "PYF", "ar": "بولينيزيا الفرنسية", "en": "French Polynesia"},
    {"iso": "MYT", "ar": "مايوت", "en": "Mayotte"},
    {"iso": "STP", "ar": "ساو تومي وبرينسيب", "en": "Sao Tome and Principe"},
    {"iso": "WSM", "ar": "ساموا", "en": "Samoa"},
    {"iso": "CUW", "ar": "كوراساو", "en": "Curaçao"},
    {"iso": "LCA", "ar": "سانت لوسيا", "en": "Saint Lucia"},
    {"iso": "GUM", "ar": "غوام", "en": "Guam"},
    {"iso": "KIR", "ar": "كيريباتي", "en": "Kiribati"},
    {"iso": "FSM", "ar": "ميكرونيزيا", "en": "Micronesia"},
    {"iso": "GRD", "ar": "غرينادا", "en": "Grenada"},
    {"iso": "VCT", "ar": "سانت فنسنت وجزر غرينادين", "en": "Saint Vincent and the Grenadines"},
    {"iso": "TON", "ar": "تونغا", "en": "Tonga"},
    {"iso": "SYC", "ar": "سيشيل", "en": "Seychelles"},
    {"iso": "VIR", "ar": "جزر العذراء الأمريكية", "en": "United States Virgin Islands"},
    {"iso": "ABW", "ar": "أروبا", "en": "Aruba"},
    {"iso": "ATG", "ar": "أنتيغوا وبربودا", "en": "Antigua and Barbuda"},
    {"iso": "AND", "ar": "أندورا", "en": "Andorra"},
    {"iso": "DMA", "ar": "دومينيكا", "en": "Dominica"},
    {"iso": "IMN", "ar": "جزيرة مان", "en": "Isle of Man"},
    {"iso": "CYM", "ar": "جزر كايمان", "en": "Cayman Islands"},
    {"iso": "BMU", "ar": "برمودا", "en": "Bermuda"},
    {"iso": "GRL", "ar": "جرينلاند", "en": "Greenland"},
    {"iso": "FRO", "ar": "جزر فارو", "en": "Faroe Islands"},
    {"iso": "MNP", "ar": "جزر ماريانا الشمالية", "en": "Northern Mariana Islands"},
    {"iso": "KNA", "ar": "سانت كيتس ونيفيس", "en": "Saint Kitts and Nevis"},
    {"iso": "TCA", "ar": "جزر توركس وكايكوس", "en": "Turks and Caicos Islands"},
    {"iso": "ASM", "ar": "ساموا الأمريكية", "en": "American Samoa"},
    {"iso": "SXM", "ar": "سينت مارتن", "en": "Sint Maarten"},
    {"iso": "MHL", "ar": "جزر مارشال", "en": "Marshall Islands"},
    {"iso": "LIE", "ar": "ليختنشتاين", "en": "Liechtenstein"},
    {"iso": "MCO", "ar": "موناكو", "en": "Monaco"},
    {"iso": "SMR", "ar": "سان مارينو", "en": "San Marino"},
    {"iso": "GIB", "ar": "جبل طارق", "en": "Gibraltar"},
    {"iso": "VGB", "ar": "جزر العذراء البريطانية", "en": "British Virgin Islands"},
    {"iso": "BES", "ar": "الجزر الكاريبية الهولندية", "en": "Caribbean Netherlands"},
    {"iso": "BLM", "ar": "سان بارتيليمي", "en": "Saint Barthélemy"},
    {"iso": "PLW", "ar": "بالاو", "en": "Palau"},
    {"iso": "COK", "ar": "جزر كوك", "en": "Cook Islands"},
    {"iso": "AIA", "ar": "أنغويلا", "en": "Anguilla"},
    {"iso": "NRU", "ar": "ناورو", "en": "Nauru"},
    {"iso": "WLF", "ar": "واليس وفوتونا", "en": "Wallis and Futuna"},
    {"iso": "TUV", "ar": "توفالو", "en": "Tuvalu"},
    {"iso": "SPM", "ar": "سان بيير وميكلون", "en": "Saint Pierre and Miquelon"},
    {"iso": "SHN", "ar": "سانت هيلينا", "en": "Saint Helena"},
    {"iso": "MSR", "ar": "مونتسرات", "en": "Montserrat"},
    {"iso": "FLK", "ar": "جزر فوكلاند", "en": "Falkland Islands"},
    {"iso": "NIU", "ar": "نيوي", "en": "Niue"},
    {"iso": "TKL", "ar": "توكيلاو", "en": "Tokelau"},
    {"iso": "VAT", "ar": "الكرسي الرسولي", "en": "Vatican City"}
]




def seed_database():
    print("🚀 بدء تهيئة قاعدة البيانات...")
    
    # 1. تنظيف الجداول القديمة وإعادة إنشائها
    print("🗑️ تنظيف الجداول القديمة...")
    try:
        # حذف جميع الجداول القديمة لتجنب التعارض
        models.Base.metadata.drop_all(bind=engine)
        # إنشاء الجداول من جديد بناءً على models.py الجديد
        models.Base.metadata.create_all(bind=engine)
        print("✅ تم إعادة بناء هيكلية قاعدة البيانات.")
    except Exception as e:
        print(f"❌ خطأ في بناء الجداول: {e}")
        return

    db = SessionLocal()
    
    try:
        # 2. إنشاء المستخدم المسؤول (Admin)
        print("👤 إنشاء حساب المسؤول...")
        # التحقق من عدم وجود المستخدم
        if db.query(models.User).filter(models.User.username == "admin").first() is None:
            admin_user = models.User(
                username="admin",
                hashed_password=get_password_hash("admin123"),
                role="admin"
            )
            db.add(admin_user)
            print("✅ تم إنشاء المستخدم: admin / admin123")

        # 3. إدخال الدول
        print(f"🌍 جاري معالجة الدول...")
        for c in ALL_COUNTRIES:
            existing = db.query(models.Country).filter(models.Country.iso_code == c["iso"]).first()
            if not existing:
                country = models.Country(
                    name_ar=c["ar"],
                    name_en=c["en"],
                    iso_code=c["iso"]
                )
                db.add(country)
        
        # 4. إدخال المصادر (Sources)
        print("📚 إدخال المصادر المرجعية...")
        if db.query(models.Source).count() == 0:
            sources = [
                models.Source(title_ar="مشروع أصناف الديمقراطية", title_en="V-Dem Institute", url="v-dem.net", type="Political"),
                models.Source(title_ar="مؤشر الدول الهشة", title_en="Fragile States Index", url="fragilestatesindex.org", type="Security"),
                models.Source(title_ar="البنك الدولي - مؤشرات الحوكمة", title_en="World Bank WGI", url="worldbank.org", type="Economic"),
            ]
            db.add_all(sources)

        # 5. أوزان الذكاء الاصطناعي الأولية
        if db.query(models.ModelWeights).count() == 0:
            print("🧠 تهيئة أوزان الذكاء الاصطناعي...")
            default_weights = {"w_M": 0.18, "w_S": 0.22, "w_B": 0.16, "w_L": 0.14, "w_R": 0.15, "w_X": 0.15}
            db.add(models.ModelWeights(version=1, w_json=default_weights))

        # حفظ كل التغييرات
        db.commit()
        print("🎉 تمت عملية التهيئة (Seed) بنجاح تام!")

    except Exception as e:
        print(f"❌ حدث خطأ أثناء الإدخال: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()