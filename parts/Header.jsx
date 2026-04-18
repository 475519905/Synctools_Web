/* global React */
const { useState, useEffect, useRef } = React;

// === SVG logo mark ===
function LogoMark() {
  return (
    <svg viewBox="0 0 24 24" fill="none">
      <defs>
        <linearGradient id="lm" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#b794ff" />
          <stop offset="1" stopColor="#5b2bd6" />
        </linearGradient>
      </defs>
      <circle cx="8" cy="12" r="6" stroke="url(#lm)" strokeWidth="2" />
      <circle cx="16" cy="12" r="6" stroke="currentColor" strokeWidth="2" opacity="0.6" />
      <circle cx="12" cy="12" r="1.6" fill="url(#lm)" />
    </svg>
  );
}

// === Promo bar ===
function PromoBar() {
  const items = Array(4).fill(0);
  return (
    <div className="promo-bar">
      <div className="promo-track">
        {items.map((_, i) => (
          <React.Fragment key={i}>
            <span>使用优惠码 <b>#SYNCTOOLS</b> 立享 80% OFF</span>
            <span>· 全球 162 国 20,000+ 设计师正在使用 ·</span>
            <span>限时折扣 · 仅剩 <b>03:12:48</b></span>
            <span>· 专业客服 1 对 1 支持 ·</span>
          </React.Fragment>
        ))}
      </div>
    </div>
  );
}

// === Nav ===
function Nav() {
  const [menuOpen, setMenuOpen] = useState(false);
  return (
    <nav className="nav">
      <div className="wrap nav-inner">
        <div className="logo">
          <div className="logo-mark"><LogoMark /></div>
          SyncTools
          <span className="mono" style={{ color: 'var(--fg-mute)', marginLeft: 6 }}>v3.0</span>
        </div>
        <div className="nav-links">
          <a href="#features">功能</a>
          <a href="#stats">用户</a>
          <a href="#testimonials">评价</a>
          <a href="#pricing">定价</a>
          <a href="Docs.html">文档</a>
        </div>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <a className="btn btn-ghost hide-mobile" href="Store.html">Learn More</a>
          <a className="btn btn-primary hide-mobile" href="#pricing">Buy Now →</a>
          <button className={`nav-burger ${menuOpen ? 'open' : ''}`} onClick={() => setMenuOpen(!menuOpen)} aria-label="菜单">
            <span/><span/><span/>
          </button>
        </div>
        <div className={`nav-mobile-drawer ${menuOpen ? 'open' : ''}`}>
          <a href="#features" onClick={() => setMenuOpen(false)}>功能</a>
          <a href="#stats" onClick={() => setMenuOpen(false)}>用户</a>
          <a href="#testimonials" onClick={() => setMenuOpen(false)}>评价</a>
          <a href="#pricing" onClick={() => setMenuOpen(false)}>定价</a>
          <a href="Docs.html">文档</a>
          <a href="Store.html">商店</a>
          <a href="#pricing" style={{ color: 'var(--accent)', fontWeight: 600 }}>Buy Now →</a>
        </div>
      </div>
    </nav>
  );
}

