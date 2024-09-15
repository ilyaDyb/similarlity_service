import concurrent.futures
import datetime
import sys
import os
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import concurrent
import numpy as np
from typing import List

from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3

from audio_processing.tests.conftest import PATH_SIMILAR
from audio_processing.features_extraction.audio_analysis import AudioProcessing, AudioTools

audio_tools = AudioTools()

def process_audio_file(file_path: str, 
                       use_advanced=False, 
                       normalize=False, 
                       normalization_type="z-score", 
                       features_to_use=None,
                       reduce_dimension=False,
                       n_components=50) -> str:
    """
    Process a single audio file, extract the features and return the signature.
    
    :param file_path: path to the audio file.
    :param use_advanced: whether to use advanced features or not.
    :param normalize: whether to normalize the signature.
    :param normalization_type: type of normalization (z-score, min-max).
    :param features_to_use: a dict that defines which features to extract.
    :param reduce_dimension: size reduction flag.
    :param abbreviation_method: split method("top_features", "aggregate", "dct").
    :param param_short: Parameters for the flexibility method. Examples: 'top_n': int | 'block_size': int | 'n_components': int
    :return: formatted signature string.
    """
    audio = AudioProcessing(file_path)
    duration = audio.get_duration()
    
    # Load half of the duration of the audio file
    audio.load_file(duration // 3 + 1)

    if features_to_use is None:
        features_to_use = {
            "use_mfcc": True, 
            "use_chromagram": True, 
            "use_rms": True, 
            "use_mel_spectrogram": True, 
            "use_tempo": True
        }

    audio.set_features_base(
        use_mfcc=features_to_use.get("use_mfcc", True),
        use_chromagram=features_to_use.get("use_chromagram", True),
        use_rms=features_to_use.get("use_rms", True),
        use_mel_spectrogram=features_to_use.get("use_mel_spectrogram", True),
        use_tempo=features_to_use.get("use_tempo", True)
    )
    
    if use_advanced:
        audio.set_features_advanced(
            use_spectral=features_to_use.get("use_spectral", True),
            use_zcr=features_to_use.get("use_zcr", True),
            use_tonnetz=features_to_use.get("use_tonnetz", True)
        )

    signature = audio.get_file_signature(normalize=normalize, normalization_type=normalization_type)

    if reduce_dimension:
        signature = audio_tools.reduce_with_dct(signature, n_components)

    
    return f"{os.path.basename(file_path)}\t{signature}"



def write_signatures_to_file(file_paths: List[str], output_file_path: str, 
                             use_advanced=False, normalize=False, normalization_type="z-score", 
                             features_to_use=None,
                             reduce_dimension=False, n_component=50):
    """Function to process files and write signatures to a file"""
    print("Running function write_signatures_to_file")
    
    with open(output_file_path, "w") as f:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(
                    process_audio_file, 
                    file_path, 
                    use_advanced, 
                    normalize, 
                    normalization_type, 
                    features_to_use,
                    reduce_dimension,
                    n_component,
                ) for file_path in file_paths
            ]
            
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    f.write(result + "\n")
                except Exception as exc:
                    print(f"Error processing file: {exc}")


def get_file_paths(folder_path):
    """Get all mp3 file paths from the folder"""
    return [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(".mp3")]


def get_signatures(file_path="signatures.txt"):
    """Читает сигнатуры из файла"""
    signatures = {}
    signature_cleaner = re.compile(r'[^\deE.,\-]')

    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip().split(maxsplit=1)
            if len(line) > 1:
                track_name = line[0]
                cleaned_signature = signature_cleaner.sub('', line[1])
                try:
                    signature_values = [float(value) for value in cleaned_signature.split(',') if value]
                    signatures[track_name] = signature_values
                except ValueError as e:
                    print(f"Skipping line due to error convert: {line}")
                    print(f"Error: {e}")

    return signatures


def calculate_distances(signatures, reference_track_name=None):
    """Вычисляет расстояния между сигнатурой выбранного трека и остальными"""
    track_names = list(signatures.keys())
    
    if reference_track_name is None:
        # Если трек не задан, используем первый трек в списке
        reference_track_name = track_names[0]
    
    if reference_track_name not in signatures:
        raise ValueError(f"Трек {reference_track_name} не найден в сигнатурах.")
    
    reference_signature = np.array(signatures[reference_track_name])
    
    dist_info = {}
    for track_name, signature_values in signatures.items():
        if track_name == reference_track_name:
            continue
        audio_tool = AudioTools()
        # get_cos_similarity | get_manhattan_distance
        dist = audio_tool.get_manhattan_distance(reference_signature, np.array(signature_values))
        dist_info[track_name] = dist
    
    return dist_info


