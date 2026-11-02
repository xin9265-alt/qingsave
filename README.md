# QingSave 视频链接解析网站

手机适配网页 + FastAPI 后端。

## 已实现
- 粘贴完整抖音分享文案，自动提取官方短链接
- 跟随跳转，尝试获取视频 ID
- 预留授权媒体资源解析接口

**目前未接入无水印视频解析服务，不能下载任意抖音视频。** 这是开发原型，未完成生产级限流和网络出口安全防护，请勿直接向公众开放。

## 本地运行
Python 3.10+：

```bash
pip install -r requirements.txt
uvicorn app:app --host 127.0.0.1 --port 8000
```

浏览 http://127.0.0.1:8000

## API
POST `/api/parse`，请求示例：

```json
{"text":"复制打开抖音 https://v.douyin.com/zjccc_ob3Zs/"}
```

GET `/api/health`

## 云部署
GitHub 仅托管代码，不会运行 Python 后端。可以在 Render 或 Railway 等 Python 托管平台连接此仓库，启动命令：

```bash
uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}
```

公网部署前需要补充限流、网络出口过滤、DNS pinning、监控等安全措施。