// === Animated Sync Demo ===
function SyncDemo() {
  const [tick, setTick] = useState(0);
  useEffect(() => {
    let raf;
    const loop = () => { setTick(t => t + 1); raf = requestAnimationFrame(loop); };
    raf = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(raf);
  }, []);
  const t = (tick % 360) / 360;
  const pulse = 0.5 + 0.5 * Math.sin(tick / 30);

  return (
    <svg className="sync-demo" viewBox="0 0 520 520" fill="none">
      <defs>
        <radialGradient id="sph1" cx="35%" cy="30%">
          <stop offset="0" stopColor="#d4b8ff" />
          <stop offset="0.5" stopColor="#8b5cf6" />
          <stop offset="1" stopColor="#2a0f6a" />
        </radialGradient>
        <radialGradient id="sph2" cx="35%" cy="30%">
          <stop offset="0" stopColor="#f0e4ff" />
          <stop offset="0.5" stopColor="#a78bfa" />
          <stop offset="1" stopColor="#1a0747" />
        </radialGradient>
        <linearGradient id="ring" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#b794ff" stopOpacity="0.8" />
          <stop offset="1" stopColor="#b794ff" stopOpacity="0" />
        </linearGradient>
        <filter id="soft"><feGaussianBlur stdDeviation="1.2" /></filter>
      </defs>

      {/* Background orbital rings */}
      {[180, 140, 100].map((r, i) => (
        <circle
          key={i}
          cx="260" cy="260" r={r}
          stroke="url(#ring)" strokeWidth="1" fill="none"
          opacity={0.4 - i * 0.1}
          transform={`rotate(${tick / (3 + i)} 260 260)`}
          strokeDasharray={`${4 + i * 6} ${10 - i * 2}`}
        />
      ))}

      {/* Main sphere */}
      <circle cx="260" cy="260" r="110" fill="url(#sph1)" filter="url(#soft)" />
      <circle cx="260" cy="260" r="110" fill="none" stroke="#b794ff" strokeOpacity="0.5" />

      {/* Secondary sphere (smaller, orbiting) */}
      <g transform={`rotate(${tick / 2} 260 260)`}>
        <circle cx="420" cy="260" r="34" fill="url(#sph2)" />
        <circle cx="420" cy="260" r="34" fill="none" stroke="#e9dcff" strokeOpacity="0.6" strokeWidth="0.5" />
      </g>

      {/* Data pulses flowing from main to orbit */}
      {[0, 0.33, 0.66].map((offset, i) => {
        const phase = (t + offset) % 1;
        const angle = tick / 2;
        const rad = angle * Math.PI / 180;
        const startX = 260 + Math.cos(rad) * 110;
        const startY = 260 + Math.sin(rad) * 110;
        const endX = 260 + Math.cos(rad) * 160;
        const endY = 260 + Math.sin(rad) * 160;
        const x = startX + (endX - startX) * phase;
        const y = startY + (endY - startY) * phase;
        return (
          <circle key={i} cx={x} cy={y} r={2.5} fill="#f0e4ff" opacity={1 - phase} />
        );
      })}

      {/* Small nodes on rings */}
      {[0, 90, 180, 270].map((deg, i) => {
        const a = (deg + tick) * Math.PI / 180;
        const r = 180;
        return (
          <circle key={i} cx={260 + Math.cos(a) * r} cy={260 + Math.sin(a) * r} r="3" fill="#b794ff" opacity={0.6 + pulse * 0.4} />
        );
      })}

      {/* Labels */}
      <g fontFamily="var(--font-mono)" fontSize="9" fill="#b794ff" opacity="0.8">
        <text x="30" y="30" letterSpacing="1">SOURCE · CINEMA</text>
        <text x="440" y="490" letterSpacing="1" textAnchor="end">TARGET · BLENDER</text>
        <text x="30" y="490" letterSpacing="1">SYNC 100%</text>
        <text x="440" y="30" letterSpacing="1" textAnchor="end">v3.0.2</text>
      </g>

      {/* Corner crosses */}
      {[[20, 20], [500, 20], [20, 500], [500, 500]].map(([x, y], i) => (
        <g key={i} stroke="#b794ff" strokeWidth="1" opacity="0.5">
          <line x1={x - 5} y1={y} x2={x + 5} y2={y} />
          <line x1={x} y1={y - 5} x2={x} y2={y + 5} />
        </g>
      ))}
    </svg>
  );
}

// === Hero ===
function Hero() {
  return (
    <section className="hero" id="hero">
      <div className="hero-halo" />
      <div className="hero-grid" />
      <SyncDemo />
      <div className="wrap hero-content">
        <div className="hero-eyebrow">
          <span className="pill">NEW</span>
          SyncTools Pro · v3.0 已发布
        </div>
        <h1>
          无界衔接,<br/>
          <span className="cn">此刻</span>
          <span className="serif"> connect </span>
          <span className="cn">世界。</span>
        </h1>
        <p className="hero-sub cn">
          高效的全平台转换工具 SyncTools，现已全新升级到 V3.0。新增骨骼、VFX、运动图形、几何节点等多种资产，快速导入复杂动画材质，帮助 3D 艺术家和设计师提升工作流效率。
        </p>
        <div className="hero-cta">
          <a className="btn btn-primary" href="#pricing">Buy Now · -80% →</a>
          <a className="btn btn-ghost" href="#features">Learn More</a>
        </div>
        <div className="hero-meta">
          <div className="item"><div className="num">20,000<span style={{color:'var(--accent)'}}>+</span></div><div className="lbl">Designers</div></div>
          <div className="item"><div className="num">162</div><div className="lbl">Countries</div></div>
          <div className="item"><div className="num">200<span style={{color:'var(--accent)'}}>+</span></div><div className="lbl">Studios & Teams</div></div>
          <div className="item"><div className="num">V3.0</div><div className="lbl">Latest Release</div></div>
        </div>
      </div>
    </section>
  );
}

