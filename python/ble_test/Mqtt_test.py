# python 3.11
## credits https://www.emqx.com/en/blog/how-to-use-mqtt-in-python
#https://www.hivemq.com/blog/mqtt-client-library-paho-python/
#https://www.emqx.com/en/blog/how-to-use-mqtt-in-python


#llops
#http://www.steves-internet-guide.com/loop-python-mqtt-client/


import random
import time
import time as dt
import pandas as pd
from paho.mqtt import client as mqtt_client
# import paho.mqtt.client as paho
from paho.mqtt import client as paho
import paho.mqtt.subscribe as subscribe
import json
from threading import Thread

broker ="test.mosquitto.org"#'localhost' #'broker.emqx.io'
port = 1883
# topic = "silabs/aoa/angle"
# Generate a Client ID with the publish prefix.
# client_id = f'publish-{random.randint(0, 1000)}'
# username = 'emqx'
# password = 'public'

FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60


def threaded_function(client):
    print("threaded_function entering..: ")
    client.loop_forever()
    print("threaded_function l;eaving..: ")
    # while True:
    #     print("running<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< {}".format(arg))
    #     time.sleep(1)
    #     client.loop_start()

def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos))

def on_message(client, userdata, message):
    print(message.topic+" "+str(message.qos)+" "+str(message.payload))

    if str(message.topic).startswith("24046"):
        print(f"!!!!!!{dt.time()} Received message {message.payload} on topic '{message.topic}' with QoS {message.qos}")
    if str(message.topic).startswith("623"):
        print(
            f"#######{dt.time()} Received message {message.payload} on topic '{message.topic}' with QoS {message.qos}")

# 0: Connection accepted
# 1: Connection refused because the protocol level is not supported
# 2: Connection refused because the server does not allow the client identifier
# 3: Connection refused because the MQTT service is not available
# 4: Connection refused because the username or password data is malformed
# 5: Connection refused because the client is not authorized to connect
def on_connect(client, userdata, flags, rc):
    print('CONNACK received with code %d.' % (rc))
    if (rc==0):
        client.on_message = on_message
        print("Connected to MQTT Broker!")
        # res=client.subscribe(topic='silabs/#', qos=1)
        # print('subscribe code {0}'.format(res))
        # res = client.subscribe(topic='#', qos=1)
        # print('subscribe code {0}'.format(res))
        # res = client.subscribe(topic='silabs/aoa/angle/ble-pd-0C4314F46BF4/#', qos=1)
        # print('subscribe code {0}'.format(res))
        res = client.subscribe(topic='623/#', qos=1)
        print('subscribe code {0}'.format(res))
        res = client.subscribe(topic='24046/#', qos=1)
        print('subscribe code {0}'.format(res))
        # res = client.subscribe('#', qos=1)
        # print('subscribe code {0}'.format(res))
    else:
        print("Failed to connect, return code %d\n", rc)


# def connect_mqtt():
#     client = paho.Client(client_id="local_test")
#     client.on_connect = on_connect
#     # client.on_publish = on_message
#     # client.on_subscribe = on_subscribe
#     client.connect(broker, port)
#
#     return client

def on_disconnect(client, userdata, rc):
    print("DisConnected result code "+str(rc))
    client.loop_stop()

    # print("Disconnected with result code: %s", rc)
    # reconnect_count, reconnect_delay = 0, FIRST_RECONNECT_DELAY
    # while reconnect_count < MAX_RECONNECT_COUNT:
    #     print("Reconnecting in %d seconds...", reconnect_delay)
    #     print(reconnect_delay)
    #
    #     try:
    #         client.reconnect()
    #         print("Reconnected successfully!")
    #
    #         return
    #     except Exception as err:
    #         print("%s. Reconnect failed. Retrying...", err)
    #
    #     reconnect_delay *= RECONNECT_RATE
    #     reconnect_delay = min(reconnect_delay, MAX_RECONNECT_DELAY)
    #     reconnect_count += 1
    # print("Reconnect failed after %s attempts. Exiting...", reconnect_count)


def run():
    client = paho.Client(client_id="local_test")
    client.on_connect = on_connect
    client.connect(broker, port)
    client.loop_start()
    return client

if __name__ == '__main__':

    client=run()
    thread = Thread(target = threaded_function, kwargs={'client':client},daemon=True)
    thread.start()

    # thread.join()
    print("thread finished...exiting")
    n=0
    while True:
        time.sleep(5)
        print("\n\n %d...--------------------------------------------------------------->>>>>>>>>>>>>>>>>..",n)
        n=n+1
        if n==3:
            print("STOP")
            client.loop_stop()
        if n==6:
            print("START")
            client.loop_start()
        # if n==8:
        #     print("START")
        #     client.loop_stop()
        #     thread.join()