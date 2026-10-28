(() => {
  const win = window.parent;
  const doc = win.document;
  const root = doc.documentElement;
  win.fishstopScrollCleanup?.();
  const prefs = typeof FS_PREFS === 'object' ? FS_PREFS : {};
  // Keep this state in the parent: the component iframe is recreated on reruns.
  const state = win.fishstopPreferences ||= {};
  const reducedMotion = () => win.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // --- Preferences -----------------------------------------------------------
  // The page paints from data-fs-theme / data-fs-lang on <html>. A click flips
  // them at once; the rerun that follows only confirms the same values, so the
  // stylesheet never changes underneath the user (that was the flicker).
  const syncPressed = () => {
    doc.querySelector('.st-key-language_switch button')?.setAttribute('aria-pressed', String(root.dataset.fsLang === 'it'));
    doc.querySelector('.st-key-theme_switch button')?.setAttribute('aria-pressed', String(root.dataset.fsTheme === 'dark'));
  };
  const applyServer = (attribute, key) => {
    const value = prefs[key];
    if (!value) return;
    const expected = state.expected?.[key];
    // A newer click is still on its way to the server: keep what the user sees.
    if (expected && expected.value !== value && Date.now() - expected.at < 4000) return;
    if (state.expected) delete state.expected[key];
    root.dataset[attribute] = value;
  };
  applyServer('fsTheme', 'theme');
  applyServer('fsLang', 'lang');
  syncPressed();

  const setTheme = value => {
    const flip = () => { root.dataset.fsTheme = value; syncPressed(); };
    // One crossfade of the whole page instead of hundreds of separate colour
    // transitions; browsers without view transitions switch instantly.
    if (doc.startViewTransition && !reducedMotion()) {
      try { doc.startViewTransition(flip); return; } catch (error) { /* fall through */ }
    }
    flip();
  };

  const scroller = doc.querySelector('[data-testid="stMain"]') || doc.querySelector('.main');
  let restoreFrame = 0;
  let restoreUntil = 0;
  let frame = 0;
  const panelSelector = '.st-key-overview_panel,.st-key-download_panel';
  const panelTops = () => {
    const top = scroller.getBoundingClientRect().top;
    return [...doc.querySelectorAll(panelSelector)].map(el => el.getBoundingClientRect().top - top + scroller.scrollTop);
  };

  const onPreferenceClick = event => {
    const button = event.target.closest?.('.st-key-preferences button');
    if (!button) return;
    state.expected ||= {};
    if (button.closest('.st-key-theme_switch')) {
      const next = root.dataset.fsTheme === 'dark' ? 'light' : 'dark';
      state.expected.theme = {value: next, at: Date.now()};
      setTheme(next);
      return;
    }
    const next = root.dataset.fsLang === 'it' ? 'en' : 'it';
    state.expected.lang = {value: next, at: Date.now()};
    root.dataset.fsLang = next;
    syncPressed();
    if (!scroller) return;
    // New copy can change section heights: remember where the reader is.
    win.cancelAnimationFrame(frame);
    win.cancelAnimationFrame(restoreFrame);
    const panels = [...doc.querySelectorAll(panelSelector)];
    const top = scroller.getBoundingClientRect().top;
    const panel = panels.reduce((best, el) =>
      Math.abs(el.getBoundingClientRect().top - top) < Math.abs(best.getBoundingClientRect().top - top) ? el : best, panels[0]);
    state.position = {
      top: scroller.scrollTop,
      panel: panel ? (panel.classList.contains('st-key-download_panel') ? '.st-key-download_panel' : '.st-key-overview_panel') : null,
      offset: panel ? top - panel.getBoundingClientRect().top : 0,
    };
    scroller.style.scrollSnapType = 'none';
    scroller.style.scrollBehavior = 'auto';
  };
  doc.addEventListener('click', onPreferenceClick, true);

  if (!scroller) {
    win.fishstopScrollCleanup = () => doc.removeEventListener('click', onPreferenceClick, true);
    return;
  }

  const restore = () => {
    if (!state.position) return;
    const panel = state.position.panel && doc.querySelector(state.position.panel);
    scroller.scrollTop = panel
      ? panel.getBoundingClientRect().top - scroller.getBoundingClientRect().top + scroller.scrollTop + state.position.offset
      : state.position.top;
    if (win.performance.now() < restoreUntil) restoreFrame = win.requestAnimationFrame(restore);
    else {
      state.position = null;
      scroller.style.scrollSnapType = '';
      scroller.style.scrollBehavior = '';
    }
  };
  if (state.position) {
    scroller.style.scrollSnapType = 'none';
    scroller.style.scrollBehavior = 'auto';
    restoreUntil = win.performance.now() + 500;
    restoreFrame = win.requestAnimationFrame(restore);
  }
  scroller.dataset.fishstopSnap = 'ready';
  // On first load the browser can snap while Streamlit is still collapsing its
  // style blocks, leaving the hero off-centre. Align the first panel once.
  if (!state.settled && !state.position) {
    state.settled = true;
    const tops = panelTops();
    if (tops.length === 2 && scroller.scrollTop < tops[1] / 2) scroller.scrollTop = tops[0];
  }

  // --- Section jumps ---------------------------------------------------------
  const JUMP_MS = 640;
  const LOCK_CAP_MS = 1300;
  let jumpStarted = 0;
  let lockedUntil = 0;
  const easeInOut = p => (p < 0.5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2);
  const jump = target => {
    win.cancelAnimationFrame(frame);
    const start = scroller.scrollTop;
    const end = Math.max(0, Math.min(target, scroller.scrollHeight - scroller.clientHeight));
    const began = win.performance.now();
    jumpStarted = Date.now();
    lockedUntil = jumpStarted + JUMP_MS + 140;
    scroller.style.scrollSnapType = 'none';
    scroller.style.scrollBehavior = 'auto';
    if (reducedMotion() || Math.abs(end - start) < 2) {
      scroller.scrollTop = end;
      scroller.style.scrollSnapType = '';
      scroller.style.scrollBehavior = '';
      return;
    }
    const tick = now => {
      const progress = Math.min(1, (now - began) / JUMP_MS);
      scroller.scrollTop = start + (end - start) * easeInOut(progress);
      if (progress < 1) frame = win.requestAnimationFrame(tick);
      else {
        scroller.style.scrollSnapType = '';
        scroller.style.scrollBehavior = '';
      }
    };
    frame = win.requestAnimationFrame(tick);
  };
  // Trackpads keep sending inertial wheel events after a jump; swallow them
  // while they keep coming (up to a cap) so one gesture moves one section.
  const holdLock = event => {
    const now = Date.now();
    if (now >= lockedUntil) return false;
    event.preventDefault();
    lockedUntil = Math.min(Math.max(lockedUntil, now + 160), jumpStarted + LOCK_CAP_MS);
    return true;
  };
  const targetFor = direction => {
    const positions = panelTops();
    if (positions.length !== 2) return null;
    const current = scroller.scrollTop;
    const index = current >= (positions[0] + positions[1]) / 2 ? 1 : 0;
    // Tall download sections must scroll back to their top before leaving them.
    if (index === 1 && direction < 0 && current > positions[1] + 2) return null;
    const next = index + direction;
    return next < 0 || next >= positions.length ? null : positions[next];
  };
  const onWheel = event => {
    if (event.ctrlKey || Math.abs(event.deltaY) < 1 || Math.abs(event.deltaX) > Math.abs(event.deltaY)) return;
    if (event.target.closest?.('.st-key-preferences')) return;
    if (reducedMotion()) return;
    if (holdLock(event)) return;
    const target = targetFor(event.deltaY > 0 ? 1 : -1);
    if (target === null) return;
    event.preventDefault();
    jump(target);
  };
  let touchStart = null;
  const onTouchStart = event => {
    touchStart = event.touches.length === 1
      ? {x: event.touches[0].clientX, y: event.touches[0].clientY} : null;
  };
  const onTouchMove = event => {
    if (event.target.closest?.('.st-key-preferences')) return;
    if (event.touches.length !== 1) { touchStart = null; return; }
    if (touchStart === null || reducedMotion()) return;
    const delta = touchStart.y - event.touches[0].clientY;
    if (Math.abs(touchStart.x - event.touches[0].clientX) > Math.abs(delta)) return;
    if (Date.now() < lockedUntil) { event.preventDefault(); return; }
    if (Math.abs(delta) < 24) return;
    const target = targetFor(Math.sign(delta));
    if (target === null) return;
    event.preventDefault();
    touchStart = null;
    jump(target);
  };
  const onCueClick = event => {
    const cue = event.target.closest?.('.scroll-cue');
    if (!cue) return;
    event.preventDefault();
    const positions = panelTops();
    if (positions.length === 2) jump(positions[1]);
  };
  doc.addEventListener('wheel', onWheel, {passive: false, capture: true});
  doc.addEventListener('click', onCueClick, true);
  scroller.addEventListener('touchstart', onTouchStart, {passive: true});
  scroller.addEventListener('touchmove', onTouchMove, {passive: false});

  // --- Reveal ----------------------------------------------------------------
  // The download section rises in the first time it enters the viewport. The
  // hidden state is only set while that section is still off screen.
  let observer = null;
  const downloads = doc.querySelector('.st-key-download_panel');
  if (downloads && root.dataset.fsReveal !== 'done' && 'IntersectionObserver' in win) {
    const box = downloads.getBoundingClientRect();
    const view = scroller.getBoundingClientRect();
    const offscreen = box.top > view.bottom - 40;
    if (!offscreen || reducedMotion()) root.dataset.fsReveal = 'done';
    else {
      root.dataset.fsReveal = 'pending';
      observer = new win.IntersectionObserver(entries => {
        if (!entries.some(entry => entry.isIntersecting)) return;
        root.dataset.fsReveal = 'done';
        observer.disconnect();
      }, {root: scroller, threshold: 0.18});
      observer.observe(downloads);
    }
  }

  win.fishstopScrollCleanup = () => {
    win.cancelAnimationFrame(frame);
    win.cancelAnimationFrame(restoreFrame);
    observer?.disconnect();
    doc.removeEventListener('click', onPreferenceClick, true);
    doc.removeEventListener('click', onCueClick, true);
    scroller.style.scrollSnapType = '';
    scroller.style.scrollBehavior = '';
    doc.removeEventListener('wheel', onWheel, {capture: true});
    scroller.removeEventListener('touchstart', onTouchStart);
    scroller.removeEventListener('touchmove', onTouchMove);
  };
})();
