import os, uuid, base64, json, io, secrets
from urllib.parse import quote
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, StreamingResponse
import qrcode

app=FastAPI()

def host(): return os.getenv("XRAY_PUBLIC_HOST","YOUR-XRAY-DOMAIN.example.com")
def port(): return os.getenv("XRAY_PUBLIC_PORT","443")

def page(body):
    return f"""<!doctype html><html lang="fa" dir="rtl"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Vercel VPN Panel</title>
<style>body{{font-family:Tahoma;background:#0f172a;color:#eee;margin:0}}main{{max-width:850px;margin:auto;padding:20px}}
.card{{background:#1e293b;padding:20px;margin:14px 0;border-radius:15px}}input,select,button{{width:100%;box-sizing:border-box;padding:12px;margin:6px 0;border-radius:8px;background:#0f172a;color:#fff;border:1px solid #475569}}button{{background:#2563eb;border:0}}pre{{white-space:pre-wrap;word-break:break-all;background:#020617;padding:15px;border-radius:8px}}</style>
<main>{body}</main>"""

def vless(uid,path,sni):
    return f"vless://{uid}@{host()}:{port()}?type=ws&security=tls&encryption=none&path={quote(path,safe='')}&sni={quote(sni or host(),safe='')}#Vercel-VLESS"

def vmess(uid,path,sni):
    x={"v":"2","ps":"Vercel-VMess","add":host(),"port":str(port()),"id":uid,"aid":"0","scy":"auto","net":"ws","type":"none","host":sni or host(),"path":path,"tls":"tls","sni":sni or host()}
    return "vmess://"+base64.urlsafe_b64encode(json.dumps(x,separators=(",",":")).encode()).decode()

def trojan(password,path,sni):
    return f"trojan://{quote(password,safe='')}@{host()}:{port()}?type=ws&security=tls&path={quote(path,safe='')}&sni={quote(sni or host(),safe='')}#Vercel-Trojan"

@app.get("/",response_class=HTMLResponse)
def home():
    return page(f"""<h1>🚀 پنل کانفیگ VPN</h1>
<div class="card"><b>Vercel Panel:</b> {os.getenv("VERCEL_URL","بعد از Deploy مشخص می‌شود")}<br>
<b>VPN Server:</b> {host()}:{port()}<br><small>Vercel فقط پنل است؛ Xray باید روی Railway یا VPS اجرا شود.</small></div>
<div class="card"><form method="post" action="/generate">
<select name="protocol"><option value="vless">VLESS</option><option value="vmess">VMess</option><option value="trojan">Trojan</option></select>
<input name="path" value="/ws" placeholder="Path"><input name="sni" value="{host()}" placeholder="SNI">
<button>ساخت کانفیگ</button></form></div>""")

@app.post("/generate",response_class=HTMLResponse)
def generate(protocol:str=Form(...),path:str=Form("/ws"),sni:str=Form("")):
    uid=str(uuid.uuid4())
    if protocol=="vless": link=vless(uid,path,sni)
    elif protocol=="vmess": link=vmess(uid,path,sni)
    else: link=trojan(secrets.token_urlsafe(18),path,sni)
    return page(f"""<h1>کانفیگ آماده است</h1><div class="card"><pre id="c">{link}</pre>
<button onclick="navigator.clipboard.writeText(document.getElementById('c').innerText)">کپی</button>
<a href="/qr?data={quote(link,safe='')}">QR Code</a></div><a href="/">← برگشت</a>""")

@app.get("/qr")
def qr(data:str):
    img=qrcode.make(data); b=io.BytesIO(); img.save(b,format="PNG"); b.seek(0)
    return StreamingResponse(b,media_type="image/png")

@app.get("/health")
def health(): return {"ok":True,"vpn_host":host(),"vpn_port":port()}
