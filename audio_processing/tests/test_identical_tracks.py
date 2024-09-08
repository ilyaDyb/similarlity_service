from audio_processing.features_extraction.audio_analysis import AudioTools
from audio_processing.tests.conftest import PATH_IDENTICAL


def test_identical_tracks(audio_processing_func):
    filename1 = PATH_IDENTICAL + "example01.mp3"
    filename2 = PATH_IDENTICAL + "example02.mp3"
    signature1 = audio_processing_func(filename1)
    signature2 = audio_processing_func(filename2)
    
    tools = AudioTools()
    cos_similarity = tools.get_cos_similarity(signature1, signature2)
    dist_euclidean = tools.get_euclidean_distance(signature1, signature2)
    print(f"cos_similarity: {cos_similarity}")
    print(f"dist_euclidean: {dist_euclidean}")
    assert cos_similarity <= 0.1
    assert dist_euclidean <= 0.1
