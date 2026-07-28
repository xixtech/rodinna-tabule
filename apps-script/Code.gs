/**
 * Rodinná tabule – datové API.
 *
 * Běží zdarma u Googlu (Apps Script), takže doma nemusí nic běžet 24/7.
 * Poskytuje dashboardu tři věci:
 *   1) události z Google kalendářů nasdílených účtu tabule
 *   2) seznamy a poznámku, které do něj posílá iOS Zkratka z Apple Poznámek
 *   3) čas poslední synchronizace, ať tabule pozná zastaralá data
 *
 * NASAZENÍ
 *   0) Přihlas se do SAMOSTATNÉHO Google účtu zřízeného jen pro tabuli.
 *      Ne do svého osobního — viz komentář u CONFIG.CALENDARS.
 *   1) script.google.com → Nový projekt → vlož tenhle soubor
 *   2) Spusť `vypisKalendare` → v Protokolu najdeš ID všech kalendářů
 *   3) Vyplň CONFIG níž (TOKEN + CALENDARS)
 *   4) Nasadit → Nová implementace → Typ: Webová aplikace
 *        Spustit jako:      Já
 *        Kdo má přístup:    Kdokoli
 *   5) Zkopíruj URL končící na /exec – to je `api` pro dashboard i pro Zkratku
 *
 * Po každé úpravě skriptu nasaď NOVOU VERZI, jinak /exec běží na staré.
 */

var CONFIG = {

  /** Dlouhý náhodný řetězec, stejný jako v nastavení tabule a ve Zkratce.
   *  Vygenerovat: openssl rand -hex 24 */
  TOKEN: 'ZMEN-ME-na-dlouhy-nahodny-retezec',

  /** Kalendáře k zobrazení – ID zjistíš funkcí `vypisKalendare`.
   *
   *  Tenhle skript má běžet pod SAMOSTATNÝM Google účtem zřízeným jen pro
   *  tabuli, ne pod tvým osobním. Ten účet vidí výhradně kalendáře, které mu
   *  někdo vědomě nasdílel — takže se k tvému osobnímu ani pracovnímu
   *  kalendáři nedostane, protože k nim nemá přístup, ne protože mu to
   *  zakazuje řádek v konfiguraci.
   *
   *  Nepoužívej 'primary' — primární kalendář účtu tabule je prázdný a nemá
   *  co zobrazovat. Vyjmenuj sem ID nasdílených kalendářů.
   */
  CALENDARS: [
    { id: 'adresa.manzelky@gmail.com', label: 'Žena',   color: '#ff8c9b' },
    { id: 'adresa.svozy@gmail.com',    label: 'Svozy',  color: '#7be0a8' },
    { id: 'xxxx@group.calendar.google.com', label: 'Rodina', color: '#bba5ff' }
  ],

  /** Kalendář, do kterého smí tabule zapisovat nové události.
   *
   *  Musí to být kalendář, kde má účet tabule právo měnit události — typicky
   *  ten, který si sám vytvořil („Rodina"). Do manželčina kalendáře zapisovat
   *  nemůže, tam má jen čtení, a je to tak správně.
   *
   *  Dej sem stejné ID jako v CALENDARS, ať je nová událost hned vidět.
   *  Prázdná hodnota vkládání v tabuli vypne. */
  WRITE_CALENDAR: 'xxxx@group.calendar.google.com',

  DEFAULT_DAYS: 14,
  MAX_DAYS: 45,
  MAX_EVENTS: 250,
  MAX_TITLE_LEN: 120,

  /** Události s tímto názvem se vynechají (bloky typu „Zaneprázdněn“). */
  SKIP_TITLES: [/^zanepr[áa]zdn/i, /^busy$/i],

  /** Maximální délka jedné položky seznamu a počet položek – ochrana proti
   *  tomu, aby chybná Zkratka poslala celý román. */
  MAX_ITEM_LEN: 120,
  MAX_ITEMS: 60,
  MAX_NOTE_LEN: 400,

  /** Volné poznámky psané přímo na tabuli. Strop je tu proto, že Script
   *  Properties má limit 9 kB na jednu vlastnost — při překročení by zápis
   *  začal padat, což je horší než odmítnout 41. poznámku. */
  MAX_NOTES: 40,
  MAX_NOTE_TEXT: 500,

  /** Odjezdy PID z Golemio API.
   *
   *  KEY      – klíč zdarma z https://api.golemio.cz/api-keys/
   *  ASW_IDS  – kódy stanovišť, víc oddělených čárkou. NENÍ to jméno zastávky;
   *             kód najdeš skriptem `python3 tools/najdi-zastavku.py "Národní třída"`
   *  LINES    – jen tyhle linky, prázdné pole = všechny
   *  LIMIT    – kolik odjezdů vrátit
   *
   *  Klíč zůstává tady na serveru, do prohlížeče se nedostane. */
  PID: {
    KEY: '',
    ASW_IDS: '',
    LINES: [],
    LIMIT: 8,
    MINUTES_AFTER: 180
  }
};

