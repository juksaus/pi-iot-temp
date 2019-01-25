from w1thermsensor import W1ThermSensor
from time import sleep, time


def send_temperature(reading):
    pass


def post_temp():
    while true:
        try:
            for sensor in W1ThermSensor.get_available_sensors():
                reading = {"event_timestamp": time.time()}
                reading['sensor'] = sensor.id
                reading['temperature'].sensor.get_temperature()
                print(reading)
                send_temperature(reading)
        except Exception e:
            print(str(e))
            raise e
        sleep(10)



if __name__ == '__main__':
    post_temp()


