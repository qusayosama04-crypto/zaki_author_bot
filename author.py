import os
import telebot
from google import genai
from dotenv import load_dotenv
import docx
import re
import time 
from flask import Flask
from threading import Thread

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# 🧹 تنظيف التنسيقات
def clean_markdown(text):
    # مسح كل النجوم المزدوجة والمفردة والهاشتاج بقوة الاستبدال المباشر
    text = text.replace('**', '')
    text = text.replace('*', '')
    text = text.replace('#', '')
    return text.strip()

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "مرحباً بك في Zaki Author 📚 (النسخة الملحمية)!\nأعطني فكرة كتابك، وسأقوم بتأليفه باحترافية وتفصيل شديد (هذا البوت مخصص للكتب الطويلة جداً، لذا قد يستغرق بعض الوقت).")

@bot.message_handler(func=lambda message: True)
def write_epic_book(message):
    topic = message.text
    msg = bot.reply_to(message, f"⏳ جاري التخطيط لمجلد ضخم عن: {topic}\nأقوم الآن برسم الفهرس وتحديد الفصول... 🧠")
    
    try:
        # 1. طلب فهرس من 12 فصلاً
        index_prompt = f"أنت مؤلف كتب عالمي. اكتب لي فهرساً يتكون من 12 فصلاً لكتاب احترافي وشامل عن '{topic}'. أريد أسماء الفصول فقط مفصولة برمز النجمة (*) بدون أي أرقام أو نصوص أخرى."
        
        index_response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=index_prompt
        )
        
        # استخراج الفصول وتجاهل الفراغات
        chapters = [c.strip() for c in index_response.text.split('*') if len(c.strip()) > 3]
        
        if not chapters:
            bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text="❌ حدث خطأ في استخراج الفهرس، يرجى المحاولة بعنوان آخر.")
            return

        # 2. تجهيز الوورد
        doc = docx.Document()
        doc.add_heading(f"كتاب: {topic}", 0)
        
        # 3. رحلة التأليف الطويلة (حلقة تكرارية)
        for i, chapter_title in enumerate(chapters, 1):
            bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text=f"✍️ جاري تأليف الفصل {i} من {len(chapters)}...\n(العنوان: {chapter_title})\n\nالجودة العالية تحتاج وقتاً، احتسِ قهوتك ☕...")
            
            # هندسة الأوامر لكتابة فصل شديد الطول
            chapter_prompt = f"""
            أنت مؤلف كتب محترف وخبير عالمي. اكتب محتوى طويلاً جداً ومفصلاً وشاملاً (أكثر من 1500 كلمة) للفصل التالي: "{chapter_title}"
            وهو جزء من كتاب بعنوان: "{topic}".
            
            الشروط الصارمة:
            1. تعمق في الشرح بشكل أكاديمي ومبسط ولا تعطِ معلومات سطحية.
            2. استخدم أمثلة عملية، دراسات حالة، أو خطوات قابلة للتطبيق.
            3. قسم الفصل إلى فقرات طويلة وعناوين فرعية لتسهيل القراءة.
            4. لا تكتب مقدمة أو خاتمة عامة للكتاب، اكتب محتوى هذا الفصل فقط وبشكل مباشر.
            """
            
            chapter_response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=chapter_prompt
            )
            
            # تنظيف وإضافة الفصل
            clean_text = clean_markdown(chapter_response.text)
            doc.add_heading(chapter_title, level=1)
            doc.add_paragraph(clean_text)
            doc.add_page_break()
            
            # استراحة 15 ثانية للهروب من حظر جوجل وإعطاء الذكاء الاصطناعي فرصة للتنفس
            time.sleep(15)

        # 4. حفظ وإرسال
        safe_topic = topic.replace(' ', '_').replace('/', '_')
        file_name = f"{safe_topic}_Epic.docx"
        doc.save(file_name)
        
        bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text="✅ تمت طباعة المجلد الضخم بنجاح! جاري التغليف والإرسال... 📦")
        
        with open(file_name, 'rb') as book_file:
            bot.send_document(message.chat.id, book_file, caption=f"📚 كتابك الملحمي الشامل جاهز!\nالعنوان: {topic}\nعدد الفصول: {len(chapters)}\nتأليف: Zaki Author Bot")
        
        os.remove(file_name)
        
    except Exception as e:
        print(f"Error: {e}")
        bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text="❌ عذراً، انقطع الاتصال بسبب الضغط الكبير. يرجى المحاولة لاحقاً.")
# --- بداية كود خدعة السيرفر (Flask) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Bot is Alive and Running 24/7!"

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# تشغيل خادم الويب الوهمي في الخلفية
keep_alive()
# --- نهاية كود الخدعة ---

# هنا يجب أن يكون سطر تشغيل البوت الخاص بك (موجود مسبقاً)
# bot.polling(none_stop=True)

print("🤖 المطبعة الملحمية تعمل الآن! جاهزة لكتابة المجلدات الضخمة...")
bot.infinity_polling(timeout=90, long_polling_timeout=90) # زدنا وقت الانتظار لتجنب انقطاع تليجرام
