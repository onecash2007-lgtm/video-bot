import os
import time
from flask import Flask
from threading import Thread
import telebot
import yt_dlp

# 1. إعداد توكن البوت الخاص بك
TOKEN = "9035100579:AAGwAPAGx744kbpyW-Ya102pR6ijtWJ9Go8"
bot = telebot.TeleBot(TOKEN)

# 2. إعداد سيرفر الويب الوهمي لضمان بقاء البوت شغالاً 24/7 (Keep-Alive)
app = Flask('')

@app.route('/')
def home():
    return "Bot is active and running 24/7!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# 3. دالة الترحيب عند إرسال /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, 
                 "أهلاً بك في بوت تحميل الفيديوهات! 📥\n\n"
                 "فقط قم بإرسال رابط أي فيديو (من تيك توك، يوتيوب، إنستغرام، فيسبوك...) وسأقوم بتحميله وإرساله لك فوراً.")

# 4. استقبال الروابط وتحميل الفيديو
@bot.message_handler(func=lambda message: True)
def download_video(message):
    url = message.text.strip()
    
    # التأكد من أن الرسالة تبدو كأنها رابط
    if not url.startswith("http://") and not url.startswith("https://"):
        bot.reply_to(message, "⚠️ أهلاً بك، يرجى إرسال **رابط صحيح** يبدأ بـ http أو https.")
        return

    msg = bot.reply_to(message, "⏳ جاري المعالجة والتحميل، يرجى الانتظار...")

    # إعدادات مكتبة yt-dlp للتحميل بأفضل جودة تناسب تيليجرام
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'max_filesize': 50 * 1024 * 1024, # حماية لتجنب الملفات الضخمة جداً (أكثر من 50 ميجابايت)
    }

    try:
        os.makedirs('downloads', exist_ok=True)
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        bot.edit_message_text("📤 جاري رفع الفيديو إليك...", message.chat.id, msg.message_id)

        # إرسال الفيديو للمستخدم
        with open(filename, 'rb') as video:
            bot.send_video(message.chat.id, video, caption="تم التحميل بنجاح بواسطة البوت ✨")

        # حذف الملف من السيرفر بعد الإرسال لتوفير المساحة
        if os.path.exists(filename):
            os.remove(filename)
            
        bot.delete_message(message.chat.id, msg.message_id)

    except Exception as e:
        print(f"Error: {e}")
        bot.edit_message_text(
            "❌ عذراً، لم أتمكن من تحميل الفيديو. قد يكون الرابط خاطئاً، أو الفيديو خاصاً، أو حجماً أكبر من المسموح.", 
            message.chat.id, 
            msg.message_id
        )

if __name__ == "__main__":
    # تشغيل السيرفر الوهمي أولاً
    keep_alive()
    print("Bot is starting...")
    # تشغيل البوت
    bot.infinity_polling()
