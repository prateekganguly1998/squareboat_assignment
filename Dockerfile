FROM python:slim

RUN useradd squareboat_social

WORKDIR /home/squareboat

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY squareboat_social squareboat_social
COPY migrations migrations
COPY app.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP app.py

RUN chown -R squareboat_social:squareboat_social ./
USER squareboat_social

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]