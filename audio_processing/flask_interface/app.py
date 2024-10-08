import os
import sys
from flask import Flask, jsonify, request

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask_interface.functions import install_preview_by_artist, install_preview_by_album, process_tracks_in_batches

app = Flask(__name__)


@app.route('/ping', methods=['get'])
def process_track():
    return jsonify({"status": "pong"}), 200

@app.route('/install/artist', methods=['post'])
def install_by_artist():
    print("Start flask route artist", flush=True)
    data: dict = request.get_json()
    artist_id = data.get("artist_id")

    if not artist_id:
        print("No id err", flush=True)
        return jsonify({"error": "request must have artist_id"}), 400
    try:
        print("Start loading tracks", flush=True)
        install_preview_by_artist(artist_id)
    except Exception as ex:
        print(ex, flush=True)
        return jsonify({"error": str(ex)}), 500
    print("Success", flush=True)
    return '', 200
    
@app.route('/install/album', methods=['post'])
def install_by_album():
    print("Start flask route album", flush=True)
    data: dict = request.get_json()
    album_id = data.get("album_id")
    if not album_id:
        print("No id err", flush=True)
        return jsonify({"error": "request must have album_id"}), 400
    try:
        print("Start loading tracks", flush=True)
        install_preview_by_album(album_id)
    except Exception as ex:
        print(ex, flush=True)
        return jsonify({"error": str(ex)}), 500
    print("Success", flush=True)
    return '', 200

@app.route('/signatures/set', methods=['post'])
def set_signatures():
    print("Start route /signatures", flush=True)
    try:
        process_tracks_in_batches()
    except Exception as ex:
        print("Error when proccessing tracks", ex)
        return jsonify({"error": ex}), 500
    return '', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
