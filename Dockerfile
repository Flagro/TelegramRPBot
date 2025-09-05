FROM python:3.11

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN pip install poetry

RUN poetry config virtualenvs.create false && poetry install

COPY . .

CMD ["python", "main.py"]
