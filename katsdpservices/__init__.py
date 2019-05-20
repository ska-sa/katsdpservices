"""katsdpservices library."""

# BEGIN VERSION CHECK
# Get package version when locally imported from repo or via -e develop install
try:
    import katversion as _katversion
except ImportError:
    import time as _time
    __version__ = "0.0+unknown.{}".format(_time.strftime('%Y%m%d%H%M'))
else:
    __version__ = _katversion.get_version(__path__[0])
# END VERSION CHECK


from .logging import setup_logging                     # noqa: F401
from .restart import setup_restart, restart_process    # noqa: F401
from .argparse import ArgumentParser                   # noqa: F401
from .interfaces import get_interface_address          # noqa: F401
from .aiomonitor import start_aiomonitor               # noqa: F401
