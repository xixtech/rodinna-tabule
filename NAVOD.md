# Návod krok za krokem

Odškrtávací seznam pro první zprovoznění. Drž se pořadí — sdílení kalendářů
musí být přijaté **dřív**, než Apps Script začne hledat jejich ID.

Co si připrav předem:

- adresu **účtu tabule** (samostatný Google účet jen pro tohle)
- adresu **manželčina** Google účtu
- vygenerovaný `.ics` se svozy (viz [README](README.md), část *Svoz odpadu*)
- počítač; iPad až od fáze E

---

## Fáze A — počítač, tvůj Google účet

**A1. Vygeneruj token.** V Terminálu:

```bash
openssl rand -hex 24
```

Výsledek si zkopíruj do poznámkového bloku, budeš ho potřebovat třikrát.

**A2. Vytvoř kalendář „Svozy".**
[calendar.google.com](https://calendar.google.com) → v levém panelu
*Jiné kalendáře* → **+** → *Vytvořit nový kalendář* → Název `Svozy` →
**Vytvořit kalendář**.

> V mobilní aplikaci Google Kalendář to nejde. Musí to být web na počítači.

**A3. Naimportuj svozy.**
Ozubené kolo vpravo nahoře → *Nastavení* → v levém menu
*Importovat a exportovat* → *Importovat* → **Vybrat soubor** → tvůj `.ics` →
*Přidat do kalendáře* nastav na **Svozy** → **Importovat**.

Musí to napsat, že naimportovalo 78 událostí.

**A4. Nasdílej „Svozy" účtu tabule.**
V *Nastavení* klikni v levém menu na **Svozy** → *Sdílet s konkrétními lidmi
a skupinami* → **Přidat lidi** → adresa účtu tabule → oprávnění
**Zobrazit všechny podrobnosti události** → **Odeslat**.

**A5. Nasdílej „Svozy" manželce.** Stejným postupem na její adresu.

> Upozornění na popelnice dostaneš **jen ty**, protože kalendář vlastníš ty.
> Když je chce i manželka, musí si stejný `.ics` naimportovat k sobě (A3
> u sebe). Google u cizích kalendářů vlastní upozornění nastavit nedovolí.

---

## Fáze B — počítač, manželka

**B1. Nasdílí svůj kalendář účtu tabule.**
Ve svém Google účtu: [calendar.google.com](https://calendar.google.com) →
*Nastavení* → v levém menu klikne na **svůj kalendář** (ten se svým jménem) →
*Sdílet s konkrétními lidmi a skupinami* → **Přidat lidi** → adresa účtu
tabule → oprávnění **Zobrazit všechny podrobnosti události** → **Odeslat**.

To je celé. Nic dalšího nikdy dělat nemusí a do žádného jiného kalendáře
nepřepisuje — píše si dál k sobě jako dosud.

> Oprávnění *Zobrazit informace o volném čase* **nestačí**, tabule by
> zobrazila jen že něco má, ale ne co.
>
> V mobilní aplikaci se sdílet nedá. Pět minut u počítače, jednorázově.

---

## Fáze C — počítač, účet tabule

Otevři si **anonymní okno** nebo jiný profil prohlížeče, ať si účty nemícháš.

**C1. Přihlas se do účtu tabule.**

**C2. Přijmi obě pozvánky ke sdílení.** Otevři [Gmail](https://mail.google.com)
toho účtu. Budou tam dva e-maily o nasdíleném kalendáři (od tebe a od
manželky). U každého klikni na odkaz, který kalendář přidá.

> Bez tohoto kroku kalendáře v účtu tabule neexistují a krok C4 je neukáže.
> Tady se to nejčastěji zasekne.

**C3. Založ projekt Apps Scriptu.**
[script.google.com](https://script.google.com) → **Nový projekt**.
Smaž, co je v editoru, a vlož celý obsah
[`apps-script/Code.gs`](apps-script/Code.gs). Ulož (⌘S).

**C4. Zjisti ID kalendářů.**
V liště nad editorem vyber funkci **`vypisKalendare`** → **▷ Spustit**.
Poprvé se zeptá na oprávnění: *Zkontrolovat oprávnění* → vyber účet tabule →
*Rozšířené* → *Přejít na … (nebezpečné)* → **Povolit**.

> To varování je normální. Znamená jen, že skript není ověřený Googlem,
> protože je tvůj vlastní.

Dole se otevře **Protokol provádění** a v něm budou řádky
`Název kalendáře -> nejake@id`. Zkopíruj si ID manželčina kalendáře
a kalendáře „Svozy".

**C5. Vyplň konfiguraci.** V editoru nahoře v `CONFIG`:

```js
TOKEN: 'sem-token-z-kroku-A1',

CALENDARS: [
  { id: 'adresa.manzelky@gmail.com', label: 'Žena',  color: '#ff8c9b' },
  { id: 'id-kalendare-svozy',        label: 'Svozy', color: '#7be0a8' }
],

WRITE_CALENDAR: '',
```

`label` je text, který se ukáže na štítku u události na zdi.

`WRITE_CALENDAR` nechej **prázdné**, pokud nechceš zakládat události přímo
z tabule. Když chceš, potřebuješ na to kalendář, kde má účet tabule právo
*měnit* události — do manželčina zapisovat nesmí, tam má jen čtení. Vytvoř si
tedy v účtu tabule kalendář `Rodina` (*Jiné kalendáře → + → Vytvořit nový
kalendář*), přidej ho do `CALENDARS` a jeho ID dej i do `WRITE_CALENDAR`.

Ulož (⌘S).

**C5b. Zkontroluj časovou zónu.** Vlevo *Nastavení projektu* (ozubené kolo) →
*Časové pásmo* musí být **(GMT+01:00) Praha**. V téhle zóně se skládají časy
nových událostí; při špatné by ti poskočily o hodiny.

**C6. Vyzkoušej, že data tečou.**
Vyber funkci **`testApi`** → **▷ Spustit**. V Protokolu musí být JSON, ve
kterém poznáš názvy skutečných událostí. Když je `events` prázdné, něco chybí
v C2 nebo C4.

**C7. Nasaď to jako webovou aplikaci.**
Vpravo nahoře **Nasadit** → *Nová implementace* → ozubené kolo u *Vybrat typ*
→ **Webová aplikace**:

| Pole | Hodnota |
|---|---|
| Popis | cokoli, třeba `v1` |
| Spustit jako | **Já** |
| Kdo má přístup | **Kdokoli** |

**Nasadit** → zkopíruj **URL webové aplikace**, končí na `/exec`.

> Po každé pozdější úpravě skriptu musíš nasadit **novou verzi**
> (*Nasadit → Spravovat implementace → ✏️ → Verze: Nová verze*), jinak
> `/exec` běží dál na staré. Tohle je nejčastější důvod, proč „to najednou
> přestalo".

---

## Fáze D — počítač, přenos na iPad

**D1. Postav si odkaz.** Do poznámkového bloku slož:

```
https://<uzivatel>.github.io/rodinna-tabule/?api=<EXEC_URL>&token=<TOKEN>&place=<OBEC>
```

Za `<EXEC_URL>` dej celou adresu z C7, za `<TOKEN>` token z A1, za `<OBEC>`
název své obce.

**D2. Pošli si ho na iPad.** AirDropem, Univerzální schránkou nebo si ho
pošli do Zpráv sám sobě.

---

## Fáze E — iPad

**E1. Otevři odkaz v Safari.** Dole vyskočí **„Nastavení převzato z adresy"**
a v hlavičce zmizí žlutý štítek *ukázková data*. Objeví se skutečné události.

Adresa se sama zkrátí, token v ní nezůstane.

**E2. Přidej na plochu.** **Sdílet** → *Přidat na plochu* → název `Tabule`.
Od teď spouštěj tabuli jen touhle ikonou, otevře se bez lišty Safari.

**E3. Vypni uspávání.** *Nastavení → Displej a jasnost → Automatický zámek →
**Nikdy***.

**E4. Připrav poznámky.** V aplikaci **Poznámky** vytvoř složku `Tabule`
a v ní dvě poznámky: `Nákup` a `Úkoly`. Obě nasdílej manželce
(otevřít poznámku → ikona spolupráce vpravo nahoře → *Přidat lidi*).

Jedna položka na řádek. Odškrtnuté pozná tabule podle `✓`, `[x]`, `x ` nebo
`--` na začátku řádku.

**E5. Vytvoř Zkratku.** Aplikace **Zkratky** → **+** → název `Tabule sync`.
Přidej akce v tomhle pořadí:

1. **Najít poznámky** — *Složka* je `Tabule`, *Název* je `Nákup`, Limit `1`
2. **Získat podrobnosti poznámky** — vlastnost **Text**, výsledek ulož jako
   proměnnou `nakup`
3. Znovu **Najít poznámky** pro `Úkoly` + **Získat podrobnosti** → `ukoly`
4. **Získat obsah adresy URL** — adresa je tvá `/exec`, *Metoda* **POST**,
   *Tělo požadavku* **JSON**, a tři pole:

   | Klíč | Hodnota |
   |---|---|
   | `token` | tvůj token |
   | `shopping` | proměnná `nakup` |
   | `tasks` | proměnná `ukoly` |

> Krok 2 nepřeskakuj. Kdybys proměnnou z *Najít poznámky* vložil do JSON
> přímo, pošle se **název** poznámky místo obsahu a na tabuli se objeví jediná
> položka „Nákup".

**E6. Spusť Zkratku ručně.** Povol přístup k Poznámkám i odeslání dat.
Musí přijít `{"ok":true,"stored":[...]}`.

- `unauthorized` → nesedí token
- nepřijde nic → v akci přepni *Tělo požadavku* z **JSON** na **Formulář**

V nastavení Zkratky ještě vypni *Zeptat se před spuštěním*, jinak nepojedou
automatizace.

**E7. Ověř na tabuli.** V *Seznamech* se objeví položky a dole čas poslední
synchronizace.

**E8. Nastav automatické spouštění.** Zkratky → záložka **Automatizace** →
**+** → *Denní čas* → čas → *Spustit okamžitě* → akce **Spustit zkratku** →
`Tabule sync`. Zakládej po jedné pro 7:00, 12:00, 16:00 a 19:00.

> Jedna automatizace umí jen jeden čas denně, proto ta čtyři. A počítej
> s tím, že časové automatizace na iPadOS jsou „nejlepší snaha" — spolehlivá
> cesta je tlačítko **Synchronizovat** přímo na tabuli.

---

## Fáze F — kosmetika

**F1. Noční ztmavení.** Zkratky → *Automatizace* → *Denní čas* 22:00 →
*Spustit okamžitě* → akce **Nastavit jasnost** na `10 %`. Druhá automatizace
na 7:00 zpátky na `70 %`.

**F2. Vedle TapHome.** Otevři tabuli, potáhni prstem od spodní hrany a chvíli
podrž, pak z Docku přetáhni TapHome k pravé hraně → **Split View**. Dělicí
čáru si nastav a iPad si rozdělení pamatuje.

**F3. Tlačítko TapHome v liště.** TapHome nemá zdokumentované URL schéma, takže
proklik jde přes Zkratky — funguje spolehlivěji než hádat schémata:

1. Zkratky → **+** → název `Otevri TapHome`
2. Jediná akce: **Otevřít aplikaci** → vyber **TapHome**
3. V *Nastavení* tabule do pole *Název Zkratky nebo odkaz* napiš
   `Otevri TapHome`

Odskočí to z tabule do TapHome a zpátky se vracíš ručně, takže na skutečné
ovládání je Split View pořád lepší.

**F4. Zakládání událostí z tabule.** Tlačítko **+** v hlavičce *Programu* nebo
*Přidat událost* na stránce Kalendář otevře formulář: co, kdy (rychlé volby
dnes/zítra/další dva dny), trvání nebo celý den, a nepovinně kde. Ukládá se do
kalendáře z `WRITE_CALENDAR`. Když je prázdné, tlačítko to řekne.

**F3. Téma.** V *Nastavení* tabule je *Téma → Podle času* (světlé 7:00–19:00).
Když je panel v tmavé chodbě, přepni na *Tmavé*.

---

## Když něco nefunguje

| Příznak | Kde je problém |
|---|---|
| Žlutý štítek *ukázková data* | tabule nemá `/exec` URL — zopakuj D1 a E1 |
| *kalendář offline* | špatná `/exec` adresa, nebo skript není nasazený jako *Kdokoli* |
| Prázdný program, ale bez chyby | v `CALENDARS` jsou špatná ID, nebo nebyly přijaté pozvánky (C2) |
| Události jen od jednoho člověka | druhé sdílení nemá *Zobrazit všechny podrobnosti* |
| Změna ve skriptu se neprojevila | nenasadil jsi novou verzi (C7) |
| Seznamy prázdné | Zkratka neproběhla, nebo chybí *Získat podrobnosti* (E5, krok 2) |
| V seznamu jediná položka „Nákup" | přesně ta chyba z E5, kroku 2 |
| Popelnice bez upozornění na telefonu | `.ics` je v cizím kalendáři, naimportuj si ho k sobě (A3) |
| Nová událost se neuloží | `WRITE_CALENDAR` je prázdné, nebo v tom kalendáři nemá účet tabule právo měnit události |
| Nová událost je o hodiny posunutá | časová zóna projektu Apps Scriptu není Praha (C5b) |
