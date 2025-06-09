# NOTES

## use python3.8 venv
- conda create -n venv-py38-robot python=3.8
- see requirements.txt for detail python packages 

## set pip package source 
pip config set global.index-url https://repo.huaweicloud.com/repository/pypi/simple



## todo

| Feature              | Status |
|----------------------|--------|
| User Login           | Done   |
| Setting              | Done   |
| Task Management      | Done   |
| Task Details         | Done   |
| Task Log Management  | Done   |
| Data Management      | Done   |
| Control Panel        | Done   |



## issue


## prompt history



## temp info

- shot with position_info
```
curl -X POST http://localhost:5000/api/obs/screenshot \
  -H "Content-Type: application/json" \
  -d '{"position_info": "Marker1"}'
{
  "position": "Marker1",
  "results": [
    {
      "camera_id": 1,
      "filename": "Marker1-s1-s1-20250525_112856.jpg",
      "filepath": "static/screenshots/20250525/Marker1-s1-c1-20250525_112856.jpg",
      "scene": "s1",
      "status": "OK"
    },
    {
      "camera_id": 2,
      "filename": "Marker1-s2-s2-20250525_112856.jpg",
      "filepath": "static/screenshots/20250525/Marker1-s2-c2-20250525_112856.jpg",
      "scene": "s2",
      "status": "OK"
    },
    {
      "camera_id": 3,
      "filename": "Marker1-s3-s3-20250525_112856.jpg",
      "filepath": "static/screenshots/20250525/Marker1-s3-c3-20250525_112856.jpg",
      "scene": "s3",
      "status": "OK"
    }
  ],
  "status": "OK",
  "timestamp": "20250525_112856"
}
```



## run obs with headless
```bash
obs --minimize-to-tray
```

sudo apt-get update && sudo apt-get install -y v4l-utils