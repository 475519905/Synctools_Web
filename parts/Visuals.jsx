/* global React */
const { useState: useState2, useEffect: useEffect2, useRef: useRef2 } = React;

// ==== Feature visualization components ====

// Vis 1 — One-click transform (animated "click to convert" progress pill)
function VisTransform() {
  const [on, setOn] = useState2(false);
  useEffect2(() => {
    const t = setInterval(() => setOn(o => !o), 2800);
    return () => clearInterval(t);
  }, []);
  return (
    <div style={{ width: '100%', height: '100%', position: 'relative', background: 'radial-gradient(ellipse at 50% 40%, rgba(139,92,246,0.2), transparent 60%)' }}>
      <div style={{ position: 'absolute', inset: 0, backgroundImage: 'linear-gradient(to right, rgba(255,255,255,0.04) 1px, transparent 1px), linear-gradient(to bottom, rgba(255,255,255,0.04) 1px, transparent 1px)', backgroundSize: '32px 32px' }} />
      <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 24 }}>
        <div style={sourceBox('#1a6bff', 'C4D')}>
          <div style={{ width: 36, height: 36, borderRadius: 6, background: on ? 'transparent' : '#b794ff', transition: 'all .4s', transform: on ? 'scale(0.5) rotate(45deg)' : 'scale(1)' }} />
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6 }}>
          <div className="mono" style={{ color: on ? '#a6ff2e' : 'var(--fg-mute)', fontSize: 9, transition: 'color .3s' }}>
            {on ? '✓ SYNCED · 0.42s' : '→ TRANSFER'}
          </div>
          <div style={{ width: 120, height: 3, background: 'rgba(255,255,255,0.08)', borderRadius: 2, overflow: 'hidden' }}>
            <div style={{ height: '100%', background: 'var(--accent)', width: on ? '100%' : '0%', transition: 'width 1.4s cubic-bezier(0.16,1,0.3,1)' }} />
          </div>
          <div className="mono" style={{ color: 'var(--fg-mute)', fontSize: 9 }}>ONE · CLICK</div>
        </div>
        <div style={sourceBox('#f2802f', 'BLN')}>
          <div style={{ width: 36, height: 36, borderRadius: 6, background: on ? '#b794ff' : 'transparent', transition: 'all .4s', transform: on ? 'scale(1)' : 'scale(0.5) rotate(-45deg)' }} />
        </div>
      </div>
      <div className="mono" style={{ position: 'absolute', top: 18, left: 18, color: 'var(--fg-mute)', fontSize: 10 }}>/ sync_001.log</div>
      <div className="mono" style={{ position: 'absolute', bottom: 18, right: 18, color: 'var(--accent)', fontSize: 10 }}>● LIVE</div>
    </div>
  );
}

function sourceBox(color, label) {
  return {
    width: 100, height: 100, borderRadius: 14,
    border: '1px solid rgba(255,255,255,0.12)',
    background: 'color-mix(in oklab, ' + color + ' 10%, var(--bg))',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    position: 'relative'
  };
}

// Vis 2 — Material sync (layered node graph)
function VisMaterial() {
  const nodes = [
    { x: 40, y: 30, w: 80, h: 44, c: 'var(--vis-c1)', l: 'BASE' },
    { x: 40, y: 95, w: 80, h: 44, c: 'var(--vis-c2)', l: 'NORMAL' },
    { x: 40, y: 160, w: 80, h: 44, c: 'var(--vis-c3)', l: 'ROUGH' },
    { x: 190, y: 95, w: 100, h: 60, c: 'var(--vis-c4)', l: 'SHADER' },
  ];
  return (
    <div style={{ width: '100%', height: '100%', position: 'relative', overflow: 'hidden' }}>
      <svg viewBox="0 0 400 260" style={{ width: '100%', height: '100%' }}>
        {/* grid */}
        <defs>
          <pattern id="mg" width="16" height="16" patternUnits="userSpaceOnUse">
            <path d="M16 0 L0 0 0 16" fill="none" stroke="var(--vis-grid)" strokeWidth="1"/>
          </pattern>
        </defs>
        <rect width="400" height="260" fill="url(#mg)" />

        {/* connections */}
        {nodes.slice(0, 3).map((n, i) => (
          <path key={i}
            d={`M${n.x + n.w} ${n.y + n.h/2} C ${n.x + n.w + 40} ${n.y + n.h/2}, ${190 - 40} ${95 + 30}, 190 ${95 + 30}`}
            stroke={n.c} strokeWidth="1.5" fill="none" opacity="0.8"
            strokeDasharray="3 3"
          >
            <animate attributeName="stroke-dashoffset" values="0;-12" dur={`${1 + i * 0.3}s`} repeatCount="indefinite" />
          </path>
        ))}

        {nodes.map((n, i) => (
          <g key={i}>
            <rect x={n.x} y={n.y} width={n.w} height={n.h} rx="6"
              fill="var(--vis-node-bg)"
              stroke={n.c} strokeWidth="1" />
            <circle cx={n.x + n.w} cy={n.y + n.h/2} r="3" fill={n.c} />
            <circle cx={n.x} cy={n.y + n.h/2} r="3" fill={n.c} />
            <text x={n.x + 10} y={n.y + 18} fill={n.c} fontFamily="var(--font-mono)" fontSize="8" letterSpacing="1">{n.l}</text>
            <rect x={n.x + 10} y={n.y + 24} width={n.w - 20} height="10" rx="2" fill={n.c} opacity="0.3" />
          </g>
        ))}

        {/* transfer indicator */}
        <g transform="translate(320, 30)">
          <rect width="60" height="28" rx="14" fill="var(--accent)" />
          <text x="30" y="18" textAnchor="middle" fill="var(--vis-pill-fg)" fontFamily="var(--font-mono)" fontSize="9" fontWeight="700" letterSpacing="1">100% PBR</text>
        </g>
        <text x="20" y="250" fill="var(--fg-mute)" fontFamily="var(--font-mono)" fontSize="8" letterSpacing="1">MATERIAL.GRAPH · 4 NODES · VERIFIED</text>
      </svg>
    </div>
  );
}

