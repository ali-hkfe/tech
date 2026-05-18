import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

def fetch_real_news(country_iso):
    """
    جلب الأخبار الحية مع تخطي حماية Google News
    """
    country_map = {
        "IRQ": "العراق", "SAU": "السعودية", "EGY": "مصر", 
        "TUR": "تركيا", "IRN": "إيران", "JOR": "الأردن",
        "SYR": "سوريا", "LBN": "لبنان", "KWT": "الكويت",
        "QAT": "قطر", "ARE": "الإمارات", "OMN": "عمان",
        "YEM": "اليمن", "SDN": "السودان", "LBY": "ليبيا",
        "USA": "أمريكا", "RUS": "روسيا", "CHN": "الصين"
    }
    
    query = country_map.get(country_iso, country_iso)
    encoded_query = urllib.parse.quote(f"{query} سياسة أمن اقتصاد")
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ar&gl=EG&ceid=EG:ar"
    
    try:
        # 🕵️‍♂️ حيلة التخفي: إخبار جوجل أننا متصفح Chrome حقيقي وليس روبوت
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            
            news_items = []
            # نجلب آخر 7 أخبار بدلاً من خبر واحد
            for item in root.findall('.//item')[:7]: 
                title = item.find('title').text
                link = item.find('link').text
                source_node = item.find('source')
                source = source_node.text if source_node is not None else "وكالات"
                
                news_items.append({
                    "title": title,
                    "link": link,
                    "source": source
                })
            
            if not news_items:
                return [{"title": f"لا توجد أخبار عاجلة حالياً عن {query}", "link": "#", "source": "النظام"}]
                
            return news_items

    except Exception as e:
        print(f"⚠️ OSINT Error: {e}")
        return [{
            "title": f"تعذر الاتصال بخدمة الأخبار المباشرة: {str(e)}",
            "link": "#",
            "source": "System"
        }]