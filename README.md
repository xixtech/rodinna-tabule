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
tools/najdi-zastavku.py kód zastávky PID podle jména
tools/nt-z-xlsx.py      časy spínání NT z exportu distributora
tools/mkicon.py         generátor ikony na plochu
apple-touch-icon.png    ikona pro Přidat na plochu
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

### Zpětný směr: přidávání z tabule do Poznámek

Web do iCloud poznámky zapsat nemůže, ale **iOS Zkratka ano**. Tabule jí předá
text adresou, kterou Apple dokumentuje:

```
shortcuts://run-shortcut?name=Tabule%20nákup&input=text&text=mléko
```

Zkratka `Tabule nákup` má **jedinou akci**: *Přidat do poznámky* → poznámka
`Nákup`, text = vstup Zkratky. Na konec jí přidej stejné *Získat obsah adresy
URL*, jaké má `Tabule sync` — tím poznámku hned pošle zpátky a tabule se
srovná sama. Totéž pro `Tabule úkol`. Názvy obou vyplň v *Nastavení* tabule.

Než se položka vrátí z Poznámek, drží ji tabule zobrazenou **čárkovaně
s „posílám…"**. Web nemá jak zjistit, že Zkratka doopravdy proběhla, takže
položka po deseti minutách bez potvrzení zmizí — to je pravda, ne chyba.
Porovnává se bez ohledu na diakritiku a velká písmena, takže „kefír" poslaný
z tabule a „Kefír" vrácený z Poznámek se nezdvojí.

### Odškrtávat z tabule nejde

A nepůjde. Zkratky umí do poznámky **jen připsat na konec** — přepsat obsah
existující poznámky neumožňují a `Create Note` by vyrobilo **novou** poznámku,
čímž by se rozbilo sdílení s manželkou.

Prakticky to ale nevadí: přidáváš v kuchyni u tabule, odškrtáváš v krámě
na telefonu, kde Poznámky máš. Ta polovina, která funguje, je ta potřebná.

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

Karta počasí ukazuje aktuální stav, dnešní rozsah teplot, vlhkost, UV
a **tlak s trendem za poslední tři hodiny**. Ta šipka je tam schválně —
klesající tlak je klasická předzvěst zhoršení a z teploty ani větru se
to nevyčte. Hourly u Open-Meteo obsahuje i uplynulé hodiny dneška, takže
se trend spočítá bez dalšího dotazu.

V *Nastavení* jde vyplnit i **druhé místo** — v kartě počasí se pak objeví
přepínač mezi oběma. Obě lokality se načtou jedním dotazem (Open-Meteo bere
souřadnice oddělené čárkou a vrací pole), takže to nic nezdrží ani nezdvojuje
počet dotazů.

## Školní rozvrh

Záložka **Rozvrh** ukazuje mřížku dnů a hodin, dnešní sloupec zvýrazněný.
Zadává se **textem, ne klikáním do mřížky** — mřížkový editor je na nástěnném
tabletu utrpení a rozvrh se mění dvakrát do roka:

```
# Adam
Po: Čj, M, Aj, Tv, Vv
Út: M, Čj, -, Hv
St: Aj, M, Čj

# Eva
Po: M, Čj
Pá: Tv, Vv, M
```

Řádek s `#` zakládá dítě — když jsou dvě a víc, objeví se nad rozvrhem
přepínač. Prázdnou hodinu napiš jako `-`. Zkratky dnů jsou tolerantní:
`Po`, `po`, `Út`, `Ut`, `úterý`, `Utery`, `ctvrtek` i `patek` fungují,
protože na klávesnici nikdo háčkovat nebude a mlčky přeskočený den by byl
horší než tolerantní parser.

Rozvrh se ukládá do localStorage iPadu, ne k Googlu — je to statická věc,
která nepotřebuje synchronizaci. Zálohu si udělej zkopírováním textu.

## Poznámky a jejich synchronizace

Záložka **Poznámky** má dva zdroje, přepínané nahoře. Je to schválně —
každý umí něco, co druhý ne, a spojit je do jednoho nejde.

### Tabule

Poznámky psané přímo na panelu. Ukládají se **u Googlu** ve Script Properties,
ne v prohlížeči — vyčištěné úložiště Safari by jinak smazalo i to, co si někdo
připsal. Jdou přidávat i mazat a objeví se na každém zařízení, které tabuli
zobrazuje.

Nesynchronizují se ale do Apple Poznámek. Do iCloud poznámky se z webové
stránky **zapsat nedá** — Apple na to nemá žádné API a žádná cesta neexistuje.

Strop je 40 poznámek po 500 znacích, protože jedna vlastnost Script Properties
má limit 9 kB a při překročení by zápis začal padat.

### Z Poznámek

Zrcadlo sdílené Apple poznámky, kterou do tabule posílá iOS Zkratka — stejný
mechanismus jako u nákupního seznamu. Manželka napíše řádek v Poznámkách na
telefonu, iCloud to rozešle a Zkratka to při dalším běhu předá tabuli.

Tady je to naopak: **synchronizuje se s Applem, ale na tabuli je to jen ke
čtení.** Přidávací pole i mazání se v tomhle režimu skryjí, protože by lhaly.

Do Zkratky přidej třetí poznámku (třeba `Nástěnka`) a její text pošli v poli
`note` — backend na to je připravený, viz část *Seznamy z Apple Poznámek*.

### Který zdroj kdy

| Chci | Zdroj |
|---|---|
| Psát z telefonu, aby to bylo na zdi | Z Poznámek |
| Psát na zdi a hned to vidět | Tabule |
| Mazat na zdi | Tabule |
| Aby to viděli všichni v Poznámkách | Z Poznámek |

