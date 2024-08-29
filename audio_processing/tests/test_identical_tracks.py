from audio_processing.features_extraction.audio_analysis import AudioTools
from audio_processing.tests.conftest import PATH_IDENTICAL

def test_identical_tracks(audio_processing_func):
    filename1 = PATH_IDENTICAL + "example01.mp3"
    filename2 = PATH_IDENTICAL + "example01.wav"
    signuture1 = audio_processing_func(filename1)
    signuture2 = audio_processing_func(filename2)
    
    tools = AudioTools()
    cos_similarity = tools.get_cos_similarity(signuture1, signuture2)
    dist_euclidean = tools.get_euclidean_distance(signuture1, signuture2)
    
    assert cos_similarity >= 0.99
    assert dist_euclidean <= 0.1
