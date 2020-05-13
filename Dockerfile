FROM python:3

ADD main.py /

RUN pip3 install pyserial
RUN pip3 install paho-mqtt
RUN pip3 install slackclient

CMD [ "python", "./main.py" ]