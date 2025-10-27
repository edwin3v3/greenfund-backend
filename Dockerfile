FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Set a default port in case Render doesn't inject one
ENV PORT=8000

# Expose port (good practice, though Render ignores it)
EXPOSE $PORT

# ✅ Correct CMD — allows $PORT to expand properly
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
