import os
import sys
import time


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from audio_processing.features_extraction.audio_analysis import AudioProcessing, AudioTools
from audio_processing.flask_interface.db import get_connection, release_connection
from audio_processing.features_extraction.api_interface import SpotifyApiInterface

from typing import List, Tuple

import concurrent.futures


def get_all_preview(artist_id="1F8usyx5PbYGWxf0bwdXwA"):
    interface = SpotifyApiInterface()
    # print("album_list started")
    album_list = interface.get_all_albums_by_atrist_id(artist_id=artist_id)
    # print("album_links started")
    album_links = interface.get_links_from_albums_list(album_list)
    # print("hrefs started")
    hrefs_to_preview = interface.get_data_for_tracks(album_links)
    # # print(hrefs_to_preview)
    # print("getting data started", len(hrefs_to_preview))
    # data = interface.get_preview_tracks(hrefs_to_preview[:2])
    # print(data)
    batch_size = 10
    for i in range(0, len(hrefs_to_preview), batch_size):
        batch = hrefs_to_preview[i:i+batch_size]
        print(f"Processing batch {i // batch_size + 1}")
        data = interface.get_preview_tracks(batch)
        
        save_to_database(data)
        
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


def process_tracks_in_batches(tracks: List[Tuple[int, str]], batch_size: int = 10):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for i in range(0, len(tracks), batch_size):
            batch = tracks[i:i + batch_size]
            futures = [executor.submit(get_signatures, track) for track in batch]
            signatures = [f.result() for f in concurrent.futures.as_completed(futures)]
            save_signatures_to_db(signatures)
            time.sleep(1)


def test_db_query():
    conn = None
    cursor = None 
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
        SET ivfflat.probes = 20; -- Настройка количества списков для поиска

        SELECT
            artist_id,
            artists,
            title,
            preview_url
        FROM
            tracks
        ORDER BY
            signature <-> (SELECT signature FROM tracks WHERE id = 1)::vector
        LIMIT 20;
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

if __name__ == "__main__":
    # get_all_preview()
    # set_signatures()
    # l = [0.6146667294714513, 0.195240835493624, -0.1931475856200202, -0.3635932923481061, -0.14032236385005847, 0.20606524851720986, 0.3524743580931272, 0.11826384418308791, -0.2033363109401254, -0.32687810518738947, -0.11618845897259304, 0.18067351955896915, 0.2972834122845864, 0.10975339019457038, -0.1587959341880939, -0.24233323407696378, -0.07696347342536183, 0.1565608474594538, 0.22638084895264066, 0.09016526613311199, -0.11553293245487582, -0.16876939407268154, -0.0619380415153816, 0.09930482490544712, 0.12678078293164624, 0.05361120926172736, -0.07373863561472449, -0.1010597587758974, -0.05799416380037902, 0.03466972024800962, 0.04239310833570621, 0.03891086339560404, -0.010223747666648512, -0.01650617698202539, -0.028841272185351926, -0.009462315651495416, -0.020191964900757066, 0.026083577978030514, 0.051601168969517705, 0.054369035224022054, -0.013463007423551991, -0.0647058943167978, -0.07952133013460394, -5.882616285117839e-05, 0.08144335449098737, 0.09454886433539898, 0.005639440599846616, -0.1081769836188888, -0.1391669995369001, -0.04130324964116746, 0.1113981353254568, 0.15045001277461148, 0.03954342014667848, -0.1375285792605201, -0.1743475922859145, -0.05606502682232343, 0.1449457665562766, 0.1944789378615739, 0.0685306931981898, -0.15317895860530184, -0.20226531828667418, -0.07827062363798695, 0.15091761728253172, 0.21404096761758856, 0.08237961980558178, -0.16338813470898175, -0.22875678634160648, -0.10184064011465829, 0.1392203924093633, 0.22305322307943704, 0.09672482902306856, -0.15303683848214658, -0.23676060193398046, -0.10691833313573472, 0.1309619831360734, 0.230401538169908, 0.10993260644966005, -0.12423020102833655, -0.2298513083087792, -0.11101331388604373, 0.10942503050416089, 0.22449945985238987, 0.11114811537880583, -0.1018039700936107, -0.22396886326798027, -0.11432448242903337, 0.08043633208278483, 0.19921523418718218, 0.09893554914321027, -0.07789748164850294, -0.19976326181518267, -0.10574930570439936, 0.058251282708527585, 0.17426608403078606, 0.09306622279510812, -0.04557139895802608, -0.15659623059331973, -0.08675851819743184, 0.040792132967527865, 0.13577180093342067, 0.07608772671954919, -0.02458176587986087, -0.11086174969869393, -0.072888023022013, 0.01250852016504675, 0.07874167303338084, 0.05013742001282655, -0.012696304136443917, -0.06636232610198514, -0.058592183234330186]
    # print(len(l))
    # print(test_db_query())
    get_all_preview(artist_id="0kD3TUffiD0sPxGwygzjg7")
    tracks = get_tracks_without_signatures()
    process_tracks_in_batches(tracks)