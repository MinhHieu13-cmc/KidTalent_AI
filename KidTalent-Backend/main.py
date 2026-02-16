import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

# 1. Cấu hình & Bảo mật
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("LỖI: Chưa tìm thấy API Key!")

# 2. Khởi tạo kho lưu trữ lịch sử tin nhắn
# Cấu trúc: { "session_id_1": ChatMessageHistory_1, "session_id_2": ChatMessageHistory_2 }
user_sessions = {}

def get_session_history(session_id: str):
    if session_id not in user_sessions:
        user_sessions[session_id] = ChatMessageHistory()
    return user_sessions[session_id]

# 3. Khởi tạo AI Model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GOOGLE_API_KEY,
    temperature=0.7
)

# 4. Kịch bản thông minh (Prompt có Trí nhớ)
template = """
Bạn là "Thám tử Gà Mơ", bạn của các bạn nhỏ.
Nhiệm vụ: Trò chuyện để tìm ra sở thích của bé.

Thông tin bé: {age} tuổi.

Lịch sử trò chuyện trước đó (Hãy đọc kỹ để không hỏi lại):
{chat_history}

Tin nhắn mới của bé: "{user_message}"

Thám tử trả lời (Ngắn gọn, vui vẻ, gợi mở):
"""

prompt = PromptTemplate(
    input_variables=["age", "chat_history", "user_message"],
    template=template
)

# 5. Tạo Chain bằng LCEL
# Kết nối: Prompt -> LLM -> Output Parser
base_chain = prompt | llm | StrOutputParser()

# Gắn khả năng quản lý lịch sử cho Chain
chain_with_history = RunnableWithMessageHistory(
    base_chain,
    get_session_history,
    input_messages_key="user_message",
    history_messages_key="chat_history",
)

# 6. API Backend
app = FastAPI(title="KidTalent AI - Có Trí Nhớ")

@app.get("/")
def read_root():
    return {"message": "KidTalent Backend is running!", "status": "ok"}

# Cập nhật Data Model: Thêm session_id
class ChatRequest(BaseModel):
    session_id: str  # Ví dụ: "be_bi_01"
    user_message: str
    child_age: int = 10


class ChatResponse(BaseModel):
    ai_reply: str


@app.post("/chat", response_model=ChatResponse)
async def chat_with_memory(request: ChatRequest):
    # --- GỌI AI TRẢ LỜI ---
    try:
        # Sử dụng chain_with_history để tự động quản lý lịch sử theo session_id
        reply_text = chain_with_history.invoke(
            {"age": request.child_age, "user_message": request.user_message},
            config={"configurable": {"session_id": request.session_id}}
        )

        return ChatResponse(ai_reply=reply_text)

    except Exception as e:
        return ChatResponse(ai_reply=f"Thám tử đang mất trí nhớ tạm thời... (Lỗi: {str(e)})")

# Chạy server: uvicorn main:app --reload