## Nízký tarif (NT/VT)

V hlavičce přehledu svítí štítek, jestli běží **NT** nebo **VT** a jak dlouho
ještě — zeleně v nízkém tarifu, šedě ve vysokém. Klepnutím se otevře záložka
**Tarif** s celým týdnem: okna NT po dnech, dnešní den zvýrazněný, právě
běžící okno plnou zelenou, a hodiny NT za den i za týden.

### Odkud časy vzít

Distributor (ČEZ, EG.D, PRE) umí vyexportovat časy spínání jako xlsx —
řádek na den, sloupce po párech „NT Za" a „NT Vy". Převod na text pro tabuli:

```bash
python3 tools/nt-z-xlsx.py ~/Downloads/Časy_spínání_NT.xlsx
```

```
# a1b2dp01
Po-Pá: 02:00-06:00, 12:30-14:30, 22:00-24:00
So,Ne: 00:00-08:00, 13:00-17:00, 22:00-24:00
```

Dny se stejnými časy se slučují do rozsahů, aby šel výsledek zkontrolovat okem.
Na chybový výstup skript navíc vypíše kolik hodin NT to dělá za týden a za den
— když ti to nevyjde na tarif, který platíš, něco se opsalo špatně.

Skript čte xlsx bez `openpyxl` (je to zip s XML), takže nic instalovat nemusíš.

Text vlož na záložce **Tarif → Upravit**. Ukládá se do localStorage iPadu, ne
k Googlu — jsou to tvoje časy spínání a do repozitáře nepatří.

### Přechod přes půlnoc

Okna se **slučují, když se dotýkají**. Bez toho by rozvrh `22:00-24:00`
následovaný `00:00-08:00` hlásil ve 23:30 „ještě 30 min", i když NT plynule
pokračuje do rána. Sloučení se dělá napříč včerejškem, dneškem a zítřkem,
takže i po půlnoci tabule správně ví, že jsi pořád v okně, které začalo večer.

Konec okna v přesnou půlnoc se píše `24:00`, ne `0:00` — jinak by to vypadalo
jako okno nulové délky.

### Víc povelů

Export obvykle obsahuje víc povelů (různé okruhy — třeba tepelné čerpadlo
a bojler). Všechny se zobrazí jako přepínač na záložce Tarif. Který z nich
hlásí štítek v hlavičce, se nastavuje v *Nastavení → Který povel NT hlásí
hlavička*, obvykle první.

## Odjezdy PID

Záložka **Odjezdy** je odjezdová tabule pro jednu zastávku: linka, směr,
za kolik minut a v kolik. Odjezd do pěti minut zežloutne, zpoždění se ukáže
červeně, doplňkově ikony pro nízkopodlažnost a klimatizaci.

Data jsou z **Golemio API** — oficiální otevřené API Prahy pro PID.
Klíč je zdarma na [api.golemio.cz/api-keys](https://api.golemio.cz/api-keys/).

Jde to přes Apps Script jako proxy ze dvou důvodů: Golemio neposílá CORS
hlavičky, takže přímý dotaz ze stránky neprojde, a klíč nemá co dělat v kódu
stránky. Odpověď se cachuje 30 s, protože tabule se ptá častěji, než se data
mění, a klíč má omezený počet dotazů. Automatické obnovování běží **jen když
je záložka vidět** — jinak by tabule pálila dotazy celý den pro nic.

### Zastávka se zadává kódem, ne jménem

Golemio chce kód stanoviště podle číselníku ASW (`aswIds`), třeba `539_1` je
Národní třída. Jméno na kód přeloží přiložený skript z veřejného seznamu
zastávek na data.pid.cz:

```bash
python3 tools/najdi-zastavku.py "Národní třída"
```

```
Národní třída  (Praha, AB)
   aswIds=539_1      stanoviště A   pásmo P   linky: —
   aswIds=539_2      stanoviště B   pásmo P   linky: —
   aswIds=539_101    stanoviště M1  pásmo P   linky: B
   aswIds=539_102    stanoviště M2  pásmo P   linky: B
```

Seznam má 18 MB, proto se překlad dělá na počítači a do tabule jde hotový kód.
Skript si ho jednou stáhne a odloží zeštíhlený do `tools/.stops-cache.json`
(v `.gitignore`). Volitelně `--linka 22` ukáže jen zastávky s tou linkou,
`--vse` i částečné shody a `--obnovit` stáhne seznam znovu.

### Nastavení

V `CONFIG.PID` v Apps Scriptu:

```js
PID: {
  KEY: 'klíč z api.golemio.cz',
  ASW_IDS: '539_1,539_2',     // víc stanovišť oddělených čárkou
  LINES: ['22'],              // jen tyhle linky, prázdné = všechny
  LIMIT: 8,
  MINUTES_AFTER: 180
}
```

Popisek zastávky nad tabulí se vyplňuje v *Nastavení* tabule — je to jen text,
skutečné stanoviště určuje `ASW_IDS`.

Ověřit to jde funkcí **`testPid`**, která do Protokolu vypíše celou odpověď
i nápovědu, když něco chybí.

## Ikona na plochu

`apple-touch-icon.png` je to, co uvidíš na ploše iPadu po *Přidat na plochu*.
Bez ní by iOS použil zmenšený snímek stránky. Generuje ji `tools/mkicon.py`
čistým Pythonem bez závislostí — kdybys chtěl jinou barvu nebo motiv, uprav
konstanty `BG` a `FG` a spusť:

```bash
python3 tools/mkicon.py apple-touch-icon.png
```

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
