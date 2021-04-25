#!/usr/bin/env python

# Displays system resource usage information on an Arduino 16x2 LCD
# DEPENDECNIES (python): pyserial psutil

import datetime, os, psutil, serial, time

# file to send serial data to
file_descriptor = '/dev/ttyACM0'

# time to wait until serial port is open when initializing the connection
serial_init_interval_seconds = 6
# time between updates to the serial port
serial_update_interval_seconds = 3

def format_float_as_string(number: float, integer_digits: int, decimal_digits: int) -> str:
    """ Converts a positive float into a string representation using the specified format.
        The integer part will be left-padded with spaces if 'number' has more than 'integer_digits'
        number of digits. If the number of digits of 'number' is larger than 'integer_digits', the
        integer part will be the largest integer possible with 'integer_digits' number of digits.

        TODO For negative numbers, the first integer digit will be a '-'.

        The decimal part of the resulting string will be padded with zeroes if necessary.

        Arguments
        ---------
        number : float
            The number to be formatted and converted into a string.

        integer_digits : int
            The number of digits which the integer part of the string representation will have.

        decimal_digits : int
            The number of digits which the decimal/fractional part of the string representation will have.
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

def get_load_avg():
    """ Returns a tuple of strings containing load average information to display on a 16x2 LCD.
        Output is padded with spaces to fill two rows of 16 characters each:
        '    Load AVG    '
        'XX.XX XX.XX XX.X'
        The first string in the returned tuple is the first row's content,
        the second string is the second row's content.
        
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
    """ Returns a tuple of strings containing CPU usage information to display on a 16x2 LCD.
        Output is padded with spaces to fill two rows of 16 characters each:
        '   CPU  Usage   '
        'XXXX.XMHz XXX.X%'
        The first string in the returned tuple is the first row's content,
        the second string is the second row's content.
        
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
    """ Returns a tuple of strings containing memory usage information to display on a 16x2 LCD.
        Output is padded with spaces to fill two rows of 16 characters each:
        '   MEM  Usage   '
        'XX.XXXGiB XXX.X%'
        The first string in the returned tuple is the first row's content,
        the second string is the second row's content.
        
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
    """ Returns a tuple of strings containing CPU/Mainboard temperature information to display on a 16x2 LCD.
        Output is padded with spaces to fill two rows of 16 characters each:
        'CPU  Temp XXX.XC'
        'MoBo Temp XXX.XC'
        The first string in the returned tuple is the first row's content,
        the second string is the second row's content.
        
    """
    # each call returns a float
    cpu_temp = psutil.sensors_temperatures().get('k10temp')[0].current
    mobo_temp = psutil.sensors_temperatures().get('thinkpad')[0].current

    output = (
        'CPU  Temp {}C'.format(format_float_as_string(cpu_temp, 3, 1)),
        'MoBo Temp {}C'.format(format_float_as_string(mobo_temp, 3, 1))
    )

    return output

def get_uptime():
    """ Returns a tuple of strings containing system uptime information to display on a 16x2 LCD.
        Output is padded with spaces to fill two rows of 16 characters each:
        '     Uptime     '
        'XXXX d XX h XX m'
        The first string in the returned tuple is the first row's content,
        the second string is the second row's content.
        
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

# open the serial port
arduino = serial.Serial(port=file_descriptor, baudrate=9600)
time.sleep(serial_init_interval_seconds)


# begin continuous loop
while True:
    cpu_usage_display = get_cpu_usage()
    arduino.write(bytes(cpu_usage_display[0] + cpu_usage_display[1], 'utf-8'))
    time.sleep(serial_update_interval_seconds)

    load_avg_display = get_load_avg()
    arduino.write(bytes(load_avg_display[0] + load_avg_display[1], 'utf-8'))
    time.sleep(serial_update_interval_seconds)

    mem_usage_display = get_memory_usage()
    arduino.write(bytes(mem_usage_display[0] + mem_usage_display[1], 'utf-8'))
    time.sleep(serial_update_interval_seconds)

    uptime_display = get_uptime()
    arduino.write(bytes(uptime_display[0] + uptime_display[1], 'utf-8'))
    time.sleep(serial_update_interval_seconds)

    temp_display = get_cpu_mobo_temperature()
    arduino.write(bytes(temp_display[0] + temp_display[1], 'utf-8'))
    time.sleep(serial_update_interval_seconds)
