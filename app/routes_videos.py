from flask import Blueprint, jsonify, request, send_from_directory
import os
import shutil

bp = Blueprint('videos_api', __name__)

VIDEO_BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'video')

@bp.route('/videos/dirs')
def list_video_dirs():
    try:
        dirs = []
        if os.path.exists(VIDEO_BASE):
            dirs = [d for d in os.listdir(VIDEO_BASE) if os.path.isdir(os.path.join(VIDEO_BASE, d))]
            dirs.sort(reverse=True)
        return jsonify({'directories': dirs})
    except Exception as e:
        return jsonify({'directories': [], 'error': str(e)})

@bp.route('/videos/list')
def list_videos():
    dir_name = request.args.get('dir', '')
    page = int(request.args.get('page', 1))
    size = int(request.args.get('size', 12))
    dir_path = os.path.join(VIDEO_BASE, dir_name)
    files = []
    total = 0
    if os.path.exists(dir_path):
        files = [f for f in os.listdir(dir_path) if f.lower().endswith('.mp4')]
        files.sort(reverse=True)
        total = len(files)
    start = (page-1)*size
    end = start+size
    return jsonify({
        'files': files[start:end],
        'total': total,
        'total_pages': (total+size-1)//size
    })

@bp.route('/videos/delete_directory', methods=['POST'])
def delete_video_dir():
    data = request.get_json()
    dir_name = data.get('directory', '')
    dir_path = os.path.join(VIDEO_BASE, dir_name)
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)
        return jsonify({'success': True, 'message': f'已删除目录 {dir_name}'})
    return jsonify({'success': False, 'message': '目录不存在'}), 404

@bp.route('/videos/clear_all', methods=['POST'])
def clear_all_videos():
    if os.path.exists(VIDEO_BASE):
        for d in os.listdir(VIDEO_BASE):
            dpath = os.path.join(VIDEO_BASE, d)
            if os.path.isdir(dpath):
                shutil.rmtree(dpath)
            elif d.lower().endswith('.mp4'):
                os.remove(dpath)
    return jsonify({'success': True, 'message': '所有视频已清空'})

# Serve video files directly from static folder
@bp.route('/static/video/<path:filename>')
def serve_video(filename):
    return send_from_directory(VIDEO_BASE, filename)
