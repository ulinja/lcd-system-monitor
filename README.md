# LCD System Monitor

Display and monitor system information on an external, microcontroller-driven 16x2 LCD.

![lcd demo](/doc/img/demo.gif)

I use this to display my headless server's current system stats on an LCD
embedded in the case. Doesn't just look awesome, it's also somewhat useful!
The LCD is driven by an Arduino Nano R3, but any 5V microcontroller with a serial
monitor should also work.

## Requirements

### Dependencies

Arduino-CLI or Ardunio IDE (just for flashing the Arduino).

Python 3.4 or above, [psutil](https://pypi.org/project/psutil/), [pyserial](https://pypi.org/project/pyserial/).

Works on all Linux or BSD machines out of the box.

It should work on Mac OS and Windows after minor modifications, namely using a
different file descriptor for the serial port (and adjusting sensors as above).
See the [psutil documentation](https://psutil.readthedocs.io/en/latest/) for more information.

### Hardware

* 1x Arduino Nano R3 (any other model should also work) + USB cable
* 1x [16x2 LCD](https://components101.com/displays/16x2-lcd-pinout-datasheet)
* 2x 10 kOhm potentiometers
* 1x 220 Ohm resistor

## Setup

Compile and upload `lcd-serial-monitor.ino` to your Arduino.
Set up the circuit like so:

![circuit diagram](/doc/img/circuit.svg)

Because they depend on your hardware, `psutil` **cannot detect your temperature
sensors automatically**. Run the included `sensor_info.py` for a list of
temperature sensors on your system, and adjust the function
`get_cpu_mobo_temperature()` in `sysmon-serial.py` accordingly.

Connect the Arduino to your server via USB and run `sysmon-serial.py`. You may
need to add the user running the script to the *uucp* group for serial data
access on Linux.
The script will start collecting a range of system monitoring information and send
it to the Arduino every 2 seconds.

## Roadmap

* `systemd` service file for `sysmon-serial.py`
* monitor network interface load
* monitor number of pending system updates
