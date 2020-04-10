import os
import can

MOTION_CONTROL_MSG_ID = 510
SYSTEM_STATE_MSG_ID = 500
SENSOR_STATE_MSG_ID = 110
MOVEMENT_MSG_ID = 100

class CanListener(can.Listener):
    def __init__(self):
        self.received_messages = []
        self.obstruction_detected = False
        self.powered_on = True

    def on_message_received(self, msg):
        self.received_messages.append(msg)

        if msg.arbitration_id == MOTION_CONTROL_MSG_ID:
            self.handle_motion_control_message(msg)

        if msg.arbitration_id == SYSTEM_STATE_MSG_ID: 
            self.handle_system_state_message(msg)

        if msg.arbitration_id == SENSOR_STATE_MSG_ID: 
            self.handle_sensor_state_message(msg)


    def handle_motion_control_message(self, msg):
        direction = msg.data[0]
        forward = bool(msg.data[1] & 0x80)
        throttle = msg.data[1] & 0x7F
        speed = self.throttle_percentage_to_mph(throttle)

        if (not self.obstruction_detected or forward > 0) and self.powered_on:
            self.send_movement_message(direction, forward, speed)

    def send_movement_message(self, direction, forward, speed):
        byte_0 = int(direction)
        byte_1 = speed

        if forward:
            byte_1 |= 0x80

        msg = can.Message(arbitration_id=MOVEMENT_MSG_ID, data=[byte_0, byte_1])

        bus.send(msg)

    def throttle_percentage_to_mph(self, throttle_percentage):
        return int(throttle_percentage * .01 * 64)

    def handle_sensor_state_message(self, msg):
       sensor_status = msg.data[0] & 0x80
       self.obstruction_detected = bool(sensor_status)

       if self.obstruction_detected: 
           self.send_movement_stop_message()

    def send_movement_stop_message(self):
        self.send_movement_message(0, 0, 0)

    def handle_system_state_message(self, msg):
       system_status = msg.data[0] & 0x80
       self.powered_on = bool(system_status)

       if not self.powered_on:
           self.send_movement_stop_message()


can_bus_adapter_name = os.getenv('CAN_BUS_ADAPTER_NAME', default='vcan0')

# Do not change these values
bus = can.interface.Bus(bustype='socketcan', channel=can_bus_adapter_name, bitrate=250000)

listener = CanListener()
notifier = can.Notifier(bus, [listener])
