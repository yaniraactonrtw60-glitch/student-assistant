import os
import streamlit as st
from openai import OpenAI
from pypdf import PdfReader

# ۱. دریافت کلید API مربوط به OpenRouter
api_key = st.secrets.get("OPENROUTER_API_KEY")

if not api_key:
    st.error("کلید OPENROUTER_API_KEY در بخش Secrets یافت نشد.")
    st.stop()

# اتصال به OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

# ۲. استخراج و کش کردن متن PDFها
@st.cache_data
def extract_pdf_context():
    combined_text = ""
    pdf_dir = "data"
    if os.path.exists(pdf_dir):
        for file in os.listdir(pdf_dir):
            if file.endswith(".pdf"):
                try:
                    reader = PdfReader(os.path.join(pdf_dir, file))
                    for page in reader.pages:
                        if text := page.extract_text():
                            combined_text += text + "\n"
                except Exception as e:
                    st.warning(f"خطا در خواندن فایل {file}: {e}")
    # محدود کردن متن برای کنترل توکن
    return combined_text[:20000]

context_text = extract_pdf_context()

# ۳. رابط کاربری Streamlit
st.set_page_config(page_title="دستیار آموزشی", page_icon="🎓")
st.title("🎓 منشی و دستیار آموزشی هوشمند")
st.caption("پاسخ‌گویی مبتنی بر اسناد کتابخانه")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("سوال خود را بنویسید..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            messages_payload = [
                {"role": "system", "content": f"شما یک دستیار آموزشی هستید. با توجه به متن زیر به سوال کاربر پاسخ دهید:\n\n{context_text}"}
            ] + st.session_state.messages

            response = client.chat.completions.create(
                model="meta-llama/llama-3.1-8b-instruct:free",
                messages=messages_payload,
            )

            reply = response.choices[0].message.content
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})

        except Exception as e:
            st.error(f"خطایی رخ داد: {e}")
