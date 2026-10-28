"""Sinh website tĩnh Xe Ghép An Tâm.

Sửa phần CẤU HÌNH bên dưới (tên, tên miền, SĐT, giá, tuyến, FAQ) rồi chạy:
    python _build/build.py
Script ghi đè index.html, tuyen/*.html, sitemap.xml, robots.txt, site.webmanifest, assets/js/config.js.
"""
import html
import json
import re
import unicodedata
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ============================== CẤU HÌNH ==============================
SITE = {
    "name": "Xe Ghép An Tâm",
    "domain": "https://xeghepantam.vn",  # ĐỔI thành tên miền thật (không có / ở cuối)
    "phone": "0369786086",
    "phone_display": "0369 786 086",
    "zalo": "0369786086",
    "email": "",  # để trống nếu chưa có
    "city": "Hà Nội",
    "region_code": "VN-HN",
    "geo": (21.0278, 105.8342),
    # Nơi nhận đơn: "/api/booking" = hàm Vercel gửi Telegram (api/booking.js). Để trống = khách tự gửi qua Zalo/SMS.
    "booking_endpoint": "/api/booking",
}

# Giá đơn vị nghìn đồng, có thể ghi khoảng "400-1000". None = "Liên hệ".
#   ghep  = giá ghép /ghế      bao   = bao xe riêng 4–5 chỗ
#   bao7  = bao xe 7 chỗ       bao16 = bao xe 16 chỗ (không có thì bỏ trống)
# group: nhóm lọc trong bảng giá (xem GROUPS). road: nhãn cung đường trên thẻ giá.
ROUTES = [
    dict(slug="xe-ghep-ha-noi-ha-long", group="hn-qn", a="Hà Nội", b="Hạ Long", road="Cao tốc 5B",
         km=160, time="2 giờ – 2 giờ 30", via="cao tốc Hà Nội – Hải Phòng (5B) và cao tốc Hải Phòng – Hạ Long",
         ghep="450", bao="1100",
         areas_b="Bãi Cháy, Hòn Gai, Tuần Châu, Hà Tu, Hùng Thắng, khu Sun World, các khách sạn ven vịnh",
         tip="Đi chơi Hạ Long cuối tuần nên đặt từ thứ Năm — xe sáng thứ Bảy thường kín chỗ sớm."),
    dict(slug="xe-ghep-ha-noi-cam-pha", group="hn-qn", a="Hà Nội", b="Cẩm Phả", road="Cao tốc",
         km=190, time="2 giờ 30 – 3 giờ", via="cao tốc 5B, cao tốc Hạ Long – Vân Đồn",
         ghep="500", bao="1300",
         areas_b="Cẩm Thạch, Cẩm Trung, Cẩm Đông, Cửa Ông, Mông Dương, các mỏ than và cảng Cẩm Phả",
         tip="Anh chị em làm mỏ đi ca nên báo giờ vào ca khi đặt — tài xế canh giờ đến sớm 15 phút."),
    dict(slug="xe-ghep-ha-noi-van-don", group="hn-qn", a="Hà Nội", b="Vân Đồn", road="Cao tốc",
         km=200, time="2 giờ 30 – 3 giờ", via="cao tốc 5B, cao tốc Hạ Long – Vân Đồn",
         ghep="600", bao="1700",
         areas_b="Sân bay Vân Đồn, cảng Cái Rồng (tàu đi Quan Lạn, Minh Châu, Cô Tô), Đông Xá, Hạ Long Xanh",
         tip="Ra đảo Quan Lạn, Cô Tô thì báo giờ tàu chạy — xe căn giờ thả bạn ngay cảng Cái Rồng."),
    dict(slug="xe-ghep-ha-noi-mong-cai", group="hn-qn", a="Hà Nội", b="Móng Cái", road="Cao tốc Vân Đồn – Móng Cái",
         km=300, time="3 giờ 30 – 4 giờ", via="cao tốc 5B, Hạ Long – Vân Đồn và Vân Đồn – Móng Cái",
         ghep="700", bao="2300",
         areas_b="Trung tâm Móng Cái, cửa khẩu Bắc Luân, bãi biển Trà Cổ, Hải Hòa, Ka Long, chợ Móng Cái",
         tip="Đi buôn hàng cửa khẩu nên chọn chuyến sớm, báo trước nếu mang hàng cồng kềnh để xếp chỗ cốp."),
    dict(slug="xe-ghep-ha-noi-uong-bi", group="hn-qn", a="Hà Nội", b="Uông Bí", road="QL18",
         km=120, time="2 giờ", via="cao tốc Hà Nội – Bắc Ninh và QL18",
         ghep="400", bao="900",
         areas_b="Trung tâm Uông Bí, Yên Tử, Phương Đông, Quang Trung, Vàng Danh, Nam Khê",
         tip="Hành hương Yên Tử mùa lễ hội nên bao xe khứ hồi, tài xế chờ đưa về trong ngày."),
    dict(slug="xe-ghep-ha-noi-dong-trieu", group="hn-qn", a="Hà Nội", b="Đông Triều", road="QL18",
         km=100, time="1 giờ 45 – 2 giờ", via="cao tốc Hà Nội – Bắc Ninh và QL18",
         ghep="300", bao="800",
         areas_b="Trung tâm Đông Triều, Mạo Khê, Tràng An, Hồng Phong, Đức Chính, KCN Kim Sen",
         tip="Tuyến ngắn, giá ghép mềm — hợp với công nhân và sinh viên đi về cuối tuần."),
    dict(slug="xe-ghep-ha-noi-hai-phong", group="hn-hp", a="Hà Nội", b="Hải Phòng", road="Cao tốc HN – HP",
         km=120, time="1 giờ 30 – 1 giờ 45", via="cao tốc Hà Nội – Hải Phòng (5B)",
         ghep="400", bao="900", bao7="1000", bao16="1600",
         areas_b="Lê Chân, Ngô Quyền, Hồng Bàng, Hải An, Kiến An, Dương Kinh, Đồ Sơn, Thủy Nguyên, An Dương, sân bay Cát Bi",
         tip="Bay sớm ở Cát Bi hoặc Nội Bài? Báo số hiệu chuyến bay để tài xế tính giờ đón dư dả."),
    dict(slug="xe-ghep-hai-phong-ha-long", group="hp-qn", a="Hải Phòng", b="Hạ Long", road="Cao tốc Bạch Đằng",
         km=70, time="1 giờ – 1 giờ 15", via="cầu Bạch Đằng và cao tốc Hải Phòng – Hạ Long",
         ghep="250", bao="400-1000",
         areas_b="Bãi Cháy, Hòn Gai, Tuần Châu, Hà Tu, Hùng Thắng, khu Sun World",
         tip="Giá bao xe dao động theo loại xe và điểm đón — gọi tổng đài để được báo giá chính xác nhất."),
    dict(slug="xe-ghep-hai-phong-cam-pha", group="hp-qn", a="Hải Phòng", b="Cẩm Phả", road="Cao tốc",
         km=100, time="1 giờ 30", via="cầu Bạch Đằng, cao tốc Hải Phòng – Hạ Long – Vân Đồn",
         ghep=None, bao="700",
         areas_b="Cẩm Thạch, Cẩm Trung, Cẩm Đông, Cửa Ông, Mông Dương",
         tip="Xe ghép tuyến này theo ngày — gọi trước để biết hôm nay có chuyến ghép giờ nào."),
    dict(slug="xe-ghep-hai-phong-mong-cai", group="hp-qn", a="Hải Phòng", b="Móng Cái", road="Cao tốc trọn tuyến",
         km=230, time="3 giờ", via="cao tốc Hải Phòng – Hạ Long – Vân Đồn – Móng Cái",
         ghep=None, bao="1400",
         areas_b="Trung tâm Móng Cái, cửa khẩu Bắc Luân, Trà Cổ, Hải Hòa, Ka Long",
         tip="Chạy cao tốc trọn tuyến nên chỉ khoảng 3 tiếng — nhanh hơn hẳn xe khách đi đường cũ."),
]

