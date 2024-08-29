from audio_processing.features_extraction.audio_analysis import AudioTools

def test_absolutely_different_tracks(audio_processing):
    signuture1 = audio_processing("path/to/track1.mp3")
    signuture2 = audio_processing("path/to/completely_different_track.mp3")
    
    tools = AudioTools()
    cos_similarity = tools.get_cos_similarity(signuture1, signuture2)
    dist_euclidean = tools.get_euclidean_distance(signuture1, signuture2)
    
    assert cos_similarity <= 0.1
    assert dist_euclidean >= 10.0
