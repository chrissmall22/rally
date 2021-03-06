# Copyright 2014: Mirantis Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import logging

from oslo_config import cfg

from rally.openstack.common import log as oslogging


common_cli_opts = [cfg.BoolOpt("rally-debug",
                   default=False,
                   help="Print debugging output only for Rally. "
                   "Off-site components stay quiet.")]

CONF = cfg.CONF
CONF.register_cli_opts(common_cli_opts)

logging.RDEBUG = logging.DEBUG + 1
logging.addLevelName(logging.RDEBUG, "RALLYDEBUG")

CRITICAL = logging.CRITICAL
DEBUG = logging.DEBUG
ERROR = logging.ERROR
FATAL = logging.FATAL
INFO = logging.INFO
NOTSET = logging.NOTSET
RDEBUG = logging.RDEBUG
WARN = logging.WARN
WARNING = logging.WARNING


def setup(product_name, version="unknown"):
    dbg_color = oslogging.ColorHandler.LEVEL_COLORS[logging.DEBUG]
    oslogging.ColorHandler.LEVEL_COLORS[logging.RDEBUG] = dbg_color

    oslogging.setup(product_name, version)

    if CONF.rally_debug:
        oslogging.getLogger(None).logger.setLevel(logging.RDEBUG)


def getLogger(name="unknown", version="unknown"):

    if name not in oslogging._loggers:
        oslogging._loggers[name] = RallyContextAdapter(logging.getLogger(name),
                                                       name,
                                                       version)
    return oslogging._loggers[name]


class RallyContextAdapter(oslogging.ContextAdapter):

    def debug(self, msg, *args, **kwargs):
        self.log(logging.RDEBUG, msg, *args, **kwargs)


class ExceptionLogger(object):
    """Context that intercepts and logs exceptions.

    Usage::
        LOG = logging.getLogger(__name__)
        ...

        def foobar():
            with ExceptionLogger(LOG, "foobar warning") as e:
                return house_of_raising_exception()

            if e.exception:
                raise e.exception # remove if not required
    """

    def __init__(self, logger, warn=None):
        self.logger = logger
        self.warn = warn
        self.exception = None

    def __enter__(self):
        return self

    def __exit__(self, type_, value, traceback):
        if value:
            self.exception = value

            if self.warn:
                self.logger.warning(self.warn)
            self.logger.debug(value)
            if is_debug():
                self.logger.exception(value)
            return True


def is_debug():
    return CONF.debug or CONF.rally_debug
