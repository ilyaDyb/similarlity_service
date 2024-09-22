from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/process_track', methods=['POST'])
def process_track():
    data = request.data()
    track_id = data.get('track_id')
    return jsonify({'status': 'success', 'track_id': track_id}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
