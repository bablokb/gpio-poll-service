#!/usr/bin/python
# --------------------------------------------------------------------------
# Script executed by systemd service for gpio-poll.service.
#
# Please edit /etc/gpio-poll.conf to configure the GPIOs to monitor
# and the scripts to be started.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/gpio-poll-service
#
# --------------------------------------------------------------------------

import select, os, sys
import ConfigParser

# --- helper functions   ---------------------------------------------------

def set_value(path, value):
  fd = open(path, 'w')
  fd.write(value)
  fd.close()
  return

def get_gpios(cparser):
  gpios = cparser.get('GLOBAL','gpios')
  return [entry.strip() for entry in gpios.split(',')]

def get_config(cparser,gpios):
  info = {}
  for gpio in gpios:
    section = 'GPIO'+gpio
    command = cparser.get(section,'command')
    edge    = cparser.get(section,'edge')
    act_low = cparser.get(section,'active_low')
    info[gpio] = {'command': command,
                  'edge': edge,
                  'act_low': act_low};
  return info

def setup_pins(info):
  for num, entry in info.iteritems():
    edge = entry['edge']
    act_low = entry['act_low']
    gpio_root = '/sys/class/gpio/'
    gpio_dir  = gpio_root + 'gpio'+num+'/'
    if not os.path.isdir(gpio_dir):
      set_value(gpio_root + 'export', num)
      set_value(gpio_dir  + 'direction', 'in')
      set_value(gpio_dir  + 'edge', edge)
      set_value(gpio_dir  + 'active_low', act_low)

def setup_poll(info):
  poll_obj = select.poll()
  for num in info:
    gpio_dir  = '/sys/class/gpio/gpio'+num+'/'
    fd = open(gpio_dir + 'value', 'r')
    info[num]['fd'] = fd
    poll_obj.register(fd,select.POLLPRI)
  return poll_obj

# --- main program   ------------------------------------------------------

parser = ConfigParser.RawConfigParser()
parser.read('/etc/gpio-poll.conf')
gpios = get_gpios(parser)
info = get_config(parser,gpios)

setup_pins(info)
poll_obj = setup_poll(info)

# --- main loop   ---------------------------------------------------------

while True:
  # wait for interrupt
  poll_result = poll_obj.poll()
  print poll_result

  # read values
  for (fd,event) in poll_result:
      os.lseek(fd,0,os.SEEK_SET)
      state = os.read(fd,1)

      # get gpio-number from filename
      name = os.readlink('/proc/self/fd/%d' % fd)
      num  = name[-8:-6]

      # execute command
      command = info[num]['command']
      os.system(command + " " + num + " " + str(state) + " &")
