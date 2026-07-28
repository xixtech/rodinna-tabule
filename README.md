# Rodinná tabule pro nástěnný iPad

Domácí informační panel pro iPad na zdi vedle TapHome. Program rodiny z několika
Google kalendářů, počasí, svozy popelnic a nákupní seznam z Apple Poznámek.

- **žádný hardware** — běží v Safari na iPadu
- **žádné předplatné** — Apps Script, GitHub Pages i Open-Meteo jsou pro tenhle objem zdarma
- **žádný server doma** — nic neběží 24/7 kromě iPadu samotného

```
index.html              celá tabule, jeden soubor bez závislostí
apps-script/Code.gs     datové API (kalendáře + seznamy) běžící u Googlu
tools/gen-svoz.py       generátor .ics z harmonogramu svozu odpadů
```

Harmonogram svozu konkrétní obce a vygenerovaný `.ics` jsou v `.gitignore` —
prozrazovaly by bydliště, tak zůstávají jen na disku.

Bez nastavení běží tabule na **ukázkových datech** — otevři `index.html` a hned
uvidíš, jak bude vypadat.

> **Zprovozňuješ to poprvé?** Jdi na **[NAVOD.md](NAVOD.md)** — odškrtávací
> seznam krok za krokem, včetně toho, co se dělá na počítači a co na iPadu.
> Tenhle README je referenční popis, ne postup.

## Jak to drží pohromadě

```
Google Kalendář ─┐
                 ├─→ Apps Script ─→ tabule v Safari na iPadu
Apple Poznámky ──┘        ↑
   (iOS Zkratka)          └── Open-Meteo (počasí, přímo z prohlížeče)
```

Kalendář čte Apps Script sám. Apple Poznámky nemají žádné API, takže je na iPadu
přečte iOS Zkratka a pošle do Apps Scriptu — detaily v části *Seznamy*.

## Co se dělá kde

Nezkoušej všechno na tabletu. Tři z těch kroků na něm nejdou vůbec.

| Krok | Kde | Proč tam |
|---|---|---|
| Nasadit Apps Script | **počítač** | editor Apps Scriptu je plnohodnotné IDE, na iPadu je to trápení |
| Vytvořit kalendář „Svozy" | **počítač** | Google Kalendář to v mobilní aplikaci **neumožňuje** |
| Naimportovat `.ics` | **počítač** | import souboru je v Google Kalendáři jen na webu |
| Nasdílet kalendář (i manželka) | **počítač** | sdílení v mobilní aplikaci **není**, jen na webu |
| Vyplnit URL a token v tabuli | **iPad** | nastavení se drží v localStorage toho konkrétního iPadu |
| Zkratka „Tabule sync" | **iPad** | musí běžet na zařízení, které visí na zdi |

Na mobilu jde použít prohlížeč v režimu „Vyžádat web pro počítače", ale
proklikat v tom sdílení kalendáře je otrava — manželce to zaber pět minut
u počítače, je to jednorázová věc.

---

## 1. Účet tabule

Apps Script čte kalendáře pod účtem, ve kterém běží. Zřiď na to **samostatný
Google účet** používaný výhradně pro tabuli.

Není to formalita. Ten účet dostane právo číst manželčin kalendář, tedy včetně
toho, kde jsou v kolik hodin děti. Účet, který nikde jinde nepoužíváš, vidí jen
to, co jste mu vědomě nasdíleli — zatímco tvůj osobní účet by měl skriptu
otevřený i pracovní kalendář, a účet přihlášený na televizi nebo jiném společném
zařízení má tolik uživatelů, kolik lidí dosáhne na dálkové ovládání.

Praktické k tomu:

- Účet nepoužívej nikde jinde — žádná televize, žádná herní konzole
- Dej mu silné unikátní heslo a zapni dvoufázové ověření
- Na `script.google.com` se do něj hlas v odděleném profilu prohlížeče nebo
  v anonymním okně, ať si ho nemícháš se svým hlavním účtem

## 2. Kalendáře

Vodicí pravidlo: **čti tam, kde data už jsou.** Kdyby měl někdo zapisovat kroužky
do nově vytvořeného kalendáře, vydrží to čtrnáct dní. Čte se proto přímo
manželčin osobní kalendář a nikdo nemusí měnit zvyk.

