from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import feedparser
import urllib.parse
from datetime import datetime

app = FastAPI()

# السماح للواجهة (React) بالاتصال بالسيرفر
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# قاموس الدول التي نراقبها
MONITORED_ZONES = {
    'IRQ': 'العراق',
    'SYR': 'سوريا',
    'SDN': 'السودان',
    'LBN': 'لبنان',
    'YEM': 'اليمن',
    'LBY': 'ليبيا',
    'EGY': 'مصر',
    'UKR': 'أوكرانيا',
    'TWN': 'تايوان'
}

# كلمات مفتاحية استخباراتية لرصد التوتر
THREAT_KEYWORDS = ['قصف', 'اشتباكات', 'انفجار', 'انهيار', 'مظاهرات', 'طوارئ', 'تحذير', 'إخلاء', 'حرب', 'أزمة', 'اغتيال', 'تصعيد']

def analyze_country_news(country_name):
    # جلب الأخبار الحية من Google News RSS باللغة العربية
    encoded_name = urllib.parse.quote(country_name)
    url = f"https://news.google.com/rss/search?q={encoded_name}&hl=ar&gl=EG&ceid=EG:ar"
    feed = feedparser.parse(url)
    
    events_count = len(feed.entries)
    tension_score = 10 # درجة توتر أساسية
    detected_signals = []
    
    # تحليل العناوين
    for entry in feed.entries[:15]: # نأخذ أحدث 15 خبر
        title = entry.title
        for keyword in THREAT_KEYWORDS:
            if keyword in title:
                tension_score += 8 # زيادة التوتر عند رصد كلمة خطيرة
                if keyword not in detected_signals:
                    detected_signals.append(keyword)
    
    # تحديد مستوى ديفكون بناءً على التوتر
    tension_score = min(100, tension_score)
    if tension_score > 80: defcon = 1
    elif tension_score > 60: defcon = 2
    elif tension_score > 40: defcon = 3
    elif tension_score > 20: defcon = 4
    else: defcon = 5
    
    # تحديد المسار (تريند)
    trend = 'up' if defcon <= 2 else ('stable' if defcon == 3 else 'down')
    
    if not detected_signals:
        detected_signals = ["هدوء أمني", "روتين سياسي"]

    return {
        "events": events_count,
        "tensionScore": tension_score,
        "signals": detected_signals[:4], # نرسل أهم 4 إشارات فقط
        "defcon": defcon,
        "trend": trend
    }

@app.get("/api/osint/live")
def get_live_osint():
    results = []
    current_time = datetime.now().strftime("%I:%M %p")
    
    for iso, name in MONITORED_ZONES.items():
        analysis = analyze_country_news(name)
        results.append({
            "iso": iso,
            "tensionScore": analysis["tensionScore"],
            "defcon": analysis["defcon"],
            "trend": analysis["trend"],
            "signals": analysis["signals"],
            "lastUpdated": current_time
        })
        
    # ترتيب من الأخطر إلى الأقل خطورة
    results.sort(key=lambda x: x["defcon"])
    return {"status": "success", "data": results}

if __name__ == "__main__":
    import uvicorn
    # تشغيل السيرفر على البورت 8000
    uvicorn.run(app, host="127.0.0.1", port=8000)