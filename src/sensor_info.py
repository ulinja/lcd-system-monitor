#!/usr/bin/env python

# Display information about all available sensors on the current system.
# Use this script to determine the specific sensor information for psutil to
# parse inside the 'get_cpu_mobo_temperature()' function.

import pprint, psutil

print('List of available sensors:')
print()

pprint.pprint(psutil.sensors_temperatures())

print()
print('Set the correct sensor name (key in this list) and')
print('entry number (index in the list mapped to that key)')
print('inside the \'get_cpu_mobo_temperature()\' function!')
