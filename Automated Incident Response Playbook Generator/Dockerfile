FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install git and curl (for healthcheck)
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

# Clone the repo
#RUN git clone https://github.com/rod-trent/JunkDrawer.git

# Set working directory to the specific folder containing AIR.py
WORKDIR "/usr/src/app/JunkDrawer/Automated Incident Response Playbook Generator"

# Install all required dependencies
RUN pip install --no-cache-dir \
    streamlit \
    python-dotenv \
    requests \
    extra-streamlit-components

COPY AIR.py .

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run the correct script name: AIR.py
CMD ["streamlit", "run", "AIR.py", "--server.address=0.0.0.0"]