// Vis 3 — Animation (scrubbing timeline + keyframes)
function VisAnimation() {
  const [p, setP] = useState2(0);
  useEffect2(() => {
    let raf;
    let start = performance.now();
    const tick = () => {
      const t = ((performance.now() - start) / 3000) % 1;
      setP(t);
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, []);
  const keys = [0.05, 0.2, 0.35, 0.5, 0.65, 0.85];

  return (
    <div style={{ width: '100%', height: '100%', position: 'relative', display: 'flex', flexDirection: 'column', padding: 24, gap: 16 }}>
      {/* viewport preview */}
      <div style={{ flex: 1, borderRadius: 10, border: '1px solid var(--line)', background: 'radial-gradient(ellipse at 30% 30%, rgba(139,92,246,0.2), transparent 60%)', position: 'relative', overflow: 'hidden' }}>
        <svg viewBox="0 0 300 160" style={{ width: '100%', height: '100%' }}>
          {/* skeletal rig */}
          <g transform={`translate(${50 + p * 200}, ${50 + Math.sin(p * Math.PI * 2) * 20})`}>
            <circle cx="0" cy="0" r="12" fill="none" stroke="var(--accent)" strokeWidth="1.5" />
            <line x1="0" y1="12" x2="0" y2="50" stroke="var(--accent)" strokeWidth="2" />
            <line x1="-20" y1="25" x2="20" y2="25" stroke="var(--accent)" strokeWidth="2" />
            <line x1="0" y1="50" x2="-15" y2="80" stroke="var(--accent)" strokeWidth="2" />
            <line x1="0" y1="50" x2="15" y2="80" stroke="var(--accent)" strokeWidth="2" />
            {[[-20,25],[20,25],[-15,80],[15,80],[0,12],[0,50]].map(([x,y],i) => <circle key={i} cx={x} cy={y} r="2.5" fill="var(--accent-deep)"/>)}
          </g>
          <text x="12" y="20" fill="var(--fg-mute)" fontFamily="var(--font-mono)" fontSize="8" letterSpacing="1">RIG · 32 BONES · IK</text>
        </svg>
      </div>
      {/* timeline */}
      <div>
        <div className="mono" style={{ fontSize: 9, color: 'var(--fg-mute)', marginBottom: 8, display: 'flex', justifyContent: 'space-between' }}>
          <span>TIMELINE · 120 FRAMES</span>
          <span style={{ color: 'var(--accent)' }}>{Math.floor(p * 120).toString().padStart(3, '0')} / 120</span>
        </div>
        <div style={{ height: 36, background: 'var(--bg)', border: '1px solid var(--line)', borderRadius: 6, position: 'relative' }}>
          {keys.map((k, i) => (
            <div key={i} style={{ position: 'absolute', left: `${k * 100}%`, top: 6, bottom: 6, width: 2, background: 'var(--accent)', opacity: 0.6, transform: 'rotate(45deg) scale(1.2)', borderRadius: 1 }} />
          ))}
          <div style={{ position: 'absolute', left: `${p * 100}%`, top: -4, bottom: -4, width: 2, background: 'var(--fg)' }} />
          <div style={{ position: 'absolute', left: `${p * 100}%`, top: -10, width: 0, height: 0, borderLeft: '6px solid transparent', borderRight: '6px solid transparent', borderTop: '8px solid var(--fg)', transform: 'translateX(-5px)' }} />
        </div>
      </div>
    </div>
  );
}

// Vis 4 — Parameters (dashboard of toggles)
function VisParams() {
  const params = [
    { l: 'RESOLUTION', v: '3840 × 2160', ok: true },
    { l: 'FRAME RATE', v: '24 FPS', ok: true },
    { l: 'ASPECT', v: '16 : 9', ok: true },
    { l: 'FOCAL LENGTH', v: '35 MM', ok: true },
    { l: 'COLOR SPACE', v: 'ACES CG', ok: true },
    { l: 'SAFE AREA', v: '95 %', ok: true },
  ];
  return (
    <div style={{ width: '100%', height: '100%', padding: 28, display: 'flex', flexDirection: 'column', gap: 12, position: 'relative' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div className="mono" style={{ color: 'var(--fg-mute)', fontSize: 10 }}>PROJECT · PARAMETERS</div>
        <div className="mono" style={{ color: 'var(--vis-status-ok)', fontSize: 10 }}>● ALL SYNCED</div>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, flex: 1 }}>
        {params.map((p, i) => (
          <div key={i} style={{ padding: '12px 14px', border: '1px solid var(--line)', borderRadius: 8, background: 'var(--bg)', display: 'flex', flexDirection: 'column', gap: 6, position: 'relative' }}>
            <div className="mono" style={{ fontSize: 9, color: 'var(--fg-mute)' }}>{p.l}</div>
            <div style={{ fontFamily: 'var(--font-display)', fontWeight: 600, fontSize: 16 }}>{p.v}</div>
            <div style={{ position: 'absolute', top: 12, right: 12, width: 6, height: 6, borderRadius: '50%', background: 'var(--accent)' }} />
          </div>
        ))}
      </div>
    </div>
  );
}

// Vis 5 — Lighting (light spheres + data)
function VisLighting() {
  return (
    <div style={{ width: '100%', height: '100%', position: 'relative' }}>
      <svg viewBox="0 0 400 300" style={{ width: '100%', height: '100%' }}>
        <defs>
          <radialGradient id="lg1"><stop offset="0" stopColor="#fff6b0" /><stop offset="0.6" stopColor="#ffaa00" stopOpacity="0.6"/><stop offset="1" stopColor="#ffaa00" stopOpacity="0"/></radialGradient>
          <radialGradient id="lg2"><stop offset="0" stopColor="#ccddff" /><stop offset="0.6" stopColor="#3b82f6" stopOpacity="0.5"/><stop offset="1" stopColor="#3b82f6" stopOpacity="0"/></radialGradient>
          <radialGradient id="lg3"><stop offset="0" stopColor="#ffccee" /><stop offset="0.6" stopColor="#ec4899" stopOpacity="0.4"/><stop offset="1" stopColor="#ec4899" stopOpacity="0"/></radialGradient>
        </defs>
        <rect width="400" height="300" fill="var(--vis-stage-bg)" />

        {/* Stage platform */}
        <ellipse cx="200" cy="220" rx="150" ry="18" fill="url(#lg1)" opacity="0.4" />

        {/* Lights */}
        <circle cx="100" cy="100" r="60" fill="url(#lg1)" />
        <circle cx="300" cy="90" r="50" fill="url(#lg2)" />
        <circle cx="200" cy="160" r="40" fill="url(#lg3)" />

        {/* Light rig crosses */}
        {[[100,100,'#ffaa00'],[300,90,'#3b82f6'],[200,160,'#ec4899']].map(([x,y,c],i) => (
          <g key={i} stroke={c} strokeWidth="1">
            <circle cx={x} cy={y} r="4" fill={c}/>
            <line x1={x-8} y1={y} x2={x+8} y2={y}/>
            <line x1={x} y1={y-8} x2={x} y2={y+8}/>
          </g>
        ))}

        {/* Labels */}
        <g fontFamily="var(--font-mono)" fontSize="8" letterSpacing="1">
          <text x="54" y="172" fill="#ffaa00">KEY · 4200K · 800W</text>
          <text x="258" y="160" fill="#3b82f6">FILL · 6500K · 400W</text>
          <text x="158" y="210" fill="#ec4899">RIM · 5000K · 200W</text>
        </g>

        <text x="20" y="285" fill="var(--fg-mute)" fontFamily="var(--font-mono)" fontSize="8" letterSpacing="1">LIGHT_RIG.V3 · INTENSITY · COLOR · SHAPE · 1:1</text>
      </svg>
    </div>
  );
}

// Vis 6 — Speed (benchmark bar chart)
function VisSpeed() {
  const [animate, setAnimate] = useState2(false);
  useEffect2(() => {
    const o = new IntersectionObserver((entries) => {
      entries.forEach(e => { if (e.isIntersecting) setAnimate(true); });
    }, { threshold: 0.3 });
    const el = document.getElementById('vis-speed');
    if (el) o.observe(el);
    return () => o.disconnect();
  }, []);
  const bars = [
    { l: 'V1.0', v: 30, t: '18.4s' },
    { l: 'V2.0', v: 62, t: '7.2s' },
    { l: 'V3.0', v: 100, t: '2.1s', hi: true },
  ];
  return (
    <div id="vis-speed" style={{ width: '100%', height: '100%', padding: 28, display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
        <div className="mono" style={{ color: 'var(--fg-mute)', fontSize: 10 }}>EXPORT · 1.2GB SCENE</div>
        <div className="mono" style={{ color: 'var(--accent)', fontSize: 10 }}>8.7× FASTER</div>
      </div>
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 14, justifyContent: 'center' }}>
        {bars.map((b, i) => (
          <div key={i}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6, fontFamily: 'var(--font-mono)', fontSize: 10, letterSpacing: 1 }}>
              <span style={{ color: b.hi ? 'var(--accent)' : 'var(--fg-dim)' }}>{b.l}</span>
              <span style={{ color: b.hi ? 'var(--accent)' : 'var(--fg-mute)' }}>{b.t}</span>
            </div>
            <div style={{ height: 28, background: 'var(--bg)', border: '1px solid var(--line)', borderRadius: 4, overflow: 'hidden', position: 'relative' }}>
              <div style={{
                height: '100%',
                width: animate ? `${b.v}%` : '0%',
                background: b.hi ? 'linear-gradient(90deg, var(--accent-deep), var(--accent))' : 'var(--line-strong)',
                transition: `width 1.2s cubic-bezier(0.16,1,0.3,1) ${i * 0.15}s`
              }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// Vis 7 — Cloud updates (pulsing cloud + version log)
function VisCloud() {
  const [n, setN] = useState2(0);
  useEffect2(() => {
    const t = setInterval(() => setN(x => (x + 1) % 4), 2500);
    return () => clearInterval(t);
  }, []);
  const versions = [
    { v: '3.0.4', d: '几何节点优化', new: true },
    { v: '3.0.3', d: 'VFX 协议升级' },
    { v: '3.0.2', d: '骨骼迁移修复' },
    { v: '3.0.1', d: '运动图形支持' },
  ];
  return (
    <div style={{ width: '100%', height: '100%', padding: 28, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
      <div style={{ position: 'relative', borderRadius: 12, border: '1px solid var(--line)', background: 'radial-gradient(circle at 50% 50%, rgba(139,92,246,0.2), transparent 60%)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <svg viewBox="0 0 120 120" style={{ width: '75%', height: '75%' }}>
          {[40, 28, 16].map((r, i) => (
            <circle key={i} cx="60" cy="60" r={r} fill="none" stroke="var(--accent)" strokeWidth="1" opacity={0.2 + (n === i ? 0.6 : 0)} style={{ transition: 'opacity .4s' }} />
          ))}
          <circle cx="60" cy="60" r="6" fill="var(--accent)" />
          <text x="60" y="110" textAnchor="middle" fill="var(--fg-mute)" fontFamily="var(--font-mono)" fontSize="6" letterSpacing="1">SYNCTOOLS CLOUD</text>
        </svg>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        <div className="mono" style={{ color: 'var(--fg-mute)', fontSize: 10, marginBottom: 4 }}>UPDATES · AUTO</div>
        {versions.map((v, i) => (
          <div key={i} style={{ padding: '10px 12px', border: '1px solid var(--line)', borderRadius: 6, background: 'var(--bg)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', position: 'relative' }}>
            <div>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: v.new ? 'var(--accent)' : 'var(--fg)' }}>v{v.v}</div>
              <div className="cn" style={{ fontSize: 11, color: 'var(--fg-mute)', marginTop: 2 }}>{v.d}</div>
            </div>
            {v.new && <div className="mono" style={{ background: 'var(--accent)', color: '#120520', padding: '2px 6px', borderRadius: 3, fontSize: 8, letterSpacing: 1, fontWeight: 700 }}>NEW</div>}
          </div>
        ))}
      </div>
    </div>
  );
}

Object.assign(window, { VisTransform, VisMaterial, VisAnimation, VisParams, VisLighting, VisSpeed, VisCloud });
