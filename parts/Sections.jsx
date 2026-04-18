/* global React, VisTransform, VisMaterial, VisAnimation, VisParams, VisLighting, VisSpeed, VisCloud */
const { useState: useState3, useEffect: useEffect3, useRef: useRef3 } = React;

function Features() {
  const rows = [
    { num: '01', title: '单击同步', titleEn: 'One-Click Transform', lead: '超级轻松，转换只需单击。此刻开始无需再手动设置繁琐的比例、轴向、层级结构等，能帮您节省大量重复操作。你可以专注于真正重要的事情 —— 你的创作愿景。', tags: ['AXIS', 'HIERARCHY', 'SCALE', 'PIVOT'], vis: <VisTransform /> },
    { num: '02', title: '材质全面互通', titleEn: 'Material · Fully Bridged', lead: '自研先进的材质转换引擎，精准还原着色器结构层级与逻辑，无论用是基础材质还是复杂的多层材质，都能确保视觉一致。', tags: ['PBR', 'MULTI-LAYER', 'SHADER GRAPH', '1:1 FIDELITY'], vis: <VisMaterial />, reverse: true },
    { num: '03', title: '动静皆为自然', titleEn: 'Motion · Effortlessly Alive', lead: '体验流畅且如此精准的动画数据传输。无论是模型还是骨骼流体、运动图形还是几何节点，多复杂都能实现流畅且高保真的动画数据互导。', tags: ['RIG', 'VFX', 'GEO NODES', 'MOGRAPH'], vis: <VisAnimation /> },
    { num: '04', title: '核心参数精准衔接', titleEn: 'Parameters · In Sync', lead: '通过一键同步核心参数，您可以轻松保持项目设置一致性。无论是画幅、焦距、分辨率、宽高比还是帧率，所有参数都能轻松对齐。', tags: ['RESOLUTION', 'FPS', 'FOCAL', 'ACES'], vis: <VisParams />, reverse: true },
    { num: '05', title: '光影流转，臻美再现', titleEn: 'Lighting · Faithfully Restored', lead: '忠实传承每一寸微妙光影，深度还原灯光信息，包括灯光尺寸、类型及形状。无损还原强度、色彩、图像纹理。', tags: ['INTENSITY', 'COLOR', 'SHAPE', 'TEXTURE'], vis: <VisLighting /> },
    { num: '06', title: '导出速度再升级', titleEn: 'Export · Radically Faster', lead: '在速度与稳定之间寻求理想平衡。新一代互导引擎，互导效率大幅提升，复杂动画、庞大场景将一键完成。更快响应更少等待，只为纤毫无间。', tags: ['8.7× FASTER', 'PARALLEL', 'STABLE', 'LIGHTWEIGHT'], vis: <VisSpeed />, reverse: true },
    { num: '07', title: '云端更新，无限进步', titleEn: 'Cloud Updates · Always Growing', lead: '每月自动推送插件更新，在每一处细节精微入妙，始终保持永久更新，让我们一起为未来的无限可能蓄势待发。', tags: ['MONTHLY', 'AUTO', 'ZERO-DOWNTIME'], vis: <VisCloud /> },
  ];

  return (
    <section className="features" id="features">
      <div className="wrap">
        <div className="feat-header reveal">
          <div className="eyebrow">// 02 · 核心能力</div>
          <h2>
            <span className="cn">无界衔接，</span><br />
            <span className="serif">core capabilities </span><span className="cn">尽在一处</span>
          </h2>
          <p className="cn">新一代数据协议，配合自研互导引擎，让每一次资产迁移都如同在同一软件中拖拽般自然。七大核心能力，为复杂项目协作而生。</p>
        </div>
        {rows.map((r, i) => (
          <div className={`feat-row reveal ${r.reverse ? 'reverse' : ''}`} key={i}>
            <div className="feat-text">
              <div className="num">/ {r.num} · {r.titleEn}</div>
              <h3><span className="cn">{r.title}</span></h3>
              <p className="lead cn">{r.lead}</p>
              <div className="tags">{r.tags.map((t, j) => <span className="tag" key={j}>{t}</span>)}</div>
            </div>
            <div className="feat-vis">{r.vis}</div>
          </div>
        ))}
      </div>
    </section>
  );
}

function Stats() {
  return (
    <section className="stats reveal" id="stats">
      <div className="stats-halo" />
      <div className="wrap stats-inner">
        <div className="mono" style={{ color: 'var(--fg-mute)', marginBottom: 24 }}>// 03 · 此刻，连接世界</div>
        <h2>
          <span className="cn">放眼全球，</span>
          <span className="serif">the future </span>
          <span className="cn">已来。</span>
        </h2>
        <p style={{ maxWidth: 640, margin: '28px auto 0', color: 'var(--fg-dim)', fontSize: 16 }} className="cn">
          来自 162 个国家的超过 2 万名设计师、200 余家企业已将 SyncTools 纳入核心工作流程。不仅涵盖初创团队，也包含国内外大型互联网公司、知名动态设计工作室与企业部门。
        </p>
        <div className="stats-grid">
          <div className="cell">
            <div className="big">20,000<span className="plus">+</span></div>
            <div className="lbl">Designers</div>
            <div className="desc cn">全球 3D 艺术家与动态设计师</div>
          </div>
          <div className="cell">
            <div className="big">162</div>
            <div className="lbl">Countries</div>
            <div className="desc cn">覆盖六大洲的专业用户</div>
          </div>
          <div className="cell">
            <div className="big">15,000<span className="plus">+</span></div>
            <div className="lbl">3D Artists</div>
            <div className="desc cn">已纳入核心工作流程</div>
          </div>
          <div className="cell">
            <div className="big">80<span className="plus">+</span></div>
            <div className="lbl">Studios</div>
            <div className="desc cn">知名企业与动态设计工作室</div>
          </div>
        </div>
      </div>
    </section>
  );
}

