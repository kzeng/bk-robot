from flask import render_template, jsonify, request, Blueprint, current_app, redirect, url_for, send_from_directory, flash, session, flash, session
import hashlib
from functools import wraps
import json
import shutil
from app.models import Task, TaskLog, MarkerConfig
from app import db
from datetime import datetime, timezone, timedelta
import asyncio
import os
import time
from threading import Thread
from ftplib import FTP
import platform
import psutil
import subprocess
from dotenv import load_dotenv, set_key
from loguru import logger
import os
from flask import stream_with_context, Response
import psutil
import subprocess
import threading
import queue
from PIL import Image

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_app.config['NEED_AUTH']:
            return f(*args, **kwargs)
        if 'authenticated' not in session:
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

bp1 = Blueprint('routes1', __name__)


@bp1.route('/photos')
@login_required
def photos_page():
    """照片管理页面"""
    return render_template('photos.html')

@bp1.route('/marker-config')
@login_required
def marker_config_page():
    """标记点位配置页面"""
    return render_template('marker_config.html')

@bp1.route('/videos')
@login_required
def videos_page():
    """视频管理页面"""
    return render_template('videos.html')


# Photo management API routes ##########################################################################
@bp1.route('/api/photos/directories', methods=['GET'])
def get_photo_directories():
    """获取所有图片目录"""
    try:
        screenshots_dir = os.path.join(current_app.config['ROOT_PATH'], 'static', 'screenshots')
        
        if not os.path.exists(screenshots_dir):
            return jsonify({
                'directories': [],
                'count': 0
            })
        
        # 获取所有子目录
        all_items = os.listdir(screenshots_dir)
        directories = [d for d in all_items 
                     if os.path.isdir(os.path.join(screenshots_dir, d))]
        
        # 添加调试输出：打印找到的目录
        logger.info(f"Found directories: {directories}")
        
        # 按目录名称排序（通常是日期格式，如YYYYMMDD）
        directories.sort(reverse=True)
        
        return jsonify({
            'directories': directories,
            'count': len(directories)
        })
    except Exception as e:
        logger.error(f"Error getting photo directories: {str(e)}")
        return jsonify({
            'status': 'ERROR',
            'message': f'Failed to get directories: {str(e)}'
        }), 500


@bp1.route('/api/photos/images', methods=['GET'])
def get_images_in_directory():
    """获取指定目录下的图片列表，支持分页和缩略图"""
    try:
        directory = request.args.get('directory', '')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 8))
        screenshots_dir = os.path.join(current_app.config['ROOT_PATH'], 'static', 'screenshots')
        thumbnails_dir = os.path.join(screenshots_dir, 'thumbnails')
        
        # 检查目录是否存在
        dir_path = os.path.join(screenshots_dir, directory) if directory else screenshots_dir
        if not os.path.exists(dir_path):
            logger.info(f"Directory does not exist: {dir_path}")
            return jsonify({
                'images': [],
                'count': 0,
                'directory': directory,
                'page': page,
                'page_size': page_size
            })

        images = []
        processed_files = set()  # 用于跟踪已处理的文件，避免重复
        
        # 递归遍历目录及其子目录
        for root, _, files in os.walk(dir_path):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                    full_path = os.path.join(root, file)
                    
                    # 验证文件是否真实存在且未被处理过
                    if not os.path.isfile(full_path) or full_path in processed_files:
                        continue
                        
                    processed_files.add(full_path)
                    
                    try:
                        # 获取文件状态信息
                        file_stat = os.stat(full_path)
                        
                        # 计算相对路径
                        rel_path = os.path.relpath(full_path, screenshots_dir)
                        rel_dir = os.path.relpath(root, screenshots_dir)
                        
                        # 确保路径分隔符统一使用正斜杠
                        web_path = rel_path.replace(os.sep, '/')
                        
                        # 构建URL
                        thumb_path = os.path.join(thumbnails_dir, rel_dir, file)
                        if os.path.exists(thumb_path):
                            thumbnail_url = url_for('static', filename=f'screenshots/thumbnails/{web_path}')
                        else:
                            thumbnail_url = url_for('static', filename=f'screenshots/{web_path}')
                            
                        images.append({
                            'filename': file,
                            'directory': rel_dir,
                            'fullUrl': url_for('static', filename=f'screenshots/{web_path}'),
                            'thumbnailUrl': thumbnail_url,
                            'size': file_stat.st_size,
                            'timestamp': file_stat.st_mtime,
                            'date': datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                        })
                    except (OSError, ValueError) as e:
                        logger.error(f"Error processing file {full_path}: {str(e)}")
                        continue

        # 按时间戳排序
        images.sort(key=lambda x: -x['timestamp'])
        
        # 分页处理
        total = len(images)
        start = (page - 1) * page_size
        end = start + page_size
        paged_images = images[start:end]

        return jsonify({
            'images': paged_images,
            'count': total,
            'directory': directory,
            'page': page,
            'page_size': page_size,
            'all_images': not directory  # 标记是否是获取所有图片
        })

    except Exception as e:
        logger.error(f"Error getting images in directory: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'ERROR',
            'message': f'Failed to get images: {str(e)}'
        }), 500


