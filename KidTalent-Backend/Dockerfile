# Sử dụng Python image chính thức làm base
FROM python:3.11-slim

# Đặt thư mục làm việc trong container
WORKDIR /app

# Copy file requirements.txt vào container
COPY requirements.txt .

# Cài đặt các thư viện cần thiết
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn vào container
COPY . .

# Mở cổng 8000 cho ứng dụng
EXPOSE 8000

# Lệnh chạy ứng dụng khi container khởi động
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
