import os
import time

import pytest
import src.main as main
from loop.deviceclient.DeviceClient import DeviceClient


@pytest.fixture(scope='module')
def loop_server_address():
    return os.getenv('LOOP_SERVER_ADDRESS', default='localhost')


@pytest.fixture(scope='module')
def can_bus_adapter_name():
    return os.getenv('CAN_BUS_ADAPTER_NAME', default='vcan0')


@pytest.fixture(scope='module')
def robotics_catalog():
    catalog_fullname = os.path.join(os.path.dirname(__file__), '../src/catalogs/shlew-robotics.json')
    with open(catalog_fullname, 'r') as file:
        robotics_catalog = file.read().replace('\n', '').replace(' ', '')
    return robotics_catalog


@pytest.fixture(scope='module')
def radio_catalog():
    catalog_fullname = os.path.join(os.path.dirname(__file__), '../src/catalogs/kicking-bird-mfg.json')
    with open(catalog_fullname, 'r') as file:
        radio_catalog = file.read().replace('\n', '').replace(' ', '')
    return radio_catalog


@pytest.fixture(scope='module')
def loop_device_client(robotics_catalog, radio_catalog, loop_server_address):
    # Create the device client and remove all existing catalogs
    loop_device_client = DeviceClient('http://{}'.format(loop_server_address))
    loop_device_client.catalogs.delete_all()

    # Load new catalogs
    loop_device_client.catalogs.put('ShlewRobotics', robotics_catalog)
    loop_device_client.catalogs.put('KickingBirdMfg', radio_catalog)
    loop_device_client.catalogs.reload()

    # Continue with your test
    yield loop_device_client

    # Lead default catalogs after tests are finished
    loop_device_client.catalogs.load_default()


def test_when_receives_move_forward_from_radio_sends_move_forward_to_motor(loop_device_client, can_bus_adapter_name):
    radio_device = loop_device_client.create_device('RadioTransmitter', can_bus_adapter_name)
    motor_control_device = loop_device_client.create_device('MotorControlBoard', can_bus_adapter_name)

    radio_device.set_property('Rotation', 0)
    radio_device.set_property('Direction',  0)
    radio_device.set_property('Throttle', 50)

    radio_device.send_message('MotionControl')
    time.sleep(1)

    assert motor_control_device.message_counts('Movement')['receiveCount'] == 1
    assert motor_control_device.get_property('Rotation') == '0'
    assert motor_control_device.get_property('Direction') == '0'
    assert motor_control_device.get_property('Speed') == '32'


def test_when_receives_move_backward_from_radio_sends_move_backward_to_motor(loop_device_client, can_bus_adapter_name):
    radio_device = loop_device_client.create_device('RadioTransmitter', can_bus_adapter_name)
    motor_control_device = loop_device_client.create_device('MotorControlBoard', can_bus_adapter_name)

    radio_device.set_property('Rotation', -90)
    radio_device.set_property('Direction',  1)
    radio_device.set_property('Throttle', 75)

    radio_device.send_message('MotionControl')
    time.sleep(1)

    assert motor_control_device.message_counts('Movement')['receiveCount'] == 1
    assert motor_control_device.get_property('Rotation') == '-90'
    assert motor_control_device.get_property('Direction') == '1'
    assert motor_control_device.get_property('Speed') == '48'


def test_when_sensors_detect_obstacle_motor_control_movement_is_stopped(loop_device_client, can_bus_adapter_name):
    motor_control_device = loop_device_client.create_device('MotorControlBoard', can_bus_adapter_name)
    sensor_device = loop_device_client.create_device('Sensors', can_bus_adapter_name)

    motor_control_device.set_property('Rotation', '92')
    motor_control_device.set_property('Direction', '1')
    motor_control_device.set_property('Speed','48')
    sensor_device.set_property('ObstructionDetected', True)
    
    sensor_device.send_message('SensorState')

    time.sleep(1)

    assert motor_control_device.message_counts('Movement')['receiveCount'] == 1
    assert motor_control_device.get_property('Rotation') == '0'
    assert motor_control_device.get_property('Direction') == '0'
    assert motor_control_device.get_property('Speed') == '0'

def test_when_receive_sensor_state_obstruction_status_is_updated(loop_device_client, can_bus_adapter_name):
    sensors_device = loop_device_client.create_device('Sensors', can_bus_adapter_name)

    sensors_device.set_property('ObstructionDetected',  True)
    sensors_device.send_message('SensorState')

    assert main.listener.obstruction_detected

    sensors_device.set_property('ObstructionDetected',  False)
    sensors_device.send_message('SensorState')

    assert not main.listener.obstruction_detected

def test_when_obstacle_is_detected_movement_messages_are_not_sent(loop_device_client, can_bus_adapter_name):
    motor_control_device = loop_device_client.create_device('MotorControlBoard', can_bus_adapter_name)
    radio_device = loop_device_client.create_device('RadioTransmitter', can_bus_adapter_name)

    main.listener.obstruction_detected = True

    radio_device.set_property('Direction',  0)
    radio_device.send_message('MotionControl')

    time.sleep(1)

    assert motor_control_device.message_counts('Movement')['receiveCount'] == 0


def test_when_obstacle_is_detected_robot_can_move_backward(loop_device_client, can_bus_adapter_name):
    motor_control_device = loop_device_client.create_device('MotorControlBoard', can_bus_adapter_name)
    radio_device = loop_device_client.create_device('RadioTransmitter', can_bus_adapter_name)

    main.listener.obstruction_detected = True

    radio_device.set_property('Direction',  1)
    radio_device.send_message('MotionControl')

    time.sleep(1)

    assert motor_control_device.message_counts('Movement')['receiveCount'] == 1

def test_when_receive_system_state_power_status_is_updated(loop_device_client, can_bus_adapter_name):
    radio_device = loop_device_client.create_device('RadioTransmitter', can_bus_adapter_name)

    radio_device.set_property('PowerMode',  False)
    radio_device.send_message('SystemState')

    assert not main.listener.powered_on

    radio_device.set_property('PowerMode',  True)
    radio_device.send_message('SystemState')

    assert main.listener.powered_on


def test_when_radio_power_is_turned_off_the_motors_are_stopped(loop_device_client, can_bus_adapter_name):
    motor_control_device = loop_device_client.create_device('MotorControlBoard', can_bus_adapter_name)
    radio_device = loop_device_client.create_device('RadioTransmitter', can_bus_adapter_name)

    motor_control_device.set_property('Rotation', '38')
    motor_control_device.set_property('Direction', '1')
    motor_control_device.set_property('Speed','48')

    radio_device.set_property('PowerMode',  False)
    radio_device.send_message('SystemState')

    time.sleep(1)

    assert motor_control_device.message_counts('Movement')['receiveCount'] == 1
    assert motor_control_device.get_property('Rotation') == '0'
    assert motor_control_device.get_property('Direction') == '0'
    assert motor_control_device.get_property('Speed') == '0'


def test_when_radio_power_is_turned_off_no_movement_commands_are_sent_to_the_motors(loop_device_client, can_bus_adapter_name):
    motor_control_device = loop_device_client.create_device('MotorControlBoard', can_bus_adapter_name)
    radio_device = loop_device_client.create_device('RadioTransmitter', can_bus_adapter_name)

    main.listener.powered_on = False

    radio_device.send_message('MotionControl')

    time.sleep(1)

    assert motor_control_device.message_counts('Movement')['receiveCount'] == 0
