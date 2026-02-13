FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /backend

# 1. 依存関係のインストール（キャッシュ活用）
# backend/ 内にいるのでそのままコピー可能
COPY requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt

# 2. ソースコード一式（app/, data/, scripts/ など）を /app にコピー
COPY . . 

# 3. 起動コマンド
# /app/app/main.py が存在するので app.main:app で指定
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]