GROUPS = [("hn-qn", "Hà Nội ⇄ Quảng Ninh"), ("hn-hp", "Hà Nội ⇄ Hải Phòng"), ("hp-qn", "Hải Phòng ⇄ Quảng Ninh")]

AREAS = {
    "Hà Nội": "Hoàn Kiếm, Ba Đình, Đống Đa, Cầu Giấy, Thanh Xuân, Hai Bà Trưng, Hoàng Mai, Long Biên, "
              "Tây Hồ, Mỹ Đình, Hà Đông, Gia Lâm, sân bay Nội Bài, các bệnh viện Bạch Mai, Việt Đức, 108",
    "Hải Phòng": "Lê Chân, Ngô Quyền, Hồng Bàng, Hải An, Kiến An, Dương Kinh, Đồ Sơn, Thủy Nguyên, An Dương, sân bay Cát Bi",
}

# Số liệu hiển thị ở dải "con số" — chỉ ghi điều đúng với dịch vụ của bạn.
STATS = [
    (24, "/7", "Tổng đài & xe chạy cả ngày lẫn đêm"),
    (5, " phút", "Xác nhận chuyến sau khi đặt"),
    (len(ROUTES), "+", "Tuyến Hà Nội – Hải Phòng – Quảng Ninh"),
    (0, "đ", "Phí đặt chỗ, huỷ trước 2 giờ"),
]

FAQ = [
    ("Xe ghép, xe tiện chuyến là gì? Vì sao rẻ hơn taxi?",
     "Xe ghép là bạn đi chung xe với khách khác cùng hướng, trả tiền theo ghế. Xe tiện chuyến (bao xe) là thuê "
     "nguyên xe nhưng tận dụng xe chạy rỗng chiều về, nên rẻ hơn taxi 30–50% mà vẫn là xe riêng sạch sẽ."),
    ("Cần đặt xe trước bao lâu?",
     "Đi gấp chỉ cần gọi trước 15–30 phút là có thể xếp xe. Để chủ động giờ và có giá tốt, nên đặt trước 1–2 tiếng "
     "hoặc từ hôm trước; dịp lễ, Tết, cuối tuần nên đặt sớm hơn."),
    ("Giá đã gồm phí cầu đường, cao tốc chưa?",
     "Giá báo là giá trọn gói, đã gồm xăng xe, lái xe và vé cao tốc. Điểm đón quá xa trung tâm có thể có phụ phí nhỏ, "
     "được báo rõ trước khi đi."),
    ("Có đón tận nhà, bệnh viện, sân bay không?",
     "Có. Xe đón trả tận cửa nhà, chung cư, khách sạn, bệnh viện (Bạch Mai, Việt Đức, 108...) và các sân bay "
     "Nội Bài, Cát Bi, Vân Đồn."),
    ("Xe có dừng bắt khách dọc đường không?",
     "Không. Xe chỉ đón đúng những khách đã đặt trước theo danh sách, không dừng đỗ bắt khách gây trễ giờ."),
    ("Mang hành lý, thú cưng có được không?",
     "Mỗi khách đi ghép được mang 1 vali và 1 túi xách. Đồ cồng kềnh hoặc thú cưng vui lòng báo trước "
     "để xếp xe 7 chỗ hoặc bao xe."),
    ("Thanh toán như thế nào?",
     "Thanh toán tiền mặt hoặc chuyển khoản cho tài xế khi xuống xe. Không thu tiền cọc khi đặt chỗ."),
    ("Huỷ chuyến có mất phí không?",
     "Huỷ trước giờ đón 2 tiếng hoàn toàn miễn phí. Chỉ cần gọi hoặc nhắn Zalo cho tổng đài."),
]

COMMITMENTS = [
    ("sparkle", "Xe đời mới, sạch thơm", "Xe 4–7 chỗ đến 16–45 chỗ, bảo dưỡng định kỳ, vệ sinh sau mỗi chuyến."),
    ("shield", "Lái xe an toàn, quen tuyến", "Tài xế nhiều năm kinh nghiệm, không lạng lách, không phóng nhanh."),
    ("wineoff", "Không rượu bia", "Tuyệt đối không lái xe khi đã uống rượu bia."),
    ("route", "Không bắt khách dọc đường", "Chỉ đón đúng khách đã đặt, không dừng đỗ chèo kéo gây trễ giờ."),
    ("tag", "Giá trọn gói, không phát sinh", "Đã gồm xăng, lái xe, vé cao tốc — chốt giá ngay khi xác nhận."),
    ("heart", "Hỗ trợ suốt hành trình", "Tổng đài trực 24/7, giúp hành lý, người già, trẻ nhỏ lên xuống xe."),
]

VEHICLES = ["Xe 4–5 chỗ", "Xe 7 chỗ", "Xe 16 chỗ", "Xe 29 chỗ", "Xe 45 chỗ"]


def from_price(r):
    """'1.400K/xe' — giá thấp nhất của tuyến kèm đơn vị, để hiển thị."""
    p, unit = min_price(r)
    return f"{p:,}K{unit}".replace(",", ".")


def min_price(r):
    """Giá thấp nhất của tuyến (nghìn đồng) và đơn vị."""
    return (int(str(r["ghep"]).split("-")[0]), "/ghế") if r["ghep"] else (int(str(r["bao"]).split("-")[0]), "/xe")


MIN_GHEP = min(int(r["ghep"].split("-")[0]) for r in ROUTES if r["ghep"])
MIN_BAO = min(int(r["bao"].split("-")[0]) for r in ROUTES)

SERVICES = [
    dict(key="ghep", title="Xe ghép giá rẻ", img="xe-7-cho",
         text="Đi chung chuyến với khách cùng hướng, trả theo ghế. Rẻ hơn taxi, không chen chúc như xe khách, vẫn đón tận nhà.",
         price=f"từ {MIN_GHEP}K/ghế", type="Xe ghép"),
    dict(key="bao", title="Bao xe tiện chuyến", img="duong-dai",
         text="Nguyên xe cho gia đình, nhóm bạn. Tận dụng xe chạy rỗng chiều về nên rẻ hơn taxi 30–50%.",
         price=f"từ {MIN_BAO}K/xe", type="Bao xe"),
    dict(key="sanbay", title="Đưa đón sân bay Nội Bài, Cát Bi, Vân Đồn", img="san-bay-noi-bai",
         text="Theo dõi giờ hạ cánh, chờ khi máy bay trễ. Đón cả chuyến đêm, hỗ trợ hành lý.",
         price="báo giá theo điểm đón", type="Bao xe"),
    dict(key="giadinh", title="Thuê xe 16–45 chỗ, hợp đồng", img="tai-xe",
         text="Xe đoàn cho du lịch, đám cưới, công tác, tour Hạ Long – Yên Tử. Xuất hoá đơn khi cần.",
         price="báo giá theo lịch trình", type="Bao xe"),
]
# =====================================================================

