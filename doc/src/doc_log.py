import yaml
import logging
import logging.config

try:
    with open('logging.yml', 'r') as stream:
        config = yaml.load(stream, Loader=yaml.FullLoader)

    logging.config.dictConfig(config)
    logger = logging.getLogger('awsLogger')
except FileNotFoundError as no_file:
    logger = logging.root


def doc_log(msg, tag=None, level=logging.INFO, logger=logger, **kwargs):
    if msg is None:
        raise KeyError('Must provide a msg to log')
    message = f'[{tag}] {msg}' if tag is not None else msg
    logger.log(level, message)


def debug(message):
    doc_log(message, level=logging.DEBUG)


def info(message):
    doc_log(message, level=logging.INFO)


def warn(message):
    doc_log(message, level=logging.WARN)


def error(message):
    doc_log(message, level=logging.ERROR)