from pathlib import Path

APP = Path("src/App.jsx")

BROKEN_ID = 'kachelmannwetter-wetter-hd-radar-vorhersage-uvm-bf4d6762'
NEXT_ID = 'sign-in-to-your-account-4b374c63'

ARTICLE = '''  {
    "id": "kachelmannwetter-wetter-hd-radar-vorhersage-uvm-bf4d6762",
    "title": "Kako brati vremensko napoved brez panike",
    "excerpt": "Praktičen slovenski vodič za razumevanje vremenske napovedi, radarja in opozoril, da lažje načrtujemo dan brez nepotrebnega pretiravanja.",
    "seoDescription": "Slovenski vodnik za branje vremenske napovedi, radarja, verjetnosti padavin in vremenskih opozoril.",
    "content": `# Kako brati vremensko napoved brez panike

Vremenska napoved je koristna šele takrat, ko jo znamo pravilno prebrati. Ena ikona oblaka ali kaplje še ne pove dovolj. Za dobro odločitev je treba pogledati čas, lokacijo, verjetnost padavin, veter, radar in morebitna opozorila.

Ta članek je preprost vodič za vsakdanjo uporabo. Namenjen je ljudem, ki želijo vedeti, ali vzeti dežnik, prestaviti izlet, zaščititi opremo ali samo bolje razumeti, zakaj se vreme včasih spremeni hitreje, kot je kazala jutranja napoved.

## Napoved ni obljuba, ampak najboljša ocena

Vreme se računa iz meritev, modelov in izkušenj meteorologov. Zato napoved ni stoodstotna obljuba, ampak najboljša ocena glede na podatke, ki so na voljo v tistem trenutku.

Bolj kot je napoved oddaljena, več negotovosti ima. Napoved za danes ali jutri je običajno uporabnejša kot napoved za deset dni naprej. Dolgoročna napoved je lahko dobra za okvirno načrtovanje, ne pa za natančno odločitev o uri odhoda.

## Najprej poglej uro, ne samo simbola

Pogosta napaka je, da uporabnik pogleda samo ikono za cel dan. Če je prikazana kaplja, to še ne pomeni, da bo deževalo od jutra do večera. Dež je lahko napovedan samo za eno uro popoldne.

Zato je bolj smiselno pogledati urni pregled. Za izlet, trening ali vožnjo je ključna ura, ne splošna dnevna oznaka.

## Radar pokaže, kaj se dogaja zdaj

Radar je uporaben za kratkoročno odločanje. Pokaže, kje so padavine trenutno in v katero smer se približno premikajo. To je posebej koristno pri plohah, nevihtah in hitro spreminjajočem se vremenu.

Radar pa ni čarobna napoved za cel dan. Če padavinski pas nastaja na novo, ga radar pred nastankom ne more pokazati. Zato je najbolje kombinirati radar z napovedjo in opozorili.

## Verjetnost padavin ne pomeni količine dežja

Verjetnost padavin pove, kako verjetno je, da bodo padavine na določenem območju ali v določenem časovnem oknu. Ne pove pa nujno, koliko dežja bo padlo.

Visoka verjetnost lahko pomeni kratek naliv, nizka verjetnost pa ne izključuje lokalne plohe. Pri načrtovanju dogodkov na prostem je zato dobro pogledati še količino padavin in veter.

## Veter pogosto bolj vpliva na občutek kot temperatura

Temperatura 10 stopinj ni vedno enaka izkušnja. Če piha močan veter, je občutek lahko precej hladnejši. Poleti pa lahko veter pomaga, da vroč dan deluje znosnejši.

Za kolesarjenje, pohodništvo, delo na prostem in dogodke je veter pogosto enako pomemben kot temperatura. Pri sunkih vetra je smiselna dodatna previdnost.

## Opozorila jemlji resno, vendar mirno

Vremenska opozorila niso namenjena paniki. Namenjena so temu, da se ljudje pravočasno pripravijo. Pri močnem vetru pospravi lahke predmete z balkona. Pri nevihtah se izogibaj izpostavljenim območjem. Pri vročini prilagodi gibanje in vodo.

Najboljša reakcija ni strah, ampak dobra priprava. Vreme je lažje obvladovati, če ga spremljamo pravočasno.

## Za Slovenijo je pomemben tudi teren

Slovenija ima morje, Alpe, doline, planote in urbana območja na kratkih razdaljah. Zato je lahko vreme v Ljubljani drugačno kot na Gorenjskem, Primorskem ali v Prekmurju.

Pri izletih ne glej samo napovedi za domači kraj. Preveri cilj poti in območje, skozi katero potuješ.

## Praktično pravilo za vsak dan

Za vsakdanjo odločitev naredi tri korake: najprej poglej urni pregled, nato radar, nato še opozorila. Če se vsi trije podatki ujemajo, je odločitev precej lažja.

Če se podatki ne ujemajo, načrtuj z rezervo. Vzemi dežnik, premakni dejavnost za uro ali pripravi drugo možnost.

## Zaključek

Dobra vremenska napoved ni samo ikona sonca ali oblaka. Je kombinacija časa, kraja, radarja, verjetnosti, vetra in opozoril. Ko te podatke bereš skupaj, dobiš precej bolj realno sliko dneva.

Najboljši pristop je preprost: preveri več kot en podatek, ne pretiravaj s paniko in načrtuj z malo rezerve. Tako vreme postane uporabna informacija, ne vir zmede.`,
    "category": "Vodniki",
    "author": "Uredništvo Blog Lab",
    "status": "published",
    "heroImage": null,
    "video": null,
    "gallery": [],
    "sources": [],
    "createdAt": "2026-09-21T13:05:00+02:00",
    "updatedAt": "2026-09-21T13:05:00+02:00"
  },'''


def replace_article(text: str) -> str:
    marker = f'  {{\n    "id": "{BROKEN_ID}"'
    start = text.find(marker)
    if start < 0:
        raise SystemExit(f"Article id not found: {BROKEN_ID}")

    next_marker = f'\n\n  {{\n    "id": "{NEXT_ID}"'
    end = text.find(next_marker, start)
    if end < 0:
        raise SystemExit(f"Next article marker not found: {NEXT_ID}")

    return text[:start] + ARTICLE + text[end:]


def main() -> None:
    text = APP.read_text(encoding="utf-8")
    patched = replace_article(text)
    APP.write_text(patched, encoding="utf-8")


if __name__ == "__main__":
    main()
