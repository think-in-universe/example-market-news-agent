FROM python:3.13-slim-bookworm

WORKDIR /app

COPY pyproject.toml /app/
COPY main.py /app/

RUN pip install uv && uv sync

CMD ["uv", "run", "main.py"]