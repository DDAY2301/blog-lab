# BlogLab – realne fotografije, avtorske pravice in Weekend (10. 11. 2026)

## Uredniška odločitev
Od tega PR dalje je v prenovljenem javnem `BlogLabMagazine` prednost dana pristnim fotografijam, ne AI-generiranim ali oljnim ilustracijam. Izvirna AB struktura strani in temnozelena/kremna paleta ostajata. Slika je vedno podrejena točnosti vsebine, ne obratno.

## Viri fotografij
- **Wikimedia Commons** je trenutno izbrani javni vir. Izbrane datoteke so ročno preverjene, z avtorjem, CC licenco, povezavo do datoteke in licenčnimi pogoji. Katalog: `src/bloglab-open-photos.js`.
- Publisher že vsebuje `agents/blog-lab-publisher/services/media_library.py`, ki uporablja Commons API in preverja licenco/prostorsko ustreznost. Nova javna komponenta sedaj spoštuje preverjen `heroImage` ter uporablja kurirane fotografije kot ustrezen nadomestni izbor.
- Brez dokazanega vira/licence fotografije **ne smemo uporabiti**. Fotografije iz Google Images, družbenih omrežij, Ticketmasterja ali promotorskih plakatov niso samodejno proste.
- Unsplash/Pexels sta možna kasnejša ponudnika, vendar uporaba njihovih API-jev zahteva spoštovanje posameznih API pravil; nobenih obvodov, nepreverjenih hotlinkov ali lažne navedbe licence.
- V foto opisu označimo ilustrativni/arhivski značaj. Brez navedbe, da je posnetek nastal na konkretni zabavi ali ob aktualnem dogodku.
- CC BY: avtor, vir, licenca in povezava. CC BY-SA: tudi obdelave naj spoštujejo zahtevo share-alike in označevanje sprememb. Licence ponovno preveriti ob dodajanju novih fotografij.
- Če za konkreten dogodek / lokacijo ni preverjene fotografije, prikaži nevtralno ozadje in naslov, ne izmisli si prizora.

## Weekend: nočno življenje, ne generični turizem
- Rubrika `Weekend` je usmerjena v **petek, soboto in nedeljo**; K4, Gala Hala, AKC Metelkova, Channel Zero, Gromka, Publika in primerljive prostore.
- Vir dogodka mora ostati dokazljiv: uradna stran organizatorja in datum, venue, start. Ločeno preveri status `confirmed`, `lastCheckedAt` in ustreznost koledarja; `feed.status=fresh` ni dokaz svežine vseh postavk.
- `src/bloglab-nightlife.js` filtrira samo potrjene klubske/glasbene dogodke na ustreznih prizoriščih, izključi delavnice in razstave in zgodnje jutranje ure pripne prejšnji noči. Ne doda izmišljenih dogodkov.
- Za ostale dogodke je še vedno na voljo celoten koledar; za posamezen Weekend večer brez potrjenih klubskih dogodkov se izpiše pošteno prazno stanje.

## Pred merge: kontrolni seznam
1. `node --test tools/tests/open-photos-weekend.test.mjs` PASS
2. `npm ci && npm run build` PASS
3. vizualni pregledi 360, 768, 1440px in delovanje /, rubrika, ?clanek, ?dogodek, ?dogodki
4. preveriti vse Wikimedia slike v dejanskem brskalniku in vidne licence
5. Weekend 13.–15. november (K4, Gala Hala, ostali) preveriti proti uradnim virom ter preprečiti zastarele dogodke
6. Publisher Agent, Health Check in Full E2E Audit brez regresije
7. Šele po testih odločitev za merge/produkcijsko objavo.

## Skill pack
V `.agents/skills/` je šest **projektno prilagojenih, skrajšanih** operativnih skill datotek iz priloženega paketa BlogLab Skill Pack v1.0. To ni bitno enaka kopija vseh evalvacij in master dokumentov ZIP; celotni ZIP ostane referenca. Ni samodejnega nameščanja v lokalne uporabniške agente in ni spremenjen `AGENTS.md`.
