FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
# The RUN command now reads from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# --- vvvv PRODUCTION CHANGES vvvv ---

# 1. Get the port from the environment variable (Render will set this to 10000)
# We set a default of 8000 just in case it's not provided.
ENV PORT=${PORT:-8000}

# 2. Expose the port that the container will listen on
EXPOSE $PORT

# 3. Update the CMD:
#    - Remove "--reload" (it's for development only)
#    - Use the "$PORT" environment variable instead of hard-coding "8000"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "$PORT"]
# --- ^^^^ END PRODUCTION CHANGES ^^^^ ---