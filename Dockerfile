ARG BUILD_ENV=prod

FROM python:3.9-slim-buster as prod
ONBUILD COPY . .

FROM python:3.9-slim-buster as dev
ONBUILD RUN echo "No source code copy for dev env"

FROM ${BUILD_ENV}

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY requirements.txt .
RUN pip install --upgrade pip && python -m pip install --no-cache-dir -r requirements.txt

# Working directory
WORKDIR /bodhitree

# Switching to a non-root user
RUN useradd bodhitree && chown -R bodhitree /bodhitree
USER bodhitree

# During debugging, this entry point will be overridden
# Configure properly for prod
CMD ["gunicorn", "--bind", "0.0.0.0:8765", "main.wsgi"]