| Kalendář | Vlastní | Nasdílí komu | Proč |
|---|---|---|---|
| Osobní manželky | manželka | účtu tabule, **Zobrazit všechny podrobnosti události** | zdroj „kdo/kdy/kde", bez změny jejího zvyku |
| „Svozy" | **ty** | účtu tabule i manželce | popelnice; vlastníš ho ty, aby ti chodila upozornění na telefon |
| „Rodina" (volitelně) | účet tabule | oběma, *Provádět změny* | výlety a věci, co nepatří nikomu |

Po nasdílení musíš v účtu tabule **kliknout na odkaz v e-mailu s pozvánkou**,
jinak se kalendář nepřidá do jeho seznamu a `vypisKalendare` ho neukáže.

Právo *Zobrazit informace o volném čase* nestačí — tabule by zobrazila, že
manželka něco má, ale ne co, a „kdo/kdy/kde" tím padá.

### Tvůj osobní kalendář na tabuli nepatří

`CONFIG.CALENDARS` ho neobsahuje a účet tabule na něj ani nemá přístup. Pracovní
schůzky na kuchyňskou zeď nepatří a u některých profesí by názvy událostí neměly
být vidět vůbec.

Když chceš, aby rodina viděla jen některé tvoje věci (dovolená, školení,
služebka), založ si kalendář „Já – rodina", zapisuj do něj jen to, co mají
vědět, a nasdílej ho účtu tabule. Tvůj hlavní kalendář zůstane mimo.

### Kdo dostane upozornění na popelnice

Tohle je past, na kterou se snadno narazí: upozornění v `.ics` platí pro
**vlastníka** kalendáře. Kdyby svozy ležely v kalendáři účtu tabule, nikomu
nezazvoní telefon, protože ten účet žádný telefon nemá.

Proto kalendář „Svozy" vlastníš ty a `.ics` importuješ k sobě — ty dostaneš
upozornění a účet tabule i manželka to mají nasdílené na čtení. Google
u cizích kalendářů vlastní upozornění nastavit nedovolí, takže když chce
upozornění na telefon i manželka, musí si `.ics` naimportovat taky k sobě.
Stejný soubor jde naimportovat vícekrát do různých kalendářů bez konfliktu.

### Zápis z mobilu

Aplikace **Google Kalendář** na iPhonu umožní při vytváření události přepnout
cílový kalendář. Nativní iOS Kalendář to umí taky, ale musí mít Google účty
přidané v *Nastavení → Aplikace → Kalendář → Účty*.

Manželka nemusí přepínat nic — píše si do svého kalendáře jako dosud.

## 3. Datové API (Apps Script)

