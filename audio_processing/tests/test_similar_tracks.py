import concurrent.futures
import datetime
import sys
import os
import re
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import concurrent
import numpy as np
from typing import List

from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3

from audio_processing.tests.conftest import PATH_SIMILAR
from audio_processing.features_extraction.audio_analysis import AudioProcessingBeta, AudioTools


def process_audio_file(file_path: str, 
                       use_advanced=False, 
                       normalize=False, 
                       normalization_type="z-score", 
                       features_to_use=None) -> str:
    """
    Process a single audio file, extract the features and return the signature.
    
    :param file_path: path to the audio file.
    :param use_advanced: whether to use advanced features or not.
    :param normalize: whether to normalize the signature.
    :param normalization_type: type of normalization (z-score, min-max).
    :param features_to_use: a dict that defines which features to extract.
    :return: formatted signature string.
    """
    audio = AudioProcessingBeta(file_path)
    duration = audio.get_duration()
    
    # Load half of the duration of the audio file
    audio.load_file(duration // 2 + 1)

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
    
    return f"{os.path.basename(file_path)}\t{signature}"



def write_signatures_to_file(file_paths: List[str], output_file_path: str, 
                             use_advanced=False, normalize=False, normalization_type="z-score", 
                             features_to_use=None):
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
                    features_to_use
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
    """Read signatures from the file"""
    signatures = {}
    signature_cleaner = re.compile(r'[^\d.,\-]')

    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip().split(maxsplit=1)
            if len(line) > 1:
                track_name = line[0]
                cleaned_signature = signature_cleaner.sub('', line[1])
                try:
                    signature_values = [float(value) for value in cleaned_signature.split(',')]
                    signatures[track_name] = signature_values
                except ValueError:
                    print(f"Skipping line due to error convert: {line}")

    return signatures


def calculate_distances(signatures):
    """Calculate Euclidean distance between track signatures"""
    track_names = list(signatures.keys())
    first_track = track_names[0]
    first_signature = np.array(signatures[first_track])

    dist_info = {}
    for track_name, signature_values in signatures.items():
        if track_name == first_track:
            continue
        audio_tool = AudioTools()  # Using AudioTools class
        # cos_similarity, manhattan_distance are good, but need to ask other people about their opinions
        dist = audio_tool.get_manhattan_distance(first_signature, np.array(signature_values))
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


def print_sorted_alg_results(output_file_path="signatures.txt"):
    """Print sorted algorithm results"""
    signatures = get_signatures(output_file_path)
    dist_info = calculate_distances(signatures)

    sorted_dist_info = dict(sorted(dist_info.items(), key=lambda item: item[1]))

    for track_name, dist in sorted_dist_info.items():
        track_normal_name = get_track_title(PATH_SIMILAR + track_name)
        print(f"{track_name}: {track_normal_name['title']}\nDistance: {dist}\n")


def start_tests(output_file_path: str, with_load: bool, folder_path: str,
                use_advanced=False, normalize=False, normalization_type="z-score", features_to_use=None):
    """Main function to start tests"""
    
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
            features_to_use=features_to_use
        )
    else:
        print(f"Signatures loaded from {output_file_path}")
    
    print("Starting distance calculation and printing results...\n")
    print_sorted_alg_results(output_file_path)


