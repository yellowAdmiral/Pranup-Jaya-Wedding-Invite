/**
 * Wedding RSVP receiver.
 * Lives inside the guest-list Google Sheet (Extensions > Apps Script) and does two jobs:
 *   GET  ?g=CODE  -> tells the invite page who the code belongs to (name and seats)
 *   POST          -> saves a reply on the "Replies" tab and marks the guest on the "Guests" tab
 *
 * Tabs it expects:
 *   Guests  columns: A Code, B Guest name(s), C Seats, ... H Replied?
 *   Replies created automatically; one row per guest code, newest answer wins.
 */

var GUESTS_TAB = 'Guests';
var REPLIES_TAB = 'Replies';
var REPLIED_COLUMN = 8;            // column H on the Guests tab
var REQUIRE_VALID_CODE = true;     // true: only guests with a real code from the Guests tab can save a reply
var NOTIFY_EMAIL = '';             // optional: an address to email on every reply. Leave '' for none.
var REPLY_HEADERS = ['Time', 'Code', 'Name', 'Reply', 'Celebrations', 'Guests', 'Food needs', 'Note'];

function doGet(e) {
  var code = String((e && e.parameter && e.parameter.g) || '').toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 12);
  var guest = findGuest_(code);
  if (!guest) return json_({ ok: false });
  return json_({
    ok: true,
    name: guest.name,
    seats: guest.seats,
    replied: guest.replied === 'Yes' || guest.replied === 'No'
  });
}

function doPost(e) {
  var d;
  try {
    d = JSON.parse(e.postData.contents);
  } catch (err) {
    return json_({ ok: false, error: 'bad request' });
  }

  var name = clean_(d.name, 120);
  var reply = d.reply === 'Yes' ? 'Yes' : (d.reply === 'No' ? 'No' : '');
  if (!name || !reply) return json_({ ok: false, error: 'missing name or reply' });

  var code = String(d.code || '').toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 12);
  if (REQUIRE_VALID_CODE && !findGuest_(code)) return json_({ ok: false, error: 'unknown code' });
  var guests = reply === 'Yes' ? Math.max(1, Math.min(parseInt(d.guests, 10) || 1, 20)) : 0;
  var record = [
    new Date(), code, name, reply,
    reply === 'Yes' ? clean_(d.events, 200) : '',
    guests,
    reply === 'Yes' ? clean_(d.diet, 200) : '',
    clean_(d.note, 1000)
  ];

  var lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = repliesSheet_(ss);

    var target = 0;
    if (code) {
      var rows = sheet.getDataRange().getValues();
      for (var i = 1; i < rows.length; i++) {
        if (String(rows[i][1]).toUpperCase() === code) { target = i + 1; break; }
      }
    }
    if (target) {
      sheet.getRange(target, 1, 1, record.length).setValues([record]);
    } else {
      sheet.appendRow(record);
    }

    var guest = findGuest_(code);
    if (guest) ss.getSheetByName(GUESTS_TAB).getRange(guest.row, REPLIED_COLUMN).setValue(reply);
  } finally {
    lock.releaseLock();
  }

  if (NOTIFY_EMAIL) {
    try {
      MailApp.sendEmail(NOTIFY_EMAIL, 'RSVP: ' + name + ' (' + (reply === 'Yes' ? 'attending' : 'not attending') + ')',
        name + ' replied ' + reply + (reply === 'Yes' ? ', ' + guests + ' guest(s).' : '.') +
        (record[7] ? '\n\nNote: ' + record[7] : ''));
    } catch (err) { /* a mail problem must never lose the reply */ }
  }
  return json_({ ok: true });
}

function findGuest_(code) {
  if (!code) return null;
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(GUESTS_TAB);
  if (!sheet) return null;
  var rows = sheet.getDataRange().getValues();
  for (var i = 1; i < rows.length; i++) {
    if (String(rows[i][0]).toUpperCase() === code && String(rows[i][1]).trim() !== '') {
      return {
        row: i + 1,
        name: String(rows[i][1]).trim(),
        seats: Number(rows[i][2]) || 0,
        replied: String(rows[i][REPLIED_COLUMN - 1] || '')
      };
    }
  }
  return null;
}

function repliesSheet_(ss) {
  var sheet = ss.getSheetByName(REPLIES_TAB);
  if (!sheet) {
    sheet = ss.insertSheet(REPLIES_TAB);
    sheet.appendRow(REPLY_HEADERS);
  }
  return sheet;
}

// Trim, cap the length, and stop a typed "=..." from being run as a formula.
function clean_(value, max) {
  var s = String(value == null ? '' : value).replace(/[\u0000-\u001f]+/g, ' ').trim().slice(0, max);
  return /^[=+\-@]/.test(s) ? "'" + s : s;
}

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