@bp1.route('/api/photos/upload', methods=['POST'])
def upload_directory():
    """上传指定目录及其子目录下的所有图片到FTP服务器(保留目录结构)"""
    try:
        data = request.get_json()
        directory = data.get('directory', '')
        
        if not directory:
            return jsonify({
                'status': 'ERROR',
                'message': '未指定目录'
            }), 400
        
        screenshots_dir = os.path.join(current_app.root_path, '..', 'static', 'screenshots')
        dir_path = os.path.join(screenshots_dir, directory)
        
        if not os.path.exists(dir_path):
            return jsonify({
                'status': 'ERROR',
                'message': f'目录不存在: {directory}'
            }), 404

        config = current_app.config
        uploaded_files = []
        
        if config.get('FTP_MOCK_MODE', False):
            # Mock mode - just simulate upload
            logger.info(f"模拟FTP上传(保留目录结构): {directory}")
            for root, _, files in os.walk(dir_path):
                for file in files:
                    if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                        # 计算相对路径，保持目录结构
                        rel_path = os.path.relpath(root, dir_path)
                        uploaded_files.append({
                            'file': file,
                            'directory': rel_path if rel_path != '.' else '',
                            'status': 'success',
                            'message': 'Simulated upload successful'
                        })
            logger.info(f"模拟上传完成，共处理 {len(uploaded_files)} 个文件")
        else:
            # Real FTP upload with directory structure
            ftp = None
            try:
                # Connect to FTP server
                ftp = FTP()
                ftp.connect(config['FTP_HOST'], config['FTP_PORT'])
                ftp.login(config['FTP_USER'], config['FTP_PASS'])
                logger.info(f"已连接FTP服务器: {config['FTP_HOST']}")

                # 设置FTP根目录
                remote_base = config.get('FTP_BASE_DIR', '/pic')
                try:
                    # 先尝试进入目录
                    ftp.cwd(remote_base)
                except Exception as e:
                    logger.info(f"FTP根目录 {remote_base} 不存在，尝试创建")
                    try:
                        # 创建目录
                        ftp.mkd(remote_base)
                        ftp.cwd(remote_base)
                        logger.info(f"成功创建并进入FTP根目录: {remote_base}")
                    except Exception as mkdir_error:
                        logger.error(f"无法创建FTP根目录 {remote_base}: {str(mkdir_error)}")
                        return jsonify({
                            'status': 'ERROR',
                            'message': f'无法创建FTP根目录: {str(mkdir_error)}',
                            'uploaded_files': []
                        }), 500
                
                # 递归上传文件，保持目录结构
                for root, _, files in os.walk(dir_path):
                    # 计算相对路径
                    rel_path = os.path.relpath(root, dir_path)
                    if rel_path != '.':
                        # 在FTP服务器上创建子目录
                        current_remote_path = remote_base
                        for subdir in rel_path.split(os.sep):
                            try:
                                # 先尝试进入目录
                                ftp.cwd(subdir)
                                current_remote_path = os.path.join(current_remote_path, subdir)
                            except:
                                try:
                                    # 如果目录不存在则创建
                                    ftp.mkd(subdir)
                                    ftp.cwd(subdir)
                                    current_remote_path = os.path.join(current_remote_path, subdir)
                                except Exception as e:
                                    logger.error(f"创建FTP目录失败 {subdir}: {str(e)}")
                                    # 返回根目录继续尝试
                                    ftp.cwd(remote_base)
                                    continue
                        
                        # 上传当前目录下的所有图片
                        for file in files:
                            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                                local_file = os.path.join(root, file)
                                try:
                                    with open(local_file, 'rb') as fp:
                                        ftp.storbinary(f'STOR {file}', fp)
                                    uploaded_files.append({
                                        'file': file,
                                        'directory': rel_path if rel_path != '.' else '',
                                        'status': 'success',
                                        'message': 'Upload successful'
                                    })
                                    logger.info(f"成功上传: {local_file}")
                                except Exception as e:
                                    error_msg = f"上传失败: {str(e)}"
                                    logger.error(f"{error_msg} - {local_file}")
                                    uploaded_files.append({
                                        'file': file,
                                        'directory': rel_path if rel_path != '.' else '',
                                        'status': 'failed',
                                        'error': error_msg
                                    })
                        
                        # 返回上级目录，为下一个子目录做准备
                        if rel_path != '.':
                            for _ in rel_path.split(os.sep):
                                ftp.cwd('..')
                    
            except Exception as ftp_error:
                logger.error(f"FTP connection error: {str(ftp_error)}")
                return jsonify({
                    'status': 'ERROR',
                    'message': f'FTP连接失败: {str(ftp_error)}',
                    'uploaded_files': uploaded_files
                }), 500
        
        return jsonify({
            'status': 'OK',
            'message': f'成功上传 {len(uploaded_files)} 个文件到 {directory}',
            'directory': directory,
            'uploaded_files': uploaded_files
        })
    except Exception as e:
        logger.error(f"Error uploading directory: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'ERROR',
            'message': f'Upload failed: {str(e)}'
        }), 500


