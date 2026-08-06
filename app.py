import os
import streamlit as st
from google import genai

# تنظیمات اولیه صفحه
st.set_page_config(page_title="دستیار و منشی آموزشی", page_icon="🎓", layout="centered")

st.title("🎓 منشی و دستیار آموزشی هوشمند")
st.caption("پاسخ‌گویی مبتنی بر اسناد و محتوای آموزشی کتابخانه")

# دریافت کلید API از تنظیمات Streamlit
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("کلید API تنظیم نشده است. لطفاً در تنظیمات Streamlit کلید GEMINI_API_KEY را وارد کنید.")
    st.stop()

# راه‌اندازی کلاینت
client = genai.Client(api_key=api_key)

# دستورالعمل سیستم (System Instruction)
system_instruction = """تو یک «منشی و دستیار آموزشی هوشمند، پویا و فعال» هستی. وظیفه تو پاسخ‌گویی به دانشجویان بر اساس اسناد، ویدئوها و فایل‌های صوتی موجود در کتابخانه است.

قواعد و اصول عملکرد تو:
۱. درک خواسته و پویایی: ابتدا هدف دانشجو را تحلیل کن (آیا طرح درس می‌خواهد؟ طرح گفتگو؟ پاسخ تحلیلی؟ یا خلاصه؟). پاسخ را دقیقاً متناسب با سطح، مخاطب و شرایط خواسته شده توسط دانشجو بازآفرینی کن.
۲. استخراج از کتابخانه: تمام پاسخ‌های تو باید مستند به فایل‌ها و ویدئوهای آپلودشده در کتابخانه باشند.
۳. استناد به منبع: در پایان هر پاسخ، حتماً منبع دقیق را ذکر کن (مثلاً: نام سند PDF، یا دقیقه مشخصی از ویدئو/فایل صوتی).
۴. لحن پاسخ‌گویی: محترمانه، ساختاریافته، کاملاً شفاف و آماده برای کپی‌برداری توسط دانشجو باشد."""

# مدیریت تاریخچه گفتگوها
if "messages" not in st.session_state:
    st.session_state.messages = []

# نمایش پیام‌های قبلی
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# کادر ورودی سوال دانشجو
if user_prompt := st.chat_input("سوال یا درخواست خود را بنویسید..."):
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    with st.chat_message("assistant"):
        with st.spinner("در حال تحلیل و جستجو در کتابخانه..."):
            try:
                response = client.models.generate_content(
                    model='gemini-2.0-flash',
                    contents=user_prompt,
                    config={
                        'system_instruction': system_instruction,
                        'temperature': 0.3,
                    }
                )
                answer_text = response.text
                st.markdown(answer_text)
                st.session_state.messages.append({"role": "assistant", "content": answer_text})
            except Exception as e:
                st.error(f"خطایی رخ داد: {e}")