ICONS = {
    "phone": '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z"/>',
    "chat": '<path d="M7.9 20A9 9 0 1 0 4 16.1L2 22z"/>',
    "pin": '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "car": '<path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.4 2.9A3.7 3.7 0 0 0 2 12v4c0 .6.4 1 1 1h2"/><circle cx="7" cy="17" r="2"/><path d="M9 17h6"/><circle cx="17" cy="17" r="2"/>',
    "plane": '<path d="M17.8 19.2 16 11l3.5-3.5C21 6 21.5 4 21 3c-1-.5-3 0-4.5 1.5L13 8 4.8 6.2c-.5-.1-.9.1-1.1.5l-.3.5c-.2.5-.1 1 .3 1.3L9 12l-2 3H4l-1 1 3 2 2 3 1-1v-3l3-2 3.5 5.3c.3.4.8.5 1.3.3l.5-.2c.4-.3.6-.7.5-1.2z"/>',
    "shield": '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/>',
    "sparkle": '<path d="M12 3l1.9 5.8L20 10.7l-6.1 1.9L12 18.4l-1.9-5.8L4 10.7l6.1-1.9z"/><path d="M19 17v4M17 19h4"/>',
    "wineoff": '<path d="M8 22h8"/><path d="M7 10h3m7 0h-1.34"/><path d="M12 15v7"/><path d="M7.3 7.3A12.3 12.3 0 0 0 7 10a5 5 0 0 0 7.39 4.39M8.64 2.98C8.75 2.67 8.87 2.34 9 2h6c1.5 4 2 6 2 8 0 .41-.05.81-.15 1.2"/><path d="m2 2 20 20"/>',
    "heart": '<path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/>',
    "tag": '<path d="M12.59 2.59A2 2 0 0 0 11.17 2H4a2 2 0 0 0-2 2v7.17a2 2 0 0 0 .59 1.42l8.7 8.7a2.43 2.43 0 0 0 3.42 0l6.58-6.58a2.43 2.43 0 0 0 0-3.42z"/><circle cx="7.5" cy="7.5" r="1.2"/>',
    "arrow": '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
    "swap": '<path d="m16 3 4 4-4 4"/><path d="M20 7H4"/><path d="m8 21-4-4 4-4"/><path d="M4 17h16"/>',
    "calendar": '<path d="M8 2v4M16 2v4"/><rect width="18" height="18" x="3" y="4" rx="2"/><path d="M3 10h18"/>',
    "route": '<circle cx="6" cy="19" r="3"/><path d="M9 19h8.5a3.5 3.5 0 0 0 0-7h-11a3.5 3.5 0 0 1 0-7H15"/><circle cx="18" cy="5" r="3"/>',
    "repeat": '<path d="m17 2 4 4-4 4"/><path d="M3 11v-1a4 4 0 0 1 4-4h14"/><path d="m7 22-4-4 4-4"/><path d="M21 13v1a4 4 0 0 1-4 4H3"/>',
    "menu": '<path d="M4 6h16M4 12h16M4 18h16"/>',
    "x": '<path d="M18 6 6 18M6 6l12 12"/>',
    "send": '<path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/>',
    "sms": '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
    "home": '<path d="M3 10.5 12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "chevron": '<path d="m6 9 6 6 6-6"/>',
    "mail": '<rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-10 5L2 7"/>',
}


