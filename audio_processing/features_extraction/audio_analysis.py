import librosa
import numpy as np
from typing import List, Optional
from scipy.spatial import distance

class AudioProcessing:
    HOP_LENGTH = 512
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


    def load_file(self) -> None:
        try:
            y, sr = librosa.load(self.filename)
            self.y = y
            self.sr = sr
        except Exception as ex:
            raise ValueError(f"Error loading file: {ex}")
        

    def set_features_base(self) -> None:
        if self.y is None or self.sr is None:
            raise ValueError("Audio file not loaded")
        
        y_harmonic, _ = librosa.effects.hpss(self.y)
        self.mfcc = librosa.feature.mfcc(y=self.y, sr=self.sr, hop_length=self.HOP_LENGTH)
        self.chromagram = librosa.feature.chroma_cqt(y=y_harmonic, sr=self.sr)

        if self.mfcc.size == 0 or self.chromagram.size == 0:
            raise ValueError("file is not contain some features")


    def set_features_advanced(self) -> None:
        if self.y is None or self.sr is None:
            raise ValueError("Audio file not loaded")
        
        self.spectral_centroid = librosa.feature.spectral_centroid(y=self.y, sr=self.sr)
        self.spectral_bandwidth = librosa.feature.spectral_bandwidth(y=self.y, sr=self.sr)
        self.zcr = librosa.feature.zero_crossing_rate(self.y)

        if self.spectral_centroid.size == 0 or self.spectral_bandwidth.size == 0 or self.zcr.size == 0:
            raise ValueError("Impossible to extract some features from file")
        

    def get_file_signuture(self) -> List[float]:
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

    def serialize_signature(self, signature_array: List[float]) -> str:
        return ','.join(map(str, signature_array))


    def deserialize_signature(self, signature_str: str) -> List[float]:
        return list(map(float, signature_str.split(',')))


    def get_cos_similarity(self, signuture1: List[float], signuture2: List[float]):
        cos_dist = distance.cosine(signuture1, signuture2)
        cos_sim = 1 - cos_dist
        return cos_sim

    def get_euclidean_distance(self, signuture1: List[float], signuture2: List[float]):
        dist = distance.euclidean(signuture1, signuture2)
        return dist



# audio = AudioProcessing(filename="audio_proccessing/tests/computing/test_audios/example01.mp3")
# audio.load_file()
# audio.set_features_base()     # 9 seconds
# audio.set_features_advanced() #
# # print(audio.__dict__)
# signuture = audio.get_file_signuture()
# signuture1 = signuture.copy()

# tools = AudioTools()
# cos_sim = tools.get_cos_similarity(signuture, signuture1)
# eucl_dist = tools.get_euclidean_distance(signuture, signuture1)
# print(cos_sim, eucl_dist)
