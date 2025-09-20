from flask import Flask, request, jsonify, url_for, send_from_directory, Response, send_file
from flask_cors import CORS
import os
from datetime import datetime
from summarizer import summarize_video

app = Flask(__name__, static_url_path='/static', static_folder='static')
CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    expose_headers=["Content-Range", "Accept-Ranges"],
    allow_headers=["Range", "Content-Type"],
)

UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')
STATIC_FOLDER = os.path.join(app.root_path, 'static')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({"status": "error", "message": "No video uploaded"}), 400

    video = request.files['video']
    input_path = os.path.join(UPLOAD_FOLDER, video.filename)

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    output_filename = f"summarized_{timestamp}_{video.filename}"
    output_path = os.path.join(STATIC_FOLDER, output_filename)

    video.save(input_path)

    # Run summarizer
    summarize_video(input_path, output_path)

    # Return relative path for frontend compatibility
    video_path = f"/static/{output_filename}"

    return jsonify({
        "status": "success",
        "video_path": video_path,
        "filename": output_filename
    })


@app.route('/video/<path:filename>')
def stream_video(filename: str):
    file_path = os.path.join(STATIC_FOLDER, filename)
    if not os.path.exists(file_path):
        return jsonify({"status": "error", "message": "File not found"}), 404

    range_header = request.headers.get('Range', None)
    file_size = os.path.getsize(file_path)
    content_type = 'video/mp4'

    if not range_header:
        # Fallback full file (not ideal for large files but works without Range)
        resp = send_file(file_path, mimetype=content_type, as_attachment=False, conditional=True)
        resp.headers.add('Accept-Ranges', 'bytes')
        return resp

    # Parse Range header: e.g. 'bytes=0-'
    try:
        bytes_range = range_header.strip().split('=')[1]
        start_str, end_str = bytes_range.split('-')
        start = int(start_str) if start_str else 0
        end = int(end_str) if end_str else file_size - 1
        end = min(end, file_size - 1)
        if start > end or start >= file_size:
            return Response(status=416)
    except Exception:
        # Malformed range header; serve full content
        resp = send_file(file_path, mimetype=content_type, as_attachment=False, conditional=True)
        resp.headers.add('Accept-Ranges', 'bytes')
        return resp

    chunk_size = (end - start) + 1
    with open(file_path, 'rb') as f:
        f.seek(start)
        data = f.read(chunk_size)

    rv = Response(data, 206, mimetype=content_type, direct_passthrough=True)
    rv.headers.add('Content-Range', f'bytes {start}-{end}/{file_size}')
    rv.headers.add('Accept-Ranges', 'bytes')
    rv.headers.add('Content-Length', str(chunk_size))
    return rv

# Serve static video files with CORS headers
#@app.route('/static/<path:filename>')
#def serve_static(filename):
#   return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)