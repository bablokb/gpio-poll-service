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

import select, os, sys, syslog
import ConfigParser

# --- helper functions   ---------------------------------------------------

""" write a value to the given path """

def set_value(path, value):
  fd = open(path, 'w')
  fd.write(value)
  fd.close()
  return

# --------------------------------------------------------------------------

""" return the array of the configured GPIO numbers """

def get_gpios(cparser):
  gpios = cparser.get('GLOBAL','gpios')
  return [entry.strip() for entry in gpios.split(',')]

# --------------------------------------------------------------------------

""" parse configuration """

def get_config(cparser,gpios):
  info = {}
  for gpio in gpios:
    section = 'GPIO'+gpio
    command = cparser.get(section,'command')
    edge    = cparser.get(section,'edge')
    act_low = cparser.get(section,'active_low')
    ig_init = cparser.get(section,'ignore_inital')
    info[gpio] = {'command': command,
                  'edge': edge,
                  'ig_init': ig_init,
                  'act_low': act_low}
  return info

# --------------------------------------------------------------------------

""" configure GPIOs """

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

# --------------------------------------------------------------------------

""" setup poll-object and register file-descriptors """

def setup_poll(info):
  poll_obj = select.poll()
  fdmap = {}
  for num in info:
    gpio_dir  = '/sys/class/gpio/gpio'+num+'/'
    fd  = open(gpio_dir + 'value', 'r')
    fno = fd.fileno()
    fdmap[fno] = { 'num': num, 'fd': fd }   # keep ref to fd to prevent
    poll_obj.register(fd,select.POLLPRI)    # garbage collection
  return poll_obj, fdmap

# --- main program   ------------------------------------------------------

syslog.openlog("gpio-poll")
parser = ConfigParser.RawConfigParser()
parser.read('/etc/gpio-poll.conf')

gpios = get_gpios(parser)
syslog.syslog("GPIOs: " + gpios)

info = get_config(parser,gpios)

setup_pins(info)
poll_obj, fdmap = setup_poll(info)

# --- main loop   ---------------------------------------------------------

while True:
  # wait for interrupt
  poll_result = poll_obj.poll()

  # read values
  for (fd,event) in poll_result:
    syslog.syslog("processing fd %s (event: %d)" % (fd,event))
    os.lseek(fd,0,os.SEEK_SET)
    state = os.read(fd,1)

    # get gpio-number from filename
    num = fdmap[fd]['num']
    syslog.syslog("state[%d]: %d" % (num,state))

    # execute command
    command = info[num]['command']
    syslog.syslog("executing %s" % command)
    os.system(command + " " + num + " " + str(state) + " &")
