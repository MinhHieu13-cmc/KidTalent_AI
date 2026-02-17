from typing import List, Optional
from pydantic import BaseModel, Field

# Đây là "Tờ phiếu đánh giá" mà AI phải điền vào sau khi chat xong
class Talent_profile(BaseModel):
    summary : str = Field(description="Tóm tắt ngắn gọn về sở thích của bé dựa trên hội thoại.")
    dominant_intelligence : str = Field(
        description= "Loại hình trí thông minh nổi trội nhất ví dụ (ngôn ngữ , vận động , âm nhạc giao tiếp...)"
    )
    personality_traits : List[str] = Field(
        description= "Danh sách 3-5 tính cách nổi bật (Ví dụ: Hướng ngoại, Tỉ mỉ, Sáng tạo...)"
    )
    suggested_careers : List[str] = Field(
        description= "Gợi ý 3 nghề nghiệp tương lai phù hợp với bé."
    )
    advice_for_parents : str = Field(
        description= "Lời khuyên dành cho cha mẹ để giúp bé phát triển tài năng này."
    )
