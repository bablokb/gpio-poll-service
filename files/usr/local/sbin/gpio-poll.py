#!/usr/bin/python
# --------------------------------------------------------------------------
# Script executed by systemd service for gpio-poll.service.
#
# Please edit /etc/gpio-poll.conf to configure the GPIO to monitor
# and the script to be started.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/gpio-poll-service
#
# --------------------------------------------------------------------------

import select, time, sys
import ConfigParser

# --- helper function   ----------------------------------------------------

def set_value(path, value):
  fd = open(path, 'w')
  fd.write(value)
  fd.close()
  return

# --- read configuration   ------------------------------------------------

config = ConfigParser.RawConfigParser()
config.read('/etc/gpio-poll.conf')
GPIO_NUMBER=config.get('GPIO','number')
GPIO_EDGE=config.get('GPIO','edge')
EXEC_ON_INT=config.get('GPIO','command')
gpio_dir = '/sys/class/gpio/gpio'+GPIO_NUMBER+'/'

# --- configure PIN   -----------------------------------------------------

set_value(gpio_dir + 'direction', 'in')
set_value(gpio_dir + 'edge', GPIO_EDGE)

# --- create file-handle and poll-object   --------------------------------

fd_gpio_value = open(gpio_dir + 'value', 'r')
poll_obj = select.poll()
poll_obj.register(fd_gpio_value, select.POLLPRI)

# --- main loop   ---------------------------------------------------------

while True:
  # wait for interrupt
  events = poll_obj.poll()

  # read value
  fd_gpio_value.seek(0)
  state = fd_gpio_value.read(1)

  # execute command
  sys.os.system(EXEC_ON_INT + " " + str(value) + " &")
  
