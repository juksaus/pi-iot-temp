import argparse
import datetime
import json
import uuid
from time import sleep, time

import jwt
import paho.mqtt.client as mqtt
from w1thermsensor import W1ThermSensor

# Token life in minutes
token_life = 60


def parse_args():
    parser = argparse.ArgumentParser(description=("Common line arguments for PiTemp -app"))

    parser.add_argument('--project-id', required=True, help='GCP Project ID')
    parser.add_argument('--registry-id', required=True, help='IoT Device Registry ID')
    parser.add_argument('--device-id', required=True, help='IoT Device ID')
    parser.add_argument('--region', help='Region, use europe-west1', default='europe-west1')
    parser.add_argument('--key-file', help='Key file path', default='~/.ssh/ec_private.pem')
    parser.add_argument('--ca-certs', help='Google certs path', default='~/.ssh/roots.pem')
    parser.add_argument('--google-mqtt-url', help='Google MQTT URL', default='mqtt.googleapis.com')
    parser.add_argument('--google-mqtt-port', help='Google MQTT port', choices=(8883, 443), default=8883, type=int)

    return parser.parse_args()


def create_jwt(cur_time, project_id, private_key_path):
    token = {
        'iat': cur_time,
        'exp': cur_time + datetime.timedelta(minutes=token_life),
        'aud': project_id
    }

    with open(private_key_path, 'r') as f:
        private_key = f.read()

    return jwt.encode(token, private_key, algorithm='ES256')


def error_str(rc):
    return '{}: {}'.format(rc, mqtt.error_string(rc))


def on_connect(unusued_client, unused_userdata, unused_flags, rc):
    print('on_connect', error_str(rc))


def on_publish(unused_client, unused_userdata, unused_mid):
    print('on_publish')


def to_json(sensor_id, identifier, measurements, event_ts):
    record = {
        'sensor_id': sensor_id,
        'id': identifier,
        'ts': event_ts,
        'data': measurements
    }
    return json.dumps(record)


def read_temperatures():
    temperatures = []
    for sensor in W1ThermSensor.get_available_sensors():
        measures = {'sensor': sensor.id, 'temperature': sensor.get_temperature()}
        temperatures.append(measures)
    return temperatures


def main():
    args = parse_args()
    project_id = args.project_id
    region = args.region
    registry_id = args.registry_id
    device_id = args.device_id
    key_file_path = args.key_file
    sensor_id = registry_id + "." + device_id

    _CLIENT_ID = 'projects/{}/locations/{}/registries/{}/devices/{}'.format(project_id, region, registry_id, device_id)
    _MQTT_TOPIC = '/devices/{}/events'.format(device_id)

    while True:
        client = mqtt.Client(client_id=_CLIENT_ID)
        current_time = datetime.datetime.utcnow()
        client.username_pw_set(username='unused',
                               password=create_jwt(current_time, project_id, key_file_path))

        client.on_connect = on_connect
        client.on_publish = on_publish

        client.tls_set(ca_certs=args.ca_certs)
        client.connect(args.google_mqtt_url, args.google_mqtt_port)

        jwt_renewal_time = time() + ((token_life - 1) * 60)  # setting token to expire in 59 minutes
        client.loop_start()

        # loop for the lifetime of the token
        while time() < jwt_renewal_time:
            # read, publish, sleep, repeat
            try:
                event_ts = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                measurements = read_temperatures()
                identifier = str(uuid.uuid4()) + '-' + sensor_id
                payload = to_json(sensor_id, identifier, measurements, event_ts)
                client.publish(_MQTT_TOPIC, payload, qos=1)
                sleep(10)
            except Exception as e:
                print("Something went wrong")
                print(str(e))
                raise
        client.loop_stop()


if __name__ == '__main__':
    main()
