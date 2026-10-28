// Vercel Serverless Function: nhận đơn đặt xe từ form và gửi về Telegram.
// Biến môi trường (Vercel → Project → Settings → Environment Variables):
//   TELEGRAM_TOKEN    token bot lấy từ @BotFather
//   TELEGRAM_CHAT_ID  id người/nhóm nhận đơn (nhóm là số âm); nhiều nơi thì cách nhau dấu phẩy

const esc = s => String(s == null ? '' : s).slice(0, 500)
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

const PHONE_RE = /^(0|\+?84)(3|5|7|8|9)\d{8}$/;

module.exports = async (req, res) => {
  if (req.method !== 'POST') return res.status(405).json({ ok: false });

  let d = req.body || {};
  if (typeof d === 'string') { try { d = JSON.parse(d); } catch { d = {}; } }

  // Bẫy bot spam: ô ẩn "website" chỉ bot mới điền
  if (d.website) return res.status(200).json({ ok: true });

  const phone = String(d.sdt || '').replace(/[\s.-]/g, '');
  if (!PHONE_RE.test(phone) || !d.diem_don || !d.diem_den) {
    return res.status(400).json({ ok: false, error: 'Thiếu thông tin hoặc SĐT không hợp lệ' });
  }

  const { TELEGRAM_TOKEN, TELEGRAM_CHAT_ID } = process.env;
  if (!TELEGRAM_TOKEN || !TELEGRAM_CHAT_ID) {
    return res.status(500).json({ ok: false, error: 'Chưa cấu hình Telegram' });
  }

  const lines = [
    `🚗 <b>ĐƠN ${esc(d.loai || 'ĐẶT XE').toUpperCase()}</b>`,
    '',
    `📍 <b>Từ:</b> ${esc(d.diem_don)}`,
    `🏁 <b>Đến:</b> ${esc(d.diem_den)}`,
    `🕒 <b>Giờ đón:</b> ${esc(d.gio_don)}`,
    `👥 <b>Số người:</b> ${esc(d.so_nguoi)}${d.loai_xe ? ' · ' + esc(d.loai_xe) : ''}`,
    `👤 <b>Khách:</b> ${esc(d.ho_ten || '(chưa có tên)')}`,
    `📞 <b>SĐT:</b> ${esc(d.sdt)}`,
  ];
  if (d.ghi_chu) lines.push(`📝 <b>Ghi chú:</b> ${esc(d.ghi_chu)}`);
  if (d.trang) lines.push('', `<i>Từ trang: ${esc(d.trang)}</i>`);

  const chatIds = TELEGRAM_CHAT_ID.split(',').map(s => s.trim()).filter(Boolean);
  const results = await Promise.allSettled(chatIds.map(async chatId => {
    const r = await fetch(`https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: chatId,
        text: lines.join('\n'),
        parse_mode: 'HTML',
        disable_web_page_preview: true,
      }),
    });
    if (!r.ok) throw new Error(`${chatId}: ${await r.text()}`);
  }));
  results.filter(x => x.status === 'rejected').forEach(x => console.error('Telegram error:', x.reason));

  // Chỉ cần 1 nơi nhận được là tính thành công
  if (results.some(x => x.status === 'fulfilled')) return res.status(200).json({ ok: true });
  return res.status(502).json({ ok: false, error: 'Không gửi được Telegram' });
};
