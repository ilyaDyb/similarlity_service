import os
import sys
import time


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from features_extraction.audio_analysis import AudioProcessing, AudioTools
from flask_interface.db import get_connection, release_connection
from features_extraction.api_interface import SpotifyApiInterface

from typing import List, Tuple

import concurrent.futures



def install_preview_by_artist(artist_id):
    interface = SpotifyApiInterface()
    album_list = interface.get_all_albums_by_atrist_id(artist_id=artist_id)
    album_links = interface.get_links_from_albums_list(album_list)
    hrefs_to_preview = interface.get_data_for_tracks(album_links)
    batch_size = 10
    for i in range(0, len(hrefs_to_preview), batch_size):
        batch = hrefs_to_preview[i:i+batch_size]
        print(f"Processing batch {i // batch_size + 1}")
        data = interface.get_preview_tracks_by_hrefs(batch)
        
        save_to_database(data)
        
        time.sleep(1)

def install_preview_by_album(album_id):
    interface = SpotifyApiInterface()
    json_data = interface.get_preview_tracks_from_album(album_id=album_id)
    tracks_preview = interface.get_clean_data_from_preview_json(json_data=json_data.get("items"))
    batch_size = 10
    for i in range(0, len(tracks_preview), batch_size):
        batch = tracks_preview[i:i+batch_size]
        save_to_database(data=batch)
        time.sleep(1)


def save_to_database(data):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        insert_query = """
        INSERT INTO tracks (title, artists, preview_url)
        VALUES (%s, %s, %s)
        ON CONFLICT (preview_url) DO NOTHING;
        """
        
        # Подготовка данных для вставки
        records = [
            (
                track['name'],
                ', '.join(track['artists']),
                track['preview_url']
            )
            for track in data
        ]
        
        cursor.executemany(insert_query, records)
        conn.commit()
        print(f"Inserted {cursor.rowcount} records into the database.")
        
    except Exception as e:
        print("Error inserting into database:", e)
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_connection(conn)

def get_tracks_without_signatures():
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
        SELECT id, preview_url FROM tracks
        WHERE signature IS NULL
        """

        cursor.execute(query)
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        print(e)
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_connection(conn)


def get_signatures(track: Tuple[int, str]) -> Tuple[int, str]:
    track_id, url = track
    audio = AudioProcessing(url)
    audio.load_file(is_url=True)
    audio.set_features_base()
    audio.set_features_advanced()
    signature = audio.get_file_signature(normalize=True, normalization_type="min-max")
    tools = AudioTools()
    signature = tools.reduce_with_dct(signature, n_components=110)
    return track_id, signature


def save_signatures_to_db(signatures: List[Tuple[int, str]]):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        update_query = """
        UPDATE tracks
        SET signature = %s
        WHERE id = %s
        """

        records = [(sig, track_id) for track_id, sig in signatures]

        cursor.executemany(update_query, records)
        conn.commit()
        print(f"Inserted {cursor.rowcount} signatures into the database.")
    except Exception as e:
        print("Error inserting into database:", e)
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_connection(conn)


def process_tracks_in_batches(batch_size: int = 10):
    tracks = get_tracks_without_signatures()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for i in range(0, len(tracks), batch_size):
            batch = tracks[i:i + batch_size]
            futures = [executor.submit(get_signatures, track) for track in batch]
            signatures = [f.result() for f in concurrent.futures.as_completed(futures)]
            save_signatures_to_db(signatures)
            time.sleep(1)