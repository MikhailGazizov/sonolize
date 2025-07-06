from copy import deepcopy
import numpy
from PIL import Image
import numpy as np
import enum


class ScanType(enum.Enum):
    '''
    Enumeration for scan types.
    Scan has to be done before starting to process the image as audio is a one dimensional array of integers whereas image
    is 2d or 3d (3d if breaking pixels down to rgba channel).
    '''
    HORIZONTAL = 0 # Horizontal scan takes rows of image and places them one big row one by one
    VERTICAL = 1 # Vertical scan takes columns of image, rotates 90 degrees counter-clockwise and places them in one big row
    RADIAL = 2 # TODO: Radially taking pixels from the center of the image


def byte_validate(n: int) -> int:
    '''
    Truncates the 8 bit constraint overflow
    :param n: any int
    :return: int between 0 and 255
    '''
    if n < 0:
        return 0
    elif n > 255:
        return 255
    else:
        return n


class Delay:
    '''
    Delay curcuit type.
    Defined by:
    Delay time - How much time has to pass till the signal will be repeated
    Volume - Loudness coefficient of repeated signal
    '''

    def __init__(self, delay_time: float = 0, volume: float = .5, sample_rate: int = 100):
        self.delay_time = delay_time
        self.sample_rate = sample_rate
        self.dr = int(delay_time * sample_rate)
        self.volume = volume

    def __call__(self, input_audio: numpy.ndarray) -> numpy.ndarray:
        '''
        Execution algorithm of the curcuit
        :param input_audio: Input signal
        :return: Output signal
        '''
        cur_audio = deepcopy(input_audio)
        for peak_i in range(self.dr, input_audio.shape[0]):
            cur_audio[peak_i] = byte_validate(int(input_audio[peak_i] + input_audio[peak_i - self.dr] * self.volume))
        return cur_audio


class Compressor:
    '''
    Compressor type;
    Defined by:
    Attack time - How much time it takes from the moment of signal exceeding the threshold till compression happens
    Release time - How much time has to pass since compression happened till it stops
    Threshold - Loudness value which has to be exceeded for the compressor to start to work
    Ration - Coefficient by which signal is compressed
    '''
    def __init__(self, attack_time: float = 0, release_time: float = 0, threshold: float = .5, ratio: float = 1,
                 sample_rate: int = 100):
        self.attack_time = attack_time
        self.release_time = release_time
        self.sample_rate = sample_rate
        self.ar = int(attack_time * sample_rate)
        self.rr = int(release_time * sample_rate)
        self.threshold = threshold * 255
        self.ratio = ratio

    def __call__(self, input_audio: numpy.ndarray) -> numpy.ndarray:
        '''
        Execution algorithm of the compressor
        :param input_audio: Input signal
        :return: Output signal
        '''
        cur_audio = deepcopy(input_audio)
        # cur_audio_offset = numpy.array([0]*self.ar) + cur_audio[:-self.ar]
        is_triggered = False
        for peak_i in range(input_audio.shape[0] - self.ar):
            if cur_audio[peak_i] >= self.threshold:
                cur_audio[peak_i + self.ar] = byte_validate(cur_audio[peak_i + self.ar] // self.ratio)
        return cur_audio


class Chain:
    '''
    This type aggregates functionality of a real chain: sequence of effects and execution
    '''

    def __init__(self, effects=None):
        if effects is None:
            effects = []
        self.effects = effects

    def __call__(self, input_stream: numpy.ndarray) -> numpy.ndarray:
        '''
        Execute the chain of effects in sequence
        :param input_stream: Input stream of audio/image
        :return: Output stream of audio/image with effects of the chain
        '''
        current_stream = input_stream
        for effect in self.effects:
            current_stream = effect(current_stream)
        return current_stream

    def __add__(self, Effect):
        '''
        Adds effects to the chain
        :param Effect: Instance of effect curcuit
        :return: None
        '''
        self.effects.append(Effect)
        return self

    def __sub__(self, Effect):
        '''
        Removes particular instance of effect from the chain
        :param Effect: Instance of effect curcuit
        :return: None
        '''
        self.effects.remove(Effect)


class Sonolize:
    '''
    Class sonolize is called to instantiate an Edit of image: it aggregates "low level" functions that facilitate getting the scan, inmporting and exporting the image.
    '''

    def scan_image(self) -> numpy.ndarray:
        '''
        Scans image; in other words unwraps 3-dimensional numpy arrays into 1-dimensional numpy array.
        :return: onedimensional numpy array depending on the scanning algorithm.
        '''


        # Shaping depending on scan type
        if self.scan_type == ScanType.HORIZONTAL:
            scan = self.pixels.reshape((self._depth * self._width * self._height), order='A')
        if self.scan_type == ScanType.VERTICAL:
            scan = self.pixels.reshape((self._depth * self._width * self._height), order='F')
        self.scan = scan
        return scan

    def unscan_image(self) -> numpy.ndarray:
        '''
        Unscans image; in other words wraps 1-dimensional numpy arrays into 3-dimensional numpy array.
        :return: 3-dimensional numpy array depending on the scanning algorithm.
        '''
        if self.scan_type == ScanType.HORIZONTAL:
            unscan = self.scan.reshape((self._height, self._width, self._depth), order='A')
        if self.scan_type == ScanType.VERTICAL:
            unscan = self.scan.reshape((self._height, self._width, self._depth), order='F')
        self.pixels = unscan
        return unscan

    def __init__(self, image_directory, scan_type=ScanType.HORIZONTAL, lock_alpha=True):
        self.image_directory = image_directory
        self.lock_alpha = lock_alpha
        self.scan_type = scan_type
        self.pixels = None

    def get_pixels(self):
        with Image.open(self.image_directory) as img:
            self.pixels = np.asarray(img)
            if self.lock_alpha and self.pixels.shape[2] == 4:
                self.pixels = np.delete(self.pixels, 3, 2)
            self._depth = self.pixels.shape[2]
            self._width = img.width
            self._height = img.height

    def save(self):
        '''
        Saves image to image folder
        :return: None
        '''
        self.unscan_image()
        Image.fromarray(self.pixels).save('backend/testimages/test1.png')

    @property
    def depth(self):
        '''
        Returns the depth (amount of channels) of the image.
        :return: integer representing the depth of the image.
        '''
        return self._depth

    @property
    def height(self):
        '''
        Returns the height of the image in pixels.
        :return: integer number representing the height of the image.
        '''
        return self._height

    @property
    def width(self):
        '''
        Returns the width of the image in pixels.
        :return: integer number representing the width of the image.
        '''
        return self._width


if __name__ == "__main__":
    print("""
    Please, keep in mind that this is utility and still under construction
    """)