def icon(name, cls="ico"):
    return (f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>')


LOGO = ('<svg class="logo-mark" viewBox="0 0 40 40" aria-hidden="true"><rect width="40" height="40" rx="11" class="logo-bg"/>'
        '<path d="M11 29 17 11M29 29 23 11" class="logo-road"/><path d="M20 14v3M20 21v3M20 28v2" class="logo-lane"/></svg>')

e = html.escape


def k(price):
    """'350-400' -> '350K – 400K'"""
    return " – ".join(f"{int(p):,}K".replace(",", ".") for p in str(price).split("-"))


def low(price):
    return int(str(price).split("-")[0]) * 1000


def high(price):
    return int(str(price).split("-")[-1]) * 1000


def slugify(s):
    s = unicodedata.normalize("NFD", s.replace("đ", "d").replace("Đ", "D"))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def tel():
    return "+84" + SITE["phone"][1:]


def ld(obj):
    return f'<script type="application/ld+json">{json.dumps(obj, ensure_ascii=False, separators=(",", ":"))}</script>'


def split_words(text, start=0, cls=""):
    out = []
    for i, w in enumerate(text.split()):
        out.append(f'<span class="h1-word{cls}"><span style="--i:{start + i}">{e(w)}</span></span>')
    return " ".join(out), start + len(text.split())


# ------------------------------------------------------------------ layout

def head(title, desc, path, base, image="assets/img/og-cover.jpg", schemas=(), preload_hero=True):
    url = SITE["domain"] + path
    lat, lng = SITE["geo"]
    preload = (f'<link rel="preload" as="image" href="{base}assets/img/hero-cao-toc-dem-1920.webp" '
               f'imagesrcset="{base}assets/img/hero-cao-toc-dem-960.webp 960w, {base}assets/img/hero-cao-toc-dem-1920.webp 1920w" '
               'imagesizes="100vw" fetchpriority="high">') if preload_hero else ""
    return f"""<!doctype html>
<html lang="vi" class="no-js">
<head>
<meta charset="utf-8">
<script>document.documentElement.className="js"</script>
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
<meta name="theme-color" content="#0B1324">
<meta name="format-detection" content="telephone=no">
<meta name="geo.region" content="{SITE['region_code']}">
<meta name="geo.placename" content="{e(SITE['city'])}">
<meta name="geo.position" content="{lat};{lng}">
<meta name="ICBM" content="{lat}, {lng}">
<meta property="og:type" content="website">
<meta property="og:locale" content="vi_VN">
<meta property="og:site_name" content="{e(SITE['name'])}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE['domain']}/{image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image" content="{SITE['domain']}/{image}">
<link rel="icon" href="{base}favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{base}assets/img/apple-touch-icon.png">
<link rel="manifest" href="{base}site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700;800&amp;display=swap">
{preload}
<link rel="stylesheet" href="{base}assets/css/styles.css">
{"".join(ld(s) for s in schemas)}
</head>"""


def header(base, home):
    a = "" if home else f"{base}index.html"
    links = [("#bang-gia", "Bảng giá"), ("#dich-vu", "Dịch vụ"), ("#tuyen-duong", "Tuyến đường"),
             ("#quy-trinh", "Cách đặt"), ("#hoi-dap", "Hỏi đáp"), ("#lien-he", "Liên hệ")]
    nav = "".join(f'<li><a href="{a}{h}">{t}</a></li>' for h, t in links)
    return f"""<a class="skip-link" href="#noi-dung">Bỏ qua tới nội dung</a>
<div class="road-progress" aria-hidden="true"><span class="road-progress__bar"></span><span class="road-progress__car">{icon("car")}</span></div>
<header class="site-header" data-header>
  <div class="container header-inner">
    <a class="brand" href="{base}index.html" aria-label="{e(SITE['name'])} – Trang chủ">{LOGO}<span>{e(SITE['name'])}</span></a>
    <nav class="nav" id="site-nav" aria-label="Điều hướng chính"><ul>{nav}</ul></nav>
    <a class="btn btn-primary btn-sm header-call" href="tel:{tel()}" data-magnet>{icon("phone")}<span>{SITE['phone_display']}</span></a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav" aria-label="Mở menu">{icon("menu", "ico ico-open")}{icon("x", "ico ico-close")}</button>
  </div>
</header>"""


def booking_form(a="", b="", kind="Xe ghép"):
    places = sorted({r["a"] for r in ROUTES} | {r["b"] for r in ROUTES})
    dl = "".join(f'<option value="{e(p)}">' for p in places)
    seat_opts = "".join(f'<option value="{n}">{n} người</option>' for n in range(1, 8))
    hour_opts = "".join(f'<option value="{h:02d}">{h:02d}h</option>' for h in range(24))
    min_opts = "".join(f'<option value="{m:02d}">{m:02d}</option>' for m in range(0, 60, 5))
    seg = "".join(
        f'<label class="seg__opt"><input type="radio" name="loai" value="{v}"{" checked" if v == kind else ""}><span>{v}</span></label>'
        for v in ("Xe ghép", "Bao xe"))
    return f"""<form class="booking card" id="booking-form" novalidate aria-labelledby="booking-title">
  <div class="booking__head">
    <h2 class="booking__title" id="booking-title">Đặt xe trong 1 phút</h2>
    <p class="booking__sub">{icon("clock")} Tổng đài gọi xác nhận trong 5 phút</p>
  </div>
  <fieldset class="seg" aria-label="Hình thức đi">{seg}</fieldset>
  <div class="route-fields">
    <div class="field"><label for="f-from">Điểm đón</label>
      <div class="field__icon">{icon("pin")}<input id="f-from" name="diem_don" list="dl-places" placeholder="VD: Cầu Giấy, Hà Nội" value="{e(a)}" required autocomplete="address-level2"></div></div>
    <button class="swap" type="button" data-swap aria-label="Đổi chiều điểm đón và điểm đến">{icon("swap")}</button>
    <div class="field"><label for="f-to">Điểm đến</label>
      <div class="field__icon">{icon("route")}<input id="f-to" name="diem_den" list="dl-places" placeholder="VD: Bãi Cháy, Hạ Long" value="{e(b)}" required></div></div>
  </div>
  <datalist id="dl-places">{dl}</datalist>
  <div class="grid-2">
    <div class="field"><label for="f-date">Ngày đón</label>
      <input id="f-date" name="ngay_don" type="date" required></div>
    <div class="field"><label for="f-hour">Giờ đón</label>
      <div class="time-pick">
        <select id="f-hour" name="gio" aria-label="Giờ">{hour_opts}</select><span aria-hidden="true">:</span>
        <select id="f-min" name="phut" aria-label="Phút">{min_opts}</select></div></div>
  </div>
  <div class="grid-2">
    <div class="field"><label for="f-seats" data-seat-label>Số người</label>
      <select id="f-seats" name="so_nguoi">{seat_opts}</select></div>
    <div class="field field--car" data-car-field hidden><label for="f-car">Loại xe</label>
      <select id="f-car" name="loai_xe">{"".join(f"<option>{v}</option>" for v in VEHICLES)}</select></div>
  </div>
  <div class="grid-2">
    <div class="field"><label for="f-phone">Số điện thoại <abbr title="bắt buộc">*</abbr></label>
      <input id="f-phone" name="sdt" type="tel" inputmode="tel" placeholder="09xx xxx xxx" required autocomplete="tel"></div>
    <div class="field"><label for="f-name">Họ tên</label>
      <input id="f-name" name="ho_ten" placeholder="Anh/chị..." autocomplete="name"></div>
  </div>
  <div class="field"><label for="f-note">Ghi chú</label>
    <textarea id="f-note" name="ghi_chu" rows="2" placeholder="Số hiệu chuyến bay, hành lý cồng kềnh, đón ở ngõ..."></textarea></div>
  <input class="hp" name="website" tabindex="-1" autocomplete="off" aria-hidden="true">
  <p class="estimate" data-estimate aria-live="polite"></p>
  <p class="form-error" data-form-error role="alert"></p>
  <button class="btn btn-primary btn-block" type="submit">{icon("send")}<span>Đặt xe ngay</span></button>
  <p class="booking__foot">{icon("shield")} Không thu cọc · Huỷ miễn phí trước 2 giờ</p>
</form>"""


def footer(base):
    a = base + "index.html"
    route_links = "".join(f'<li><a class="link" href="{base}tuyen/{r["slug"]}.html">Xe ghép {e(r["a"])} – {e(r["b"])}</a></li>' for r in ROUTES)
    email = (f'<li>{icon("mail")}<a class="link" href="mailto:{SITE["email"]}">{SITE["email"]}</a></li>' if SITE["email"] else "")
    year = date.today().year
    return f"""<footer class="site-footer" id="lien-he">
  <div class="container footer-grid">
    <div class="footer-about">
      <a class="brand brand--light" href="{a}">{LOGO}<span>{e(SITE['name'])}</span></a>
      <p>Kết nối khách cần đi lại với những xe chạy rỗng chiều về cùng hành trình, để mỗi chuyến đi đều tiết kiệm và thoải mái.</p>
      <a class="footer-phone" href="tel:{tel()}">{icon("phone")}{SITE['phone_display']}</a>
    </div>
    <nav aria-label="Tuyến xe ghép"><h3>Tuyến phổ biến</h3><ul>{route_links}</ul></nav>
    <nav aria-label="Liên kết nhanh"><h3>Liên kết</h3><ul>
      <li><a class="link" href="{a}#bang-gia">Bảng giá</a></li><li><a class="link" href="{a}#dich-vu">Dịch vụ</a></li>
      <li><a class="link" href="{a}#quy-trinh">Cách đặt xe</a></li><li><a class="link" href="{a}#hoi-dap">Hỏi đáp</a></li></ul></nav>
    <div><h3>Liên hệ</h3><ul class="contact-list">
      <li>{icon("phone")}<a class="link" href="tel:{tel()}">{SITE['phone_display']}</a></li>
      <li>{icon("chat")}<a class="link" href="https://zalo.me/{SITE['zalo']}" target="_blank" rel="noopener">Zalo {SITE['phone_display']}</a></li>
      {email}<li>{icon("pin")}<span>{e(SITE['city'])}</span></li>
      <li>{icon("clock")}<span>Hoạt động 24/7, cả lễ Tết</span></li></ul></div>
  </div>
  <div class="container footer-bottom">
    <p>© {year} {e(SITE['name'])}. Giá trên website mang tính tham khảo, giá chính xác được báo khi xác nhận chuyến.</p>
    <p class="footer-arrive" data-arrive>Tới nơi rồi! Gọi xe thôi.</p>
  </div>
</footer>
<div class="float-actions" aria-label="Liên hệ nhanh">
  <a class="fab fab--zalo" href="https://zalo.me/{SITE['zalo']}" target="_blank" rel="noopener" aria-label="Chat Zalo">{icon("chat")}<span>Zalo</span></a>
  <a class="fab fab--call" href="tel:{tel()}" aria-label="Gọi {SITE['phone_display']}">{icon("phone")}</a>
</div>
<nav class="mobile-bar" aria-label="Thao tác nhanh">
  <a href="tel:{tel()}" class="mobile-bar__call">{icon("phone")}<span>Gọi ngay</span></a>
  <a href="https://zalo.me/{SITE['zalo']}" target="_blank" rel="noopener" class="mobile-bar__zalo">{icon("chat")}<span>Zalo</span></a>
  <a href="#dat-xe" class="mobile-bar__book" data-book>{icon("car")}<span>Đặt xe</span></a>
</nav>
<dialog class="dialog" id="booking-dialog" aria-labelledby="dlg-title">
  <div class="dialog__body">
    <div class="dialog__check">{icon("check")}</div>
    <h2 id="dlg-title">Đã ghi nhận chuyến của bạn!</h2>
    <p class="dialog__lead" data-dlg-lead>Gửi thông tin cho tổng đài bằng 1 chạm để được xác nhận ngay:</p>
    <pre class="dialog__summary" data-dlg-summary></pre>
    <div class="dialog__actions">
      <a class="btn btn-zalo" data-dlg-zalo href="https://zalo.me/{SITE['zalo']}" target="_blank" rel="noopener">{icon("chat")}<span>Gửi qua Zalo</span></a>
      <a class="btn btn-dark" data-dlg-sms href="sms:{SITE['phone']}">{icon("sms")}<span>Gửi SMS</span></a>
      <a class="btn btn-primary" href="tel:{tel()}">{icon("phone")}<span>Gọi {SITE['phone_display']}</span></a>
    </div>
    <p class="dialog__hint" data-dlg-hint>Nội dung đã được sao chép — mở Zalo và dán vào khung chat.</p>
    <button class="dialog__close" type="button" data-dlg-close aria-label="Đóng">{icon("x")}</button>
  </div>
</dialog>
<script src="{base}assets/js/config.js" defer></script>
<script src="{base}assets/js/app.js" defer></script>
</body>
</html>"""


def hero_media(base, alt):
    return f"""<div class="hero__media" aria-hidden="false">
    <img class="hero__img" data-parallax src="{base}assets/img/hero-cao-toc-dem-1920.webp"
      srcset="{base}assets/img/hero-cao-toc-dem-960.webp 960w, {base}assets/img/hero-cao-toc-dem-1920.webp 1920w"
      sizes="100vw" width="1920" height="1239" alt="{e(alt)}" fetchpriority="high" decoding="async">
    <div class="hero__shade"></div>
    <div class="streaks" aria-hidden="true">{"".join(f'<span class="streak" style="--s:{i}"></span>' for i in range(7))}</div>
    <div class="hero__spot" aria-hidden="true"></div>
  </div>"""


def img(base, name, alt, sizes="(max-width: 640px) 100vw, 50vw", cls=""):
    return (f'<img class="{cls}" src="{base}assets/img/{name}-1200.webp" srcset="{base}assets/img/{name}-640.webp 640w, '
            f'{base}assets/img/{name}-1200.webp 1200w" sizes="{sizes}" width="1200" height="800" alt="{e(alt)}" loading="lazy" decoding="async">')


def price_rows(r):
    """(nhãn, giá, đơn vị, loại) cho từng mức giá của tuyến."""
    rows = [("Ghép ghế", r["ghep"], "/ghế", "ghep"),
            ("Bao xe 4–5 chỗ" if r.get("bao7") else "Bao xe riêng", r["bao"], "", "bao")]
    if r.get("bao7"):
        rows.append(("Bao xe 7 chỗ", r["bao7"], "", "bao"))
    if r.get("bao16"):
        rows.append(("Bao xe 16 chỗ", r["bao16"], "", "bao"))
    return rows


def pr(price, unit=""):
    return f"{k(price)}<small>{unit}</small>" if price else '<span class="ticket__ask">Liên hệ</span>'


def ticket(r, base):
    rows = "".join(
        f'<li data-kind="{kind}"><span>{icon("users" if kind == "ghep" else "car")}{lbl}</span><b>{pr(p, unit)}</b></li>'
        for lbl, p, unit, kind in price_rows(r))
    kind = "Xe ghép" if r["ghep"] else "Bao xe"
    return f"""<article class="ticket card" data-spotlight data-group="{r['group']}">
  <div class="ticket__main">
    <span class="ticket__road">{icon("route")}{e(r['road'])}</span>
    <p class="ticket__route"><span>{e(r['a'])}</span>{icon("swap")}<span>{e(r['b'])}</span></p>
    <p class="ticket__meta">{r['km']} km · {icon("clock")}{e(r['time'])}</p>
  </div>
  <div class="ticket__stub">
    <ul class="ticket__prices">{rows}</ul>
    <div class="ticket__actions">
      <button class="btn btn-primary btn-sm" type="button" data-book data-from="{e(r['a'])}" data-to="{e(r['b'])}" data-kind="{kind}">Đặt tuyến này</button>
      <a class="ticket__more link" href="{base}tuyen/{r['slug']}.html" aria-label="Chi tiết tuyến {e(r['a'])} – {e(r['b'])}">Chi tiết</a>
    </div>
  </div>
</article>"""


def faq_block(items, title="Câu hỏi thường gặp", eyebrow="Hỏi đáp"):
    qa = "".join(f"""<details class="faq__item" data-reveal><summary><h3>{e(q)}</h3>{icon("chevron")}</summary><div class="faq__a"><p>{e(a)}</p></div></details>"""
                 for q, a in items)
    return f"""<section class="section section--alt" id="hoi-dap" aria-labelledby="faq-title">
  <div class="container container--narrow">
    <p class="eyebrow" data-reveal>{eyebrow}</p>
    <h2 class="h2" id="faq-title" data-float>{e(title)}</h2>
    <div class="faq">{qa}</div>
  </div>
</section>"""


def cta_block():
    return f"""<section class="cta" aria-labelledby="cta-title">
  <div class="cta__glow" aria-hidden="true"></div>
  <div class="container cta__inner">
    <p class="eyebrow eyebrow--dark" data-reveal>Tổng đài 24/7</p>
    <h2 class="h2 h2--light" id="cta-title" data-float>Cần đi ngay? Gọi là có xe.</h2>
    <a class="cta__phone" href="tel:{tel()}" data-magnet>{SITE['phone_display']}</a>
    <div class="cta__actions" data-reveal>
      <a class="btn btn-primary btn-lg" href="tel:{tel()}" data-magnet>{icon("phone")}<span>Gọi đặt xe</span></a>
      <a class="btn btn-zalo btn-lg" href="https://zalo.me/{SITE['zalo']}" target="_blank" rel="noopener">{icon("chat")}<span>Nhắn Zalo</span></a>
    </div>
  </div>
</section>"""


def business_schema():
    lat, lng = SITE["geo"]
    s = {
        "@context": "https://schema.org",
        "@type": ["LocalBusiness", "TaxiService"],
        "@id": SITE["domain"] + "/#business",
        "name": SITE["name"],
        "url": SITE["domain"] + "/",
        "telephone": tel(),
        "image": SITE["domain"] + "/assets/img/og-cover.jpg",
        "logo": SITE["domain"] + "/assets/img/apple-touch-icon.png",
        "priceRange": f"{min(low(p) for r in ROUTES for _, p, _, _ in price_rows(r) if p):,}₫ – "
                      f"{max(high(p) for r in ROUTES for _, p, _, _ in price_rows(r) if p):,}₫".replace(",", "."),
        "currenciesAccepted": "VND",
        "paymentAccepted": "Tiền mặt, Chuyển khoản",
        "address": {"@type": "PostalAddress", "addressLocality": SITE["city"], "addressCountry": "VN"},
        "geo": {"@type": "GeoCoordinates", "latitude": lat, "longitude": lng},
        "openingHoursSpecification": {"@type": "OpeningHoursSpecification",
                                      "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                                      "opens": "00:00", "closes": "23:59"},
        "areaServed": sorted({r["a"] for r in ROUTES} | {r["b"] for r in ROUTES}),
        "sameAs": [f"https://zalo.me/{SITE['zalo']}"],
        "hasOfferCatalog": {
            "@type": "OfferCatalog", "name": "Bảng giá xe ghép, xe tiện chuyến",
            "itemListElement": [{
                "@type": "Offer", "name": f"Xe ghép {r['a']} – {r['b']}",
                "url": f"{SITE['domain']}/tuyen/{r['slug']}.html",
                "priceSpecification": {"@type": "UnitPriceSpecification", "price": min_price(r)[0] * 1000,
                                       "priceCurrency": "VND", "unitText": "ghế" if r["ghep"] else "xe"}} for r in ROUTES]},
    }
    if SITE["email"]:
        s["email"] = SITE["email"]
    return s


def faq_schema(items):
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in items]}


