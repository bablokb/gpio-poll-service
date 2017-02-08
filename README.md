README
======

What it is
----------

This project implements a systemd service polling one or more GPIO-pins
for an interrupt (i.e. a value change). Technically, it does not poll
but uses the same named system-call, so the service does not consume
any ressources.

Installation
------------

The service is implemented in python 2 but has no additional prerequisites,
so a standard Raspbian installation will do fine.

To install the service, run

    git clone https://github.com/bablokb/gpio-poll-service
    cd gpio-poll-service
    sudo tools/install

This will install the necessary files and enable (but not start) the service.

To start the service (after proper configuration), run

    sudo systemctl start gpio-poll.service

This will also happen after a reboot automatically.

Configuration
-------------

To configure the service, you have to edit `/etc/gpio-poll.conf`. This file
has one `[GLOBAL]` section which lists the GPIOs to monitor, and which
enables to set a debug-flag. If the latter is `1`, the service will
write various messages to the system log.

For every GPIO listet in the global section, you have to add an individual
section named `[GPIOxx]` with xx being the number of the GPIO.

The service supports the following parameters for every section:

  - `active_low`: this configures the value-state of the pin if set to low
  - `edge`: detect changes. Can be either `both`, `rising` or `falling`
  - `ignore_initial`: don't report initial state
  - `command`: the command to execute on interrupt

The `command` is called with two parameters: the pin number and the current
value (`0` or `1`). Note that unless you set `ignore_initial: 1` the interrupt
will also trigger on startup and call the configured command. This will
happen in any case. E.g. even if you configured `edge: rising` and the
initial state is `0` your command will be called with a value of `0` once.


Examples
--------

In the `examples`-directory you will find a script called `gpio-shutdown`.
This script will notify the desktop user of failing power supply and
initiate shutdown. If AC comes back soon enough, the script cancels
the shutdown and informs the user accordingly. You need of course some
additional electronics to monitor the power supply and set the appropriate
GPIO-pin for the service.

For the example to work, you have to install additional packages:

   sudo apt-get update
   sudo apt-get -y install libnotify-bin notification-daemon

You should also copy the `gpio-shutdown`-script to `/usr/local/sbin`
and configure the service as documented in the script.
