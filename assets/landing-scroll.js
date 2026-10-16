(() => {
  const win = window.parent;
  const doc = win.document;
  win.fishstopScrollCleanup?.();
  const scroller = doc.querySelector('[data-testid="stMain"]') || doc.querySelector('.main');
  if (!scroller) return;
  // Keep this state in the parent: the component iframe is recreated on reruns.
  const params = new URLSearchParams(win.location.search);
  for (const [key, active] of [['language', params.get('lang') === 'it'], ['theme', params.get('theme') === 'dark']]) {
    doc.querySelector(`.st-key-${key}_switch button`)?.setAttribute('aria-pressed', String(active));
  }
  const state = win.fishstopPreferences ||= {};
  let restoreFrame = 0;
  let restoreUntil = 0;
  const panelSelector = '.st-key-overview_panel,.st-key-download_panel';
  const restore = () => {
    if (!state.position) return;
    const panel = state.position.panel && doc.querySelector(state.position.panel);
    const target = panel
      ? panel.getBoundingClientRect().top - scroller.getBoundingClientRect().top + scroller.scrollTop + state.position.offset
      : state.position.top;
    scroller.scrollTop = target;
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
  const onPreferenceClick = event => {
    if (!event.target.closest?.('.st-key-preferences button')) return;
    win.cancelAnimationFrame(frame);
    win.clearTimeout(pending);
    win.cancelAnimationFrame(restoreFrame);
    const panels = [...doc.querySelectorAll(panelSelector)];
    const panel = panels.reduce((best, el) =>
      Math.abs(el.getBoundingClientRect().top - scroller.getBoundingClientRect().top) <
      Math.abs(best.getBoundingClientRect().top - scroller.getBoundingClientRect().top) ? el : best, panels[0]);
    state.position = {
      top: scroller.scrollTop,
      panel: panel ? (panel.classList.contains('st-key-download_panel') ? '.st-key-download_panel' : '.st-key-overview_panel') : null,
      offset: panel ? scroller.getBoundingClientRect().top - panel.getBoundingClientRect().top : 0,
    };
    scroller.style.scrollSnapType = 'none';
    scroller.style.scrollBehavior = 'auto';
  };
  doc.addEventListener('click', onPreferenceClick, true);
  scroller.dataset.fishstopSnap = 'ready';
  let lockedUntil = 0;
  let frame = 0;
  let pending = 0;
  const jump = target => {
    const start = scroller.scrollTop;
    const end = Math.max(0, Math.min(target, scroller.scrollHeight - scroller.clientHeight));
    const began = win.performance.now();
    scroller.style.scrollSnapType = 'none';
    scroller.style.scrollBehavior = 'auto';
    lockedUntil = Date.now() + 620;
    const tick = now => {
      const progress = Math.min(1, (now - began) / 420);
      const ease = 1 - Math.pow(1 - progress, 3);
      scroller.scrollTop = start + (end - start) * ease;
      if (progress < 1) frame = win.requestAnimationFrame(tick);
      else {
        scroller.style.scrollSnapType = '';
        scroller.style.scrollBehavior = '';
      }
    };
    frame = win.requestAnimationFrame(tick);
  };
  const scheduleJump = target => {
    // Hold the current section briefly, then animate one deliberate transition.
    lockedUntil = Date.now() + 800;
    pending = win.setTimeout(() => {
      pending = 0;
      jump(target);
    }, 180);
  };
  const onWheel = (event) => {
    if (event.ctrlKey || Math.abs(event.deltaY) < 1 || Math.abs(event.deltaX) > Math.abs(event.deltaY)) return;
    if (event.target.closest?.('.st-key-preferences')) return;
    if (win.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    const panels = [...doc.querySelectorAll('.st-key-overview_panel,.st-key-download_panel')];
    if (panels.length !== 2) return;
    const now = Date.now();
    if (now < lockedUntil) { event.preventDefault(); return; }
    const top = scroller.getBoundingClientRect().top;
    const positions = panels.map(el => el.getBoundingClientRect().top - top + scroller.scrollTop);
    const current = scroller.scrollTop;
    const index = current >= (positions[0] + positions[1]) / 2 ? 1 : 0;
    const direction = event.deltaY > 0 ? 1 : -1;
    // Tall download sections must scroll back to their top before leaving them.
    if (index === 1 && direction < 0 && current > positions[1] + 2) return;
    const next = index + direction;
    if (next < 0 || next >= panels.length) return;
    event.preventDefault();
    scheduleJump(positions[next]);
  };
  let touchStart = null;
  const onTouchStart = event => {
    touchStart = event.touches.length === 1
      ? {x: event.touches[0].clientX, y: event.touches[0].clientY} : null;
  };
  const onTouchMove = event => {
    if (event.target.closest?.('.st-key-preferences')) return;
    if (event.touches.length !== 1) { touchStart = null; return; }
    if (touchStart === null || win.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    const delta = touchStart.y - event.touches[0].clientY;
    if (Math.abs(touchStart.x - event.touches[0].clientX) > Math.abs(delta)) return;
    if (Date.now() < lockedUntil) { event.preventDefault(); return; }
    if (Math.abs(delta) < 20) return;
    const panels = [...doc.querySelectorAll('.st-key-overview_panel,.st-key-download_panel')];
    if (panels.length !== 2) return;
    const positions = panels.map(el => el.getBoundingClientRect().top - scroller.getBoundingClientRect().top + scroller.scrollTop);
    const index = scroller.scrollTop >= (positions[0] + positions[1]) / 2 ? 1 : 0;
    if (index === 1 && delta < 0 && scroller.scrollTop > positions[1] + 2) return;
    const next = index + Math.sign(delta);
    if (next < 0 || next > 1) return;
    event.preventDefault();
    touchStart = null;
    scheduleJump(positions[next]);
  };
  doc.addEventListener('wheel', onWheel, {passive: false, capture: true});
  scroller.addEventListener('touchstart', onTouchStart, {passive: true});
  scroller.addEventListener('touchmove', onTouchMove, {passive: false});
  win.fishstopScrollCleanup = () => {
    win.cancelAnimationFrame(frame);
    win.cancelAnimationFrame(restoreFrame);
    win.clearTimeout(pending);
    doc.removeEventListener('click', onPreferenceClick, true);
    scroller.style.scrollSnapType = '';
    scroller.style.scrollBehavior = '';
    doc.removeEventListener('wheel', onWheel, {capture: true});
    scroller.removeEventListener('touchstart', onTouchStart);
    scroller.removeEventListener('touchmove', onTouchMove);
  };
})();
