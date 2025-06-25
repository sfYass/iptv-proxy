# api/stream.py
from flask import Flask, request, Response, stream_with_context
import requests
from urllib.parse import urljoin

app = Flask(__name__)

BASE_URL = "https://cdn-globecast.akamaized.net/live/eds/2m_monde/hls_video_ts_tuhawxpiemz257adfc/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0",
    "Referer": "http://www.radio2m.ma/"
}

def stream_proxy(url):
    with requests.get(url, headers=HEADERS, stream=True) as res:
        res.raise_for_status()
        for chunk in res.iter_content(chunk_size=8192):
            if chunk:
                yield chunk

@app.route('/')
def index():
    return "IPTV Proxy Server is running. Use /api/stream to access the IPTV stream."

@app.route('/stream')
def stream():
    return Response(stream_with_context(stream_proxy(BASE_URL + "2m_monde.m3u8")),
                    content_type='application/vnd.apple.mpegurl')

@app.route('/<path:filename>')
def segments(filename):
    target_url = urljoin(BASE_URL, filename)
    return Response(stream_with_context(stream_proxy(target_url)), content_type='application/octet-stream')

# Required for Vercel
def handler(environ, start_response):
    from werkzeug.middleware.dispatcher import DispatcherMiddleware
    from werkzeug.serving import run_simple
    return app(environ, start_response)