@bp1.route('/api/photos/delete_directory', methods=['POST'])
def delete_directory():
    """删除指定目录及其所有内容"""
    try:
        data = request.get_json()
        directory = data.get('directory', '')
        
        if not directory:
            return jsonify({
                'status': 'ERROR',
                'message': 'No directory specified'
            }), 400
        

        screenshots_dir = os.path.join(current_app.root_path, '..', 'static', 'screenshots')
        dir_path = os.path.join(screenshots_dir, directory)
        
        if not os.path.exists(dir_path):
            return jsonify({
                'status': 'ERROR',
                'message': f'Directory not found: {directory}'
            }), 404
        
        # 删除目录及其内容
        import shutil
        shutil.rmtree(dir_path)
        
        return jsonify({
            'status': 'OK',
            'message': f'Directory {directory} and its contents have been deleted',
            'directory': directory
        })
    except Exception as e:
        logger.error(f"Error deleting directory: {str(e)}")
        return jsonify({
            'status': 'ERROR',
            'message': f'Delete operation failed: {str(e)}'
        }), 500


@bp1.route('/api/photos/delete_image', methods=['POST'])
def delete_image():
    """删除指定目录下的单个图片文件"""
    logger.info("Received request to delete image")
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'ERROR',
                'message': 'No JSON data received'
            }), 400

        directory = data.get('directory', '')  # 允许空目录，表示根目录
        filename = data.get('filename')
        
        logger.info(f"Deleting image - Directory: {directory}, Filename: {filename}")

        if not filename:  # 只检查文件名是否存在
            return jsonify({
                'status': 'ERROR',
                'message': 'Filename is required'
            }), 400
        
        # 获取截图根目录
        screenshots_dir = os.path.join(current_app.root_path, '..', 'static', 'screenshots')
        screenshots_dir = os.path.normpath(screenshots_dir)
        logger.info(f"Screenshots base directory: {screenshots_dir}")

        # 确保screenshots目录存在
        if not os.path.exists(screenshots_dir):
            logger.error(f"Screenshots directory does not exist: {screenshots_dir}")
            return jsonify({
                'status': 'ERROR',
                'message': f'Screenshots directory not found at: {screenshots_dir}'
            }), 404

        # 优先检查日期子目录（如果文件名包含日期）
        file_path = None
        year_month_day = None
        
        # 尝试从文件名提取日期 (格式: YYYYMMDD)
        if 'Unknown-' in filename:
            year_month_day = filename.split('-')[2][:8]  # Extract from Unknown-CameraX-YYYYMMDD_HHMMSS
        else:
            try:
                # Handle both formats:
                # 1. CameraX-YYYYMMDD_HHMMSS.png
                # 2. M1-s2-c2-YYYYMMDD_HHMMSS.png
                if '-' in filename and '_' in filename:
                    # Split on underscore first to get the date part
                    date_part = filename.split('_')[0]
                    # Then get the last segment which contains the date
                    year_month_day = date_part.split('-')[-1][:8]
                else:
                    year_month_day = filename.split('_')[1][:8]  # Fallback to original format
            except IndexError:
                pass
        
        logger.info(f"Extracted date from filename: {year_month_day}")

        # 确保screenshots目录存在
        if not os.path.exists(screenshots_dir):
            logger.error(f"Screenshots directory does not exist: {screenshots_dir}")
            return jsonify({
                'status': 'ERROR',
                'message': f'Screenshots directory not found'
            }), 404
        
        # 如果找到日期且目录未指定，优先检查日期子目录
        if year_month_day and year_month_day.isdigit() and not directory:
            dated_dir = os.path.join(screenshots_dir, year_month_day)
            logger.info(f"Checking dated directory: {dated_dir}")
            if os.path.exists(dated_dir):
                dated_path = os.path.normpath(os.path.join(dated_dir, filename))
                logger.info(f"Checking file path: {dated_path}")
                if os.path.exists(dated_path):
                    file_path = dated_path
                    logger.info(f"Found file in dated directory: {file_path}")
                else:
                    # Also check root directory as fallback
                    root_path = os.path.normpath(os.path.join(screenshots_dir, filename))
                    if os.path.exists(root_path):
                        file_path = root_path
                        logger.info(f"Found file in root directory: {file_path}")
                    else:
                        logger.warning(f"File not found at path: {dated_path} or {root_path}")
            else:
                # Check root directory if dated directory doesn't exist
                root_path = os.path.normpath(os.path.join(screenshots_dir, filename))
                if os.path.exists(root_path):
                    file_path = root_path
                    logger.info(f"Found file in root directory: {root_path}")
                else:
                    logger.warning(f"Dated directory not found: {dated_dir} and file not in root")
        
        # 构造最终文件路径
        if directory:
            # 如果指定了目录，直接使用该目录
            file_path = os.path.normpath(os.path.join(screenshots_dir, directory, filename))
        else:
            # 如果没有指定目录，尝试从文件名提取日期目录
            # 文件名格式: YYYYMMDDXXXX-... or Unknown-...-YYYYMMDD...
            date_str = None
            if filename.startswith('20') and len(filename) >= 8:  # Starts with year
                date_str = filename[:8]  # YYYYMMDD
            elif 'Unknown-' in filename:  # Unknown-s1-c1-L2-YYYYMMDD_...
                parts = filename.split('-')
                if len(parts) >= 3:
                    date_part = parts[2]
                    if len(date_part) >= 8 and date_part[:4].isdigit():
                        date_str = date_part[:8]  # YYYYMMDD
            
            # 检查日期目录是否存在
            if date_str:
                date_dir = os.path.join(screenshots_dir, date_str)
                if os.path.exists(date_dir):
                    file_path = os.path.normpath(os.path.join(date_dir, filename))
                    logger.info(f"Found file in dated directory: {file_path}")
                else:
                    file_path = os.path.normpath(os.path.join(screenshots_dir, filename))
            else:
                file_path = os.path.normpath(os.path.join(screenshots_dir, filename))
        
        logger.info(f"Final file path to delete: {file_path}")
        logger.info(f"Absolute path: {os.path.abspath(file_path)}")
        
        # 验证路径是否在screenshots目录下（安全检查）
        if not os.path.abspath(file_path).startswith(os.path.abspath(screenshots_dir)):
            logger.error(f"Invalid file path outside screenshots directory: {file_path}")
            return jsonify({
                'status': 'ERROR',
                'message': 'Invalid file path - cannot delete files outside screenshots directory'
            }), 403
        
        if not os.path.exists(file_path):
            logger.info(f"File not found at primary path, searching recursively...")
            found = False
            for root, _, files in os.walk(screenshots_dir):
                if filename in files:
                    file_path = os.path.join(root, filename)
                    logger.info(f"Found file at: {file_path}")
                    found = True
                    break
            
            if not found:
                logger.error(f"File not found at path: {os.path.abspath(file_path)}")
                return jsonify({
                    'status': 'ERROR',
                    'message': f'File not found: {filename} in directory {directory}',
                    'full_path': os.path.abspath(file_path)
                }), 404
        
        # 删除文件
        logger.info(f"Deleting file: {file_path}")
        os.remove(file_path)
        
        return jsonify({
            'status': 'OK',
            'message': f'File {filename} has been deleted from directory {directory}',
            'directory': directory,
            'filename': filename
        })
    except Exception as e:
        logger.error(f"Error deleting image: {str(e)}")
        return jsonify({
            'status': 'ERROR',
            'message': f'Delete operation failed: {str(e)}'
        }), 500


