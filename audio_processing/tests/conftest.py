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
        audio.load_file()
        audio.set_features_base()
        # audio.set_features_advanced()
        return audio.get_file_signuture()
    return _process_audio