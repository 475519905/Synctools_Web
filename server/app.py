"""QQ identity login only. No order entitlements are granted here."""
import hashlib,hmac,json,os,secrets,sqlite3,time
from urllib.parse import urlencode,urlparse
from urllib.request import Request,urlopen
from flask import Flask,request,redirect,jsonify
app=Flask(__name__)
BASE=os.environ.get('PUBLIC_BASE','https://synctools.cn')
CALLBACK='https://activate.synctools.cn/api/auth/qq/callback'
APP_ID=os.environ.get('QQ_APP_ID','1906548516')
KEY=os.environ.get('QQ_APP_KEY','')
SIGN_KEY=os.environ.get('SESSION_HASH_KEY','')
DB=os.environ.get('QQ_DB','/var/lib/synctools-web/identity.db')
COOKIE='__Host-st_web_session'
FLOW='__Host-st_qq_flow'
TTL=7*86400

def digest(v):return hmac.new(SIGN_KEY.encode(),v.encode(),hashlib.sha256).hexdigest()
def db():
 c=sqlite3.connect(DB,timeout=15);c.row_factory=sqlite3.Row;return c

def init_db():
 with db() as c:
  c.executescript('''CREATE TABLE IF NOT EXISTS flows(state TEXT PRIMARY KEY, browser TEXT NOT NULL, expires INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY, nickname TEXT NOT NULL, avatar TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS sessions(token TEXT PRIMARY KEY, user_id TEXT NOT NULL, expires INTEGER NOT NULL);''')

def fetch(path,params):
 req=Request('https://graph.qq.com/'+path+'?'+urlencode(params),headers={'User-Agent':'SyncTools-QQ-Login/1.0'})
 with urlopen(req,timeout=12) as r:return json.loads(r.read(65536))

def finish_error():return redirect('/Account.html?login=failed',303)

@app.after_request
def headers(r):
 r.headers['Cache-Control']='no-store';r.headers['Referrer-Policy']='no-referrer';r.headers['X-Content-Type-Options']='nosniff'
 return r

@app.get('/api/health')
def health():return jsonify(ok=True,configured=bool(KEY and SIGN_KEY))

@app.get('/api/auth/qq/start')
def start():
 if not KEY or len(SIGN_KEY)<32:return jsonify(error='Login is not configured'),503
 state=secrets.token_urlsafe(32);browser=secrets.token_urlsafe(32);now=int(time.time())
 with db() as c:
  c.execute('DELETE FROM flows WHERE expires<?',(now,));c.execute('DELETE FROM sessions WHERE expires<?',(now,))
  c.execute('INSERT INTO flows VALUES(?,?,?)',(digest(state),digest(browser),now+600))
 url='https://graph.qq.com/oauth2.0/authorize?'+urlencode({'response_type':'code','client_id':APP_ID,'redirect_uri':CALLBACK,'state':state,'scope':'get_user_info'})
 r=redirect(url);r.set_cookie(FLOW,browser,max_age=600,secure=True,httponly=True,samesite='Lax',path='/');return r

@app.get('/api/auth/qq/complete')
def complete():
 state=request.args.get('state','');code=request.args.get('code','');browser=request.cookies.get(FLOW,'')
 if not state or len(state)>128 or not browser:return finish_error()
 with db() as c:
  c.execute('BEGIN IMMEDIATE');row=c.execute('SELECT * FROM flows WHERE state=?',(digest(state),)).fetchone()
  if not row or row['expires']<time.time() or not hmac.compare_digest(row['browser'],digest(browser)):return finish_error()
  c.execute('DELETE FROM flows WHERE state=?',(digest(state),))
 if not code or len(code)>1024 or request.args.get('error'):return finish_error()
 try:
  token=fetch('oauth2.0/token',{'grant_type':'authorization_code','client_id':APP_ID,'client_secret':KEY,'code':code,'redirect_uri':CALLBACK,'fmt':'json','need_openid':'1'})
  access=token['access_token'];openid=token.get('openid')
  if not openid:
   identity=fetch('oauth2.0/me',{'access_token':access,'fmt':'json'});assert identity.get('client_id')==APP_ID;openid=identity['openid']
  profile=fetch('user/get_user_info',{'access_token':access,'oauth_consumer_key':APP_ID,'openid':openid});assert profile.get('ret')==0
  nickname=str(profile.get('nickname') or 'QQ 用户')[:128];avatar=str(profile.get('figureurl_qq_2') or profile.get('figureurl_qq_1') or '')
  host=urlparse(avatar).hostname or ''
  if not (avatar.startswith('https://') and (host.endswith('.qlogo.cn') or host=='qlogo.cn' or host.endswith('.qq.com'))):avatar=''
 except Exception:
  # Never log upstream URLs: token exchanges include credentials.
  return finish_error()
 uid=digest('qq:'+openid);session=secrets.token_urlsafe(48)
 with db() as c:
  c.execute('INSERT INTO users VALUES(?,?,?) ON CONFLICT(id) DO UPDATE SET nickname=excluded.nickname,avatar=excluded.avatar',(uid,nickname,avatar))
  c.execute('INSERT INTO sessions VALUES(?,?,?)',(digest(session),uid,int(time.time())+TTL))
 r=redirect('/Account.html?welcome=1',303);r.delete_cookie(FLOW,path='/',secure=True,httponly=True,samesite='Lax');r.set_cookie(COOKIE,session,max_age=TTL,secure=True,httponly=True,samesite='Lax',path='/');return r

@app.get('/api/auth/me')
def me():
 token=request.cookies.get(COOKIE,'')
 if not token:return jsonify(authenticated=False)
 with db() as c:row=c.execute('SELECT u.nickname,u.avatar FROM users u JOIN sessions s ON s.user_id=u.id WHERE s.token=? AND s.expires>?',(digest(token),time.time())).fetchone()
 return jsonify(authenticated=bool(row),user=dict(row) if row else None)

@app.post('/api/auth/logout')
def logout():
 if request.headers.get('Origin')!=BASE or request.headers.get('X-SyncTools-Action')!='logout':return jsonify(error='Invalid origin'),403
 with db() as c:c.execute('DELETE FROM sessions WHERE token=?',(digest(request.cookies.get(COOKIE,'')),))
 r=jsonify(ok=True);r.delete_cookie(COOKIE,path='/',secure=True,httponly=True,samesite='Lax');return r