@bp1.route('/api/photos/clear_all', methods=['POST'])
def clear_all_photos():
    """清空所有图片和目录"""
    try:
        screenshots_dir = os.path.join(current_app.root_path, '..', 'static', 'screenshots')
        
        # 如果目录不存在，直接返回成功
        if not os.path.exists(screenshots_dir):
            return jsonify({
                'status': 'OK',
                'message': 'Screenshots directory does not exist, nothing to clear'
            })
        
        # 遍历目录中的所有文件和子目录
        for item in os.listdir(screenshots_dir):
            item_path = os.path.join(screenshots_dir, item)
            
            # 如果是文件，则直接删除
            if os.path.isfile(item_path):
                os.remove(item_path)
            # 如果是目录，则递归删除
            elif os.path.isdir(item_path):
                import shutil
                shutil.rmtree(item_path)
        
        return jsonify({
            'status': 'OK',
            'message': 'All photos and directories have been cleared'
        })
    except Exception as e:
        logger.error(f"Error clearing all photos: {str(e)}")
        return jsonify({
            'status': 'ERROR',
            'message': f'Clear operation failed: {str(e)}'
        }), 500

@bp1.route('/static/screenshots/<path:filename>')
def serve_screenshots(filename):
    """Serve screenshots files"""
    screenshots_dir = os.path.join(current_app.config['ROOT_PATH'], 'static', 'screenshots')
    return send_from_directory(screenshots_dir, filename)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_app.config['NEED_AUTH']:
            return f(*args, **kwargs)
        if 'authenticated' not in session:
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

# @bp1.route('/login', methods=['GET', 'POST'])
# def login():
#     if not current_app.config['NEED_AUTH']:
#         return redirect(url_for('main.tasks_page'))

#     if request.method == 'POST':
#         username = request.form.get('username')
#         password = request.form.get('password')

#         if username == 'admin':
#             hashed_password = hashlib.sha1(password.encode()).hexdigest()
#             if hashed_password == current_app.config['ADMIN_PASSWORD']:
#                 session['authenticated'] = True
#                 session['role'] = 'admin'
#                 session['username'] = username
#                 return redirect(url_for('main.tasks_page'))

