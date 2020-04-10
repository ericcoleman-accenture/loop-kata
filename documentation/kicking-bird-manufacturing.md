# Technical Specs

## Messages

### System State Message
Message length: 2 bytes  
Id: 500

#### Bit 0 - Power Mode (boolean)
Whether the system is/should be powered. Can be either transmitted (requested state) or received (current state)

true - power is either currently on or should be on  
false - power is either currently off or should be off

#### Bits 1-7 - Battery Level (unsigned integer)
Transmitted battery percentage, in 1% increments

#### Examples
[0x8C] - Power is on, 12% battery  
[0xE4] - Power is on, 100% battery  
[0x02] - Power is off, 2% battery  


### Motion Control Message
Message length: 2 bytes  
Id: 510

#### Bit 0-7 - Direction (integer)
Direction in degrees.

0 - straight  
90 - right  
-90 - left  

#### Bit 8 - Forwards/Backwards (unsigned integer)
0 - forwards  
1 - backwards

#### Bits 9-15 - Throttle (unsigned integer)
Throttle percentage  
0-100 - Throttle percentage, in one percent increments

#### Examples
[0x30, 0x00] - Move straight forward with 24% throttle  
[0xC9, 0x2D] - Move backwards 45 degrees to the right with 64% throttle  
[0x02, 0x5A] - Move right with 1% throttle  
[0x4C, 0xA6] - Move left with 38% throttle  
[0x00, 0xA6] - Stop
