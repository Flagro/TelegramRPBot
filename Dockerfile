# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    python3-venv \
    ffmpeg \
    git \
    curl \
    && curl -sSL https://install.python-poetry.org | python3 -

# Set work directory
WORKDIR /code

# Copy project file
COPY ./pyproject.toml /code/

# Install project dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Copy all project
COPY . /code/

CMD ["bash"]
