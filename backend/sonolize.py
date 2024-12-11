from copy import deepcopy
import numpy
from PIL import Image
import numpy as np
import enum



class ScanType(enum.Enum):
    HORIZONTAL = 0
    VERTICAL = 1
    RADIAL = 2

def byte_validate(n: int):
    if n < 0:
        return 0
    elif n > 255:
        return 255
    else:
        return n

class Delay:

    def __init__(self, delay_time: float = 0, volume : float = .5, sample_rate: int = 100):
        self.delay_time = delay_time
        self.sample_rate = sample_rate
        self.dr = int(delay_time*sample_rate)
        self.volume = volume

    def __call__(self, input_audio: numpy.ndarray):
        cur_audio = deepcopy(input_audio)
        for peak_i in range(self.dr, input_audio.shape[0]):
            cur_audio[peak_i] = byte_validate(int(input_audio[peak_i] + input_audio[peak_i - self.dr]*self.volume))
        return cur_audio

class Compressor:

    def __init__(self, attack_time: float = 0, release_time: float = 0, threshold : float = .5, ratio: float = 1, sample_rate: int = 100):
        self.attack_time = attack_time
        self.release_time = release_time
        self.sample_rate = sample_rate
        self.ar = int(attack_time*sample_rate)
        self.rr = int(release_time * sample_rate)
        self.threshold = threshold*255
        self.ratio = ratio


    def __call__(self, input_audio: numpy.ndarray):
        cur_audio = deepcopy(input_audio)
        #cur_audio_offset = numpy.array([0]*self.ar) + cur_audio[:-self.ar]
        is_triggered = False
        for peak_i in range(input_audio.shape[0] - self.ar):
            if cur_audio[peak_i] >= self.threshold:
                cur_audio[peak_i + self.ar] = byte_validate(cur_audio[peak_i + self.ar]//self.ratio)
        return cur_audio



class Chain:

    def __init__(self, effects: list = []):
        self.effects = effects

    def __call__(self, input_stream):
        current_stream = input_stream
        for effect in self.effects:
            current_stream = effect(current_stream)
        return current_stream

class Sonolize:

    def _scan_image(self):
        if self.scan_type == ScanType.HORIZONTAL:
            scan = self.pixels.reshape((self._depth * self._width * self._height), order='A')
        if self.scan_type == ScanType.VERTICAL:
            scan = self.pixels.reshape((self._depth * self._width * self._height), order='F')
        return scan

    def _unscan_image(self):
        if self.scan_type == ScanType.HORIZONTAL:
            unscan = self.scan.reshape((self._height,self._width,  self._depth), order='A')
        if self.scan_type == ScanType.VERTICAL:
            unscan = self.scan.reshape(( self._height,self._width, self._depth), order='F')
        return unscan

    def __init__(self, image_directory, scan_type=ScanType.HORIZONTAL, lock_alpha = True):
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

if __name__ == "__main__":

    print("""
    Please, keep in mind that this is utility and still under construction
    """)


