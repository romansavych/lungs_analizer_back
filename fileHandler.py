import numpy as np
from matplotlib import pyplot as plt
from scipy.io import wavfile
import matplotlib as mpl


def drawGraphByFile(title , filepath , color):
    samplerate, data = wavfile.read(filepath)
    np.set_printoptions(threshold=np.inf)
    mpl.rcParams['agg.path.chunksize'] = 10000
    np.set_printoptions(threshold=np.inf)
    mpl.rcParams['agg.path.chunksize'] = 10000
    x = data
    median = np.median(data)
    # plotting
    plt.title(title)
    plt.xlabel("median: " + str(median))

    plt.plot(x, color)
    plt.show()

def getArrayOfValues(filepath):
    samplerate, data = wavfile.read(filepath)
    res = []

    print(data.shape)
    if len(data.shape) == 2:
        data = np.array([m[0] for m in data])

    if data.any():
        for x in data:
            res.append(x / 10000)

    return res
def drawGraphByArray(array , color , title = "title"):
    plt.title(title)
    plt.plot(np.float64(array), color)
    plt.show()


