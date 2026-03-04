# Common Library

Shared code used by both the remote and robot projects.

## RadioProtocol.h

Contains common definitions for radio communication:
- Network ID
- Frequency
- Packet types
- Node IDs

## Usage

Include in your project:
```cpp
#include <RadioProtocol.h>
```

The library is automatically found via `lib_extra_dirs` in each project's platformio.ini.
