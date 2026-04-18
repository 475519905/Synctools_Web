/* global React */
/* Shared subpage components: Nav + Footer (non-landing versions) */

function SubNav({ current }) {
  const [menuOpen, setMenuOpen] = React.useState(false);
  const links = [
    { href: 'Store.html', label: '商店' },
    { href: 'Docs.html', label: '文档' },
    { href: 'Download.html', label: '下载' },
  ];
  return (
    <nav className="nav">
      <div className="wrap nav-inner">
        <a href="SyncTools Pro.html" className="logo" style={{ textDecoration: 'none', color: 'inherit' }}>
          <div className="logo-mark"><SubLogoMark /></div>
          SyncTools
          <span className="mono" style={{ color: 'var(--fg-mute)', marginLeft: 6 }}>v3.0</span>
        </a>
        <div className="nav-links">
          {links.map((l, i) => (
            <a key={i} href={l.href} style={current === l.label ? { color: 'var(--fg)' } : {}}>{l.label}</a>
          ))}
        </div>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <a className="btn btn-ghost hide-mobile" href="Account.html">用户中心</a>
          <a className="btn btn-primary hide-mobile" href="Store.html">Buy Now →</a>
          <button className={`nav-burger ${menuOpen ? 'open' : ''}`} onClick={() => setMenuOpen(!menuOpen)} aria-label="菜单">
            <span/><span/><span/>
          </button>
        </div>
        <div className={`nav-mobile-drawer ${menuOpen ? 'open' : ''}`}>
          <a href="SyncTools Pro.html">首页</a>
          {links.map((l, i) => (
            <a key={i} href={l.href} onClick={() => setMenuOpen(false)}>{l.label}</a>
          ))}
          <a href="Account.html">用户中心</a>
          <a href="Store.html" style={{ color: 'var(--accent)', fontWeight: 600 }}>Buy Now →</a>
        </div>
      </div>
    </nav>
  );
}

function SubLogoMark() {
  return (
    <svg viewBox="0 0 24 24" fill="none">
      <defs>
        <linearGradient id="slm" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#b794ff" />
          <stop offset="1" stopColor="#5b2bd6" />
        </linearGradient>
      </defs>
      <circle cx="8" cy="12" r="6" stroke="url(#slm)" strokeWidth="2" />
      <circle cx="16" cy="12" r="6" stroke="currentColor" strokeWidth="2" opacity="0.6" />
      <circle cx="12" cy="12" r="1.6" fill="url(#slm)" />
    </svg>
  );
}

function SubFooter() {
  return (
    <footer className="footer">
      <div className="wrap">
        <div className="footer-grid">
          <div className="footer-brand">
            <a href="SyncTools Pro.html" className="logo" style={{ textDecoration: 'none', color: 'inherit' }}>
              <div className="logo-mark"><SubLogoMark /></div>
              SyncTools
            </a>
            <p className="tag cn">Transforming everything has never been so simple. 无界衔接，此刻连接世界。</p>
          </div>
          <div>
            <h4>Product</h4>
            <div className="links">
              <a href="SyncTools Pro.html">首页</a>
              <a href="Store.html">商店</a>
              <a href="Download.html">下载</a>
              <a href="Docs.html">文档</a>
            </div>
          </div>
          <div>
            <h4>Resources</h4>
            <div className="links">
              <a href="Docs.html">文档中心</a>
              <a href="#">社区</a>
              <a href="#">更新日志</a>
            </div>
          </div>
          <div>
            <h4>Account</h4>
            <div className="links">
              <a href="Account.html">用户中心</a>
              <a href="#">联系支持</a>
            </div>
          </div>
        </div>
        <div className="footer-bottom">
          <div>© 2026 SyncTools · All rights reserved</div>
          <div>v3.0.4</div>
        </div>
      </div>
    </footer>
  );
}

function SubToast({ msg }) {
  if (!msg) return null;
  return <div className="st-toast show">{msg}</div>;
}

Object.assign(window, { SubNav, SubFooter, SubLogoMark, SubToast });