#         elif username == 'su':
#             hashed_password = hashlib.sha1(password.encode()).hexdigest()
#             if hashed_password == current_app.config['SUPER_USER_PASSWORD']:
#                 session['authenticated'] = True
#                 session['role'] = 'super_user'
#                 session['username'] = username
#                 return redirect(url_for('main.index'))

#         flash('用户名或密码错误', 'danger')
#     return render_template('login.html')

# @bp1.route('/logout')
# def logout():
#     session.pop('authenticated', None)
#     session.pop('role', None)
#     session.pop('username', None)
#     flash('已退出登录', 'info')
#     return redirect(url_for('main.login'))




@bp1.route('/api/marker-config', methods=['GET', 'POST'])
@login_required
def api_marker_configs():
    """标记点位配置API"""
    if request.method == 'GET':
        search = request.args.get('search', '')
        query = MarkerConfig.query
        if search:
            query = query.filter(
                (MarkerConfig.mid.ilike(f'%{search}%')) |
                (MarkerConfig.mid_short.ilike(f'%{search}%'))
            )
        configs = query.all()
        return jsonify([{
            'id': c.id,
            'mid': c.mid,
            'mid2': c.mid2,
            'mid_short': c.mid_short,
            'x': c.x,
            'y': c.y,
            'w': c.w,
            'h': c.h,
            'x2': c.x2,
            'y2': c.y2,
            'w2': c.w2,
            'h2': c.h2
        } for c in configs])
    
    data = request.json
    config = MarkerConfig(
        mid=data['mid'],
        mid2=data.get('mid2', ''),
        mid_short=data['mid_short'],
        x=data['x'],
        y=data['y'],
        w=data['w'],
        h=data['h'],
        x2=data.get('x2', 0),
        y2=data.get('y2', 0),
        w2=data.get('w2', 0),
        h2=data.get('h2', 0)
    )
    try:
        db.session.add(config)
        db.session.commit()
        return jsonify({
            'id': config.id,
            'message': 'Created successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp1.route('/api/marker-config/<int:id>', methods=['PUT', 'DELETE'])
@login_required
def api_marker_config(id):
    """单个标记点位配置API"""
    config = MarkerConfig.query.get_or_404(id)
    
    if request.method == 'DELETE':
        try:
            db.session.delete(config)
            db.session.commit()
            return jsonify({'message': 'Deleted successfully'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400
    
    data = request.json
    try:
        config.mid = data['mid']
        config.mid2 = data.get('mid2', '')
        config.mid_short = data['mid_short']
        config.x = data['x']
        config.y = data['y']
        config.w = data['w']
        config.h = data['h']
        config.x2 = data.get('x2', 0)
        config.y2 = data.get('y2', 0)
        config.w2 = data.get('w2', 0)
        config.h2 = data.get('h2', 0)
        db.session.commit()
        return jsonify({
            'id': config.id,
            'message': 'Updated successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp1.route('/api/marker-config/clear', methods=['POST'])
@login_required
def clear_marker_configs():
    """清空所有点位配置"""
    try:
        num_deleted = db.session.query(MarkerConfig).delete()
        db.session.commit()
        return jsonify({
            'status': 'OK',
            'message': f'成功删除 {num_deleted} 个点位配置'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'ERROR',
            'message': f'清空点位失败: {str(e)}'
        }), 500

@bp1.route('/api/marker-config/sync', methods=['POST'])
@login_required
def sync_marker_configs():
    """同步机器人点位配置"""
    try:
        # Check if we should use mock data
        # if current_app.config.get('MOCK_MARKER_DATA'):
        if False:
            result = {
                'type': 'response',
                'command': '/api/markers/query_list',
                'status': 'OK',
                'error_message': '',
                'results': {
                    'meeting_room1': {
                        'marker_name': '01020301041',
                        'pose': {'position': {'x': -8.58, 'y': 6.36}}
                    },
                    'meeting_room2': {
                        'marker_name': '01020301042', 
                        'pose': {'position': {'x': -8.58, 'y': 6.36}}
                    }
                }
            }
        else:
            # Call robot API to get marker list
            robot_control = current_app.robot_control
            result = robot_control.send_command("/api/markers/query_list")
        
        if result.get('status') != 'OK':
            return jsonify({
                'status': 'ERROR',
                'error_type': result.get('error_type', 'unknown_error'),
                'message': f'获取机器人点位失败: {result.get("error_message", "未知错误")}'
            }), 500

        # 清空现有点位
        db.session.query(MarkerConfig).delete()
        
               
        # 解析并添加新点位
        markers = result.get('results', {})
        count = 0
        for location_name, info in markers.items():
            marker_name = info.get('marker_name')
            if marker_name:
                # 创建简写名称（M1, M2, ...）
                # if marker_name != 'CD':
                if marker_name.strip().replace(' ', '').upper() != 'CD':
                    count += 1
                    mid_short = f'M{count}'
                else:
                    mid_short = 'CD'
                    
                config = MarkerConfig(
                    mid=marker_name,
                    mid2='00000000000',  # 默认值，后续可更新
                    mid_short=mid_short,
                    x=0,
                    y=0,
                    w=0,
                    h=0,
                    x2=0,
                    y2=0,
                    w2=0,
                    h2=0
                )
                db.session.add(config)
        
        db.session.commit()
        return jsonify({
            'status': 'OK',
            'message': f'成功同步 {count+1} 个点位',
            'results': {
                'count': count+1,
                'markers': list(markers.keys())
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'ERROR',
            'error_type': 'database_error',
            'message': f'同步点位失败: {str(e)}',
            'details': 'Failed to update database with marker data'
        }), 500

@bp1.route('/api/photos/crop', methods=['POST'])
def crop_images():
    USE_MID2 = False

    try:
        logger.info("开始处理裁剪请求")
        data = request.get_json()
        directory = data.get('directory')
        if not directory:
            logger.warning("目录参数为空")
            return jsonify({
                'success': False,
                'message': '目录参数不能为空',
                'processed_files': []
            })

        # 确保目录存在
        screenshots_dir = os.path.join(current_app.root_path, '..', 'static', 'screenshots')
        
        # 如果pic文件夹存在，先清空其内容
        pic_dir = os.path.join(screenshots_dir, 'pic')
        if os.path.exists(pic_dir):
            logger.info(f"清空pic文件夹: {pic_dir}")
            shutil.rmtree(pic_dir)
            os.makedirs(pic_dir, exist_ok=True)

        dir_path = os.path.join(screenshots_dir, directory)
        logger.info(f"检查目录路径: {dir_path}")
        
        if not os.path.exists(dir_path):
            logger.error(f"目录不存在: {dir_path}")
            return jsonify({
                'success': False,
                'message': f'目录 {directory} 不存在，完整路径: {dir_path}',
                'processed_files': []
            })

        processed_files = []
        
        # 遍历目录中的所有图片文件
        for filename in os.listdir(dir_path):
            if not filename.endswith(('.png', '.jpg', '.jpeg')) or 'Unknown' in filename:
                continue

            # 解析文件名获取marker ID
            try:
                marker_id = filename.split('-')[0]  # 获取第一个划线前的部分作为marker ID
                
                # 查询marker_config表获取裁剪参数
                marker_config = MarkerConfig.query.filter_by(mid=marker_id).first()
                if marker_config == None:
                    USE_MID2 = True
                    marker_config = MarkerConfig.query.filter_by(mid2=marker_id).first()
                else:
                    USE_MID2 = False
                
                if not marker_config:
                    processed_files.append({
                        'file': filename,
                        'status': 'failed',
                        'error': f'找不到对应的marker配置: {marker_id}'
                    })
                    continue

                # 图片完整路径
                img_path = os.path.join(dir_path, filename)
                
                try:
                    logger.info(f"开始处理图片: {img_path}")
                    img = Image.open(img_path)
                    width, height = img.size

                    logger.info(f"图片打开成功: {img_path}, 大小: {img.size}, 模式: {img.mode}")

                    if USE_MID2:
                        if marker_config.x2 == 0 and marker_config.y2 == 0 and \
                        marker_config.w2 == 0 and marker_config.h2 == 0:
                            logger.info(f"配置参数全为0，跳过裁剪: {marker_id}")
                            new_img = img
                        else:
                            # 执行裁剪
                            x = marker_config.x2
                            y = marker_config.y2
                            w = min(width,  marker_config.w2 + x)
                            h = min(height, marker_config.h2 + y)
                            logger.info(f"裁剪参数: x={x}, y={y}, w={w}, h={h}")
                            new_img = img.crop((
                                x,  
                                y,  
                                w,
                                h
                            ))
                            logger.info(f"裁剪完成(mid2): {new_img.size}, 模式: {new_img.mode}")
                    else:
                        # 如果x,y,w,h都为0，则跳过裁剪但仍然保存新文件
                        if marker_config.x == 0 and marker_config.y == 0 and \
                        marker_config.w == 0 and marker_config.h == 0:
                            logger.info(f"配置参数全为0，跳过裁剪: {marker_id}")
                            new_img = img
                        else:
                            # 执行裁剪
                            x = marker_config.x
                            y = marker_config.y
                            w = min(width,  marker_config.w + x)
                            h = min(height, marker_config.h + y)
                            logger.info(f"裁剪参数(mid): x={x}, y={y}, w={w}, h={h}")
                            new_img = img.crop((
                                x,  
                                y,  
                                w,
                                h
                            ))
                            logger.info(f"裁剪完成(mid): {new_img.size}, 模式: {new_img.mode}")

                    # 生成新的文件名
                    base_name = os.path.splitext(filename)[0]
                    ext = os.path.splitext(filename)[1]
                    new_filename = f"{base_name}-crop{ext}"
                    new_path = os.path.join(dir_path, new_filename)

                    # 保存新图片
                    logger.info(f"保存裁剪后的图片: {new_path}")
                    new_img.save(new_path, optimize=False, compression_level=0)
                    logger.info(f"成功保存裁剪后的图片: {new_path}")

                    # 准备处理结果
                    result = {
                        'file': filename,
                        'status': 'success',
                        'new_file': new_filename
                    }

                    # 如果是裁剪后的文件，进行分类移动
                    if new_filename.endswith('-crop.png'):
                        try:
                            # 解析文件名各部分
                            parts = base_name.split('-')  # 不包含-crop.png部分
                            if len(parts) >= 4:
                                first_part = parts[0]  # 例如：01020301041
                                second_part = parts[1]  # 例如：s1
                                time_part = parts[3]    # 例如：1751422638
                                
                                # 构建 FOLDER1：01 + 前10位 + 第二个字段从第2个字符起到末尾，不足2位前面补0
                                if len(first_part) >= 10 and len(second_part) >= 2:
                                    prefix_10 = first_part[:10]  # 取前10位
                                    # second_char = second_part[1]  # 取第二个字符
                                    second_char = second_part[1:]  # 从第二个字符开始到末尾
                                    folder1 = f"01{prefix_10}{second_char.zfill(2)}"  # 补0确保两位
                                    
                                    # 构建文件名：第一个字段的最后一位
                                    if len(first_part) > 0:
                                        new_filename_final = f"{first_part[-1]}.png"
                                        
                                        # 构建新的目录结构：pic/[FOLDER1]/book/[TIME]/[FILENAME].png
                                        new_dir = os.path.join(screenshots_dir, 'pic', folder1, 'book', time_part)
                                        new_file_path = os.path.join(new_dir, new_filename_final)
                                        
                                        # 创建目录（如果不存在）
                                        os.makedirs(new_dir, exist_ok=True)
                                        
                                        # 移动文件
                                        logger.info(f"移动文件到新位置: {new_file_path}")
                                        shutil.move(new_path, new_file_path)
                                        logger.info(f"成功移动文件到: {new_file_path}")
                                        
                                        # 更新处理状态
                                        result['moved_to'] = os.path.relpath(new_file_path, screenshots_dir)
                        except Exception as e:
                            logger.error(f"移动文件时出错: {str(e)}", exc_info=True)
                            result['move_error'] = str(e)
                    
                    processed_files.append(result)
                except Exception as e:
                    logger.error(f"处理图片时出错: {str(e)}", exc_info=True)
                    processed_files.append({
                        'file': filename,
                        'status': 'failed',
                        'error': str(e)
                    })

            except Exception as e:
                processed_files.append({
                    'file': filename,
                    'status': 'failed',
                    'error': str(e)
                })

        # 统计处理结果
        success_count = len([f for f in processed_files if f['status'] == 'success'])
        fail_count = len([f for f in processed_files if f['status'] == 'failed'])

        logger.info(f"裁剪处理完成: {success_count} 成功, {fail_count} 失败")
        return jsonify({
            'success': True,
            'message': f'处理完成: {success_count} 成功, {fail_count} 失败',
            'processed_files': processed_files
        })

    except Exception as e:
        logger.error(f"裁剪过程发生错误: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'处理过程中发生错误: {str(e)}',
            'processed_files': []
        }), 500  # 添加500状态码表示服务器错误


@bp1.route('/api/videos/list', methods=['GET'])
def get_videos_in_directory():
    """获取指定目录下的视频列表，支持分页"""
    try:
        directory = request.args.get('dir', '')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('size', 8))
        videos_dir = os.path.join(current_app.root_path, '..', 'static', 'video')
        # 目录为空时递归所有视频
        if directory:
            dir_path = os.path.join(videos_dir, directory)
        else:
            dir_path = videos_dir
        if not os.path.exists(dir_path):
            return jsonify({
                'files': [],
                'total_count': 0,
                'total_pages': 1,
                'page': page,
                'size': page_size
            })
        files = []
        for root, _, filenames in os.walk(dir_path):
            for file in filenames:
                if file.lower().endswith('.mp4'):
                    # 只返回文件名
                    files.append(os.path.relpath(os.path.join(root, file), dir_path if directory else videos_dir))
            if directory:
                break  # 只遍历当前目录
        files.sort(reverse=True)
        total_count = len(files)
        total_pages = max(1, (total_count + page_size - 1) // page_size)
        start = (page - 1) * page_size
        end = start + page_size
        paged_files = files[start:end]
        return jsonify({
            'files': paged_files,
            'total_count': total_count,
            'total_pages': total_pages,
            'page': page,
            'size': page_size
        })
    except Exception as e:
        logger.error(f"Error getting videos: {str(e)}")
        return jsonify({
            'files': [],
            'total_count': 0,
            'total_pages': 1,
            'page': 1,
            'size': 8,
            'error': str(e)
        }), 500
    
# ---------------------- 视频一键上传 API ----------------------
@bp1.route('/api/videos/upload', methods=['POST'])
def upload_video_directory():
    """
    上传指定视频目录及其子目录下的所有mp4到FTP服务器(保留目录结构，根为vid)
    POST参数: { directory: '20250804' }
    """
    try:
        data = request.get_json()
        directory = data.get('directory', '')
        if not directory:
            return jsonify({
                'status': 'ERROR',
                'message': '未指定目录'
            }), 400

        # 本地视频目录
        videos_dir = os.path.join(current_app.root_path, '..', 'static', 'video')
        dir_path = os.path.join(videos_dir, directory)
        if not os.path.exists(dir_path):
            return jsonify({
                'status': 'ERROR',
                'message': f'目录不存在: {directory}'
            }), 404

        config = current_app.config
        uploaded_files = []

        if config.get('FTP_MOCK_MODE', False):
            # Mock模式-仅模拟
            logger.info(f"模拟FTP上传视频目录: {directory}")
            for root, _, files in os.walk(dir_path):
                for file in files:
                    if file.lower().endswith('.mp4'):
                        rel_path = os.path.relpath(root, dir_path)
                        uploaded_files.append({
                            'file': file,
                            'directory': rel_path if rel_path != '.' else '',
                            'status': 'success',
                            'message': 'Simulated upload successful'
                        })
            logger.info(f"模拟上传完成，共处理 {len(uploaded_files)} 个视频文件")
        else:
            # 真正FTP上传
            ftp = None
            try:
                ftp = FTP()
                ftp.connect(config['FTP_HOST'], config['FTP_PORT'])
                ftp.login(config['FTP_USER'], config['FTP_PASS'])
                logger.info(f"已连接FTP服务器: {config['FTP_HOST']}")

                # 设置FTP根目录 vid
                remote_base = config.get('FTP_VIDEO_BASE_DIR', '/vid')
                try:
                    ftp.cwd(remote_base)
                except Exception as e:
                    logger.info(f"FTP根目录 {remote_base} 不存在，尝试创建")
                    try:
                        ftp.mkd(remote_base)
                        ftp.cwd(remote_base)
                        logger.info(f"成功创建并进入FTP根目录: {remote_base}")
                    except Exception as mkdir_error:
                        logger.error(f"无法创建FTP根目录 {remote_base}: {str(mkdir_error)}")
                        return jsonify({
                            'status': 'ERROR',
                            'message': f'无法创建FTP根目录: {str(mkdir_error)}',
                            'uploaded_files': []
                        }), 500

                # 递归上传mp4，保持目录结构
                for root, _, files in os.walk(dir_path):
                    rel_path = os.path.relpath(root, dir_path)
                    # 创建子目录
                    if rel_path != '.':
                        current_remote_path = remote_base
                        for subdir in rel_path.split(os.sep):
                            try:
                                ftp.cwd(subdir)
                                current_remote_path = os.path.join(current_remote_path, subdir)
                            except:
                                try:
                                    ftp.mkd(subdir)
                                    ftp.cwd(subdir)
                                    current_remote_path = os.path.join(current_remote_path, subdir)
                                except Exception as e:
                                    logger.error(f"创建FTP目录失败 {subdir}: {str(e)}")
                                    ftp.cwd(remote_base)
                                    continue
                    # 上传当前目录下所有mp4
                    for file in files:
                        if file.lower().endswith('.mp4'):
                            local_file = os.path.join(root, file)
                            try:
                                with open(local_file, 'rb') as fp:
                                    ftp.storbinary(f'STOR {file}', fp)
                                uploaded_files.append({
                                    'file': file,
                                    'directory': rel_path if rel_path != '.' else '',
                                    'status': 'success',
                                    'message': 'Upload successful'
                                })
                                logger.info(f"成功上传: {local_file}")
                            except Exception as e:
                                error_msg = f"上传失败: {str(e)}"
                                logger.error(f"{error_msg} - {local_file}")
                                uploaded_files.append({
                                    'file': file,
                                    'directory': rel_path if rel_path != '.' else '',
                                    'status': 'failed',
                                    'error': error_msg
                                })
                    # 返回上级目录
                    if rel_path != '.':
                        for _ in rel_path.split(os.sep):
                            ftp.cwd('..')
            except Exception as ftp_error:
                logger.error(f"FTP connection error: {str(ftp_error)}")
                return jsonify({
                    'status': 'ERROR',
                    'message': f'FTP连接失败: {str(ftp_error)}',
                    'uploaded_files': uploaded_files
                }), 500

        return jsonify({
            'status': 'OK',
            'message': f'成功上传 {len(uploaded_files)} 个视频到 {directory}',
            'directory': directory,
            'uploaded_files': uploaded_files
        })
    except Exception as e:
        logger.error(f"Error uploading video directory: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'ERROR',
            'message': f'Upload failed: {str(e)}'
        }), 500