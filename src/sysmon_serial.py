#!/usr/bin/env python

# Displays system resource usage information on an Arduino 16x2 LCD
# DEPENDECNIES (python): pyserial psutil

import datetime, os, psutil, serial, time
from typing import Tuple

# file to send serial data to
file_descriptor = '/dev/ttyACM0'
baud_rate = 9600

# time to wait until serial port is open after initializing the connection
serial_init_interval_seconds = 6
# time between updates to the serial port
serial_update_interval_seconds = 3


def format_float_as_string(number: float, integer_digits: int, decimal_digits: int) -> str:
    """ Converts a float into its string representation according to the arguments.

        The integer part of the resulting string will contain exactly 'integer_digits' number of
        characters. Excess space is padded with blank spaces. If 'number' is larger than the largest
        number that can be represented with 'integer_digits' number of digits, the largest number
        is used. This behaviour is analogous for negative numbers.

        The decimal part of the resulting string will contain exactly 'decimal_digits' number of
        characters. Excess space is padded with zeroes.

        For negative input numbers, '-' occupies one character in the integer part of the resulting
        string.

        Examples
        --------
        format_float_as_string(123.45, 4, 3) -> ' 123.450'
        format_float_as_string(123.45, 2, 1) ->   '99.4'
        format_float_as_string(-23.45, 2, 3) ->   '-9.450'

        Arguments
        ---------
        number : float
            The number to be formatted and converted into a string.

        integer_digits : int
            The number of digits which the integer part of the string representation will have.

        decimal_digits : int
            The number of digits which the decimal/fractional part of the string representation will have.

        Returns
        -------
        float_as_string : str
            A string representation of number, where the number of characters before the decimal point is exactly
            'integer_digits' and where the number of characters after the decimal point is exactly 'decimal_digits'.
    """
    # calculate smallest/largest possible integer for the given number of integer digits,
    # taking into account the '-' sign on negative numbers
    max_integer_size = pow(10, integer_digits) - 1
    min_integer_size = 0 - int(max_integer_size / 10)

    # split input number into integer part and decimal part
    integer_part = int(number)
    decimal_part = abs(number) - abs(integer_part)

    # max out integer part if number of digits is exceeded
    if number < min_integer_size:
        integer_part = min_integer_size
    if number > max_integer_size:
        integer_part = max_integer_size

    # round decimal part to 'decimal_digits' decimal places
    decimal_part = round(decimal_part, decimal_digits)
    # cast to integer
    decimal_part = int(decimal_part * pow(10, decimal_digits))

    # cast to string
    integer_part=str(integer_part)
    decimal_part=str(decimal_part)

    # pad integer_part with spaces on the left if necessary
    integer_part = integer_part.rjust(integer_digits, ' ')
    # pad decimal_part with zeroes on the right if necessary
    #decimal_part = decimal_part.rjust(decimal_digits, '0')

    return integer_part + '.' + decimal_part

def get_load_avg() -> Tuple[str]:
    """ Retrieve average load values of the system.

    Returns a tuple containing two strings, each of 16 characters in length.
    The first and second string contained are in the following format respectively:
    '    Load AVG    '
    'XX.XX XX.XX XX.X'
    
    Returns
    -------
    output : Tuple(str)
        A tuple containing two strings, each of 16 characters in length.
        They contain system information about CPU load averages.
    """
    # psutil.getloadavg() produces three floats inside a tuple
    load_all = psutil.getloadavg()

    output = (
        # first row
        '    Load AVG    ',

        # second row, with each number in the format 'XX.XX'
        # except the last number in the format 'XX.X'
        '{0} {1} {2}'.format(
            format_float_as_string(load_all[0], 2, 2),
            format_float_as_string(load_all[1], 2, 2),
            format_float_as_string(load_all[2], 2, 1)
            )
    )

    return output

def get_cpu_usage():
    """ Retrieve current CPU frequency and utilization (in percent) of the system.

    Returns a tuple containing two strings, each of 16 characters in length.
    The first and second string contained are in the following format respectively:
    '   CPU  Usage   '
    'XXXX.XMHz XXX.X%'
    
    Returns
    -------
    output : Tuple(str)
        A tuple containing two strings, each of 16 characters in length.
        They contain system information about current CPU frequency and utilization.
    """
    # each call returns a float
    cpu_freq = psutil.cpu_freq()[0]
    cpu_percent = psutil.cpu_percent(interval=None)

    output = (
        '   CPU  Usage   ',
        '{0}MHz {1}%'.format(
            format_float_as_string(cpu_freq, 4, 1),
            format_float_as_string(cpu_percent, 3, 1)
        )
    )

    return output

