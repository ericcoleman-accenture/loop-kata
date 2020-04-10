## Backstory
Your team has entered in the Tatanka Robotics Triathlon, which is being held in 6 weeks. With the triathlon being so close, you have decided to outsource the radio transmitter/receiver, as well as all of the external sensors and motors. Here is the architecture diagram you have all agreed upon.

<img width="70%" alt="Architecture Diagram" src="./readme_resources/architecture.jpg">

The vendor for the wireless radio and receiver, Kicking Bird LLC, hasn't begun manufacturing yet. However, they have provided a catalog containing the CAN bus message structures, as well as expected behavioral patterns. They have given you a 4-5 week lead time, so waiting for their equipment to show up before starting development will put you past the deadline.

Fortunately, the robotics manufacturer, Shlew's Your Daddy Robotics, has cut their lead time down to 2 weeks, so integration with them will be much easier. They have also provided a catalog and specs for their sensors and Motor Control Board (MCB).


## Now what?
We will provide you access to a tool called LOOP. What is LOOP you ask? LOOP is a tool that can be used to simulate devices communicating over the CAN bus. For this kata, we will be using LOOP as a tool for our integration tests to simulate 3 difference devices (wireless receiver, sensor, and motor control board). LOOP can be run as a service locally (in the case of local development), or run on a separate device.


## What is a CAN bus?
The easiest way to think of a CAN bus is as an event queue sending bytes of data that form messages. While this is a very simplified view of CAN, it will suffice for this kata.


## What is a catalog?
A catalog is a JSON representation of the devices, messages, and properties that will be sent/received to/from LOOP. These can be found in `src/catalogs/`


## Is there more documentation?
The manufacturers have sent some documentation along with their catalogs. This can be found in the `documentation/` directory


## What you will need
* Access to LOOP Server and Client repositories
* Debian or Ubuntu machine (virtual machine is acceptable)


## Setting up your machine
* [Check out the setup instructions here](./readme_resources/configuring_for_vcan.md)


## User Stories
### Story 1
Accept movement commands from the radio and tell the Motor Control Board to move in a corresponding fashion (i.e. forwards, backwards, turn, stop, etc.)  
_note: Make sure you convert from throttle percentage to miles per hour_

### Story 2
Accept sensor data and take avoidance maneuvers to prevent a collision  
_note: When an object has been detected, stop and do not allow the robot to move forward_

### Story 3
Accept System State message and change power mode based on message  
_note: If power is turned off, stop all movement and ignore all Motion Control messages_


## Environment Variables
`LOOP_SERVER_ADDRESS` - The IP address or domain name of the loop server (default: localhost)  
`CAN_BUS_ADAPTER_NAME` - Name of the CAN bus adapter the messages should be communicating on (default: vcan0)


## Useful tips
### Bits
Since you will be using bit manipulation, it is important to understand how to read the bits. Let's use an example:

You have a message, 0x21. How does this get represented in bits?

```
0x21 = 0010 0001
       ^       ^--- bit 7
       bit 0
```

_note: For this kata, we will always be using Big Endian. Little Endian is not necessary to understand at this time_

_note 2: When sending a message using the python can utility, the data attribute looks like [byte2, byte1, byte0], which is what the message looks like on the CAN bus_


### Checking hex values
When you are checking a CAN message, it may be more useful to compare to the hex value than the integer representation. Example:  
`assert my_hex_value == 128` can be kinda strange, since the intent is to actually check the hex value  
`assert my_hex_value == 0x80` is much easier to understand (the left-most bit should be high)
