# Website Xe Ghép An Tâm

Website tĩnh (HTML/CSS/JS thuần, không thư viện) — tải nhanh, chuẩn SEO, chạy trên mọi hosting tĩnh.

## Sửa nội dung
Mọi thông tin (tên, tên miền, SĐT, giá, tuyến, FAQ, cam kết) nằm ở phần **CẤU HÌNH** trong `_build/build.py`.
Sửa xong chạy:

```
python _build/build.py
```

Script sinh lại `index.html`, `tuyen/*.html`, `sitemap.xml`, `robots.txt`, `site.webmanifest`, `assets/js/config.js`.
**Không sửa tay các file này** (sẽ bị ghi đè). CSS/JS giao diện: `assets/css/styles.css`, `assets/js/app.js`. Quy chuẩn thiết kế: `DESIGN.md`.

## Xem thử trên máy
```
python -m http.server 8000
```
Mở http://localhost:8000

## Trước khi đưa lên mạng
1. Đổi `SITE["domain"]` thành tên miền thật → build lại (canonical, sitemap, schema đều dùng nó).
2. Upload toàn bộ thư mục (trừ `_build/` nếu muốn) lên hosting: Cloudflare Pages, Netlify, Vercel, GitHub Pages hoặc hosting thường.
3. Khai báo website với Google Search Console, gửi `sitemap.xml`.
4. Tạo Google Business Profile (Google Maps) cùng tên + SĐT — yếu tố quan trọng nhất cho SEO địa phương.

## Nhận đơn đặt xe
Mặc định: khách bấm "Đặt xe ngay" → hiện tóm tắt chuyến + nút gửi qua **Zalo** (tự sao chép nội dung), **SMS** hoặc **Gọi**.
Muốn đơn tự đổ về Google Sheets: tạo Google Apps Script Web App nhận POST JSON, dán URL vào `SITE["booking_endpoint"]` rồi build lại.
