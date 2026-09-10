"use client";

import { useEffect, useMemo, useRef, useState } from "react";

const STORAGE_KEY = "blog-lab-articles-v1";
const CATEGORIES = ["Šport", "Politika", "Aktualno", "Novice", "Projekti", "Mnenja", "Vodniki", "Drugo"];

const starterArticles = [{
  id: "bepicolombo-zacel-prihod-k-merkurju",
  title: "BepiColombo začel prihod k Merkurju: prvi ključni korak je uspel",
  excerpt: "Po skoraj osmih letih potovanja se je od misije BepiColombo uspešno ločil pogonski modul. Dve znanstveni sondi zdaj nadaljujeta zahtevno sklepno pot proti Merkurju.",
  seoDescription: "BepiColombo je uspešno odvrgel pogonski modul in začel sklepno fazo prihoda k Merkurju. Kaj sledi evropski in japonski vesoljski misiji?",
  content: `# BepiColombo začel prihod k Merkurju: prvi ključni korak je uspel

Skupna evropsko-japonska misija BepiColombo je 3. septembra uspešno opravila prvi ključni korak sklepnega prihoda k Merkurju. Od sestavljene sonde se je ločil Mercury Transfer Module (MTM), pogonski modul, ki je plovilo od izstrelitve leta 2018 vodil skozi medplanetarni prostor. Evropska vesoljska agencija (ESA) je uspeh potrdila po sprejemu radijskih signalov prek anten v Španiji in Argentini.

Dogodek še ne pomeni, da je BepiColombo že v orbiti Merkurja. Misijo čaka več občutljivih manevrov, preden bosta njena evropska in japonska znanstvena orbiterja lahko začela raziskovanje planeta, ki je Soncu najbližje.

## Potrditev je na Zemljo potovala več minut

Ločitev se je zgodila več kot 200 milijonov kilometrov od Zemlje. Zaradi velike razdalje nadzorna ekipa ni mogla posegati v dogajanje v realnem času. Zaporedje ukazov je moralo biti pripravljeno vnaprej, inženirji pa so nato čakali na spremembo radijskega signala in telemetrijo plovila.

ESA je najprej zaznala Dopplerjev premik, ki je bil skladen z načrtovano spremembo hitrosti ob ločitvi. Poznejši sprejem signala z dveh postaj globokega vesolja je potrdil, da je bil MTM uspešno odvržen. Prvi podatki so pokazali tudi, da sistemi delujejo normalno in da sončne celice evropskega orbiterja polnijo baterije.

To je pomembna razlika med domnevo in potrjenim dejstvom: začetni signal je nakazoval pravilno izvedbo, popolna potrditev pa je prišla šele s telemetrijo. Pri tako oddaljeni misiji mora ekipa uspeh vsakega koraka preveriti, preden nadaljuje naslednjo fazo.

## Zakaj je prihod k Merkurju tako zahteven

Merkur je blizu Sonca, vendar to ne pomeni, da ga je preprosto doseči. Vesoljsko plovilo med potjo navznoter pridobiva hitrost zaradi Sončeve gravitacije, zato mora velik del energije porabiti za zaviranje. BepiColombo je zato uporabil električni pogon in devet preletov planetov, s katerimi je postopoma prilagajal hitrost in smer.

Misija je bila izstreljena 20. oktobra 2018. Na poti je enkrat obletela Zemljo, dvakrat Venero in šestkrat Merkur. Po več milijardah prepotovanih kilometrov je MTM svojo nalogo končal; za nadaljnje manevre bo odgovoren evropski Mercury Planetary Orbiter (MPO), na katerega je še vedno pritrjen japonski orbiter Mio.

Ekstremno okolje predstavlja dodatno težavo. Oprema mora prenašati močno Sončevo sevanje in velike temperaturne razlike, hkrati pa natančno delovati pri manevrih, ki jih zaradi komunikacijske zakasnitve ni mogoče sproti popravljati.

## Kaj sledi po uspešni ločitvi

Po trenutno objavljenem načrtu naj bi sestavljeno plovilo 21. novembra vstopilo v orbito Merkurja. Nato naj bi se evropski MPO in japonski Mio ločila 9. oziroma 10. decembra ter začela pot proti vsak svoji delovni orbiti. Redna znanstvena opazovanja so predvidena za april 2027.

Ti datumi so načrtovani prihodnji mejniki, ne že opravljeni dogodki. Pri vesoljskih misijah se lahko časovnica spremeni zaradi stanja plovila, navigacijskih meritev ali varnostnih odločitev nadzorne ekipe. Današnja potrditev pomeni le, da je prvi korak prihodne faze uspel in da je plovilo po njem v nominalnem stanju.

## Dva orbiterja, dva pogleda na isti planet

Evropski MPO bo preučeval površje, notranjo zgradbo in kemično sestavo Merkurja. Japonski Mio se bo osredotočil predvsem na magnetno polje planeta ter njegovo interakcijo s Sončevim vetrom. Sočasne meritve z različnih orbit bodo znanstvenikom omogočile povezovanje dogajanja na površju, v redki eksosferi in v magnetnem okolju.

Merkur ostaja eden slabše raziskanih planetov notranjega Osončja. Pred BepiColombom sta ga od blizu obiskali le Nasini misiji Mariner 10 in Messenger, pri čemer je bila Messenger prva sonda v njegovi orbiti. Nova misija naj bi zato izboljšala razumevanje planeta in ponudila širši vpogled v nastanek kamnitih planetov blizu zvezd.

Uspešna ločitev MTM je velik inženirski dosežek, vendar je najbolj občutljiv del prihoda še pred misijo. Pravi znanstveni izplen bo prišel šele po varni namestitvi obeh orbiterjev in preverjanju instrumentov. Današnji rezultat je pomemben predvsem zato, ker je BepiColombo po dolgem potovanju odprl vrata tej naslednji fazi.

## Viri

- ESA, sprotne uradne posodobitve prihoda misije BepiColombo, 3. september 2026: https://www.esa.int/Science_Exploration/Space_Science/BepiColombo/Latest_updates_BepiColombo_s_arrival_at_Mercury
- ESA, opis prihodne faze in časovnica, 27. avgust 2026: https://www.esa.int/Enabling_Support/Operations/Watch_live_BepiColombo_begins_its_arrival_at_Mercury
- Associated Press, poročilo o sklepni poti dveh sond proti Merkurju, 3. september 2026: https://apnews.com/article/8840475f5f873b9bcc7245f45ffdc50c
- ESA, pregled misije BepiColombo in znanstvenih ciljev: https://www.esa.int/Science_Exploration/Space_Science/BepiColombo`,
  category: "Aktualno",
  author: "Uredništvo Blog Lab",
  status: "published",
  createdAt: "2026-09-03T18:01:00.000Z",
  updatedAt: "2026-09-03T18:01:00.000Z"
}, {
  id: "dublin-proracun-eu-siritev-demokraticna-odpornost",
  title: "Dublin odpira tri velika vprašanja EU: proračun, širitev in demokratična odpornost",
  excerpt: "Evropski ministri so se v Dublinu zbrali na neformalnem zasedanju o proračunu EU za obdobje 2028–2034, širitvi in zaščiti demokratičnih sistemov.",
  seoDescription: "Ministri EU v Dublinu razpravljajo o proračunu 2028–2034, širitvi Unije in demokratični odpornosti. Pojasnjujemo dejstva in odprta vprašanja.",
  content: `# Dublin odpira tri velika vprašanja EU: proračun, širitev in demokratična odpornost

Ministri držav članic, pristojni za evropske zadeve, so se 3. septembra zbrali v Dublinu na dvodnevnem neformalnem zasedanju Sveta za splošne zadeve. Na dnevnem redu so naslednji dolgoročni proračun Evropske unije za obdobje 2028–2034, širitev EU ter krepitev demokratične odpornosti. Pogovor poteka pod irskim predsedovanjem Svetu EU.

Srečanje je politično pomembno, vendar samo po sebi ne prinaša zavezujočih odločitev. Neformalna ministrska zasedanja so namenjena izmenjavi stališč in pripravi kompromisov, medtem ko se pravni in proračunski sklepi sprejemajo po formalnih postopkih institucij EU.

## Dolgoročni proračun zahteva širok kompromis

Prvo osrednje vprašanje je večletni finančni okvir za leta 2028–2034. Gre za sedemletni načrt, ki določa zgornje meje porabe in razmerja med področji, kot so kohezija, kmetijstvo, raziskave, konkurenčnost, varnost ter zunanje delovanje Unije.

Irsko predsedstvo je napovedalo dve delovni razpravi o proračunu, pri eni pa sodelujejo tudi predstavniki Evropskega parlamenta. To je potrjeno dejstvo iz uradnega programa. Odprto ostaja, kako bodo države uskladile različne interese: neto plačnice praviloma poudarjajo nadzor skupne porabe, države z večjimi kohezijskimi in kmetijskimi potrebami pa opozarjajo na pomen stabilnega financiranja tradicionalnih politik.

Minister Thomas Byrne je dejal, da želi zasedanje približati dogovor, ki bi koristil državljanom in skupnostim v vseh članicah. To je cilj irskega predsedstva, ne že dosežen rezultat. Končni finančni okvir bo zahteval soglasje držav članic, Evropski parlament pa mora dati svojo odobritev.

## Širitev: politična podpora še ni članstvo

Drugi del razprav je namenjen širitvi. Ministrom članic se pridružujejo predstavniki držav kandidatk in potencialnih kandidatk. Takšna vključitev kaže, da je širitev visoko na političnem dnevnem redu, vendar ne pomeni avtomatičnega pospeška ali vnaprej določenega datuma članstva.

Vsaka kandidatka napreduje po svojem postopku in mora izpolniti pogoje na področjih pravne države, demokratičnih institucij, gospodarstva ter prevzema evropske zakonodaje. Države članice imajo pri ključnih korakih pomembno vlogo, zato lahko politična nesoglasja proces upočasnijo tudi takrat, ko obstaja splošna podpora širitvi.

Irsko predsedstvo širitev predstavlja kot strateško prednostno nalogo. To je politično stališče predsedujoče države. Dejstvo pa je, da je srečanje razpravljalno in da mora biti vsak naslednji formalni korak sprejet po pravilih pristopnega procesa.

## Demokratična odpornost sega od volitev do informacijskega prostora

Tretja tema je odpornost demokratičnih sistemov. Uradna napoved ne določa enega samega ukrepa, temveč odpira širši pogovor o tem, kako države in institucije zaščitijo demokratične procese pred tujim vmešavanjem, dezinformacijami, kibernetskimi napadi in padanjem zaupanja v institucije.

Pri tem obstaja občutljivo ravnotežje. Učinkovita zaščita volitev, javnih ustanov in medijskega prostora je legitimna naloga oblasti, vendar ukrepi ne smejo neupravičeno omejevati svobode izražanja ali politične konkurence. Zato bodo pomembni pravna jasnost, neodvisen nadzor in javno preverljivi razlogi za morebitne omejitve.

## Kaj lahko srečanje dejansko doseže

Najverjetnejši neposredni rezultat zasedanja ni nov zakon, temveč jasnejši pregled, kje med državami obstaja soglasje in kje bodo potrebna nadaljnja pogajanja. Pri proračunu bodo ključni obseg, prednostne naloge in morebitni novi viri prihodkov. Pri širitvi bo v ospredju povezava med geopolitično nujnostjo ter izpolnjevanjem pogojev. Pri demokratični odpornosti pa bo treba varnostne potrebe uskladiti s temeljnimi pravicami.

Dublinsko srečanje je zato najbolje razumeti kot pripravo političnega terena. Njegov pomen se ne bo meril po velikih napovedih prvega dne, ampak po tem, ali bodo razprave v naslednjih mesecih olajšale formalne dogovore med državami članicami, Evropsko komisijo in Evropskim parlamentom.

## Viri

- Irsko predsedstvo Sveta EU, napoved zasedanja in dnevni red, 3. september 2026: https://irish-presidency.consilium.europa.eu/en/news/minister-byrne-to-chair-eu-talks-in-dublin-on-eu-budget-and-enlargement/
- Irsko predsedstvo Sveta EU, uradna stran neformalnega zasedanja, 3.–4. september 2026: https://irish-presidency.consilium.europa.eu/en/events/informal-meeting-of-european-affairs-ministers-general-affairs-council/
- Svet Evropske unije, uradni koledar in opis zasedanja, 3.–4. september 2026: https://www.consilium.europa.eu/en/meetings/gac/2026/09/03-04/
- Reuters, ozadje pogajanj o naslednjem dolgoročnem proračunu EU, 19. junij 2026: https://www.reuters.com/business/eu-leaders-clash-over-blocs-next-7-year-budget-seek-new-revenue-sources-2026-06-19/`,
  category: "Politika",
  author: "Uredništvo Blog Lab",
  status: "published",
  createdAt: "2026-09-03T13:03:00.000Z",
  updatedAt: "2026-09-03T13:03:00.000Z"
}, {
  id: "tiafoe-v-tretjem-krogu-op-zda",
  title: "Tiafoe v tretjem krogu: ameriško upanje na OP ZDA ostaja živo",
  excerpt: "Frances Tiafoe je Japonca Reija Sakamota premagal s 6:3, 7:6 (2), 7:5. Zanesljiva zmaga ga pelje v tretji krog in ohranja ameriške upe na domači moški naslov.",
  seoDescription: "Frances Tiafoe je na OP ZDA 2026 premagal Reija Sakamota in napredoval v tretji krog. Analiza rezultata, igre in ameriškega lova na naslov.",
  content: `# Tiafoe v tretjem krogu: ameriško upanje na OP ZDA ostaja živo

Frances Tiafoe je v drugem krogu odprtega prvenstva ZDA premagal japonskega kvalifikanta Reija Sakamota s 6:3, 7:6 (2), 7:5. Osemindvajsetletni Američan je dvoboj na stadionu Louis Armstrong končal brez izgubljenega niza in si zagotovil mesto med najboljšimi 32 igralci turnirja.

Rezultat je za domače občinstvo pomemben tudi zaradi zgodovinskega ozadja. Ameriški tenisači čakajo na domačega zmagovalca moškega turnirja vse od leta 2003, ko je v New Yorku slavil Andy Roddick. Tiafoe, ki je na OP ZDA že dvakrat igral v polfinalu, sodi med igralce, od katerih navijači pričakujejo, da bi lahko dolgo čakanje končali.

## Hiter začetek je določil smer dvoboja

Tiafoe je Sakamotu odvzel servis že v prvi igri. Zgodnja prednost mu je omogočila, da je prvi niz vodil brez večjega tveganja in ga dobil s 6:3. Američan je igral bolj zbrano kot v uvodnem krogu, ko je za zmago proti Martinu Dammu potreboval pet nizov.

Drugi niz je bil precej tesnejši. Tiafoe je imel priložnost, da ga zaključi pred podaljšano igro, vendar sta zaporedni dvojni napaki Sakamotu odprli pot nazaj. Američan se je po tem zapletu hitro zbral. V podaljšani igri je dobil štiri od prvih petih točk in jo prepričljivo zaključil s 7:2.

Sakamoto tudi v tretjem nizu ni popustil. Dvajsetletni kvalifikant je z močnim začetnim udarcem ostajal v stiku ter na celotnem dvoboju dosegel 18 asov. Toda 40 neizsiljenih napak je bilo proti izkušenemu tekmecu preveliko breme. Tiafoe je zadnji niz dobil s 7:5 in dvoboj končal v treh nizih.

## Sakamotov nastop je vseeno pomemben

Poraz ne izniči uspešnega turnirja mladega Japonca. Sakamoto se je na glavni turnir prebil skozi kvalifikacije, v odločilnem kvalifikacijskem krogu premagal svojega vzornika Keija Nišikorija in nato dosegel svojo prvo zmago v glavnem delu OP ZDA. V prvem krogu je v petih nizih izločil Aleksandra Vukića.

Proti Tiafoeju je pokazal, da lahko z začetnim udarcem in napadalnim tenisom pritisne na uveljavljene igralce. Razlika se je pokazala predvsem pri nadzoru tveganja. Veliko število neizsiljenih napak mu je preprečilo, da bi močan servis pretvoril v osvojeni niz.

## Tiafoe je prihranil dragoceno energijo

Zmaga v treh nizih ima na dvotedenskem turnirju dodatno vrednost. Tiafoe je po napornem uvodnem dvoboju tokrat preživel manj časa na igrišču in se izognil novemu dolgemu obračunu. V nadaljevanju turnirja, ko se kakovost tekmecev praviloma povečuje, lahko takšen prihranek energije vpliva na regeneracijo in pripravo.

Američan ima z newyorškim občinstvom posebno povezavo. Njegova najboljša rezultata na turnirju sta polfinala, zato dobro pozna pritisk velikih večernih tekem. Tokrat je energijo tribun uporabil učinkovito: po težavah ob koncu drugega niza ni izgubil nadzora nad srečanjem.

## Domači naslov ostaja velik, a oddaljen cilj

Napredovanje v tretji krog še ni dokaz, da je Tiafoe pripravljen osvojiti turnir. Do naslova ga loči še pet zmag, v žrebu pa ostajajo številni najboljši igralci sveta. Njegova zmaga nad kvalifikantom je bila pričakovana, zato bo prava ocena forme mogoča šele proti zahtevnejšim tekmecem.

Kljub temu je opravil nalogo, ki je na turnirjih za grand slam ni mogoče jemati kot samoumevno. Po petih nizih v prvem krogu je izboljšal zbranost, v ključni podaljšani igri ostal miren in dvoboj zaključil, preden bi se Sakamoto lahko povsem vrnil. Ameriško upanje tako ostaja živo, zgodovinski cilj pa še naprej dovolj oddaljen, da zahteva previdnost pri napovedih.

## Viri

- Uradna stran OP ZDA, poročilo o dvoboju, 2. september 2026: https://www.usopen.org/en_US/news/articles/2026-09-02/frances_tiafoe_sharpens_up_for_round_2_win_at_2026_us_open.html
- ATP Tour, uradni rezultati OP ZDA 2026: https://www.atptour.com/en/news/us-open-2026-results
- Reuters, Tiafoejeva zmaga nad Sakamotom, 3. september 2026: https://www.reuters.com/sports/tennis/tiafoe-reaches-us-open-third-round-with-straight-sets-win-over-sakamoto-2026-09-03/
- Uradna stran OP ZDA, pregled sredinih rezultatov, 2. september 2026: https://www.usopen.org/en_US/news/articles/2026-09-02/who_won_on_wednesday_at_the_2026_us_open_results_and_highlights.html`,
  category: "Šport",
  author: "Uredništvo Blog Lab",
  status: "published",
  createdAt: "2026-09-03T06:59:00.000Z",
  updatedAt: "2026-09-03T06:59:00.000Z"
}, {
  id: "svet-bo-presegel-mejo-ena-cela-pet-stopinje",
  title: "Svet bo presegel mejo 1,5 °C: kaj opozorilo UNEP dejansko pomeni",
  excerpt: "Novo poročilo Programa ZN za okolje opozarja, da bo svet mejo segrevanja 1,5 °C verjetno presegel že v nekaj letih. Vrnitev pod prag ostaja mogoča, vendar zelo negotova.",
  seoDescription: "UNEP opozarja, da bo svet kmalu presegel 1,5 °C segrevanja. Pojasnjujemo podnebni presežek, tveganja ter pomen hitrega zmanjšanja izpustov.",
  content: `# Svet bo presegel mejo 1,5 °C: kaj opozorilo UNEP dejansko pomeni

Program Združenih narodov za okolje (UNEP) je 2. septembra objavil poročilo »Limiting Overshoot«, ki prinaša neprijetno, a pomembno ugotovitev: svet bo mejo segrevanja 1,5 stopinje Celzija glede na predindustrijsko obdobje najverjetneje presegel že v naslednjih nekaj letih. Tudi najbolj optimističen obravnavani scenarij predvideva vrh okoli 1,8 °C.

To ne pomeni, da so vsa podnebna prizadevanja brez smisla. Pomeni pa, da se je cilj spremenil: poleg preprečevanja še višjega segrevanja bo treba presežek nad 1,5 °C omejiti, ga čim prej doseči na vrhu ter temperaturo dolgoročno poskusiti znova znižati.

## Kaj pomeni preseganje meje

Meja 1,5 °C iz Pariškega sporazuma se nanaša na dolgoročno povprečno globalno temperaturo, ne na posamezen vroč dan, mesec ali leto. Svet je v nekaterih krajših obdobjih ta prag že presegel, toda poročilo govori o prehodu v trajnejše obdobje segrevanja nad mejo.

UNEP tak razvoj opisuje kot »overshoot« oziroma temperaturni presežek. Pot, ki jo organizacija še vidi kot najboljšo razpoložljivo možnost, ima tri dele: čim manjši presežek, čim zgodnejši temperaturni vrh in nato upad. Razlika med kratkim ter omejenim presežkom in dolgotrajnim segrevanjem je pomembna, saj se z vsako dodatno desetinko stopinje povečujejo tveganja.

## Zakaj vrnitev ni preprosta

Po ugotovitvah poročila bi bila vrnitev pod 1,5 °C tehnično še mogoča, vendar je zelo negotova. Zahtevala bi hitro in obsežno zmanjšanje izpustov toplogrednih plinov, doseganje neto ničelnih izpustov ter odstranjevanje dela ogljikovega dioksida, ki je že v ozračju.

Tehnologije in naravne rešitve za odstranjevanje ogljika imajo omejitve. Pogozdovanje zahteva velike površine in trajno zaščito gozdov, industrijske metode pa so še drage in se ne uporabljajo v potrebnem obsegu. Zato odstranjevanje ogljika ne more nadomestiti zmanjševanja izpustov pri energetiki, prometu, industriji in rabi zemljišč.

Associated Press ob poročilu poudarja tudi razliko med začasnim preseganjem in nepovratnimi posledicami. Globalna temperatura bi se v prihodnosti lahko znižala, vendar vseh izgub ne bi bilo mogoče odpraviti. Nekateri ekosistemi, ledeniki in skupnosti bi lahko utrpeli škodo še pred morebitno vrnitvijo pod prag.

## Vsaka desetinka stopinje ostaja pomembna

Pri podnebnih mejah hitro nastane napačen vtis, da je po prekoračitvi cilja vseeno, kako visoko se temperatura dvigne. Znanstveno sporočilo je ravno nasprotno. Segrevanje za 1,6 °C prinaša manjše tveganje kot segrevanje za 2 °C, to pa je varnejše od sveta pri 2,5 ali 3 °C.

Višje temperature povečujejo verjetnost in intenzivnost vročinskih valov, suš, ekstremnih padavin ter poplav. Povečujejo tudi pritisk na prehranske sisteme, oskrbo z vodo, zdravje ljudi, obalne kraje in biotsko raznovrstnost. Nekatere posledice so postopne, druge pa lahko nastopijo, ko naravni sistemi dosežejo kritične meje.

## Kaj poročilo zahteva od držav

Glavno sporočilo ni poziv k opustitvi cilja 1,5 °C, temveč k hitrejšemu ukrepanju. Države morajo obljube pretvoriti v dejansko zmanjšanje izpustov, hkrati pa vlagati v prilagajanje na vročino, poplave, sušo in dvig morske gladine. Posebno pomembna ostajata financiranje ranljivih držav in pravična porazdelitev stroškov prehoda.

Poročilo tudi ne daje dovoljenja za odlašanje v pričakovanju prihodnjih tehnologij. Več izpustov danes pomeni višji in daljši presežek ter večjo odvisnost od metod odstranjevanja ogljika, katerih prihodnji obseg ni zagotovljen.

Najbolj pošten povzetek je zato dvojen. Preseganje 1,5 °C je po novi oceni skoraj neizogibno in del škode bo nepovraten. Toda velikost segrevanja, trajanje presežka in posledice za ljudi so še vedno odvisni od odločitev, ki jih države, podjetja in družbe sprejmejo zdaj.

## Viri

- UNEP, uradna predstavitev poročila »Limiting Overshoot«, 2. september 2026: https://www.unep.org/news-and-stories/press-release/unep-world-set-cross-15degc-global-warming-can-still-limit-adapt-and
- Reuters, povzetek ključnih ugotovitev UNEP, 2. september 2026: https://www.reuters.com/sustainability/cop/global-temperature-rises-exceed-15-celsius-within-few-years-unep-says-2026-09-02/
- Associated Press, razlaga temperaturnega presežka in posledic, 2. september 2026: https://apnews.com/article/climate-change-threshold-catastrophe-overshoot-un-warming-1b2d126e8359ba77e5546f27d8f4a4e1
- Združeni narodi, pojasnilo pomena meje 1,5 °C: https://www.un.org/en/climatechange/science/climate-issues/degrees-matter`,
  category: "Aktualno",
  author: "Uredništvo Blog Lab",
  status: "published",
  createdAt: "2026-09-02T18:01:00.000Z",
  updatedAt: "2026-09-02T18:01:00.000Z"
}, {
  id: "leipzig-dron-nemske-obtozbe-in-odziv-eu",
  title: "Leipzig po poskusu napada z dronom: nemške obtožbe in odziv EU",
  excerpt: "Nemčija je Rusijo obtožila odgovornosti za spodleteli napad z eksplozivnim dronom na letališču Leipzig/Halle. Moskva očitke zavrača, EU pa razpravlja o dodatnih sankcijah.",
  seoDescription: "Kaj je znano o spodletelem napadu z dronom na letališču Leipzig/Halle, kaj trdita Nemčija in Rusija ter kakšen odziv pripravlja EU.",
  content: `# Leipzig po poskusu napada z dronom: nemške obtožbe in odziv EU

Nemška vlada je 1. septembra Rusijo javno obtožila odgovornosti za spodleteli napad z eksplozivnim dronom na letališču Leipzig/Halle. Incident se je zgodil v začetku avgusta, ko so letališki delavci našli napravo v bližini ukrajinskega tovornega letala. Rusija obtožbo zavrača. Evropski zunanji ministri medtem razpravljajo o političnem odzivu in morebitni razširitvi sankcij.

Primer odpira resno varnostno vprašanje, vendar zahteva natančno ločevanje med potrjenimi okoliščinami, ugotovitvami nemških oblasti ter političnimi izjavami posameznih predstavnikov.

## Kaj je bilo najdeno na letališču

Po poročanju Reutersa in Associated Pressa je bila 4. avgusta na območju letališča Leipzig/Halle odkrita z eksplozivom opremljena brezpilotna naprava. V bližini je bilo ukrajinsko tovorno letalo, naprava pa ni eksplodirala. Nemški organi so sprožili preiskavo dogodka, ki bi lahko ogrozil civilno letalstvo in pomembno evropsko logistično vozlišče.

Potrjeno je torej, da je bila nevarna naprava najdena in onesposobljena ter da primer preiskujejo nemški organi. Javno dostopna poročila ne omogočajo neodvisnega preverjanja vseh obveščevalnih podatkov, na katere se sklicuje nemška vlada.

## Nemčija odgovornost pripisuje Rusiji

Nemški notranji minister Alexander Dobrindt je dejal, da ugotovitve obveščevalnih služb kažejo na ljudi, ki naj bi delovali po naročilu ruskih državnih struktur. Zunanji minister Johann Wadephul je napovedal več odzivnih ukrepov, med drugim zaprtje ruskega generalnega konzulata v Bonnu in Ruskega doma v Berlinu. Na pogovor je bil poklican tudi ruski veleposlanik.

To je uradno stališče nemške vlade, ne sodna ugotovitev. Nemčija trdi, da ima za pripis odgovornosti obveščevalno podlago, vendar celotno dokazno gradivo zaradi narave preiskave ni javno. Zato je korektno zapisati, da Berlin odgovornost pripisuje Rusiji, ne pa, da je bila odgovornost že pravnomočno dokazana.

## Moskva očitke zavrača

Ruska stran je nemške navedbe označila za lažne in neutemeljene. Moskva zanika vpletenost ter trdi, da Berlin uporablja incident za zaostrovanje odnosov. Tudi to je izjava ene od vpletenih strani; sama po sebi ne potrjuje niti ne ovrže nemških ugotovitev.

Razlika med obema stališčema je velika. Nemčija govori o državnem naročilu in delu širšega vzorca hibridnih dejavnosti, Rusija pa zanika povezavo z dogodkom. Nadaljnja kazenska preiskava in morebitni sodni postopki bodo zato ključni za javno preverljiv prikaz dokazov.

## EU razpravlja o sankcijah, odločitev še ni sprejeta

Na srečanju zunanjih ministrov EU na Irskem je Wadephul 2. septembra dejal, da bo Unija v prihodnjih tednih delala na dodatnih sankcijah proti posameznikom, povezanim z Rusijo. Visoka predstavnica EU Kaja Kallas je ocenila, da ima poskus napada značilnosti terorizma, ki ga podpira država. Njena formulacija je politična ocena, ne nova neodvisna preiskovalna ugotovitev.

Pomembno je tudi, da napoved dela na sankcijah še ne pomeni njihovega sprejetja. Sankcije EU potrebujejo soglasje držav članic in pravno opredeljene cilje. Do takrat gre za smer političnega usklajevanja, ne za dokončen ukrep.

## Zakaj je primer pomemben za Evropo

Letališče Leipzig/Halle je veliko tovorno vozlišče, zato incident presega dvostranski spor med Berlinom in Moskvo. Če bodo nemške ugotovitve podprte z dodatnimi javno preverljivimi dokazi, bo primer okrepil evropsko razpravo o zaščiti prometne infrastrukture, nadzoru brezpilotnih naprav in odzivu na prikrite operacije.

Hkrati morajo oblasti preprečiti, da bi resna politična obtožba prehitela dokazni postopek. Najbolj zanesljiv trenutni povzetek je zato naslednji: nevarna naprava je bila odkrita, Nemčija odgovornost pripisuje ruskim državnim strukturam, Rusija to zanika, EU pa šele oblikuje skupen odziv.

## Viri

- Reuters, nemška obtožba in napovedani ukrepi, 1. september 2026: https://www.reuters.com/world/europe/germany-says-russia-responsible-drone-attack-leipzig-airport-2026-09-01/
- Reuters, rusko zavračanje obtožb, 1. september 2026: https://www.reuters.com/world/europe/russia-calls-germanys-leipzig-drone-attack-claims-false-and-an-unprecedented-2026-09-01/
- Reuters, razprava EU o dodatnih sankcijah, 2. september 2026: https://www.reuters.com/world/europe/eu-work-further-sanctions-against-russian-individuals-germany-says-2026-09-02/
- Associated Press, pregled incidenta in evropskega odziva, 2. september 2026: https://apnews.com/article/8a0054face48cc56f6cb6bcf9a8f4b51
- Deutschlandfunk, povzetek tiskovne konference nemške vlade, 2. september 2026: https://www.deutschlandfunk.de/drohnen-vorfall-in-leipzig-bundesregierung-macht-russland-verantwortlich-russisches-generalkonsulat--100.html`,
  category: "Politika",
  author: "Uredništvo Blog Lab",
  status: "published",
  createdAt: "2026-09-02T13:00:00.000Z",
  updatedAt: "2026-09-02T13:00:00.000Z"
}, {
  id: "slovenija-po-zmagi-nad-madzarsko-ostaja-v-igri-za-sp",
  title: "Slovenija po zmagi nad Madžarsko ostaja v igri za svetovno prvenstvo",
  excerpt: "Košarkarska reprezentanca je v Tivoliju premagala Madžarsko z 92:77 in se povzpela na tretje mesto skupine L. Zmaga je pomembna, vendar pot do SP 2027 še ni končana.",
  seoDescription: "Slovenija je v kvalifikacijah za SP 2027 premagala Madžarsko z 92:77. Prepelič je dosegel 24 točk, reprezentanca pa ostaja v boju za Katar.",
  content: `# Slovenija po zmagi nad Madžarsko ostaja v igri za svetovno prvenstvo

Slovenska košarkarska reprezentanca si je z domačo zmago nad Madžarsko znova odprla pot proti svetovnemu prvenstvu 2027. V nedeljo, 30. avgusta, je v ljubljanski dvorani Tivoli zmagala z 92:77 in po osmih tekmah zasedla tretje mesto skupine L. To je položaj, ki ob koncu kvalifikacij prinaša nastop na prvenstvu v Katarju, vendar boj še zdaleč ni odločen.

Slovenija je tekmo vodila od začetka do konca. Rezultat po četrtinah je bil 25:17, 43:36 in 75:59, v zaključku pa je reprezentanca ohranila dovolj nadzora, da madžarski poskus približevanja ni ogrozil zmage. Uradna statistika FIBA potrjuje končni izid in skoraj 49-odstoten slovenski met iz igre.

## Prepelič prevzel odgovornost

Klemen Prepelič je bil prvi strelec Slovenije s 24 točkami, ob tem pa je po poročanju slovenskih medijev dodal še devet podaj. Aleksej Nikolić je dosegel 18 točk, Alen Omić pa 15 točk in 12 skokov. Prav razpršena odgovornost je bila ena od pomembnih razlik v primerjavi s tekmami, na katerih je bila slovenska igra preveč odvisna od posameznih rešitev.

Začetek je pokazal jasen namen. Slovenija je povedla z 10:0 in Madžarsko takoj prisilila v lovljenje rezultata. Gostje so do polčasa zaostanek zmanjšali na sedem točk, toda domači so po odmoru odgovorili z najboljšo četrtino večera. Pred zadnjimi desetimi minutami je prednost znašala 16 točk.

Zmaga ni temeljila le na napadu. Slovenija je imela izrazito premoč v skoku, s čimer je omejevala druge priložnosti tekmeca in si ustvarjala dodatne napade. FIBA navaja tudi boljši slovenski odstotek meta za tri točke: 37,1 odstotka proti madžarskim 29,2 odstotka.

## Pomembni dve točki, ne pa že vozovnica

Po osmih krogih je Francija na vrhu skupine, za njo je Finska. Slovenija je z zmago skočila na tretje mesto, medtem ko so razlike med reprezentancami v sredini skupine majhne. To pomeni, da lahko že naslednji kvalifikacijski tekmi znova pomembno spremenita vrstni red.

V naslednjo fazo razmišljanja zato ne sodi vprašanje, ali je Slovenija že uvrščena, temveč kako ponoviti raven igre iz Tivolija. Napredovanje si bodo zagotovile prve tri reprezentance skupine. Rezultati iz prvega dela se prenašajo, zato ima vsaka zmaga v drugem krogu dodatno težo.

Slovenijo v nadaljevanju čakajo nove tekme novembra, kvalifikacije pa se bodo končale februarja 2027. Sestava ekip se lahko med posameznimi okni spremeni, saj se reprezentančni koledar prekriva s klubskimi obveznostmi v ligi NBA in drugih tekmovanjih. Prav zato bo pomembna širina kadra, ki je bila proti Madžarski vidna.

## Tivoli je dobil tekmo, kakršno je Slovenija potrebovala

Po porazu proti Franciji je bilo srečanje z Madžarsko skoraj nujno dobiti. Slovenska ekipa je pritisk sprejela dobro: hitro je prevzela pobudo, preživela slabše minute pred polčasom in nato odločno odgovorila. Takšna tekma ne rešuje vseh vprašanj, ponuja pa uporaben vzorec za nadaljevanje kvalifikacij.

Pomembna je bila tudi podpora 2.500 gledalcev, kolikor jih navaja uradni zapisnik FIBA. Tivoli je reprezentanci ponudil domače okolje, igralci pa so navijačem vrnili z energičnim začetkom in nadzorovanim zaključkom.

Slovenija ima zdaj boljši položaj, kot ga je imela pred tekmo, vendar še nima prostora za sprostitev. Zmaga z 92:77 je predvsem dokaz, da lahko tudi brez vseh najbolj znanih imen odigra kolektivno in dovolj učinkovito. Če bo to ponovila v preostalih oknih, bo boj za tretje zaporedno svetovno prvenstvo ostal v slovenskih rokah.

## Viri

- FIBA, uradni zapisnik tekme Slovenija–Madžarska, 30. avgust 2026: https://www.fiba.basketball/en/events/fiba-basketball-world-cup-2027-european-qualifiers/games/127086-SLO-HUN
- FIBA, uradno pojasnilo sistema kvalifikacij za SP 2027: https://www.fiba.basketball/en/events/fiba-basketball-world-cup-2027-european-qualifiers/how-to-qualify-for-the-world-cup
- 24UR, poročilo s tekme in izjave reprezentantov, 30. avgust 2026: https://www.24ur.com/sport/kosarka/madzare-je-treba-premagati-zlepa-ali-zgrda.html
- Siol Sportal, pregled tekme in statistike, 30. avgust 2026: https://siol.net/sportal/kosarka/kvalifikacije-sp-2027-drugi-del-drugi-krog-slovenija-madzarska-700152`,
  category: "Šport",
  author: "Uredništvo Blog Lab",
  status: "published",
  createdAt: "2026-09-02T07:02:00.000Z",
  updatedAt: "2026-09-02T07:02:00.000Z"
}, {
  id: "nenavaden-signal-v-iskanju-temne-snovi",
  title: "Nenavaden signal v globinah: nov namig v iskanju temne snovi",
  excerpt: "Eksperiment LUX-ZEPLIN je zaznal en delčni dogodek, ki ga znani šumi težko pojasnijo. Rezultat je zanimiv, vendar še zdaleč ni potrjeno odkritje temne snovi.",
  seoDescription: "LUX-ZEPLIN je zaznal nenavaden delčni dogodek, združljiv z nekaterimi modeli temne snovi, a raziskovalci poudarjajo, da en signal ne pomeni odkritja.",
  content: `# Nenavaden signal v globinah: nov namig v iskanju temne snovi

Mednarodna skupina raziskovalcev eksperimenta LUX-ZEPLIN (LZ) je 1. septembra predstavila nenavaden rezultat: v podatkih so našli en delčni dogodek, ki ga z znanimi viri ozadja za zdaj težko razložijo. Signal se je pojavil na območju, kjer bi lahko pričakovali interakcijo hipotetičnega delca temne snovi, imenovanega WIMP. Toda raziskovalci so pri razlagi izrecno previdni. Ne trdijo, da so temno snov odkrili.

Rezultat je pomemben predvsem zato, ker prihaja iz enega najobčutljivejših poskusov neposrednega iskanja temne snovi. Hkrati je dober primer, kako znanost obravnava presenetljive podatke: zanimiv dogodek je začetek preverjanja, ne konec zgodbe.

## Kaj je eksperiment dejansko zaznal

LZ deluje približno 1,5 kilometra pod površjem v raziskovalnem centru Sanford Underground Research Facility v Južni Dakoti. Globoka podzemna lokacija detektor ščiti pred velikim delom kozmičnih delcev, ki bi lahko posnemali iskani signal. V središču naprave je velika količina tekočega ksenona, v katerem raziskovalci iščejo izjemno redke trke delcev z jedri atomov.

Pri predstavljenem dogodku je detektor zabeležil odziv, podoben jedrskemu odboju. Takšen podpis bi lahko nastal, če bi WIMP trčil v jedro ksenona. Analiza je zajela izpostavljenost 2,84 tonskega leta in razširjeno energijsko območje, kar raziskovalcem omogoča preverjanje več modelov temne snovi kot pri običajnem iskanju.

Ključno dejstvo je, da gre za en sam dogodek. Ekipa je ocenila, da ga običajni pričakovani šumi ne pojasnijo zlahka, vendar še preverja druge možne razlage, povezane z delovanjem detektorja ali redkimi fizikalnimi procesi.

## Zakaj en signal še ni odkritje

V fiziki delcev mora biti verjetnost naključja izjemno majhna, preden raziskovalci govorijo o odkritju. En nenavaden dogodek tega merila ne dosega. Potrebnih bo več podatkov, neodvisno preverjanje analize in po možnosti podobni signali v drugih eksperimentih.

Tiskovna objava Univerze Brown rezultat opisuje kot najzanimivejši namig, ki ga je do zdaj zaznal LZ, obenem pa navaja jasno opozorilo vodstva eksperimenta, da skupina ne želi prehitevati dokazov. Tudi Reuters poroča, da bi dogodek lahko predstavljal prvi namig, vendar ne potrditve.

Previdnost ni znak šibkosti rezultata. Je bistveni del postopka, s katerim znanstveniki ločujejo resnične pojave od statističnih naključij, nepopolno razumljenega ozadja ali merilnih posebnosti.

## Kaj sploh je temna snov

Običajna snov sestavlja zvezde, planete in vse, kar lahko neposredno opazujemo. Po današnjih ocenah pa predstavlja le približno 15 odstotkov vse snovi v vesolju. Preostanek naj bi bila temna snov, ki ne oddaja in ne odbija svetlobe. Astronomi o njenem obstoju sklepajo iz gravitacijskih učinkov na gibanje galaksij, jate galaksij in ukrivljanje svetlobe.

WIMP-i oziroma šibko interagirajoči masivni delci so ena od predlaganih razlag, niso pa edina. Če bi dogodek v LZ pozneje potrdili kot interakcijo WIMP-a, bi to pomenilo velik preboj v fiziki. Če se izkaže za drug proces, bo rezultat še vedno pomagal izboljšati razumevanje detektorja in prihodnja iskanja.

## Naslednji korak je več podatkov

Rezultat je bil predstavljen na konferenci TeV Particle Astrophysics na Japonskem, znanstveni članek pa bo po napovedi ekipe objavljen na repozitoriju arXiv in predložen reviji Physical Review Letters. S tem bodo metode in izračuni na voljo širši strokovni skupnosti.

Najbolj pošten povzetek današnje novice je zato preprost: LUX-ZEPLIN je zaznal nekaj, kar je vredno resne pozornosti, vendar odgovor na vprašanje, ali je človeštvo prvič neposredno zaznalo temno snov, še ni znan. O tem bodo odločili dodatni podatki, preverjanje in čas.

## Viri

- LUX-ZEPLIN, uradna objava rezultatov, 1. september 2026: https://lz.lbl.gov/
- Univerza Brown, pojasnilo rezultata LZ, 1. september 2026: https://www.brown.edu/news/2026-09-01/lz-dark-matter-results
- Brookhaven National Laboratory, povzetek ugotovitev, 1. september 2026: https://www.bnl.gov/newsroom/news.php?a=123133
- Reuters, poročilo o možnem namigu temne snovi, 1. september 2026: https://www.reuters.com/science/scientists-make-potential-breakthrough-search-dark-matter-2026-09-01/`,
  category: "Aktualno",
  author: "Uredništvo Blog Lab",
  status: "published",
  createdAt: "2026-09-01T18:02:00.000Z",
  updatedAt: "2026-09-01T18:02:00.000Z"
}, {
  id: "bledski-strateski-forum-evropa-pred-odlocitvami",
  title: "Bledski strateški forum: Evropa med varnostjo, širitvijo in zaupanjem v demokracijo",
  excerpt: "Na Bledu se danes zaključuje 21. strateški forum. V ospredju so evropska varnost, Ukrajina, širitev EU, konkurenčnost in vprašanje, kako okrepiti zaupanje v demokratične institucije.",
  seoDescription: "Bledski strateški forum 2026 odpira razpravo o evropski varnosti, Ukrajini, širitvi EU, konkurenčnosti in demokratični odpornosti.",
  content: `# Bledski strateški forum: Evropa med varnostjo, širitvijo in zaupanjem v demokracijo

Na Bledu se 1. septembra zaključuje 21. Bledski strateški forum, ki letos poteka pod naslovom »Moč soustvarjanja prihodnosti«. Program združuje politične predstavnike, evropske institucije, gospodarstvo in civilno družbo, glavne razprave pa se vrtijo okoli evropske varnosti, vojne v Ukrajini, širitve Evropske unije, gospodarske konkurenčnosti in odpornosti demokratičnih družb.

Forum sam po sebi ne sprejema zavezujočih odločitev. Njegov pomen je predvsem v tem, da v Sloveniji na enem mestu odpira vprašanja, ki bodo v prihodnjih mesecih vplivala na politiko EU in držav Zahodnega Balkana. Pri spremljanju razprav je zato treba ločiti med uradno sprejetimi ukrepi, političnimi predlogi posameznih govorcev in širšimi ocenami sodelujočih.

## Ukrajina ostaja osrednje varnostno vprašanje

Generalni sekretar Sveta Evrope Alain Berset je obisk Slovenije in nastop na forumu povezal s podporo Ukrajini, odgovornostjo za mednarodne zločine ter krepitvijo demokratične varnosti. Svet Evrope izpostavlja vzpostavljanje posebnega tribunala za kaznivo dejanje agresije, razvoj mehanizma za povračilo škode in pripravo novega akcijskega načrta za Ukrajino za obdobje 2027–2030.

To so konkretni institucionalni procesi, vendar njihova izvedba še ni zaključena. Razprava na Bledu zato ne pomeni, da so bili sprejeti novi pravni ukrepi, temveč kaže, da vprašanje odgovornosti in povojne ureditve ostaja visoko na evropskem političnem dnevnem redu.

## Širitev EU je hkrati geopolitična in institucionalna odločitev

V programu foruma ima pomembno mesto prihodnost evropske širitve, predvsem v odnosu do držav Zahodnega Balkana. Evropska komisija širitev opisuje kot odgovor na geopolitične spremembe, vendar ostajajo članstvo, časovnica in pogoji odvisni od napredka posameznih kandidatk ter soglasja držav članic.

Razprava ni omejena samo na vprašanje, katere države bi se lahko pridružile. V EU poteka tudi razmislek, kako bi razširjena povezava sprejemala odločitve in varovala vladavino prava. Francija, Nemčija, Nizozemska, Belgija in Luksemburg so junija predlagale razpravo o dodatnih varovalkah za prihodnje članice, med drugim o začasnih omejitvah nekaterih glasovalnih pravic. Gre za predlog petih držav, ne za že sprejeto skupno politiko EU.

Za Slovenijo je širitev posebej pomembna zaradi geografske bližine, gospodarskih povezav in dolgoletnega političnega zagovarjanja vključevanja Zahodnega Balkana. Hkrati mora država podpirati merljive reforme, saj bi širitev brez jasnih pravil lahko oslabila zaupanje v evropske institucije.

## Demokracija ni samo vprašanje volitev

Program foruma vključuje razprave o pripravljenosti državljanov braniti demokracijo, o politični apatiji ter o vlogi kulture in javnih institucij v času kriz. Takšna vprašanja so pomembna, ker demokratična odpornost ni odvisna zgolj od izvedbe volitev. Vključuje tudi neodvisnost sodstva, svobodo medijev, preglednost odločanja, varstvo človekovih pravic in sposobnost institucij, da se odzovejo na dezinformacije.

Prisotnost Sveta Evrope na Bledu poudarja prav ta širši pogled. Organizacija združuje 46 držav in se osredotoča na človekove pravice, demokracijo ter vladavino prava. Njena vloga se razlikuje od Evropske unije, zato pobud obeh institucij ni primerno enačiti.

## Konkurenčnost kot politična tema

Poleg varnosti in demokracije program odpira vprašanje evropske gospodarske konkurenčnosti, dostopa do kapitala, trga dela, industrije, zdravstva in vesoljskih tehnologij. Razprava kaže, da zunanja in notranja politika nista več ločeni področji: energija, dobavne verige, tehnološka odvisnost in gospodarska rast neposredno vplivajo na sposobnost Evrope, da vodi samostojno varnostno politiko.

Za Slovenijo je pomembno, da se razprave prevedejo v izvedljive predloge za podjetja, raziskovalne ustanove in javni sektor. Sama navzočnost visokih gostov še ni rezultat. Merilo uspeha bodo morebitna poznejša sodelovanja, usklajene pobude in spremembe politik.

## Kaj lahko forum dejansko doseže

Bledski strateški forum Sloveniji omogoča vidnost in dostop do političnih razprav na visoki ravni. Njegova omejitev je, da sklepi razprav večinoma niso pravno zavezujoči. Zato bo treba po zaključku preveriti, katere zamisli bodo dobile podporo v Svetu EU, Evropski komisiji, Svetu Evrope ali nacionalnih vladah.

Današnji program kaže precej jasno sliko evropskih prednostnih nalog: varnost Ukrajine, prihodnost širitve, gospodarska moč in zaupanje v demokracijo se obravnavajo kot medsebojno povezana vprašanja. Odprto pa ostaja, ali bodo politični voditelji iz dialoga prešli k usklajenim odločitvam.

## Viri

- Bledski strateški forum, uradni program 2026: https://www.bledstrategicforum.org/concept_note/BSF-2026-Programme.pdf
- Bledski strateški forum, uradna stran: https://www.bledstrategicforum.org/
- Svet Evrope, obisk generalnega sekretarja v Sloveniji: https://www.coe.int/en/web/portal/-/secretary-general-to-address-bled-strategic-forum-on-renewing-democracy-in-europe
- Evropska komisija, Forum o širitvi EU 2026: https://enlargement.ec.europa.eu/
- Reuters, predlog petih držav o varovalkah pri širitvi, 9. junij 2026: https://www.reuters.com/world/five-eu-countries-float-safeguards-future-eu-members-2026-06-09/`,
  category: "Politika",
  author: "Uredništvo Blog Lab",
  status: "published",
  createdAt: "2026-09-01T12:03:00.000Z",
  updatedAt: "2026-09-01T12:03:00.000Z"
}, {
  id: "pogacar-po-uspesni-operaciji-zacenja-okrevanje",
  title: "Pogačar po uspešni operaciji začenja zahtevno okrevanje",
  excerpt: "Tadej Pogačar je po hudem padcu na Vuelti uspešno prestal operacijo leve ključnice. Čas njegove vrnitve ostaja odprt, prednost pa ima popolno okrevanje.",
  seoDescription: "Tadej Pogačar je po padcu na Vuelti uspešno prestal operacijo ključnice. Kaj je potrjeno, kaj ostaja neznano in kaj poškodba pomeni za sezono 2026.",
  content: `# Pogačar po uspešni operaciji začenja zahtevno okrevanje

Slovenski kolesarski zvezdnik Tadej Pogačar je uspešno prestal operacijo zlomljene leve ključnice, potem ko je zaradi hudega padca predčasno končal letošnjo Dirko po Španiji. Poseg je pomemben prvi korak, vendar zdravniška služba njegove ekipe še ni določila datuma vrnitve na tekmovanja. V ospredju ostajata varno okrevanje po pretresu možganov in spremljanje stabilnega zloma vratnega vretenca C7.

## Padec, ki je končal boj za rdečo majico

Pogačar je padel približno 33 kilometrov pred ciljem osme etape Vuelte. Čeprav je po nesreči poskusil nadaljevati, mu bolečina tega ni dopuščala. Zdravniški pregled je pokazal pretres možganov, premaknjen zlom leve ključnice, stabilen zlom vretenca C7 in več odrgnin. Ekipa je obenem sporočila, da ni bilo drugih večjih poškodb ali nevroloških posledic.

Nesreča je prekinila izjemno uspešen začetek dirke. Pogačar je do odstopa dobil tri etape in nosil rdečo majico vodilnega. Na Vuelti je želel dopolniti zbirko zmag na vseh treh največjih tritedenskih dirkah, vendar je športni cilj po padcu nemudoma postal drugotnega pomena.

## Operacija je uspela, napovedi ostajajo previdne

Po poročanju ekipe UAE Team Emirates-XRG in več mednarodnih medijev je bila operacija ključnice v Barceloni uspešna. Poseg so izvedli po tem, ko so zdravniki zaradi pretresa možganov ocenili, da je varno nadaljevati zdravljenje. Pogačar naj bi še nekaj dni ostal pod zdravniškim nadzorom.

Uspešna operacija še ne pomeni, da je mogoče zanesljivo določiti datum vrnitve. Pri takšni kombinaciji poškodb ni odločilna samo ključnica. Pretres možganov zahteva postopno spremljanje simptomov, zlom v vratnem delu hrbtenice pa posebej previden pristop. Zato bi bile napovedi o skorajšnji vrnitvi ali nastopu na določeni dirki za zdaj špekulacija.

## Kaj poškodba pomeni za nadaljevanje sezone

Pogačarjev tekmovalni koledar je vključeval pomembne jesenske cilje, med njimi svetovno prvenstvo in evropsko prvenstvo. Njegova ekipa možnosti nastopa še ni dokončno izključila, vendar trenutno ni potrdila nobenega roka. Odločitev bo odvisna od celjenja, nevroloških pregledov, odziva na rehabilitacijo in soglasja zdravnikov.

Vrhunski kolesarji se po operaciji ključnice včasih hitro vrnejo na sobno kolo, toda primeri niso neposredno primerljivi. Pogačarjeve dodatne poškodbe pomenijo, da običajnih časovnic ni primerno uporabljati kot napoved. Najpomembnejši merili bosta odsotnost simptomov in dolgoročna varnost, ne koledar tekmovanj.

## Ekipa mora na Vuelti spremeniti načrt

Odstop vodilnega je spremenil tudi razmerja na dirki. Pogačarjevi moštveni kolegi so ostali brez kapetana za skupno zmago, zato se je ekipa preusmerila k etapnim uspehom in bolj napadalnemu dirkanju. Vodstvo je prevzel Enric Mas, boj za končno razvrstitev pa se je naenkrat odprl drugim favoritom.

Za slovenske navijače je novica o uspešni operaciji spodbudna, a glavna zgodba prihodnjih dni ne bo hitrost njegove vrnitve. Pomembneje bo, da okrevanje poteka brez zapletov in da se Pogačar na kolo vrne šele, ko bo to varno. Dokler ekipa ne objavi novega zdravniškega poročila, ostajajo vsi natančni datumi zgolj ugibanje.

## Viri

- Uradna stran Tadeja Pogačarja: https://tadejpogacar.com/painful-end-to-the-vuelta-for-tadej/
- RTVE, 31. avgust 2026: https://www.rtve.es/deportes/20260831/pogacar-operacion-fractura-clavicula-vuelta-2026/17207663.shtml
- Reuters, 29. avgust 2026: https://www.reuters.com/sports/vuelta-leader-pogacar-forced-abandon-after-stage-eight-crash-2026-08-29/
- Associated Press: https://www.ctpost.com/sports/article/tour-de-france-champion-pogacar-has-collarbone-22411508.php`,
  category: "Šport",
  author: "Uredništvo Blog Lab",
  status: "published",
  createdAt: "2026-09-01T08:00:00.000Z",
  updatedAt: "2026-09-01T08:00:00.000Z"
}, {
  id: "dobrodosli-v-blog-lab",
  title: "Dobrodošli v Blog Lab",
  excerpt: "To je testna objava. Uredite jo ali ustvarite nov članek in preverite, kako vaš agent opravi celoten postopek.",
  content: "# Preprost prostor za testiranje\n\nBlog Lab je namenjen hitremu preizkušanju pisanja in objavljanja člankov.\n\n## Kaj lahko preizkusite?\n\nAgent lahko vnese naslov, izbere kategorijo, pripravi povzetek, napiše vsebino ter članek shrani kot osnutek ali ga objavi.\n\nVsi podatki so v tej različici shranjeni lokalno v vašem brskalniku.",
  category: "Novice",
  author: "Uredništvo",
  status: "published",
  createdAt: "2026-09-01T08:00:00.000Z",
  updatedAt: "2026-09-01T08:00:00.000Z"
}];

