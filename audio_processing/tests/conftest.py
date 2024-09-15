import pytest
import sys
import os

from audio_processing.features_extraction.audio_analysis import AudioProcessing

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

PATH_IDENTICAL = "audio_processing/tests/computing/test_audios/identical/"
PATH_DIFFERENT = "audio_processing/tests/computing/test_audios/different/"
PATH_SIMILAR   = "audio_processing/tests/computing/test_audios/similar/"

@pytest.fixture
def audio_processing_func():
    def _process_audio(filename):
        audio = AudioProcessing(filename)
        duration = audio.get_duration()
        audio.load_file(duration=duration // 2 - 1)
        audio.set_features_base()
        # audio.set_features_advanced()
        return audio.get_file_signature()
    return _process_audio