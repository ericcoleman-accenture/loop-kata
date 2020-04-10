# Technical Specs

## Messages

### Movement Message
Message length: 2 bytes  
Id: 100

#### Bit 0-7 - Direction (integer)
Direction in degrees.

0 - straight  
90 - right  
-90 - left

#### Bit 8 - Forwards/Backwards (unsigned integer)
0 - forwards  
1 - backwards

#### Bits 9-15 - Speed (unsigned integer)
Absolute speed (this is a velocity measurement, not to be confused with accelaration)  
0-64 - Movement speed in tenths of miles per hour

In order to completely stop, set the speed to 0

#### Examples
[0x18, 0x00] - Move straight forward at 2.4 mph  
[0xC0, 0x2D] - Move backwards 45 degrees to the right at 6.4 mph  
[0x01, 0x5A] - Move right at 0.1 mph  
[0x26, 0xA6] - Move left at 3.8 mph  
[0x00, 0xA6] - Stop


### Sensor State Message
Message length: 1 byte  
Id: 110

#### Bit 0 - Obstruction Detected (boolean)
0 - No obstruction detected  
1 - Obstruction detected

#### Examples
[0x00] - No obstruction detected  
[0x80] - Obstruction detected
