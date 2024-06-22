
from lib.mqtt import MQTTClient   # For use of MQTT protocol to talk to Adafruit IO
import lib.keys as keys

def connect():
    # Use the MQTT protocol to connect to Adafruit IO
    client = MQTTClient(keys.AIO_CLIENT_ID, keys.AIO_SERVER, keys.AIO_PORT, keys.AIO_USER, keys.AIO_KEY)

    # Subscribed messages will be delivered to this callback
    #client.set_callback(mqtt_comms.sub_cb) # Don't need it, we only send data.
    client.connect()
    #client.subscribe(keys.AIO_LIGHTS_FEED)
    print("Connected to %s" % (keys.AIO_SERVER))
    #print("Connected to %s, subscribed to %s topic" % (keys.AIO_SERVER, keys.AIO_LIGHTS_FEED))

    return client

def send_number(client, number, topic, verbose):

    if verbose:
        print("Publishing: {0} to {1} ... ".format(number, topic), end='')

    try:
        client.publish(topic=topic, msg=str(number))
        if verbose:
            print("DONE")
        return 1
    except Exception as e:
        if verbose:
            print("FAILED")
        return -1

def disconnect(client):
    client.disconnect()
