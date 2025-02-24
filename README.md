# Online English Test

这是一个用于英语考试的应用程序，支持语音识别和答案提交功能。

## 项目依赖

### 1. Python 版本
- Python 3.13（推荐使用 [pyenv](https://github.com/pyenv/pyenv) 或 [conda](https://docs.conda.io/en/latest/) 管理 Python 版本）

### 2. 依赖库
项目的依赖库列在 `requirements.txt` 文件中。你可以通过以下命令安装所有依赖：

```bash
pip install -r requirements.txt
```

#### 主要依赖库
- `Flask`: Web 框架。
- `speech_recognition`: 语音识别库。
- `pydub`: 音频处理库（用于支持多种音频格式）。
- `wave`: Python 标准库，用于处理 WAV 文件。
- `gunicorn`: 用于生产环境部署的 WSGI 服务器（可选）。

### 3. 其他工具
- [FFmpeg](https://ffmpeg.org/): `pydub` 依赖的工具，用于处理音频文件。可以通过以下命令安装：
  - macOS: `brew install ffmpeg`
  - Ubuntu: `sudo apt install ffmpeg`
  - Windows: 下载并安装 [FFmpeg](https://ffmpeg.org/download.html)。

---

## 部署方法

### 1. 本地运行
1. 克隆项目到本地：
   ```bash
   git clone https://github.com/BornChanger/onlineTest.git
   cd onlineTest
   ```

2. 创建虚拟环境并激活：
   ```bash
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   venv\Scripts\activate     # Windows
   ```

3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

4. 运行应用：
   ```bash
   python app.py
   ```

5. 访问应用：
   打开浏览器，访问 `http://127.0.0.1:5000`。

---

### 2. 生产环境部署
推荐使用 `gunicorn` 和 `nginx` 部署到生产环境。

#### 使用 Gunicorn 运行
1. 安装 Gunicorn：
   ```bash
   pip install gunicorn
   ```

2. 启动应用：
   ```bash
   gunicorn -w 4 app:app
   ```

3. 访问应用：
   打开浏览器，访问 `http://127.0.0.1:8000`。

#### 使用 Nginx 反向代理
1. 安装 Nginx：
   - macOS: `brew install nginx`
   - Ubuntu: `sudo apt install nginx`

2. 配置 Nginx：
   编辑 `/etc/nginx/sites-available/default`，添加以下内容：
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       }
   }
   ```

3. 重启 Nginx：
   ```bash
   sudo systemctl restart nginx
   ```

4. 访问应用：
   打开浏览器，访问 `http://yourdomain.com`。

---

## 项目结构

```
onlineTest/
├── app.py                # 主应用程序文件
├── requirements.txt      # 依赖库列表
├── static/               # 静态文件（CSS、JS、图片等）
│   └── styles.css
├── templates/            # HTML 模板文件
│   └── index.html       # 主页面
│   └── results.html     # 考试结果页面
├── uploads/              # 上传文件存储目录
└── README.md             # 项目说明文档
```

---

## 常见问题

### 1. 上传的文件不是有效的 WAV 文件
确保上传的文件是有效的 WAV 文件。如果需要支持其他格式，请使用 `pydub` 进行格式转换。

### 2. 语音识别失败
- 检查音频文件是否清晰。
- 确保音频文件的采样率和声道数符合 `speech_recognition` 的要求。

### 3. 部署后无法访问
- 检查防火墙设置，确保端口（如 80 或 5000）已开放。
- 检查 Nginx 或 Gunicorn 的日志文件，排查错误。

---

## 贡献指南
欢迎提交 Issue 或 Pull Request！请确保代码风格一致，并通过所有测试。

---

## 许可证
本项目基于 MIT 许可证开源。详情请参阅 [LICENSE](LICENSE) 文件。

---

如果你有其他需求或需要进一步定制，请告诉我！