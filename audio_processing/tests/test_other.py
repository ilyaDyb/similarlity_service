import datetime
import sys
import os
from sklearn.decomposition import PCA
import numpy as np
from pydub.audio_segment import AudioSegment

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from audio_processing.features_extraction.audio_analysis import AudioProcessing
# from audio_processing.tests.test_similar_tracks import get_signatures
from audio_processing.tests.conftest import PATH_SIMILAR

def determine_optimal_components(signature_matrix: np.ndarray, variance_threshold: float = 0.95) -> int:
    """
    Определяет оптимальное количество компонент PCA, чтобы сохранить заданную долю дисперсии.
    
    :param signature_matrix: матрица векторов признаков всех аудиофайлов.
    :param variance_threshold: доля общей дисперсии, которую нужно сохранить.
    :return: оптимальное количество компонент.
    """

    pca = PCA()
    pca.fit(signature_matrix)
    cumulative_variance = np.cumsum(pca.explained_variance_ratio_)
    n_components = np.searchsorted(cumulative_variance, variance_threshold) + 1
    return n_components

# signatures = get_signatures()
# signatures_list = list(signatures.values())
# signature_matrix = np.array(signatures_list).astype('float32')
# optional_components = determine_optimal_components(signature_matrix, variance_threshold=0.99)
# print(optional_components)

def convert_mp3_to_wav(input_path, output_path):
    audio = AudioSegment.from_mp3(input_path)
    audio.export(output_path, format="wav")

def test_difference_by_duration_for_different_formats():
    audio_processing1 = AudioProcessing(PATH_SIMILAR + "example49.mp3")
    audio_processing2 = AudioProcessing(PATH_SIMILAR + "example49.wav")
    start1 = datetime.datetime.now()
    dur = audio_processing1.get_duration()
    audio_processing1.load_file(dur//2+1)
    audio_processing1.set_features_base()
    # audio_processing1.set_features_advanced()
    end1 = datetime.datetime.now()
    print(f"MP3 was loaded in: {end1-start1}")
    start2 = datetime.datetime.now()
    dur = audio_processing1.get_duration()
    audio_processing2.load_file(dur//2+1)
    audio_processing2.set_features_base()
    # audio_processing2.set_features_advanced()
    end2 = datetime.datetime.now()
    print(f"WAV was loaded in: {end2-start2}")

# def test_difference_by_duration_for_different_formats():
#     audio_processing1 = AudioProcessing(PATH_SIMILAR + "example49.mp3")
#     audio_processing2 = AudioProcessing(PATH_SIMILAR + "example49.wav")
#     res1 = features_extract_pattern(audio_processing1, "mp3")
#     res2 = features_extract_pattern(audio_processing2, "wav")
#     print(f"{res1}\n{res2}")

# def features_extract_pattern(audio, type: str):
#     start = datetime.datetime.now()
#     dur = audio.get_duration()
#     audio.load_file(dur//2+1)
#     audio.set_features_base()
#     audio.set_features_advanced()
#     end = datetime.datetime.now()
#     return f"{type} was loaded in: {end-start}"