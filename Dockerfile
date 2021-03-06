# Build env
ARG BUILD_ENV=prod

# Copy source code if production env
FROM python:3.9-slim-buster as prod
ONBUILD COPY . /bodhitree

# Dont copy source code if development env
FROM python:3.9-slim-buster as dev
ONBUILD COPY requirements.dev.txt /tmp/requirements.dev.txt
ONBUILD RUN python -m pip install --no-cache-dir -r /tmp/requirements.dev.txt

FROM ${BUILD_ENV}

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY requirements.txt /tmp/requirements.txt
RUN python -m pip install --no-cache-dir -r /tmp/requirements.txt

# Working directory
WORKDIR /bodhitree

# During debugging, this entry point will be overridden
# TODO: Configure properly for prod
CMD ["gunicorn", "--bind", "0.0.0.0:8765", "main.wsgi"]
