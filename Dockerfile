FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen

COPY . .

EXPOSE 8501

CMD ["uv", "run", "streamlit", "run", "src/ui/interface.py", "--server.address", "0.0.0.0"]