def get_track_title(file_path):
    """Get track metadata (title, artist)"""
    try:
        audio = MP3(file_path, ID3=EasyID3)
        return {
            'title': audio.get('title', ['Unknown'])[0],
            'artist': audio.get('artist', ['Unknown'])[0]
        }
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return {'title': 'Unknown', 'artist': 'Unknown'}


def print_sorted_alg_results(output_file_path="signatures.txt", reference_track_name=None):
    """Выводит отсортированные результаты алгоритма"""
    signatures = get_signatures(output_file_path)
    dist_info = calculate_distances(signatures, reference_track_name)
    
    sorted_dist_info = dict(sorted(dist_info.items(), key=lambda item: item[1]))
    
    for track_name, dist in sorted_dist_info.items():
        track_normal_name = get_track_title(os.path.join(PATH_SIMILAR, track_name))
        print(f"{track_name}: {track_normal_name['title']}\nDistance: {dist}\n")


def start_tests(output_file_path: str, with_load: bool, folder_path: str,
                use_advanced=False, normalize=False, normalization_type="z-score", features_to_use=None,
                reduce_dimension=False, reference_track_name=None, n_component=50):
    """Основная функция для запуска тестов"""
    
    if with_load:
        if not output_file_path:
            raise ValueError("The specified output file path is empty")
        print("Processing files...")
        file_paths = get_file_paths(folder_path)
        
        # Используем ранее написанную функцию для записи сигнатур в файл с различными параметрами
        write_signatures_to_file(
            file_paths, output_file_path, 
            use_advanced=use_advanced, 
            normalize=normalize, 
            normalization_type=normalization_type, 
            features_to_use=features_to_use,
            reduce_dimension=reduce_dimension,
        )
    else:
        print(f"Signatures loaded from {output_file_path}")
    
    print("Starting distance calculation and printing results...\n")
    print_sorted_alg_results(output_file_path, reference_track_name)


def run_multiple_tests():
    """
    comment on what is not needed for tests, and uncomment what is needed, otherwise,
    everything will take a very long time to complete, and depending on the IDE, some answers may disappear
    """

    folder_path = PATH_SIMILAR
    output_file_path = "signatures.txt"

    print("Running test: Custom feature selection...")
    custom_features = {
        "use_mfcc": True,
        "use_chromagram": True,
        "use_rms": True,
        "use_mel_spectrogram": True,
        "use_tempo": True,
        "use_spectral": True,
        "use_zcr": True,
        "use_tonnetz": True
    }
    # reference_track_name = 'example144.mp3'
    reference_track_name = 'example26.mp3'
    # Тест без сокращения размерности
    # print("Running test without dimensionality reduction...")
    # start_tests(
    #     output_file_path=output_file_path,
    #     with_load=False,
    #     folder_path=folder_path,
    #     use_advanced=True,
    #     normalize=True,
    #     normalization_type="min-max",
    #     features_to_use=custom_features,
    #     reduce_dimension=False,
    #     reference_track_name=reference_track_name
    # )

    # Тест с сокращением размерности (метод 'top_features')
    # print("\nRunning test with dimensionality reduction (top_features)...")
    start_tests(
        output_file_path=output_file_path,
        with_load=True,
        folder_path=folder_path,
        use_advanced=True,
        normalize=True,
        normalization_type="min-max",
        features_to_use=custom_features,
        reduce_dimension=True,
        n_component=110,
        reference_track_name=reference_track_name
    )
    

if __name__ == "__main__":
    start = datetime.datetime.now()
    run_multiple_tests()
    end = datetime.datetime.now()
    print(f"Code ended in: {end-start}")

# dur // 2 + 1
# Code ended in: 0:04:15.348827 With advanced params and HOP_LENGTH=1024
# Code ended in: 0:04:33.292834 with advanced params abd HOP_LENGTH=512
# Code ended in: 0:03:51.431116 without advanced params abd HOP_LENGTH=512
# Code ended in: 0:03:50.825652 without advanced params and HOP_LENTGTH=1024

# dur // 3 + 1
# Code ended in: 0:02:52.942209 with advanced params and HOP_512 GOOD RESULT!
# Code ended in: 0:02:36.997121 with advanced and hop_512 sr=18000!!! Good result!
# Code ended in: 0:01:39.875553 wit ..................... sr=10000!!! BAD result
# Code ended in: 0:02:09.422232 ......................... sr=14000!!! better
# Code ended in: 0:02:19.165008 ......................... sr=15500!!! better

# dur = 
# start_ratio, end_ratio = 0.33, 0.66
# total_duration = audio_processing1.get_duration()
# start_time = round(total_duration * start_ratio)
# end_time = total_duration * end_ratio
# duration = round(end_time - start_time)
# Code ended in: 0:03:10.635004 with advanced params and HOP_512 BAD RESULT
