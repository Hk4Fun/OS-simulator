import functools


def mutex_lock(func):
    """
    Mutex lock decorator for pools

    :param fun: function to decorate
    :return: wrapped function
    """

    @functools.wraps(func)
    def wrapper(*args):
        self = args[0]
        self.lock.acquire()
        value = func(*args)
        self.lock.release()
        return value

    return wrapper
