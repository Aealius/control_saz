FROM python:3.13-slim

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY app app
COPY migrations migrations
COPY control_saz.py config.py boot.sh ./

ENV FLASK_APP control_saz.py
EXPOSE 5000
ENTRYPOINT [ "boot.sh" ]
