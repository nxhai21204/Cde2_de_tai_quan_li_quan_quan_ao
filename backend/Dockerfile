# Dockerfile

# 1. Chọn base image Python 3.10
FROM python:3.10-slim

# 2. Set working directory
WORKDIR /app

# 3. Copy requirements
COPY requirements.txt .

# 4. Cập nhật pip và cài dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir "pydantic[email]>=2.0"


# 5. Copy toàn bộ project
COPY . .

# 6. Expose port của FastAPI
EXPOSE 8001

# 7. Lệnh chạy FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
