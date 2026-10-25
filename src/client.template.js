// DSH TNOLAR Theme: dependency-free client plugin.
// It runs only in the browser. The animated document is sandboxed in a srcdoc iframe.
// The build script replaces the HTML placeholder with a JavaScript string literal.
export const name = 'dsh-theme-tnolar';
const ANIMATION_HTML = __STARTUP_HTML_JSON__;
const THEME_CSS = __TNOLAR_THEME_CSS_JSON__;
const PREFERENCE_KEY = 'dsh-theme-tnolar:enabled';
const THEME_KEY = 'dsh-theme-tnolar:theme-enabled';
const OVERLAY_ID = 'dsh-theme-tnolar-overlay';
const THEME_STYLE_ID = 'dsh-theme-tnolar-theme-style';
const MAX_DURATION_MS = 120000; // interactive startup: fail open after a long idle period
let current = null;


function themeEnabled() {
  try { return localStorage.getItem(THEME_KEY) !== 'false'; }
  catch { return true; }
}

function installThemeStyles() {
  if (typeof document === 'undefined' || !themeEnabled()) return () => {};
  if (document.getElementById(THEME_STYLE_ID)) return () => {};
  const previousThemeMarker = document.documentElement.getAttribute('data-tnolar-theme');
  const style = document.createElement('style');
  style.id = THEME_STYLE_ID;
  style.textContent = THEME_CSS;
  document.head.append(style);
  document.documentElement.setAttribute('data-tnolar-theme', '1');
  return () => {
    style.remove();
    if (document.documentElement.getAttribute('data-tnolar-theme') === '1') {
      if (previousThemeMarker === null) document.documentElement.removeAttribute('data-tnolar-theme');
      else document.documentElement.setAttribute('data-tnolar-theme', previousThemeMarker);
    }
  };
}

function shouldAutoplay() {
  if (typeof window === 'undefined' || typeof document === 'undefined') return false;
  if (window.top !== window.self) return false;
  // A hot-installed plugin must not suddenly cover an established session.
  if (performance.now() > 30000) return false;
  try { return localStorage.getItem(PREFERENCE_KEY) !== 'false'; }
  catch { return true; }
}

