import os, re, socket, ipaddress
from urllib.parse import urlparse, urljoin
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI(title="QingSave")
HOSTS = {"v.douyin.com", "www.douyin.com", "douyin.com", "iesdouyin.com"}
PAT = re.compile(r'https?://(?:v\.douyin\.com|www\.douyin\.com|douyin\.com)/[^\s<>"\']+', re.I)

class Payload(BaseModel):
    text: str

def check_url(url):
    p = urlparse(url)
    if p.scheme != "https" or p.hostname not in HOSTS or p.port not in (None, 443) or p.username or p.password:
        raise HTTPException(400, "仅允许抖音官方 HTTPS 链接")
    try:
        ips = {x[4][0] for x in socket.getaddrinfo(p.hostname, 443, type=socket.SOCK_STREAM)}
        if not ips or any(not ipaddress.ip_address(ip).is_global for ip in ips):
            raise HTTPException(400, "目标地址不安全")
    except OSError:
        raise HTTPException(502, "域名解析失败")

@app.post("/api/parse")
async def parse(data: Payload):
    if len(data.text) > 6000:
        raise HTTPException(400, "分享文案过长")
    match = PAT.search(data.text)
    if not match:
        raise HTTPException(400, "没有识别到抖音分享链接")
    original = match.group(0).rstrip("，。！；、,.;!")
    current = original
    async with httpx.AsyncClient(timeout=8, follow_redirects=False, headers={"User-Agent": "Mozilla/5.0"}) as client:
        for _ in range(5):
            check_url(current)
            try:
                async with client.stream("GET", current) as response:
                    status = response.status_code
                    location = response.headers.get("location")
            except httpx.HTTPError:
                raise HTTPException(502, "链接请求失败，请稍后重试")
            if status in (301, 302, 303, 307, 308) and location:
                current = urljoin(current, location)
                continue
            break
        else:
            raise HTTPException(502, "跳转次数过多")
    check_url(current)
    match = re.search(r"/video/(\d+)", current)
    return {"success": True, "original_url": original, "resolved_url": current,
            "video_id": match.group(1) if match else None, "video_url": None,
            "status": "metadata_only",
            "message": "已解析分享链接。尚未配置授权的视频媒体接口，暂不支持无水印下载。"}

@app.get("/api/health")
def health():
    return {"ok": True}

@app.get("/")
def index():
    return FileResponse(os.path.join(os.path.dirname(__file__), "static", "index.html"))