const emptyDraft = () => ({
  id: "",
  title: "",
  excerpt: "",
  content: "",
  category: "Novice",
  author: "",
  status: "draft",
  createdAt: "",
  updatedAt: ""
});

function slugify(value) {
  return value
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/(^-|-$)/g, "") || `clanek-${Date.now()}`;
}

function formatDate(value) {
  return new Intl.DateTimeFormat("sl-SI", {
    day: "numeric",
    month: "long",
    year: "numeric"
  }).format(new Date(value));
}

function readingTime(content = "") {
  return Math.max(1, Math.ceil(content.trim().split(/\s+/).filter(Boolean).length / 190));
}

function ArticleBody({ content }) {
  return (
    <div className="article-body">
      {content.split("\n").map((line, index) => {
        if (line.startsWith("### ")) return <h3 key={index}>{line.slice(4)}</h3>;
        if (line.startsWith("## ")) return <h2 key={index}>{line.slice(3)}</h2>;
        if (line.startsWith("# ")) return <h1 key={index}>{line.slice(2)}</h1>;
        if (line.startsWith("- ")) return <div className="bullet" key={index}>• {line.slice(2)}</div>;
        if (!line.trim()) return <div className="line-space" key={index} />;
        return <p key={index}>{line}</p>;
      })}
    </div>
  );
}