function createOverlay() {
  if (current !== null) return current;
  if (!document.body) return null;
  const oldOverlay = document.getElementById(OVERLAY_ID);
  if (oldOverlay) return null;

  const appRoot = document.getElementById('root');
  const previousInert = Boolean(appRoot?.inert);
  const focused = document.activeElement instanceof HTMLElement ? document.activeElement : null;
  const outer = document.createElement('div');
  outer.id = OVERLAY_ID;
  outer.setAttribute('role', 'dialog');
  outer.setAttribute('aria-label', 'DSH 全球协同网络主题启动动画');
  outer.setAttribute('aria-modal', 'true');
  outer.style.cssText = 'position:fixed;inset:0;z-index:2147483646;background:#020b10;overflow:hidden;opacity:1;transition:opacity 300ms ease';
  const shadow = outer.attachShadow({ mode: 'open' });
  const css = document.createElement('style');
  css.textContent = `
    :host{all:initial;display:block}
    .wrap{width:100%;height:100%;position:relative;background:#020b10;color:#b9e7e3;font-family:Consolas,monospace}
    iframe{position:absolute;inset:0;width:100%;height:100%;border:0;background:#020b10}
    .skip{position:absolute;right:clamp(16px,2.8vw,48px);top:clamp(12px,2.2vh,32px);border:1px solid #5ba5a9;
      background:rgba(1,15,20,.88);color:#b5e9e4;padding:10px 15px;font:600 13px Consolas,monospace;
      letter-spacing:.08em;cursor:pointer;z-index:3;box-shadow:0 0 24px rgba(20,150,151,.22)}
    .skip:hover,.skip:focus-visible{background:#134049;border-color:#9afaf1;outline:2px solid #9afaf1;outline-offset:2px}
    .label{position:absolute;left:24px;bottom:12px;font:10px Consolas,monospace;color:#74b6b5;letter-spacing:.2em;
      opacity:.45;pointer-events:none;z-index:2}
    @media (prefers-reduced-motion:reduce){iframe{opacity:1}}
  `;
  const wrap = document.createElement('div');
  wrap.className = 'wrap';
  const frame = document.createElement('iframe');
  frame.title = 'DSH 启动序列：9 国首都 14 条定向链路';
  frame.setAttribute('sandbox', 'allow-scripts'); // no same-origin, no top-level navigation
  frame.setAttribute('referrerpolicy', 'no-referrer');
  const skip = document.createElement('button');
  skip.type = 'button';
  skip.className = 'skip';
  skip.textContent = '跳过动画 / ESC';
  const label = document.createElement('div');
  label.className = 'label';
  label.textContent = 'DSH / THEMED WORLD STARTUP · VISUAL SIMULATION';
  wrap.append(frame, skip, label);
  shadow.append(css, wrap);

  let done = false;
  let closeTimer = 0;
  let watchdog = 0;
  let cleanTimer = 0;
  function restore() {
    if (appRoot) appRoot.inert = previousInert;
    if (focused && focused.isConnected && typeof focused.focus === 'function') {
      try { focused.focus({preventScroll:true}); } catch { /* non-fatal */ }
    }
  }
  function cleanup() {
    window.clearTimeout(closeTimer);
    window.clearTimeout(watchdog);
    window.clearTimeout(cleanTimer);
    window.removeEventListener('message', onMessage);
    window.removeEventListener('keydown', onKeyDown, true);
    skip.removeEventListener('click', close);
    frame.removeEventListener('error', close);
    outer.remove();
    restore();
    current = null;
  }
  function close() {
    if (done) return;
    done = true;
    outer.style.opacity = '0';
    // Do not leave the app inert while fading out or if CSS transitions are suppressed.
    cleanTimer = window.setTimeout(cleanup, 320);
  }
  function onKeyDown(e) { if (e.key === 'Escape') close(); }
  function onMessage(event) {
    if (event.source !== frame.contentWindow || !event.data || event.data.source !== 'dsh-theme-tnolar') return;
    if (event.data.event === 'enter' || event.data.event === 'skip') close();
  }
  current = { close, cleanup };
  window.addEventListener('message', onMessage);
  window.addEventListener('keydown', onKeyDown, true);
  skip.addEventListener('click', close);
  frame.addEventListener('error', close);
  watchdog = window.setTimeout(close, MAX_DURATION_MS);
  if (appRoot) appRoot.inert = true;
  document.body.append(outer);
  frame.srcdoc = ANIMATION_HTML;
  return current;
}

function runOnce() {
  if (!shouldAutoplay() || document.documentElement.dataset.dshTnolarShown === '1') return;
  document.documentElement.dataset.dshTnolarShown = '1';
  try { createOverlay(); }
  catch (error) { console.warn('[dsh-theme-tnolar] unable to start animation', error); current?.cleanup(); }
}

export function apply(ctx) {
  let disposed = false;
  const onReady = () => { if (!disposed) runOnce(); };
  const setup = () => {
    let removeTheme = installThemeStyles();
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', onReady, {once:true});
    else onReady();
    // Optional programmatic control; no UI service injection is necessary.
    const controller = Object.freeze({
      replay: () => createOverlay(),
      skip: () => current?.close(),
      setEnabled: (value) => { try { localStorage.setItem(PREFERENCE_KEY, value ? 'true' : 'false'); } catch {} },
      setThemeEnabled: (value) => {
        try { localStorage.setItem(THEME_KEY, value ? 'true' : 'false'); } catch {}
        removeTheme();
        removeTheme = value ? installThemeStyles() : () => {};
      },
    });
    window.DSHTNOLAR = controller;
    return () => {
      disposed = true;
      document.removeEventListener('DOMContentLoaded', onReady);
      current?.cleanup();
      removeTheme();
      if (window.DSHTNOLAR === controller) delete window.DSHTNOLAR;
    };
  };
  if (ctx && typeof ctx.effect === 'function') ctx.effect(setup, 'dsh-theme-tnolar: boot overlay');
  else setup();
}