var PROPS = PropertiesService.getScriptProperties();

/* ══════════════════════════════  GET  ═══════════════════════════════ */

function doGet(e) {
  var p = (e && e.parameter) || {};
  var cb = sanitizeCallback(p.callback);

  try {
    if (p.token !== CONFIG.TOKEN) return out({ error: 'unauthorized' }, cb);

    // Zakládání události jde přes GET schválně. Prohlížeč by na POST s JSON
    // tělem poslal preflight OPTIONS, který Apps Script neumí obsloužit, a
    // celé by to spadlo na CORS. GET projde vždy, včetně JSONP fallbacku.
    if (p.action === 'addEvent') return out(addEvent(p), cb);
    if (p.action === 'addNote')  return out(addNote(p), cb);
    if (p.action === 'delNote')  return out(delNote(p), cb);
    if (p.action === 'pid')      return out(pidDepartures(), cb);

    var days = parseInt(p.days, 10);
    if (!days || days < 1) days = CONFIG.DEFAULT_DAYS;
    if (days > CONFIG.MAX_DAYS) days = CONFIG.MAX_DAYS;

    return out({
      generatedAt: new Date().toISOString(),
      days: days,
      events: collectEvents(days),
      lists: readLists(),
      notes: readNotes(),
      note: PROPS.getProperty('note') || '',
      syncedAt: PROPS.getProperty('syncedAt') || null
    }, cb);

  } catch (err) {
    return out({ error: String((err && err.message) || err) }, cb);
  }
}

/* ══════════════════════════════  POST  ══════════════════════════════ */

/**
 * Přijímá obsah Apple Poznámek z iOS Zkratky.
 *
 * Tělo požadavku (JSON):
 *   { "token": "...", "shopping": "mléko\npečivo", "tasks": "...", "note": "..." }
 *
 * Vynechané klíče se nemažou – Zkratka může posílat jen to, co zrovna čte.
 * Prázdný string ale seznam smaže, aby šel vyprázdnit.
 */
function doPost(e) {
  try {
    var body = {};

    // Zkratky umí poslat tělo jako JSON, jako formulář, nebo (po přesměrování
    // na googleusercontent) jen jako query parametry. Bereme všechny tři.
    if (e && e.postData && e.postData.contents) {
      try {
        body = JSON.parse(e.postData.contents);
      } catch (parseErr) {
        body = {};   // nebyl JSON – spolehneme se na e.parameter níž
      }
    }
    if (e && e.parameter) {
      ['token', 'tasks', 'shopping', 'note'].forEach(function (k) {
        if (body[k] === undefined && typeof e.parameter[k] === 'string') {
          body[k] = e.parameter[k];
        }
      });
    }

    if (body.token !== CONFIG.TOKEN) return out({ error: 'unauthorized' }, null);

    var touched = [];

    ['tasks', 'shopping'].forEach(function (key) {
      if (typeof body[key] !== 'string') return;
      PROPS.setProperty('list.' + key, JSON.stringify(parseList(body[key])));
      touched.push(key);
    });

    if (typeof body.note === 'string') {
      PROPS.setProperty('note', String(body.note).slice(0, CONFIG.MAX_NOTE_LEN).trim());
      touched.push('note');
    }

    if (!touched.length) return out({ error: 'nothing to store' }, null);

    PROPS.setProperty('syncedAt', new Date().toISOString());
    return out({ ok: true, stored: touched }, null);

  } catch (err) {
    return out({ error: String((err && err.message) || err) }, null);
  }
}

/**
 * Z textu poznámky udělá seznam položek.
 *
 * Apple Poznámky posílají odškrtávací seznam jako řádky textu. Odškrtnuté
 * položky Zkratka nijak neoznačí, takže se poznávají podle běžných zápisů,
 * které lidi v poznámkách používají – odrážky, pomlčky, „x“ na začátku.
 */
