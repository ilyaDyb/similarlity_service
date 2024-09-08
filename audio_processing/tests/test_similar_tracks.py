import concurrent.futures
import datetime
import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import concurrent
import numpy as np
from typing import List

from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3

from audio_processing.tests.conftest import PATH_SIMILAR
from audio_processing.features_extraction.audio_analysis import AudioProcessing, AudioTools



def process_audio_file(file_path: str) -> str:
    audio = AudioProcessing(file_path)
    dur = audio.get_duraction()
    audio.load_file(dur//2 + 1)
    audio.set_features_base()
    signature = audio.get_file_signature()

    return f"{os.path.basename(file_path)}\t{signature}"


def write_signatures_to_file(file_paths: List[str], output_file_path: str):
    print("run func write_signatures_to_file")
    with open(output_file_path, "w") as f:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            features = [executor.submit(process_audio_file, file) for file in file_paths]
            for future in concurrent.futures.as_completed(features):
                try:
                    result = future.result()
                    f.write(result + "\n")
                except Exception as exc:
                    print(f"Error processing file: {exc}")


def get_file_paths(folder_path):
    file_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(".mp3")]
    return file_paths
    

def get_signatures():
    path = "signatures.txt"
    signatures = {}
    with open(path, "r", encoding="utf-8") as file:
        for _ in range(96):
            line = file.readline().strip().split(maxsplit=1)
            if len(line) > 1:
                track_name = line[0]  # Assuming the first element is the track name
                cleaned_signature = line[1].replace('[', '').replace(']', '').replace("'", "")
                signature_values = [float(value) for value in cleaned_signature.split(',')]
                signatures[track_name] = signature_values
    return signatures


def calculate_distances(signatures):
    track_names = list(signatures.keys())
    first_track = track_names[0]
    first_signature = np.array(signatures[first_track])

    dist_info = {}
    for track_name, signature_values in signatures.items():
        if track_name == first_track:
            continue
        audio_tool = AudioTools()  # Assuming you have an AudioTools class implemented
        dist = audio_tool.get_euclidean_distance(first_signature, np.array(signature_values))
        dist_info[track_name] = dist
    
    return dist_info



def get_track_title(file_path):
    try:
        audio = MP3(file_path, ID3=EasyID3)
        return {
            'title': audio.get('title', ['Unknown'])[0],
            'artist': audio.get('artist', ['Unknown'])[0]
        }
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return {'title': 'Unknown', 'artist': 'Unknown'}

def print_sorted_alg_results():
    signatures = get_signatures()  # ASDASDASDASDADSADS FIX
    dist_info = calculate_distances(signatures)

    sorted_dist_info = dict(sorted(dist_info.items(), key=lambda item: item[1]))

    for track_name, dist in sorted_dist_info.items():
        track_normal_name = get_track_title(PATH_SIMILAR + track_name)
        print(f"{track_name}: {track_normal_name['title']}\ndistance: {dist}\n")


def main():
    start_time = datetime.datetime.now()
    file_paths = get_file_paths(PATH_SIMILAR)
    output_file_path = "signatures.txt" # for example
    # write_signatures_to_file(file_paths=file_paths, output_file_path=output_file_path) # comment this if you already loaded file
    time.sleep(2)
    print_sorted_alg_results()
    end_time = datetime.datetime.now()
    print(f"{len(file_paths)} was loaded in: {end_time-start_time}")

if __name__ ==  "__main__":
    main()

