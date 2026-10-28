# DESIGN.md — Xe Ghép An Tâm

> Đèn pha trên cao tốc lúc chạng vạng: tối, tin cậy, và luôn có một vệt sáng hổ phách dẫn đường tới nút "Đặt xe".

## 1. Visual Theme & Atmosphere

**Style**: Night Highway — Warm Professional pha Dark Tech (tham chiếu seed #4 + #2 trong `style-seeds.md`)
**Keywords**: tin cậy, nhanh, đêm cao tốc, đèn pha hổ phách, rõ giá, thân thiện, di động-trước-tiên
**Tone**: chuyên nghiệp, ấm, chắc chắn — NOT rẻ tiền, rối mắt, banner nhấp nháy kiểu web taxi cũ
**Feel**: như ngồi ghế phụ một chiếc xe sạch, tài xế bật xi-nhan đúng lúc — mọi thứ đều đúng giờ.

**Interaction Tier**: L2 Lưu loát (scroll reveal, nav đổi trạng thái, parallax nhẹ, spotlight)
**Dependencies**: CSS + Vanilla JS (không thư viện — tối ưu Core Web Vitals cho SEO)

Tham chiếu nội dung: xeghepnhanh.vn (8 section: header/hotline → form đặt xe → dịch vụ → bảng giá bao xe → bảng giá ghép → dịch vụ 24H → form lần 2 → số liệu đội xe → cảm nghĩ → footer cam kết). Giữ đủ chức năng, thay toàn bộ ngôn ngữ thị giác.

## 2. Color Palette & Roles

```css
:root {
  /* Backgrounds */
  --bg: #F6F7FB;              /* nền trang sáng */
  --surface: #FFFFFF;         /* thẻ, form */
  --surface-alt: #EEF1F8;     /* section xen kẽ */
  --surface-hover: #F9FAFD;
  --ink: #0B1324;             /* nền tối: hero, số liệu, CTA, footer */
  --ink-2: #131D33;           /* bề mặt trên nền tối */
  --ink-3: #1C2843;

  /* Borders */
  --border: #E2E6EF;
  --border-hover: #C9D0DE;
  --border-dark: rgba(255,255,255,.10);

  /* Text */
  --text: #0B1324;
  --text-secondary: #4A556B;
  --text-tertiary: #7C879C;
  --text-on-dark: #F4F6FB;
  --text-on-dark-2: #A9B3C7;

  /* Accent — đèn pha */
  --accent: #FFB21A;
  --accent-hover: #FFC247;
  --accent-press: #E89C00;
  --accent-ink: #1A1300;      /* chữ trên nền accent (tương phản 11:1) */
  --accent-2: #FF5A36;        /* đèn hậu — chỉ dùng trong gradient */
  --zalo: #0068FF;

  /* RGB variants */
  --bg-rgb: 246,247,251;
  --ink-rgb: 11,19,36;
  --accent-rgb: 255,178,26;
  --accent-2-rgb: 255,90,54;

  /* Semantic */
  --success: #1F9D63;
  --error: #E5484D;
  --warning: #F5A524;
}
```

**Color Rules:**
- Mọi màu qua CSS variable; không hardcode hex trong component.
- Accent hổ phách chỉ dành cho hành động chính (Gọi / Đặt xe) và giá tiền — không dùng làm màu trang trí rải rác.
- Nền tối (`--ink`) chỉ ở: Hero, dải số liệu, CTA cuối, footer. Nhịp: tối → sáng → sáng → tối → sáng → tối.
- Chữ trên nền accent luôn là `--accent-ink`, không dùng trắng.

## 3. Typography Rules

**Font Stack:**
```css
@import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700;800&display=swap');
font-family: 'Be Vietnam Pro', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
```

| Role | Font | Size | Weight | Line Height | Letter Spacing |
|------|------|------|--------|-------------|----------------|
| Hero H1 | Be Vietnam Pro | clamp(2.5rem, 5.6vw, 4.5rem) | 800 | 1.08 | -0.025em |
| Section H2 | Be Vietnam Pro | clamp(1.9rem, 3.6vw, 2.75rem) | 800 | 1.15 | -0.02em |
| H3 | Be Vietnam Pro | 1.25rem | 700 | 1.35 | -0.01em |
| Body | Be Vietnam Pro | 1rem–1.0625rem | 400 | 1.7 | 0.005em |
| Label / Eyebrow | Be Vietnam Pro | 0.8125rem | 700 | 1.4 | 0.12em, uppercase |
| Giá tiền | Be Vietnam Pro | 1.75rem | 800 | 1 | -0.02em, tabular-nums |

**Typography Rules:**
- Tiếng Việt: dùng font có đủ dấu (Be Vietnam Pro được thiết kế cho tiếng Việt). Line-height body ≥ 1.7.
- Heading weight ≥ 700; số tiền luôn `font-variant-numeric: tabular-nums`.
- **NEVER use**: Inter/Roboto làm font chính, font chữ viết tay, font không đủ dấu tiếng Việt (gây lỗi dấu chồng).

**Text Decoration (theo text-decoration-rules.md):**
- Hero H1: một cụm từ khoá có gradient hổ phách → đỏ đèn hậu chảy chậm; phần còn lại trắng phẳng.
- H2: không gradient, không đổ bóng. H3: phẳng.

## 4. Component Stylings

### Buttons
```css
.btn{display:inline-flex;align-items:center;justify-content:center;gap:.55rem;min-height:48px;padding:0 1.35rem;
  border-radius:999px;font:700 1rem/1 var(--font);border:1.5px solid transparent;cursor:pointer;
  transition:transform .25s var(--ease),background-color .2s,box-shadow .25s,border-color .2s;position:relative;overflow:hidden}
.btn-primary{background:var(--accent);color:var(--accent-ink);box-shadow:0 8px 24px -8px rgba(var(--accent-rgb),.65)}
.btn-primary:hover{background:var(--accent-hover);transform:translateY(-2px);box-shadow:0 14px 32px -10px rgba(var(--accent-rgb),.8)}
.btn-primary:active{background:var(--accent-press);transform:translateY(0) scale(.98)}
.btn:focus-visible{outline:3px solid var(--accent);outline-offset:3px}
.btn:disabled,.btn[aria-disabled=true]{opacity:.5;cursor:not-allowed;transform:none;box-shadow:none}
.btn-ghost{background:transparent;color:inherit;border-color:currentColor}
.btn-ghost:hover{background:rgba(255,255,255,.08)}
.btn-zalo{background:var(--zalo);color:#fff}   /* màu thương hiệu Zalo — ngoại lệ duy nhất */
```

### Cards (vé giá / dịch vụ)
```css
.card{background:var(--surface);border:1px solid var(--border);border-radius:var(--r-lg);
  transition:transform .35s var(--ease),box-shadow .35s var(--ease),border-color .2s}
.card:hover{transform:translateY(-4px);box-shadow:var(--shadow-lg);border-color:var(--border-hover)}
.card:focus-within{border-color:var(--accent);box-shadow:0 0 0 3px rgba(var(--accent-rgb),.3)}
/* SpotlightCard: ::before radial-gradient tại --mx/--my, opacity 0 → 1 khi hover */
```

### Navigation
```css
.site-header{position:fixed;inset:0 0 auto;z-index:50;color:var(--text-on-dark);transition:background-color .3s,box-shadow .3s,color .3s}
.site-header.is-scrolled{background:rgba(var(--bg-rgb),.86);backdrop-filter:blur(12px);color:var(--text);box-shadow:0 1px 0 var(--border)}
.nav a{padding:.5rem .8rem;border-radius:999px}
.nav a:hover{background:rgba(var(--accent-rgb),.14)}
.nav a:focus-visible{outline:2px solid var(--accent)}
```

### Links
```css
.link{color:inherit;background:linear-gradient(currentColor,currentColor) 0 100%/0 2px no-repeat;transition:background-size .3s var(--ease)}
.link:hover,.link:focus-visible{background-size:100% 2px}
```

### Tags / Badges
```css
.badge{display:inline-flex;align-items:center;gap:.4rem;padding:.35rem .75rem;border-radius:999px;
  font-size:.8125rem;font-weight:700;letter-spacing:.06em;background:rgba(var(--accent-rgb),.14);color:var(--accent-press)}
```

### Form fields
```css
.field input,.field select,.field textarea{width:100%;min-height:48px;padding:.75rem 1rem;border:1.5px solid var(--border);
  border-radius:var(--r-md);background:var(--surface);font:500 1rem var(--font);color:var(--text);transition:border-color .2s,box-shadow .2s}
.field input:hover{border-color:var(--border-hover)}
.field input:focus{outline:none;border-color:var(--accent);box-shadow:0 0 0 4px rgba(var(--accent-rgb),.22)}
.field input[aria-invalid=true]{border-color:var(--error)}
.field input:disabled{background:var(--surface-alt);cursor:not-allowed}
```

### Segmented (Xe ghép / Bao xe)
Radio ẩn + label dạng pill; trạng thái checked = nền `--ink`, chữ trắng; focus-visible = outline accent.

## 5. Layout Principles

**Container:** max 1200px, padding ngang `clamp(16px, 4vw, 32px)`; biến thể hẹp 760px cho FAQ.

**Spacing Scale:** 4 · 8 · 12 · 16 · 24 · 32 · 48 · 64 · 96 · 128
- Section padding: `clamp(64px, 10vw, 120px)` dọc
- Component gap: 24px (desktop) / 16px (mobile)
- Card internal padding: 24–32px

**Grid:**
```css
.hero-grid{display:grid;grid-template-columns:1.1fr .9fr;gap:clamp(32px,5vw,72px);align-items:center}
.ticket-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:20px}
.bento{display:grid;grid-template-columns:repeat(6,1fr);grid-auto-rows:minmax(200px,auto);gap:20px}
/* bento: ô lớn span 4×2, ô vừa span 2×2, ô ngang span 3 — không bao giờ lưới đều */
```

## 6. Depth & Elevation

| Level | Treatment | Use |
|-------|-----------|-----|
| Flat | none | section, bảng |
| Subtle | `0 1px 2px rgba(var(--ink-rgb),.06), 0 1px 1px rgba(var(--ink-rgb),.04)` | thẻ nghỉ |
| Elevated | `0 18px 40px -18px rgba(var(--ink-rgb),.28)` | thẻ hover, form đặt xe |
| Floating | `0 30px 60px -20px rgba(var(--ink-rgb),.45)` | dialog, nút nổi |
| Glow | `0 8px 24px -8px rgba(var(--accent-rgb),.65)` | chỉ nút primary |

## 7. Animation & Interaction

**Motion Philosophy**: chuyển động như xe chạy êm — chỉ transform + opacity, easing `cubic-bezier(.22,1,.36,1)`, không giật.
**Tier**: L2

### Dependencies
Không có. IntersectionObserver + requestAnimationFrame thuần.

### Signature moments (6 loại bắt buộc của L2)
| Loại | Hiệu ứng | Vị trí |
|------|----------|--------|
| Text — Hero H1 | SplitText: từng từ trượt lên từ mặt nạ, stagger 60ms; cụm khoá GradientText chảy | Hero |
| Text — Section H2 | ScrollFloat: từ nổi lên khi vào viewport | mọi H2 |
| Text — Body/Label | RotatingText: tuyến đường xoay vòng trong câu phụ đề; CountUp số liệu | Hero, dải số liệu |
| Element | Magnet trên CTA gọi điện + ripple khi bấm | Hero, CTA |
| Component | SpotlightCard trên bento dịch vụ + vé giá có tab chuyển Ghép/Bao | Dịch vụ, Bảng giá |
| Background | Vệt đèn cao tốc chạy chéo (CSS) + spotlight theo chuột trên ảnh hero | Hero |

**3 điểm "wow" của trang chủ:** (1) Hero ảnh cao tốc đêm + vệt đèn + chữ trồi lên; (2) cú cuộn đầu: dải marquee khổng lồ tên tuyến + giá chạy 2 chiều trên nền hổ phách; (3) bảng giá dạng **vé xe** đục lỗ + bento dịch vụ không đều có spotlight.
**Chi tiết tinh nghịch:** thanh tiến độ cuộn là một con đường, có chiếc xe nhỏ chạy theo; cuộn tới cuối trang hiện "Tới nơi rồi! Gọi xe thôi".

### Entrance Animation
```css
@keyframes rise{from{opacity:0;transform:translateY(24px)}to{opacity:1;transform:none}}
.h1-word{display:inline-block;overflow:hidden;vertical-align:top}
.h1-word>span{display:inline-block;transform:translateY(105%);animation:wordUp .9s var(--ease) forwards;animation-delay:calc(var(--i)*60ms + 150ms)}
@keyframes wordUp{to{transform:none}}
```

### Scroll Behavior
```js
const io = new IntersectionObserver((es)=>es.forEach(e=>{ if(e.isIntersecting){ e.target.classList.add('is-in'); io.unobserve(e.target);} }),{rootMargin:'0px 0px -10% 0px'});
document.querySelectorAll('[data-reveal]').forEach(el=>io.observe(el));
// header .is-scrolled khi scrollY > 24; ảnh hero parallax translateY(scrollY*0.25) trong rAF
```

### Hover & Focus States
Mọi `a, button, input, select, summary` có `:hover` và `:focus-visible` (outline 3px accent, offset 3px).

### Reduced Motion
```css
@media (prefers-reduced-motion: reduce){
  *,*::before,*::after{animation-duration:.01ms!important;animation-iteration-count:1!important;transition-duration:.01ms!important;scroll-behavior:auto!important}
  .h1-word>span,[data-reveal]{transform:none!important;opacity:1!important}
  .marquee-track,.streak{animation:none!important}
}
```

## 8. Do's and Don'ts

### Do
- Luôn có đường gọi điện trong 1 chạm: header, hero, mobile sticky bar, CTA cuối.
- Giá hiển thị rõ ràng, có chữ "tham khảo" và cách tính (ghép = /người, bao = /xe).
- Form đặt xe tối đa 1 màn hình mobile; trường bắt buộc tối thiểu (SĐT, điểm đón, điểm đến, giờ).
- Mỗi trang 1 H1 chứa từ khoá tuyến; ảnh có `alt` mô tả, `width/height` cố định chống CLS.
- Mỗi tuyến có trang riêng với nội dung riêng (khoảng cách, thời gian, điểm đón) — không copy y nguyên.
- Dùng icon SVG inline, nét 2px, bo tròn.

### Don't
- ❌ Hardcode hex trong component.
- ❌ Dùng emoji làm icon.
- ❌ `filter: blur()` trên phần tử chuyển động; backdrop-filter > 14px.
- ❌ Thư viện animation nặng (GSAP/Lenis) — trang dịch vụ địa phương cần LCP < 2.5s trên 4G.
- ❌ Popup chặn màn hình khi vừa vào trang; chữ chạy kiểu `<marquee>` nhấp nháy.
- ❌ Đánh giá/sao giả trong structured data (Google phạt) — chỉ thêm khi có đánh giá thật.
- ❌ Màu đỏ/xanh lá chói làm nền section.
- ❌ Ảnh placeholder khối màu đơn.
- ❌ Khối text chỉ toàn từ khoá (keyword stuffing).

## 9. Responsive Behavior

| Name | Width | Key Changes |
|------|-------|-------------|
| Desktop | > 1024px | Hero 2 cột (chữ + form), bento 6 cột, nav ngang |
| Tablet | 641–1024px | Hero 1 cột, form dưới chữ; bento 2 cột; nav thu vào menu |
| Mobile | ≤ 640px | Mọi lưới 1 cột; marquee nhỏ lại; thanh hành động dính đáy (Gọi · Zalo · Đặt xe) |

**Touch Targets:** tối thiểu 48×48px.
**Collapsing Strategy:** nav → nút menu mở panel toàn chiều ngang; bảng giá → thẻ vé xếp dọc; nút nổi desktop ẩn trên mobile (thay bằng sticky bar).

```css
@media (max-width:1024px){.hero-grid{grid-template-columns:1fr}.bento{grid-template-columns:repeat(2,1fr)}.bento>*{grid-column:span 2!important;grid-row:auto!important}}
@media (max-width:640px){.bento{grid-template-columns:1fr}.mobile-bar{display:grid}.float-actions{display:none}body{padding-bottom:72px}}
```
