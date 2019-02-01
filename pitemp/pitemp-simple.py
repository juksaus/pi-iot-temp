import datetime
import json
import uuid

from w1thermsensor import W1ThermSensor
from w1thermsensor import errors


# This is an example which will only print the sensor values

# Converting the payload to JSON
def to_json(identifier, measurements, event_ts):
    record = {
        'id': identifier,
        'ts': event_ts,
        'data': measurements
    }
    return json.dumps(record)


# W1ThermSensor reading the temperatures from all available sensors
def read_temperatures():
    temperatures = []
    for sensor in W1ThermSensor.get_available_sensors():
        try:
            measures = {'sensor': sensor.id, 'temperature': sensor.get_temperature()}
            temperatures.append(measures)
        except errors.SensorNotReadyError as e:
            print("Skipping measure as sensor not ready")

    return temperatures


def main():
    event_ts = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    measurements = read_temperatures()
    identifier = str(uuid.uuid4())
    payload = to_json(identifier, measurements, event_ts)
    print(payload)


if __name__ == '__main__':
    main()