function Testimonials() {
  const quotes = [
    { q: '这是我遇到过最热衷于收集用户反馈以及建议的开发团队了。从插件发布到功能逐步完善，可以看到用户的反馈在新版的发布得到了体现。这可能和开发者们本身也是使用者有关吧。最后，非常感谢各位开发者不辞辛苦的持续付出。', n: 'Paul Nicklen', r: '资深动态设计师' },
    { q: '非常优秀，但我更期待能达到颠覆般的优秀。插件我用的最多的就是灯光插件。那真是用过的人都说好，优化了我很多调整灯光时浪费的时间。', n: '弈星', r: '网易美术总监' },
    { q: '简直是黑科技插件！功能很强大！当你对接不同工作流的团队而手足无措时，每次总能用这个顺利解决，是个好东西！', n: 'BeSSeL', r: '高级场景设计师' },
  ];
  return (
    <section className="testi reveal" id="testimonials">
      <div className="wrap">
        <div className="feat-header">
          <div className="eyebrow">// 04 · 听听他们怎么说</div>
          <h2><span className="cn">来自创作者的</span><br/><span className="serif">real stories.</span></h2>
        </div>
        <div className="testi-grid">
          {quotes.map((t, i) => (
            <div className="testi-card" key={i}>
              <div className="quote-mark">"</div>
              <p className="quote">{t.q}</p>
              <div className="who">
                <div className="name">{t.n}</div>
                <div className="role cn">{t.r}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function Pricing() {
  const [copied, setCopied] = useState3(false);
  const copy = () => {
    navigator.clipboard?.writeText('SYNCTOOLS');
    setCopied(true);
    setTimeout(() => setCopied(false), 1800);
  };
  return (
    <section className="pricing reveal" id="pricing">
      <div className="pricing-halo" />
      <div className="wrap pricing-inner">
        <div className="pricing-card">
          <div>
            <div className="eyebrow">// 05 · LIMITED OFFER</div>
            <h2><span className="cn">未来已来，</span><br/><span className="serif">at 80% off.</span></h2>
            <p className="cn">
              前往官方商城购买，将享受专业客服 1 对 1 支持，由技术专家帮您选购，同时提供技术指导和安装帮助。购买即获得订单金额 5% 积分返还等多项专属权益。
            </p>
            <div style={{ marginTop: 28, display: 'flex', flexWrap: 'wrap', gap: 20, fontFamily: 'var(--font-mono)', fontSize: 11, letterSpacing: '0.08em', textTransform: 'uppercase', color: 'var(--fg-dim)' }}>
              <div>✓ 终身授权</div>
              <div>✓ 云端更新</div>
              <div>✓ 1:1 技术支持</div>
              <div>✓ 5% 积分返还</div>
            </div>
          </div>
          <div className="pricing-right">
            <div className="price-tile">
              <div className="tag">-80%</div>
              <div className="mono" style={{ color: 'var(--fg-mute)', marginBottom: 12 }}>SYNCTOOLS PRO · V3.0</div>
              <div className="row">
                <span className="now">¥398</span>
                <span className="old">¥1988</span>
                <span className="unit">/ 终身</span>
              </div>
              <div className="coupon">
                <div className="code">#SYNCTOOLS</div>
                <button className="copy" onClick={copy}>{copied ? 'Copied ✓' : 'Copy'}</button>
              </div>
              <div className="bullets">
                <div className="b cn">全 DCC 流式协作支持</div>
                <div className="b cn">主流渲染器无缝兼容</div>
                <div className="b cn">每月自动功能更新</div>
                <div className="b cn">专业客服 1 对 1 咨询</div>
              </div>
              <a className="btn btn-accent buy" href="#">
                Buy Now →
              </a>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer className="footer">
      <div className="wrap">
        <div className="footer-grid">
          <div className="footer-brand">
            <div className="logo">
              <div className="logo-mark"><LogoMark /></div>
              SyncTools
            </div>
            <p className="tag cn">Transforming everything has never been so simple. 无界衔接，此刻连接世界。</p>
          </div>
          <div>
            <h4>Product</h4>
            <div className="links">
              <a href="#features">Features</a>
              <a href="#pricing">Pricing</a>
              <a href="#">Changelog</a>
              <a href="#">Roadmap</a>
            </div>
          </div>
          <div>
            <h4>Resources</h4>
            <div className="links">
              <a href="#">Documentation</a>
              <a href="#">Tutorials</a>
              <a href="#">Community</a>
              <a href="#">Support</a>
            </div>
          </div>
          <div>
            <h4>Company</h4>
            <div className="links">
              <a href="#">About</a>
              <a href="#">Blog</a>
              <a href="#">Press</a>
              <a href="#">Contact</a>
            </div>
          </div>
        </div>
        <div className="footer-bottom">
          <div>© 2026 SyncTools · All rights reserved</div>
          <div>v3.0.4 · Built with care for 3D artists</div>
        </div>
      </div>
    </footer>
  );
}

Object.assign(window, { Features, Stats, Testimonials, Pricing, Footer });