# ------------------------------------------------------------------ pages

def page_home():
    base = ""
    w1, n = split_words("Xe ghép liên tỉnh")
    w2, n = split_words("đón tận nơi,", n, " h1-word--hl")
    w3, n = split_words("đúng giờ, giá rõ.", n)
    rot = json.dumps([f"{r['a']} ⇄ {r['b']}" for r in ROUTES], ensure_ascii=False)
    marquee_items = "".join(
        f'<li><span>{e(r["a"])}</span>{icon("swap")}<span>{e(r["b"])}</span><b>{from_price(r)}</b></li>' for r in ROUTES)
    marquee_items2 = "".join(
        f'<li><span>Bao xe {e(r["a"])} – {e(r["b"])}</span><b>{k(r["bao"])}</b></li>' for r in reversed(ROUTES))
    tickets = "".join(ticket(r, base) for r in ROUTES)
    group_chips = "".join(
        f'<button class="chip" type="button" data-filter-group="{g}" aria-pressed="false">{e(lbl)}</button>' for g, lbl in GROUPS)
    s = SERVICES
    bento = f"""
    <article class="bento__item bento__item--xl card" data-spotlight data-reveal>
      {img(base, s[0]['img'], 'Xe 7 chỗ đời mới chạy tuyến xe ghép liên tỉnh', '(max-width: 1024px) 100vw, 66vw', 'bento__img')}
      <div class="bento__content bento__content--over">
        <span class="badge badge--dark">{icon("users")} Phổ biến nhất</span>
        <h3>{s[0]['title']}</h3><p>{s[0]['text']}</p>
        <div class="bento__foot"><b class="bento__price">{s[0]['price']}</b>
          <button class="btn btn-primary btn-sm" type="button" data-book data-kind="{s[0]['type']}">Đặt xe ghép {icon("arrow")}</button></div>
      </div>
    </article>
    <article class="bento__item bento__item--tall card" data-spotlight data-reveal>
      {img(base, s[2]['img'], 'Cánh máy bay – dịch vụ đưa đón sân bay Nội Bài, Cát Bi, Vân Đồn', '(max-width: 1024px) 100vw, 33vw', 'bento__img bento__img--top')}
      <div class="bento__content">
        <span class="bento__icon">{icon("plane")}</span>
        <h3>{s[2]['title']}</h3><p>{s[2]['text']}</p>
        <div class="bento__foot"><b class="bento__price">{s[2]['price']}</b>
          <button class="btn btn-ghost-dark btn-sm" type="button" data-book data-kind="Bao xe">Đặt xe {icon("arrow")}</button></div>
      </div>
    </article>
    <article class="bento__item bento__item--wide card" data-spotlight data-reveal>
      <div class="bento__content">
        <span class="bento__icon">{icon("car")}</span>
        <h3>{s[1]['title']}</h3><p>{s[1]['text']}</p>
        <div class="bento__foot"><b class="bento__price">{s[1]['price']}</b>
          <button class="btn btn-ghost-dark btn-sm" type="button" data-book data-kind="Bao xe">Bao xe {icon("arrow")}</button></div>
      </div>
      {img(base, s[1]['img'], 'Xe tiện chuyến trên cung đường dài', '(max-width: 1024px) 100vw, 33vw', 'bento__img bento__img--side')}
    </article>
    <article class="bento__item bento__item--accent card" data-spotlight data-reveal>
      <span class="bento__icon">{icon("repeat")}</span>
      <p class="bento__big">-70%</p>
      <h3>Lượt về khứ hồi</h3><p>Đặt 2 chiều, lượt về giảm đến 70% tuỳ quãng đường.</p>
    </article>
    <article class="bento__item bento__item--call card" data-spotlight data-reveal>
      <h3>Gấp? Gọi thẳng tổng đài</h3>
      <p>Xếp chuyến sớm nhất, kể cả nửa đêm và ngày lễ.</p>
      <a class="bento__call-num" href="tel:{tel()}">{icon("phone")}{SITE['phone_display']}</a>
    </article>
    <article class="bento__item bento__item--wide card" data-spotlight data-reveal>
      <div class="bento__content">
        <span class="bento__icon">{icon("heart")}</span>
        <h3>{s[3]['title']}</h3><p>{s[3]['text']}</p>
        <div class="bento__foot"><b class="bento__price">{s[3]['price']}</b>
          <a class="btn btn-ghost-dark btn-sm" href="tel:{tel()}">Gọi báo giá {icon("phone")}</a></div>
      </div>
      {img(base, s[3]['img'], 'Tài xế cầm lái an toàn trên đường phố', '(max-width: 1024px) 100vw, 33vw', 'bento__img bento__img--side')}
    </article>"""
    stats = "".join(
        f'<li data-reveal><p class="stat__num"><span data-count="{v}">{v}</span>{e(suf)}</p><p class="stat__label">{e(lbl)}</p></li>'
        for v, suf, lbl in STATS)
    commits = "".join(
        f'<li class="commit" data-reveal><span class="commit__icon">{icon(ic)}</span><div><h3>{e(t)}</h3><p>{e(d)}</p></div></li>'
        for ic, t, d in COMMITMENTS)
    route_cards = "".join(
        f"""<li data-reveal><a class="route-link card" href="tuyen/{r['slug']}.html">
          <span class="route-link__name">Xe ghép {e(r['a'])} – {e(r['b'])}</span>
          <span class="route-link__meta">{r['km']} km · {e(r['time'])} · từ <b>{from_price(r)}</b></span>
          {icon("arrow", "ico route-link__arrow")}</a></li>""" for r in ROUTES)

    title = "Xe Ghép Hà Nội – Hải Phòng – Quảng Ninh | Đón Tận Nơi 24/7"
    desc = (f"Xe ghép, xe tiện chuyến Hà Nội – Hải Phòng – Hạ Long, Cẩm Phả, Móng Cái từ {MIN_GHEP}K/ghế. "
            f"Đón tận nơi, sân bay Nội Bài, Cát Bi. Gọi {SITE['phone_display']}.")
    website = {"@context": "https://schema.org", "@type": "WebSite", "@id": SITE["domain"] + "/#website",
               "url": SITE["domain"] + "/", "name": SITE["name"], "inLanguage": "vi-VN",
               "publisher": {"@id": SITE["domain"] + "/#business"}}

    body = f"""{head(title, desc, "/", base, schemas=[business_schema(), website, faq_schema(FAQ)])}
<body class="page-home">
{header(base, True)}
<main id="noi-dung">
<section class="hero" aria-labelledby="hero-title">
  {hero_media(base, "Đường cao tốc về đêm với vệt đèn xe – dịch vụ xe ghép liên tỉnh")}
  <div class="container hero-grid">
    <div class="hero__copy">
      <p class="pill" data-anim style="--d:0"><span class="pill__dot"></span>Xe ghép · Bao xe · Sân bay — 24/7</p>
      <h1 class="h1" id="hero-title">{w1}<br> {w2}<br> {w3}</h1>
      <p class="hero__lead" data-anim style="--d:6">Chuyến <span class="rotator" data-rotate='{e(rot)}'><span class="rotator__text">{e(ROUTES[0]['a'])} ⇄ {e(ROUTES[0]['b'])}</span></span>
        hôm nay còn chỗ. Xe đời mới, ưu tiên cao tốc, không bắt khách dọc đường, giá trọn gói báo trước.</p>
      <ul class="hero__points" data-anim style="--d:8">
        <li>{icon("home")}Đón trả tận nhà &amp; sân bay</li><li>{icon("tag")}Từ {MIN_GHEP}K/ghế</li><li>{icon("shield")}Không thu cọc</li></ul>
      <div class="hero__ctas" data-anim style="--d:10">
        <a class="btn btn-primary btn-lg" href="tel:{tel()}" data-magnet>{icon("phone")}<span>Gọi {SITE['phone_display']}</span></a>
        <a class="btn btn-ghost btn-lg" href="https://zalo.me/{SITE['zalo']}" target="_blank" rel="noopener">{icon("chat")}<span>Chat Zalo</span></a>
      </div>
    </div>
    <div class="hero__form" id="dat-xe" data-anim style="--d:4">{booking_form()}</div>
  </div>
</section>

<div class="marquee-clip"><section class="marquee" aria-label="Các tuyến và giá xe ghép">
  <ul class="marquee-track">{marquee_items}{marquee_items.replace('<li>', '<li aria-hidden="true">')}</ul>
  <ul class="marquee-track marquee-track--rev" aria-hidden="true">{marquee_items2}{marquee_items2}</ul>
</section></div>

<section class="section" id="bang-gia" aria-labelledby="price-title">
  <div class="container">
    <p class="eyebrow" data-reveal>Bảng giá toàn tuyến</p>
    <h2 class="h2" id="price-title" data-float>Giá rõ từng tuyến, không phát sinh</h2>
    <div class="filters" data-reveal>
      <div class="chips" role="group" aria-label="Lọc theo tuyến">
        <button class="chip" type="button" data-filter-group="all" aria-pressed="true">Tất cả tuyến</button>{group_chips}
      </div>
      <div class="tabs tabs--3" role="group" aria-label="Lọc theo loại chuyến">
        <button class="tab" type="button" data-filter-kind="all" aria-pressed="true">Tất cả</button>
        <button class="tab" type="button" data-filter-kind="bao" aria-pressed="false">Bao xe</button>
        <button class="tab" type="button" data-filter-kind="ghep" aria-pressed="false">Xe ghép</button>
        <span class="tabs__ink" aria-hidden="true"></span>
      </div>
    </div>
    <div class="ticket-grid" id="ticket-grid" aria-live="polite">{tickets}</div>
    <p class="note">{icon("tag")} Giá tham khảo đã gồm xăng xe, lái xe và vé cao tốc. Ghép tính theo ghế, bao xe tính theo xe. Điểm đón quá xa trung tâm có thể có phụ phí nhỏ, báo rõ trước khi đi.</p>
  </div>
</section>

<section class="section section--alt" id="dich-vu" aria-labelledby="svc-title">
  <div class="container">
    <p class="eyebrow" data-reveal>Dịch vụ</p>
    <h2 class="h2" id="svc-title" data-float>Một cuộc gọi, đủ mọi kiểu đi</h2>
    <div class="bento">{bento}</div>
  </div>
</section>

<section class="section" id="quy-trinh" aria-labelledby="how-title">
  <div class="container">
    <p class="eyebrow" data-reveal>Cách đặt xe</p>
    <h2 class="h2" id="how-title" data-float>3 bước, chưa tới 1 phút</h2>
    <ol class="steps">
      <li class="step" data-reveal><span class="step__num">01</span><span class="step__icon">{icon("send")}</span>
        <h3>Gửi yêu cầu</h3><p>Điền form, gọi {SITE['phone_display']} hoặc nhắn Zalo: điểm đón, điểm đến, giờ đi.</p></li>
      <li class="step" data-reveal><span class="step__num">02</span><span class="step__icon">{icon("phone")}</span>
        <h3>Xác nhận trong 5 phút</h3><p>Tổng đài gọi lại chốt giá trọn gói, gửi biển số xe và SĐT tài xế.</p></li>
      <li class="step" data-reveal><span class="step__num">03</span><span class="step__icon">{icon("car")}</span>
        <h3>Xe đón tận nơi</h3><p>Tài xế gọi trước 15 phút. Lên xe, thắt dây an toàn, thanh toán khi tới nơi.</p></li>
    </ol>
  </div>
</section>

<section class="stats" aria-label="Con số nổi bật">
  <div class="container"><ul class="stats__grid">{stats}</ul></div>
</section>

<section class="section" aria-labelledby="commit-title">
  <div class="container commit-wrap">
    <div class="commit-media" data-reveal>{img(base, "doi-xe", "Bãi đỗ với nhiều xe sẵn sàng phục vụ khách", "(max-width: 1024px) 100vw, 45vw")}</div>
    <div>
      <p class="eyebrow" data-reveal>Cam kết</p>
      <h2 class="h2" id="commit-title" data-float>Đi xa vẫn yên tâm như ngồi xe nhà</h2>
      <ul class="commits">{commits}</ul>
    </div>
  </div>
</section>

<section class="section section--alt" id="tuyen-duong" aria-labelledby="routes-title">
  <div class="container">
    <p class="eyebrow" data-reveal>Tuyến đường</p>
    <h2 class="h2" id="routes-title" data-float>Tuyến xe ghép chạy mỗi ngày</h2>
    <ul class="route-list">{route_cards}</ul>
  </div>
</section>

{faq_block(FAQ)}
{cta_block()}
</main>
{footer(base)}"""
    (ROOT / "index.html").write_text(body, encoding="utf-8")


