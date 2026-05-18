from flask import Flask, request, send_file
from flask_cors import CORS  # 🚨 هذا هو السطر المفقود الذي يبحث عنه البايثون!

import pandas as pd
import matplotlib.pyplot as plt
import io
import os

# ... (باقي الكود كما هو)

# مكتبات معالجة اللغة العربية
import arabic_reshaper
from bidi.algorithm import get_display

# مكتبات ReportLab المتقدمة (للفقرات والجداول والصفحات المتعددة)
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.enums import TA_RIGHT, TA_CENTER

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}) # 🚨 فتح جميع منافذ الاتصال إجبارياً
# 1. تسجيل الخط العربي (تأكد من وجود ملف الخط في نفس المجلد)
# يمكنك تغيير Cairo-Regular.ttf إلى اسم ملف الخط الذي لديك
font_path = "Cairo-Regular.ttf" 
if os.path.exists(font_path):
    pdfmetrics.registerFont(TTFont('ArabicFont', font_path))
else:
    print("⚠️ تحذير: ملف الخط العربي غير موجود. يرجى إضافته لتجنب ظهور مربعات بدلاً من الحروف.")

# دالة سحرية لضبط اللغة العربية
def process_arabic(text):
    if not text: return ""
    reshaped_text = arabic_reshaper.reshape(str(text))
    bidi_text = get_display(reshaped_text)
    return bidi_text

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    data = request.json
    
    country = data.get('country', 'الدولة المستهدفة')
    risk_score = data.get('risk_score', 50)
    narrative = data.get('ai_narrative', 'لم يتم توفير تحليل سردي.')
    actions = data.get('actions', [])
    
    buffer = io.BytesIO()
    # تقليل الهوامش ليعطي مساحة أكبر للنص والجداول
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=40, bottomMargin=40)
    elements = []

    styles = getSampleStyleSheet()
    font_name = 'ArabicFont' if has_arabic_font else 'Helvetica'
    
    # 🌟 إضافة wordWrap='RTL' لضبط السطور العربية
    title_style = ParagraphStyle('ArabicTitle', fontName=font_name, fontSize=24, alignment=TA_CENTER, textColor=colors.HexColor("#1e3a8a"), spaceAfter=25)
    heading_style = ParagraphStyle('ArabicHeading', fontName=font_name, fontSize=18, alignment=TA_RIGHT, textColor=colors.HexColor("#b45309"), spaceAfter=15, spaceBefore=25)
    
    # ضبط تباعد الأسطر (leading) ليريح العين
    normal_style = ParagraphStyle('ArabicNormal', fontName=font_name, fontSize=14, alignment=TA_RIGHT, leading=24, spaceAfter=15, wordWrap='RTL')

    # --- الغلاف ---
    elements.append(Paragraph(process_arabic("وثيقة الإنقاذ الاستراتيجي والتدخل العاجل"), title_style))
    elements.append(Paragraph(process_arabic(f"الهدف الجيوسياسي: {country}"), ParagraphStyle('sub', fontName=font_name, fontSize=16, alignment=TA_CENTER, spaceAfter=20)))
    
    # خط فاصل ديكوري
    elements.append(Table([[""]], colWidths=[535], style=[('LINEBELOW', (0,0), (-1,-1), 2, colors.HexColor("#1e3a8a")), ('BOTTOMPADDING', (0,0), (-1,-1), 10)]))
    elements.append(Spacer(1, 20))

    elements.append(Paragraph(process_arabic(f"مؤشر الخطر الحرج: {risk_score}%"), heading_style))

    # --- التحليل السردي ---
    elements.append(Paragraph(process_arabic("التشخيص الاستراتيجي العميق:"), heading_style))
    for p in narrative.split('\n'):
        if p.strip():
            elements.append(Paragraph(process_arabic(p.strip()), normal_style))

    # --- المخطط البياني ---
    elements.append(Paragraph(process_arabic("مؤشرات السيناريوهات:"), heading_style))
    plt.figure(figsize=(6, 3)) # تكبير المخطط قليلاً
    plt.bar([process_arabic("متفائل"), process_arabic("مرجح"), process_arabic("متشائم")], [30, 60, 90], color=['#10b981', '#f59e0b', '#ef4444'])
    plt.tight_layout()
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=150) # زيادة دقة الصورة
    img_buffer.seek(0)
    plt.close()
    
    # توسيط الصورة
    img = RLImage(img_buffer, width=350, height=180)
    img.hAlign = 'CENTER'
    elements.append(img)
    elements.append(Spacer(1, 20))

    # --- جدول التوصيات السيادية ---
    elements.append(Paragraph(process_arabic("القرارات السيادية العاجلة:"), heading_style))
    if actions:
        table_data = [[process_arabic("الأولوية"), process_arabic("القرار السيادي المطلوب"), process_arabic("الإطار الزمني")]]
        for act in actions:
            # استخراج النص بشكل آمن
            action_text = act.get('action', act.get('decision', ''))
            # تغليف النص الطويل داخل الخلية باستخدام Paragraph لكي لا يكسر الجدول
            action_paragraph = Paragraph(process_arabic(action_text), ParagraphStyle('TableText', fontName=font_name, fontSize=12, alignment=TA_RIGHT, leading=18))
            
            table_data.append([
                process_arabic(act.get('priority', 'عاجل')),
                action_paragraph, # نضع الفقرة المنسقة بدلاً من النص الخام
                process_arabic(act.get('timeline', 'مستمر'))
            ])
            
        # 🌟 مقاسات هندسية دقيقة لتناسب عرض A4 (المجموع = 535)
        t = Table(table_data, colWidths=[85, 350, 100])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e3a8a")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,0), 'CENTER'), # توسيط العناوين
            ('ALIGN', (0,1), (0,-1), 'CENTER'), # توسيط الأولوية
            ('ALIGN', (2,1), (2,-1), 'CENTER'), # توسيط الزمن
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), # توسيط عمودي للجميع
            ('FONTNAME', (0,0), (-1,-1), font_name),
            ('FONTSIZE', (0,0), (-1,-1), 12),
            ('BOTTOMPADDING', (0,0), (-1,-1), 12),
            ('TOPPADDING', (0,0), (-1,-1), 12),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#ffffff"), colors.HexColor("#f8fafc")]), # تلوين الصفوف بالتناوب
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#94a3b8")),
        ]))
        elements.append(t)
    else:
        elements.append(Paragraph(process_arabic("لا توجد توصيات متوفرة."), normal_style))

    doc.build(elements)
    buffer.seek(0)
    
    return send_file(buffer, as_attachment=True, download_name=f"Strategic_Report.pdf", mimetype='application/pdf')
if __name__ == '__main__':
    # إضافة host='0.0.0.0' تجبر السيرفر على فتح بوابته للجميع
    app.run(host='0.0.0.0', debug=True, port=5000)