/* global React, PromoBar, Nav, Hero, DccRail, Features, Stats, Testimonials, Pricing, Footer */
const { useState: useState4, useEffect: useEffect4 } = React;

const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{
  "theme": "light"
}/*EDITMODE-END*/;

function App() {
  const [theme, setTheme] = useState4(TWEAK_DEFAULTS.theme);
  const [tweaksOn, setTweaksOn] = useState4(false);

  useEffect4(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  // Tweaks protocol
  useEffect4(() => {
    const onMsg = (e) => {
      const d = e.data || {};
      if (d.type === '__activate_edit_mode') setTweaksOn(true);
      if (d.type === '__deactivate_edit_mode') setTweaksOn(false);
    };
    window.addEventListener('message', onMsg);
    window.parent.postMessage({ type: '__edit_mode_available' }, '*');
    return () => window.removeEventListener('message', onMsg);
  }, []);

  // Scroll reveal
  useEffect4(() => {
    const els = document.querySelectorAll('.reveal');
    const io = new IntersectionObserver((entries) => {
      entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('in'); });
    }, { threshold: 0.1, rootMargin: '0px 0px -80px 0px' });
    els.forEach(el => io.observe(el));
    return () => io.disconnect();
  }, []);

  const toggleTheme = () => {
    const next = theme === 'dark' ? 'light' : 'dark';
    setTheme(next);
    window.parent.postMessage({ type: '__edit_mode_set_keys', edits: { theme: next } }, '*');
  };

  return (
    <>
      <PromoBar />
      <Nav />
      <Hero />
      <DccRail />
      <Features />
      <Stats />
      <Testimonials />
      <Pricing />
      <Footer />
      <div className={`tweaks ${tweaksOn ? 'on' : ''}`}>
        <span className="title">Theme</span>
        <span style={{ color: theme === 'light' ? 'var(--accent)' : 'var(--fg-mute)' }}>Light</span>
        <button className={`toggle ${theme === 'dark' ? 'on' : ''}`} onClick={toggleTheme} />
        <span style={{ color: theme === 'dark' ? 'var(--accent)' : 'var(--fg-mute)' }}>Dark</span>
      </div>
    </>
  );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
