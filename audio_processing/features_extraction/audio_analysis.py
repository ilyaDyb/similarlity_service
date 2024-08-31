import datetime
import librosa
import numpy as np

from typing import List, Optional
from scipy.spatial import distance
from mutagen.mp3 import MP3

class AudioProcessing:
    HOP_LENGTH = 256
    N_FFT = None


    def __init__(self, filename) -> None:
        self.filename = filename

        self.y: Optional[np.ndarray] = None
        self.sr: Optional[int] = None

        self.mfcc: Optional[np.ndarray] = None
        self.chromagram: Optional[np.ndarray] = None

        self.spectral_centroid: Optional[np.ndarray] = None
        self.spectral_bandwidth: Optional[np.ndarray] = None
        self.zcr: Optional[np.ndarray] = None


    def get_duraction(self):
        return MP3(self.filename).info.length


    def load_file(self, duraction=None) -> None:
        try:
            y, sr = librosa.load(self.filename, duration=duraction)
            self.y = y
            self.sr = sr
        except Exception as ex:
            raise ValueError(f"Error loading file: {ex}")
        

    def set_features_base(self) -> None:
        if self.y is None or self.sr is None:
            raise ValueError("Audio file not loaded")
        
        y_harmonic, _ = librosa.effects.hpss(self.y)
        self.mfcc = librosa.feature.mfcc(y=self.y, sr=self.sr, hop_length=self.HOP_LENGTH, n_mfcc=10)
        # self.chromagram = librosa.feature.chroma_cqt(y=y_harmonic, sr=self.sr)
        self.chromagram = librosa.feature.chroma_stft(y=y_harmonic, sr=self.sr)

        if self.mfcc.size == 0 or self.chromagram.size == 0:
            raise ValueError("file is not contain some features")


    def set_features_advanced(self) -> None:
        """does not work correctly for similarity results"""
        if self.y is None or self.sr is None:
            raise ValueError("Audio file not loaded")
        
        self.spectral_centroid = librosa.feature.spectral_centroid(y=self.y, sr=self.sr)
        self.spectral_bandwidth = librosa.feature.spectral_bandwidth(y=self.y, sr=self.sr)
        self.zcr = librosa.feature.zero_crossing_rate(self.y)

        if self.spectral_centroid.size == 0 or self.spectral_bandwidth.size == 0 or self.zcr.size == 0:
            raise ValueError("Impossible to extract some features from file")
        

    def get_file_signature(self) -> List[float]:
        if self.mfcc is None or self.chromagram is None:
            raise ValueError("Base parameters were not loaded")
        
        mfcc_mean = np.mean(self.mfcc, axis=1)
        mfcc_std = np.std(self.mfcc, axis=1)

        chroma_mean = np.mean(self.chromagram, axis=1)
        chroma_std = np.std(self.chromagram, axis=1)

        signature = np.hstack([
            mfcc_mean, mfcc_std, 
            chroma_mean, chroma_std
        ])

        if self.spectral_centroid is not None:
            spectral_centroid_mean = np.mean(self.spectral_centroid, axis=1)
            signature = np.hstack([signature, spectral_centroid_mean])

        if self.spectral_bandwidth is not None:
            spectral_bandwidth_mean = np.mean(self.spectral_bandwidth, axis=1)
            signature = np.hstack([signature, spectral_bandwidth_mean])

        if self.zcr is not None:
            zcr_mean = np.mean(self.zcr, axis=1)
            signature = np.hstack([signature, zcr_mean])

        return signature.tolist()


class AudioTools:
    """
    Cosine Similarity  is good for assessing the overall direction of features, but may be less sensitive to large differences in amplitude.
    Euclidean Distance and Manhattan Distance show the overall difference and can be good metrics for roughly assessing differences.
    Chebyshev Distance is good if you want to know the maximum individual difference between features.

    Cosine Similarity  подходит для оценки общего направления признаков, но может быть менее чувствительным к сильным различиям в амплитудах.
    Euclidean Distance и Manhattan Distance показывают общую разницу и могут быть хорошими метриками для грубой оценки различий.
    Chebyshev Distance подходит, если вам важно знать максимальное индивидуальное отличие между признаками.
    """

    def serialize_signature(self, signature_array: List[float]) -> str:
        return ','.join(map(str, signature_array))


    def deserialize_signature(self, signature_str: str) -> List[float]:
        return list(map(float, signature_str.split(',')))


    def get_cos_similarity(self, signature1: List[float], signature2: List[float]):
        cos_sim = distance.cosine(signature1, signature2)
        return cos_sim


    def get_euclidean_distance(self, signature1: List[float], signature2: List[float]):
        dist = distance.euclidean(signature1, signature2)
        return dist


    def get_manhattan_distance(self, signature1: List[float], signature2: List[float]):
        dist = distance.cityblock(signature1, signature2)
        return dist


    def get_chebyshev_distance(self, signature1: List[float], signature2: List[float]):
        dist = distance.chebyshev(signature1, signature2)
        return dist


    def get_minkowski_distance(self, signature1: List[float], signature2: List[float]):
        dist = distance.minkowski(signature1, signature2)
        return dist


    def get_correlation_distance(self, signature1: List[float], signature2: List[float]):
        dist = distance.correlation(signature1, signature2)
        return dist


# TODO experiment with track lengths, see how the results behave with the middle
# of the track at a certain length, just to the middle, and from the middle to the end

# filename = "audio_processing/tests/computing/test_audios/different/example01.mp3"

# audio = AudioProcessing(filename)
# from datetime import datetime
# now = datetime.now()
# duraction = audio.get_duraction()
# end = datetime.now()
# print(f"duraction: {duraction//2}\nTime: {end-now}")



# TODO use this method in future

# from concurrent.futures import ThreadPoolExecutor

# def process_file(filename):
#     audio_processor = AudioProcessing(filename)
#     # audio_processor.load_file() # 12 sec
#     # dur = audio_processor.get_duraction()
#     # audio_processor.load_file(duraction=(dur//2+1)) # 6 sec
#     # audio_processor.set_features_base()
#     return audio_processor.get_file_signature()

# PATH = "audio_processing/tests/computing/test_audios/different/"
# filenames = [PATH + "example01.mp3", PATH + "example02.mp3", PATH + "example03.mp3"]

# with ThreadPoolExecutor() as executor:
#     start = datetime.datetime.now()
#     results = list(executor.map(process_file, filenames))
#     for i, result in enumerate(results):
#         print(f"Result {i+1} for file {filenames[i]}: {result}")
#     end = datetime.datetime.now()
#     print(end - start)