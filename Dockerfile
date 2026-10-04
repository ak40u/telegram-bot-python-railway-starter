FROM python:3.13-slim

# Print log lines as they happen. Without this, Python buffers stdout when it is not a terminal,
# and a bot that stops on a bad token never shows why.
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY main.py .

# The start command lives in the image rather than in railway.json: Railway no longer reads
# config-as-code for services created from a template.
CMD ["python", "main.py"]
