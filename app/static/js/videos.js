// videos.js
// 视频管理页面脚本

document.addEventListener('DOMContentLoaded', function() {
    let currentDir = '';
    let currentPage = 1;
    let pageSize = 8;
    let totalPages = 1;

    // 初始化
    loadVideoDirs();

    document.getElementById('refresh-video-dir').onclick = loadVideoDirs;
    document.getElementById('delete-video-dir').onclick = deleteCurrentDir;
    document.getElementById('clear-all-videos').onclick = clearAllVideos;

    // 加载目录列表
    function loadVideoDirs() {
        fetch('/videos/dirs')
            .then(res => res.json())
            .then(data => {
                let ul = document.getElementById('video-dir-list');
                ul.innerHTML = '';
                (data.directories || []).forEach(dir => {
                    let li = document.createElement('li');
                    li.className = 'list-group-item list-group-item-action';
                    li.textContent = dir;
                    li.onclick = function() {
                        document.querySelectorAll('#video-dir-list .active').forEach(e => e.classList.remove('active'));
                        li.classList.add('active');
                        currentDir = dir;
                        currentPage = 1;
                        loadVideos();
                    };
                    ul.appendChild(li);
                });
                // 默认选中第一个
                if (data.directories && data.directories.length > 0) {
                    ul.firstChild && ul.firstChild.click();
                } else {
                    document.getElementById('video-list').innerHTML = '<div class="text-muted">暂无视频目录</div>';
                }
            });
    }

    // 加载视频文件
    function loadVideos() {
        if (!currentDir) return;
        fetch(`/videos/list?dir=${encodeURIComponent(currentDir)}&page=${currentPage}&size=${pageSize}`)
            .then(res => res.json())
            .then(data => {
                renderVideoList(data.files || []);
                // 分页
                totalPages = data.total_pages || 1;
                renderPagination();
                document.getElementById('current-dir-title').textContent = `视频文件 - ${currentDir}`;
            });
    }

    // 渲染视频缩略图
    function renderVideoList(files) {
        let list = document.getElementById('video-list');
        list.innerHTML = '';
        if (!Array.isArray(files)) return;
        files.forEach(file => {
            let col = document.createElement('div');
            // 完全对齐 photos.html 的图片缩略图布局
            col.className = 'col-md-2-4 col-sm-3 col-4';
            col.innerHTML = `
                <div class="card img-container video-thumb" style="cursor:pointer;">
                  <div class="ratio ratio-16x9 bg-light d-flex align-items-center justify-content-center" style="background:#eee;">
                    <i class="fas fa-video text-muted" style="font-size: 3rem;"></i>
                  </div>
                  <div class="card-body p-2">
                    <p class="card-text text-truncate mb-1" title="${file}">${file}</p>
                  </div>
                </div>`;
            col.querySelector('.video-thumb').onclick = function() {
                previewVideo(file);
            };
            list.appendChild(col);
        });
    }

    // 渲染分页
    function renderPagination() {
        let ul = document.getElementById('video-pagination');
        ul.className = 'pagination justify-content-center'; // 保持和photos.html一致
        ul.innerHTML = '';
        if (totalPages <= 1) return;
        // 最多显示7个页码按钮（包括省略号）
        const maxVisiblePages = 5;
        let startPage = Math.max(1, currentPage - 2);
        let endPage = Math.min(totalPages, currentPage + 2);
        if (currentPage <= 3) {
            endPage = Math.min(maxVisiblePages, totalPages);
        } else if (currentPage >= totalPages - 2) {
            startPage = Math.max(1, totalPages - maxVisiblePages + 1);
        }
        // 上一页
        let prevLi = document.createElement('li');
        prevLi.className = 'page-item' + (currentPage === 1 ? ' disabled' : '');
        prevLi.innerHTML = '<a class="page-link" href="#">上一页</a>';
        prevLi.onclick = function(e) {
            e.preventDefault();
            if (currentPage > 1) {
                currentPage--;
                loadVideos();
            }
        };
        ul.appendChild(prevLi);
        // 第一页
        if (startPage > 1) {
            let firstLi = document.createElement('li');
            firstLi.className = 'page-item';
            firstLi.innerHTML = '<a class="page-link" href="#">1</a>';
            firstLi.onclick = function(e) {
                e.preventDefault();
                currentPage = 1;
                loadVideos();
            };
            ul.appendChild(firstLi);
            if (startPage > 2) {
                let ellipsisLi = document.createElement('li');
                ellipsisLi.className = 'page-item ellipsis';
                ellipsisLi.innerHTML = '<span class="page-link">...</span>';
                ul.appendChild(ellipsisLi);
            }
        }
        // 中间页码
        for (let i = startPage; i <= endPage; i++) {
            let li = document.createElement('li');
            li.className = 'page-item' + (i === currentPage ? ' active' : '');
            li.innerHTML = `<a class="page-link" href="#">${i}</a>`;
            li.onclick = function(e) {
                e.preventDefault();
                currentPage = i;
                loadVideos();
            };
            ul.appendChild(li);
        }
        // 最后一页
        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                let ellipsisLi = document.createElement('li');
                ellipsisLi.className = 'page-item ellipsis';
                ellipsisLi.innerHTML = '<span class="page-link">...</span>';
                ul.appendChild(ellipsisLi);
            }
            let lastLi = document.createElement('li');
            lastLi.className = 'page-item';
            lastLi.innerHTML = `<a class="page-link" href="#">${totalPages}</a>`;
            lastLi.onclick = function(e) {
                e.preventDefault();
                currentPage = totalPages;
                loadVideos();
            };
            ul.appendChild(lastLi);
        }
        // 下一页
        let nextLi = document.createElement('li');
        nextLi.className = 'page-item' + (currentPage === totalPages ? ' disabled' : '');
        nextLi.innerHTML = '<a class="page-link" href="#">下一页</a>';
        nextLi.onclick = function(e) {
            e.preventDefault();
            if (currentPage < totalPages) {
                currentPage++;
                loadVideos();
            }
        };
        ul.appendChild(nextLi);
    }

    // 预览视频
    function previewVideo(filename) {
        let video = document.getElementById('preview-video');
        let label = document.getElementById('preview-filename');
        console.log('Attempting to preview video:', filename, 'in directory:', currentDir);
        // 清空旧内容
        video.pause();
        video.removeAttribute('src');
        video.innerHTML = '';
        video.load();
        // 直接设置 src 属性
        let videoUrl = `/static/video/${currentDir}/${filename}`;
        console.log('Video URL:', videoUrl);
        video.src = videoUrl;
        video.setAttribute('type', 'video/mp4');
        video.setAttribute('controls', '');
        video.setAttribute('playsinline', '');
        video.load();
        // 事件监听和弹窗逻辑保持不变
        video.onerror = function() {
            console.error('Video playback error:', video.error);
            console.error('Network state:', video.networkState);
            console.error('Ready state:', video.readyState);
        };
        video.onloadedmetadata = function() {
            console.log('Video metadata loaded - dimensions:', 
                video.videoWidth, 'x', video.videoHeight,
                'duration:', video.duration);
        };
        video.oncanplay = function() {
            console.log('Video can now play');
        };
        video.onstalled = function() {
            console.warn('Video stalled - buffering data');
        };
        video.onprogress = function() {
            console.log('Video loading progress:', 
                video.buffered.length ? video.buffered.end(0) : 0);
        };
        label.textContent = filename;
        let modal = new bootstrap.Modal(document.getElementById('videoPreviewModal'));
        modal.show();
        // Try to play with comprehensive error handling
        let playPromise = video.play();
        if (playPromise !== undefined) {
            playPromise
                .then(() => console.log('Video playback started successfully'))
                .catch(e => {
                    console.error('Playback failed:', e);
                    console.error('Current video source:', video.currentSrc);
                    console.error('Video ready state:', video.readyState);
                    label.textContent = `${filename} (播放失败: ${e.message})`;
                });
        }
    }

    // 删除当前目录
    function deleteCurrentDir() {
        if (!currentDir) return;
        if (!confirm(`确定要删除目录 ${currentDir} 吗？此操作不可恢复！`)) return;
        fetch('/videos/delete_directory', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ directory: currentDir })
        })
            .then(res => res.json())
            .then(data => {
                alert(data.message || '删除成功');
                loadVideoDirs();
                // 自动刷新页面
                setTimeout(() => window.location.reload(), 500);
            });
    }

    // 清空所有视频
    function clearAllVideos() {
        if (!confirm('确定要清空所有视频文件吗？此操作不可恢复！')) return;
        fetch('/videos/clear_all', {method: 'POST'})
            .then(res => res.json())
            .then(data => {
                alert(data.message || '已清空');
                loadVideoDirs();
                // 自动刷新页面
                setTimeout(() => window.location.reload(), 500);
            });
    }
});
