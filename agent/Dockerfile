FROM python:3.11-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml ./
RUN uv pip install --system "livekit-agents[google,images,turn-detector]~=1.4" "google-genai>=1.16.0" "python-dotenv>=1.0.0"

COPY agent.py ./
RUN python agent.py download-files

CMD ["python", "agent.py", "start"]
