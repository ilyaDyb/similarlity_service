from typing import List, Optional

import librosa
import numpy as np

from scipy.spatial import distance
from scipy.fftpack import dct
from mutagen.mp3 import MP3


class AudioProcessing:
    """v 1.2.0"""
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
        self.tempo: Optional[float] = None
        self.rms: Optional[np.ndarray] = None
        self.mel_spectrogram: Optional[np.ndarray] = None
        self.tonnetz: Optional[np.ndarray] = None

    def get_duration(self):
        return MP3(self.filename).info.length

    def load_file(self, duration=None, offset=None) -> None:
        try:
            if not offset:
                y, sr = librosa.load(self.filename, duration=duration, sr=15500)
            self.y = y
            self.sr = sr
        except Exception as ex:
            raise ValueError(f"Error loading file: {ex}")

    def set_features_base(self, use_mfcc=True, use_chromagram=True, use_rms=True, use_mel_spectrogram=True, use_tempo=True) -> None:
        """Extraction of basic features with usage options"""
        if self.y is None or self.sr is None:
            raise ValueError("Audio file not loaded")
        
        y_harmonic, _ = librosa.effects.hpss(self.y)

        if use_mfcc:
            self.mfcc = librosa.feature.mfcc(y=self.y, sr=self.sr, hop_length=self.HOP_LENGTH)
        
        if use_chromagram:
            self.chromagram = librosa.feature.chroma_stft(y=y_harmonic, sr=self.sr)

        if use_rms:
            self.rms = librosa.feature.rms(y=self.y)
        
        if use_mel_spectrogram:
            self.mel_spectrogram = librosa.feature.melspectrogram(y=self.y, sr=self.sr)

        if use_tempo:
            self.tempo, _ = librosa.beat.beat_track(y=self.y, sr=self.sr)

        if (use_mfcc and self.mfcc.size == 0) or (use_chromagram and self.chromagram.size == 0):
            raise ValueError("Some features are missing in the file")

    def set_features_advanced(self, use_spectral=True, use_zcr=True, use_tonnetz=True) -> None:
        """Advanced feature extraction with usage options"""
        if self.y is None or self.sr is None:
            raise ValueError("Audio file not loaded")

        if use_spectral:
            self.spectral_centroid = librosa.feature.spectral_centroid(y=self.y, sr=self.sr)
            self.spectral_bandwidth = librosa.feature.spectral_bandwidth(y=self.y, sr=self.sr)

        if use_zcr:
            self.zcr = librosa.feature.zero_crossing_rate(self.y)

        if use_tonnetz:
            self.tonnetz = librosa.feature.tonnetz(y=self.y, sr=self.sr)

        if (use_spectral and (self.spectral_centroid.size == 0 or self.spectral_bandwidth.size == 0)) or \
           (use_zcr and self.zcr.size == 0) or (use_tonnetz and self.tonnetz.size == 0):
            raise ValueError("Impossible to extract some advanced features")


    def __normalize_signature(self, signature: np.ndarray, normalization_type="z-score") -> np.ndarray:
        """Optional signature normalization"""
        if normalization_type == "z-score":
            return (signature - np.mean(signature)) / np.std(signature)
        elif normalization_type == "min-max":
            return (signature - np.min(signature)) / (np.max(signature) - np.min(signature))
        else:
            raise ValueError("Unknown normalization type")


    def get_file_signature(self, normalize=False, normalization_type="z-score") -> List[float]:
        """Signuture extraction"""
        if self.mfcc is None or self.chromagram is None:
            raise ValueError("Base features were not loaded")

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

        if self.rms is not None:
            rms_mean = np.mean(self.rms, axis=1)
            signature = np.hstack([signature, rms_mean])

        if self.mel_spectrogram is not None:
            mel_spectrogram_mean = np.mean(self.mel_spectrogram, axis=1)
            signature = np.hstack([signature, mel_spectrogram_mean])

        if self.tempo is not None:
            signature = np.hstack([signature, self.tempo])

        if self.tonnetz is not None:
            tonnetz_mean = np.mean(self.tonnetz, axis=1)
            signature = np.hstack([signature, tonnetz_mean])

        if normalize:
            signature = self.__normalize_signature(signature, normalization_type)

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

    def reduce_with_dct(self, signature: List[float], n_components: int) -> List[float]:
        """
        Снижает размерность вектора признаков с помощью DCT, сохраняя первые n_components коэффициентов.

        :param signature: исходный вектор признаков.
        :param n_components: количество коэффициентов для сохранения.
        :return: вектор признаков уменьшенной размерности.
        """
        signature_array = np.array(signature)
        # Применяем DCT
        dct_coefficients = dct(signature_array, norm='ortho')
        # Выбираем первые n_components коэффициентов
        reduced_signature = dct_coefficients[:n_components]
        return reduced_signature.tolist()

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