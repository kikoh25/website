import http.server,socketserver,re,os,sys
ROOT='/home/claude/website'
hdr={}
cur=None
for l in open(ROOT+'/_headers'):
    if not l.strip(): continue
    if not l.startswith(' '): cur=l.strip(); hdr[cur]=[]
    else:
        k,v=l.strip().split(': ',1); hdr[cur].append((k,v))
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(s,*a,**k): super().__init__(*a,directory=ROOT,**k)
    def end_headers(s):
        for k,v in hdr['/*']: s.send_header(k,v)
        super().end_headers()
    def log_message(s,*a): pass
    def translate_path(s,p):
        r=super().translate_path(p)
        if os.path.isdir(r) and not os.path.exists(os.path.join(r,'index.html')): return r
        return r
socketserver.TCPServer.allow_reuse_address=True
socketserver.TCPServer(('127.0.0.1',8765),H).serve_forever()
