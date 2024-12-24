from abc import ABC, abstractmethod
from copy import deepcopy
import numpy
from PIL import Image
import numpy as np
import enum
from typing import Union


class ScanType(enum.Enum):
    HORIZONTAL = 0
    VERTICAL = 1
    RADIAL = 2


def byte_validate(n: int) -> int:
    """
    Validates a number to be between 0 and 255
    :param n: number to be validated
    :return: byte truncated number
    """
    if n < 0:
        return 0
    elif n > 255:
        return 255
    else:
        return n

""" Effects """


class SoundEffect(ABC):

    def __init__(self, sample_rate):
        """
        Encapsulation of the base sound effect
        :param sample_rate: amount of bytes in a sample of 1 second
        """
        self.sample_rate = sample_rate

    @abstractmethod
    def __call__(self, input_audio):
        pass

class Delay(SoundEffect):

    def __init__(self, delay_time: float = 0,
                 volume: float = .5,
                 sample_rate: int = 100):
        """
        Initializes a Delay effect with following parameters:
        :param delay_time: 'seconds' that have to pass for delay to repeat the signal
        :param volume: multiplier of volume of repeated signal
        """
        super().__init__(sample_rate)
        self.delay_time = delay_time
        self.volume = volume

        # Conversion to rates for better math
        self.dr = int(delay_time * sample_rate)

    def __call__(self, input_audio: numpy.ndarray):
        for peak_i in range(self.dr, input_audio.shape[0]):
            input_audio[peak_i] = byte_validate(int(input_audio[peak_i] + input_audio[peak_i - self.dr] * self.volume))
        return input_audio


class Compressor(SoundEffect):

    def __init__(self, attack_time: float = 0,
                 release_time: float = 0,
                 threshold: float = .5,
                 ratio: float = 1,
                 sample_rate: int = 100):
        """
        Initializes compressor with following parameters:
        :param attack_time: 'seconds' that have to pass for compressor to engage
        :param release_time:  'seconds' that have to pass for compressor to release
        :param threshold: needed volume to trigger Compressor (0 to 1)
        :param ratio: multiplier by which compressor will lower the volume on triggering
        """
        super().__init__(sample_rate)
        self.attack_time = attack_time
        self.release_time = release_time
        self.ratio = ratio
        self.threshold = threshold * 255

        # Conversion to rates for better math
        self.ar = int(attack_time * sample_rate)
        self.rr = int(release_time * sample_rate)

    def __call__(self, input_audio: numpy.ndarray):
        # cur_audio_offset = numpy.array([0]*self.ar) + cur_audio[:-self.ar]
        is_triggered = False
        for peak_i in range(input_audio.shape[0] - self.ar):
            if input_audio[peak_i] >= self.threshold:
                input_audio[peak_i + self.ar] = byte_validate(input_audio[peak_i + self.ar] // self.ratio)
        return input_audio


class Chain:

    def __init__(self, effects: list = []):
        self.effects = effects

    def __add__(self, effect: Union[Delay, Compressor]):
        """
        Pushes new effect to the chain
        :param effect: Effect
        """
        if issubclass(type(effect), SoundEffect):
            self.effects.append(effect)

    def __sub__(self, effect: Union[Delay, Compressor]):
        """
        Removes effect from the chain
        :param effect: Effect
        """
        self.effects.remove(effect)

    def __call__(self, input_stream: numpy.ndarray) -> numpy.ndarray:
        """
        Engages all effects on input signal (scan) sequentially
        :param input_stream: 1-dimensional scan of image
        :return: processed 1-dimensional scan of image
        """
        current_stream = input_stream
        for effect in self.effects:
            current_stream = effect(current_stream)
        return current_stream


class Sonolize:

    def _scan_image(self):
        """
        Scanning of image basically traverses by image bytes to get a 1-dimensional PCM-like array
        :return: Numpy array (1 dimensional)
        """
        if self.scan_type == ScanType.HORIZONTAL:
            scan = self.pixels.reshape((self._depth * self._width * self._height), order='A')
        if self.scan_type == ScanType.VERTICAL:
            scan = self.pixels.reshape((self._depth * self._width * self._height), order='F')
        return scan

    def _unscan_image(self):
        """
        Traverse of a 1-dimensional scan of a picture into its original 2-dimensional byte array
        :return: Numpy array (bidimensional)
        """
        if self.scan_type == ScanType.HORIZONTAL:
            unscan = self.scan.reshape((self._height, self._width, self._depth), order='A')
        if self.scan_type == ScanType.VERTICAL:
            unscan = self.scan.reshape((self._height, self._width, self._depth), order='F')
        return unscan

    def __init__(self, image_directory, scan_type=ScanType.HORIZONTAL, lock_alpha=True):
        """
        Initializes an object containing bytes of image in both one and two dimensions.
        :param image_directory: Directory of import
        :param scan_type: Chosen Traverse type
        :param lock_alpha: Flag that locks the alpha channel so that effect loop doesn't affect it
        """
        with Image.open(image_directory) as img:
            self.pixels = np.asarray(img)
            if lock_alpha and self.pixels.shape[2] == 4:
                self.pixels = np.delete(self.pixels, 3, 2)
            self._depth = self.pixels.shape[2]
            self._width = img.width
            self._height = img.height
        self.scan_type = scan_type
        self.scan = self._scan_image()

    def _save(self):
        Image.fromarray(self.pixels).save('testimages/test1.png')

    @property
    def depth(self):
        return self._depth

    @property
    def height(self):
        return self._height

    @property
    def width(self):
        return self._width

    def get_scan(self):
        return deepcopy(self.scan)

    def set_scan(self, new_scan: numpy.ndarray):
        if new_scan.shape == self.scan.shape:
            self.scan = new_scan
        return new_scan


if __name__ == "__main__":
    print("""
    Please, keep in mind that this is utility and still under construction
    """)
