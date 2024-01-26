FROM python:3.11-slim
LABEL authors="michael"

WORKDIR home

COPY *.csv python/
COPY *.py python/

RUN pip install uvicorn fastapi pandas scikit-learn pydantic

WORKDIR python

CMD ["python", "fastapi_service.py"]