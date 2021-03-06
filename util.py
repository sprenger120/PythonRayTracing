import numpy as np
import numbers


def clipColor(color) :
    if not isColor(color) : # todo remove for production
        raise Exception()
    return np.minimum(np.maximum(color, [0.0, 0.0, 0.0]), [1.0, 1.0, 1.0])


# has tests
def isColor(color) :
    return len(color) == 3  \
           and isinstance(color[0], numbers.Number) \
           and isinstance(color[1], numbers.Number) \
           and isinstance(color[2], numbers.Number)

def formatSeconds(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%dh %02dm %02ds" % (h, m, s)