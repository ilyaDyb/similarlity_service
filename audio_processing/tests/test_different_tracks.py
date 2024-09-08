from audio_processing.features_extraction.audio_analysis import AudioTools
from audio_processing.tests.conftest import PATH_DIFFERENT

# similarity_service/
#
#   pytest audio_processing/tests/test_different_tracks.py -v -s
#

def run_test_pair(audio_processing_func, filename1, filename2, expected_cos_similarity, expected_dist_euclidean):
    """Helper function to test a pair of audio tracks"""
    filename1 = PATH_DIFFERENT + filename1
    filename2 = PATH_DIFFERENT + filename2
    signature1 = audio_processing_func(filename1)
    signature2 = audio_processing_func(filename2)
    
    tools = AudioTools()
    cos_similarity = tools.get_cos_similarity(signature1, signature2)
    dist_euclidean = tools.get_euclidean_distance(signature1, signature2)
    dist_manhattan = tools.get_manhattan_distance(signature1, signature2)
    dist_chebyshev = tools.get_chebyshev_distance(signature1, signature2)
    dist_minkowski = tools.get_minkowski_distance(signature1, signature2)
    dist_correlation = tools.get_correlation_distance(signature1, signature2)
    
    print(f"Testing {filename1} vs {filename2}")
    print(f"Cosine similarity: {cos_similarity} --- {expected_cos_similarity >= cos_similarity}")
    print(f"Euclidean distance: {dist_euclidean}")
    print(f"Manhattan distance: {dist_manhattan}")
    print(f"Chebyshev distance: {dist_chebyshev}")
    print(f"Minkowski distance: {dist_minkowski}")
    print(f"Correlation distance: {dist_correlation}\n")
    
    # assert cos_similarity <= expected_cos_similarity
    assert dist_euclidean >= expected_dist_euclidean

def test_different_tracks(audio_processing_func):
    """Test different tracks with varying levels of similarity"""
    test_cases = [
        ("example05.mp3", "example06.mp3", 0.1, 10.0),
        ("example05.mp3", "example07.mp3", 0.1, 20.0),
        ("example06.mp3", "example07.mp3", 0.1, 50.0),
        ("example07.mp3", "example08.mp3", 0.1, 50.0),
    ]

    # example1 - Glamur      - Nkeeei, uniqe ...
    # example2 - Твое место  - PHARAOH
    # example3 - Hard phonk  - unknown
    # example4 - empty sound - unknown 
    
    for filename1, filename2, expected_cos_similarity, expected_dist_euclidean in test_cases:
        run_test_pair(audio_processing_func, filename1, filename2, expected_cos_similarity, expected_dist_euclidean)
