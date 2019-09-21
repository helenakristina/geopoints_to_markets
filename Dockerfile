FROM continuumio/miniconda3

RUN conda config --add channels conda-forge 

RUN conda config --set channel_priority strict

RUN conda update -n base -c defaults conda

RUN conda create -n env python=3.7

ADD requirements.txt /opt/app/requirements.txt

RUN conda install --yes --channel conda-forge --file /opt/app/requirements.txt

ADD src /opt/app/src

ADD input /opt/app/input

ADD output /opt/app/output

ADD conf /opt/app/conf

WORKDIR /opt/app/src

CMD ["python", "/opt/app/src/app.py"]