function Icon({ name }) {
  const paths = {
    home: <><path d="m3 11 9-8 9 8"/><path d="M5 10v10h14V10"/><path d="M9 20v-6h6v6"/></>,
    edit: <><path d="M12 20h9"/><path d="m16.5 3.5 4 4L8 20H4v-4Z"/></>,
    file: <><path d="M6 2h8l4 4v16H6Z"/><path d="M14 2v5h5"/><path d="M9 13h6M9 17h6"/></>,
    search: <><circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/></>,
    arrow: <><path d="m9 18 6-6-6-6"/></>,
    export: <><path d="M12 3v12"/><path d="m7 10 5 5 5-5"/><path d="M5 21h14"/></>,
    close: <><path d="m6 6 12 12M18 6 6 18"/></>
  };
  return <svg aria-hidden="true" viewBox="0 0 24 24" className="icon">{paths[name]}</svg>;
}

export default function Home() {
  const [articles, setArticles] = useState([]);
  const [view, setView] = useState("home");
  const [draft, setDraft] = useState(emptyDraft());
  const [selectedId, setSelectedId] = useState("");
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState("Vse");
  const [preview, setPreview] = useState(false);
  const [toast, setToast] = useState("");
  const [ready, setReady] = useState(false);
  const importRef = useRef(null);

  useEffect(() => {
    try {
      const stored = JSON.parse(localStorage.getItem(STORAGE_KEY) || "null");
      if (Array.isArray(stored) && stored.length) {
        const storedIds = new Set(stored.map((article) => article.id));
        setArticles([...starterArticles.filter((article) => !storedIds.has(article.id)), ...stored]);
      } else {
        setArticles(starterArticles);
      }
    } catch {
      setArticles(starterArticles);
    }
    setReady(true);
  }, []);

  useEffect(() => {
    if (ready) localStorage.setItem(STORAGE_KEY, JSON.stringify(articles));
  }, [articles, ready]);

  useEffect(() => {
    if (!toast) return;
    const timer = setTimeout(() => setToast(""), 2400);
    return () => clearTimeout(timer);
  }, [toast]);

  const published = useMemo(
    () => articles.filter((article) => article.status === "published"),
    [articles]
  );

  const shownArticles = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    return articles
      .filter((article) => filter === "Vse" || (filter === "Objavljeno" ? article.status === "published" : article.status === "draft"))
      .filter((article) => !normalized || `${article.title} ${article.excerpt} ${article.category}`.toLowerCase().includes(normalized))
      .sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt));
  }, [articles, filter, query]);

  const selected = articles.find((article) => article.id === selectedId);

  function navigate(nextView) {
    setView(nextView);
    setPreview(false);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function newArticle() {
    setDraft(emptyDraft());
    navigate("editor");
  }

  function editArticle(article) {
    setDraft({ ...article });
    navigate("editor");
  }

  function openArticle(article) {
    setSelectedId(article.id);
    navigate("article");
  }

  function validateDraft() {
    if (!draft.title.trim()) {
      setToast("Dodajte naslov članka.");
      return false;
    }
    if (!draft.content.trim()) {
      setToast("Dodajte vsebino članka.");
      return false;
    }
    return true;
  }

  function saveArticle(status) {
    if (!validateDraft()) return;
    const now = new Date().toISOString();
    const id = draft.id || `${slugify(draft.title)}-${Date.now().toString().slice(-5)}`;
    const article = {
      ...draft,
      id,
      title: draft.title.trim(),
      excerpt: draft.excerpt.trim() || draft.content.replace(/^#+\s*/gm, "").trim().slice(0, 155),
      author: draft.author.trim() || "Uredništvo",
      status,
      createdAt: draft.createdAt || now,
      updatedAt: now
    };
    setArticles((current) => [article, ...current.filter((item) => item.id !== id)]);
    setDraft(article);
    setToast(status === "published" ? "Članek je objavljen." : "Osnutek je shranjen.");
    navigate("dashboard");
  }

  function removeArticle(id) {
    const target = articles.find((item) => item.id === id);
    if (!target || !window.confirm(`Izbrišem članek »${target.title}«?`)) return;
    setArticles((current) => current.filter((item) => item.id !== id));
    setToast("Članek je izbrisan.");
  }

  function exportArticles() {
    const blob = new Blob([JSON.stringify(articles, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `blog-lab-${new Date().toISOString().slice(0, 10)}.json`;
    link.click();
    URL.revokeObjectURL(url);
    setToast("Podatki so izvoženi.");
  }

  function importArticles(event) {
    const file = event.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      try {
        const data = JSON.parse(reader.result);
        if (!Array.isArray(data)) throw new Error();
        setArticles(data);
        setToast("Članki so uvoženi.");
      } catch {
        setToast("Datoteka ni veljaven izvoz Blog Lab.");
      }
      event.target.value = "";
    };
    reader.readAsText(file);
  }

  return (
    <main>
      <header className="site-header">
        <button className="brand" onClick={() => navigate("home")} aria-label="Blog Lab – domov">
          <span className="brand-mark">B</span>
          <span>Blog Lab</span>
        </button>
        <nav aria-label="Glavna navigacija">
          <button className={view === "home" ? "active" : ""} onClick={() => navigate("home")}>
            <Icon name="home" /> Objave
          </button>
          <button className={view === "dashboard" ? "active" : ""} onClick={() => navigate("dashboard")}>
            <Icon name="file" /> Članki
          </button>
        </nav>
        <button className="primary small" onClick={newArticle} id="new-article-button" data-testid="new-article">
          <span>+</span> Nov članek
        </button>
      </header>

      {view === "home" && (
        <>
          <section className="hero">
            <div className="eyebrow"><span /> PROSTOR ZA IDEJE</div>
            <h1>Pišemo jasno.<br /><em>Objavljamo preprosto.</em></h1>
            <p>Minimalna testna platforma za članke, osnutke in preizkušanje vašega agenta.</p>
            <button className="primary" onClick={newArticle}>Napiši prvi članek <Icon name="arrow" /></button>
          </section>

          <section className="feed container">
            <div className="section-heading">
              <div>
                <span className="kicker">ZADNJE OBJAVE</span>
                <h2>Sveže iz uredništva</h2>
              </div>
              <span className="count">{published.length} {published.length === 1 ? "objava" : "objav"}</span>
            </div>
            <div className="post-grid">
              {published.length ? published.slice(0, 6).map((article, index) => (
                <article className={`post-card ${index === 0 ? "featured" : ""}`} key={article.id} onClick={() => openArticle(article)}>
                  <div className="card-art"><span>{article.category.slice(0, 1)}</span></div>
                  <div className="card-copy">
                    <div className="meta"><span>{article.category}</span><span>{readingTime(article.content)} min branja</span></div>
                    <h3>{article.title}</h3>
                    <p>{article.excerpt}</p>
                    <div className="card-foot"><span>{article.author}</span><span>{formatDate(article.updatedAt)}</span></div>
                  </div>
                </article>
              )) : (
                <div className="empty-state">
                  <h3>Še ni objavljenih člankov.</h3>
                  <p>Ustvarite članek in ga objavite — prikazal se bo tukaj.</p>
                  <button className="secondary" onClick={newArticle}>Ustvari članek</button>
                </div>
              )}
            </div>
          </section>
        </>
      )}

      {view === "dashboard" && (
        <section className="dashboard container">
          <div className="page-title">
            <div><span className="kicker">UREDNIK</span><h1>Vsi članki</h1><p>Upravljajte objave in osnutke na enem mestu.</p></div>
            <button className="primary" onClick={newArticle}>+ Nov članek</button>
          </div>
          <div className="stats">
            <div><strong>{articles.length}</strong><span>Vsi članki</span></div>
            <div><strong>{published.length}</strong><span>Objavljeno</span></div>
            <div><strong>{articles.length - published.length}</strong><span>Osnutki</span></div>
          </div>
          <div className="toolbar">
            <label className="search"><Icon name="search" /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Išči po naslovu ali kategoriji…" /></label>
            <div className="filters">
              {["Vse", "Objavljeno", "Osnutki"].map((item) => <button className={filter === item ? "active" : ""} key={item} onClick={() => setFilter(item)}>{item}</button>)}
            </div>
            <div className="data-actions">
              <button className="icon-button" onClick={exportArticles} title="Izvozi JSON"><Icon name="export" /></button>
              <button className="text-button" onClick={() => importRef.current?.click()}>Uvozi</button>
              <input ref={importRef} type="file" accept="application/json" hidden onChange={importArticles} />
            </div>
          </div>
          <div className="article-list">
            {shownArticles.map((article) => (
              <article key={article.id}>
                <div className={`status-dot ${article.status}`} />
                <div className="list-main">
                  <div className="list-meta"><span>{article.category}</span><span>{formatDate(article.updatedAt)}</span></div>
                  <h3>{article.title}</h3>
                  <p>{article.excerpt}</p>
                </div>
                <span className={`status-pill ${article.status}`}>{article.status === "published" ? "Objavljeno" : "Osnutek"}</span>
                <div className="row-actions">
                  {article.status === "published" && <button onClick={() => openArticle(article)}>Odpri</button>}
                  <button onClick={() => editArticle(article)}>Uredi</button>
                  <button className="danger" onClick={() => removeArticle(article.id)}>Izbriši</button>
                </div>
              </article>
            ))}
            {!shownArticles.length && <div className="empty-row">Ni člankov, ki ustrezajo iskanju.</div>}
          </div>
        </section>
      )}

      {view === "editor" && (
        <section className="editor-shell">
          <div className="editor-topbar">
            <button className="back" onClick={() => navigate("dashboard")}>← Nazaj na članke</button>
            <div className="editor-actions">
              <button className="secondary" onClick={() => setPreview(true)}>Predogled</button>
              <button className="secondary" onClick={() => saveArticle("draft")} id="save-draft-button">Shrani osnutek</button>
              <button className="primary" onClick={() => saveArticle("published")} id="publish-button" data-testid="publish-article">Objavi članek</button>
            </div>
          </div>
          <div className="editor-grid">
            <div className="editor-main">
              <label htmlFor="article-title">Naslov članka</label>
              <input id="article-title" data-testid="article-title" className="title-input" value={draft.title} onChange={(event) => setDraft({ ...draft, title: event.target.value })} placeholder="Vnesite jasen in zanimiv naslov…" autoFocus />
              <label htmlFor="article-excerpt">Kratek povzetek</label>
              <textarea id="article-excerpt" data-testid="article-excerpt" className="excerpt-input" value={draft.excerpt} onChange={(event) => setDraft({ ...draft, excerpt: event.target.value })} placeholder="V eni ali dveh povedih opišite vsebino članka…" maxLength={220} />
              <div className="content-label"><label htmlFor="article-content">Vsebina</label><span>{draft.content.length} znakov · {readingTime(draft.content)} min branja</span></div>
              <div className="format-hint"><b>Namig:</b> uporabite # za naslov, ## za podnaslov in - za alinejo.</div>
              <textarea id="article-content" data-testid="article-content" className="content-input" value={draft.content} onChange={(event) => setDraft({ ...draft, content: event.target.value })} placeholder="# Uvod\n\nZačnite pisati članek…" />
            </div>
            <aside className="editor-sidebar">
              <div className="side-card">
                <h3>Podrobnosti objave</h3>
                <label htmlFor="article-author">Avtor</label>
                <input id="article-author" data-testid="article-author" value={draft.author} onChange={(event) => setDraft({ ...draft, author: event.target.value })} placeholder="Ime avtorja" />
                <label htmlFor="article-category">Kategorija</label>
                <select id="article-category" data-testid="article-category" value={draft.category} onChange={(event) => setDraft({ ...draft, category: event.target.value })}>
                  {CATEGORIES.map((category) => <option key={category}>{category}</option>)}
                </select>
              </div>
              <div className="agent-note">
                <span className="agent-dot" />
                <div><strong>Pripravljeno za agenta</strong><p>Polja in gumbi imajo jasne oznake za zanesljivo avtomatizacijo.</p></div>
              </div>
            </aside>
          </div>
        </section>
      )}

      {view === "article" && selected && (
        <article className="article-page">
          <button className="back" onClick={() => navigate("home")}>← Vse objave</button>
          <div className="article-heading">
            <span className="article-category">{selected.category}</span>
            <h1>{selected.title}</h1>
            <p>{selected.excerpt}</p>
            <div className="article-byline"><strong>{selected.author}</strong><span>•</span><span>{formatDate(selected.updatedAt)}</span><span>•</span><span>{readingTime(selected.content)} min branja</span></div>
          </div>
          <ArticleBody content={selected.content} />
          <div className="article-end"><span>Konec članka</span><button className="secondary" onClick={() => editArticle(selected)}>Uredi članek</button></div>
        </article>
      )}

      {preview && (
        <div className="modal-backdrop" onMouseDown={() => setPreview(false)}>
          <div className="preview-modal" onMouseDown={(event) => event.stopPropagation()} role="dialog" aria-modal="true" aria-label="Predogled članka">
            <button className="modal-close" onClick={() => setPreview(false)}><Icon name="close" /></button>
            <span className="article-category">{draft.category}</span>
            <h1>{draft.title || "Naslov članka"}</h1>
            <p className="preview-excerpt">{draft.excerpt || "Kratek povzetek članka bo prikazan tukaj."}</p>
            <ArticleBody content={draft.content || "Vsebina članka bo prikazana tukaj."} />
          </div>
        </div>
      )}

      {toast && <div className="toast" role="status">{toast}</div>}

      <footer>
        <span>Blog Lab</span><p>Preprost prostor za dobre zgodbe.</p><span>Testna različica</span>
      </footer>
    </main>
  );
}
