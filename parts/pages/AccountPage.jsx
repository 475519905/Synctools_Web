function AccountPage() {
 const [state,setState]=React.useState(null);
 React.useEffect(()=>{fetch('/api/auth/me',{credentials:'same-origin'}).then(r=>r.json()).then(setState).catch(()=>setState({error:true}));},[]);
 async function logout(){const r=await fetch('/api/auth/logout',{method:'POST',headers:{'X-SyncTools-Action':'logout'}});if(r.ok)location.assign('/Account.html');}
 const failed=new URLSearchParams(location.search).get('login')==='failed';
 return <><SubNav current=""/><main className="wrap" style={{padding:'70px 20px',minHeight:'65vh'}}><h1>SyncTools 用户中心</h1>{failed && <p role="alert">QQ 授权未完成，请重新尝试。审核期间请使用已配置的调试 QQ 号。</p>}{!state ? <p>正在读取登录状态…</p> : state.authenticated ? <section><h2>{new URLSearchParams(location.search).has('welcome')?'欢迎使用 SyncTools，':''}{state.user.nickname}</h2>{state.user.avatar && <img src={state.user.avatar} alt="QQ头像" width="64" height="64" referrerPolicy="no-referrer"/>}<p>您已通过 QQ 登录。QQ 身份登录不代表已购买插件，订单验证、下载与设备管理请前往激活中心。</p><a className="btn btn-primary" href="https://activate.synctools.cn/">前往激活中心验证订单</a><button className="btn btn-ghost" onClick={logout}>退出登录</button></section> : <section><h2>使用 QQ 快速登录</h2><p>授权后可使用 QQ 昵称和头像登录本网站。我们不会获取您的 QQ 密码。</p><QQLoginButton/><p>继续登录即表示您已阅读<a href="Privacy.html">隐私说明</a>。订单权限仍需在激活中心单独核验。</p>{state.error && <p>登录服务暂不可用，请稍后重试。</p>}</section>}</main><SubFooter/></>;
}

ReactDOM.createRoot(document.getElementById("root")).render(<AccountPage />);
