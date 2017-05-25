import os
import sys
import logging
import ConfigParser
import json

# logging

logging.basicConfig(format="[%(asctime)s] %(name)s %(levelname)s: %(message)s", level=logging.INFO)
logger = logging.getLogger('cbio-importer')

# configuration

config = ConfigParser.ConfigParser()

if 'CBIO_CONFIG' not in os.environ:
    logger.error('fatal: CBIO_CONFIG environment variable is not set')
    sys.exit(1)

try:
    with open(os.environ['CBIO_CONFIG']) as fp:
        config.readfp(fp, filename=os.environ['CBIO_CONFIG'])
except IOError, e:
    logger.error("fatal: error reading configuration file: '{0}'".format(os.environ['CBIO_CONFIG']))
    logger.error(e)
    sys.exit(1)

def get_config_value(option, default):

    option_type = type(default)

    try:
        if option_type == str:
            return config.get('importer', option)
        elif option_type == int:
            return config.getint('importer', option)
        elif option_type == bool:
            return config.getboolean('importer', option)
        elif option_type == list or option_type == dict:
            return json.loads(config.get('importer', option))
    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
        return default
