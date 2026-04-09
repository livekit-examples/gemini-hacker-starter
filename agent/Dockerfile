FROM python:3.11-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml ./
RUN uv pip install --system "livekit-agents[google,images]~=1.4" "google-genai>=1.16.0" "python-dotenv>=1.0.0"

COPY agent.py ./

CMD ["python", "agent.py", "start"]
