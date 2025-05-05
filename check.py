import os
import time
from flask import Flask, Response, render_template
import json

app = Flask(__name__)

# 用于记录启动后的文件追踪
START_TIME = time.time()
DOWNLOAD_FOLDER = "./download" 

# 缓存启动后的文件清单（根据创建时间判断）
def get_recent_files():
    recent_files = []
    try:
        for f in os.listdir(DOWNLOAD_FOLDER):
            f_path = os.path.join(DOWNLOAD_FOLDER, f)
            if os.path.getctime(f_path) >= START_TIME:
                recent_files.append(f)
    except FileNotFoundError:
        return []
    return recent_files

def get_all_entries_with_type():
    entries = []
    for f in os.listdir(DOWNLOAD_FOLDER):
        f_path = os.path.join(DOWNLOAD_FOLDER, f)
        entry_type = "file" if os.path.isfile(f_path) else "dir" if os.path.isdir(f_path) else "other"
        entries.append({
            "name": f,
            "type": entry_type
        })
    return entries

@app.route("/download_status")
def download_status():
    recent_files = get_recent_files()

    result = {
        "files_since_startup_count": len(recent_files),
        "files_since_startup": recent_files,
        "entries": get_all_entries_with_type()
    }

    return Response(
        json.dumps(result, ensure_ascii=False, indent=2),  # 中文正常显示
        content_type='application/json; charset=utf-8'
    )

@app.route("/")
def home():
    return render_template("index.html")

app.run(host="0.0.0.0", port=8001)