function parseList(text) {
  var out = [];

  String(text).split(/\r?\n/).forEach(function (raw) {
    var line = raw.trim();
    if (!line) return;

    // odškrtnuté: ✓ ✔ ☑ x] [x] nebo přeškrtnutá konvence -- text
    var done = /^([✓✔☑✅]|\[[xX✓]\]|x\s|--)\s*/.test(line);

    // uklidit odrážky a značky na začátku
    line = line
      .replace(/^([✓✔☑✅☐□]|\[[ xX✓]?\]|[-–•*]|x)\s+/, '')
      .replace(/^--\s*/, '')
      .trim();

    if (!line) return;
    if (out.length >= CONFIG.MAX_ITEMS) return;

    out.push({ label: line.slice(0, CONFIG.MAX_ITEM_LEN), done: done });
  });

  return out;
}

function readLists() {
  return {
    tasks: readList('tasks'),
    shopping: readList('shopping')
  };
}

function readList(key) {
  try {
    return JSON.parse(PROPS.getProperty('list.' + key) || '[]');
  } catch (err) {
    return [];
  }
}

/* ═════════════════════════  odjezdy PID  ════════════════════════════ */

/**
 * Odjezdy ze zastávky přes Golemio API.
 *
 * Jde to přes proxy ze dvou důvodů: klíč nesmí skončit v prohlížeči a Golemio
 * neposílá CORS hlavičky, takže by přímý dotaz ze stránky stejně neprošel.
 *
 * Odpověď cachujeme 30 s — tabule se ptá častěji, než se data mění, a klíč
 * má omezený počet dotazů.
 */
function pidDepartures() {
  var cfg = CONFIG.PID || {};
  if (!cfg.KEY) return { error: 'chybí Golemio API klíč (CONFIG.PID.KEY)' };
  if (!cfg.ASW_IDS) return { error: 'chybí kód stanoviště (CONFIG.PID.ASW_IDS)' };

  var cache = CacheService.getScriptCache(),
      hit = cache.get('pid');
  if (hit) {
    try { return JSON.parse(hit); } catch (err) { /* spadneme na nové volání */ }
  }

  var url = 'https://api.golemio.cz/v2/pid/departureboards/' +
            '?aswIds=' + encodeURIComponent(cfg.ASW_IDS) +
            '&limit=' + encodeURIComponent(Math.min(30, cfg.LIMIT * 3 || 20)) +
            '&minutesAfter=' + encodeURIComponent(cfg.MINUTES_AFTER || 180) +
            '&skip=atStop&mode=departures&order=real';

  var res;
  try {
    res = UrlFetchApp.fetch(url, {
      method: 'get',
      headers: { 'x-access-token': cfg.KEY },
      muteHttpExceptions: true
    });
  } catch (err) {
    return { error: 'Golemio nedostupné: ' + String((err && err.message) || err) };
  }

  var code = res.getResponseCode();
  if (code === 401 || code === 403) return { error: 'Golemio odmítlo klíč (' + code + ')' };
  if (code !== 200) return { error: 'Golemio vrátilo HTTP ' + code };

  var body;
  try {
    body = JSON.parse(res.getContentText());
  } catch (err) {
    return { error: 'Golemio poslalo něco, co není JSON' };
  }

  var want = (cfg.LINES || []).map(String),
      list = [];

  (body.departures || []).forEach(function (d) {
    var line = String(((d.route || {}).short_name) || '');
    if (want.length && want.indexOf(line) < 0) return;
    if (list.length >= (cfg.LIMIT || 8)) return;

    var ts = d.departure_timestamp || {};
    list.push({
      line: line,
      headsign: ((d.trip || {}).headsign) || '',
      minutes: ts.minutes != null ? String(ts.minutes) : '',
      at: ts.predicted || ts.scheduled || null,
      delay: ((d.delay || {}).minutes != null) ? d.delay.minutes : null,
      ac: !!((d.trip || {}).is_air_conditioned),
      wheelchair: ((d.trip || {}).is_wheelchair_accessible) === true,
      platform: ((d.stop || {}).platform_code) || ''
    });
  });

  var result = {
    departures: list,
    infotexts: (body.infotexts || []).map(function (t) {
      return String(t.text || t.description || '').slice(0, 300);
    }).filter(Boolean).slice(0, 3),
    at: new Date().toISOString()
  };

  cache.put('pid', JSON.stringify(result), 30);
  return result;
}

