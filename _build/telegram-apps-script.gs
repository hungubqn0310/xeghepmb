/**
 * Nhận đơn đặt xe từ website và gửi về Telegram (Google Apps Script).
 *
 * Token và chat_id KHÔNG ghi trong file này — đặt trong
 * Project Settings → Script properties:
 *   TELEGRAM_TOKEN   = 123456:ABC...   (lấy từ @BotFather)
 *   TELEGRAM_CHAT_ID = 123456789       (nhóm thì là số âm, VD -1001234567890)
 *
 * Deploy → New deployment → Web app → Execute as: Me, Who has access: Anyone
 * → copy URL .../exec dán vào SITE["booking_endpoint"] trong build.py.
 */

function doPost(e) {
  try {
    var d = JSON.parse(e.postData.contents || '{}');
    if (!d.sdt || !d.diem_don || !d.diem_den) return reply({ ok: false, error: 'missing' });
    sendTelegram(formatMessage(d));
    return reply({ ok: true });
  } catch (err) {
    console.error(err);
    return reply({ ok: false, error: String(err) });
  }
}

function formatMessage(d) {
  var phone = String(d.sdt).replace(/[^\d+]/g, '');
  var lines = [
    '🚗 <b>ĐƠN ' + esc(d.loai || 'ĐẶT XE').toUpperCase() + '</b>',
    '',
    '📍 <b>Từ:</b> ' + esc(d.diem_don),
    '🏁 <b>Đến:</b> ' + esc(d.diem_den),
    '🕒 <b>Giờ đón:</b> ' + esc(d.gio_don),
    '👥 <b>Số người:</b> ' + esc(d.so_nguoi) + (d.loai_xe ? ' · ' + esc(d.loai_xe) : ''),
    '👤 <b>Khách:</b> ' + esc(d.ho_ten || '(chưa có tên)'),
    '📞 <b>SĐT:</b> <a href="tel:' + phone + '">' + esc(d.sdt) + '</a>',
  ];
  if (d.ghi_chu) lines.push('📝 <b>Ghi chú:</b> ' + esc(d.ghi_chu));
  if (d.trang) lines.push('', '<i>Từ trang: ' + esc(d.trang) + '</i>');
  return lines.join('\n');
}

function sendTelegram(text) {
  var props = PropertiesService.getScriptProperties();
  var token = props.getProperty('TELEGRAM_TOKEN');
  var chatId = props.getProperty('TELEGRAM_CHAT_ID');
  var res = UrlFetchApp.fetch('https://api.telegram.org/bot' + token + '/sendMessage', {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify({ chat_id: chatId, text: text, parse_mode: 'HTML', disable_web_page_preview: true }),
    muteHttpExceptions: true,
  });
  if (res.getResponseCode() !== 200) throw new Error('Telegram: ' + res.getContentText());
}

function esc(s) {
  return String(s == null ? '' : s).slice(0, 500)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function reply(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

/** Chạy hàm này trong trình soạn thảo để thử gửi 1 tin mẫu. */
function testGui() {
  sendTelegram(formatMessage({
    loai: 'Xe ghép', diem_don: 'Cầu Giấy, Hà Nội', diem_den: 'TP Thanh Hóa', gio_don: '08:00 T7, 01/11',
    so_nguoi: '2', ho_ten: 'Khách thử', sdt: '0912345678', ghi_chu: 'Tin thử từ Apps Script',
  }));
}