def run_multiple_tests():
    """
    comment on what is not needed for tests, and uncomment what is needed, otherwise,
    everything will take a very long time to complete, and depending on the IDE, some answers may disappear
    """

    folder_path = PATH_SIMILAR
    output_file_path = "signatures.txt"

    # Сценарий 1: Базовые функции без нормализации
    # print("Running test 1: Basic features without normalization...")
    # start = datetime.datetime.now()
    # start_tests(output_file_path, with_load=True, folder_path=folder_path, 
    #             use_advanced=False, normalize=False)
    # end = datetime.datetime.now()
    # print(f"Completed in {end-start}")

    # # Сценарий 2: Расширенные функции с нормализацией z-score
    # print("Running test 2: Advanced features with z-score normalization...")
    # start_tests(output_file_path, with_load=True, folder_path=folder_path, 
    #             use_advanced=True, normalize=True, normalization_type="z-score")

    # # Сценарий 3: Только базовые функции с min-max нормализацией
    # print("Running test 3: Basic features with min-max normalization...")
    # start_tests(output_file_path, with_load=True, folder_path=folder_path, 
    #             use_advanced=False, normalize=True, normalization_type="min-max")

    # # Сценарий 4: Пользовательская выборка функций (с выбором конкретных опций)
    print("Running test 4: Custom feature selection...")
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
    start_tests(output_file_path, with_load=False, folder_path=folder_path, 
                use_advanced=True, normalize=True, normalization_type="min-max",#"z-score", 
                features_to_use=custom_features)
#58
# use_advenced = true, normalize=true/type="min-max"
    # custom_features = {
    #     "use_mfcc": True,
    #     "use_chromagram": True,
    #     "use_rms": False,
    #     "use_mel_spectrogram": False,
    #     "use_tempo": False,
    #     "use_spectral": False,
    #     "use_zcr": False,
    #     "use_tonnetz": False
    # }
# example52.mp3: Внутренности в кейсе
# Distance: 0.20490456319711448

# example80.mp3: Я Потратил Ночь На Поиск
# Distance: 0.23026421778431533

# example21.mp3: Краснодарский край
# Distance: 0.2363582485884195

# example53.mp3: ММ
# Distance: 0.2502759023046886

# example64.mp3: Твоё место
# Distance: 0.2579327834742623

# example67.mp3: Кто-Нибудь Знает, О Чем Эта Песня?
# Distance: 0.2788736059876297
#58
#     start_tests(output_file_path, with_load=False, folder_path=folder_path, 
#                 use_advanced=True, normalize=False, normalization_type="min-max",#"z-score", 
#                 features_to_use=custom_features)
#     custom_features = {
#         "use_mfcc": True,
#         "use_chromagram": True,
#         "use_rms": True,
#         "use_mel_spectrogram": True,
#         "use_tempo": True,
#         "use_spectral": True,
#         "use_zcr": True,
#         "use_tonnetz": True
#     }
# example63.mp3: Может Расскажешь, Что Ты Чувствуешь (Главные Ворота)
# Distance: 0.08437524242000398

# example69.mp3: Откровение успешного человека
# Distance: 0.11191952472650282

# example94.mp3: Печаль Cо Знаком 8
# Distance: 0.1467269898691925

# example92.mp3: Такими, Как Сейчас (Время Гасить Свечи)
# Distance: 0.18012658723395925

# example64.mp3: Твоё место
# Distance: 0.1833653583982515

# example57.mp3: Взглянем В Глаза Правде
# Distance: 0.2016821913932027

# example85.mp3: Никогда Опять
# Distance: 0.22980699157910786


#58
    # custom_features = {
    #     "use_mfcc": True,
    #     "use_chromagram": True,
    #     "use_rms": True,
    #     "use_mel_spectrogram": True,
    #     "use_tempo": True,
    #     "use_spectral": False,
    #     "use_zcr": False,
    #     "use_tonnetz": False
    # }
    # start_tests(output_file_path, with_load=False, folder_path=folder_path, 
    #             use_advanced=False, normalize=True, normalization_type="min-max",#"z-score", 
    #             features_to_use=custom_features)
# example33.mp3: New World
# Distance: 0.08493928804895526

# example39.mp3: ФОНК ДЛЯ ДРИФТА
# Distance: 0.1309673442788629

# example63.mp3: Может Расскажешь, Что Ты Чувствуешь (Главные Ворота)
# Distance: 0.16929594315560967

# example07.mp3: Vmeste My
# Distance: 0.18750654489857557

# example94.mp3: Печаль Cо Знаком 8
# Distance: 0.19349410139441423

