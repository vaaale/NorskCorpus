FROM ubuntu

RUN apt-get -y update
#RUN apt-get -y upgrade

RUN apt-get install -y python3-pip

COPY entrypoint.sh .
RUN /bin/chmod +x ./entrypoint.sh

CMD ["./entrypoint.sh"]
