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
    data: dict = request.get_json()
    artist_id = data.get("artist_id")
    if not artist_id:
        return jsonify({"error": "request must have atrist_id"}), 400
    try:
        install_preview_by_artist(artist_id)
    except Exception as ex:
        return jsonify({"error": ex}), 500
    return 200
    
@app.route('/install/album', methods=['post'])
def install_by_album():
    data: dict = request.get_json()
    album_id = data.get("album_id")
    if not album_id:
        return jsonify({"error": "request must have album_id"}), 400
    try:
        install_preview_by_album(album_id)
    except Exception as ex:
        return jsonify({"error": ex}), 500
    return 200

@app.route('/signatures/set', methods=['post'])
def set_signatures():
    try:
        process_tracks_in_batches()
    except Exception as ex:
        return jsonify({"error": ex}), 500
    return 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
