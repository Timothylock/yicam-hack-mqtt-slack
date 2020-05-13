import os
import json
import paho.mqtt.client as mqtt
from ftplib import FTP
from slack import WebClient
from slack.errors import SlackApiError

filename = "./tmp.mp4"

# Env Vars
broker = os.environ['MQTT_BROKER']
broker_port = int(os.environ['MQTT_PORT'])
topic = os.environ['TOPIC']
cam_ip = os.environ['CAM_IP']
ftp_user = os.environ['FTP_USER']
ftp_pass = os.environ['FTP_PASS']
skip_trailing = int(os.environ['SKIP_TRAILING_VIDEO'])

# Initialize Slack Client
slack_client = WebClient(token=os.environ['SLACK_API_TOKEN'])


def upload_to_slack():
    try:
        response = slack_client.files_upload(
            channels='#security',
            file=filename)
        assert response["file"] 
    except SlackApiError as e:
        print(f"Got an error: {e.response['error']}")


def on_connect(client, userdata, flags, rc):
    print("Connected with result code {0}".format(str(rc)))
    client.subscribe(topic)


def on_message(client, userdata, msg):
    print("Message received-> " + msg.topic + " " + str(msg.payload))
    parsed_msg = json.loads(msg.payload)

    for i, file_path in enumerate(parsed_msg["files"]):
        # The trailing video is the first file
        if i == 0 and skip_trailing == 1:
            continue

        print("processing " + file_path)
        try:
            print("downloading")
            ftp = FTP(cam_ip)
            ftp.login(user=ftp_user, passwd=ftp_pass)

            localfile = open(filename, 'wb')
            ftp.retrbinary('RETR /tmp/sd/record/' + file_path, localfile.write, 1024)
            ftp.quit()
            localfile.close()

            print("uploading to slack")
            upload_to_slack()
        except Exception as e:
            print("failed to process file " + file_path + ":" + e)
    print("complete")


client = mqtt.Client(topic + "slack_file_pusher")
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker, broker_port)
client.loop_forever()
