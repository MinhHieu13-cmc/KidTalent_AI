from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import requests


# 1. HÀM TẢI FONT TIẾNG VIỆT (Tự động tải nếu thiếu)
def setup_font():
    # Lấy thư mục hiện tại của file report_generator.py (KidTalent-Backend)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(base_dir, "DejaVuSans.ttf")
    
    # URL từ repo chính thức của matplotlib (cực kỳ ổn định và chuẩn binary)
    url = "https://raw.githubusercontent.com/matplotlib/matplotlib/main/lib/matplotlib/mpl-data/fonts/ttf/DejaVuSans.ttf"
    
    try:
        # Kiểm tra nếu file tồn tại nhưng bị hỏng (là file HTML hoặc quá nhỏ)
        is_corrupted = False
        if os.path.exists(font_path):
            file_size = os.path.getsize(font_path)
            # File font chuẩn phải nặng khoảng 700KB. Nếu < 100KB chắc chắn lỗi.
            if file_size < 100000:
                is_corrupted = True
            else:
                # Kiểm tra nội dung xem có phải HTML không
                with open(font_path, 'rb') as f:
                    header = f.read(15)
                    if b"<!DOCTYPE" in header or b"<html" in header:
                        is_corrupted = True

        # Nếu chưa có font hoặc font bị hỏng, tải lại từ nguồn tin cậy
        if not os.path.exists(font_path) or is_corrupted:
            if is_corrupted:
                print(f"Phát hiện file font hiện tại bị hỏng (nội dung lỗi). Đang tải lại từ: {url}")
            else:
                print(f"Đang tải font hỗ trợ tiếng Việt vào: {font_path}...")
            
            r = requests.get(url, stream=True, timeout=20)
            if r.status_code == 200:
                with open(font_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                print("Tải font chuẩn thành công!")
            else:
                print(f"Không thể tải font (Status: {r.status_code}). Sử dụng font mặc định.")
                return 'Helvetica'
        
        # Đăng ký font với ReportLab
        pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
        return 'DejaVuSans'
    except Exception as e:
        print(f"Lỗi khi xử lý font: {e}. Sử dụng font mặc định.")
        return 'Helvetica'


# 2. HÀM TẠO FILE PDF
def create_talent_pdf(output, data):
    # Cấu hình trang giấy
    doc = SimpleDocTemplate(output, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)

    # Chuẩn bị font
    font_name = setup_font()

    # Định nghĩa các kiểu chữ (Styles)
    styles = getSampleStyleSheet()

    # Kiểu Tiêu đề (To, Đậm, Giữa)
    title_style = ParagraphStyle(
        'TalentTitle',
        parent=styles['Heading1'],
        fontName=font_name,
        fontSize=24,
        alignment=1,  # Center
        spaceAfter=30,
        textColor=colors.HexColor("#2E86C1")  # Màu xanh TeenUp
    )

    # Kiểu Nội dung thường
    normal_style = ParagraphStyle(
        'TalentNormal',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=12,
        leading=16,  # Khoảng cách dòng
        spaceAfter=12
    )

    # Kiểu Tiêu đề con (Heading 2)
    h2_style = ParagraphStyle(
        'TalentH2',
        parent=styles['Heading2'],
        fontName=font_name,
        fontSize=16,
        textColor=colors.HexColor("#D35400"),  # Màu cam
        spaceAfter=10,
        spaceBefore=20
    )

    # --- NỘI DUNG PDF ---
    story = []

    # 1. Tiêu đề
    story.append(Paragraph("HỒ SƠ TÀI NĂNG TRẺ", title_style))
    story.append(Spacer(1, 12))

    # 2. Lời dẫn
    intro = f"Báo cáo phân tích dành cho bé: <b>{data.get('child_name', 'Bé Yêu')}</b> ({data.get('age', 8)} tuổi)"
    story.append(Paragraph(intro, normal_style))
    story.append(Spacer(1, 12))

    # 3. Kết quả phân tích
    story.append(Paragraph("Tóm tắt tài năng", h2_style))
    story.append(Paragraph(data.get('summary', 'Chưa có tóm tắt.'), normal_style))

    story.append(Paragraph("1. Trí thông minh nổi trội", h2_style))
    story.append(Paragraph(data['dominant_intelligence'], normal_style))

    story.append(Paragraph("2. Tính cách đặc trưng", h2_style))
    # Nối danh sách tính cách thành chuỗi
    traits = ", ".join(data['personality_traits'])
    story.append(Paragraph(traits, normal_style))

    story.append(Paragraph("3. Nghề nghiệp tương lai gợi ý", h2_style))
    for job in data['suggested_careers']:
        story.append(Paragraph(f"• {job}", normal_style))

    story.append(Paragraph("4. Lời khuyên cho Phụ huynh", h2_style))
    story.append(Paragraph(data['advice_for_parents'], normal_style))

    story.append(Spacer(1, 40))

    # 5. Footer (Quảng cáo khéo léo cho TeenUp)
    footer = "Báo cáo được tạo bởi hệ thống AI của <b>KidTalent</b>."
    story.append(Paragraph(footer, ParagraphStyle('Footer', parent=normal_style, fontSize=10, textColor=colors.grey,
                                                  alignment=1)))

    # Xây dựng file
    doc.build(story)
    return output