FROM python:3.11-slim
WORKDIR /app
COPY .. /app
RUN pip install --no-cache-dir -e . fastapi uvicorn[standard]
CMD ["uvicorn", "worker.worker:app", "--host", "0.0.0.0", "--port", "8001"]
