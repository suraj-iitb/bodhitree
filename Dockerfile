# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.9-slim-buster

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY requirements.txt .
RUN pip install --upgrade pip && python -m pip install -r requirements.txt

WORKDIR /bodhitree

# Switching to a non-root user, please refer to https://aka.ms/vscode-docker-python-user-rights
RUN useradd bodhitree && chown -R bodhitree /bodhitree
USER bodhitree

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["gunicorn", "--bind", "0.0.0.0:8765", "main.wsgi"]
