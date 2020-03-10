FROM ubuntu

RUN apt-get -y update
#RUN apt-get -y upgrade

RUN apt-get install -y python3-pip

COPY entrypoint.sh .
COPY entrypoint.py .
RUN /bin/chmod +x ./entrypoint.sh
RUN /bin/chmod +x ./entrypoint.py

CMD ["./entrypoint.sh"]
