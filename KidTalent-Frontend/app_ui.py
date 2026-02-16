import streamlit as st
import requests
import uuid  # Để tạo mã định danh cho từng bé (Session ID)
import os
# 1. Cấu hình trang web
st.set_page_config(page_title="Thám tử Gà Mơ 🐔", page_icon="🕵️‍♂️")

st.title("🕵️‍♂️ Thám tử Gà Mơ - Khám phá Tài năng")
st.write("Chào bạn nhỏ! Hãy kể cho Thám tử nghe về sở thích của bạn nhé!")

# 2. Kết nối với Backend (QUAN TRỌNG)
# Đây là địa chỉ của cái "Hộp Docker" bạn đã chạy hôm qua
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/chat")

# 3. Quản lý Lịch sử Chat & Session ID
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())  # Tạo 1 mã ngẫu nhiên cho bé này

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant",
         "content": "Chào nhóc tì! Thám tử Gà Mơ đây. Nhóc tên là gì và năm nay bao nhiêu tuổi rồi? 🐔"}
    ]

# 4. Hiển thị hội thoại cũ
for msg in st.session_state.messages:
    # Chọn avatar: Gà cho AI, Người cho bé
    avatar = "🐔" if msg["role"] == "assistant" else "👶"
    with st.chat_message(msg["role"], avatar=avatar):
        st.write(msg["content"])

# 5. Xử lý khi bé nhập tin nhắn
if user_input := st.chat_input("Nhập câu trả lời của bé vào đây..."):
    # Hiện tin nhắn của bé lên màn hình ngay lập tức
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="👶"):
        st.write(user_input)

    # Gửi sang Backend để AI suy nghĩ
    with st.chat_message("assistant", avatar="🐔"):
        with st.spinner("Thám tử đang suy nghĩ..."):
            try:
                # Gửi gói tin JSON sang API
                payload = {
                    "session_id": st.session_state.session_id,
                    "user_message": user_input,
                    "child_age": 8  # Tạm để cứng, sau này có thể làm ô nhập tuổi
                }

                response = requests.post(BACKEND_URL, json=payload)

                if response.status_code == 200:
                    ai_reply = response.json()["ai_reply"]
                    st.write(ai_reply)

                    # Lưu lời AI vào lịch sử
                    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                else:
                    st.error("Thám tử bị mất kết nối với tổng hành dinh! 😭")

            except Exception as e:
                st.error(f"Lỗi kết nối: {e}")
                st.info("Gợi ý: Bạn đã chạy Backend (Docker/Uvicorn) chưa?")