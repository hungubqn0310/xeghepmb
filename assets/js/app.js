/* Xe Ghép An Tâm — tương tác trang (vanilla, không thư viện) */
(() => {
  'use strict';
  const CFG = window.SITE_CONFIG || { phone: '', zalo: '', routes: [] };
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const canHover = matchMedia('(hover: hover) and (pointer: fine)').matches;
  const store = {
    get(k) { try { return JSON.parse(localStorage.getItem(k)); } catch { return null; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch { /* bỏ qua */ } },
  };

  /* ---------- header, menu, road progress ---------- */
  const header = $('[data-header]');
  const toggle = $('.nav-toggle');
  const progress = $('.road-progress');
  const arrive = $('[data-arrive]');
  const parallax = $('[data-parallax]');
  let ticking = false;

  function onScroll() {
    const y = scrollY;
    const max = document.documentElement.scrollHeight - innerHeight;
    const p = max > 0 ? Math.min(1, y / max) : 0;
    header.classList.toggle('is-scrolled', y > 24);
    progress.style.setProperty('--p', p.toFixed(4));
    if (arrive) arrive.classList.toggle('is-on', p > 0.985);
    if (parallax && !reduce && y < innerHeight * 1.2) parallax.style.transform = `translate3d(0,${y * 0.25}px,0)`;
    ticking = false;
  }
  addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
  onScroll();

  function setMenu(open) {
    document.body.classList.toggle('nav-open', open);
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Đóng menu' : 'Mở menu');
    if (open) header.classList.add('is-scrolled'); else onScroll();
  }
  toggle?.addEventListener('click', () => setMenu(!document.body.classList.contains('nav-open')));
  $$('#site-nav a').forEach(a => a.addEventListener('click', () => setMenu(false)));
  addEventListener('keydown', e => { if (e.key === 'Escape') setMenu(false); });

  /* ---------- H2 ScrollFloat: tách từ ---------- */
  $$('[data-float]').forEach(h => {
    const words = h.textContent.trim().split(/\s+/);
    h.setAttribute('aria-label', h.textContent.trim());
    h.innerHTML = words.map((w, i) => `<span class="fw" aria-hidden="true" style="--w:${i}">${w}</span>`).join(' ');
  });

  /* ---------- reveal ---------- */
  const groups = new Map();
  $$('[data-reveal]').forEach(el => {
    const parent = el.parentElement;
    const n = groups.get(parent) || 0;
    el.style.setProperty('--stagger', Math.min(n, 6));
    groups.set(parent, n + 1);
  });
  const io = new IntersectionObserver(entries => entries.forEach(e => {
    if (!e.isIntersecting) return;
    e.target.classList.add('is-in');
    io.unobserve(e.target);
  }), { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
  $$('[data-reveal],[data-float]').forEach(el => io.observe(el));

  /* ---------- CountUp ---------- */
  const countIO = new IntersectionObserver(entries => entries.forEach(e => {
    if (!e.isIntersecting) return;
    countIO.unobserve(e.target);
    const el = e.target, to = +el.dataset.count;
    if (reduce || to === 0) { el.textContent = to; return; }
    const t0 = performance.now(), dur = 1400;
    const step = t => {
      const k = Math.min(1, (t - t0) / dur);
      el.textContent = Math.round(to * (1 - Math.pow(1 - k, 3)));
      if (k < 1) requestAnimationFrame(step);
    };
    el.textContent = '0';
    requestAnimationFrame(step);
  }), { threshold: 0.6 });
  $$('[data-count]').forEach(el => countIO.observe(el));

  /* ---------- RotatingText (tuyến trong hero) ---------- */
  const rot = $('[data-rotate]');
  if (rot && !reduce) {
    const items = JSON.parse(rot.dataset.rotate);
    const span = $('.rotator__text', rot);
    let i = 0;
    setInterval(() => {
      if (document.hidden) return;
      span.classList.add('is-out');
      setTimeout(() => {
        i = (i + 1) % items.length;
        span.textContent = items[i];
        span.classList.remove('is-out');
        span.classList.add('is-in');
        void span.offsetWidth;
        span.classList.remove('is-in');
      }, 420);
    }, 2600);
  }

  /* ---------- spotlight theo chuột (rAF) ---------- */
  if (canHover && !reduce) {
    const hero = $('.hero'), spot = $('.hero__spot');
    let raf = 0, last;
    const flush = () => {
      raf = 0;
      const { el, x, y } = last;
      el.style.setProperty('--mx', x + 'px');
      el.style.setProperty('--my', y + 'px');
    };
    const track = (el, target) => ev => {
      const r = el.getBoundingClientRect();
      last = { el: target || el, x: ev.clientX - r.left, y: ev.clientY - r.top };
      if (!raf) raf = requestAnimationFrame(flush);
    };
    if (hero && spot) hero.addEventListener('pointermove', track(hero, spot));
    $$('[data-spotlight]').forEach(c => c.addEventListener('pointermove', track(c)));

    /* Magnet CTA */
    $$('[data-magnet]').forEach(btn => {
      btn.addEventListener('pointermove', ev => {
        const r = btn.getBoundingClientRect();
        const dx = (ev.clientX - r.left - r.width / 2) * 0.22, dy = (ev.clientY - r.top - r.height / 2) * 0.3;
        btn.style.transform = `translate(${dx}px,${dy}px)`;
      });
      btn.addEventListener('pointerleave', () => { btn.style.transform = ''; });
    });
  }

  /* ---------- ripple ---------- */
  document.addEventListener('pointerdown', ev => {
    const btn = ev.target.closest('.btn');
    if (!btn || reduce) return;
    const r = btn.getBoundingClientRect(), d = Math.max(r.width, r.height) * 2.2;
    const s = document.createElement('span');
    s.className = 'ripple';
    s.style.cssText = `width:${d}px;height:${d}px;left:${ev.clientX - r.left - d / 2}px;top:${ev.clientY - r.top - d / 2}px`;
    btn.appendChild(s);
    setTimeout(() => s.remove(), 650);
  });

  /* ---------- lọc bảng giá: nhóm tuyến + loại chuyến ---------- */
  const grid = $('#ticket-grid');
  if (grid) {
    const filter = { group: 'all', kind: 'all' };
    const groupBtns = $$('[data-filter-group]');
    const kindBtns = $$('[data-filter-kind]');
    const kindBox = $('.tabs--3');
    const apply = () => {
      let n = 0;
      $$('.ticket', grid).forEach(t => {
        const rows = $$('.ticket__prices li', t);
        rows.forEach(li => { li.hidden = filter.kind !== 'all' && li.dataset.kind !== filter.kind; });
        const show = (filter.group === 'all' || t.dataset.group === filter.group) && rows.some(li => !li.hidden);
        t.hidden = !show;
        t.classList.remove('is-shown');
        if (show && !reduce) { t.style.setProperty('--n', n++); void t.offsetWidth; t.classList.add('is-shown'); }
      });
      grid.scrollLeft = 0;
    };
    const press = (btns, btn) => btns.forEach(b => b.setAttribute('aria-pressed', String(b === btn)));
    groupBtns.forEach(b => b.addEventListener('click', () => { filter.group = b.dataset.filterGroup; press(groupBtns, b); apply(); }));
    kindBtns.forEach((b, i) => b.addEventListener('click', () => {
      filter.kind = b.dataset.filterKind; press(kindBtns, b); kindBox.dataset.active = i; apply();
    }));
  }

  /* ---------- form đặt xe ---------- */
  const form = $('#booking-form');
  if (!form) return;
  const f = name => form.elements[name];
  const estimate = $('[data-estimate]', form);
  const errBox = $('[data-form-error]', form);
  const carField = $('[data-car-field]', form);
  const seatLabel = $('[data-seat-label]', form);

  const norm = s => (s || '').toLowerCase().replace(/đ/g, 'd').normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9]+/g, '-');
  const fmt = p => String(p).split('-').map(n => (+n).toLocaleString('vi-VN') + 'K').join(' – ');
  const findRoute = (a, b) => {
    const A = norm(a), B = norm(b);
    if (!A || !B) return null;
    const hit = (txt, key) => txt.includes(key) || (key === 'san-bay-noi-bai' && txt.includes('noi-bai'));
    return CFG.routes.find(r => (hit(A, r.keys[0]) && hit(B, r.keys[1])) || (hit(A, r.keys[1]) && hit(B, r.keys[0])));
  };

  // Giờ đón mặc định: 2 tiếng sau, làm tròn 15 phút (giờ dạng 24h, chọn riêng giờ/phút)
  const dateInput = f('ngay_don');
  const ymd = d => new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
  const pad = n => String(n).padStart(2, '0');
  const now = new Date();
  dateInput.min = ymd(now);
  const def = new Date(now.getTime() + 2 * 3600e3);
  def.setMinutes(Math.ceil(def.getMinutes() / 15) * 15, 0, 0);
  dateInput.value = ymd(def);
  f('gio').value = pad(def.getHours());
  f('phut').value = pad(def.getMinutes());
  const pickupTime = () => (dateInput.value ? new Date(`${dateInput.value}T${f('gio').value}:${f('phut').value}`) : null);

  const saved = store.get('xg-khach');
  if (saved) { f('sdt').value = saved.sdt || ''; f('ho_ten').value = saved.ho_ten || ''; }

  function kind() { return form.querySelector('input[name=loai]:checked').value; }
  function update() {
    const isBao = kind() === 'Bao xe';
    carField.hidden = !isBao;
    seatLabel.textContent = isBao ? 'Số khách' : 'Số người';
    const r = findRoute(f('diem_don').value, f('diem_den').value);
    if (!r) { estimate.innerHTML = ''; return; }
    if (isBao) {
      const car = f('loai_xe').value;
      const price = { 'Xe 4–5 chỗ': r.bao, 'Xe 7 chỗ': r.bao7, 'Xe 16 chỗ': r.bao16 }[car];
      estimate.innerHTML = price
        ? `Giá tham khảo bao ${car.toLowerCase()}: <b>${fmt(price)}</b>/xe`
        : `Bao ${car.toLowerCase()}: tổng đài sẽ báo giá khi xác nhận.`;
    } else if (r.ghep) {
      const n = +f('so_nguoi').value;
      const lo = +String(r.ghep).split('-')[0] * n;
      estimate.innerHTML = `Giá tham khảo: <b>${fmt(r.ghep)}</b>/ghế${n > 1 ? ` · ${n} ghế ≈ <b>${lo.toLocaleString('vi-VN')}K</b>` : ''}`;
    } else {
      estimate.innerHTML = `Ghép ghế tuyến này: tổng đài báo giá khi xác nhận · bao xe từ <b>${fmt(r.bao)}</b>`;
    }
  }
  form.addEventListener('input', update);
  form.addEventListener('change', update);
  update();

  $('[data-swap]', form).addEventListener('click', () => {
    const a = f('diem_don').value;
    f('diem_don').value = f('diem_den').value;
    f('diem_den').value = a;
    update();
  });

  // Nút "Đặt tuyến này" / "Đặt xe" ở khắp trang
  $$('[data-book]').forEach(btn => btn.addEventListener('click', ev => {
    const { from, to, kind: k } = btn.dataset;
    if (from) f('diem_don').value = from;
    if (to) f('diem_den').value = to;
    if (k) { const r = form.querySelector(`input[name=loai][value="${k}"]`); if (r) r.checked = true; }
    update();
    ev.preventDefault();
    form.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'center' });
    form.classList.remove('is-flash'); void form.offsetWidth; form.classList.add('is-flash');
    setTimeout(() => (f('diem_don').value ? f('sdt') : f('diem_don')).focus({ preventScroll: true }), 600);
  }));

  const phoneRe = /^(0|\+?84)(3|5|7|8|9)\d{8}$/;
  function validate() {
    const bad = [];
    const check = (name, ok) => { f(name).setAttribute('aria-invalid', String(!ok)); if (!ok) bad.push(f(name)); };
    check('diem_don', f('diem_don').value.trim().length > 1);
    check('diem_den', f('diem_den').value.trim().length > 1);
    const t = pickupTime();
    check('ngay_don', !!t && t.getTime() > Date.now() - 10 * 60e3);
    check('sdt', phoneRe.test(f('sdt').value.replace(/[\s.-]/g, '')));
    return bad;
  }
  form.addEventListener('input', e => { if (e.target.getAttribute('aria-invalid') === 'true') validate(); errBox.textContent = ''; });

  form.addEventListener('submit', async ev => {
    ev.preventDefault();
    const bad = validate();
    if (bad.length) {
      const only = bad.length === 1 && bad[0];
      errBox.textContent = only === f('sdt') ? 'Số điện thoại chưa đúng (VD: 0912 345 678).'
        : only === dateInput && dateInput.value ? 'Giờ đón đã qua, vui lòng chọn ngày giờ khác.'
        : 'Vui lòng điền điểm đón, điểm đến, ngày giờ đón và số điện thoại.';
      bad[0].focus();
      return;
    }
    const d = pickupTime();
    const when = `${f('gio').value}:${f('phut').value} ${d.toLocaleDateString('vi-VN', { weekday: 'short', day: '2-digit', month: '2-digit' })}`;
    const isBao = kind() === 'Bao xe';
    const data = {
      loai: kind(), diem_don: f('diem_don').value.trim(), diem_den: f('diem_den').value.trim(), gio_don: when,
      so_nguoi: f('so_nguoi').value, loai_xe: isBao ? f('loai_xe').value : '', ho_ten: f('ho_ten').value.trim(),
      sdt: f('sdt').value.trim(), ghi_chu: f('ghi_chu').value.trim(), trang: location.href,
      website: f('website').value,
    };
    store.set('xg-khach', { sdt: data.sdt, ho_ten: data.ho_ten });

    const lines = [
      `ĐẶT ${data.loai.toUpperCase()}`,
      `• Từ: ${data.diem_don}`,
      `• Đến: ${data.diem_den}`,
      `• Giờ đón: ${data.gio_don}`,
      `• Số người: ${data.so_nguoi}${data.loai_xe ? ' · ' + data.loai_xe : ''}`,
      `• Khách: ${data.ho_ten || '(chưa có tên)'} – ${data.sdt}`,
    ];
    if (data.ghi_chu) lines.push(`• Ghi chú: ${data.ghi_chu}`);
    const msg = lines.join('\n');

    let sent = false;
    if (CFG.endpoint) {
      const btn = form.querySelector('[type=submit]');
      btn.disabled = true;
      try {
        if (CFG.endpoint.startsWith('/')) {
          // Cùng domain (Vercel /api): đọc được kết quả thật
          const res = await fetch(CFG.endpoint, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
          sent = res.ok;
        } else {
          // Domain khác (Apps Script...): không đọc được phản hồi
          await fetch(CFG.endpoint, { method: 'POST', mode: 'no-cors', headers: { 'Content-Type': 'text/plain;charset=utf-8' }, body: JSON.stringify(data) });
          sent = true;
        }
      } catch { /* rơi về Zalo/SMS */ }
      btn.disabled = false;
    }
    openDialog(msg, sent);
  });

  /* ---------- dialog xác nhận ---------- */
  const dlg = $('#booking-dialog');
  function openDialog(msg, sent) {
    $('[data-dlg-summary]', dlg).textContent = msg;
    $('[data-dlg-lead]', dlg).textContent = sent
      ? 'Tổng đài sẽ gọi lại trong 5 phút. Muốn nhanh hơn, gửi thêm qua Zalo hoặc gọi ngay:'
      : 'Gửi thông tin cho tổng đài bằng 1 chạm để được xác nhận ngay:';
    const sep = /iPhone|iPad|iPod/.test(navigator.userAgent) ? '&' : '?';
    $('[data-dlg-sms]', dlg).href = `sms:${CFG.phone}${sep}body=${encodeURIComponent(msg)}`;
    const hint = $('[data-dlg-hint]', dlg);
    hint.hidden = true;
    $('[data-dlg-zalo]', dlg).onclick = () => {
      navigator.clipboard?.writeText(msg).then(() => { hint.hidden = false; }, () => {});
    };
    if (typeof dlg.showModal === 'function') dlg.showModal(); else dlg.setAttribute('open', '');
  }
  $('[data-dlg-close]', dlg)?.addEventListener('click', () => dlg.close());
  dlg?.addEventListener('click', e => { if (e.target === dlg) dlg.close(); });
})();
