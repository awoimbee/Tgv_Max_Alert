FROM python:3.9

WORKDIR /opt/app
COPY tgvmax_alert .

ENTRYPOINT [ "python", "./main.py" ]
