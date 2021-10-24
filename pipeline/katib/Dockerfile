FROM alpine:latest

RUN apk add python3 py3-pip
RUN pip3 install kubernetes

COPY submit_katib.py /

ENTRYPOINT ["python3", "submit_katib.py"]