def get_memory_usage():
    """ Retrieve current memory usage of the system.

    Returns a tuple containing two strings, each of 16 characters in length.
    The first and second string contained are in the following format respectively:
    '   MEM  Usage   '
    'XX.XXXGiB XXX.X%'
    
    Returns
    -------
    output : Tuple(str)
        A tuple containing two strings, each of 16 characters in length.
        They contain system information about current memory usage.
    """
    # each call returns a float
    mem_used_bytes = psutil.virtual_memory().used
    mem_percent = psutil.virtual_memory().percent

    # convert mem_used_bytes to GiB
    mem_used_gib = mem_used_bytes / pow(2, 30)

    output = (
        '   MEM  Usage   ',
        '{0}GiB {1}%'.format(
            format_float_as_string(mem_used_gib, 2, 3),
            format_float_as_string(mem_percent, 3, 1)
        )
    )

    return output

def get_cpu_mobo_temperature():
    """ Retrieve current CPU and mainboard temperature readings of the system.

    Returns a tuple containing two strings, each of 16 characters in length.
    The first and second string contained are in the following format respectively:
    'CPU  Temp XXX.XC'
    'MoBo Temp XXX.XC'
    
    Returns
    -------
    output : Tuple(str)
        A tuple containing two strings, each of 16 characters in length.
        They contain information about current CPU/chipset temperature readings.
    """
    # XXX the following function calls are system-specific!
    # Use 'sensor_info.py' to determine the correct sensors for your system.
    # More info: 'https://psutil.readthedocs.io/en/latest/#psutil.sensors_temperatures'
    try:
        # works on AMD processors
        cpu_temp = psutil.sensors_temperatures().get('k10temp')[0].current
        # works on thinkpad mainboards
        mobo_temp = psutil.sensors_temperatures().get('thinkpad')[0].current

        output = (
            'CPU  Temp {}C'.format(format_float_as_string(cpu_temp, 3, 1)),
            'MoBo Temp {}C'.format(format_float_as_string(mobo_temp, 3, 1))
        )
    except TypeError:
        print("get_cpu_mobo_temperature(): Failed sensor lookup! Please enter correct sensor information.")
        output = (
            'CPU  Temp {}C'.format(" NaN "),
            'MoBo Temp {}C'.format(" NaN ")
        )

    return output

def get_uptime():
    """ Retrieve current system uptime information.

    Returns a tuple containing two strings, each of 16 characters in length.
    The first and second string contained are in the following format respectively:
    '     Uptime     '
    'XXXX d XX h XX m'
    
    Returns
    -------
    output : Tuple(str)
        A tuple containing two strings, each of 16 characters in length.
        They contain system information about the current uptime.
    """
    time_of_boot = datetime.datetime.fromtimestamp(psutil.boot_time())
    time_since_boot = datetime.datetime.now() - time_of_boot
    # timedelta internal values
    days_since_boot = time_since_boot.days
    # seconds excluding days
    seconds_since_boot = time_since_boot.seconds

    # calculate the other values as integers
    minutes_since_boot = seconds_since_boot / 60
    hours_since_boot = int(minutes_since_boot / 60)
    minutes_since_boot = int(minutes_since_boot - (hours_since_boot * 60))

    # cast to padded strings
    days_since_boot = str(days_since_boot).rjust(4, ' ')
    hours_since_boot = str(hours_since_boot).rjust(2, ' ')
    minutes_since_boot = str(minutes_since_boot).rjust(2, ' ')

    # calculate values to be inserted

    output = (
        '     Uptime     ',
        '{0} d {1} h {2} m'.format(days_since_boot, hours_since_boot, minutes_since_boot)
    )

    return output

def main():
    """ Periodically sends system information strings to the serial port.
    """

    # open the serial port
    arduino = serial.Serial(port=file_descriptor, baudrate=baud_rate)
    # wait a while until it is ready to receive
    time.sleep(serial_init_interval_seconds)

    # functions displaying different system information in the same format
    sysinfo_functions = [
        get_cpu_usage,
        get_load_avg,
        get_memory_usage,
        get_uptime,
        get_cpu_mobo_temperature
    ]

    # begin continuous loop, wait between transmissions
    while True:
        # call each function and send its output to the serial connection
        for function in sysinfo_functions:
            display_output = function()
            arduino.write(bytes(display_output[0] + display_output[1], 'utf-8'))
            time.sleep(serial_update_interval_seconds)

if __name__ == "__main__":
    main()