# example69.mp3: Откровение успешного человека
# Distance: 0.21058361157998032

# example85.mp3: Никогда Опять
# Distance: 0.2307289953066244

# example80.mp3: Я Потратил Ночь На Поиск
# Distance: 0.2446539062065374

# example83.mp3: Конечно оригинал, заказывал из штатов
# Distance: 0.2634591308979744

# example03.mp3: ЗАХОТЕЛ (SLOWED)
# Distance: 0.2738144142492559

#58
    # custom_features = {
    #     "use_mfcc": True,
    #     "use_chromagram": True,
    #     "use_rms": False,
    #     "use_mel_spectrogram": False,
    #     "use_tempo": True,
    #     "use_spectral": False,
    #     "use_zcr": False,
    #     "use_tonnetz": False
    # }
    # start_tests(output_file_path, with_load=False, folder_path=folder_path, 
    #             use_advanced=False, normalize=True, normalization_type="min-max",#"z-score", 
    #             features_to_use=custom_features)
# example81.mp3: В Огне
# Distance: 0.281672282033585

# example16.mp3: Где ты
# Distance: 0.2899688572234463

# example54.mp3: Cadillac
# Distance: 0.3017380453208208

# example32.mp3: 9mm
# Distance: 0.3384249951870946

# example09.mp3: ЗАХОТЕЛ
# Distance: 0.3533509957231791

# example26.mp3: BAIXO (slowed)
# Distance: 0.3877132463483123

# example40.mp3: AVOID MYSELF
# Distance: 0.39656828349259116

# example72.mp3: Солярис
# Distance: 0.39781126977765946

# example02.mp3: Gde Ti
# Distance: 0.4063307777157318

# example97.mp3: Кайф Ты Поймала
# Distance: 0.4284746057608066

#58
    # custom_features = {
    #     "use_mfcc": True,
    #     "use_chromagram": True,
    #     "use_rms": False,
    #     "use_mel_spectrogram": False,
    #     "use_tempo": True,
    #     "use_spectral": True,
    #     "use_zcr": True,
    #     "use_tonnetz": False
    # }
    # start_tests(output_file_path, with_load=False, folder_path=folder_path, 
    #             use_advanced=True, normalize=True, normalization_type="min-max",#"z-score", 
    #             features_to_use=custom_features)
# example93.mp3: Пост Фактум
# Distance: 0.03218753952404753

# example40.mp3: AVOID MYSELF
# Distance: 0.03398528896359667

# example52.mp3: Внутренности в кейсе
# Distance: 0.03603994354594611

# example69.mp3: Откровение успешного человека
# Distance: 0.04050265133772532

# example50.mp3: Всему Свое Время
# Distance: 0.042242455681620016

# example96.mp3: Чёрный плащ
# Distance: 0.04230113389052345

# example21.mp3: Краснодарский край
# Distance: 0.04590131020013165

# example94.mp3: Печаль Cо Знаком 8
# Distance: 0.04929322364788831

# example56.mp3: Нет Сердца
# Distance: 0.050868284683649526

# example43.mp3: On The Creep
# Distance: 0.05812579536433911

# example63.mp3: Может Расскажешь, Что Ты Чувствуешь (Главные Ворота)
# Distance: 0.060028106439864816

# example45.mp3: MY LAST HOUR
# Distance: 0.0629985134793178

# example32.mp3: 9mm
# Distance: 0.06529123512417859

# example53.mp3: ММ
# Distance: 0.06789886977247077
# def main():
#     run_multiple_tests()
    # start_time = datetime.datetime.now()
    
    # # Example: running without signature loading and with printing distance results
    # start_tests(output_file_path="signatures.txt", with_load=True, folder_path=PATH_SIMILAR)
    
    # end_time = datetime.datetime.now()
    # print(f"Tests completed in: {end_time - start_time}")


if __name__ == "__main__":
    run_multiple_tests()