/* ═══════════════════════  volné poznámky  ═══════════════════════════ */

/**
 * Poznámky psané přímo na tabuli. Drží se u Googlu, ne v localStorage iPadu —
 * vyčištěné úložiště prohlížeče by jinak smazalo i to, co si někdo připsal.
 */
function readNotes() {
  try {
    var n = JSON.parse(PROPS.getProperty('notes') || '[]');
    return Array.isArray(n) ? n : [];
  } catch (err) {
    return [];
  }
}

function writeNotes(notes) {
  PROPS.setProperty('notes', JSON.stringify(notes.slice(0, CONFIG.MAX_NOTES)));
}

function addNote(p) {
  var text = String(p.text || '').trim().slice(0, CONFIG.MAX_NOTE_TEXT);
  if (!text) return { error: 'prázdná poznámka' };

  var notes = readNotes();
  if (notes.length >= CONFIG.MAX_NOTES) {
    return { error: 'poznámek je maximum (' + CONFIG.MAX_NOTES + '), něco smaž' };
  }

  notes.unshift({ id: Utilities.getUuid(), text: text, at: new Date().toISOString() });
  writeNotes(notes);
  return { ok: true, count: notes.length };
}

function delNote(p) {
  var id = String(p.id || '');
  if (!id) return { error: 'chybí id' };

  var notes = readNotes(), before = notes.length;
  notes = notes.filter(function (n) { return n.id !== id; });
  if (notes.length === before) return { error: 'poznámka nenalezena' };

  writeNotes(notes);
  return { ok: true, count: notes.length };
}

/* ═════════════════════  zakládání události  ═════════════════════════ */

/**
 * Vytvoří událost v CONFIG.WRITE_CALENDAR.
 *
 * Parametry: title, date (2026-07-28), a pak buď allDay=1, nebo
 * time (16:30) + minutes (trvání). Volitelně location.
 *
 * Časy se skládají v časové zóně projektu Apps Scriptu — zkontroluj si ji
 * v Nastavení projektu (má být Europe/Prague), jinak ti události poskočí.
 */
function addEvent(p) {
  if (!CONFIG.WRITE_CALENDAR) return { error: 'vkládání není povolené (WRITE_CALENDAR je prázdné)' };

  var cal = openCalendar(CONFIG.WRITE_CALENDAR);
  if (!cal) return { error: 'kalendář pro zápis není dostupný' };

  var title = String(p.title || '').trim().slice(0, CONFIG.MAX_TITLE_LEN);
  if (!title) return { error: 'chybí název' };

  var date = String(p.date || '');
  if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) return { error: 'chybné datum' };

  var ev;
  try {
    if (p.allDay === '1' || p.allDay === 'true') {
      ev = cal.createAllDayEvent(title, atLocal(date));
    } else {
      var time = String(p.time || '');
      if (!/^\d{1,2}:\d{2}$/.test(time)) return { error: 'chybný čas' };
      var mins = parseInt(p.minutes, 10);
      if (!mins || mins < 5) mins = 60;
      if (mins > 24 * 60) mins = 24 * 60;
      var start = atLocal(date, time);
      ev = cal.createEvent(title, start, new Date(start.getTime() + mins * 60000));
    }
    var loc = String(p.location || '').trim().slice(0, CONFIG.MAX_TITLE_LEN);
    if (loc) ev.setLocation(loc);
  } catch (err) {
    return { error: 'kalendář odmítl událost: ' + String((err && err.message) || err) };
  }

  return { ok: true, title: title, date: date };
}

/** '2026-07-28' + '16:30' → Date v časové zóně projektu. */
function atLocal(date, time) {
  var d = date.split('-').map(Number),
      t = String(time || '0:0').split(':').map(Number);
  return new Date(d[0], d[1] - 1, d[2], t[0] || 0, t[1] || 0, 0, 0);
}

/* ═══════════════════════════  kalendáře  ════════════════════════════ */