0. Přihlas se do **účtu tabule** (viz část 1), ne do svého osobního.
1. [script.google.com](https://script.google.com) → **Nový projekt**, obsah
   `apps-script/Code.gs` vlož do editoru (přepiš `Code.gs`, který tam je).
2. Vygeneruj token:
   ```bash
   openssl rand -hex 24
   ```
3. Spusť funkci **`vypisKalendare`** (▷ Spustit). Poprvé bude chtít oprávnění
   ke kalendáři účtu tabule — potvrď. V *Protokolu* pak najdeš ID kalendářů,
   které tomu účtu někdo nasdílel.
4. Vyplň v `CONFIG` `TOKEN`, `CALENDARS` (ID, jméno, barva) a `WRITE_CALENDAR`.

   `WRITE_CALENDAR` je kalendář, do kterého smí tabule zakládat události přímo
   z panelu. Musí to být kalendář, kde má účet tabule právo **měnit** události
   — tedy ten, který si sám vytvořil. Do manželčina kalendáře zapisovat nemůže,
   tam má jen čtení, a je to tak správně. Dej sem stejné ID jako v `CALENDARS`,
   ať je nová událost hned vidět. Prázdná hodnota vkládání vypne.

   Zkontroluj si taky **časovou zónu projektu** (*Nastavení projektu →
   Časové pásmo* = `Europe/Prague`). Skládají se v ní časy nových událostí,
   takže při špatné zóně by ti poskočily.
5. Zkontroluj funkcemi **`testApi`** (kalendář) a **`testPost`** (parsování
   seznamu z poznámky), že se v Protokolu objeví rozumný výstup.
6. **Nasadit → Nová implementace** → Typ **Webová aplikace**:
   - *Spustit jako:* **Já**
   - *Kdo má přístup:* **Kdokoli**
7. Zkopíruj URL končící `/exec`.

> Po každé úpravě skriptu musíš nasadit **novou verzi** — `/exec` jinak dál běží
> na staré. Tohle je zdaleka nejčastější důvod, proč „to přestalo fungovat".
>
> URL s tokenem je klíč k datům i k zápisu seznamů. Skript vrací jen název, čas
> a místo události. Kdyby URL unikla, vygeneruj nový token a nasaď znovu.

## 4. Hosting stránky

Stránka musí být na HTTPS adrese, aby ji šlo na iPadu přidat na plochu.
Obě varianty jsou zdarma:

**GitHub Pages**
```bash
cd ~/Sites/rodinny-dashboard
git init && git add . && git commit -m "rodinna tabule"
gh repo create rodinna-tabule --public --source=. --push
```
Pak *Settings → Pages → Source: main / root*.

> Na free plánu musí být repo veřejné. Nic tajného v souborech není — token,
> souřadnice i názvy se zadávají až v UI na iPadu a drží se v jeho localStorage.

**Cloudflare Pages** — na [pages.cloudflare.com](https://pages.cloudflare.com)
lze složku jen přetáhnout, bez gitu.

## 5. iPad

1. Nastav `/exec` URL, token a místo. Dvě cesty:

   **Přes adresu (snazší)** — na počítači si postav odkaz a pošli si ho
   AirDropem nebo Univerzální schránkou:
   ```
   https://<uzivatel>.github.io/rodinna-tabule/?api=https://script.google.com/macros/s/XXXX/exec&token=TVUJ_TOKEN&place=<tvoje-obec>
   ```
   Tabule parametry uloží a **hned query z adresy smaže**, takže token
   nezůstane v adresním řádku, v historii ani v záložce na ploše. Souřadnice
   si k názvu místa dopočítá sama. Podporované parametry: `api`, `token`,
   `place`, `days`, `family`, `shortcut`, `taphome` a `reset=1`.

   **Ručně** — v Safari otevři adresu tabule, jdi na **Nastavení**, vyplň
   pole a ulož. Token opisovat na tabletu ale nedoporučuju.
2. **Sdílet → Přidat na plochu** → jméno „Tabule". Ikona z plochy se otevře
   na celou obrazovku bez lišty Safari.
3. **Nastavení → Displej a jasnost → Automatický zámek → Nikdy.**
4. Noční ztmavení: aplikace **Zkratky** → *Automatizace* → *Denní čas* → 22:00
   → akce **Nastavit jasnost** na 10 %, druhá automatizace na 7:00 zpět.
   Zapni *Spustit okamžitě* bez ptaní.
5. Vedle TapHome: potáhni prstem od spodní hrany, drž, a přetáhni druhou
   aplikaci do **Split View**. iPad 10 Split View umí (Stage Manager ne — ten
   vyžaduje M1). Rozdělení si iPad pamatuje.
6. Zámek na jednu aplikaci: *Nastavení → Zpřístupnění → Asistovaný přístup*,
   pak trojklik bočního tlačítka. Ve Split View to nefunguje — vyber si buď
   zámek, nebo přepínání.

Kalendář se obnovuje každých 5 minut, počasí každých 15. Při výpadku wifi
zůstanou zobrazená poslední data a v hlavičce naskočí žlutý štítek.

## 6. Seznamy z Apple Poznámek

Apple Poznámky **nemají veřejné API** — z webové stránky se přečíst nedají.
Řešení proto obchází ten problém přes iPad: **iOS Zkratka** na iPadu poznámky
přečte a pošle do Apps Scriptu, odkud si je tabule vyzvedne.

Manželka tím nemění nic — dál používá Poznámky a dál je to sdílená poznámka
v iCloudu. Tabule je jen zobrazuje, odškrtává se v Poznámkách.

### Příprava poznámek

V Poznámkách vytvoř (nebo použij existující) poznámky pojmenované **Nákup**
a **Úkoly**, případně **Vzkaz** na rodinnou zprávu. Nasdílej je manželce
běžnou spoluprací v iCloudu. Jedna položka na řádek.

Skript pozná odškrtnuté položky podle běžných zápisů na začátku řádku:
`✓`, `✔`, `☑`, `[x]`, `x ` nebo `--`. Odrážky a pomlčky odstraní.

### Zkratka „Tabule sync"

Na **iPadu** v aplikaci Zkratky vytvoř zkratku s názvem `Tabule sync`:

1. **Najít poznámky** — filtr *Název* je `Nákup`, limit 1
2. **Získat podrobnosti poznámky** — vlastnost *Text* → ulož jako proměnnou `nakup`
3. Body 1–2 zopakuj pro `Úkoly` → proměnná `ukoly` a případně `Vzkaz` → `vzkaz`
4. **Získat obsah adresy URL** na tvou `/exec` adresu:
   - Metoda: **POST**
   - Tělo požadavku: **JSON**
   - Pole: `token` = tvůj token, `shopping` = `nakup`, `tasks` = `ukoly`,
     `note` = `vzkaz`

Názvy akcí se mezi verzemi iPadOS mírně liší, ale vždycky existuje akce, která
najde poznámku, a akce, která z ní vytáhne text. Zkratku spusť ručně — v odpovědi
musí přijít `{"ok":true,...}`.

Kdyby POST s JSON tělem neprošel (Apps Script občas při přesměrování zahodí
tělo), přepni *Tělo požadavku* na **Formulář** se stejnými poli. Backend přijímá
oba formáty.

### Spouštění

- **Ručně**: tlačítko *Synchronizovat* v tabuli — spustí Zkratku na iPadu
  a po chvíli si vyzvedne nová data. Název Zkratky se zadává v Nastavení.
- **Automaticky**: Zkratky → *Automatizace* → *Denní čas*, se zapnutým
  *Spustit okamžitě*. Jedna automatizace = jeden čas denně, takže si nastav
  několik (7:00, 12:00, 16:00, 19:00). Před nákupem stejně zmáčkneš tlačítko.

### Alternativa: Poznámky pod Google účtem

Existuje i cesta bez Zkratky. V *Nastavení → Aplikace → Mail → Účty* jde
u Google účtu zapnout **Poznámky**; poznámky vytvořené pod tím účtem se ukládají
do složky v Gmailu, odkud je Apps Script přečte přímo a tabule je má vždy živé.

Nedoporučuju to ale: poznámky pod Google účtem **nepodporují sdílení**
v iCloudu, takže byste oba museli mít v telefonu ten samý Google účet
a psát do jeho složky. To už je změna zvyku, které se chceme vyhnout.

## 7. Svoz odpadu

Obce vydávají harmonogram jako PDF s barevným kalendářem, což se do Google
Kalendáře nedá nacvakat rozumně — bio bývá v zimě nepravidelné a směsný jede
na sudé týdny. Generátor proto vezme opsané termíny a vyrobí `.ics` k importu:

```bash
python3 tools/gen-svoz.py tools/svoz-data-moje-obec-2026.json svozy-2026.ics
```

Formát datového souboru je popsaný v hlavičce `tools/gen-svoz.py`. Deklaruje se
v něm u každého svozu den v týdnu a volitelně pravidlo (sudý ISO týden, týdenní
řada bez mezer), a skript pak **ověří, že opsané termíny pravidlu odpovídají**.
Když ne, spadne a vypíše které — lepší chyba při generování než tichý špatný
termín na zdi.

Datový soubor i výsledný `.ics` jsou v `.gitignore`, protože harmonogram
identifikuje obec.

**Import**: Google Kalendář → *Nastavení* → *Importovat a exportovat* →
*Importovat* → vybrat soubor → jako cílový kalendář zvolit **Rodina**.
Importuj do sdíleného kalendáře, ne do osobního — jinak to manželka neuvidí.

Události mají upozornění 6 hodin před začátkem (tedy 18:00 předchozího dne)
a jsou označené jako *transparentní*, takže v kalendáři nedělají
„zaneprázdněn".

Tabule z nich staví samostatnou dlaždici s nejbližším svozem — pozná je podle
slov *bio*, *papír*, *plast*, *směsný*, *komunál* nebo *popelnice* v názvu —
a den předem ji zežloutí.

## 8. Zdroj počasí

[Open-Meteo](https://open-meteo.com) — bez API klíče, bez registrace. Pro Česko
skládá předpověď z modelů DWD **ICON-D2** (2,2 km, nejbližší hodiny) a ICON-EU
(7 km) na delší horizont. Data jsou pod licencí CC-BY 4.0, free tier je pro
nekomerční použití s limitem 10 000 dotazů denně. Tabule se ptá 4× za hodinu,
tedy ~100 dotazů denně — vejdeme se s velkou rezervou.

Místo se zadává názvem a souřadnice dopočítá geokódovací API Open-Meteo.

## 9. TapHome

TapHome **nemá webové GUI**, takže se ovládání domu nedá vložit do stránky jako
iframe. Co jde:

**Ovládání zůstává v aplikaci** (doporučeno) — tabule a TapHome vedle sebe
ve Split View, případně TapHome ve Slide Over, aby se dal vytáhnout od hrany.

**Proklik do aplikace** tlačítkem *TapHome* v liště funguje, ale ne přes URL
schéma — TapHome žádné zdokumentované nemá. Jde to přes Zkratky, což je
spolehlivější, protože akce **Otevřít aplikaci** umí spustit jakoukoli
nainstalovanou aplikaci bez ohledu na schémata:

1. Zkratky → **+** → název `Otevri TapHome`
2. Jediná akce: **Otevřít aplikaci** → vyber **TapHome**
3. V *Nastavení* tabule napiš do pole *Název Zkratky nebo odkaz* text
   `Otevri TapHome`

Tlačítko pozná, co jsi zadal: text s `://` otevře jako odkaz (kdybys někdy
ověřené schéma měl), cokoli jiného spustí jako Zkratku.

Počítej s tím, že se tím z tabule odskočí do TapHome a zpátky se vracíš ručně.
Na skutečné ovládání je Split View pořád lepší — vidíš oboje současně.

**Read-only dlaždice** — teploty v pokojích, spotřeba, stav stínění a garáže.
TapHome má cloudové API na `https://api.taphome.com/api/CloudApi/v1/`
(`getAllDevicesValues`, `getMultipleDevicesValues`) s hlavičkou
`Authorization: TapHome {token}`. Token se vyrábí v *Nastavení → Expose devices
→ TapHome API*.

Musí to jít přes Apps Script jako proxy ze dvou důvodů: API neposílá CORS
hlavičky, takže prohlížeč přímý dotaz odmítne, a token by jinak byl v kódu
stránky čitelný pro kohokoli. Lokální API (`http://<ip-core>/…`) je z HTTPS
stránky nepoužitelné — Safari to zablokuje jako mixed content. Proxy proto míří
na cloud a odpovědi cachuje (API vrací 503 při dotazech častěji než každých
500 ms).

**Ovládání z tabule** — technicky `POST setDeviceValue` přes stejnou proxy.
Smysl to má jen pro pár scén („Odejít", „Dobrou noc") s whitelistem povolených
zařízení v proxy. Přes Google to má odezvu okolo sekundy, takže na stmívání
nebo dojezd žaluzií se to nehodí.

## 10. Baterie

iPad trvale v nabíječce necykluje baterii, což je pro životnost lepší než
opakované vybíjení — ale drží ji na 100 % a při teple to urychluje degradaci.
Praktická opatření: nezavírat iPad do neventilovaného boxu, snížit jasnost,
a počítat s tím, že baterie po pár letech nafoukne. Pro panel na zdi to není
zásadní problém, jen ho nedávej za nábytek, kde by se hřál.

## Co dál stojí za zvážení

- **Narozeniny** — Google umí automatický kalendář z kontaktů, stačí přidat
  do `CONFIG.CALENDARS`
- **Jmeniny** — veřejné API doplněné do Apps Scriptu
- **Školní jídelníček** — když škola používá Strava.cz nebo podobné, jde
  vytáhnout přes Apps Script
- **Pyl a kvalita vzduchu** — Open-Meteo má Air Quality API, taky bez klíče
- **MHD odjezdy** — PID Golemio API, zdarma, ale vyžaduje registraci klíče
- **Home Assistant** — až bude doma něco běžet 24/7. Komunitní integrace
  [martindybal/taphome-homeassistant](https://github.com/martindybal/taphome-homeassistant)
  dostane přes TapHome API celý dům do jednoho dashboardu s kalendářem,
  takže by padla potřeba Split View.
