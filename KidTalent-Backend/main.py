import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.output_parsers import PydanticOutputParser
from schemas import Talent_profile
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

# --- [NEW] API PHÂN TÍCH TÀI NĂNG ---
# 1. Tạo Parser (Bộ dịch mã để ép AI trả về JSON chuẩn)
parser = PydanticOutputParser(pydantic_object=Talent_profile)
# 2. Tạo Prompt chuyên dụng cho việc Phân tích
analysis_template = """
Bạn là Chuyên gia Tâm lý Giáo dục trẻ em.
Nhiệm vụ của bạn là đọc lịch sử trò chuyện dưới đây giữa "Thám tử Gà Mơ" và một em bé {age} tuổi.
Hãy phân tích kỹ lưỡng để tìm ra thiên hướng tài năng của bé.

LỊCH SỬ TRÒ CHUYỆN:
{chat_history}

YÊU CẦU ĐẦU RA:
{format_instructions}
"""

analysis_prompt = PromptTemplate(
    template=analysis_template,
    input_variables=["age", "chat_history"],
    partial_variables= {"format_instructions": parser.get_format_instructions()}
)


# 3. Định nghĩa API Endpoint mới
class AnalyzeRequest(BaseModel):
    session_id: str
    child_age: int = 10


@app.post("/analyze")  # Không cần response_model vì nó trả về JSON động
async def analyze_talent(request: AnalyzeRequest):
    session_id = request.session_id

    # Kiểm tra xem bé này có lịch sử chat chưa
    if session_id not in user_sessions:
        return {"error": "Chưa có dữ liệu trò chuyện nào để phân tích!"}

    # Lấy toàn bộ lịch sử chat từ bộ nhớ
    memory = user_sessions[session_id]
    history_messages = memory.messages
    
    # Chuyển list tin nhắn thành text để AI đọc
    history_text = ""
    for msg in history_messages:
        role = "Bé" if msg.type == "human" else "Thám tử"
        history_text += f"{role}: {msg.content}\n"

    if not history_text.strip():
        return {"error": "Cuộc trò chuyện quá ngắn, chưa đủ dữ liệu phân tích."}

    print(f"--- Đang phân tích hồ sơ bé {session_id} ---")

    # Tạo Chain phân tích
    analysis_chain = analysis_prompt | llm | parser

    try:
        # Gọi AI thực hiện phân tích
        result = analysis_chain.invoke({
            "age": request.child_age,
            "chat_history": history_text
        })

        # Kết quả 'result' lúc này đã là một object Python (TalentProfile)
        # Chúng ta chuyển nó thành JSON (dict) để trả về cho Frontend
        return result.dict()

    except Exception as e:
        return {"error": f"Lỗi phân tích: {str(e)}"}

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