// === DCC Rail ===
function DccRail() {
  const dccs = [
    {
      n: 'Cinema 4D', c: '#011a6a',
      svg: (
        <svg viewBox="0 0 40 40"><rect width="40" height="40" rx="8" fill="#011a6a"/><path d="M20 10a10 10 0 1 0 9.5 13.2l-3.8-1.3a6 6 0 1 1 0-3.8L29.5 16.8A10 10 0 0 0 20 10z" fill="#fff"/></svg>
      )
    },
    {
      n: 'Maya', c: '#0696d7',
      svg: (
        <svg viewBox="0 0 40 40"><rect width="40" height="40" rx="8" fill="#0696d7"/><path d="M11 13l4 14h2l3-10 3 10h2l4-14h-3l-2 9-2.6-9h-2.8l-2.6 9-2-9z" fill="#fff"/></svg>
      )
    },
    {
      n: 'Blender', c: '#ea7600',
      svg: (
        <svg viewBox="0 0 40 40"><rect width="40" height="40" rx="8" fill="#1a1a1a"/><circle cx="20" cy="22" r="8" fill="#ea7600"/><circle cx="20" cy="22" r="4" fill="#fff"/><circle cx="18.5" cy="20.5" r="1.2" fill="#1a1a1a"/></svg>
      )
    },
    {
      n: 'Houdini', c: '#ff4713',
      svg: (
        <svg viewBox="0 0 40 40"><rect width="40" height="40" rx="8" fill="#ff4713"/><path d="M12 12h6v6h-6zm10 0h6v6h-6zM12 22h6v6h-6zm10 0h6v6h-6z" fill="#fff"/><path d="M18 18h4v4h-4z" fill="#fff"/></svg>
      )
    },
    {
      n: '3ds Max', c: '#1f9ed9',
      svg: (
        <svg viewBox="0 0 40 40"><rect width="40" height="40" rx="8" fill="#1f9ed9"/><text x="20" y="25" fontFamily="var(--font-display)" fontSize="13" fontWeight="800" fill="#fff" textAnchor="middle" letterSpacing="-0.5">3ds</text></svg>
      )
    },
    {
      n: 'Unreal Engine', c: '#0e1013',
      svg: (
        <svg viewBox="0 0 40 40"><rect width="40" height="40" rx="8" fill="#0e1013"/><circle cx="20" cy="20" r="10" fill="none" stroke="#fff" strokeWidth="1.5"/><path d="M15 15v8l5-2 5 2v-8" fill="none" stroke="#fff" strokeWidth="1.5" strokeLinejoin="round"/><circle cx="20" cy="19" r="1.5" fill="#fff"/></svg>
      )
    },
    {
      n: 'Unity', c: '#111',
      svg: (
        <svg viewBox="0 0 40 40"><rect width="40" height="40" rx="8" fill="#111"/><g transform="translate(20 20)"><path d="M0-9 L7.8-4.5 L7.8 4.5 L0 9 L-7.8 4.5 L-7.8-4.5 Z" fill="none" stroke="#fff" strokeWidth="1.3"/><path d="M0-9 L7.8 4.5 M0-9 L-7.8 4.5 M-7.8-4.5 L7.8 4.5 M7.8-4.5 L-7.8 4.5 M0 9 L0-3" stroke="#fff" strokeWidth="0.8" opacity="0.6"/></g></svg>
      )
    },
  ];
  return (
    <section className="rail">
      <div className="wrap">
        <div className="rail-head">
          <div className="mono">&nbsp;</div>
          <div className="mono">全 DCC 流式协作 · 主流渲染器支持</div>
        </div>
        <div className="rail-logos">
          {dccs.map((d, i) => (
            <div className="rail-logo" key={i}>
              <div className="brand-mark">{d.svg}</div>
              <div className="name">{d.n}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

Object.assign(window, { LogoMark, PromoBar, Nav, Hero, DccRail, SyncDemo });
