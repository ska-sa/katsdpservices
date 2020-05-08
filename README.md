# Common code for MeerKAT Science Data Processor services

This contains common code used by services that make up the Science Data Processor
subsystem of the MeerKAT radio telescope. It includes

- A common logging setup, which examines environment variables to configure
  some logging options and specify a server to receive logs in Graylog
  format.
- An extension to `argparse` to receive command-line options via
  [katsdptelstate](https://github.com/ska-sa/katsdptelstate).
- Signal handlers to restart the process and adjust log levels.
- Utilities to simplify integration with
  [aiomonitor](https://github.com/aio-libs/aiomonitor).
- A simple wrapper around [netifaces](https://github.com/al45tair/netifaces) to
  get the IP address of a network interface.
