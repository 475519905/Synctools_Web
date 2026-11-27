import importlib.util,os,tempfile,unittest
from urllib.parse import urlparse,parse_qs
os.environ['QQ_DB']=tempfile.mktemp();os.environ['SESSION_HASH_KEY']='t'*64;os.environ['QQ_APP_KEY']='test-only'
spec=importlib.util.spec_from_file_location('qq','server/app.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.init_db()
class QQTests(unittest.TestCase):
 def client(self):return m.app.test_client()
 def test_no_entitlements(self):self.assertEqual(self.client().get('/api/auth/me').json,{'authenticated':False})
 def test_bad_state(self):self.assertIn('failed',self.client().get('/api/auth/qq/complete?state=bad&code=fake').location)
 def test_login_replay_logout(self):
  c=self.client();r=c.get('/api/auth/qq/start',base_url=m.BASE);state=parse_qs(urlparse(r.location).query)['state'][0]
  def fake(p,args):
   if p=='oauth2.0/token':return {'access_token':'no-real-token','openid':'test-user'}
   return {'ret':0,'nickname':'<test>','figureurl_qq_2':'https://qlogo.cn/test.png'}
  old=m.fetch;m.fetch=fake
  try:
   url='/api/auth/qq/complete?state='+state+'&code=test'
   r=c.get(url,base_url=m.BASE);self.assertIn('welcome',r.location)
   self.assertTrue(c.get('/api/auth/me',base_url=m.BASE).json['authenticated'])
   self.assertIn('failed',c.get(url,base_url=m.BASE).location)
   self.assertEqual(c.post('/api/auth/logout',base_url=m.BASE).status_code,403)
   self.assertEqual(c.post('/api/auth/logout',base_url=m.BASE,headers={'Origin':m.BASE,'X-SyncTools-Action':'logout'}).status_code,200)
   self.assertFalse(c.get('/api/auth/me',base_url=m.BASE).json['authenticated'])
  finally:m.fetch=old
 def test_foreign_browser(self):
  a=self.client();r=a.get('/api/auth/qq/start',base_url=m.BASE);s=parse_qs(urlparse(r.location).query)['state'][0]
  b=self.client();self.assertIn('failed',b.get('/api/auth/qq/complete?state='+s+'&code=x',base_url=m.BASE).location)
if __name__=='__main__':unittest.main()
