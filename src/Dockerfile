FROM python:3.12-slim
LABEL author="viktor"

WORKDIR /app/todo_bot

COPY src ./src
COPY ./requirements.txt .

RUN apt-get update && apt-get upgrade
RUN pip3 install -r  requirements.txt && pip3 cache purge

CMD python3 -m src prod