function collectEvents(days) {
  var start = new Date();
  start.setHours(0, 0, 0, 0);
  var end = new Date(start.getTime() + days * 24 * 60 * 60 * 1000);

  var events = [];

  CONFIG.CALENDARS.forEach(function (c) {
    var cal = openCalendar(c.id);
    if (!cal) {
      Logger.log('Kalendář nedostupný: ' + c.id + ' (nasdílený? správné ID?)');
      return;
    }
    cal.getEvents(start, end).forEach(function (ev) {
      var title = ev.getTitle() || '(bez názvu)';
      if (isSkipped(title)) return;

      events.push({
        title:    title,
        start:    ev.getStartTime().toISOString(),
        end:      ev.getEndTime().toISOString(),   // u celodenních je konec exkluzivní
        allDay:   ev.isAllDayEvent(),
        location: shortLocation(ev.getLocation()),
        label:    c.label,
        color:    c.color
      });
    });
  });

  events.sort(function (a, b) { return a.start < b.start ? -1 : a.start > b.start ? 1 : 0; });
  return events.slice(0, CONFIG.MAX_EVENTS);
}

function openCalendar(id) {
  try {
    return id === 'primary' ? CalendarApp.getDefaultCalendar() : CalendarApp.getCalendarById(id);
  } catch (err) {
    return null;
  }
}

function isSkipped(title) {
  return (CONFIG.SKIP_TITLES || []).some(function (re) { return re.test(title); });
}

/** Z „Bazén Podolí, Podolská 74, Praha 4“ nechá jen „Bazén Podolí“. */
function shortLocation(loc) {
  if (!loc) return '';
  var first = String(loc).split(',')[0].trim();
  return first.length > 40 ? first.slice(0, 39) + '…' : first;
}

/* ════════════════════════════  pomůcky  ═════════════════════════════ */

function out(obj, cb) {
  var body = JSON.stringify(obj);
  if (cb) {
    return ContentService.createTextOutput(cb + '(' + body + ');')
      .setMimeType(ContentService.MimeType.JAVASCRIPT);
  }
  return ContentService.createTextOutput(body)
    .setMimeType(ContentService.MimeType.JSON);
}

/** Callback jde z URL – propustíme jen bezpečný identifikátor. */
function sanitizeCallback(cb) {
  if (!cb) return null;
  return /^[A-Za-z0-9_$]{1,64}$/.test(cb) ? cb : null;
}

/** Spusť ručně (▷ Spustit) a v Protokolu najdeš ID všech kalendářů,
 *  ke kterým má tvůj účet přístup – včetně nasdílených od manželky. */
function vypisKalendare() {
  CalendarApp.getAllCalendars().forEach(function (c) {
    Logger.log(c.getName() + '   ->   ' + c.getId());
  });
}

/** Kontrola před nasazením: načte se kalendář? */
function testApi() {
  var r = doGet({ parameter: { token: CONFIG.TOKEN, days: 7 } });
  Logger.log(r.getContent());
}

/** Kontrola zakládání události. Vytvoří skutečnou událost — pak ji smaž. */
function testAddEvent() {
  var d = new Date();
  var iso = d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') +
            '-' + String(d.getDate()).padStart(2, '0');
  Logger.log(JSON.stringify(addEvent({
    title: 'TEST z tabule – smaž mě',
    date: iso, time: '20:00', minutes: '30', location: 'Doma'
  })));
}

/** Kontrola parsování seznamu z poznámky, bez volání přes web. */
function testPost() {
  var r = doPost({
    postData: {
      contents: JSON.stringify({
        token: CONFIG.TOKEN,
        shopping: '- mléko\n- pečivo\n✓ ovoce\nrajčata',
        note: 'Večer připravit věci dětem.'
      })
    }
  });
  Logger.log(r.getContent());
  Logger.log(JSON.stringify(readLists(), null, 2));
}

/** Kontrola odjezdů PID. Napoví, co přesně Golemio vrátilo. */
function testPid() {
  var r = pidDepartures();
  Logger.log(JSON.stringify(r, null, 2));
  if (r.error) {
    Logger.log('--- Zkontroluj CONFIG.PID: klíč z api.golemio.cz a kód stanoviště ' +
               'ze skriptu tools/najdi-zastavku.py ---');
  }
}

/** Kontrola poznámek bez volání přes web. */
function testNotes() {
  Logger.log(JSON.stringify(addNote({ text: 'Zkušební poznámka' })));
  var n = readNotes();
  Logger.log(JSON.stringify(n, null, 2));
  if (n.length) Logger.log(JSON.stringify(delNote({ id: n[0].id })));
}

/** Kdyby bylo potřeba začít od čistého stolu. */
function smazSeznamy() {
  ['list.tasks', 'list.shopping', 'note', 'notes', 'syncedAt'].forEach(function (k) {
    PROPS.deleteProperty(k);
  });
  Logger.log('Smazáno.');
}
