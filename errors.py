import logging

logger = logging.getLogger('log')


class OutOfMemoryError(Exception):
    def __init__(self):
        super().__init__()
        logger.error('out of memory!')


class CodeFormatError(Exception):
    def __init__(self):
        super().__init__()
        logger.error('code format error!')
