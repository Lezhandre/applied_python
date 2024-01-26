FROM python:3.11-slim
LABEL authors="michael"

WORKDIR home

COPY .env python/

COPY handlers/*.py python/handlers/
COPY *.py python/

RUN pip install requests aiogram pandas pydantic_settings

WORKDIR python

#CMD ["python", "bot.py"]