def page_route(r):
    base = "../"
    path = f"/tuyen/{r['slug']}.html"
    A, B = r["a"], r["b"]
    areas_a = AREAS.get(A, A)
    others = [o for o in ROUTES if o is not r]
    rows = price_rows(r)
    mp, mu = min_price(r)
    ghep_txt = f"{k(r['ghep'])}/ghế" if r["ghep"] else "liên hệ báo giá"
    bao_txt = ", ".join(f"{lbl.lower()} {k(p)}" for lbl, p, _, kind in rows if kind == "bao")
    title = f"Xe Ghép {A} – {B} Giá Từ {mp}K, Đón Tận Nơi 24/7 | {SITE['name']}"
    if len(title) > 70:
        title = f"Xe Ghép {A} – {B} Giá Từ {mp}K, Đón Tận Nơi 24/7"
    price_short = f"chỉ {k(r['ghep'])}/ghế, bao xe từ {k(r['bao'])}" if r["ghep"] else f"bao xe riêng từ {k(r['bao'])}"
    desc = (f"Xe ghép {A} đi {B} {price_short}. {r['km']} km, {r['time']}. "
            f"Đón trả tận nơi, giá trọn gói, chạy 24/7. Gọi {SITE['phone_display']}.")
    faqs = [
        (f"Giá xe ghép {A} – {B} bao nhiêu?",
         f"Xe ghép {A} – {B}: ghép ghế {ghep_txt}; {bao_txt}. "
         "Giá trọn gói đã gồm xăng xe, lái xe và vé cao tốc, được chốt khi tổng đài xác nhận."),
        (f"Đi xe từ {A} đến {B} mất bao lâu?",
         f"Quãng đường khoảng {r['km']} km, xe đi mất {r['time']} theo {r['via']}, tuỳ tình trạng giao thông."),
        (f"Xe ghép {A} – {B} đón ở đâu?",
         f"Xe đón trả tận nơi tại {areas_a} và {r['areas_b']}. Điểm xa trung tâm vui lòng báo khi đặt."),
        (f"Xe {A} – {B} có chạy ban đêm không?",
         "Có. Xe chạy liên tục 24/7, kể cả chuyến đêm và ngày lễ Tết. Chuyến sau 22h nên đặt trước để được xếp xe."),
        ("Đặt xe như thế nào?",
         f"Điền form trên trang, gọi {SITE['phone_display']} hoặc nhắn Zalo. Tổng đài gọi lại xác nhận trong 5 phút."),
    ]
    crumbs = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Trang chủ", "item": SITE["domain"] + "/"},
        {"@type": "ListItem", "position": 2, "name": "Tuyến đường", "item": SITE["domain"] + "/#tuyen-duong"},
        {"@type": "ListItem", "position": 3, "name": f"Xe ghép {A} – {B}", "item": SITE["domain"] + path}]}
    service = {"@context": "https://schema.org", "@type": "Service", "serviceType": "Xe ghép, bao xe liên tỉnh",
               "name": f"Xe ghép {A} – {B}", "description": desc, "url": SITE["domain"] + path,
               "provider": {"@id": SITE["domain"] + "/#business", "@type": "LocalBusiness", "name": SITE["name"], "telephone": tel()},
               "areaServed": [A, B],
               "offers": {"@type": "AggregateOffer", "priceCurrency": "VND",
                          "lowPrice": min(low(p) for _, p, _, _ in rows if p),
                          "highPrice": max(high(p) for _, p, _, _ in rows if p),
                          "offerCount": sum(1 for _, p, _, _ in rows if p)}}
    others_html = "".join(
        f'<li><a class="route-link card" href="{o["slug"]}.html"><span class="route-link__name">Xe ghép {e(o["a"])} – {e(o["b"])}</span>'
        f'<span class="route-link__meta">từ <b>{from_price(o)}</b></span>{icon("arrow", "ico route-link__arrow")}</a></li>'
        for o in sorted(others, key=lambda o: o["group"] != r["group"]))
    w1, n = split_words(f"Xe ghép {A}")
    w2, n = split_words(f"đi {B}", n, " h1-word--hl")
    pic = "san-bay-noi-bai" if "Vân Đồn" in B else ("duong-dai" if r["km"] > 150 else "xe-5-cho")
    chips = "".join(f'<li><span>{e(lbl)}</span><b>{pr(p, unit or "/xe")}</b></li>'
                    for lbl, p, unit, _ in rows if p)
    table_rows = "".join(
        f'<tr><td>{"Xe ghép" if kind == "ghep" else "Bao xe riêng"}</td><td>{e(lbl.replace("Bao xe ", "").replace("Ghép ghế", "4–7 chỗ").replace("riêng", "4–5 chỗ"))}</td>'
        f'<td>{"<b>" + k(p) + "</b>" + (unit or "/xe") if p else "Liên hệ báo giá"}</td></tr>' for lbl, p, unit, kind in rows)
    if r["ghep"]:
        price_para = (f"Đi ghép chỉ <strong>{k(r['ghep'])}/ghế</strong> — rẻ hơn nhiều so với taxi, không chen chúc như xe khách. "
                      f"Cần riêng tư cho gia đình hoặc nhóm bạn, bao xe riêng chỉ từ <strong>{k(r['bao'])}</strong>.")
    else:
        price_para = (f"Tuyến này chủ yếu chạy bao xe riêng, giá từ <strong>{k(r['bao'])}</strong>/xe — "
                      "rẻ hơn taxi nhờ tận dụng xe chạy chiều về. Xe ghép theo ngày, gọi tổng đài để hỏi chuyến.")

    body = f"""{head(title, desc, path, base, schemas=[service, crumbs, faq_schema(faqs)])}
<body class="page-route">
{header(base, False)}
<main id="noi-dung">
<section class="hero hero--route" aria-labelledby="hero-title">
  {hero_media(base, f"Xe ghép {A} đi {B} trên cao tốc")}
  <div class="container hero-grid">
    <div class="hero__copy">
      <nav class="crumbs" aria-label="Breadcrumb" data-anim style="--d:0"><ol>
        <li><a href="../index.html">Trang chủ</a></li><li><a href="../index.html#tuyen-duong">Tuyến đường</a></li>
        <li aria-current="page">{e(A)} – {e(B)}</li></ol></nav>
      <h1 class="h1 h1--route" id="hero-title">{w1}<br> <span class="nowrap">{w2}</span></h1>
      <p class="hero__lead" data-anim style="--d:5">Đón tận nơi, giá trọn gói, xe chạy 24/7.</p>
      <ul class="route-meta" data-anim style="--d:6">
        <li>{icon("route")}{r['km']} km</li><li>{icon("clock")}{e(r['time'])}</li><li>{icon("car")}{e(r['road'])}</li></ul>
      <ul class="price-chips" data-anim style="--d:7">{chips}</ul>
      <div class="hero__ctas" data-anim style="--d:9">
        <a class="btn btn-primary btn-lg" href="tel:{tel()}" data-magnet>{icon("phone")}<span>Gọi {SITE['phone_display']}</span></a>
        <a class="btn btn-ghost btn-lg" href="https://zalo.me/{SITE['zalo']}" target="_blank" rel="noopener">{icon("chat")}<span>Chat Zalo</span></a>
      </div>
    </div>
    <div class="hero__form" id="dat-xe" data-anim style="--d:4">{booking_form(A, B, "Xe ghép" if r["ghep"] else "Bao xe")}</div>
  </div>
</section>

<section class="section" aria-labelledby="about-title">
  <div class="container article-grid">
    <article class="prose">
      <p class="eyebrow" data-reveal>Thông tin tuyến</p>
      <h2 class="h2" id="about-title" data-float>Xe ghép {e(A)} đi {e(B)} có gì khác?</h2>
      <p data-reveal>Dịch vụ xe ghép {e(A)} – {e(B)} của {e(SITE['name'])} đón bạn ngay tại cửa nhà và trả tận nơi cần đến,
        không phải ra bến, không phải chờ xe khách bắt khách dọc đường. Quãng đường khoảng <strong>{r['km']} km</strong>,
        xe chạy theo {e(r['via'])}, mất <strong>{e(r['time'])}</strong>.</p>
      <p data-reveal>{price_para}</p>
      <p class="tip" data-reveal>{icon("sparkle")}<span><strong>Mẹo:</strong> {e(r['tip'])}</span></p>
      <h3 data-reveal>Bảng giá xe {e(A)} – {e(B)}</h3>
      <div class="table-wrap" data-reveal><table class="price-table">
        <thead><tr><th scope="col">Hình thức</th><th scope="col">Loại xe</th><th scope="col">Giá tham khảo</th></tr></thead>
        <tbody>
          {table_rows}
          <tr><td>Xe đoàn</td><td>16–45 chỗ</td><td>Báo giá theo lịch trình</td></tr>
        </tbody></table></div>
      <h3 data-reveal>Điểm đón trả</h3>
      <ul class="areas" data-reveal>
        <li>{icon("pin")}<div><b>{e(A)}:</b> {e(areas_a)}</div></li>
        <li>{icon("pin")}<div><b>{e(B)}:</b> {e(r['areas_b'])}</div></li></ul>
    </article>
    <aside class="article-aside" data-reveal>
      {img(base, pic, f"Xe phục vụ tuyến {A} – {B}", "(max-width: 1024px) 100vw, 40vw", "aside-img")}
      <div class="aside-card card">
        <h3>Đặt nhanh tuyến này</h3>
        <ul class="aside-list"><li>{icon("check")}Không thu cọc</li><li>{icon("check")}Huỷ miễn phí trước 2 giờ</li><li>{icon("check")}Thanh toán khi tới nơi</li></ul>
        <a class="btn btn-primary btn-block" href="tel:{tel()}">{icon("phone")}<span>{SITE['phone_display']}</span></a>
      </div>
    </aside>
  </div>
</section>

{faq_block(faqs, f"Hỏi đáp xe ghép {A} – {B}")}

<section class="section" aria-labelledby="other-title">
  <div class="container">
    <p class="eyebrow" data-reveal>Tuyến khác</p>
    <h2 class="h2" id="other-title" data-float>Có thể bạn cũng cần</h2>
    <ul class="route-list">{others_html}</ul>
  </div>
</section>
{cta_block()}
</main>
{footer(base)}"""
    (ROOT / "tuyen").mkdir(exist_ok=True)
    (ROOT / "tuyen" / f"{r['slug']}.html").write_text(body, encoding="utf-8")


