FROM pytorch/pytorch:1.8.1-cuda11.1-cudnn8-devel

RUN apt-get update

WORKDIR /
COPY *.py /
RUN pip install h5py mlflow google-cloud-storage

ENTRYPOINT ["train.py"]
