from __future__ import unicode_literals
import yt_dlp
import os
import json
from flask import (
    Blueprint, current_app, request, Response, jsonify
)

bp = Blueprint('convert', __name__, url_prefix='/convert')

@bp.post('/audio')
def convert():
    print('Attempting Conversion...')
    content_type = request.headers.get('Content-Type')
    if (content_type != 'application/json'):
        return Response(json.dump({'Error': 'Content-Type not supported'}), status=400, mimetype='application/json')
    else:
        body = request.json
        url = body['url']
        fileId = body['fileId']
        title = body['title']
        fileFormat = body['fileFormat']

        # use --no-keep-video post processor arg
        ydl_opts = {
            'format': 'bestaudio/best',
            'extractaudio': True,
            'outtmpl': os.path.join(current_app.root_path, 'media/%(id)s.%(ext)s'),
            'ffmpeg_location': '/workspace/ffmpeg/bin',
            'postprocessor_args': {
                'FFmpegMetadata': ['--parse-metadata', '"customTitle:(?P<meta_title>)"', '--add-metadata']
            },
            'postprocessors': [{
                'key': 'FFmpegMetadata'
            },
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': fileFormat,
                'preferredquality': '192'
            }, 
            ]
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print('Starting Conversion...')
            ydl.download(url)

        payload = {
            'title': title,
            'filename': "%s.%s" % (fileId, fileFormat)
        }
        return jsonify(payload)