def write_misc():
    today = date.today().isoformat()
    urls = [("/", "1.0", "weekly")] + [(f"/tuyen/{r['slug']}.html", "0.8", "monthly") for r in ROUTES]
    sm = "".join(f"<url><loc>{SITE['domain']}{u}</loc><lastmod>{today}</lastmod><changefreq>{c}</changefreq><priority>{p}</priority></url>"
                 for u, p, c in urls)
    (ROOT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>\n', encoding="utf-8")
    (ROOT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nDisallow: /_build/\n\nSitemap: {SITE['domain']}/sitemap.xml\n", encoding="utf-8")
    (ROOT / "site.webmanifest").write_text(json.dumps({
        "name": SITE["name"], "short_name": SITE["name"], "lang": "vi", "start_url": "/", "display": "standalone",
        "background_color": "#0B1324", "theme_color": "#0B1324",
        "icons": [{"src": "/assets/img/apple-touch-icon.png", "sizes": "180x180", "type": "image/png"},
                  {"src": "/favicon.svg", "sizes": "any", "type": "image/svg+xml"}]}, ensure_ascii=False, indent=2), encoding="utf-8")
    cfg = {
        "phone": SITE["phone"], "phoneDisplay": SITE["phone_display"], "zalo": SITE["zalo"],
        "endpoint": SITE["booking_endpoint"],
        "routes": [{"a": r["a"], "b": r["b"], "ghep": r["ghep"], "bao": r["bao"],
                    "bao7": r.get("bao7"), "bao16": r.get("bao16"),
                    "keys": [slugify(r["a"]), slugify(r["b"])]} for r in ROUTES],
    }
    (ROOT / "assets" / "js").mkdir(parents=True, exist_ok=True)
    (ROOT / "assets" / "js" / "config.js").write_text(
        "// Sinh tự động bởi _build/build.py — đừng sửa tay.\nwindow.SITE_CONFIG = "
        + json.dumps(cfg, ensure_ascii=False, indent=2) + ";\n", encoding="utf-8")


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    page_home()
    for route in ROUTES:
        page_route(route)
    write_misc()
    print(f"Đã sinh index.html + {len(ROUTES)} trang tuyến + sitemap.xml, robots.txt, site.webmanifest, config.js")
