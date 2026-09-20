"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import LivePulse from "./LivePulse";
import {
  ArticleGallery,
  ArticleHero,
  ArticleSources,
  ArticleVideo,
  InlineArticleMedia,
  MediaEditorFields,
  isInlineMediaLine,
  normalizeArticleMedia
} from "./ArticleMedia";

const TERMINAL_URL = "https://blog-lab.dan-grmusa.workers.dev/";
const CATEGORIES = ["Šport", "Politika", "Aktualno", "Novice", "Projekti", "Mnenja", "Vodniki", "Drugo"];

const starterArticles = [
  {
    "id": "nocno-zivljenje-v-ljubljani-1ae9f6e3",
    "title": "Nočno življenje v Ljubljani",
    "excerpt": "Ljubljana ponuja bogato nočno življenje, od barov do klubov.",
    "seoDescription": "Ljubljana ima živahno nočno življenje, ki ponuja različne možnosti zabave.",
    "content": "Ljubljana, prestolnica Slovenije, je mesto z bogatim nočnim življenjem. Od barov do klubov, mesto ponuja različne možnosti zabave za vse okuse. \n## Nočni klubi in bari \nLjubljana ima številne nočne klube in bare, ki so odprti do zgodnjih ur zjutraj. Nekateri od najbolj priljubljenih klubov so tisti, ki gostijo žive glasbene izvedbe, medtem ko drugi ponujajo DJ-je in plesne zabave. \n## Zabava za vse \nNe glede na to, ali ste fan glasbe, plesa ali samo želite uživati v dobrim času, Ljubljana ima nekaj za vsakogar. Mesto ponuja tudi številne restavracije in kavarnice, ki so odprte do pozno v noč, zato lahko uživate v dobri hrani in pitju, medtem ko se zabavate. \n## Študentska scenа \nLjubljana ima tudi živahno študentsko sceno, saj je mesto dom številnim univerzam in fakultetam. Študentje pogosto organizirajo zabave in dogodke, ki so odprti za javnost, zato je mesto zmeraj polno življenja in energije. \nLjubljanski študentje so tudi pozivali k ponovni uvedbi nočnih avtobusnih linij, ki bi jim omogočila lažje gibanje po mestu v nočnem času. \n## Zaključek \nLjubljana je mesto, ki ponuja nekaj za vsakogar, tudi v nočnem času. Od barov do klubov, restavracij in kavarnic, mesto je polno možnosti za zabavo in sprostitev. Če ste v Ljubljani, si lahko privoščite nočno življenje, ki ga mesto ponuja.",
    "category": "aktualno",
    "author": "Blog Lab Publisher",
    "status": "published",
    "heroImage": null,
    "video": null,
    "gallery": [],
    "sources": [
      {
        "label": "Ljubljanainfo.com",
        "url": "https://news.google.com/rss/articles/CBMivwFBVV95cUxPb3lEZ2VjbkFpa2R5ejU1YVVBQ09qbzZaT3RZNE9uRkxDaUFxVjVNM2hGdzNSRGxPOC13MG5jalhwZWgtTlFNU1dMcnVXUkZBTTM3c1ozWkQ4SXVCelh3Z3J1TUtfVGxGSXBlLTRFb0FUNnp1cW1rdmd2dVJidEstQ3ZYT1JMelk4dkVRRmVJTE1sQ3IzSktIelVhTW5NalV4cTdUWEZoT1FhTDVBYTdWTXlROEhUYmotM3JwcG9pdw?oc=5"
      },
      {
        "label": "24ur.com",
        "url": "https://news.google.com/rss/articles/CBMi0AFBVV95cUxPV0dqdU9ISkVzbk9Na0d4a1FRcmktM015aVl6MG9UMmllZlZ0aklNNDIxMXMxbUY5QVFDSTdtM1ZqTE5ZT3Z3WFZmR0thWGlFWmdvQkJ0Q2pyYmF4Y0J4WUpPeWxoNG0tN1BwMWtDeV9UdG1sRjNld1VrOEtSRjA2M243NVhXcl91U2dVc0xBelJzUWdVU1lEMV9ocmpUamNBS3VHSzhOQjNhWWxuQ3RZMEs5eDd3Y1dfcVFoTDRGeFZrckZ4bDhnYmFZSzJaWHIy?oc=5"
      }
    ],
    "createdAt": "2026-09-20T09:06:41+02:00",
    "updatedAt": "2026-09-20T09:06:41+02:00"
  },

  {
    "id": "drava-cycle-route-maribor-ptuj-guide",
    "title": "Cycling the Drava: A Car-Light Maribor–Ptuj Guide",
    "excerpt": "Ride the official 30 km Drava Bike stage from Maribor to Ptuj, with route choices, current-condition checks, safer planning and a carefully verified train-return strategy.",
    "seoDescription": "Plan the 30 km Drava cycle route from Maribor to Ptuj: official route options, bike and weather checks, safety advice and a car-light train return.",
    "content": "The official Drava Bike route makes it possible to link two of eastern Slovenia’s most rewarding cities on a **30-kilometre cycling stage**. The route page lists two alternatives between Maribor and Ptuj—via **Starše** or **Duplek**—so this is not a single line that every rider should follow automatically.\n\nThis guide is for independent leisure cyclists who want a one-way ride and a possible rail return. It is not a promise of a traffic-free path: expect a mixture of cycle infrastructure, local roads and changing surfaces, and make the current official map your source of truth.\n\n## Choose the official route before you start\n\nThe Slovenian and Croatian section of Drava Bike is divided into six marked stages. Maribor–Ptuj is stage 3, listed as:\n\n1. **Via Starše — 30 km**\n2. **Via Duplek — 30 km**\n\n### Via Starše or via Duplek?\n\nBoth official alternatives are listed at 30 km, but equal distance does not mean equal conditions. Compare the current map, surface information and any local warning before choosing; do not improvise a link between the branches.\n\nDownload or open the [official Drava Bike map](https://dravabike.si/en/) before departure. Do not choose a branch only because it looks shorter in a general navigation app. Temporary works, river conditions and local diversions can make a saved route outdated.\n\nThe official site displayed active warnings for other Drava Bike sections when checked on **20 September 2026**. That is a useful reminder to read the live warnings page even when your planned stage is not named in the alert.\n\n## What the ride is like\n\nThe broad direction follows the Drava east from Maribor towards Ptuj, but the ride is not a closed racing circuit. You may meet residents, farm vehicles, walkers and other cyclists. Slow down where sight lines narrow and follow road signs whenever the route joins public roads.\n\nThe official route describes the wider Drava Bike journey as suitable for families and leisure cyclists. That does not mean every rider, child or trailer will find every section easy. Fitness, traffic confidence, surface conditions and weather all matter.\n\nAllow generous time for stops rather than treating 30 km as a fixed schedule. Maribor and Ptuj both reward a slower visit, and an unhurried pace leaves room to turn back or change plans if conditions deteriorate.\n\n## Weather and seasonal planning\n\nThe Drava Bike page showed a warm forecast of roughly **12–28°C for 20 September 2026**, followed by cooler days. A website forecast is not a guarantee for the river corridor.\n\nCheck the [official ARSO forecast](https://meteo.arso.gov.si/met/en/) on the morning of the ride. Postpone the trip for thunderstorms, strong wind, flooding, poor visibility or any official warning. In early autumn, carry a light waterproof and an extra layer even when the afternoon looks warm.\n\nDaylight is shortening. Set a turnaround time and avoid relying on an unfamiliar river route after dark.\n\n## Bike, equipment and skills\n\nA serviced trekking, touring, gravel or suitable city bike is a sensible starting point. Before leaving, check brakes, tyres, chain and lights.\n\nCarry:\n\n- a helmet and high-visibility detail;\n- water and food;\n- a spare tube or repair kit, pump and basic tool;\n- a charged phone plus an offline copy of the official route;\n- identification, payment card and some cash;\n- a light waterproof layer and sun protection;\n- front and rear lights, even for a daytime plan.\n\nThe Slovenian route name is `Dravska kolesarska pot`. It can help when asking locally for directions, but route signs and the current official map take priority over informal advice.\n\n## A car-light plan\n\nMaribor and Ptuj both have railway stations. A train can make a one-way ride practical, but **bicycle carriage is not automatic on every service**.\n\nUse the [Slovenian Railways timetable](https://potniski.sz.si/en/) for the exact travel date and check that the chosen train accepts bicycles. Confirm available space, any bicycle supplement and current disruption notices. Rail-replacement buses may have different bicycle rules or no usable capacity.\n\nA robust plan is:\n\n1. Check the outbound and return timetable before leaving accommodation.\n2. Confirm bicycle carriage for the specific train, not just the route.\n3. Keep enough time to reach the station without rushing.\n4. Identify an earlier fallback service.\n5. Do not make the final train of the day your only rescue plan.\n\nIf you are uncertain about carriage conditions, ask Slovenian Railways before the ride or plan a return by bicycle only if your fitness, daylight and weather make the extra distance realistic.\n\n## Experiencing Maribor and Ptuj responsibly\n\nStart only after you have checked the bicycle, weather and route. In Maribor, use marked cycling infrastructure and ride slowly in shared pedestrian areas. In Ptuj, dismount where signs or crowded old-town spaces require it.\n\nVisit Ptuj’s official tourism site includes cycling and mobility information, while Visit Maribor provides destination planning for the starting city. Opening hours for attractions and food stops change seasonally, so verify them separately rather than assuming they match your cycling schedule.\n\nOn the route:\n\n- keep right and signal turns;\n- give pedestrians space and use a bell early, not aggressively;\n- close any gate you legitimately pass through;\n- do not enter fields, riverbanks or construction areas to shortcut;\n- take litter with you;\n- respect wildlife and avoid loud music;\n- never ride through a signed closure.\n\n## Direct sources and last check\n\nInformation was checked on **20 September 2026**:\n\n- [Drava Bike — official route, stages, map, warnings and transport](https://dravabike.si/en/)\n- [Visit Maribor — official destination information](https://www.visitmaribor.si/en/)\n- [Visit Ptuj — cycling, mobility and destination information](https://visitptuj.eu/en/)\n- [Slovenian Railways — live timetable and passenger notices](https://potniski.sz.si/en/)\n- [ARSO — official Slovenian weather service](https://meteo.arso.gov.si/met/en/)\n\nRecheck the official route warnings, weather and exact train service immediately before departure.",
    "category": "Šport",
    "author": "Uredništvo Blog Lab",
    "status": "published",
    "heroImage": null,
    "video": null,
    "gallery": [],
    "sources": [
      {
        "label": "Drava Bike — Official route and stage map",
        "url": "https://dravabike.si/en/"
      },
      {
        "label": "Visit Maribor — Official destination information",
        "url": "https://www.visitmaribor.si/en/"
      },
      {
        "label": "Visit Ptuj — Cycling and mobility information",
        "url": "https://visitptuj.eu/en/"
      },
      {
        "label": "Slovenian Railways — Timetable and passenger notices",
        "url": "https://potniski.sz.si/en/"
      },
      {
        "label": "ARSO — Official weather service",
        "url": "https://meteo.arso.gov.si/met/en/"
      }
    ],
    "createdAt": "2026-09-20T09:02:24+02:00",
    "updatedAt": "2026-09-20T09:02:24+02:00"
  },
  {
    "id": "rakov-skocjan-hiking-guide",
    "title": "Rakov Škocjan: A Safety-First Hiking Guide to Slovenia’s Natural Bridges",
    "excerpt": "Walk a five-kilometre karst trail between Rakov Škocjan’s natural bridges, with current logging warnings, responsible-visit rules and transport advice from Ljubljana.",
    "seoDescription": "Plan a Rakov Škocjan hike: 5 km trail, natural bridges, access from Ljubljana, current 2026 logging warning, safety and responsible visitor advice.",
    "content": "Rakov Škocjan is a forested karst valley between Cerknica and Planina where the Rak stream appears, disappears and passes beneath two natural stone bridges. For visitors based in Ljubljana, it offers a quieter nature trip than Slovenia’s best-known alpine destinations—but it still requires preparation.\n\nThe official **Rakov Škocjan Educational Trail** is approximately **5 kilometres** long and mostly lies between 500 and 600 metres above sea level. Its information boards explain how a former cave ceiling collapsed, leaving the Big and Small Natural Bridges.\n\n## Important current warning\n\n**Checked on 20 September 2026:** the Slovenian Forest Service and Notranjska Regional Park report tree felling and timber removal at individual points beside the road and educational trail from **15 September to 31 December 2026**.\n\nDo not enter an active work area. Follow temporary signs and workers’ instructions, expect short interruptions, and turn back if the safe route is unclear. Falling trees, branches and forestry machinery are not hazards to walk around for a photograph.\n\nThe Cerknica-area forecast checked for 20 September indicated increasing cloud, with temperatures around 11–25°C. Conditions in the shaded valley can feel cooler and wetter. Recheck the [official ARSO forecast](https://meteo.arso.gov.si/met/en/) before departure.\n\n## What you will see\n\n### Big Natural Bridge\n\nThe western end of the valley is marked by the Big Natural Bridge, a surviving section of the former cave roof. View it only from maintained paths and designated viewpoints. Limestone edges can be slippery, especially after rain.\n\n### The Rak stream and valley floor\n\nThe Rak is supplied by underground karst water. Its level and visible course change with rainfall and wider water conditions, so photographs from another season may not match your visit. Flooded or muddy ground is a reason to alter the walk, not to force a crossing.\n\n### Church ruins and forest\n\nNear the trail are the remains of the Church of St Cantianus. The surrounding fir-and-beech forest is ecologically rich and particularly attractive in autumn. Leave plants, stones and archaeological remains in place.\n\n### Small Natural Bridge\n\nThe 42-metre-high Small Natural Bridge stands above the eastern cave system. Stay behind barriers and on the maintained route. Do not enter caves or scramble below the bridge when water, darkness, loose rock or official restrictions make access unsafe.\n\n## Route planning\n\nThe park publishes a downloadable GPX file and elevation profile for the five-kilometre educational trail. Download the official track before leaving mobile coverage, but treat signs and temporary forestry instructions as more authoritative than a saved route.\n\nAllow roughly **two to three hours** for a relaxed circuit with stops. This is a planning estimate, not an official walking time; mud, photography, children and work-area diversions can make the visit longer.\n\nA simple plan is:\n\n1. Begin at an authorised parking or access point.\n2. Follow the marked educational trail rather than informal shortcuts.\n3. Visit the natural bridges and interpretation points only where access remains open.\n4. Return by the marked route before dusk.\n\nAvoid combining the outing with unsupported cave exploration. A forest walk and a cave visit require different equipment, permissions and risk assessment.\n\n## Getting there from Ljubljana\n\nNotranjska Regional Park describes the wider area as about an hour’s drive from Ljubljana. Drivers should use official roads and designated parking only; motor vehicles are prohibited in the natural environment.\n\nFor a car-light journey, trains run towards **Rakek**, while buses connect Ljubljana with **Cerknica**. These services do not necessarily deliver you to the Rakov Škocjan trailhead. Check the live [Slovenian Railways timetable](https://potniski.sz.si/en/) or [Ljubljana Bus Station](https://www.ap-ljubljana.si/en/) and arrange the final connection in advance. Do not assume a taxi or local transfer will be waiting.\n\nIf public transport and the final transfer do not align, visit the Lake Cerknica Visitor Centre or choose an organised excursion instead of attempting a long roadside walk.\n\n## Equipment and suitability\n\nWear shoes with dependable grip. Carry water, a light waterproof layer, a charged phone, an offline map and basic first aid. In autumn, add warm clothing and a small light even for a daytime visit.\n\nThe route is mostly gentle in profile, but natural surfaces, roots, mud, steps and temporary forestry work can limit accessibility. Visitors using wheelchairs, pushchairs or mobility aids should contact the park before travelling for current, section-specific advice.\n\nChildren should remain close to an adult near water, cliffs, caves and work zones. Keep dogs on a leash to protect wildlife and other visitors.\n\n## Responsible behaviour\n\nRakov Škocjan is protected nature, not an adventure park.\n\n- Stay on marked and maintained trails.\n- Park only in designated areas.\n- Take all waste away.\n- Do not light fires or camp outside designated areas.\n- Keep noise low and do not disturb wildlife.\n- Do not pick plants or collect rocks.\n- Respect private property and temporary closures.\n- Never cross forestry barriers or approach working machinery.\n\nFor another water-shaped landscape nearby, read [Paddling Lake Cerknica: When the Disappearing Lake Allows It](?article=paddling-lake-cerknica-guide). If you prefer an alpine day trip, compare the conditions with [Hiking Velika Planina: A Responsible Day Trip from Ljubljana](?article=hiking-velika-planina-guide).\n\n## Sources and last update\n\nInformation was last checked on **20 September 2026**:\n\n- [Notranjska Regional Park: Rakov Škocjan Educational Trail](https://notranjski-park.si/en/activities/hiking/rakov-skocjan-educational-trail)\n- [Notranjska Regional Park: current tree-logging notice](https://notranjski-park.si/en/latest/news/tree-logging-in-rakov-skocjan)\n- [Notranjska Regional Park: how to reach the area](https://notranjski-park.si/en/plan-your-trip/how-to-reach-us)\n- [Notranjska Regional Park: rules of conduct](https://notranjski-park.si/en/plan-your-trip/rules-of-conduct)\n- [ARSO: official Slovenian weather service](https://meteo.arso.gov.si/met/en/)\n\nConditions, access and public transport can change. Check the park notice, weather and live timetable again on the day of travel.",
    "category": "Vodniki",
    "author": "Uredništvo Blog Lab",
    "status": "published",
    "heroImage": null,
    "video": null,
    "gallery": [],
    "sources": [
      {
        "label": "Notranjska Regional Park — Rakov Škocjan Educational Trail",
        "url": "https://notranjski-park.si/en/activities/hiking/rakov-skocjan-educational-trail"
      },
      {
        "label": "Notranjska Regional Park — Tree logging notice",
        "url": "https://notranjski-park.si/en/latest/news/tree-logging-in-rakov-skocjan"
      },
      {
        "label": "Notranjska Regional Park — How to reach us",
        "url": "https://notranjski-park.si/en/plan-your-trip/how-to-reach-us"
      },
      {
        "label": "Notranjska Regional Park — Rules of conduct",
        "url": "https://notranjski-park.si/en/plan-your-trip/rules-of-conduct"
      },
      {
        "label": "ARSO — Official weather service",
        "url": "https://meteo.arso.gov.si/met/en/"
      }
    ],
    "createdAt": "2026-09-20T08:59:45+02:00",
    "updatedAt": "2026-09-20T08:59:45+02:00"
  },
  {
    "id": "politicni-pregled-19-9-2026-81290509",
    "title": "Politični pregled: 19. 9. 2026",
    "excerpt": "Samodejni pregled najnovejših objav za področje politika, sestavljen iz javno dostopnih RSS virov in neposrednih povezav do izvirnikov.",
    "seoDescription": "Samodejni pregled najnovejših objav za področje politika, sestavljen iz javno dostopnih RSS virov in neposrednih povezav do izvirnikov.",
    "content": "Danes, 19. 9. 2026, Blog Lab povzema nove objave s področja **politika**. Pregled je sestavljen samo iz podatkov, ki so bili objavljeni v navedenih virih; kjer RSS ne vsebuje dovolj podrobnosti, dodatnih dejstev ne ugibamo.\n\nPri političnih temah je poudarek na nevtralnem povzemanju objavljenih informacij. Pregled ne podpira kandidatov, strank ali političnih odločitev in ne napoveduje volilnih izidov.\n\n## 1. Duh Alice Weidel že leta vlada Sloveniji - delo.si\n\nDuh Alice Weidel že leta vlada Sloveniji delo.si Objavljeno: Sat, 19 Sep 2026 03:00:00 GMT.\n\n[Odpri izvirni vir](https://news.google.com/rss/articles/CBMiggFBVV95cUxNcFExMExXZUJFTUx2eGZyeFJaVG1FRmpJMElZUnZHVlVjNWdSVjZEekc3T1ViX0ExQWtPbEhXY2tVZ0dNNm5oS1duUDdLSWNmREFpVXhGN28xR2x0eFUtbjM1MjRydVlBaC1tMWpvNDZZR3pUajlfVlNmZ3JpNWhVcHVR?oc=5)\n\n## 2. (VIDEO) Golob o Janševem načrtu glede javnega sektorja: \"To ni nobena politika ali taktika, to je navadna hinavščina\" - Večer\n\n(VIDEO) Golob o Janševem načrtu glede javnega sektorja: \"To ni nobena politika ali taktika, to je navadna hinavščina\" Večer Objavljeno: Fri, 18 Sep 2026 08:16:00 GMT.\n\n[Odpri izvirni vir](https://news.google.com/rss/articles/CBMisAFBVV95cUxPWHRvUU54alkwTzVoTFhxQ0JDbEEzYmdsWXAxZ0dPRDh5a1ppREtnVVhPQTU3R042OE9XbE9aYURLZE85M3F3ZjRwZU8tNm50NUpvME83ZERObVdnRUN2RHhhckc3LThaNmdxWUhVcmgzZVkyMTVKVFIxdEpFLTJFU1IwMTZfNnhRWHdSUENtVWxna19NM2ZYQ1VQb2JtcUlEYWwxMTBrbHlZcHd4VWVVLQ?oc=5)\n\n## 3. Ko se politiki izogibajo javne televizije: lastni kanali in manj neprijetnih vprašanj - Dnevnik\n\nKo se politiki izogibajo javne televizije: lastni kanali in manj neprijetnih vprašanj Dnevnik Objavljeno: Tue, 15 Sep 2026 22:06:10 GMT.\n\n[Odpri izvirni vir](https://news.google.com/rss/articles/CBMiowFBVV95cUxPaXJyNzZUYzdiVzA3S3Q5S1lpVzNYVHJXNkpJYmNQbEQzRlRCVVlabE8yajhUTFZkY0c0eERrdzBudTdVN2ZRdE1VOHlPY0x2NEtmem1uQTUxdFhsSUxqaHFKVUFPR2ZfX1ZqWGxKOUFLelRaVnNsVmJEejZWX2VqM2o0ZVU5TWJIWVBkSnNZc2Z3ek0wZTRjSnU2VnpXYzg4Y1FF?oc=5)\n\n## 4. (INTERVJU) Tone Kajzer za Demokracijo: Slovenije ne prodajamo nikomur! - Najdi.si novice\n\n(INTERVJU) Tone Kajzer za Demokracijo: Slovenije ne prodajamo nikomur! Najdi.si novice Objavljeno: Sat, 19 Sep 2026 13:37:15 GMT.\n\n[Odpri izvirni vir](https://news.google.com/rss/articles/CBMi2gFBVV95cUxNUEI0MzdyeGVMN1lxYmJkUlF3WXVWcmhoRkQ1TXJHMy1aQzZxTmdDZTMtVmc1MGUycDJreHg2ZENOR0xwMVdTeG9wY21ocUpma0Z6T3U4MXlhODFVLXJoUVRpd1ByX0N4SEZPNGh1STJYY3NqNjk1bndaQ3l6ajc0WXhxQTB4VHdVQ2JUY09PbmlfNU5FMlJKLUZOM01kOVEtNTdWM2RPcjdwd3BrYnJtalloR3FFQkJWN29jenBzTGhMZVVadW01M0VscXJ4a3JmY3gyUjZSR1ROdw?oc=5)\n\n## 5. Bodo zaradi politične agende uprave in Sveta zaposleni na RTV ostali brez plač? - Info360\n\nBodo zaradi politične agende uprave in Sveta zaposleni na RTV ostali brez plač? Info360 Objavljeno: Thu, 17 Sep 2026 03:05:28 GMT.\n\n[Odpri izvirni vir](https://news.google.com/rss/articles/CBMiqwFBVV95cUxPaWdPY25ZWWJncUFsWDMtRjVEdlpEWW4zWW9OTGNYQmx2X3pDRWdNUWFVbi1zWXNab1dJRzhmVmR2OFNqaXBYZWE3TzY3V0pJVWphdW53VGFVZ1VqLUFfNlpMMktDM0pTM1lsajJDOW1rMXZXNnplOFM1WnFCcEJENm45cllNeDNmdEt0Q0hLc3ZLWHBwZ29kRWMtM1RheExyX0JLeHVhRElkejQ?oc=5)\n\n## Kaj spremljati naprej\n\nKer se aktualne zgodbe hitro dopolnjujejo, je smiselno preveriti izvirne povezave za morebitne nove podatke, popravke ali odzive. Blog Lab bo naslednji pregled pripravil šele, ko zazna nove, še neobdelane vnose.",
    "category": "Politika",
    "author": "Blog Lab Publisher",
    "status": "published",
    "heroImage": null,
    "video": null,
    "gallery": [],
    "sources": [
      {
        "label": "Google News Slovenija – politika — Duh Alice Weidel že leta vlada Sloveniji - delo.si",
        "url": "https://news.google.com/rss/articles/CBMiggFBVV95cUxNcFExMExXZUJFTUx2eGZyeFJaVG1FRmpJMElZUnZHVlVjNWdSVjZEekc3T1ViX0ExQWtPbEhXY2tVZ0dNNm5oS1duUDdLSWNmREFpVXhGN28xR2x0eFUtbjM1MjRydVlBaC1tMWpvNDZZR3pUajlfVlNmZ3JpNWhVcHVR?oc=5"
      },
      {
        "label": "Google News Slovenija – politika — (VIDEO) Golob o Janševem načrtu glede javnega sektorja: \"To ni nobena politika ali taktika, to je navadna hinavščina\"…",
        "url": "https://news.google.com/rss/articles/CBMisAFBVV95cUxPWHRvUU54alkwTzVoTFhxQ0JDbEEzYmdsWXAxZ0dPRDh5a1ppREtnVVhPQTU3R042OE9XbE9aYURLZE85M3F3ZjRwZU8tNm50NUpvME83ZERObVdnRUN2RHhhckc3LThaNmdxWUhVcmgzZVkyMTVKVFIxdEpFLTJFU1IwMTZfNnhRWHdSUENtVWxna19NM2ZYQ1VQb2JtcUlEYWwxMTBrbHlZcHd4VWVVLQ?oc=5"
      },
      {
        "label": "Google News Slovenija – politika — Ko se politiki izogibajo javne televizije: lastni kanali in manj neprijetnih vprašanj - Dnevnik",
        "url": "https://news.google.com/rss/articles/CBMiowFBVV95cUxPaXJyNzZUYzdiVzA3S3Q5S1lpVzNYVHJXNkpJYmNQbEQzRlRCVVlabE8yajhUTFZkY0c0eERrdzBudTdVN2ZRdE1VOHlPY0x2NEtmem1uQTUxdFhsSUxqaHFKVUFPR2ZfX1ZqWGxKOUFLelRaVnNsVmJEejZWX2VqM2o0ZVU5TWJIWVBkSnNZc2Z3ek0wZTRjSnU2VnpXYzg4Y1FF?oc=5"
      },
      {
        "label": "Google News Slovenija – politika — (INTERVJU) Tone Kajzer za Demokracijo: Slovenije ne prodajamo nikomur! - Najdi.si novice",
        "url": "https://news.google.com/rss/articles/CBMi2gFBVV95cUxNUEI0MzdyeGVMN1lxYmJkUlF3WXVWcmhoRkQ1TXJHMy1aQzZxTmdDZTMtVmc1MGUycDJreHg2ZENOR0xwMVdTeG9wY21ocUpma0Z6T3U4MXlhODFVLXJoUVRpd1ByX0N4SEZPNGh1STJYY3NqNjk1bndaQ3l6ajc0WXhxQTB4VHdVQ2JUY09PbmlfNU5FMlJKLUZOM01kOVEtNTdWM2RPcjdwd3BrYnJtalloR3FFQkJWN29jenBzTGhMZVVadW01M0VscXJ4a3JmY3gyUjZSR1ROdw?oc=5"
      },
      {
        "label": "Google News Slovenija – politika — Bodo zaradi politične agende uprave in Sveta zaposleni na RTV ostali brez plač? - Info360",
        "url": "https://news.google.com/rss/articles/CBMiqwFBVV95cUxPaWdPY25ZWWJncUFsWDMtRjVEdlpEWW4zWW9OTGNYQmx2X3pDRWdNUWFVbi1zWXNab1dJRzhmVmR2OFNqaXBYZWE3TzY3V0pJVWphdW53VGFVZ1VqLUFfNlpMMktDM0pTM1lsajJDOW1rMXZXNnplOFM1WnFCcEJENm45cllNeDNmdEt0Q0hLc3ZLWHBwZ29kRWMtM1RheExyX0JLeHVhRElkejQ?oc=5"
      }
    ],
    "createdAt": "2026-09-19T16:34:25+02:00",
    "updatedAt": "2026-09-19T16:34:25+02:00"
  },

  {
    "id": "franja-partisan-hospital-history-guide",
    "title": "Franja Partisan Hospital: History, Humanity and a Closed-Site Guide",
    "excerpt": "Understand the wartime hospital hidden in Pasica Gorge, why its humanitarian legacy matters, and how to plan a responsible visit while the site remains closed.",
    "seoDescription": "Explore the verified history of Franja Partisan Hospital near Cerkno, its European heritage significance and responsible alternatives while the site is closed.",
    "content": "Franja Partisan Hospital is remembered not because war made the Pasica Gorge picturesque, but because medical staff, resistance members and local people created a hidden place of care under extreme conditions. The site near Cerkno is a **monument of national importance** and a holder of the **European Heritage Label**.\n\nThe physical hospital is currently **closed because of storm damage**. Do not enter the gorge, bypass barriers or treat the closure as an invitation to explore independently. This guide explains the documented history and shows how to approach the story responsibly while access remains suspended.\n\n## What is documented history?\n\nAccording to the Idrija Municipal Museum, the hospital operated in the difficult-to-access Pasica Gorge at Dolenji Novaki during the Second World War. Fourteen wooden huts supported treatment and daily life, including wards, operating facilities, an X-ray facility, kitchen, storage, laundry, a power supply and shelters.\n\nThe museum records that **578 wounded people received shelter between 23 December 1943 and 5 May 1945**. The patients included people of different nationalities, Allied airmen and wounded soldiers from the opposing side.\n\nThe hospital took the name of physician **Franja Bojc Bidovec**. Its history also includes founder and doctor Viktor Volčjak, other medical workers, orderlies, local helpers and patients whose individual experiences should not be reduced to a single heroic legend.\n\n## Why the story matters\n\nFranja is evidence of organisation, medical skill and solidarity under occupation. Its European Heritage Label recognises its contribution to a shared European history.\n\nThat recognition does not turn every wartime story into a simple moral tale. The hospital belonged to the partisan resistance environment, and its staff worked amid occupation, violence, secrecy and political conflict. A responsible visit holds two ideas together:\n\n- the historical setting was complex and traumatic;\n- saving wounded people, including individuals from different sides, carries a clear humanitarian meaning.\n\nThis distinction matters. **Humanity is the interpretation supported by the hospital's documented work; it is not permission to romanticise war.**\n\n## What visitors can see when the site reopens\n\nThe museum describes a cluster of reconstructed wooden huts compressed into the narrow gorge. Exhibits and interpretation connect the buildings with accounts of staff and patients.\n\nThe landscape is part of the experience, but it is also a source of risk. A steep gorge, water and storm damage require managed access. Only use the official entrance and follow museum instructions after a formal reopening. The Slovenian name on signs is `Partizanska bolnica Franja`.\n\n## How to experience the history while Franja is closed\n\n1. Check the [Idrija Municipal Museum homepage](https://www.muzej-idrija-cerkno.si/en/) immediately before travelling. On 19 September 2026 it clearly stated that Franja was closed because of storm damage.\n2. Visit **Cerkno Museum** instead. It is managed by the same institution and provides essential regional context.\n3. Use the museum's published materials to learn about the people behind the hospital rather than approaching the closed gorge.\n4. Plan transport to Cerkno in advance. Rural services and seasonal timetables can change, so confirm the complete return journey before departure.\n5. If Franja reopens, verify opening hours, ticket arrangements, path conditions and accessibility directly with the museum.\n\nThe museum listed Cerkno Museum hours as **Tuesday–Friday 09:00–15:00** and **Saturday, Sunday and holidays 10:00–17:00**, with Monday closed, when checked on 19 September 2026. These hours can change.\n\n## Accessibility and responsible behaviour\n\nThe original setting is a narrow natural gorge, so visitors with reduced mobility should not assume step-free access. Contact the museum before planning a future visit and ask about the actual condition of the path.\n\nAt every memorial site:\n\n- respect closures and barriers;\n- keep noise low and do not stage playful photographs in treatment or memorial spaces;\n- do not remove natural or historical material;\n- distinguish museum evidence from family stories, rumours and later political interpretations;\n- supervise children near water, rock and steep paths.\n\n## Direct sources\n\n- [Idrija Municipal Museum — current opening information and closure notice](https://www.muzej-idrija-cerkno.si/en/)\n- [Idrija Municipal Museum — Franja history and heritage significance](https://www.muzej-idrija-cerkno.si/en/obiscite-nas/top-10-zanimivosti/?zanimivost=6011)\n- [Idrija Municipal Museum — visit planning](https://www.muzej-idrija-cerkno.si/en/obiscite-nas/)\n\nSources and closure status were checked on **19 September 2026**. The closure is time-sensitive: rely on the museum's current notice, not an older travel article or map listing.",
    "category": "Vodniki",
    "author": "Uredništvo Blog Lab",
    "status": "published",
    "heroImage": null,
    "video": null,
    "gallery": [],
    "sources": [
      {
        "label": "Idrija Municipal Museum — current opening information and closure notice",
        "url": "https://www.muzej-idrija-cerkno.si/en/"
      },
      {
        "label": "Idrija Municipal Museum — Franja history and heritage significance",
        "url": "https://www.muzej-idrija-cerkno.si/en/obiscite-nas/top-10-zanimivosti/?zanimivost=6011"
      },
      {
        "label": "Idrija Municipal Museum — visit planning",
        "url": "https://www.muzej-idrija-cerkno.si/en/obiscite-nas/"
      }
    ],
    "createdAt": "2026-09-19T14:58:52+02:00",
    "updatedAt": "2026-09-19T14:58:52+02:00"
  },

  {
    "id": "sportni-pregled-19-9-2026-8a936707",
    "title": "Športni pregled: 19. 9. 2026",
    "excerpt": "Samodejni pregled najnovejših objav za področje šport, sestavljen iz javno dostopnih RSS virov in neposrednih povezav do izvirnikov.",
    "seoDescription": "Samodejni pregled najnovejših objav za področje šport, sestavljen iz javno dostopnih RSS virov in neposrednih povezav do izvirnikov.",
    "content": "Danes, 19. 9. 2026, Blog Lab povzema nove objave s področja **šport**. Pregled je sestavljen samo iz podatkov, ki so bili objavljeni v navedenih virih; kjer RSS ne vsebuje dovolj podrobnosti, dodatnih dejstev ne ugibamo.\n\n## 1. Slovenija po prvem dnevu proti Izraelu vodi z 2:0 - rtvslo.si\n\nSlovenija po prvem dnevu proti Izraelu vodi z 2:0 rtvslo.si Objavljeno: Fri, 18 Sep 2026 15:36:40 GMT.\n\n[Odpri izvirni vir](https://news.google.com/rss/articles/CBMijAFBVV95cUxQMjhOZkZFalFuTzliUVQ2TVZqZVVHYjM4dHlTRWVKUEZXSjBNZkEzbTlkTUJMcDN5Y3JmU3FDMC1raG5MZ3h4VFNQVXpWU0hGbU9RTVdlaDhGOU9yaERfeVBtRDl0clpucFZsek96N1ByUHI4MGtMZTNyd0ZCNHFyNi1vQ2h3eXVFU253Rw?oc=5)\n\n## 2. Diši po kolajni: Slovenija stopnjuje formo, prihaja še Klemen Čebulj - Delo.si\n\nDiši po kolajni: Slovenija stopnjuje formo, prihaja še Klemen Čebulj Delo.si Objavljeno: Fri, 18 Sep 2026 10:00:00 GMT.\n\n[Odpri izvirni vir](https://news.google.com/rss/articles/CBMiqAFBVV95cUxQdjBESU52NlNxdkFGVUtzcDJGdzVzLTNldlhfY1lOc3lDbmxBVGdWZzZFb0djWEJfb2JDUThRbVVfWjh3Wm5WblpKREFrbE15YUxsaGN4UG14MDZsdTcyd2VfdTdyV3M4Vm0yV29TbUxJS2d1MG1Lc185NnpWYVR5QVJQaE5PazcxaHdEYUFGYng3TjRWSld3REs2V1A2Y3ZwNDFoeTZleHE?oc=5)\n\n## 3. O začetku Toura v Sloveniji - Janez Janša takole s šefom največje dirke - Ekipa\n\nO začetku Toura v Sloveniji - Janez Janša takole s šefom največje dirke Ekipa Objavljeno: Sat, 19 Sep 2026 05:26:00 GMT.\n\n[Odpri izvirni vir](https://news.google.com/rss/articles/CBMivAFBVV95cUxPUk9pZDBKY3NublNzb3JQOGswVDRYV3BPMnJ1UXVHT1NGU0RKQy0yMmo1Ni1vblhidi13N2traUYtZXdGaVE1VTkwSHFKa2ItQm92dW90Z2dBMVVHOEUzbVRLY0pnTlVjNHFEaDBPTE80eXNtcDFzWVlXSXhsNUJKTUJCTHJUeUVVc2tiZ1h5WnlydkZwS3A4RG82ZVRyYTdYamFtZUNHZDdvU01mNzAwM3dpZmIwRTFIYkhYdw?oc=5)\n\n## 4. Po Pogačarju Slovenija ostala tudi brez drugega velikega aduta, to je razlog - Žurnal24\n\nPo Pogačarju Slovenija ostala tudi brez drugega velikega aduta, to je razlog Žurnal24 Objavljeno: Sat, 19 Sep 2026 07:13:00 GMT.\n\n[Odpri izvirni vir](https://news.google.com/rss/articles/CBMiwgFBVV95cUxOQUdKSVYwbWNwRWpEdXk0OGlmN2NsSkdYT21TVWJpU3BmeDFwNnBXdjBsYS1oeTlXX1lfbm45cnZna2xjNDNuZnA4dEZSNWJrRlBrQW0wSTJpVlNnR0s4VTZtNWpQakEtQ1Q1Vl9IWnpHX01oY0RlNGFOdjVJbm5kLU5lOURCM1IwaUNkNi13X3lFS3F4X0RRWlUxT2NsaUZobmdYNl83d09feHo1bUowVUVaejZfZTh5ZHNyRzRNUktxUdIBtwFBVV95cUxOODFjb1VLSTlIRU43NHZyZkUwSUFYVWVnNVROeUwyQzQ0eVE0b2x6dk02WWduU1h6Vjc2T3Zlc3NzYkZPcDcwT1Zua1I0MWRlbVpsUDNCZ3pHV1BiTDAzTGV0VC1vOF9XUXVXam9aUDl6a0pkWEVmSDlMZnk2Y0gyLWVtam9HSzE3WVMyY1FjSzBGbkQzN3lYTlJrQTBhYTY2NV90bXNpZ0tacmVWcS1nX3lleDhSZjA?oc=5)\n\n## 5. \"Želja je, da se v prihodnjih letih prvi trije dnevi Toura odvijejo v Sloveniji\" - rtvslo.si\n\n\"Želja je, da se v prihodnjih letih prvi trije dnevi Toura odvijejo v Sloveniji\" rtvslo.si Objavljeno: Thu, 17 Sep 2026 20:03:34 GMT.\n\n[Odpri izvirni vir](https://news.google.com/rss/articles/CBMi2gFBVV95cUxNU2lPeFZJRm03ZXd4T1ZLbzU1c09HdTBYUWdCUGd3NWUybm1wS241SzVqN05kYTVOeF9XZEJZX1p1MnVwSW9ORGtQbGdBR0w0LVI5T1RyTjdxaUlnQ0pjUjRqNG9XZWw1Q2lnNXJJVHFQZGJCUUlNVGpQSlduZ3JQZmFjOUJEVHdTOUtFd25lVjU4OUh6cEFCSzF2a0s0YW9mbEpyS2xwdDZkU2hiajFwV05QQXRWRmw3cGowOGlocHRsdi1JbGxDY3h0OUdScU1WVGRDOTZBQWtXUQ?oc=5)\n\n## Kaj spremljati naprej\n\nKer se aktualne zgodbe hitro dopolnjujejo, je smiselno preveriti izvirne povezave za morebitne nove podatke, popravke ali odzive. Blog Lab bo naslednji pregled pripravil šele, ko zazna nove, še neobdelane vnose.",
    "category": "Šport",
    "author": "Blog Lab Publisher",
    "status": "published",
    "heroImage": null,
    "video": null,
    "gallery": [],
    "sources": [
      {
        "label": "Google News Slovenija – šport — Slovenija po prvem dnevu proti Izraelu vodi z 2:0 - rtvslo.si",
        "url": "https://news.google.com/rss/articles/CBMijAFBVV95cUxQMjhOZkZFalFuTzliUVQ2TVZqZVVHYjM4dHlTRWVKUEZXSjBNZkEzbTlkTUJMcDN5Y3JmU3FDMC1raG5MZ3h4VFNQVXpWU0hGbU9RTVdlaDhGOU9yaERfeVBtRDl0clpucFZsek96N1ByUHI4MGtMZTNyd0ZCNHFyNi1vQ2h3eXVFU253Rw?oc=5"
      },
      {
        "label": "Google News Slovenija – šport — Diši po kolajni: Slovenija stopnjuje formo, prihaja še Klemen Čebulj - Delo.si",
        "url": "https://news.google.com/rss/articles/CBMiqAFBVV95cUxQdjBESU52NlNxdkFGVUtzcDJGdzVzLTNldlhfY1lOc3lDbmxBVGdWZzZFb0djWEJfb2JDUThRbVVfWjh3Wm5WblpKREFrbE15YUxsaGN4UG14MDZsdTcyd2VfdTdyV3M4Vm0yV29TbUxJS2d1MG1Lc185NnpWYVR5QVJQaE5PazcxaHdEYUFGYng3TjRWSld3REs2V1A2Y3ZwNDFoeTZleHE?oc=5"
      },
      {
        "label": "Google News Slovenija – šport — O začetku Toura v Sloveniji - Janez Janša takole s šefom največje dirke - Ekipa",
        "url": "https://news.google.com/rss/articles/CBMivAFBVV95cUxPUk9pZDBKY3NublNzb3JQOGswVDRYV3BPMnJ1UXVHT1NGU0RKQy0yMmo1Ni1vblhidi13N2traUYtZXdGaVE1VTkwSHFKa2ItQm92dW90Z2dBMVVHOEUzbVRLY0pnTlVjNHFEaDBPTE80eXNtcDFzWVlXSXhsNUJKTUJCTHJUeUVVc2tiZ1h5WnlydkZwS3A4RG82ZVRyYTdYamFtZUNHZDdvU01mNzAwM3dpZmIwRTFIYkhYdw?oc=5"
      },
      {
        "label": "Google News Slovenija – šport — Po Pogačarju Slovenija ostala tudi brez drugega velikega aduta, to je razlog - Žurnal24",
        "url": "https://news.google.com/rss/articles/CBMiwgFBVV95cUxOQUdKSVYwbWNwRWpEdXk0OGlmN2NsSkdYT21TVWJpU3BmeDFwNnBXdjBsYS1oeTlXX1lfbm45cnZna2xjNDNuZnA4dEZSNWJrRlBrQW0wSTJpVlNnR0s4VTZtNWpQakEtQ1Q1Vl9IWnpHX01oY0RlNGFOdjVJbm5kLU5lOURCM1IwaUNkNi13X3lFS3F4X0RRWlUxT2NsaUZobmdYNl83d09feHo1bUowVUVaejZfZTh5ZHNyRzRNUktxUdIBtwFBVV95cUxOODFjb1VLSTlIRU43NHZyZkUwSUFYVWVnNVROeUwyQzQ0eVE0b2x6dk02WWduU1h6Vjc2T3Zlc3NzYkZPcDcwT1Zua1I0MWRlbVpsUDNCZ3pHV1BiTDAzTGV0VC1vOF9XUXVXam9aUDl6a0pkWEVmSDlMZnk2Y0gyLWVtam9HSzE3WVMyY1FjSzBGbkQzN3lYTlJrQTBhYTY2NV90bXNpZ0tacmVWcS1nX3lleDhSZjA?oc=5"
      },
      {
        "label": "Google News Slovenija – šport — \"Želja je, da se v prihodnjih letih prvi trije dnevi Toura odvijejo v Sloveniji\" - rtvslo.si",
        "url": "https://news.google.com/rss/articles/CBMi2gFBVV95cUxNU2lPeFZJRm03ZXd4T1ZLbzU1c09HdTBYUWdCUGd3NWUybm1wS241SzVqN05kYTVOeF9XZEJZX1p1MnVwSW9ORGtQbGdBR0w0LVI5T1RyTjdxaUlnQ0pjUjRqNG9XZWw1Q2lnNXJJVHFQZGJCUUlNVGpQSlduZ3JQZmFjOUJEVHdTOUtFd25lVjU4OUh6cEFCSzF2a0s0YW9mbEpyS2xwdDZkU2hiajFwV05QQXRWRmw3cGowOGlocHRsdi1JbGxDY3h0OUdScU1WVGRDOTZBQWtXUQ?oc=5"
      }
    ],
    "createdAt": "2026-09-19T13:05:14+02:00",
    "updatedAt": "2026-09-19T13:05:14+02:00"
  },

  {
    "id": "aktualni-pregled-19-9-2026-550bfe97",
    "title": "Aktualni pregled: 19. 9. 2026",
    "excerpt": "Samodejni pregled najnovejših objav za področje aktualno, sestavljen iz javno dostopnih RSS virov in neposrednih povezav do izvirnikov.",
    "seoDescription": "Samodejni pregled najnovejših objav za področje aktualno, sestavljen iz javno dostopnih RSS virov in neposrednih povezav do izvirnikov.",
    "content": "Danes, 19. 9. 2026, Blog Lab povzema nove objave s področja **aktualno**. Pregled je sestavljen samo iz podatkov, ki so bili objavljeni v navedenih virih; kjer RSS ne vsebuje dovolj podrobnosti, dodatnih dejstev ne ugibamo.\n\n## 1. Nisem taka, da bi delala nekaj na pol - Ekipa\n\nNisem taka, da bi delala nekaj na pol Ekipa Objavljeno: Fri, 18 Sep 2026 08:39:26 GMT.\n\n[Odpri izvirni vir](https://news.google.com/rss/articles/CBMimAFBVV95cUxOYm5kcXBRV2lZOU1vM3RJbXo1YlhTdU9CcFMwaWtheDhyY2lRVklReHd1SU44TWswR0E3eW9YWHZvQzFNSEVaMVVvX2JPcjNFZ3ozUG83NGlENGxDQ2NISnJIelYwdjBpQnQxYWJDd2h6NzhRV1JqbFgzMXgtejIzdlZJZ2c4ZWFsUjZzMDFlYXBMb2hMaWxSbw?oc=5)\n\n## 2. Skriti biser Slovenije, kjer so turisti našli svoj raj: »Boljše lokacije za družine še nismo videli« - Dnevnik\n\nSkriti biser Slovenije, kjer so turisti našli svoj raj: »Boljše lokacije za družine še nismo videli« Dnevnik Objavljeno: Wed, 26 Aug 2026 07:00:00 GMT.\n\n[Odpri izvirni vir](https://news.google.com/rss/articles/CBMipAFBVV95cUxOS2k1X3ZzUDBUNXJxSG5Xbkh5am9oSVVTRDVieG9hUUhENU5Sa19Rb0dGZE1BTVBoNzRmWlNCUTN1OHVka0FNZDE4NnZQY0RuUzhvZkdKNnZhZzZ6N3FrbVBCak9CTC1TVGxHN1IxdHplQ25DRFFTNUpYbHJYOHFiaXdxTDlFZUViLTJJZXd0bmpTS253c1F2MnJXQVVSZU9IbjlUZA?oc=5)\n\n## 3. National Geographic: Pridite do Bleda, potem pa vozite naprej! - Žurnal24\n\nNational Geographic: Pridite do Bleda, potem pa vozite naprej! Žurnal24 Objavljeno: Thu, 02 Jul 2026 07:00:00 GMT.\n\n[Odpri izvirni vir](https://news.google.com/rss/articles/CBMiogFBVV95cUxPRllORmhoamt6alBlX096MzN3TEhnejFXSFlBTFJPQmh6Ti1NWmdicndfYUJHLXZzZUZrLUo4UmI2SWhaT1libF9kcnRuT1lJOFFDbkF1amhkbFcwWnJ4cjBUZV83bWY2TDVwUlJhRnJPS3NUYi0tMjZEczk3V21RODdyTHRMSUtSRVZpOHI4dlpFY3d4ZFhxUXNxcy11ZUFEbGfSAacBQVVfeXFMTkdOcjJfUjZLYXJnVmJPSVVBSDJaLWhOZGNWd3FfWGZiVmRmVV93SWF1WVU0YmRSSVBOU01qekc3LXNwV3plMnBCcTlFdEtPWWhhdElWYXEwQ0d2MlN6QWNwUFc2bEh1MXlqclhvdzlfQWdSQnE3bk9TeTh4dFczbTdYN2VZVHVMRVNfYWlaeEpNT3FBRmQzckw4TkpkSmtsbzQ5LVVKOTg?oc=5)\n\n## 4. Če ti trg pove, da si zamočil, sprejmeš in greš naprej - Delo.si\n\nČe ti trg pove, da si zamočil, sprejmeš in greš naprej Delo.si Objavljeno: Thu, 11 Jun 2026 07:00:00 GMT.\n\n[Odpri izvirni vir](https://news.google.com/rss/articles/CBMilwFBVV95cUxOYWtDNm1KTnRGZ0xRRkRNbGtfbnpVMG4tamN1a3I4Y2NjRWExbWZTVG9YLXRQcVF1cHVleXRZNjJEQ2hwVEt0eG1RX1NGUXZZVUtzVEM2eEg4QkJ1dHdMQTJ0WFpnX1JjOXdZSmpZMWFLNXZvam1wLXl6VnIybWQzcy1FMkg5ZEFVUmVQYkh3Y25JZkZDaEVV?oc=5)\n\n## 5. Veselje na OŠ Malečnik: Naprej o palačinkah zapeli, potem pa jih v novi kuhinji tudi pripravili (FOTO) - Maribor24.si\n\nVeselje na OŠ Malečnik: Naprej o palačinkah zapeli, potem pa jih v novi kuhinji tudi pripravili (FOTO) Maribor24.si Objavljeno: Mon, 17 Nov 2025 08:00:00 GMT.\n\n[Odpri izvirni vir](https://news.google.com/rss/articles/CBMi0gFBVV95cUxNQlI3bXM2TzJZSHlsZ2dvYlJPeWYxN1kyaVA4cERpc2luN1JRd05LWXQ2M2dCTHNDVERlQ3Y5TEVUNUltWnFCX0ZxSUtpYVBXS3M3WmJ4TEJROC0xQTRHZmMtSHhDSlBDMXVXeVFpZVVSNFdJZmxuRGtmNGw5WjJXZTU4aXkwTHlWamVmMmdhOXRDVlZjLV9tQ0FFQ196eHV3Wm9NX3FZVFF6dlNNWW9Wa0Nib284bFprMzdsZXNRS2ZFZG1PZnRBNngtd2E5WmhId0E?oc=5)\n\n## Kaj spremljati naprej\n\nKer se aktualne zgodbe hitro dopolnjujejo, je smiselno preveriti izvirne povezave za morebitne nove podatke, popravke ali odzive. Blog Lab bo naslednji pregled pripravil šele, ko zazna nove, še neobdelane vnose.",
    "category": "Aktualno",
    "author": "Blog Lab Publisher",
    "status": "published",
    "heroImage": null,
    "video": null,
    "gallery": [],
    "sources": [
      {
        "label": "Google News – aktualno – potem naprej — Nisem taka, da bi delala nekaj na pol - Ekipa",
        "url": "https://news.google.com/rss/articles/CBMimAFBVV95cUxOYm5kcXBRV2lZOU1vM3RJbXo1YlhTdU9CcFMwaWtheDhyY2lRVklReHd1SU44TWswR0E3eW9YWHZvQzFNSEVaMVVvX2JPcjNFZ3ozUG83NGlENGxDQ2NISnJIelYwdjBpQnQxYWJDd2h6NzhRV1JqbFgzMXgtejIzdlZJZ2c4ZWFsUjZzMDFlYXBMb2hMaWxSbw?oc=5"
      },
      {
        "label": "Google News – aktualno – potem naprej — Skriti biser Slovenije, kjer so turisti našli svoj raj: »Boljše lokacije za družine še nismo videli« - Dnevnik",
        "url": "https://news.google.com/rss/articles/CBMipAFBVV95cUxOS2k1X3ZzUDBUNXJxSG5Xbkh5am9oSVVTRDVieG9hUUhENU5Sa19Rb0dGZE1BTVBoNzRmWlNCUTN1OHVka0FNZDE4NnZQY0RuUzhvZkdKNnZhZzZ6N3FrbVBCak9CTC1TVGxHN1IxdHplQ25DRFFTNUpYbHJYOHFiaXdxTDlFZUViLTJJZXd0bmpTS253c1F2MnJXQVVSZU9IbjlUZA?oc=5"
      },
      {
        "label": "Google News – aktualno – potem naprej — National Geographic: Pridite do Bleda, potem pa vozite naprej! - Žurnal24",
        "url": "https://news.google.com/rss/articles/CBMiogFBVV95cUxPRllORmhoamt6alBlX096MzN3TEhnejFXSFlBTFJPQmh6Ti1NWmdicndfYUJHLXZzZUZrLUo4UmI2SWhaT1libF9kcnRuT1lJOFFDbkF1amhkbFcwWnJ4cjBUZV83bWY2TDVwUlJhRnJPS3NUYi0tMjZEczk3V21RODdyTHRMSUtSRVZpOHI4dlpFY3d4ZFhxUXNxcy11ZUFEbGfSAacBQVVfeXFMTkdOcjJfUjZLYXJnVmJPSVVBSDJaLWhOZGNWd3FfWGZiVmRmVV93SWF1WVU0YmRSSVBOU01qekc3LXNwV3plMnBCcTlFdEtPWWhhdElWYXEwQ0d2MlN6QWNwUFc2bEh1MXlqclhvdzlfQWdSQnE3bk9TeTh4dFczbTdYN2VZVHVMRVNfYWlaeEpNT3FBRmQzckw4TkpkSmtsbzQ5LVVKOTg?oc=5"
      },
      {
        "label": "Google News – aktualno – potem naprej — Če ti trg pove, da si zamočil, sprejmeš in greš naprej - Delo.si",
        "url": "https://news.google.com/rss/articles/CBMilwFBVV95cUxOYWtDNm1KTnRGZ0xRRkRNbGtfbnpVMG4tamN1a3I4Y2NjRWExbWZTVG9YLXRQcVF1cHVleXRZNjJEQ2hwVEt0eG1RX1NGUXZZVUtzVEM2eEg4QkJ1dHdMQTJ0WFpnX1JjOXdZSmpZMWFLNXZvam1wLXl6VnIybWQzcy1FMkg5ZEFVUmVQYkh3Y25JZkZDaEVV?oc=5"
      },
      {
        "label": "Google News – aktualno – potem naprej — Veselje na OŠ Malečnik: Naprej o palačinkah zapeli, potem pa jih v novi kuhinji tudi pripravili (FOTO) - Maribor24.si",
        "url": "https://news.google.com/rss/articles/CBMi0gFBVV95cUxNQlI3bXM2TzJZSHlsZ2dvYlJPeWYxN1kyaVA4cERpc2luN1JRd05LWXQ2M2dCTHNDVERlQ3Y5TEVUNUltWnFCX0ZxSUtpYVBXS3M3WmJ4TEJROC0xQTRHZmMtSHhDSlBDMXVXeVFpZVVSNFdJZmxuRGtmNGw5WjJXZTU4aXkwTHlWamVmMmdhOXRDVlZjLV9tQ0FFQ196eHV3Wm9NX3FZVFF6dlNNWW9Wa0Nib284bFprMzdsZXNRS2ZFZG1PZnRBNngtd2E5WmhId0E?oc=5"
      }
    ],
    "createdAt": "2026-09-19T12:05:31+02:00",
    "updatedAt": "2026-09-19T12:05:31+02:00"
  },

  {
    "id": "cycling-ljubljana-city-guide",
    "title": "Cycling Ljubljana: A Safe City Guide for Visitors",
    "excerpt": "Explore Ljubljana by bike with a practical beginner route, BicikeLJ advice, wet-weather precautions and simple rules for sharing streets and pedestrian areas.",
    "seoDescription": "Cycle Ljubljana safely: a beginner-friendly city route, BicikeLJ tips, traffic rules, weather checks and practical advice for international visitors.",
    "content": "Ljubljana is compact enough to explore on foot, yet a bicycle makes it easier to connect the historic centre with Tivoli Park, Špica and greener neighbourhoods. The best first ride is not a race through the old town: it is a flexible, low-stress circuit that uses marked cycle infrastructure and leaves time to walk the bike in busy pedestrian areas.\n\nThis guide is for visitors who are comfortable balancing, braking and signalling on an ordinary city bicycle. It is not a mountain-bike route or a substitute for a guided lesson.\n\n## Is today suitable for cycling?\n\nThe forecast checked on **19 September 2026** indicated variable cloud with possible showers, especially earlier in the day, and a daytime high around 22°C in Ljubljana. Conditions can change locally. Check the current [ARSO weather forecast](https://meteo.arso.gov.si/met/en/) immediately before setting out and postpone the ride if thunder is nearby, visibility is poor or surfaces are unsafe.\n\nAfter rain, expect slippery leaves, polished paving stones, painted road markings and bridge surfaces. Brake earlier, corner gently and leave more stopping distance. A bright layer and working lights improve visibility even during daytime showers.\n\n## Renting a bike: BicikeLJ or a conventional rental?\n\n[BicikeLJ](https://www.bicikelj.si/en/home) is Ljubljana's public bike-sharing system. Its official app shows stations and bicycle availability and offers short-term and annual subscription options. The provider currently states that the first 60 minutes of each individual journey are included, but fees and conditions can change.\n\nBefore releasing a bike:\n\n- read the current subscription and payment terms;\n- inspect both brakes, tyres, saddle and lights;\n- choose another bicycle if anything feels unsafe;\n- plan a station near your destination;\n- after returning the bike, confirm in the app that the rental has actually ended.\n\nBike sharing works best for short urban hops. For a longer continuous ride, a child seat, specialist sizing or guaranteed equipment, use a staffed rental shop and ask what is included. Do not assume that a shared bicycle comes with a helmet or other accessories.\n\n## A beginner-friendly Ljubljana cycling circuit\n\nThis is a suggested sequence of areas, not a turn-by-turn navigation track. Temporary works and traffic arrangements can change, so follow current signs and use a reliable cycling map.\n\n### 1. Start beside Tivoli Park\n\nBegin near a BicikeLJ station or rental point on the city-centre side of Tivoli. Use marked cycle paths around the park and respect any signs that restrict riding on particular walking paths. Tivoli is a good place to test the brakes and saddle before entering busier streets.\n\n### 2. Continue towards the city centre\n\nFollow signed cycle infrastructure rather than copying pedestrians or taking the shortest line on a phone map. Ljubljana's centre contains pedestrian and shared spaces; where cycling is prohibited, crowded or uncomfortable, dismount and walk. Give pedestrians plenty of room and never weave through a group.\n\nIf you would rather discover the architecture slowly on foot, save the central section for the [self-guided Plečnik walking tour](?article=plecnik-ljubljana-self-guided-walking-tour).\n\n### 3. Follow the river towards Špica\n\nFrom the centre, use the permitted riverside connections towards Špica. The river makes orientation easy, but not every promenade is a cycle route. Obey local signs, reduce speed near cafés, bridges and playgrounds, and walk whenever the space becomes primarily pedestrian.\n\nŠpica is a sensible turnaround point for a short outing. Stronger riders can continue only on clearly permitted routes after checking the map and daylight.\n\n### 4. Return without rushing\n\nComplete the circuit on signed streets or cycle tracks and return the bicycle to an authorised station or rental shop. With stops, a relaxed city ride may take two to three hours, but distance and duration depend on detours, crowds and where you collect the bike.\n\nFor a longer coastal rail-trail rather than an urban outing, read the separate [Parenzana cycling guide](?article=cycling-the-parenzana-slovenia-guide).\n\n## Essential road rules and shared-space etiquette\n\nTreat the bicycle as a vehicle, not as a shortcut through any open-looking space.\n\n- Use cycle lanes and tracks where they are provided and follow traffic lights and signs.\n- Ride predictably, keep right where applicable and signal before turning.\n- Do not ride on an ordinary pavement unless signs permit cycling.\n- Slow down at crossings, driveways and bus stops; drivers and pedestrians may not have seen you.\n- Use lights in darkness and reduced visibility.\n- Do not hold a phone, wear headphones that block traffic or ride after drinking alcohol.\n- In shared or pedestrian zones, travel at a speed appropriate to the people around you and dismount when necessary.\n\nFor the legal wording and any temporary changes, consult the [Slovenian Police road-safety information](https://www.policija.si/eng/prevention/traffic-safety) and on-street signs.\n\n## Helmets, children and accessibility\n\nA helmet is a sensible choice for every rider even where the law may not require one for an adult. It must fit correctly and be replaced after a significant impact. Children need age-appropriate equipment, close supervision and a route chosen for their actual skills—not merely for its short distance.\n\nStandard public-share bicycles are not designed for every body or access need. Travellers who need an adapted cycle, handcycle, stable tricycle or other support should arrange equipment with a specialist provider before arrival and confirm surfaces, gradients and storage.\n\n## What to carry\n\nFor a short city ride, take:\n\n- water and a light waterproof layer;\n- a charged phone with an offline map;\n- identification and the rental contact details;\n- a small lock if supplied by the rental company;\n- sunscreen in clear weather;\n- a plan for returning the bicycle before the rental deadline.\n\nKeep valuables with you. Do not leave bags loose in a basket where they can affect steering or be easily taken.\n\n## When to choose another activity\n\nWalk or use public transport if thunderstorms are developing, roads are icy, heavy rain reduces visibility or you do not feel confident in unfamiliar traffic. A flexible plan is part of safe travel, not a missed opportunity.\n\nOn a dry day, Ljubljana rewards an unhurried rider: use the bicycle to connect neighbourhoods, then stop and explore each place at walking speed.\n\n## Sources and last check\n\nInformation and conditions were checked on **19 September 2026**:\n\n- [Ljubljana Tourism: Cycling](https://www.visitljubljana.com/en/visitors/sights-and-activities/active-holidays/cycling/)\n- [BicikeLJ: official service website](https://www.bicikelj.si/en/home)\n- [ARSO: official Slovenian weather service](https://meteo.arso.gov.si/met/en/)\n- [Slovenian Police: Traffic Safety](https://www.policija.si/eng/prevention/traffic-safety)\n\nRental terms, weather and traffic arrangements can change. Recheck all operational information immediately before riding.",
    "category": "Šport",
    "author": "Uredništvo Blog Lab",
    "status": "published",
    "heroImage": null,
    "video": null,
    "gallery": [],
    "sources": [
      {
        "label": "Ljubljana Tourism — Cycling",
        "url": "https://www.visitljubljana.com/en/visitors/sights-and-activities/active-holidays/cycling/"
      },
      {
        "label": "BicikeLJ — official service",
        "url": "https://www.bicikelj.si/en/home"
      },
      {
        "label": "ARSO — official weather service",
        "url": "https://meteo.arso.gov.si/met/en/"
      },
      {
        "label": "Slovenian Police — Traffic Safety",
        "url": "https://www.policija.si/eng/prevention/traffic-safety"
      }
    ],
    "createdAt": "2026-09-19T09:02:57+02:00",
    "updatedAt": "2026-09-19T09:02:57+02:00"
  },
  {
    "id": "aktualni-pregled-18-9-2026-b139f344",
    "title": "Aktualni pregled: 18. 9. 2026",
    "excerpt": "Samodejni pregled najnovejših objav za področje aktualno, sestavljen iz javno dostopnih RSS virov in neposrednih povezav do izvirnikov.",
    "seoDescription": "Samodejni pregled najnovejših objav za področje aktualno, sestavljen iz javno dostopnih RSS virov in neposrednih povezav do izvirnikov.",
    "content": "Danes, 18. 9. 2026, Blog Lab povzema nove objave s področja **aktualno**. Pregled je sestavljen samo iz podatkov, ki so bili objavljeni v navedenih virih; kjer RSS ne vsebuje dovolj podrobnosti, dodatnih dejstev ne ugibamo.\n\n## 1. Najnižja gledanost oddaje Marcel v desetih letih, Tarča ostaja paradni konj - Info360\n\nNajnižja gledanost oddaje Marcel v desetih letih, Tarča ostaja paradni konj Info360 Objavljeno: Tue, 01 Sep 2026 07:00:00 GMT.\n\n[Odpri izvirni vir](https://news.google.com/rss/articles/CBMiwAFBVV95cUxNY3hsMTM4TmpCN2RFLVRxSTNhaTRuR3NhNWtYOExBZDFvQjREcE85NlNUUnU4MmdCb1l4TUVUZGtMSXY3SWNheUI2bVlLMU0wLWh6WEtUbHE4MTNIZHJrR291RDFJSVQtZVZSMHVFeUdBQ3g3TE1iMEw3bTZKcjNqcW14b01hT3RLc0lJeU5qOTdxQXhkcTdrSWhKSElWS1VNT2NIZzFlaVZPdUhfSkp3QTBFZGNwVU5IN0QwTUpqNDg?oc=5)\n\n## 2. Jelka Godec, nad TV Slovenija. Poslanci se sami odločamo ali bomo v vaših oddajah sodelovali ali ne! - e-Maribor\n\nJelka Godec, nad TV Slovenija. Poslanci se sami odločamo ali bomo v vaših oddajah sodelovali ali ne! e-Maribor Objavljeno: Wed, 16 Sep 2026 05:06:48 GMT.\n\n[Odpri izvirni vir](https://news.google.com/rss/articles/CBMiuwFBVV95cUxOM1F6d0diYmRtMzZOYnFZLTlVY2ExUldmM1ZXNW9TM1Noa3FCTzNRVUF0aHBIeGlqRTRqLWUwbm45M0J0Q1IzVEtLVlFJY2YxWlFJbkJPaXlsSHo1aWdIb0RkamsySzd1X09BMktTcXlSNzFqNmVCU0FULWIycG9YZ1ktelBzcWdXcGRFaXk0b3pncHFOZkhIVnNKS0V5NngxdDlIWkwxX2p4ZEktQW53QkhkRVMxYTlVX01R?oc=5)\n\n## 3. Nov zakon - souporaba električne energije - PwC\n\nNov zakon - souporaba električne energije PwC Objavljeno: Mon, 13 Jul 2026 07:59:51 GMT.\n\n[Odpri izvirni vir](https://news.google.com/rss/articles/CBMihgFBVV95cUxPV19kYnd6MUtuQURJVTZuTFpDZGNENmRvd3NOR1Q1Tm11VXFfTzJVYzFRSUU5UldzQXJtT2RfeUVBcGFDcFQyNnYxN21QZ3lnUTdJSXJYeWdwQlpiRHNSR0g2aXR2a3kzUmp3bEN4eUdFU3ppMVQ4WnlpU1ZaRVNIOTZCRmpfUQ?oc=5)\n\n## 4. Aktualno: prodaja avtomobilov v Sloveniji: Julija je bil vsak četrti novi avtomobilov v Sloveniji električen Novice - AVTO FOKUS -\n\nAktualno: prodaja avtomobilov v Sloveniji: Julija je bil vsak četrti novi avtomobilov v Sloveniji električen Novice AVTO FOKUS - Objavljeno: Mon, 10 Aug 2026 07:00:00 GMT.\n\n[Odpri izvirni vir](https://news.google.com/rss/articles/CBMiowFBVV95cUxOQ3dCM3gyanhNUkpMRUxQaFpWWWViaEtRN211WmVhc1gzekM0WWhOQ0swUWpBaEk4ZWNCNk1FZGtIWEstR2R1MEM2WUVtVnk2MWhrc3RRWV8tTDdxa0tpYXQwNUJvcVV6UEtGZUpRaGE2TXB5WnRpbVU1NjA4UTZaWkRMeTl6cGFncnlNWVdmS1hfRnNFTE1BVU5ZMHRmUUlpQ3pV?oc=5)\n\n## 5. Pred Stevanovićevim obiskom v Srbiji znova aktualno vprašanje statusa srbske skupnosti v Sloveniji - Siol.net\n\nPred Stevanovićevim obiskom v Srbiji znova aktualno vprašanje statusa srbske skupnosti v Sloveniji Siol.net Objavljeno: Wed, 03 Jun 2026 07:00:00 GMT.\n\n[Odpri izvirni vir](https://news.google.com/rss/articles/CBMi1gFBVV95cUxPNW4xS2Z0dXdKNXdpRWp1YnJFcjRfa0k1aDMxM2stM0pmRFY0VThEMXBTNEVOMm9IRmZoazBiTkdrZWZPb09SSkpsRTF3WWI0a05jQTBRd1prYkd3ZU1wSmxENDdoWFpxNDNjRHZfUEMxZU9LdVNjdWlVLVVwYzJFWk9rSjJaSGw2QXZJcUs3MnVmVlpPYUxfSVBIbndGMHhWRVdsMEtlelFGM0c5R01Oc0M3WDhMMU5HdG91RDJCS29GdzVtQVU1bzU3ejVQXzZmTFVKV1R3?oc=5)\n\n## Kaj spremljati naprej\n\nKer se aktualne zgodbe hitro dopolnjujejo, je smiselno preveriti izvirne povezave za morebitne nove podatke, popravke ali odzive. Blog Lab bo naslednji pregled pripravil šele, ko zazna nove, še neobdelane vnose.",
    "category": "Aktualno",
    "author": "Blog Lab Publisher",
    "status": "published",
    "heroImage": null,
    "video": null,
    "gallery": [],
    "sources": [
      {
        "label": "Google News Slovenija – aktualno — Najnižja gledanost oddaje Marcel v desetih letih, Tarča ostaja paradni konj - Info360",
        "url": "https://news.google.com/rss/articles/CBMiwAFBVV95cUxNY3hsMTM4TmpCN2RFLVRxSTNhaTRuR3NhNWtYOExBZDFvQjREcE85NlNUUnU4MmdCb1l4TUVUZGtMSXY3SWNheUI2bVlLMU0wLWh6WEtUbHE4MTNIZHJrR291RDFJSVQtZVZSMHVFeUdBQ3g3TE1iMEw3bTZKcjNqcW14b01hT3RLc0lJeU5qOTdxQXhkcTdrSWhKSElWS1VNT2NIZzFlaVZPdUhfSkp3QTBFZGNwVU5IN0QwTUpqNDg?oc=5"
      },
      {
        "label": "Google News Slovenija – aktualno — Jelka Godec, nad TV Slovenija. Poslanci se sami odločamo ali bomo v vaših oddajah sodelovali ali ne! - e-Maribor",
        "url": "https://news.google.com/rss/articles/CBMiuwFBVV95cUxOM1F6d0diYmRtMzZOYnFZLTlVY2ExUldmM1ZXNW9TM1Noa3FCTzNRVUF0aHBIeGlqRTRqLWUwbm45M0J0Q1IzVEtLVlFJY2YxWlFJbkJPaXlsSHo1aWdIb0RkamsySzd1X09BMktTcXlSNzFqNmVCU0FULWIycG9YZ1ktelBzcWdXcGRFaXk0b3pncHFOZkhIVnNKS0V5NngxdDlIWkwxX2p4ZEktQW53QkhkRVMxYTlVX01R?oc=5"
      },
      {
        "label": "Google News Slovenija – aktualno — Nov zakon - souporaba električne energije - PwC",
        "url": "https://news.google.com/rss/articles/CBMihgFBVV95cUxPV19kYnd6MUtuQURJVTZuTFpDZGNENmRvd3NOR1Q1Tm11VXFfTzJVYzFRSUU5UldzQXJtT2RfeUVBcGFDcFQyNnYxN21QZ3lnUTdJSXJYeWdwQlpiRHNSR0g2aXR2a3kzUmp3bEN4eUdFU3ppMVQ4WnlpU1ZaRVNIOTZCRmpfUQ?oc=5"
      },
      {
        "label": "Google News Slovenija – aktualno — Aktualno: prodaja avtomobilov v Sloveniji: Julija je bil vsak četrti novi avtomobilov v Sloveniji električen Novice -…",
        "url": "https://news.google.com/rss/articles/CBMiowFBVV95cUxOQ3dCM3gyanhNUkpMRUxQaFpWWWViaEtRN211WmVhc1gzekM0WWhOQ0swUWpBaEk4ZWNCNk1FZGtIWEstR2R1MEM2WUVtVnk2MWhrc3RRWV8tTDdxa0tpYXQwNUJvcVV6UEtGZUpRaGE2TXB5WnRpbVU1NjA4UTZaWkRMeTl6cGFncnlNWVdmS1hfRnNFTE1BVU5ZMHRmUUlpQ3pV?oc=5"
      },
      {
        "label": "Google News Slovenija – aktualno — Pred Stevanovićevim obiskom v Srbiji znova aktualno vprašanje statusa srbske skupnosti v Sloveniji - Siol.net",
        "url": "https://news.google.com/rss/articles/CBMi1gFBVV95cUxPNW4xS2Z0dXdKNXdpRWp1YnJFcjRfa0k1aDMxM2stM0pmRFY0VThEMXBTNEVOMm9IRmZoazBiTkdrZWZPb09SSkpsRTF3WWI0a05jQTBRd1prYkd3ZU1wSmxENDdoWFpxNDNjRHZfUEMxZU9LdVNjdWlVLVVwYzJFWk9rSjJaSGw2QXZJcUs3MnVmVlpPYUxfSVBIbndGMHhWRVdsMEtlelFGM0c5R01Oc0M3WDhMMU5HdG91RDJCS29GdzVtQVU1bzU3ejVQXzZmTFVKV1R3?oc=5"
      }
    ],
    "createdAt": "2026-09-18T21:56:36+02:00",
    "updatedAt": "2026-09-18T21:56:36+02:00"
  },

  {
    id: "lipica-lipizzan-unesco-heritage-guide",
    title: "Lipica and the Lipizzaner: A Living UNESCO Tradition",
    excerpt: "Explore the documented history and living breeding tradition behind Slovenia’s Lipizzaner horses, with practical advice for a respectful visit to Lipica.",
    seoDescription: "Visit Lipica responsibly: understand the 1580 stud farm, UNESCO-listed Lipizzaner breeding traditions, horse welfare and practical trip planning.",
    content: `At Lipica, the horse is not a mascot added to a tourist site. The **Lipizzaner breeding tradition** shaped the estate, its landscape and generations of specialist knowledge. Lipica Stud Farm traces its foundation to **1580**, while UNESCO inscribed the multinational traditions of Lipizzan horse breeding on its Representative List of the Intangible Cultural Heritage of Humanity in **2022**.

This guide separates the documented history from popular shorthand and explains how an international visitor can experience the working stud farm respectfully.

## What is documented history?

The Habsburg court established the stud farm at Lipica in 1580. The location in the Karst was selected for breeding horses for court use, and the farm became the place from which the Lipizzaner breed takes its name.

Lipica is therefore historically central to the breed, but Lipizzaner culture is not exclusively Slovenian. UNESCO's 2022 inscription is shared by **Austria, Bosnia and Herzegovina, Croatia, Hungary, Italy, Romania, Slovakia and Slovenia**. The nomination recognises knowledge and social practices maintained by breeders, riders, carriage drivers, craftspeople and other communities across those countries.

The inscription concerns a **living tradition**, not a claim that every stable, performance or horse is itself a UNESCO monument.

## The “white horse” story: fact and simplification

Adult Lipizzaners are widely recognised for their light grey appearance, so they are commonly called white horses. In equestrian terminology, most are **grey**: many foals are born dark and their coats lighten as they mature.

Not every horse follows exactly the same visual path, and colour alone does not define the breed. Pedigree, breeding knowledge, conformation, health, training and long-term care matter more than the postcard image.

There is no need for a legend to explain this change. It is a biological coat-colour process, while the cultural story lies in the human knowledge used to breed and care for the horses.

## Why UNESCO recognised the tradition

UNESCO describes Lipizzan breeding as a body of practices, knowledge and values transmitted over generations. Breeding is connected with classical riding, carriage driving, stable work, veterinary care, ceremonies and everyday relationships between people and horses.

That wider meaning changes how to visit Lipica. A riding-school presentation may be visually memorable, but it is only one public expression of a much larger system. Pastures, historic stables, avenues, training spaces and the work of staff all belong to the cultural landscape.

## How to Experience It Today

Lipica remains a working stud farm as well as a visitor attraction. The official site publishes a daily programme that may include guided tours, horses being released to pasture, presentations, riding-school performances or carriage experiences. Activities vary by date, season, weather and horse welfare.

Before travelling:

1. Open the official day programme for your exact date.
2. Check opening hours and which activities require a separate ticket or reservation.
3. Confirm the language and time of any guided tour.
4. Recheck the programme on the morning of the visit.
5. Allow enough time to walk between facilities without rushing animals or staff.

Do not treat an older travel article as a timetable. Lipica explicitly reserves the right to change its programme.

## Getting to Lipica

Lipica is in Slovenia's Karst region, near Sežana and the Italian border. Drivers should follow the current approach and parking signs rather than stopping beside pasture fences or access roads.

Public transport needs more planning. Arriva has published a Sežana–Lokev–Lipica service, but routes and frequencies can change. Check the live journey planner for both directions and confirm the final return before departure. If the connection does not fit, consider an authorised taxi from Sežana or a pre-arranged tour rather than assuming that an informal transfer will be available.

For a car-light trip from Ljubljana, compare current rail or coach options to Sežana with the onward local connection. Build in a generous transfer margin.

## Respecting horses and a working farm

Horses are sentient animals, and calm behaviour is part of a responsible visit.

- Follow staff instructions, barriers and signs.
- Do not feed or touch a horse unless staff explicitly permit it.
- Keep voices low and avoid flash, sudden movements and loud phone audio.
- Never enter a stable, paddock, training area or pasture without permission.
- Supervise children closely near fences and horses.
- Check the current policy before bringing a dog.
- Do not fly a drone without all required permissions.
- Accept programme changes made for weather, veterinary care or animal welfare.

A cancelled appearance is not a failed heritage experience. Protecting a horse takes priority over a promised photograph.

## Accessibility, weather and comfort

The estate is extensive and includes outdoor routes. Wear comfortable footwear and prepare for sun, rain or Karst wind. Visitors with reduced mobility, sensory needs or other access requirements should contact Lipica before travelling and ask about the precise route, surfaces, toilets, seating and access to the day's activities.

Facilities, catering and payment options can change. Check directly rather than making the visit depend on an unconfirmed service.

## A thoughtful half-day plan

Begin with a guided introduction to understand the farm's history and vocabulary. Continue through the historic core and landscape, then watch a scheduled presentation only if it operates that day. Leave time to observe the estate quietly instead of moving from one photo opportunity to the next.

When you see a light-coated adult horse, remember the fuller story: not a mythical animal that simply “belongs” to one country, but a living breed sustained through documented, shared European knowledge.

## Direct sources

Information was checked on **18 September 2026**:

- [UNESCO: Lipizzan horse breeding traditions](https://ich.unesco.org/en/RL/lipizzan-horse-breeding-traditions-01687)
- [Government of Slovenia: UNESCO inscription of Lipizzan breeding traditions](https://www.gov.si/en/news/2022-12-01-lipizzan-horse-breeding-traditions-inscribed-on-the-unesco-representative-list/)
- [Lipica Stud Farm: official visitor information and daily programme](https://www.lipica.org/)
- [Slovenian Tourist Board: Lipica and the Lipizzaner](https://www.slovenia.info/en/places-to-go/regions/mediterranean-karst-slovenia/lipica)
- [Arriva Slovenia: current buses and timetables](https://arriva.si/en/)

Opening hours, transport and presentations can change. Recheck the official sources shortly before travel.`,
    category: "Vodniki",
    author: "Uredništvo Blog Lab",
    status: "published",
    heroImage: null,
    video: null,
    gallery: [],
    sources: [],
    createdAt: "2026-09-18T14:58:47+02:00",
    updatedAt: "2026-09-18T14:58:47+02:00"
  },

  {
    id: "blog-lab-system-test-persistent",
    title: "Testni članek Blog Lab: trajna objava na vseh napravah",
    excerpt: "Trajna testna objava za preverjanje, da javni Blog Lab, zasebni terminal in repo-backed objave delujejo enako na vseh napravah.",
    seoDescription: "Trajni sistemski test Blog Lab za preverjanje objav na vseh napravah.",
    content: `Ta članek je **trajni produkcijski test** sistema Blog Lab. Za razliko od lokalnega osnutka je zapisan neposredno v GitHub repozitorij, zato mora biti viden enako na vsakem računalniku in telefonu.

## Kaj preverja ta objava?

- da javna stran naloži repo-backed članke;
- da objava ni odvisna od localStorage posameznega brskalnika;
- da povezava do članka deluje neposredno;
- da je novi multimedia renderer združljiv tudi s članki brez fotografije ali videa.

## Kako bomo uporabljali test?

Ko agent iz terminala uspešno objavi nov članek, mora ta postati enako trajen kot ta objava. Lokalni uredniški osnutki se lahko še vedno uporabljajo za preizkus, vendar se na javni naslovnici ne obravnavajo več kot trajne produkcijske objave.

## Stanje

Če ta članek vidiš na več napravah, repo-backed prikaz deluje pravilno.`,
    category: "Aktualno",
    author: "Blog Lab",
    status: "published",
    heroImage: null,
    video: null,
    gallery: [],
    sources: [],
    createdAt: "2026-09-18T12:57:00+02:00",
    updatedAt: "2026-09-18T12:57:00+02:00"
  },
  {
    id: "smarna-gora-hike-ljubljana-guide",
    title: "Hiking Šmarna Gora: Ljubljana’s Car-Free Hill Escape",
    excerpt: "Plan a short hike from Ljubljana to Šmarna Gora using city buses, a standard marked route and practical safety advice for steep, muddy or crowded trails.",
    seoDescription: "Hike Šmarna Gora from Ljubljana without a car: trail choices, city buses, difficulty, equipment, summit facilities and responsible visitor advice.",
    content: `**Šmarna Gora** is Ljubljana’s most popular local hill: close enough for a half-day trip, high enough to feel like a genuine hike and reachable by city bus. Ljubljana Tourism lists the standard route via Spodnja Kuhinja at **1.94 kilometres**, **366 metres of ascent** and about **55 minutes uphill**, ending at 669 metres.

That choice is useful but can also confuse first-time visitors. This guide focuses on a conventional marked ascent from the Tacen or Šmartno side, not on the exposed or protected climbing routes found elsewhere on the hill.

**Current conditions, 18 September 2026:** Ljubljana's forecast includes scattered morning thunderstorms followed by mostly cloudy weather, with a high near 21°C. Do not enter the forest while thunder is audible or lightning is visible. Rain can leave roots, stones and steep soil slippery even after a storm passes; Saturday currently looks more settled, but recheck the forecast before departure.

## Is the hike suitable for you?

The ordinary routes are short by Slovenian mountain standards, but they are not flat walks. Expect a sustained climb on forest paths, stones and roots. Rain can make the descent slippery, while fallen leaves may hide uneven ground in autumn.

Allow roughly **two to three hours** for an unhurried return outing, including a summit break. Individual ascent times vary greatly with route, fitness, trail conditions and crowds, so do not treat a fast local time as a target.

Choose another activity if you cannot safely manage a steep descent, if thunderstorms are forecast or if ice and snow exceed your experience and equipment.

## Getting there without a car

Ljubljana Tourism lists city-bus access using **LPP lines 8, 1B and 15**, depending on the chosen starting point. For the familiar Tacen approach, check the current LPP journey planner for a stop near Tacenski most and confirm the return service before leaving.

Bus routes and frequencies can change. Do not rely on an old screenshot or blog timetable; search the live planner on the morning of your hike. You need an active Urbana payment method or another ticket option currently accepted by LPP.

The Šmarna Gora district currently reports a **partial road closure on the Šmartno–Gameljne–Črnuče local road**, scheduled from 31 August to no later than 30 November 2026 during electrical-infrastructure work. This is not a published hiking-trail closure, but it may affect road traffic or bus timing, so allow extra time and follow local signs.

From the bus stop, follow official local signs toward the marked trailhead. The many informal shortcuts visible in the forest are not automatically safe or permitted routes.

## Choosing a route

For a first visit, select a normal waymarked hiking path and stay on it in both directions. At junctions, follow the red-and-white Slovenian mountain markings and destination signs rather than the footprints of the person ahead.

Avoid choosing a path merely because it appears shorter on a phone map. Šmarna Gora also has demanding and very demanding routes, including protected sections where exposure and fixed equipment change the nature of the outing.

If a sign describes your option as \`zahtevna pot\` or \`zelo zahtevna pot\`, that means **demanding** or **very demanding trail**. Turn back and use an easier marked route unless you deliberately planned for that level and possess the required skills and equipment.

## What to bring

- Shoes with reliable grip; smooth city trainers are a poor choice after rain.
- Water, even though refreshments may be available at the summit.
- A light waterproof layer and an insulating layer in cooler months.
- A charged phone with the route saved offline.
- A small first-aid kit and any personal medication.
- Trekking poles if they help you control the descent.

The summit inn is a welcome feature, not an emergency plan. Opening hours, payment options and available food can change, so check directly before depending on it.

## At the summit

The summit area includes the Church of the Mother of God and viewpoints over Ljubljana and, in clear conditions, toward surrounding mountain ranges. Share narrow viewpoints and paths patiently: the hill is a daily exercise venue for residents as well as a visitor attraction.

Keep church access clear, lower your voice around worship and private events, and do not enter closed areas. If the view is obscured by cloud, do not leave the marked path in search of a better angle.

## Autumn and bad-weather safety

September can bring warm afternoons, cold rain and rapidly changing visibility. Before leaving, check the current forecast and the Alpine Association of Slovenia’s trail-closure page.

- Do not use any officially closed trail.
- Turn around if heavy rain, lightning, strong wind or poor visibility develops.
- Descend before darkness unless you intentionally planned and equipped for a night hike.
- In an emergency call **112**, but remember that mobile reception and rescue response are never guaranteed.

Šmarna Gora is lower than the Alps, yet slips, heat stress and navigation errors can still happen. A popular trail is not the same as a risk-free trail.

## Responsible trail behaviour

Stay on marked paths to limit erosion and avoid disturbing private land. Do not cut switchbacks, leave litter, play loud music or block the trail while resting. Keep dogs under effective control and follow any posted leash requirements.

Uphill walkers generally need space to maintain rhythm, while faster runners should pass only when there is room. A simple greeting and clear warning make shared trails safer.

## A practical half-day plan

1. Check the forecast, trail notices and live LPP connection.
2. Take a morning bus to your selected trailhead.
3. Photograph the route board and confirm your marked ascent.
4. Climb at a conversational pace and pause away from junctions.
5. Rest at the summit without relying on the inn being open.
6. Descend the same known route if conditions or navigation are uncertain.
7. Return to central Ljubljana by bus.

The hike itself is free. Your predictable costs are public transport and any food or drink purchased at the summit.

## Continue exploring responsibly

For a longer mountain excursion in stable weather, see [Hiking Velika Planina: A Responsible Day Trip from Ljubljana](?article=velika-planina-hiking-guide-september). If wet trails rule out a forest ascent, use the largely urban [Plečnik self-guided walking route](?article=plecnik-ljubljana-self-guided-walking-tour) when city conditions are safe.

## Direct sources

Information was checked on **18 September 2026**:

- [Ljubljana Tourism: Šmarna Gora route via Spodnja Kuhinja](https://www.visitljubljana.com/en/visitors/sights-and-activities/active-holidays/hiking-trails/smarna-gora-route-via-spodnja-kuhinja-669-m)
- [Ljubljana Tourism: hiking routes](https://www.visitljubljana.com/en/visitors/sights-and-activities/active-holidays/hiking-trails/)
- [Alpine Association of Slovenia: current trail closures](https://stanje-poti.pzs.si/en.php)
- [LPP: Ljubljana city buses and journey planning](https://www.lpp.si/en)
- [Šmarna Gora district: current local notices](https://www.smarna-gora.si/)
- [Šmarna Gora summit webcam and local temperature](https://www.smarnagora.com/)

Conditions, transport and facilities can change. Recheck the direct sources shortly before setting out.`,
    category: "Šport",
    author: "Uredništvo Blog Lab",
    status: "published",
    createdAt: "2026-09-18T08:57:58+02:00",
    updatedAt: "2026-09-18T09:00:00+02:00",
  },

  {
    id: "bohinj-cows-ball-2026-visitor-guide",
    title: "Bohinj Cows’ Ball 2026: A Car-Light Visitor Guide",
    excerpt: "Visit Bohinj’s traditional Kravji bal in Ukanc with confirmed times, ticket prices, free event buses, parking guidance and respectful tips for experiencing living pastoral heritage.",
    seoDescription: "Plan the 67th Bohinj Cows’ Ball in Ukanc on 20 September 2026: programme, tickets, free buses, boat packages, parking and responsible visitor advice.",
    content: `The **67th Traditional Cows’ Ball**—\`Kravji bal\` in Slovene—takes place in **Ukanc, Bohinj, on Sunday 20 September 2026**. The event runs from **10:00 to 18:00**, with the ceremonial arrival of decorated cattle from the high pastures expected at about **13:00**.

This is a public festival built around Bohinj’s pastoral heritage, not a staged wildlife attraction. Its central image—the return of cattle and herders from mountain pastures—comes from the seasonal movement of livestock known as transhumance. Visitors also encounter local food, crafts, music and demonstrations connected with rural life.

## Essential event details

- **Date:** Sunday 20 September 2026
- **Time:** 10:00–18:00
- **Place:** Ukanc, at the western end of Lake Bohinj
- **Adult admission:** €10 on the day or €8 in advance
- **Children aged 7–14:** €6
- **Children under 7:** free

Prices and programme details were checked on **17 September 2026**. Buy only through the organiser or its linked official sales channel, and recheck the event page before departure in case weather or operational conditions change.

## What happens during the day?

The festival opens in the morning, while the best-known moment is scheduled for around 13:00, when herders bring decorated cattle into the event area. The arrival time is approximate: animals, people and mountain conditions do not run like a theatre cue.

The wider programme presents elements of Bohinj’s dairy and shepherding culture alongside entertainment and food. Treat demonstrations as interpretations of living heritage rather than proof that every historic practice is still performed in exactly the same way.

For a comfortable visit, arrive before midday. This gives you time to find the entrance, understand the layout and choose a viewing place without blocking routes used by animals, handlers or emergency staff.

## The easiest car-light journey

Bohinj has published a special transport plan for the festival. On 20 September, dedicated buses will connect villages and park-and-ride locations with Ukanc:

1. **Lower Bohinj Valley:** Bohinjska Bistrica–Lake Bohinj–Ukanc, approximately every 20 minutes from 08:30 to 19:00.
2. **Upper Bohinj Valley:** Jereka–Stara Fužina–Ukanc, first departure at 09:00 and then approximately every 30 minutes between 10:00 and 19:00.
3. **Nomenj route:** Nomenj–Lake Bohinj–Ukanc, approximately every 60 minutes from 08:00 to 19:00.

The municipality states that these event services are free. Line 3 between Lake Bohinj and Ukanc and marked Line 9 services to Savica Waterfall are also free that day; Lines 4 and 5 are not included in the free offer.

If arriving from elsewhere in Slovenia, check the current national bus or rail connection to Bohinjska Bistrica, then allow generous transfer time. Event traffic and passenger numbers may affect the journey.

## Parking and the lake boat option

Drivers are asked to leave vehicles outside Ukanc and continue by bus. The official recommendation is to use **P13 Danica** or **P23 Kobla** in Bohinjska Bistrica. Free event-day parking is also listed at Ribčev Laz–Kristal, Stara Fužina–Labora and P32 Nomenj.

Park only in marked spaces. Roadside parking is prohibited and creates problems for residents, buses and emergency access.

A panoramic boat package combines admission with travel across Lake Bohinj. The published adult price is **€12 with a one-way boat journey** or **€17 with a return journey**. Confirm sailing times, capacity and the departure pier before relying on this option, especially if wind or poor weather is forecast.

## How to experience the festival responsibly

- Keep well behind barriers and follow instructions from animal handlers.
- Do not touch, feed, startle or crowd the cattle.
- Avoid flash photography and sudden noise near animals.
- Keep children close and dogs away from livestock; check the organiser’s pet rules before bringing one.
- Wear footwear suitable for grass, mud and uneven ground.
- Bring rain protection and a warm layer: late-September weather beside the lake can change quickly.
- Use refillable water containers and dispose of waste only at designated points.
- Ask before photographing individual herders, craftspeople or children.

The event is inside the wider Triglav National Park landscape. Festival admission does not relax conservation rules: remain on authorised routes, respect private land and do not extend the day with an unplanned mountain hike.

## A simple day plan

Take an early connection to Bohinjska Bistrica, then use the free event bus to Ukanc. Arrive between 10:00 and 11:30 to explore calmly, eat before the busiest period and locate the viewing area. Watch the cattle arrival at about 13:00, then spend the afternoon with the heritage programme before returning by organised transport.

Save the official transport page on your phone, but also note your last practical return connection. Mobile coverage, battery life and crowding can make last-minute planning unreliable.

## Direct sources

Information was checked on **17 September 2026**:

- [Bohinj Tourist Association: official Cows’ Ball event page](https://tdbohinj.si/)
- [Bohinj destination: official event calendar](https://www.bohinj.si/)
- [Promet Bohinj: festival buses, parking and boat packages](https://promet.bohinj.si/en/2026/08/road-closures-and-transport-during-events/)
- [Slovenian Tourist Board: 67th Traditional Cow Ball 2026](https://www.slovenia.info/en/things-to-do/events)

Recheck the organiser and transport notices shortly before travel. Weather, traffic measures and programme timing can change.`,
    category: "Aktualno",
    author: "Uredništvo Blog Lab",
    status: "published",
    createdAt: "2026-09-17T21:38:19+02:00",
    updatedAt: "2026-09-17T21:38:19+02:00",
  },

  {
    id: "skofja-loka-passion-play-unesco-guide",
    title: "Škofja Loka Passion Play: A UNESCO Heritage Guide",
    excerpt: "Discover the documented history and living community tradition behind Slovenia's oldest preserved dramatic text, with a practical year-round visit to Škofja Loka.",
    seoDescription: "Explore the Škofja Loka Passion Play responsibly: its 1721 manuscript, UNESCO status, performances, museum exhibition and practical visitor route.",
    content: `The **Škofja Loka Passion Play**—\`Škofjeloški pasijon\` in Slovene—is more than a historic script. It is a community procession that turns the medieval streets and squares of Škofja Loka into a moving stage. UNESCO added the tradition to its Representative List of the Intangible Cultural Heritage of Humanity in **2016**.

The large 2026 performances took place from **21 March to 19 April 2026**. Visitors arriving later in the year should not expect a live procession, but they can still understand the story through the old town, the permanent museum exhibition and the Capuchin heritage connected with the manuscript.

## What is documented history?

The preserved play was written in **1721** by the Capuchin friar Father Romuald, also identified in sources as Romuald Marušič or Romuald Štandreški. It is recognised by the official heritage organisations as the oldest preserved dramatic text in the Slovenian language.

Its subject is Christian: scenes present the Passion of Christ and other biblical material. The procession format matters as much as the words. Performers move through the town and spectators encounter successive scenes in public space rather than inside a conventional theatre.

The manuscript is associated with the Capuchin monastery in Škofja Loka. The official tourism site describes it as an exceptionally early preserved European directing book. That phrase refers to the practical staging record as well as the literary text; it should not be read as a claim that European theatre began in Škofja Loka.

## What UNESCO recognition means

UNESCO recognised the **living practice**, not merely an old object. The heritage survives because local residents, performers, craftspeople and volunteers transmit knowledge and recreate the procession periodically.

This distinction is useful for visitors:

- the **manuscript** is a historical document;
- the **Passion narrative** comes from Christian religious tradition;
- the **procession** is a recurring community performance;
- UNESCO status recognises the cultural practice and its transmission.

There is no local legend that needs to be accepted as fact here. Religious belief, documented manuscript history and contemporary heritage work are different layers, and each deserves to be described on its own terms.

## Why the town is part of the performance

Škofja Loka's historic centre is not a decorative backdrop added to a modern show. Streets and squares shape how the procession moves and how spectators experience it. Periodic performances bring together roughly a thousand performers and volunteers, according to the destination's official account.

The scale explains why the full production is not a daily attraction. The tradition depends on extensive local participation and preparation. Outside a performance year, visitors should approach it as heritage to study rather than a spectacle that can be ordered on demand.

## How to experience it today

Begin on **Mestni trg**, the main historic square, and walk slowly through the compact old centre. Rather than inventing an exact procession route, use the official map or tourist information available on the day of your visit: staging and visitor arrangements can change between performance cycles.

Then visit the permanent Passion Play exhibition at **Loški muzej** in Škofja Loka Castle. The museum describes a display combining historic objects, photographs, film, a digital version of the Passion codex and material from earlier performances. Check the museum's current opening hours, admission and accessibility information before climbing to the castle.

The Capuchin library and monastery provide another historical connection. Access is not equivalent to an always-open public museum, so contact the local tourist information centre or monastery in advance instead of arriving with an expectation of unrestricted entry.

## A practical half-day plan

1. Arrive in Škofja Loka and begin at the tourist information point or main square.
2. Spend 45–60 minutes walking through Mestni trg and the old-town streets.
3. Allow time for the uphill walk to Škofja Loka Castle.
4. Explore the permanent Passion Play exhibition inside Loški muzej.
5. If arranged in advance, add the Capuchin heritage site and library.

The centre is compact but includes cobbles, slopes and steps. Visitors with limited mobility should confirm step-free routes and museum access directly; historic streets can create barriers even when destinations provide accessible services.

## Reaching Škofja Loka without a car

Škofja Loka is accessible from Ljubljana by bus and train, but the railway station lies about **2.5 kilometres** from the centre. The destination's public-transport page lists a local bus between the railway station, bus station and central area. Timetables and fares may change, so verify the current connection with the operator before travelling.

If arriving by train, allow extra transfer time. If arriving by intercity bus, the bus station is closer to the historic centre. A car is not necessary for the central heritage route.

## Respectful visiting

- Treat the Passion Play as both religious tradition and community heritage.
- Do not enter monastic or worship spaces without permission.
- Ask before photographing people, services or private interiors.
- During future performances, follow official crowd routes and never obstruct performers.
- Support year-round preservation by using museums, guides and local businesses rather than seeking unauthorised access to the manuscript.

## Direct sources

Historical and visitor information was checked on **17 September 2026**:

- [UNESCO: Škofja Loka Passion Play](https://ich.unesco.org/en/RL/skofja-loka-passion-play-01203)
- [Official Škofja Loka Passion Play site](https://www.pasijon.si/en/about/)
- [Tourism Škofja Loka: UNESCO heritage](https://www.visitskofjaloka.si/si/dozivetja/umetnost-in-kultura/unesco-dediscina)
- [Loški muzej: permanent Passion Play exhibition](https://www.loski-muzej.si/skofjeloski-pasijon/)
- [Tourism Škofja Loka: public transport](https://www.visitskofjaloka.si/si/javni-prevoz)

Always recheck museum opening times, transport and access arrangements shortly before visiting.`,
    category: "Vodniki",
    author: "Uredništvo Blog Lab",
    status: "published",
    createdAt: "2026-09-17T15:02:06+02:00",
    updatedAt: "2026-09-17T15:02:06+02:00",
  },

  {
    id: "julian-alps-trail-run-2026-guide",
    title: "Julian Alps Trail Run 2026: Runner and Spectator Guide",
    excerpt: "Plan race weekend in the Julian Alps with confirmed dates, start towns, closed-registration advice, live tracking, parking changes and mountain-safety context.",
    seoDescription: "Visit Julian Alps Trail Run by UTMB on 18–20 September 2026: race dates, start towns, spectator advice, live tracking, access and mountain safety.",
    content: `Julian Alps Trail Run by UTMB returns from **Friday 18 to Sunday 20 September 2026**, linking several towns around Slovenia's Julian Alps before the races converge on Kranjska Gora. This guide is for registered runners and visitors who want to follow the event responsibly; official entries for every listed 2026 distance are already closed.

The event is not the same experience as hiking the Juliana Trail. It is a timed mountain-running weekend with separate courses, race controls and participant rules. Spectators should use official information, stay off the marked course and expect temporary changes around the event hub.

## Which races happen when?

The organiser lists seven races or categories:

- **I Feel Slovenia 120K:** starts in Radovljica on Friday 18 September; the published course is 122 km with 5,855 m of ascent.
- **Sky Trail 50K:** starts in Žirovnica on Friday 18 September; the published course is 55 km with 2,828 m of ascent.
- **Lake Bled 80K:** starts in Bled on Saturday 19 September; the published course is 80 km with 3,866 m of ascent.
- **Kranjska Gora 25K:** starts in Kranjska Gora on Sunday 20 September; 25 km with 1,090 m of ascent.
- **Intersport Speed 15K:** starts in Kranjska Gora on Sunday 20 September; the published course is 17 km with 583 m of ascent.
- **Vitranc Funny 10K** and **NextGen 10K:** both are listed for Sunday 20 September in Kranjska Gora; each published course is 11 km with 329 m of ascent.

Do not use these headline figures as navigation. Registered runners should download the current race guide, read their race-specific instructions and follow only official course markings.

## A practical plan for spectators

Kranjska Gora is the clearest base for the weekend because it hosts Sunday's shorter races and the main event atmosphere. For runners on the longer courses, use the organiser's \`UTMB Live\` service rather than trying to intercept them on mountain roads. Tracking is informative, not a guarantee of a runner's condition or exact position.

A low-impact spectator plan:

1. Check the official event schedule and your runner's course before leaving.
2. Choose one authorised public viewing location with safe pedestrian access.
3. Keep the full width of the marked trail and finish approach clear.
4. Never provide unauthorised pacing or assistance; race rules govern outside support.
5. Carry your rubbish back and avoid shortcuts across meadows or protected habitat.

The event website also lists supporter bus transfers. Check availability and booking conditions directly with the organiser before relying on them.

## Access and current parking changes

Kranjska Gora can be reached by scheduled bus connections, but timetables vary by day and season. Check the current journey planner before travel and leave extra time for race-weekend traffic.

The municipal parking service currently states that the **Občina** and **Dvorana Vitranc** car parks are closed through the end of race week. Do not drive to Kranjska Gora assuming your usual parking place will be available. Follow temporary signs and marshal instructions; guests covered by a local GOST parking subscription may use other municipal car parks under the conditions published by the parking operator.

## Safety for registered runners

September conditions in the Julian Alps can change quickly, while the long races extend through the night and over sustained climbing. The organiser publishes a dedicated equipment page and race regulations. Mandatory kit is a minimum, not a substitute for skills or judgement.

Before your start:

- check the latest official weather forecast and organiser alerts;
- carry every item required for your specific race, including any activated hot- or cold-weather kit;
- know the cut-off rules, aid-station plan and emergency procedure in the race guide;
- do not continue through injury, hypothermia symptoms, lightning exposure or unsafe terrain merely to finish;
- follow organiser, medical and mountain-rescue instructions immediately.

Spectators should prepare for cold rain too. Wear grippy footwear, carry warm waterproof layers and avoid entering remote mountain terrain just to find a quieter viewpoint.

## How to experience it responsibly

The courses pass through sensitive Alpine landscapes, including areas around Triglav National Park. Race participation does not make the mountains a closed sporting arena: residents, wildlife and other trail users remain part of the landscape.

Stay on designated paths, keep noise low away from the event hub, never move course markers and do not follow runners by bicycle or car on restricted roads. If you are not registered, enjoy the atmosphere as a spectator rather than entering a course unofficially.

## Direct sources

Details were checked on **17 September 2026**:

- [Julian Alps Trail Run by UTMB — official event site](https://julianalps.utmb.world/)
- [Official race list, dates, distances and registration status](https://julianalps.utmb.world/races)
- [Official event schedule](https://julianalps.utmb.world/runners/event-schedule)
- [Official equipment information](https://julianalps.utmb.world/runners/equipment)
- [Kranjska Gora municipal parking notices](https://parking.kranjska-gora.si/)

Event operations can change close to race time. Recheck the official schedule, race guide, weather alerts and transport information before setting out.`,
    category: "Šport",
    author: "Uredništvo Blog Lab",
    status: "published",
    createdAt: "2026-09-17T09:02:57+02:00",
    updatedAt: "2026-09-17T09:02:57+02:00",
  },

  {
    "id": "plecnik-ljubljana-self-guided-walking-tour",
    "title": "Plečnik’s Ljubljana: A Self-Guided UNESCO Walking Tour",
    "excerpt": "Follow Jože Plečnik’s human-centred vision through Ljubljana on a practical walking route linking Trnovo, the river embankments, the National Library, bridges and Central Market.",
    "seoDescription": "Walk through Plečnik’s Ljubljana with this self-guided UNESCO route covering Trnovo, the National Library, Cobblers’ Bridge, Triple Bridge, Central Market and Plečnik House.",
    "content": "Jože Plečnik did not rebuild Ljubljana from a blank plan. Between the two world wars, he reshaped the existing city through bridges, promenades, trees, columns, markets, cultural buildings and carefully framed views. This self-guided walk follows that idea from Trnovo to the Central Market and helps visitors recognise why UNESCO describes his work as human-centred urban design.\n\nThe outdoor route is approximately 3 kilometres and takes about 60–90 minutes without museum visits. Allow three hours if you stop frequently and join a tour of Plečnik House. Most exterior landmarks are free to see.\n\nLast updated: **17 September 2026**.\n\n## Who was Jože Plečnik?\n\nJože Plečnik was born in Ljubljana in **1872** and died there in **1957**. He trained and worked in Vienna, later taught and designed in Prague, and returned to Ljubljana, where his interventions transformed the city during the period between the First and Second World Wars.\n\nThe Museum and Galleries of Ljubljana explains that Plečnik learned his craft in Vienna, broadened his architectural experience in Prague and developed many of his Ljubljana projects from his home in Trnovo. UNESCO places his Ljubljana work in a wider historical transition: after the dissolution of Austria-Hungary, the city was developing from a provincial centre into the symbolic capital of the Slovenian people.\n\nThis is documented history rather than legend. Plečnik’s influence is sometimes described as if he designed the whole city, but that is an exaggeration. He worked with an older urban fabric and added connected interventions at different scales.\n\n## Why Plečnik’s Ljubljana is UNESCO-listed\n\nUNESCO inscribed **The Works of Jože Plečnik in Ljubljana – Human Centred Urban Design** on the World Heritage List in **2021**. The serial property includes public spaces and institutions rather than one isolated monument.\n\nUNESCO identifies two principal routes through his city:\n\n- a land axis running from Trnovo Bridge through Vegova Street toward Congress Square;\n- a water axis following the Ljubljanica embankments and bridges from Trnovo toward the Sluice Gate.\n\nThese axes explain the best way to experience Plečnik’s Ljubljana: walk through it. His work connects daily activities—crossing a river, shopping, reading, meeting and resting—rather than separating architecture from ordinary life.\n\n## Self-guided Plečnik walking route\n\n### 1. Begin at Plečnik House in Trnovo\n\nStart at **Karunova 4–6**, where Plečnik lived and developed many of his ideas. The preserved home and permanent exhibition introduce his working methods, objects and personal environment.\n\nThe original home can only be visited on a guided tour. As checked on 17 September 2026, Plečnik House is open **Tuesday to Sunday, 10:00–18:00**, and closed on Mondays. Tours begin every full hour and may be conducted in Slovenian and English when the group is international. The adult ticket including the permanent exhibition and guided home visit is listed at **€12**; advance booking is recommended. Confirm current availability before travelling because capacity and prices can change.\n\nIf the museum is closed, the exterior still provides a logical starting point for the public walking route.\n\n### 2. Cross Trnovo Bridge\n\nWalk to Trnovo Church and cross **Trnovo Bridge**. Plečnik treated the bridge as more than traffic infrastructure: its width, trees and architectural details make it feel like a small public square above the Gradaščica.\n\nPause without blocking cyclists or residents. Notice how the bridge connects the church, neighbourhood streets and the start of the green promenade rather than functioning as an isolated photo stop.\n\n### 3. Follow the green axis toward the Roman Wall\n\nContinue toward the remains of Roman Emona on Mirje. Plečnik’s treatment of archaeological fragments is important because it shows his dialogue with earlier Ljubljana rather than an attempt to erase it.\n\nThe archaeological area is an outdoor heritage site. Do not climb on walls or move stones, and remember that preservation takes priority over obtaining an unobstructed photograph.\n\n### 4. Walk Vegova Street to the National and University Library\n\nTurn north along **Vegova Street**, where trees, monuments and paving create a formal approach to the **National and University Library**, usually abbreviated as NUK.\n\nThe library’s dark brick-and-stone façade rewards close observation. Its varied materials and projecting windows give it a deliberately layered appearance. The building remains a working national library, so exterior viewing should not be confused with unrestricted access to reading rooms. Check NUK’s official visitor information before planning an interior visit.\n\n### 5. Continue to Congress Square\n\nVegova Street leads toward **Congress Square and Zvezda Park**, the northern end of UNESCO’s green promenade. This is a useful place to understand Plečnik’s method: architecture, trees, paths and views operate together.\n\nCongress Square also connects the route to Ljubljana’s older ceremonial centre. Take time to look back along Vegova Street before moving toward the river.\n\n### 6. Cross Cobblers’ Bridge\n\nDescend toward the Ljubljanica and cross **Cobblers’ Bridge**. Its rows of columns turn the crossing into a social space—a bridge that also behaves like a square.\n\nThe present structure belongs to Plečnik’s interwar transformation of the riverfront, but the crossing itself has a much longer urban history. Keep that distinction clear: Plečnik redesigned an established location rather than inventing the city’s relationship with the river.\n\n### 7. Follow the embankments to Triple Bridge\n\nWalk north beside the Ljubljanica to **Triple Bridge**. Plečnik expanded the existing central crossing with two pedestrian bridges, producing a fan-shaped connection between the medieval town, Prešeren Square and the modern city.\n\nThis is one of Ljubljana’s busiest pedestrian points. Step aside before stopping for photographs and keep the central flow clear. Early morning offers a calmer view of the bridge’s geometry.\n\n### 8. Finish at Plečnik’s Central Market\n\nContinue east to the riverside market buildings between Triple Bridge and Dragon Bridge. Plečnik placed the market beside the Ljubljanica as a long civic façade serving ordinary commercial life.\n\nThe outdoor stalls and indoor sections follow their own operating schedules, so do not assume every area will be open throughout the day. Morning is generally the most useful time to combine the architecture with an active market visit. Respect vendors by asking before photographing people or close-up displays.\n\nFrom here, visitors can continue toward the Sluice Gate to follow more of UNESCO’s water axis or return to the city centre.\n\n## A shorter accessible option\n\nVisitors with limited time or mobility can focus on the mostly level central section:\n\n1. Congress Square;\n2. National and University Library exterior;\n3. Cobblers’ Bridge;\n4. Triple Bridge;\n5. Central Market.\n\nSurfaces vary between smooth paving, stone and cobbles, and crowds can narrow routes near the bridges and market. Plečnik House lists a reduced ticket for visitors with disabilities and free entry for carers, but visitors who need a particular accommodation should contact the museum before arrival. A listed discount does not by itself confirm that every preserved room is step-free.\n\n## How to read Plečnik’s details\n\nLook for repeated design ideas rather than racing between landmarks:\n\n- **Columns used outdoors:** classical forms become practical markers for bridges and public spaces.\n- **Routes framed by trees:** greenery is part of the architecture, not leftover decoration.\n- **Small transitions:** steps, lamps, balustrades and changes in paving guide movement.\n- **Old and new together:** Roman remains, baroque landmarks and modern interventions remain visible in dialogue.\n- **Everyday civic use:** markets, promenades and crossings show why UNESCO emphasises a human scale.\n\nPlečnik’s Ljubljana is best understood as a connected urban experience, not a checklist of façades.\n\n## Responsible visiting\n\n- Walk or use public transport; the central route does not require a car.\n- Keep entrances, cycle lanes, bridges and market aisles clear.\n- Treat NUK as a working institution and Plečnik House as a preserved museum environment.\n- Do not climb on archaeological remains, columns or river barriers.\n- Support market vendors when photographing or sampling local products.\n- Recheck museum hours and tour availability on the day of your visit.\n\n## Continue exploring Ljubljana and Slovenia\n\nFor another Ljubljana story, read [Why Ljubljana Has Dragons: Legend, History and a Walking Trail](?article=ljubljana-dragon-legend-walking-guide). To compare documented history with folklore outside the capital, continue with [Idrija Mercury: Legend, History and UNESCO Heritage](?article=idrija-mercury-legend-unesco-guide). Visitors planning a mountain day after the city can use [Hiking Velika Planina: A Responsible Day Trip from Ljubljana](?article=velika-planina-hiking-guide-september).\n\n## Sources\n\nHistorical and visitor information was checked on **17 September 2026**:\n\n- [UNESCO World Heritage Centre: The Works of Jože Plečnik in Ljubljana](https://whc.unesco.org/en/list/1643/)\n- [Museum and Galleries of Ljubljana: Plečnik House](https://mgml.si/en/plecnik-house/)\n- [Ljubljana Tourism: Plečnik’s Ljubljana](https://www.visitljubljana.com/en/visitors/sights-and-activities/plecniks-ljubljana/)",
    "category": "Vodniki",
    "author": "Uredništvo Blog Lab",
    "status": "published",
    "createdAt": "2026-09-17T09:00:00+02:00",
    "updatedAt": "2026-09-17T09:00:00+02:00"
  },
  {
    id: "poljanska-fest-2026-ljubljana-guide",
    title: "Poljanska Fest 2026: Ljubljana Street Festival Guide",
    excerpt: "Plan a free Sunday at Poljanska Fest with the confirmed programme, street-closure details, music, food and practical advice for reaching the neighbourhood on foot.",
    seoDescription: "Visit Poljanska Fest in Ljubljana on 20 September 2026: confirmed programme, free entry, street closure, food, concerts and practical access tips.",
    content: `Poljanska Fest turns one of Ljubljana's historic approaches to the city centre into a neighbourhood street festival on **Sunday 20 September 2026**. From breakfast and children's storytelling to interviews, jazz, blues and swing, the event offers international visitors a relaxed way to experience Ljubljana beyond its main postcard sights.

The festival runs from **10:00 to 22:00** and admission is **free**. Details below were checked against Ljubljana Tourism's official event listing on **16 September 2026**.

## Date, time and exact location

The event occupies **Poljanska cesta between Resljeva cesta and Ulica Janeza Pavla II**. This section of the road closes to traffic while shops, cafés, food providers and performers move into the street.

Key facts:

- **Date:** Sunday 20 September 2026;
- **Time:** 10:00–22:00;
- **Place:** Poljanska cesta, from Resljeva cesta to Ulica Janeza Pavla II;
- **Admission:** free;
- **Format:** outdoor food, talks, children's activities and live music.

The organiser says the road reopens to traffic at **22:00**. Treat the published times as the current plan and check the official listing again on the morning of the event, especially if weather or operational conditions change.

## Confirmed programme

The official schedule moves from a family-friendly morning to evening concerts:

1. **10:00:** breakfast from local food businesses, music by DJ Zvuk and a comic-book reading for children by Izar Lunaček.
2. **12:30:** street performance by Počeni škafi.
3. **15:00:** lunch accompanied by DJ Zvuk.
4. **16:00:** live interviews led by journalist Patricija Maličev.
5. **17:00:** a final philosophical gathering and audience conversation.
6. **19:00:** Teja Saksida and her ensemble perform jazz standards in translation.
7. **20:00:** blues and soul with Jana Šušteršič and saxophone.
8. **21:00:** Počeni škafi bring swing to the main stage.
9. **22:00:** scheduled end and reopening of the road.

The programme includes named food providers, but the festival listing does not promise fixed menus or prices. Bring a payment card and some euros, then decide on site rather than relying on unofficial menus shared earlier.

## When should you arrive?

Choose your arrival time according to the experience you want:

- **Families:** arrive close to 10:00 for breakfast and children's storytelling, before the street becomes busier.
- **Food-focused visitors:** breakfast or the 15:00 lunch period gives the clearest culinary anchor.
- **Culture and conversation:** arrive before 16:00 for the interviews and philosophical gathering.
- **Live-music visitors:** come by 18:30, allowing time to walk the street before the first evening concert.

Because this is a free public event, there are no reserved seats. Popular performances may attract standing crowds, so do not block doorways, crossings or access to homes and businesses.

## How to get there without a car

Poljanska cesta begins just east of Ljubljana's pedestrian centre. From the Triple Bridge or Central Market area, the western end of the festival zone is a straightforward walk of roughly 10–15 minutes for most visitors.

Walking is the simplest option because the event itself closes part of the road. If you use a city bus, check the live Ljubljana Passenger Transport journey planner before departure: the street closure can affect stops, routes and travel times. Cyclists should dismount in dense crowds and use designated parking rather than attaching bicycles to barriers, shopfronts or emergency infrastructure.

Do not drive toward the closed section expecting drop-off access. For taxis or accessible transport, arrange a meeting point outside the closure and confirm the closest usable approach with the operator on the day.

## Accessibility and comfort

The event takes place on a paved city street, but stalls, cables and crowds can narrow the usable route. Visitors who need step-free access should arrive earlier, when movement is likely to be easier, and contact the event information source in advance if a specific accommodation is essential.

Bring:

- weather-appropriate layers for a full day outdoors;
- a reusable water bottle;
- hearing protection for young children during evening concerts;
- a small bag that remains easy to manage in a crowd;
- any essential medication.

There is no need to carry specialised equipment—\`comfortable shoes\` are more useful than a tightly packed sightseeing schedule.

## Make it part of a Ljubljana day

Poljanska Fest works well as a neighbourhood extension to a central-city itinerary. A balanced day might look like this:

1. Visit Ljubljana Central Market in the morning.
2. Walk east to Poljanska cesta for breakfast or the midday performance.
3. Explore the festival street and support independent local businesses.
4. Take a quiet break beside the Ljubljanica before returning for the evening concerts.

Avoid trying to combine every programme item with multiple distant attractions. The value of the event lies in spending time in the district and seeing how residents temporarily reclaim the street for food, conversation and music.

## Responsible festival etiquette

- **Use bins and reusable containers** where available; do not leave cups or food packaging on the street.
- **Keep emergency access clear**, even when a performance attracts a crowd.
- **Ask before photographing children or identifiable residents** at close range.
- **Supervise children and dogs** around food stalls, cables and loud music.
- **Respect the neighbourhood:** people live above and beside the event area.
- **Follow staff and city instructions** if the layout or programme changes.

## Direct sources

Information was checked on **16 September 2026**:

- [Ljubljana Tourism: Poljanska Fest 2026](https://www.visitljubljana.com/en/visitors/events/events-in-ljubljana/poljanska-fest)
- [Ljubljana Tourism: events calendar](https://www.visitljubljana.com/en/visitors/events/events-in-ljubljana)
- [Ljubljana Passenger Transport: official website](https://www.lpp.si/en)`,
    category: "Aktualno",
    author: "Uredništvo Blog Lab",
    status: "published",
    createdAt: "2026-09-16T20:59:53+02:00",
    updatedAt: "2026-09-16T20:59:53+02:00",
  },
  {
    id: "idrija-mercury-legend-unesco-guide",
    title: "Idrija Mercury: Legend, History and UNESCO Heritage",
    excerpt: "Separate Idrija’s tub-maker legend from its documented mercury history, then plan a responsible visit to the mine, castle museum and UNESCO heritage sites.",
    seoDescription: "Explore Idrija’s mercury legend and documented UNESCO mining heritage, with practical advice for visiting Anthony’s Main Road and Gewerkenegg Castle.",
    content: `Idrija's story begins with a flash of liquid metal in a stream—or so local tradition says. What followed is documented on a global scale: five centuries of mercury mining shaped the town, connected it to trade across the Atlantic and left an industrial landscape shared with Almadén in Spain on the UNESCO World Heritage List.

This guide separates the memorable origin story from the historical record and shows how to explore the heritage without romanticising the dangerous work or the toxic metal behind it.

## The tub-maker story: legend, not a discovery report

The familiar tale says that in **1490** a maker of wooden tubs found unusually heavy, shining droplets while soaking a tub in a creek. The discoverer is often called **Škafar**, a name linked to the Slovenian word for a tub.

Visit Idrija explicitly presents the tub-maker episode as a **legend**. It is a powerful local origin story, but it should not be treated as an eyewitness account or proof of exactly who first identified the deposit. The date itself has firmer institutional support: UNESCO records that mercury was first found at Idrija in **1490**.

That distinction matters. Folklore helps a community explain its beginnings; historical interpretation asks what surviving records and material evidence can establish.

## What the evidence establishes

Idrija developed around mercury extraction for roughly five centuries. UNESCO identifies Idrija and Almadén as the two largest mercury mines in the world until recent times and describes their preserved shafts, galleries, surface installations, miners' housing and civic buildings as evidence of a specialised mining society.

Mercury's chemical symbol is \`Hg\`. Because the metal was used in amalgamation to extract silver and gold, production in Idrija and Almadén became part of an intercontinental economic system from the early modern period onward. The Idrija Municipal Museum explains that mercury from the two mines was used in South American precious-metal production from the mid-16th century.

The heritage therefore tells more than a story of engineering. It also raises questions about labour, illness, pollution and the unequal costs of global trade. UNESCO notes plainly that mercury is a pollutant dangerous to human health.

## Why Idrija is a UNESCO World Heritage site

In **2012**, UNESCO inscribed the serial property **Heritage of Mercury: Almadén and Idrija**. The designation joins sites in Slovenia and Spain because together they preserve the technical, urban and social evidence of mercury extraction and its worldwide trade.

In Idrija, the protected story extends beyond the underground workings. It includes infrastructure, storage, administrative buildings and places associated with miners' lives. That is why a useful visit combines at least two perspectives:

- the underground working environment at Anthony's Main Road;
- the town-wide historical interpretation at Gewerkenegg Castle and the Idrija Municipal Museum.

## How to experience it today

### 1. Enter through Anthony's Main Road

Anthony's Main Road leads into the oldest visitor-accessible part of the Idrija mine. Visits are organised experiences rather than independent cave walks. Check the [official mine schedule](https://www.cudhg-idrija.si/en/schedule) and reserve ahead, especially for a specific language or during busy periods.

Expect stairs, low temperatures and an underground environment. Follow the guide, remain on the visitor route and disclose relevant mobility, respiratory or health concerns before booking. The visit is industrial heritage interpretation—not an invitation to enter closed workings or collect minerals.

### 2. Continue to Gewerkenegg Castle

The castle was not a noble residence. From the early 16th century until the end of the Second World War it housed the mine administration, and guarded cellars were used to store mercury. Today its museum exhibitions explain mining technology, workers' lives, Idrija lace and the connections between Idrija and Almadén.

Confirm current hours and admission on the [Idrija Municipal Museum visitor pages](https://www.muzej-idrija-cerkno.si/en/obiscite-nas/kje-smo/) before setting out. A combined mine-and-museum visit gives better context than either attraction alone.

### 3. Add the smelting story if time allows

The Hg Smelting Plant explains how mercury-bearing ore became liquid metal and why the process was both technically important and hazardous. It completes the route from geology to extraction, processing and export. Do not handle unidentified mineral material or assume that historic industrial sites are harmless because they are museums.

## A practical car-light day trip

Idrija lies **56 kilometres west of Ljubljana**. The official destination site says it can be reached directly by bus from Ljubljana; rail travellers should change to a bus at Logatec. Check the current operator timetable before travel, because connections and journey times can change.

A sensible sequence is:

1. Take a morning bus to Idrija and walk from the bus station into the compact centre.
2. Join a pre-booked underground tour at Anthony's Main Road.
3. Allow time for lunch; Idrija žlikrofi, the town's protected filled pasta, are the most characteristic local choice.
4. Visit Gewerkenegg Castle and its museum exhibitions.
5. Add the smelting plant only if opening times and your return bus leave enough margin.

Individual opening hours do not always align, so build the day around the timed mine tour rather than assuming every site is continuously open. The official multi-attraction package currently advertises adult and child options, but verify the live price and inclusions before purchase.

## Visit responsibly

- **Treat mercury as hazardous.** Do not touch droplets, ore or residues outside supervised exhibits.
- **Respect barriers and guides.** Historic workings are controlled environments, not shortcuts or adventure playgrounds.
- **Dress for underground conditions.** Wear closed, stable footwear and bring a warm layer even when the surface is mild.
- **Read beyond the machinery.** Notice the evidence of miners' housing, administration and family life as well as technical achievements.
- **Keep legend and history distinct.** Retell the Škafar story as local tradition, while using UNESCO and museum evidence for historical claims.

## Direct sources

Information was checked on **16 September 2026**:

- [UNESCO World Heritage Centre: Heritage of Mercury, Almadén and Idrija](https://whc.unesco.org/en/list/1313/)
- [Idrija Municipal Museum: UNESCO Heritage](https://www.muzej-idrija-cerkno.si/en/obiscite-nas/unesco-heritage/)
- [Visit Idrija: UNESCO mercury story](https://www.visit-idrija.si/en/experience/2019092609005398/unesco-mercury-story)
- [Visit Idrija: how to reach Idrija](https://www.visit-idrija.si/en/destination/how-to-reach-us/)
- [Visit Idrija: Discover the secrets of mercury](https://www.visit-idrija.si/en/plan-your-stay/packages/135/discover-the-secrets-of-mercury/)`,
    category: "Vodniki",
    author: "Uredništvo Blog Lab",
    status: "published",
    createdAt: "2026-09-16T14:58:17+02:00",
    updatedAt: "2026-09-16T14:58:17+02:00",
  },
  {
    id: "ljubljana-marathon-2026-runner-spectator-guide",
    title: "Ljubljana Marathon 2026: Runner and Spectator Guide",
    excerpt: "Plan the 30th Ljubljana Marathon weekend with confirmed race times, bib collection, Expo access, spectator advice and practical city transport tips.",
    seoDescription: "A practical guide to the 30th Ljubljana Marathon on 17–18 October 2026, including race times, bib pickup, Expo, course access and spectator tips.",
    content: `The **30th NLB Ljubljana Marathon** takes place on **Saturday 17 and Sunday 18 October 2026**, turning the Slovenian capital into a weekend-long running venue. The programme includes children’s and school events, a 10-kilometre race, a half marathon and the full marathon, while the free Running Expo opens two days earlier.

This guide is for registered runners, companions and visitors deciding how to experience the weekend. Information was checked against the organiser’s official pages on **16 September 2026**.

## Registration has closed

The organiser states that standard online registration closed at **24:00 on 15 September 2026** and that late registration is not available at the event. Do not travel expecting to buy a marathon or half-marathon place at the start.

Registered participants should use the official account and organiser instructions for any permitted changes. Never buy a bib informally: identity, emergency details and timing data must match the authorised runner. The organiser’s FAQ explains the official procedure and fees for post-deadline name, bib or distance changes.

## Key weekend times

The official programme confirms:

- **Saturday 17 October:** the 10 km race starts at **16:30**;
- **Sunday 18 October:** the marathon and half marathon start at **09:00**;
- the children’s programme begins on Saturday, with individual schedules published by the organiser;
- the Running Expo operates from **15 to 17 October**.

The full marathon distance is 42.195 km, the half marathon is 21.098 km and the Saturday road race is 10 km. Check the final organiser schedule before leaving your accommodation because assembly times and access rules are earlier than the race starts.

## Collecting your bib and starter pack

Bib collection takes place only at the NLB Ljubljana Marathon Expo at **Ljubljana Exhibition and Convention Centre, Dunajska cesta 18**. The official collection hours are:

- Thursday 15 October: **09:00–19:00**;
- Friday 16 October: **09:00–19:00**;
- Saturday 17 October: **09:00–21:00**.

Bring the official voucher—printed or displayed as a QR code on your phone—and valid identification. Retrieve the voucher from the confirmation email or the organiser’s \`MY ACCOUNT\` area before travelling, rather than searching for it in a crowded hall.

The organiser advises runners to wear the bib visibly on the front and complete the emergency-information section on its reverse. Do not fold over or cover the timing component.

## The Running Expo is open to visitors

The Expo is at the same exhibition centre and has **free admission**. It is open:

- Thursday 15 October, 09:00–19:00;
- Friday 16 October, 09:00–19:00;
- Saturday 17 October, 09:00–21:00.

The announced programme includes running equipment, sports nutrition, international race organisers, a 30th-anniversary exhibition and a “Made in Slovenia” avenue featuring local food and crafts. Non-runners can visit, but the busiest periods are likely to coincide with bib collection. Give participants space near collection points and do not treat product samples as a substitute for your normal race nutrition.

## Start, finish and course character

The organiser describes the marathon route as flat. The marathon and half marathon start on **Slovenska cesta** and finish at **Kongresni trg**. The course crosses central streets and outer parts of Ljubljana under full road closure.

For marathon runners, the official limit is **six hours**. Anyone who has not completed the first 20 km in 2 hours 45 minutes gross time is redirected to the finish and listed with the half-marathon results. Train for this rule rather than trying to solve it with an unusually fast opening pace.

The organiser lists eight refreshment stations and six water stations on the marathon route. Use only products already tested during training. October conditions can range from cool rain to unexpectedly warm sun, so final clothing and hydration choices should follow the actual forecast, not a long-range assumption.

## A sensible final-month plan

With the event about a month away, fitness gains must be balanced against injury risk. Avoid suddenly increasing weekly distance or adding unfamiliar speed sessions. Registered runners should follow an established plan, taper appropriately for their distance and seek qualified medical advice for persistent pain, illness or concerns about exercise.

A practical checklist:

1. Confirm that registration, name and distance are correct.
2. Book accommodation and plan Expo collection before race day.
3. Test shoes, socks, breakfast and fuel during training—nothing new on race morning.
4. Study the official course, start zone and baggage instructions when final versions are published.
5. Save emergency contacts and carry essential medication as advised by a clinician.
6. Check the official weather forecast and organiser notices during race week.

Do not run with fever, chest pain, severe breathing difficulty or an injury that changes your gait. A start number is not an obligation to start.

## Getting around without a car

Central road closures make walking and public transport the practical default. Registered marathon participants receive free public transport on race day with their bib, according to the organiser. Confirm exactly which services and period this covers before travelling.

The Expo at Dunajska cesta 18 is north of the city centre and is served by urban transport. On race weekend, allow for rerouted buses and longer walks around closures. Ljubljana railway and bus stations are within walking distance of the Expo for many visitors, while the start and finish area lies farther south in the centre.

Drivers should use official traffic and parking information published closer to the event. Never move barriers, enter a closed street or park across an emergency route, even if navigation software still suggests it.

## How to watch responsibly

Spectators can make the event better without obstructing it:

- choose a viewing point before roads close;
- stand behind barriers and leave crossings clear;
- never step onto the course for a photograph;
- keep dogs controlled and away from runners;
- supervise children near crowded corners;
- follow police, marshal and medical instructions;
- take rubbish away or use event bins.

If following a specific runner, use the organiser’s official mobile app or live-tracking information when available. Mobile data and GPS can lag in crowded areas, so agree on a post-race meeting point in advance.

The finish area at Kongresni trg will be busy. Give runners time to pass through medals, refreshments and medical checks before arranging a reunion away from the narrowest exits.

## If you are visiting rather than racing

The marathon is also a chance to see Ljubljana as a sporting city. Visit the free Expo, watch a race section and explore open parts of the pedestrian centre on foot. Expect a different city rhythm: some usual bus routes, taxi approaches and museum access points may be altered.

Businesses outside the closed course remain worth visiting, but make reservations flexible and check access. Do not plan a tight airport or rail connection immediately after crossing the city during the Sunday race.

## Final checks before the weekend

- Reopen the official schedule, course and traffic pages shortly before travel.
- Download or print the bib voucher and pack identification.
- Confirm your start zone, baggage procedure and meeting point.
- Follow the actual weather forecast and medical guidance.
- Use only official channels for registration changes and tracking.
- Allow extra time throughout central Ljubljana.

The best marathon weekend is not defined only by a personal best. Good preparation, realistic pacing and respect for closures help runners, spectators, residents and emergency teams share the city safely.

## Verified sources

- [NLB Ljubljana Marathon: official 2026 event page](https://ljubljanskimaraton.si/en/)
- [Official marathon rules, route and registration information](https://ljubljanskimaraton.si/en/marathon)
- [Official bib collection instructions](https://ljubljanskimaraton.si/en/information-for-runners/starting-numbers-and-chips)
- [Official Running Expo programme and hours](https://ljubljanskimaraton.si/en/running-expo)
- [Official runner FAQ](https://ljubljanskimaraton.si/en/faq)`,
    category: "Šport",
    author: "Uredništvo Blog Lab",
    status: "published",
    createdAt: "2026-09-16T09:00:37+02:00",
    updatedAt: "2026-09-16T09:00:37+02:00",
  },
  {
    id: "mineralfest-ljubljana-2026-visitor-guide",
    title: "MineralFest Ljubljana 2026: A Visitor’s Guide",
    excerpt: "Plan a practical visit to Ljubljana’s two-day mineral, fossil and jewellery fair, with verified dates, ticket prices, highlights and car-light access.",
    seoDescription: "Visit MineralFest Ljubljana on 19–20 September 2026: verified hours, ticket prices, exhibitions, workshops and practical Cankarjev dom access tips.",
    content: `MineralFest Ljubljana returns to Cankarjev dom on **19 and 20 September 2026**, offering an indoor weekend stop for visitors interested in geology, fossils, jewellery and hands-on craft. The 2026 edition marks the fair’s tenth anniversary and brings together Slovenian and international exhibitors alongside special displays and activities.

This guide uses information checked on **15 September 2026**. Event details can still change, so recheck the organiser and venue pages before setting out.

## Dates, hours and venue

The official tourism listing gives the event window as **Saturday 19 September from 09:00 until Sunday 20 September at 19:00**. Cankarjev dom lists the fair on both days in its **Large Reception Hall** (*Velika sprejemna dvorana*), in central Ljubljana.

The venue is at Prešernova cesta 10, beside Republic Square and a short walk from the pedestrianised historic centre. If you are staying centrally, walking is usually the simplest choice. For longer journeys, consult Ljubljana Passenger Transport’s current journey planner and allow extra time for any European Mobility Week diversions.

## What tickets cost

Cankarjev dom’s event listing shows these **door prices**:

- adults: **€8.50**;
- students, seniors and disabled visitors: **€7.50**;
- primary-school children: **€4.00**;
- family ticket: **€21.00**.

The organiser also advertises lower advance prices, including **€7.50 for adults**, **€6.50 for pupils, students, pensioners and disabled visitors**, and **€3.50 for primary-school children**. Because eligibility wording differs slightly between listings, select the correct concession category in the official ticket shop and bring any supporting identification that may be requested.

Do not rely on an old screenshot or social-media post for the final price. Use the linked Cankarjev dom ticket page immediately before purchase and check whether a ticket is valid for one day or the whole weekend.

## What you can see and do

The official Slovenian tourism listing describes a mix of mineral, fossil, jewellery and esoterica exhibitors. It also announces:

- **The Enchanting World of Minerals**, a special display by the Slovenian Museum of Natural History;
- **Loški Kremen**, presented by Gorazd and Blaž Tomc;
- wire-jewellery making;
- gemstone-cutting activities;
- a Wheel of Fortune activity.

Treat workshop places and activity times as limited unless the organiser confirms otherwise. If one activity is essential to your visit, contact the organiser or check the latest programme rather than assuming it runs continuously.

## A useful plan for first-time visitors

Allow roughly **90 minutes to three hours**, depending on whether you want to shop, attend activities or examine the special exhibitions carefully. Arriving near opening time may give you more space to speak with exhibitors; later visits can be livelier but busier.

Start with the museum-backed mineral display before browsing commercial stands. It gives scientific context for colour, crystal form and geological origin, making the sales area easier to assess. Then compare labels and prices across several exhibitors before buying.

Families can make the visit more focused by choosing a small question in advance: how fossils form, why minerals have different colours, or how a rough stone becomes jewellery. Young children should remain supervised around fragile, sharp or small objects.

## Buying responsibly

A beautiful specimen does not automatically have a clear or ethical origin. Ask the seller:

1. What is the mineral or fossil?
2. Where was it collected?
3. Is the label included?
4. Has it been treated, dyed, repaired or assembled?
5. Are there export or import restrictions for your destination?

Keep the receipt and written identification. Rules for collecting, selling and transporting geological or palaeontological material vary by country, and airline baggage rules are separate from customs rules. If provenance is vague or a protected fossil claim sounds extraordinary, leave it and seek expert advice.

Claims that crystals diagnose or treat illness are not a substitute for medical care. Enjoy minerals for their geology, craft, beauty or cultural meaning without treating unverified health claims as evidence.

## Accessibility and comfort

Cankarjev dom publishes visitor accessibility information, but individual needs differ. Contact the venue in advance about step-free routes, wheelchair spaces, assistance or companion-ticket conditions. The fair can involve prolonged standing, bright display lighting and crowded aisles; plan breaks and avoid blocking circulation while examining a stand.

Bring a small reusable bag with padding if you expect to buy delicate pieces. Heavy specimens become uncomfortable quickly, so consider weight before continuing a full day of sightseeing.

## Make it part of a Ljubljana day

MineralFest works well as the indoor anchor of a city day. From Cankarjev dom, most visitors can walk to Congress Square, the National Museum of Slovenia or the historic centre. Check each institution’s current opening hours and ticket requirements separately.

For a quieter itinerary, visit the fair in the morning, take lunch in the centre and spend the afternoon walking beside the Ljubljanica. Keep purchases secure, dry and out of direct sun rather than carrying them loose through a crowded market or café.

## Before you go

- Reconfirm the programme, prices and opening times on 18 or 19 September.
- Buy only through the official organiser or Cankarjev dom ticket channel.
- Use public transport or walk where practical; do not assume central parking will be available.
- Ask before photographing people, private collections or sales displays.
- Supervise children and handle objects only with the exhibitor’s permission.
- Request provenance and treatment information before buying.

MineralFest is most rewarding when approached as more than a shopping hall: it is a chance to connect attractive objects with the science, craft and responsible collecting practices behind them.

## Verified sources

- [MineralFest Slovenia: official organiser and 2026 event information](https://www.mineralfest.si/)
- [Cankarjev dom: MineralFest Ljubljana event and ticket prices](https://www.cd-cc.si/en)
- [Official Cankarjev dom ticket shop](https://vstopnice.cd-cc.si/)
- [Slovenian Tourist Board: MineralFest Ljubljana 2026](https://www.slovenia.info/en/things-to-do/events/12980-mineralfest-ljubljana-2026)
- [Cankarjev dom: accessibility information](https://www.cd-cc.si/en/accessibility)`,
    category: "Aktualno",
    author: "Uredništvo Blog Lab",
    status: "published",
    createdAt: "2026-09-15T20:59:27+02:00",
    updatedAt: "2026-09-15T20:59:27+02:00",
  },
  {
    id: "kurent-ptuj-unesco-heritage-guide",
    title: "Kurent in Ptuj: UNESCO Heritage Beyond the Carnival",
    excerpt: "Meet Slovenia’s best-known Shrovetide figure, separate living tradition from popular legend, and plan a respectful visit to Ptuj even outside carnival season.",
    seoDescription: "Discover the Kurent tradition of Ptuj, its UNESCO-listed door-to-door rounds, meanings, costume and practical ways to experience the heritage responsibly.",
    content: `With a shaggy sheepskin outfit, a belt of heavy bells and a dramatic headpiece, the Kurent is one of Slovenia’s most recognisable traditional figures. Visitors often hear that Kurenti “chase winter away.” That is a useful introduction to the symbolism, but it is not a complete history—and the figure is not simply a carnival mascot.

The heritage recognised by UNESCO is specifically the **door-to-door rounds of Kurenti**, a living Shrovetide custom rooted in communities around Ptuj. Understanding that distinction makes a visit more interesting and more respectful.

## What UNESCO actually recognised

UNESCO inscribed the door-to-door rounds of Kurenti on the Representative List of the Intangible Cultural Heritage of Humanity in **2017**. The custom is practised between **Candlemas on 2 February and Ash Wednesday**, so its exact end date changes with the Christian calendar.

Groups move from house to house, jumping and ringing the bells worn around their waists. UNESCO’s description also notes the presence of one or more accompanying devils and the importance of families, schools, museums and associations in passing knowledge and skills to younger generations.

The inscription recognises a community practice, not ownership of every horned or feathered costume that appears at a parade. It also does not mean that UNESCO has certified the popular supernatural explanations as historical fact.

## Tradition, belief and what history can prove

The familiar interpretation says that the noise and movement drive winter away and call in spring. Visit Ptuj presents this as an **ancient belief** associated with the Kurent. It belongs to the meaning people give the custom and should be described as belief or folklore—not as a scientifically verifiable event.

Historical certainty is more limited. Carnival customs change as communities transmit them, and their origins are not captured in one simple founding document. It is safer to say that the Kurent tradition has deep roots in the Shrovetide culture of north-eastern Slovenia than to claim a precise prehistoric age.

The living tradition has changed too. Visit Ptuj notes that in the past the outfit was worn by adult men, while safeguarding today involves a broader network of families, societies, schools and museums. Tradition is not frozen: continuity depends on people practising, teaching and adapting it.

## Kurent or Korant?

You may encounter both names. **Kurent** is widely used in Ptuj and in international descriptions; **Korant** is common in parts of the surrounding countryside. Treat the local choice of name as part of regional identity rather than correcting it.

Costumes also vary. Official Ptuj tourism material distinguishes feathered and horned types. Do not assume that every group should look identical: details can indicate the wearer’s community and local tradition.

## The outfit is not a souvenir costume

A Kurent outfit combines sheepskin clothing, bells and an elaborate headpiece. Visit Ptuj states that a complete outfit can weigh up to **40 kilograms**. The weight, heat, noise and constant movement help explain why the rounds demand stamina and learned practice.

Visitors should not enter a procession, grab bells or touch a headpiece for a photograph unless the wearer explicitly invites it. Ask before photographing people at close range, especially children and participants preparing away from the public route.

Buying a mass-produced mask and treating it as comic fancy dress can flatten a living custom into decoration. A better souvenir supports a local maker, museum or heritage organisation and comes with an explanation of what it represents.

## How to experience the heritage outside Shrovetide

You do not need to visit during the busiest carnival weekend. **Kurent House** at Murkova ulica 7 in Ptuj presents the character through an interactive visitor experience and operates under the auspices of the Slovenian National Commission for UNESCO.

At the time of verification on **15 September 2026**, the official listing advertised summer opening from Wednesday to Sunday, 12:00–18:00, with Thursday closed; visits take place on the hour and capacity is limited. Hours can change, so check the official page and online ticket availability before travelling.

The Ptuj-Ormož Regional Museum at Ptuj Castle also holds a traditional carnival-mask collection. Combining the Kurent House with the castle gives useful context: one focuses tightly on the living figure, while the museum places masks within the wider culture of the region.

Allow time to walk through Ptuj’s historic centre rather than treating the heritage stop as a quick photo opportunity. Kurent House, the Tourist Information Centre and the route toward the castle are close enough to combine on foot for most visitors.

## Visiting during Kurentovanje

Kurentovanje is Ptuj’s large carnival festival, but the UNESCO-listed practice is broader than the organised event. Village rounds and community encounters are central to the heritage.

If planning a future carnival visit:

- confirm the year’s exact dates and programme on the official festival or Visit Ptuj website;
- book accommodation early;
- use public transport where practical and expect street closures;
- dress for winter weather and long periods outdoors;
- protect young children’s hearing around large groups of bells;
- stay behind barriers and follow stewards’ instructions;
- never describe every masked participant as a performer hired for tourists.

Do not publish or rely on a future festival date until the organiser has confirmed it. Shrovetide dates move from year to year, and individual rounds may not be public events.

## A respectful visitor checklist

Before your visit:

1. Check current opening hours, tickets and language options.
2. Distinguish the UNESCO-listed rounds from the wider festival programme.
3. Refer to “belief,” “tradition” or “folklore” when discussing the expulsion of winter.
4. Ask permission before close-up photographs or physical contact with costume elements.
5. Give moving groups space; bells, headpieces and crowds require room.
6. Support the communities safeguarding the custom through official visits and local work.

The Kurent is memorable because the sight and sound are extraordinary. The deeper reason to visit Ptuj is quieter: this is heritage kept alive through repeated community practice, not a legend staged only for spectators.

## Verified sources

- [UNESCO: Door-to-door rounds of Kurenti](https://ich.unesco.org/en/RL/door-to-door-rounds-of-kurenti-01278)
- [UNESCO decision 12.COM 11.B.30](https://ich.unesco.org/en/decisions/12.COM/11.B.30)
- [Visit Ptuj: Kurent](https://visitptuj.eu/en/see-do/culture-heritage/sightseeing/kurent-2/)
- [Visit Ptuj: Kurent House](https://visitptuj.eu/en/see-do/culture-heritage/sightseeing/kurent-house/)
- [Ptuj-Ormož Regional Museum](https://pmpo.si/en/)`,
    category: "Vodniki",
    author: "Uredništvo Blog Lab",
    status: "published",
    createdAt: "2026-09-15T15:00:20+02:00",
    updatedAt: "2026-09-15T15:00:20+02:00",
  },
  {
    id: "soca-rafting-early-autumn-2026",
    title: "Early Autumn Rafting on the Soča: A Safety-First Guide",
    excerpt: "Plan a mid-September Soča rafting or kayaking trip with the 2026 navigation hours, permit rules, cold-water equipment and honest advice on choosing a guide.",
    seoDescription: "A practical safety-first guide to rafting and kayaking the Soča in autumn 2026, including permits, navigation hours, equipment, river flow and guided trips.",
    content: "# Early Autumn Rafting on the Soča: A Safety-First Guide\n\nThe Soča is famous for its clear emerald colour, but its appearance can disguise the seriousness of the river. It is a cold Alpine waterway with fast current, technical rapids and sections that are unsuitable for inexperienced paddlers.\n\nMid-September is a particularly useful moment to plan carefully. The official 2026 navigation regime changes on **16 September**, shortening permitted hours in parts of the river system. Water temperature, flow, weather and daylight can also feel very different from midsummer.\n\nFor a first visit, a guided rafting trip with an experienced local operator is usually the most sensible way to experience the river. Independent kayaking belongs to paddlers who can honestly assess their skills, read water, perform rescues and select a section appropriate to current conditions.\n\n## The official 2026 navigation rules\n\nNavigation on regulated sections of the Soča and Koritnica is permitted only during specified dates and hours. A valid permit is required to use the marked entry and exit points, and access is allowed only at those designated places.\n\nThe official river-management website lists these hours for the autumn period beginning **16 September 2026**:\n\n- **Sector 1 – Bovec:** 09:00–18:00, from 16 September to 31 October;\n- **Sector 2 – Kobarid:** 10:00–18:00;\n- **Sector 3 – Tolmin:** 10:00–17:00, from 16 September to 31 October.\n\nThese are the legal navigation windows, not guaranteed departure times for commercial tours. Operators may cancel, delay or change a trip when water, weather, group ability or safety requires it.\n\nPermits can be bought online, at tourist information centres and through larger tourism providers. Ask your operator before paying: a guided-tour price may or may not include the required permit, and procedures can change.\n\n## Do not choose a trip by photograph alone\n\n“Rafting on the Soča” can describe different river sections and different levels of difficulty. A calm-looking promotional image does not tell you about the entire route.\n\nBefore booking, ask:\n\n- Which exact entry and exit points will be used?\n- How long is the time on the water, separate from changing and transport?\n- What swimming ability is required?\n- What are the operator's age, weight and health restrictions?\n- Is the navigation permit included?\n- Which protective equipment is provided?\n- What happens if the river level or weather makes the planned section unsuitable?\n- Is transport back to the base included?\n\nTell the provider honestly about weak swimming, injuries, medical conditions and previous paddling experience. The easiest way to create risk is to let embarrassment decide which trip you join.\n\n## Why guided rafting suits most visitors\n\nA raft places several guests with a guide in one craft. It still requires active participation: you must listen to commands, paddle, brace your feet correctly and know what to do if you fall into the water.\n\nA professional briefing should cover the paddling commands, safe sitting position, how to hold the paddle, what to do during a capsize or swim, and how to respond to a throw rope. Pay attention even if you have rafted elsewhere. River hazards and rescue plans are specific to the section and the day.\n\nSit-on-top boats and “easy kayaking” packages are not automatically risk-free alternatives. Confirm the craft, route, supervision and prerequisites rather than relying on the activity name.\n\n## Independent kayaking requires real competence\n\nThe river authority describes the Soča as a cold Alpine river with a steep gradient and significant difficulty in places. It recommends qualified local guides for visitors who do not know the river.\n\nIndependent paddlers should study the official sector map, forbidden sections, entry and exit points and current notices before launching. Scout unfamiliar hazards from a safe place and never follow another group blindly.\n\nDo not paddle alone. Your group should have an agreed rescue plan, appropriate first-aid knowledge and the ability to recover a swimmer and equipment. A permit is not a certificate of competence and does not mean conditions are safe.\n\nThe official site says downstream navigation is not recommended when flow at the Log Čezsoški measuring station is above **40 m³/s**. That threshold is not the only safety test: low water, debris, damaged equipment, poor visibility, cold, fatigue and lack of skill can also make a trip unsafe.\n\n## Essential cold-water equipment\n\nThe river manager recommends a helmet, buoyancy aid, neoprene suit, neoprene footwear, an anorak, a rescue rope of at least 15 metres, a first-aid kit and a knife.\n\nOn a guided trip, ask what is supplied and what you must bring. Equipment needs to fit correctly; an oversized helmet or loose buoyancy aid is not adequate protection.\n\nA sensible personal packing list includes:\n\n- swimsuit and towel;\n- synthetic base layer if the operator recommends one;\n- dry clothes and warm layer for afterwards;\n- secure eyewear strap if needed;\n- any essential medication disclosed to the guide;\n- water and a small snack;\n- sunscreen for exposed skin.\n\nLeave valuables at the base if secure storage is offered. Do not take a phone onto the river unless the operator approves a properly secured waterproof solution.\n\n## Alcohol and the river do not mix\n\nNavigation while under the influence of alcohol or other substances is prohibited. Save beer, wine and celebratory drinks for after the activity, once everyone is off the water and transport is arranged.\n\nDo not treat an afternoon rafting slot as an extension of a long lunch. Cold water and current punish slow reactions.\n\n## A realistic half-day from Bovec\n\nAllow more time than the advertised paddling duration. A typical outing also involves registration, permit checks, changing, equipment fitting, a safety briefing, transport to the launch site, the descent, return transfer and a shower or change of clothes.\n\nArrive early and eat a light meal beforehand. Heavy food immediately before rafting can be uncomfortable, while skipping food entirely can leave you cold and tired.\n\nAfterwards, keep the day flexible. A short walk in Bovec, a meal from a local provider or a visit to a viewpoint is more realistic than racing to a distant attraction.\n\n## Weather, flow and cancellation decisions\n\nCheck the official river notices and the Slovenian Environment Agency data on the morning of the trip. A sunny forecast in Bovec does not by itself confirm safe navigation upstream or downstream.\n\nRespect a cancellation. A responsible operator may offer another section, another time or a land-based alternative. Pressure to “get what you paid for” should never override the guide's decision.\n\nIf thunderstorms, very high flow or another hazard changes the plan, use the day for a marked valley walk, a museum or a cultural site. Never launch independently simply because a commercial trip was cancelled.\n\n## Getting there without creating a transport problem\n\nBovec is the main base for many water-sports providers, while regulated entry and exit points extend through the Bovec, Kobarid and Tolmin sectors. Guided operators commonly organise river transfers, but you should confirm this in writing.\n\nIf arriving by public transport, verify the current timetable and the walking distance from your stop to the operator's base. Autumn services may differ from summer schedules.\n\nIndependent paddlers must use authorised access points and lawful parking. Do not block emergency access, private land, farm roads or the space operators need for trailers and rescue vehicles.\n\n## Respect the river corridor\n\nUse toilets and changing facilities rather than the riverbank. Pack out all rubbish, including food scraps, tape and damaged equipment. Do not use soap or shampoo in the river.\n\nKeep noise low near homes and campsites. Enter and leave only at marked points, and do not create shortcuts down fragile banks. Camp only at designated campsites.\n\nThe Soča is not a studio set built around an activity. It is a living river corridor shared by wildlife, residents, anglers, walkers, emergency services and other paddlers.\n\n## Final checklist\n\nBefore leaving your accommodation, confirm:\n\n1. the operator, meeting point and start time;\n2. the exact activity and river section;\n3. swimming, age and health requirements;\n4. whether the permit is included;\n5. what equipment and transport are provided;\n6. current flow, weather and official notices;\n7. dry clothing and medication;\n8. a backup plan if the trip is cancelled.\n\nThe best Soča experience is not the most dramatic one. It is the trip that matches the day's river, the group's real ability and the official rules—and brings everyone back warm, safe and eager to see more of the valley.\n\n## Verified sources\n\n- Soča navigation authority, 2026 rules, hours, safety guidance and equipment: https://www.soca-plovba.si/english/\n- Soča Valley official tourism portal, 2026 navigation-season notice and permit information: https://www.soca-valley.com/en/soca-valley/news/2026031909172449/the-navigation-season-on-the-soca-river-begins/\n- Official online river-permit portal: https://gosoca.si/\n- Soča Valley official visitor portal: https://www.soca-valley.com/en/\n- Slovenian Environment Agency, hydrological information: https://www.arso.gov.si/en/water/",
    category: "Šport",
    author: "Uredništvo Blog Lab",
    status: "published",
    createdAt: "2026-09-15T07:07:19.000Z",
    updatedAt: "2026-09-15T07:07:19.000Z",
  },
  {
    id: "european-mobility-week-2026-car-light-slovenia",
    title: "European Mobility Week 2026: A Car-Light Slovenia Trip",
    excerpt: "Use European Mobility Week to plan a practical Ljubljana stay and rail day trips, with current advice on tickets, bicycles, accessibility and disruptions.",
    seoDescription: "Plan a car-light Slovenia trip for European Mobility Week 2026 with practical tips for Ljubljana buses, bike sharing, rail day trips and accessibility.",
    content: "European Mobility Week runs from **16 to 22 September 2026**, ending with Car-Free Day. The European Commission describes it as an annual campaign in which towns and cities test cleaner transport ideas, introduce measures and invite residents to reconsider everyday journeys. The 2026 theme is **“Mobility for Everyone”**, with particular attention to intergenerational fairness.\n\nFor visitors, the week is a useful prompt rather than a promise that every Slovenian town will close the same streets or run the same programme. Local events, diversions and temporary traffic rules are decided locally, so check municipal notices shortly before travelling.\n\n## Why Slovenia works well for a car-light break\n\nSlovenia is compact, and Ljubljana is an easy base for combining walking, city buses and rail day trips. Much of Ljubljana's historic centre is pedestrianised. The official tourism portal lists walking, city buses, BicikeLJ bike sharing and the free electric Kavalir vehicles among the ways to move around; Kavalir is intended especially for older people, visitors with reduced mobility and anyone who finds longer walks difficult.\n\nA car-free trip still needs planning. Rail engineering works, replacement buses and seasonal timetables can change a route. Use the Slovenian Railways timetable on the day of travel and read its live travel notices before buying a ticket.\n\n## A practical three-day plan\n\n### Day 1: Ljubljana on foot, by bus and shared bike\n\nBegin in the pedestrian centre around Prešeren Square, the riverside markets and the castle hill. Distances are short enough to walk, while a city bus is useful for places beyond the centre.\n\nLjubljana buses accept the Urbana card; contactless bank-card payment is also available, but the transfer conditions differ. Check the current fare and payment instructions on the official city-bus page before boarding.\n\nBicikeLJ is designed for short point-to-point rides between docking stations. Register before you need a bicycle, inspect the brakes and tyres, and confirm that the return has been accepted at the docking point. Walk the bicycle in crowded pedestrian areas and use lights after dusk.\n\n### Day 2: choose one rail day trip\n\nPick a destination served by rail rather than trying to combine several towns. **Škofja Loka** offers a medieval old-town walk after the final connection from the railway station; **Celje** works for urban history and its hilltop castle; **Maribor** combines the Drava riverfront with a compact centre. These are ideas, not fixed itineraries: search the exact journey in the official timetable and allow time for the return connection.\n\nAt Ljubljana station, construction can alter platforms and access routes. Check departure screens and current railway notices, and arrive earlier than you would at a small station.\n\n### Day 3: make the final kilometre part of the visit\n\nChoose a nearby nature or heritage stop that can be reached by train or scheduled bus, then walk only on signed public routes. Save the return timetable offline, carry water and a light rain layer, and avoid relying on the last service of the day when a missed connection would leave no alternative.\n\n## Taking a bicycle on the train\n\nDo not assume every train accepts a full-size bicycle. Slovenian Railways marks eligible services with a bicycle symbol, capacity is limited, and staff may refuse bicycles when space or safety requires it. The operator advises avoiding weekday peaks from 06:00–08:00 and 14:00–16:00; tourist services can also be crowded on weekends and holidays. Replacement buses generally cannot carry bicycles.\n\nA folding bicycle packed as luggage or a rental at the destination may be simpler. Whatever you choose, keep doors and aisles clear and follow staff instructions.\n\n## Accessibility and inclusive planning\n\n“Mobility for Everyone” is a reminder that walking and cycling are not equally practical for every traveller. Ljubljana's Kavalir service can help inside the pedestrian zone, while railway assistance may need advance notice. Check step-free access for the exact station and train, and contact the operator before travel rather than assuming every connection is accessible.\n\nBuild in rest stops, choose realistic distances and keep a weather-safe alternative. Travelling car-light should increase freedom, not turn the holiday into an endurance test.\n\n## Before you set out\n\n- Check the local municipality or tourist-office website for Mobility Week events, closures and bus diversions.\n- Recheck rail and bus times on the day, including the final return.\n- Buy the correct ticket before boarding where required.\n- Carry a charged phone, offline directions and a backup payment method.\n- Use marked crossings and cycle routes; wear visible clothing after dark.\n- Never leave a shared bicycle outside an approved return station.\n- If you drive for one section, use an official car park or park-and-ride site and continue by public transport.\n\nEuropean Mobility Week can make a September city break more interesting, but the best result is useful beyond one campaign: fewer parking worries, slower encounters with Slovenian towns and a travel plan that leaves more room to notice the places between the landmarks.\n\n## Verified sources\n\n- [European Commission: European Mobility Week](https://transport.ec.europa.eu/transport-themes/urban-transport/european-mobility-week_en)\n- [Official European Mobility Week campaign](https://mobilityweek.eu/)\n- [Visit Ljubljana: Getting around](https://www.visitljubljana.com/en/visitors/travel-information/getting-around)\n- [Visit Ljubljana: City buses](https://www.visitljubljana.com/en/visitors/travel-information/getting-around/city-buses)\n- [Slovenian Railways: Timetable and travel updates](https://potniski.sz.si/en/)\n- [Slovenian Railways: Taking a bicycle on the train](https://potniski.sz.si/en/useful-information/take-your-bike-on-the-train/)",
    category: "Aktualno",
    author: "Uredništvo Blog Lab",
    status: "published",
    createdAt: "2026-09-14T19:02:29.000Z",
    updatedAt: "2026-09-14T19:02:29.000Z",
  },{
  id: "juliana-trail-autumn-slow-hiking-guide",
  title: "Autumn on the Juliana Trail: A Slow-Hiking Guide",
  excerpt: "Circle the Julian Alps without climbing their summits. This practical autumn guide explains how to choose stages, travel light and hike the Juliana Trail responsibly.",
  seoDescription: "Plan an autumn hike on Slovenia’s 267 km Juliana Trail, with advice on stages, accommodation, public transport, weather, safety and responsible travel.",
  content: "# Autumn on the Juliana Trail: A Slow-Hiking Guide\n\nThe Juliana Trail offers a different way to experience Slovenia’s most famous mountains. Instead of leading to the summit of Triglav, it travels **around the Julian Alps**, connecting valleys, villages, rivers, forests and cultural landscapes.\n\nThe core circular route is approximately **267 kilometres**, divided into **16 daily stages**. Official route information gives stages of roughly 18 to 25 kilometres, with more than 7,000 metres of ascent across the full circuit.\n\nFew visitors need to walk all of it. In early autumn, choosing two or three connected stages can be more rewarding—and safer—than forcing a complete itinerary through changing weather and shorter days.\n\n## Why walk the edge of the mountains?\n\nThe Juliana Trail is not a lesser version of a summit route. Its purpose is different.\n\nHigh Alpine hikes concentrate effort on ridges, rock and peaks. The Juliana Trail keeps returning to inhabited valleys, where walkers encounter farms, churches, rivers, railway towns and the different identities of Gorenjska and the Soča Valley.\n\nYou still see the high mountains, but you do not need a helmet, harness or protected climbing route to understand them.\n\nThe trail also spreads visitor movement beyond the most crowded viewpoints. That only works when hikers stay on the marked route, use local services and treat villages as homes rather than outdoor sets.\n\n## The core route in simple terms\n\nOfficial Julian Alps information describes a 16-stage loop of 267 kilometres. A separate extension toward Brda adds further stages, but first-time visitors should understand the core circuit before adding kilometres.\n\nThe trail connects well-known gateways including Kranjska Gora, the Upper Sava Valley, Bled, Bohinj, the Bača Valley, Tolmin, Kobarid and Bovec before returning toward the north-western corner of Slovenia.\n\nBecause it is circular, there is no compulsory first stage. Kranjska Gora is the conventional reference point, but travellers can begin wherever accommodation and public transport fit their trip.\n\nAlways use the current official stage descriptions and GPX files. Distances, diversions and access conditions can change.\n\n## Why September can be excellent\n\nSeptember often brings cooler walking temperatures, softer light and less pressure at major attractions than peak summer. Villages and public transport hubs remain active, while the landscape begins its transition toward autumn.\n\nIt also introduces new risks:\n\n- daylight shortens quickly;\n- morning fog can hide junctions;\n- thunderstorms and prolonged rain remain possible;\n- wet leaves make stone and roots slippery;\n- some seasonal buses reduce frequency;\n- mountain huts, tourist services and smaller accommodations may change hours;\n- the first cold spell can bring snow to higher ground.\n\nDo not plan from climate averages alone. Check the official Slovenian weather forecast and local trail information each evening and again before departure.\n\n## A good three-day approach\n\nRather than naming one “best” section, choose a base according to the landscapes you want to experience.\n\n### Option 1: lakes and villages\n\nStages around Bled and Bohinj combine famous lake views with quieter settlements and forested connections. They suit travellers who want developed transport and accommodation options.\n\nDo not assume the path follows a flat lakeside promenade. A full stage still requires several hours of walking, navigation and elevation change.\n\n### Option 2: railway and valley landscapes\n\nThe sections through the Bača Valley and toward Tolmin reveal a less familiar side of the Julian Alps. Rail access can make a linear itinerary possible, but connections are not frequent enough to improvise carelessly.\n\nCheck the exact station, stop and timetable. A place name on a map does not guarantee that every train stops there.\n\n### Option 3: the Soča Valley\n\nStages around Tolmin, Kobarid and Bovec combine river scenery with First World War heritage, villages and mountain views.\n\nThe turquoise Soča can distract from practical planning. Summer shuttle patterns may no longer apply, and popular accommodation can still fill around events. Confirm every transfer before committing to a one-way stage.\n\nFor any option, book two nights in advance and select a walk with a realistic exit point.\n\n## How difficult is it?\n\nThe Juliana Trail generally avoids the technical terrain associated with high-mountain routes, but “non-technical” does not mean easy.\n\nA stage of 18 to 25 kilometres can take most of the day once climbs, photography, meals and route-finding are included. Repeating that effort on consecutive days changes the challenge.\n\nYou should be comfortable walking for five to eight hours with a day pack. Train with the shoes and weight you intend to carry.\n\nIf you are uncertain, begin with one stage and use a fixed accommodation base. There is no award for converting a holiday into an injury.\n\n## Navigation\n\nFollow the official trail markings and carry the current route digitally and offline.\n\nA reliable setup includes:\n\n- the official Juliana Trail stage page;\n- a downloaded GPX track in a navigation app;\n- an offline topographic map;\n- a charged phone and power bank;\n- written details of accommodation and transport;\n- a simple paper overview as backup.\n\nA GPX line is not permission to cross a closure, private field or damaged bridge. Obey signs and official diversions on the ground.\n\nIf the route becomes unclear, return to the last confirmed marker. Do not create a shortcut down an unmarked slope.\n\n## Accommodation and luggage\n\nThe trail’s valley character makes guesthouses, hotels, farm stays and campsites part of the experience. Availability differs sharply between destinations.\n\nReserve each night before starting a linear stage. Confirm:\n\n- the actual address and walking distance from the trail;\n- check-in deadline;\n- whether dinner is available;\n- breakfast time or an early takeaway option;\n- luggage storage;\n- payment method;\n- cancellation conditions.\n\nDo not assume luggage transfer exists between every pair of stages. If using a commercial service, verify the provider, collection window and maximum bag size directly.\n\nA lighter pack improves both safety and enjoyment. Carry what you need for weather and emergencies, not a city wardrobe for every evening.\n\n## Public transport as part of the route\n\nTrains and buses can turn the Juliana Trail into a low-car journey, particularly around Jesenice, Bled, Bohinj and the Bača and Soča valleys.\n\nTimetables are seasonal. A route that worked in August may have fewer departures in mid-September.\n\nUse official journey planners and check service notices. For a linear day walk:\n\n1. confirm the final departure from your endpoint;\n2. save the stop’s exact location;\n3. identify an earlier backup connection;\n4. keep enough time for a delayed arrival on foot;\n5. carry funds for an emergency taxi where service exists.\n\nIf driving, do not leave one car at an informal roadside pull-off. Use authorised parking and understand whether overnight parking is permitted.\n\n## What to carry\n\nFor an autumn stage, pack:\n\n- broken-in hiking shoes with good grip;\n- waterproof jacket and rain cover;\n- warm mid-layer, hat and light gloves;\n- water and enough food for the entire stage;\n- basic first aid and blister care;\n- headlamp, even for a planned daytime finish;\n- phone, power bank and offline map;\n- sun protection;\n- emergency contact and accommodation details.\n\nWater fountains and open cafés should be treated as welcome bonuses, not guaranteed resupply.\n\nPack all rubbish out. Small organic scraps are still waste and can affect wildlife.\n\n## Weather and turnaround decisions\n\nCheck the Slovenian Environment Agency forecast, not only a global phone widget. Compare the valley forecast with any relevant mountain outlook.\n\nStart early enough to finish in daylight. If heavy rain, strong wind, thunderstorms or an abrupt temperature drop are forecast, shorten the stage or use public transport.\n\nTurn around or stop at a safe settlement when:\n\n- the marked trail is closed;\n- streams are rising;\n- visibility makes navigation uncertain;\n- someone in the group is cold, injured or exhausted;\n- the remaining distance no longer fits the daylight.\n\nCall **112** for an emergency in Slovenia. Share your route and expected arrival with someone before setting out.\n\n## Respect Triglav National Park\n\nParts of the wider route experience are connected with Triglav National Park and its surrounding biosphere landscape. Follow park rules wherever they apply.\n\nStay on marked paths, observe wildlife from a distance and keep noise low. Do not pick protected plants, build stone piles or leave food.\n\nUse official campsites and accommodation. Wild camping and sleeping in vehicles are not a responsible substitute for a booked bed, and local rules vary.\n\nDogs should be controlled and must not disturb livestock or wildlife. Check accommodation and transport policies before bringing one.\n\n## Walk through working landscapes\n\nThe trail passes through places where people farm, manage forests and move animals.\n\nClose gates exactly as you find them. Give cattle and horses space, particularly animals with young. Never feed livestock or enter a fenced pasture merely because the GPX line appears close.\n\nBuy lunch, local cheese or another product where appropriate, but ask before photographing people or private property.\n\nSlow hiking creates value when visitors participate respectfully in local economies.\n\n## One trail, many trips\n\nCompleting all 16 stages is a fine long-term goal, not a requirement.\n\nA first visit might be:\n\n- one stage linked by train;\n- a two-night lake-and-village itinerary;\n- three Soča Valley stages with pre-booked transfers;\n- a return trip each year to continue the circuit.\n\nRecord where you stopped and return in another season. The Juliana Trail is designed to connect landscapes, not to be consumed as quickly as possible.\n\n## The reward of walking around\n\nThe highest point is not always the best place to understand a mountain range.\n\nOn the Juliana Trail, Triglav and its neighbours remain on the horizon while daily life fills the foreground: a railway crossing, a village church, a pasture, a river bridge and an evening meal after a long stage.\n\nChoose a realistic section, check every connection and let early autumn set the pace. Walking around the Julian Alps can show you more of Slovenia than racing to the top.\n\n## Sources\n\n- Julian Alps, official Juliana Trail overview and stages: https://julian-alps.com/en/tour/long-distance-hiking/juliana-trail-overall-tour/59142622/\n- Slovenian Tourist Board, Juliana Trail: https://www.slovenia.info/en/things-to-do/active-holidays/hiking-backpacking/trails/juliana-trail\n- Julian Alps, responsible travel information: https://julian-alps.com/en/plan-your-trip/responsible-travel/\n- Julian Alps, mobility information: https://julian-alps.com/en/plan-your-trip/mobility/\n- Triglav National Park, official visitor information: https://www.tnp.si/en/visit/\n- Slovenian Environment Agency, weather forecasts: https://meteo.arso.gov.si/met/en/\n- Slovenian Railways, passenger journey planner: https://potniski.sz.si/en/\n- Alpine Association of Slovenia, mountain trail conditions: https://stanje-poti.pzs.si/en.php",
  category: "Šport",
  author: "Uredništvo Blog Lab",
  status: "published",
  createdAt: "2026-09-14T07:02:17.000Z",
  updatedAt: "2026-09-14T07:02:17.000Z"
}, {
  id: "first-international-day-caves-karst-slovenia-guide",
  title: "The First International Day of Caves and Karst: Explore Slovenia Underground",
  excerpt: "The world’s first UNESCO International Day of Caves and Karst was launched in Postojna. Here is why Slovenia matters—and how to visit its underground responsibly.",
  seoDescription: "Discover why Postojna hosted the first International Day of Caves and Karst in September 2026, plus practical advice for visiting Slovenia’s caves responsibly.",
  content: "# The First International Day of Caves and Karst: Explore Slovenia Underground\n\nOn **13 September 2026**, the world marked the UNESCO International Day of Caves and Karst for the first time—and its inaugural celebration took place in **Postojna, Slovenia**.\n\nA scientific conference and public programme ran from 10 to 13 September under the title *Explore, Understand and Protect*. The location was no accident. Slovenia is one of the places where the international scientific language of karst began, and Postojna remains a global centre for cave research as well as one of Europe’s best-known cave destinations.\n\nFor travellers, the new international day is an invitation to look beyond spectacular formations. Caves are living ecosystems, water systems, archives of Earth history and fragile places that must be visited on their own terms.\n\n## What UNESCO proclaimed\n\nAt its 43rd General Conference in 2025, UNESCO proclaimed **13 September of every year** the International Day of Caves and Karst.\n\nThe aim is to build public understanding of landscapes formed by dissolving rock, the underground water they hold, the species they shelter and the scientific and cultural knowledge connected with them.\n\nThe International Union of Speleology, headquartered in Postojna, helped advance the proposal. UNESCO’s official information confirms that the first celebration was hosted in Postojna from 10 to 13 September 2026.\n\nThis is a recurring international observance, not simply a one-off tourism festival. The 2026 gathering was its symbolic beginning.\n\n## Why Postojna?\n\nThe word **karst** comes from the German form of *Kras*, the name of the limestone plateau extending across south-western Slovenia and north-eastern Italy.\n\nResearchers used this landscape to develop concepts and terminology that are now applied to similar terrain around the world. Sinkholes, disappearing rivers, springs and cave systems are not separate curiosities here; they are connected parts of a hydrological landscape.\n\nPostojna brings several strands together:\n\n- a famous show cave with a long visitor tradition;\n- the Karst Research Institute of the Research Centre of the Slovenian Academy of Sciences and Arts;\n- the headquarters of the International Union of Speleology;\n- nearby cave systems, intermittent waters and protected habitats;\n- generations of local knowledge about living above a hidden drainage network.\n\nThe first international celebration therefore recognised Slovenia’s scientific role as well as its tourism appeal.\n\n## Three very different cave experiences\n\nDo not treat Slovenian caves as interchangeable. Choose one that fits your interests, mobility and available time.\n\n### Postojna Cave: the accessible introduction\n\nPostojna Cave offers the most structured first encounter. The standard guided visit takes about **90 minutes** and covers roughly five kilometres, combining an underground train with a little over one kilometre on foot.\n\nThe operator runs tours throughout the year. Visitors select a timed departure and are advised to reach the entrance 30 minutes early; train boarding begins before the advertised tour time.\n\nPostojna is suitable for travellers who want a highly organised visit, multilingual interpretation and developed visitor facilities. The path is designed for tourism, but the underground climate is still cool and damp. Bring a warm layer and shoes with reliable grip even on a hot day.\n\nBook through the official website and confirm the current timetable. A ticket is tied to a particular departure, and popular times can fill.\n\n### Škocjan Caves: the underground river canyon\n\nŠkocjan Caves are a UNESCO World Heritage property. Their defining feature is not a cave train but the immense underground canyon cut by the Reka River.\n\nAll visits to the principal cave route are guided. The park’s standard visit lasts about an hour and a half, with walking, stairs and changing underground conditions. Exact routes can vary with water levels, conservation needs and the season.\n\nChoose Škocjan if you want to understand the power of an active underground river and why karst is a landscape-scale process. Check the official park website for the day’s schedule, route description and accessibility information.\n\nPhotography rules are stricter in sensitive underground spaces. Follow the guide rather than assuming that a phone camera is harmless.\n\n### Križna Cave: small groups and strict limits\n\nKrižna Cave near the Lož Valley offers a much less engineered experience. The shorter visit includes a boat ride on the first underground lake, while longer water routes operate under strict conditions and very limited visitor numbers.\n\nThis is not a spontaneous alternative when another attraction is sold out. Check the official reservation calendar, tour length, age and health conditions, and provided equipment. The longest tour is seasonal and can require booking years in advance.\n\nKrižna Cave demonstrates an important conservation principle: sometimes protecting a place means allowing very few people to enter.\n\n## Choose one cave, not a checklist\n\nPostojna, Škocjan and Križna can all fit into a longer Slovenian trip, but racing through several caves in one day reduces each to a photograph and increases road traffic.\n\nFor a better visit:\n\n1. Select one main underground experience.\n2. Book the official tour before arranging transport.\n3. Add a surface walk, museum or local meal nearby.\n4. Stay overnight in the Karst or Notranjska region if your schedule permits.\n5. Visit a second cave on another day only if it offers a genuinely different perspective.\n\nPostojna pairs naturally with the Expo Cave Karst exhibition or a carefully timed visit to Predjama Castle. Škocjan can be combined with marked surface trails in the regional park. Križna Cave sits near the changing landscape of Lake Cerknica and Notranjska Regional Park.\n\n## What to wear underground\n\nCave temperature does not follow the summer forecast outside. Wear layers that can stay warm in cool, humid air.\n\nBring:\n\n- closed walking shoes with good grip;\n- a fleece or light insulated layer;\n- a waterproof outer layer if the attraction recommends one;\n- any personal medication you may need;\n- a small bag that leaves your hands free.\n\nDo not bring a large suitcase to the entrance. Check storage options in advance.\n\nFor less developed caves, use only the helmet, lamp, boots or protective clothing supplied or approved by the operator. Your phone light is not caving equipment.\n\n## Accessibility requires specific questions\n\n“Accessible” can mean different things underground. A train, smooth path, steep staircase and narrow natural passage may exist within the same attraction.\n\nPostojna’s operator describes the walking path as generally easy and conditionally suitable for visitors with limited mobility, while recommending a train-only option for some wheelchair users. Confirm arrangements directly before buying.\n\nŠkocjan and Križna involve different physical demands. Ask about:\n\n- total walking distance and number of steps;\n- handrails and rest points;\n- narrow or low passages;\n- boat transfers;\n- toilets and seating;\n- assistance for hearing, vision or mobility needs.\n\nContact the specific cave, not a generic ticket reseller. Conditions can change and staff can explain the actual route offered that day.\n\n## Protect what you came to see\n\nCave formations grow on timescales that make human damage effectively permanent. A touched surface can collect skin oils; a broken formation cannot be repaired by the next visitor season.\n\nInside any cave:\n\n- stay on the designated path;\n- never touch, collect or move rock, crystal, bone or sediment;\n- do not feed or handle animals;\n- keep voices low;\n- obey photography and lighting rules;\n- never leave a coin, ribbon, food wrapper or “natural” offering;\n- do not enter a closed passage.\n\nCave wildlife is easy to miss. Bats are only part of the underground community, and disturbance can be especially harmful during hibernation or breeding periods.\n\nThe correct souvenir is knowledge, a legally purchased local product or a photograph taken where permitted—not a piece of the cave.\n\n## Caves are also water infrastructure\n\nKarst aquifers store and move groundwater, often rapidly and with limited natural filtration. Pollution entering a sinkhole can reappear at a distant spring.\n\nVisitors can help on the surface:\n\n- use marked toilets and waste facilities;\n- never pour liquids into a sinkhole or stream;\n- avoid trampling vegetation around cave entrances;\n- stay on marked trails;\n- use refillable bottles;\n- choose official parking and shared transport where practical.\n\nA cave tour becomes more meaningful when you recognise that the water below may supply ecosystems and communities beyond the visible entrance.\n\n## Guided tourism is not the same as wild caving\n\nA show-cave visit follows a managed route with trained staff. Independent speleology requires technical skills, equipment, local knowledge, permission and rescue planning.\n\nNever enter an unmarked cave because it appears on a map or social-media video. Hazards include flooding, falling rock, vertical drops, hypothermia, difficult navigation and areas without phone reception.\n\nIf you want a genuine caving experience, book an authorised adventure programme or contact a recognised speleological organisation. Do not imitate online explorers.\n\nIn an emergency in Slovenia, call **112**. Prevention, however, is far more reliable than underground rescue.\n\n## Getting to Slovenia’s karst region\n\nPostojna has road and rail connections from Ljubljana, but the cave park and other regional attractions may require additional walking or local transport. Check the official Slovenian Railways and bus planners for your exact date.\n\nŠkocjan Caves are near Divača, yet the final connection and walking route should be confirmed before departure. Križna Cave is more rural and needs careful transport planning.\n\nIf driving, use designated car parks and never block village lanes, farm access or rescue routes. Allow extra time between timed tickets; regional roads are not an invitation to hurry.\n\n## Beyond 13 September\n\nThe inaugural celebration has ended, but the new international day returns every year. More importantly, its message applies on every cave visit.\n\nA good underground trip should leave three impressions:\n\n- wonder at the scale and beauty of the karst;\n- curiosity about the science and human history;\n- a stronger reason to protect water, habitats and geological heritage.\n\nSlovenia did not host the first International Day of Caves and Karst simply because it has photogenic caverns. It hosted the day because this landscape helped the world learn how to read the ground beneath its feet.\n\nEnter with a guide, listen carefully and leave the underground exactly as you found it.\n\n## Sources\n\n- UNESCO, International Day of Caves and Karst: https://www.unesco.org/en/days/caves-karst\n- UNESCO Digital Library, proclamation document: https://unesdoc.unesco.org/ark:/48223/pf0000394998\n- International Union of Speleology, first celebration in Postojna: https://uis-speleo.org/index.php/event/unesco-international-day-of-caves-and-karst/\n- Postojna Cave Park, official tour information: https://www.postojnska-jama.eu/en/information/postojna-cave-tours/\n- Postojna Cave Park, current timetables: https://www.postojnska-jama.eu/en/information/tour-timetables/\n- Škocjan Caves Regional Park, official visitor information: https://www.park-skocjanske-jame.si/en/read/tourist-information/visits-of-the-skocjan-caves\n- UNESCO World Heritage Centre, Škocjan Caves: https://whc.unesco.org/en/list/390/\n- Križna Cave, official tours and reservations: https://krizna-jama.si/en/krizna-cave-tours/",
  category: "Aktualno",
  author: "Uredništvo Blog Lab",
  status: "published",
  createdAt: "2026-09-13T19:01:47.000Z",
  updatedAt: "2026-09-13T19:01:47.000Z"
}, {
  id: "king-matjaz-peca-legend-history-guide",
  title: "King Matjaž Beneath Peca: Legend, History and a Koroška Journey",
  excerpt: "Meet Slovenia’s sleeping King Matjaž beneath Mount Peca, separate folklore from the historical Matthias Corvinus, and plan a thoughtful visit to Koroška.",
  seoDescription: "Explore the legend of King Matjaž beneath Mount Peca, its historical links to Matthias Corvinus, and practical visitor stops in Slovenia’s Koroška region.",
  content: "# King Matjaž Beneath Peca: Legend, History and a Koroška Journey\n\nDeep beneath Mount Peca, according to one of Slovenia’s best-known legends, a good king sleeps beside his army. His beard grows around a stone table. When it circles the table nine times, **King Matjaž** will awaken and bring justice back to the land.\n\nThis is folklore, not a report of a hidden medieval court. Yet the story has shaped the identity of Slovenia’s Koroška region so strongly that visitors can encounter it in a mountain cave, in local art and at an annual winter festival.\n\nThe tale becomes more meaningful when its layers are kept separate: the sleeping hero of oral tradition, the historical ruler often linked to him, and the real mining communities beneath Peca.\n\n## The legend of the sleeping king\n\nIn the best-known Slovenian version, Matjaž is a just ruler loved by ordinary people. After enemies overwhelm his forces, the mountain opens and gives refuge to the king and his surviving soldiers.\n\nInside Peca, they fall into an enchanted sleep around a stone table. Matjaž’s beard continues to grow. When it winds around the table for the ninth time, the king will rise, defeat injustice and begin a better age.\n\nDetails vary between tellings. Some versions emphasise foreign invaders; others focus on betrayal, social justice or the return of peace. This variation is normal in oral tradition. A folk legend is not one fixed script but a story carried, reshaped and localised by generations.\n\nVisitors should therefore avoid asking which dramatic detail “really happened.” A better question is why communities preserved the hope of a fair ruler who would return when most needed.\n\n## Was King Matjaž a real person?\n\nThe legendary Matjaž is frequently associated with **Matthias Corvinus**, the historical king of Hungary and Croatia who reigned from 1458 to 1490.\n\nCorvinus was a real fifteenth-century monarch, military leader and Renaissance patron. His territories and campaigns affected a wide part of Central Europe. Folk traditions about “Matthias the Just” developed in several languages and regions after his death.\n\nThat connection does not make the Slovenian cave story a biography. Slovenian versions also place Matjaž in the age of **Carantania**, a much earlier early-medieval principality. The centuries do not align. Scholars treat King Matjaž as a composite folk hero whose character absorbed memories, hopes and motifs from different periods.\n\nIn short:\n\n- Matthias Corvinus belongs to documented fifteenth-century history.\n- King Matjaž beneath Peca belongs to folklore.\n- The historical king may have influenced the legendary name and image, but the sleeping army and ninefold beard are not historical facts.\n\nKeeping this distinction clear protects both the history and the story.\n\n## Why Peca is the perfect mountain for the tale\n\nPeca rises to **2,126 metres** in the Karavanke range above the Meža Valley. Its broad slopes, forests, rock faces and underground spaces make it an ideal home for an enchanted king.\n\nThe mountain also contains a very real subterranean world. Generations of miners excavated lead and zinc beneath Peca, creating an immense network of workings. The disused mine is now interpreted by **Podzemlje Pece – Peca Underground**, a tourist mine and museum in Mežica.\n\nThe Slovenian Tourist Board describes roughly 1,000 kilometres of mine passages beneath the mountain. That industrial labyrinth is not the legendary king’s army camp, but it explains why “inside Peca” feels tangible rather than abstract.\n\nKoroška’s landscape lets geology, labour and folklore overlap. A responsible visit makes room for all three.\n\n## First stop: Mežica and Peca Underground\n\nBegin in **Mežica**, where the tourist mine and museum introduce the region’s mining history.\n\nThe operator offers guided underground experiences, while exact programmes, age limits, equipment, departure times and availability can change. Check the official website and reserve before travelling. Do not arrive expecting to explore abandoned passages independently.\n\nA standard heritage visit is the best choice if the legend and mining history are your priorities. More demanding underground cycling and kayaking experiences are activities with their own fitness, skill and booking requirements; they should not be treated as casual additions.\n\nInside a former mine:\n\n- follow the guide and remain with the group;\n- wear the supplied safety equipment correctly;\n- bring warm clothing and closed footwear as instructed;\n- disclose mobility, health or claustrophobia concerns before booking;\n- never cross barriers or enter unlit side passages.\n\nThe mine preserves the memory of working lives, not merely an adventure set. Listen for explanations of extraction, machinery, minerals and everyday labour as carefully as for the stories.\n\n## Finding the king’s cave\n\nTourism sources describe a “royal cave” beneath Peca where visitors can look for a statue of King Matjaž. Access should be planned through current local information rather than an unverified map pin.\n\nAsk the Koroška tourist office, the Municipality of Črna na Koroškem tourist information point or a local guide about the present route, road conditions and safe parking. Weather, forestry work and seasonal conditions can affect access.\n\nThe statue is an interpretation of a legend. Treat the cave and surrounding mountain as a natural place:\n\n- stay on the established approach;\n- do not carve names or leave objects;\n- avoid candles, smoke and loud music;\n- take all rubbish away;\n- do not disturb bats or other wildlife.\n\nA photograph is enough. The site does not need coins, ribbons or improvised offerings.\n\n## Hiking on Peca\n\nExperienced hikers may combine the story with a mountain day, but Peca is a serious Alpine objective rather than a themed stroll.\n\nThe summit elevation is 2,126 metres. Conditions can be wintry outside the calendar months that visitors assume are “winter,” and fog can remove the views and make navigation difficult. Check the official mountain forecast, current trail information and hut opening before departure.\n\nFor any higher route:\n\n- use a current marked-trail map;\n- choose a route that matches the least experienced person;\n- wear proper hiking shoes and carry insulating and waterproof layers;\n- take enough water and food;\n- turn back if weather, daylight or energy deteriorates;\n- call 112 in an emergency.\n\nDo not follow folklore-themed social posts as navigation instructions. If you are unfamiliar with Slovenian mountain terrain, use a licensed guide.\n\nTravellers who do not want a summit hike can still understand the story through Mežica, Črna na Koroškem, the mine museum and a locally advised visit to the king’s statue.\n\n## The snow castles of King Matjaž\n\nEach winter, Črna na Koroškem celebrates the legend through **King Matjaž’s Castles**, a community event in which teams create structures from snow and ice.\n\nThe festival has been held for decades, but its exact dates, programme and location should always be checked on the municipality or regional tourism website. Snow-dependent events can change.\n\nThe 2026 edition took place from 30 January to 1 February. Do not use those dates for a future trip; consult the next official announcement.\n\nThe festival shows how living heritage works. People do not preserve the legend only by repeating an old text. They rebuild it socially through sculpture, music, gathering and friendly competition.\n\nIf attending a future edition, use organised parking or shuttles, dress for prolonged cold and respect the competition area. Avoid climbing finished structures unless organisers explicitly allow it.\n\n## Build a one-day cultural itinerary\n\nA realistic day should focus on one underground experience and one above-ground stop.\n\n### Morning: Peca Underground\n\nPre-book a guided mine or museum visit in Mežica. Arrive early enough for registration, clothing instructions and safety preparation.\n\n### Lunch: taste Koroška without rushing\n\nChoose a locally operated restaurant or tourist farm. Regional tourism sources mention dishes connected with miners and local households, including bread-and-horseradish preparations and rolled pastries. Ask what is genuinely local and available that day rather than expecting a fixed “legend menu.”\n\n### Afternoon: Črna na Koroškem and the Matjaž story\n\nVisit Črna, learn about the winter snow-castle tradition and seek current advice for the king’s cave or other heritage points. If conditions are poor, choose a short village walk or exhibition instead of forcing a mountain excursion.\n\nAllow extra driving time. Koroška’s roads are scenic but slower than a motorway estimate may suggest.\n\n## Two days are better\n\nWith an overnight stay, the story gains context.\n\nUse the first day for the mine and local heritage. Reserve the second for a suitable hike, a cycling experience or another stop within the **Karawanken–Karavanke UNESCO Global Geopark**.\n\nBook accommodation in the Meža Valley and spend locally. A slower itinerary reduces rushed driving and helps visitor spending reach the communities that maintain the landscape and its stories.\n\nPublic transport options can be limited for trailheads and timed underground tours. Check connections carefully; if driving, confirm parking with the attraction and never leave a vehicle on forestry access roads.\n\n## How to tell the story responsibly\n\nKing Matjaž is often marketed as a charming mystery, but it also carries ideas about justice, collective memory and endurance.\n\nWhen sharing it:\n\n- introduce the sleeping king with “legend says”;\n- identify Matthias Corvinus as a possible historical influence, not the man proven to be sleeping beneath Peca;\n- avoid presenting Carantania and the fifteenth century as the same period;\n- credit Koroška as a living cultural landscape, not an empty fantasy setting;\n- connect the legend with real mining heritage and local communities.\n\nThe distinction does not weaken the magic. It reveals how societies transform history into hope.\n\n## When the king wakes\n\nNo responsible guide can show you a sleeping army. What Koroška can offer is more interesting: a mountain whose interior contains both imagined refuge and documented labour.\n\nYou can stand near the place where the king is said to wait, descend into passages built by miners and see how a medieval ruler’s name became a regional symbol.\n\nKing Matjaž remains asleep because legends are not predictions to verify. They are ways of carrying a question across centuries: what would a truly just ruler look like, and why do people keep waiting for one?\n\nVisit Peca with that question, and the landscape will tell more than one story.\n\n## Sources\n\n- Slovenian Tourist Board, “Sleeping king and Peca Underground”: https://www.slovenia.info/en/press-centre/news-of-the-tourism-press-agency/6837-sleeping-king-and-peca-underground\n- Slovenian Tourist Board, “Explore the world of Slovenian myths and legends”: https://www.slovenia.info/en/stories/explore-the-world-of-slovenian-myths-and-legends\n- Peca Underground – Tourist Mine and Museum, official site: https://www.podzemljepece.com/\n- Koroška regional tourism portal, King Matjaž’s Castles: https://www.koroska.si/\n- Municipality of Črna na Koroškem, 2026 King Matjaž’s Castles notice: https://www.crna.si/\n- Karawanken–Karavanke UNESCO Global Geopark, Mežica Mining Museum: https://www.geopark-karawanken.at/\n- Encyclopaedia Britannica, Matthias Corvinus: https://www.britannica.com/biography/Matthias-I-king-of-Hungary",
  category: "Vodniki",
  author: "Uredništvo Blog Lab",
  status: "published",
  createdAt: "2026-09-13T13:02:16.000Z",
  updatedAt: "2026-09-13T13:02:16.000Z"
}, {
  id: "paddling-lake-cerknica-water-level-guide",
  title: "Paddling Lake Cerknica: When the Disappearing Lake Allows It",
  excerpt: "Lake Cerknica can be a remarkable place to paddle—but only when water levels, navigation zones and wetland protections allow it. Here is how to plan responsibly.",
  seoDescription: "Plan a responsible canoe or kayak trip on Slovenia’s intermittent Lake Cerknica, with live water-level checks, navigation rules, safety and low-water alternatives.",
  content: "# Paddling Lake Cerknica: When the Disappearing Lake Allows It\n\nLake Cerknica is not a conventional lake with a dependable shoreline. It is an **intermittent karst lake**: water arrives, spreads across the polje and later drains through the limestone underground. When conditions are suitable, a canoe or kayak offers a quiet way to experience this changing wetland. When the water is low, the responsible choice is to leave the boat ashore.\n\nThat uncertainty is not an inconvenience to overcome. It is the defining feature of the place.\n\nThis guide explains how international visitors can make a safe, lawful and wildlife-sensitive plan—and how to enjoy the landscape when paddling is not possible.\n\n## First: check the live water levels\n\nDo not decide whether to bring or rent a boat from photographs, a calendar or last week’s report. Open Notranjska Regional Park’s official **Water Level and Navigation** page on the day of your trip.\n\nWhen this guide was prepared, the latest reading displayed for **Stržen at Gorenje Jezero** was **19 centimetres at 17:00 on 8 September 2026**, with a water temperature of 17.6°C. That single gauge does not describe every part of the lake, but it illustrates how quickly expectations can diverge from reality on an intermittent lake.\n\nFor a go/no-go decision, check all current readings and the official navigation notice. If the park says a zone is closed or the threshold is not met, do not launch—even if an isolated pool looks deep enough.\n\nWater levels may also change during a visit. Note the trend, not only the number, and ask the visitor centre for current local advice.\n\n## Understand the navigation thresholds\n\nThe park divides the navigable area into zones. These rules protect visitors and the wetland.\n\nIn the main navigation area, navigation ends when the gauge at **Dolenje Jezero falls below 150 centimetres**.\n\nThe eastern restricted area has tighter conditions. Navigation there is prohibited from **1 March through 15 June** during the bird-nesting season. Outside that period, it is permitted only when the Dolenje Jezero gauge is above **320 centimetres**. Navigation on the Stržen watercourse in that restricted area is allowed while the Gorenje Jezero gauge is above **100 centimetres**.\n\nThese are legal and ecological limits, not targets to test. Conditions at the launch point, along a channel and in open water can differ. Follow the official map and any temporary instructions on site.\n\n## Which craft are permitted?\n\nThe park’s rules allow human-powered craft including kayaks, canoes and rowing boats within the designated navigation area. Sailboats and surf-type craft are also listed, while motorised vessels are reserved for specified public-service uses. Electric boats are allowed only for fish-management purposes.\n\nFor most visitors, a stable recreational kayak or open canoe is the sensible choice. A stand-up paddleboard may be permitted as a surf-type craft, but low water, vegetation and wind can make it impractical.\n\nUse an official entry and exit point shown on the park map. Do not create a shortcut across reeds, meadows or private land, and do not drag a loaded boat over sensitive habitat to reach a shrinking channel.\n\nIf renting equipment, confirm that the operator is open, where launching is currently possible and what happens to a reservation if water levels are unsuitable.\n\n## Why the lake disappears\n\nThe lake’s changing extent is geology, not legend. Water collects on the Cerknica polje when inflow exceeds the capacity of underground karst passages. It later drains through sinkholes and caves when conditions reverse.\n\nNotranjska Regional Park describes Lake Cerknica as Europe’s largest intermittent lake. Its seasonally flooded grasslands, watercourses and underground connections support habitats used by birds, amphibians, fish, insects and wetland plants.\n\nLocal stories have long tried to explain the lake’s dramatic transformations, but visitors should distinguish folklore from the hydrological processes documented by scientists and conservation managers. The real system is extraordinary enough: the “shore” can shift across a broad landscape, turning familiar paddling routes into grassland.\n\n## A practical half-day paddle plan\n\nOnly use this outline after the park’s live information confirms suitable conditions.\n\n### 1. Start at the visitor centre\n\nThe Lake Cerknica Visitor Centre at **Dolenje Jezero 68** is the best first stop for orientation. Confirm the open navigation zones, designated launch points, weather outlook and any conservation restrictions.\n\nA printed or downloaded map is useful because the open-water shape can be misleading. Mobile coverage and battery life should never be your only navigation system.\n\n### 2. Keep the route conservative\n\nChoose an out-and-back or short loop close to an official access point. An intermittent lake rewards observation, not distance records.\n\nAllow more time than the map suggests. Shallow passages, aquatic vegetation, changing wind and wildlife detours can slow progress. Turn back early if the water becomes too thin, the channel unclear or the wind stronger.\n\n### 3. Land only where allowed\n\nPlan the return before launching. Do not assume any visible bank is a suitable exit. Mud can be deep, vegetation fragile and adjacent fields privately managed.\n\nFinish at a designated point and clean mud and plant fragments from footwear and equipment before taking them to another water body. This reduces the risk of moving invasive organisms.\n\n## Essential safety\n\nWear a correctly fitted personal flotation device at all times. Even shallow water can be cold, and mud or submerged vegetation can make standing difficult.\n\nCarry:\n\n- a charged phone in a waterproof case;\n- a downloaded map and the park’s emergency information;\n- drinking water, sun protection and a windproof layer;\n- spare dry clothing sealed in a bag;\n- a small first-aid kit.\n\nCheck the local forecast, especially wind and thunderstorms. Open water can become uncomfortable quickly, while narrow channels may not offer an easy landing.\n\nPaddle with a companion where possible and tell someone your route and expected return. Beginners should use a local guide or instructor. Do not mix alcohol with paddling.\n\nIn an emergency, call **112**, Slovenia’s emergency number, and describe your last confirmed access point or visible landmark.\n\n## Give wildlife room\n\nLake Cerknica is not an outdoor gym with birds in the background. It is a protected wetland in which recreation is a guest.\n\nKeep well away from bird concentrations, nests and reed edges. If birds repeatedly call, change direction or leave the water as you approach, you are too close. Never pursue wildlife for a photograph.\n\nTravel quietly, keep the group compact and avoid speakers. Do not feed animals or remove plants. Binoculars provide a better encounter than closing the distance with a boat.\n\nThe spring closure in the restricted area is a minimum safeguard. Responsible paddlers remain cautious in every season.\n\n## If the water is too low\n\nA low-water day is not a failed visit. It reveals the lake’s other identity.\n\nWalk one of the park’s marked routes, visit the interpretation centre or book an official birdwatching experience. The park’s **Drvošec trail** and observation points offer a landscape-scale view without requiring navigable water. Check current trail conditions and opening hours before setting out.\n\nIn September 2026, the park is also presenting the exhibition **Images of Lake Cerknica: Where Water Tells Stories** at the Jože Udovič Library and its branches through the end of the month. Verify the current venue and hours if you want an indoor alternative.\n\nDo not attempt to “find water” by driving or walking across the lake bed. Stay on public roads and marked paths, respect barriers and never block agricultural access.\n\n## When to go\n\nThere is no guaranteed paddling month. Rainfall, snowmelt and underground drainage decide more than the season printed on a travel itinerary.\n\nBuild flexibility into your trip:\n\n- check the hydrological page before leaving your accommodation;\n- keep walking, cycling or birdwatching equipment available;\n- avoid a non-refundable paddling-only schedule;\n- contact the visitor centre if the readings or zone map are unclear.\n\nAutumn can bring beautiful light, migrating birds and changing water levels, but conditions vary from year to year. Spring may hold more water while also bringing strict nesting-season limits in the protected eastern area.\n\n## A better kind of adventure\n\nThe best Lake Cerknica outing begins with accepting that the lake sets the terms.\n\nIf the official thresholds, weather and local advice align, paddle gently from a designated access point and let the shifting channels define the day. If they do not, explore on foot and watch how a lake becomes meadow.\n\nEither choice can reveal the same lesson: in a karst wetland, responsible travel means adapting to water, wildlife and place—not asking them to adapt to you.\n\n## Sources\n\n- Notranjska Regional Park, live water level and navigation rules: https://notranjski-park.si/en/latest/water-level\n- Notranjska Regional Park, Lake Cerknica: https://notranjski-park.si/en/discover/natural-landmarks/lake-cerknica\n- Notranjska Regional Park, visitor recommendations: https://notranjski-park.si/en/latest/recommendations\n- LIFE Cerknica project, habitats and conservation: https://notranjski-park.si/en/projects/life-cerknisko-jezero\n- Notranjska Regional Park, guided birdwatching experience: https://notranjski-park.si/en/plan-your-trip/experiences/the-mysterious-bird-life-of-lake-cerknica\n- Notranjska Regional Park, September 2026 exhibition: https://notranjski-park.si/en/latest/events/images-of-lake-cerknica-where-water-tells-stories",
  category: "Šport",
  author: "Uredništvo Blog Lab",
  status: "published",
  createdAt: "2026-09-13T07:01:58.000Z",
  updatedAt: "2026-09-13T07:01:58.000Z"
}, {
  id: "festival-maribor-2026-visitor-guide",
  title: "Festival Maribor 2026: A Classical Music City Break",
  excerpt: "Maribor’s annual classical music festival runs from 15 to 27 September. Here is how to plan concerts, transport and an unhurried city stay.",
  seoDescription: "Plan a visit to Festival Maribor 2026 from 15–27 September, with practical advice on tickets, venues, public transport and city attractions.",
  content: "# Festival Maribor 2026: A Classical Music City Break\n\nFrom **15 to 27 September 2026**, Maribor becomes a destination for travellers who prefer chamber music and concert halls to crowded sightseeing checklists.\n\nFestival Maribor is the city’s established autumn classical music festival. The Slovenian Tourist Board and Maribor’s official destination calendar confirm this year’s dates, while the festival organiser provides the live programme and ticket information.\n\nFor international visitors, the event is more than a series of concerts. Its venues, evening timetable and location beside the Drava make it an ideal reason to spend at least one night in Slovenia’s second-largest city.\n\n## Start with the official programme\n\nFestival schedules can change, and different concerts may use different venues, start times and ticket rules. Open the organiser’s current programme before booking transport or accommodation.\n\nChoose one or two performances that genuinely interest you. A festival city break works better when there is time for dinner, a riverside walk and an unhurried arrival at the hall.\n\nCheck four details for every event:\n\n- exact venue and entrance;\n- start time and recommended arrival time;\n- seating or admission conditions;\n- ticket collection and cancellation rules.\n\nDo not rely on an old social-media graphic. Use the current event page and the information printed on your ticket.\n\n## The dates and festival character\n\nThe official tourism listings describe Festival Maribor as a renowned annual classical music festival. The event runs for nearly two weeks, so visitors can build a trip around a single concert or stay for several programmes.\n\nThe festival is known for using several Maribor venues rather than one isolated arena. Culture.si highlights spaces including **Union Hall** and **Kazina Hall**, while individual editions may add other locations.\n\nThis scattered format turns the city into part of the experience. It also means you must confirm the address rather than automatically walking to the same building each evening.\n\n## Arriving in Maribor\n\nMaribor is connected with Ljubljana and other Slovenian cities by rail and intercity bus. International rail connections also serve the wider region, but timetables and engineering works can change.\n\nCheck the official Slovenian Railways planner shortly before travelling. If your train arrives close to concert time, allow a generous buffer for finding the venue, collecting tickets and storing luggage.\n\nDriving is possible, but an evening concert is a poor moment to search for parking beside a historic venue. Use official car parks, check operating hours and continue on foot or by city bus.\n\n## A useful public-transport benefit\n\nNarodni dom Maribor has announced that festival ticket holders can use **Marprom city buses to travel to festival concerts and back without an additional fare** during the festival period.\n\nBefore boarding, check the current instructions: confirm which ticket must be shown, the valid time window and whether any lines or services are excluded. Keep the festival ticket accessible on your phone or in print.\n\nThis benefit makes it easier to stay outside the immediate centre and reduces the pressure to drive after an evening performance.\n\n## Build a concert day in three acts\n\n### Morning: understand Maribor\n\nBegin at the old city centre and the Drava riverfront. Walk rather than racing between landmarks. Maribor’s scale makes it possible to connect streets, squares and the river without turning the day into a transport exercise.\n\nThe city’s most famous living heritage is the **Old Vine**, recognised as the world’s oldest grapevine. Visit its official interpretation point if opening hours fit your plan, but remember that it is a living plant and cultural symbol, not merely a photo backdrop.\n\n### Afternoon: leave space before the concert\n\nHave a late lunch or early dinner and return to your accommodation to change, rest and check the ticket.\n\nSeptember weather can shift quickly. Carry a compact rain layer, particularly if the venue requires a walk across the centre. Smart casual clothing is usually a practical choice unless the organiser states otherwise; comfort matters more than performing formality.\n\n### Evening: arrive early\n\nAim to reach the venue at least 20 to 30 minutes before the advertised start, or earlier if the organiser requests it. Historic halls may have several entrances, limited cloakroom space or stairs.\n\nSilence your phone completely, including alarms and vibration. Do not photograph, record or leave your seat during a performance unless venue rules permit it. Applause customs can vary by programme; follow the audience and the performers’ cues.\n\n## Tickets: buy from official channels\n\nUse the festival organiser or its authorised ticket partner. Avoid screenshots, social-media resellers and unofficial offers that cannot be verified.\n\nWhen purchasing, check whether the price includes a numbered seat, whether reductions require identification and whether the ticket is digital or must be collected.\n\nIf a concert is sold out, consult the organiser for returns or additional performances. Do not assume a ticket will be available at the door.\n\n## Choosing accommodation\n\nA hotel or guesthouse in the centre is convenient for walking, but Maribor’s bus benefit may make other neighbourhoods practical too.\n\nBook according to your final concert venue, not simply a generic “city centre” label. Check the actual walking route after dark and whether reception or self-check-in will still be available after the performance.\n\nStaying overnight is safer and more enjoyable than planning a long drive immediately after a late concert. It also directs more visitor spending into the local economy.\n\n## Food and wine without rushing\n\nMaribor sits within one of Slovenia’s major wine regions, and autumn is closely linked with harvest culture. A pre-concert meal can introduce local food and Styrian wine, but reserve enough time for service.\n\nIf drinking alcohol, use public transport or walk. Ask for tap water, eat properly and choose small tastings rather than turning the concert into the final stop of a drinking itinerary.\n\nSeek locally operated restaurants and make reservations on busy festival evenings. Tell staff if you have a fixed concert time.\n\n## Accessibility\n\nHistoric performance spaces differ in their step-free access, seating and toilet facilities. Contact the box office before buying if you need wheelchair access, an aisle seat, hearing assistance or another accommodation.\n\nDo not assume every venue in a multi-location festival has the same facilities. Ask about the precise hall and entrance listed for your performance.\n\n## Combine the festival with wider Maribor\n\nA second day can include the Drava riverfront, the Old Vine area, museums or a short excursion toward Pohorje. Check seasonal opening hours and weather before adding outdoor plans.\n\nLater in September, the city’s wine-related events begin to overlap with the musical calendar. That can enrich a visit but also increase demand for accommodation and restaurant tables.\n\nKeep the itinerary coherent: one major cultural event, one neighbourhood walk and one regional food experience are enough for a rewarding day.\n\n## Why go now?\n\nFestival Maribor gives travellers a timely reason to see the city as a cultural destination rather than a stop between Ljubljana and Austria.\n\nThe best visit does not depend on knowing every composer in advance. Read the programme notes, choose a concert that sparks curiosity and allow Maribor to frame the music with river views, historic halls and early-autumn evenings.\n\nThe festival runs from **15 through 27 September 2026**. Verify the live programme, book through official channels and let the concert—not a frantic checklist—set the rhythm of the trip.\n\n## Sources\n\n- Slovenian Tourist Board, Festival Maribor 2026 event listing: https://www.slovenia.info/en/things-to-do/events/27032-festival-maribor-2026\n- Visit Maribor, official destination and events calendar: https://www.visitmaribor.si/\n- Narodni dom Maribor, festival information and ticketing: https://nd-mb.si/\n- Culture.si, background and venue information for Festival Maribor: https://www.culture.si/en/Festival_Maribor\n- Slovenian Railways, official journey planner: https://potniski.sz.si/en/\n- Marprom, official Maribor city transport information: https://www.marprom.si/en/",
  category: "Aktualno",
  author: "Uredništvo Blog Lab",
  status: "published",
  createdAt: "2026-09-12T18:59:57.000Z",
  updatedAt: "2026-09-12T18:59:57.000Z"
}, {
  id: "erazem-predjama-history-legend-visitor-guide",
  title: "Erazem of Predjama: History Behind the Rebel Knight",
  excerpt: "Meet the real fifteenth-century knight behind Slovenia’s Robin Hood-style legend, then explore Predjama Castle with fact and folklore kept clearly apart.",
  seoDescription: "Discover the history and legend of Erazem of Predjama, with practical advice for visiting Predjama Castle and the cave beneath it.",
  content: "# Erazem of Predjama: History Behind the Rebel Knight\n\nPredjama Castle looks as if a storyteller designed it: walls pressed into a cave mouth, high above a Slovenian village, with the Karst disappearing into darkness behind it.\n\nIts most famous resident was **Erazem of Predjama**, a fifteenth-century nobleman whose conflict with imperial authority became one of Slovenia’s best-known castle legends. He was a real historical person. The dramatic details repeated today—secret deliveries during a year-long siege, a treacherous servant and a fatal cannonball striking the castle toilet—belong to a story shaped by centuries of retelling.\n\nVisitors do not need to choose between history and legend. Predjama is most rewarding when you understand where the evidence ends and folklore begins.\n\n## The historical core\n\nOfficial Slovenian tourism sources place Erazem at Predjama in the **fifteenth century** and describe him as a rebellious knight or robber baron who opposed imperial power.\n\nA Slovenian Tourist Board account links his death to the year **1484** and names Gašper Ravbar, a Trieste baron, as the commander involved in the siege. This gives the story a documented late-medieval setting.\n\nPredjama itself is more than scenery. The castle occupies a vast cave entrance in a 123-metre cliff, using the rock as part of its defensive structure. The site has guarded this position for more than 800 years, although the building visitors see reflects later development as well as its medieval origins.\n\nThe cave system behind and beneath the castle provided natural passages and practical advantages. That physical reality helps explain why stories of secret movement and supplies were so believable.\n\n## The legend of the siege\n\nIn the popular version, Erazem retreats to Predjama Castle after defying the emperor. An imperial force surrounds the apparently impregnable stronghold and waits for hunger to force surrender.\n\nMonths pass, but food continues to appear inside. Erazem supposedly mocks the besiegers by throwing fresh cherries or other provisions from the castle, proving that their blockade has failed. A hidden route through the Karst is said to have connected the castle with the outside world.\n\nThe final betrayal is the tale’s most theatrical scene. A servant signals when Erazem enters a vulnerable room, allowing the attackers to aim a cannon. The rebellious knight dies in the castle toilet—an undignified ending that has ensured the story is remembered.\n\nThese elements should be presented as **legend**, not a complete military record. Official visitor materials themselves describe Erazem as the subject of multiple legends, ranging from noble hero to bandit. The conflicting portraits are part of his cultural afterlife.\n\n## Slovenia’s Robin Hood—or a robber baron?\n\nModern retellings often call Erazem a Slovenian Robin Hood. The comparison is useful because it immediately suggests a rebel resisting authority. It can also oversimplify him.\n\nThe historical language surrounding Erazem is less comfortable: knight, outlaw, robber baron and violent opponent of imperial rule. Folklore tends to turn ambiguous figures into heroes or villains according to the needs of each generation.\n\nWhen you visit, listen for both versions. Ask what is supported by documents, what is inferred from the castle’s architecture and what survives because it makes a compelling story.\n\n## Reading the castle as evidence\n\nPredjama’s real structure is as fascinating as the legend.\n\nNotice how built rooms merge with exposed rock. The castle did not merely stand beside a cave; it incorporated the Karst into defence, storage and movement. Windows and platforms command the valley, while the cliff limits the directions from which an attacker could approach.\n\nInside, displays include original objects alongside replicas and models. The official visitor description points to the knight’s room, the dining room’s late-Gothic interpretation and a Renaissance hall. Treat reconstructed spaces as interpretation rather than assuming every object belonged to Erazem.\n\nAn audio guide or guided explanation is valuable because the building’s irregular levels can otherwise feel like a collection of dramatic rooms without chronology.\n\n## The cave below the castle\n\nThe cave beneath Predjama has a history much older than Erazem. Official information states that archaeological finds show human use from the Stone Age, with Roman-period remains also found in the entrance area.\n\nSeasonal cave visits are managed around the underground environment and bat hibernation. The operator’s current timetable says tours run only during the open season and lists limited departures through late September. Schedules can change, so check the live timetable before travelling and reserve where required.\n\nA castle ticket does not necessarily mean every underground passage is open. Do not enter closed sections or attempt to find a “secret exit” independently.\n\n## Planning a visit in September\n\nPredjama Castle is near Postojna Cave, making the two attractions a practical pair, but they are separate sites.\n\nThe operator places the castle about nine kilometres from Postojna Cave. A shuttle may operate in high season, but availability is seasonal. Confirm transport before arrival rather than assuming you can move easily between timed bookings.\n\nA sensible plan is:\n\n1. Check the official timetable and ticket conditions.\n2. Reserve any timed Postojna Cave tour first.\n3. Allow travel time between the cave park and Predjama.\n4. Visit the castle without rushing its steep stairs and narrow passages.\n5. Add the cave beneath the castle only if it is officially open and your schedule allows.\n\nWear shoes with good grip and bring a layer. A castle built into rock can feel cool and damp even when the village outside is warm.\n\n## Accessibility and comfort\n\nPredjama’s historic structure includes stairs, uneven floors and confined areas. Travellers with limited mobility should consult the operator directly about current access before purchasing a ticket.\n\nFamilies should keep children close on staircases and viewing areas. Large bags make narrow interiors uncomfortable; bring only what you need.\n\nThe exterior viewpoint provides the famous full view of the castle, but respect barriers, private land and traffic. Do not step into the road or climb slopes for a photograph.\n\n## Visit responsibly\n\nPredjama is both a major attraction and a small living village. Use designated parking, keep noise low outside the visitor area and do not block residents’ access.\n\nInside the castle and cave, obey photography instructions and never touch formations, rock surfaces or exhibits. Natural underground spaces recover slowly—or not at all—from careless contact.\n\nIf you combine Predjama with Postojna Cave, avoid an overpacked itinerary. The region deserves more than a hurried photograph at each entrance. A slower visit leaves time to understand the Karst landscape that made both sites possible.\n\n## What the legend adds\n\nErazem’s story survives because the building makes it feel plausible. Stand beneath the cliff and the questions arrive naturally: How could an army capture this place? Where did food come from? Which passage led outside? Who could be trusted?\n\nHistory confirms a rebellious fifteenth-century knight and a real conflict. Architecture confirms a castle bound to a cave system. Legend supplies cherries, betrayal and a perfectly memorable death.\n\nKeep those layers separate, and Predjama becomes richer. It is not only the home of a Slovenian Robin Hood. It is a place where landscape, power and storytelling have reinforced one another for centuries.\n\n## Sources\n\n- Predjama Castle, official site: https://www.postojnska-jama.eu/en/predjama-castle/\n- Postojna Cave Park, official Predjama Castle tour information: https://www.postojnska-jama.eu/en/information/predjama-castle-tour/\n- Postojna Cave Park, cave beneath Predjama Castle: https://www.postojnska-jama.eu/en/attractions-in-the-park/cave-under-predjama-castle/\n- Postojna Cave Park, current tour timetables: https://www.postojnska-jama.eu/en/information/tour-timetables/\n- Slovenian Tourist Board, Slovenian myths and legends: https://www.slovenia.info/en/stories/explore-the-world-of-slovenian-myths-and-legends\n- Slovenian Tourist Board, Postojna Cave and Predjama overview: https://www.slovenia.info/en/places-to-go/attractions/postojna-cave",
  category: "Vodniki",
  author: "Uredništvo Blog Lab",
  status: "published",
  createdAt: "2026-09-12T13:02:13.000Z",
  updatedAt: "2026-09-12T13:02:13.000Z"
}, {
  id: "cycling-parenzana-slovenian-coast-guide",
  title: "Cycling the Parenzana: Slovenia’s Coastal Rail Trail",
  excerpt: "Ride a former railway through Slovenian Istria, linking coastal towns, vineyards, salt pans and stone tunnels on a flexible cycling day.",
  seoDescription: "Plan a Parenzana cycling trip on Slovenia’s coast, with route choices, bike advice, tunnel safety, responsible travel tips and official maps.",
  content: "# Cycling the Parenzana: Slovenia’s Coastal Rail Trail\n\nA railway once carried passengers and goods between Trieste and Poreč. Today, much of its route has become the **Parenzana**, also called the Path of Health and Friendship—a cross-border trail where bicycles have replaced steam trains.\n\nFor visitors to Slovenia, the coastal section offers an unusually rich day on two wheels. It links Koper, Izola, Strunjan and the Portorož–Piran area while passing vineyards, olive groves, salt-pan landscapes and railway tunnels.\n\nSeptember is a practical time to consider the ride: the strongest summer heat may ease, but daylight, rain and coastal wind still require planning. Treat the Parenzana as a real journey, not simply a flat promenade.\n\n## Understand the route before you start\n\nThe complete Parenzana runs for roughly **130 kilometres** across Italy, Slovenia and Croatia, following the former narrow-gauge railway between Trieste and Poreč.\n\nYou do not need to ride the entire international route. The Slovenian Tourist Board estimates the Slovenian section at approximately four to eight hours, depending on pace and stops, and describes the full trail as easy. “Easy,” however, does not mean effortless for every visitor. Distance, mixed surfaces, navigation, other trail users and changing weather all matter.\n\nFor a relaxed tourism day, select a manageable section around Slovenian Istria rather than chasing the full distance. Koper, Izola, Strunjan and Portorož provide logical places to build a route around accommodation, bike rental and meals.\n\n## A flexible Slovenian coastal itinerary\n\n### Begin in Koper\n\nKoper is a useful starting point because it combines a historic centre with cycling services. Visit Koper lists the Parenzana among the area’s most popular trails and provides cycling maps through its tourist information channels.\n\nBefore leaving, check tyre pressure, brakes, gears and lights. Download an official map for offline use and confirm how you will return if riding one way.\n\n### Continue toward Izola\n\nThe coastal landscape changes quickly between urban waterfronts and quieter stretches. Slow down where the route is shared with pedestrians, runners or local traffic. Do not assume a painted cycling symbol gives you priority at every crossing.\n\nIzola makes a sensible food or water stop. Lock the bicycle securely and keep valuables with you. In warmer conditions, refill before continuing inland toward Strunjan.\n\n### Ride through Strunjan\n\nThe route passes through a protected and cultivated landscape shaped by salt, agriculture and the sea. The Parenzana is a transport corridor, but nearby reserves have their own access rules.\n\nWithin Strunjan Landscape Park, cycling is prohibited in the nature reserves on the cliff and in the salt pans and lagoon area. Stay on the permitted route, dismount where signs require it and never create shortcuts through protected ground.\n\n### Experience the Valeta Tunnel\n\nOne of the most memorable features is the **Valeta Tunnel**, a 550-metre stone tunnel between Strunjan and Portorož. It was built as part of the railway in the early twentieth century and is now illuminated and closed to motor vehicles.\n\nUse bicycle lights anyway. They make you visible if fixed lighting fails or another rider approaches. Remove sunglasses before entering, reduce speed and do not stop in the middle for photographs. Sound and distance can be deceptive inside a curved tunnel.\n\n### Finish around Portorož or Piran\n\nPortorož offers an easy place to end, eat or connect with local services. Piran’s historic centre is nearby, but its narrow pedestrian streets call for patience and often a dismounted bicycle.\n\nIf you plan to finish in Piran, check bicycle access and parking arrangements. Never leave a rental bike outside the provider’s permitted area, and confirm return procedures before starting.\n\n## Which bicycle should you choose?\n\nThe Slovenian Tourist Board recommends **trekking or mountain bikes** for the Slovenian section. A hybrid or e-bike can also suit many riders when supplied by a reputable rental provider and used within its conditions.\n\nA road bike with very narrow tyres may be less comfortable on variable surfaces. Before accepting any rental, check:\n\n- brakes and tyre condition;\n- front and rear lights;\n- correct saddle height;\n- lock and repair kit;\n- battery range and charger arrangements for an e-bike;\n- emergency contact and breakdown policy.\n\nAn e-bike reduces effort but does not shorten braking distance or replace handling skills. Start in a low assistance mode and conserve battery for the return.\n\n## What to carry\n\nBring more than you would for a short city-bike ride:\n\n- water and a small snack;\n- helmet and cycling gloves;\n- lights, even for illuminated tunnels;\n- compact rain and wind layer;\n- sun protection;\n- charged phone plus offline map;\n- basic repair kit if not supplied;\n- identification and rental documents.\n\nSeptember weather can shift quickly. Check the local forecast shortly before departure and postpone when storms, extreme wind or poor visibility make the coast unsafe.\n\n## Share the trail responsibly\n\nThe Parenzana is also used by walkers and runners. Ring a bell early, pass slowly and leave generous space. Keep right where local signs and conditions indicate, but do not force a pass on a narrow section.\n\nAt road crossings, assume drivers have not seen you. Obey traffic lights and signs, and walk the bicycle where visibility is poor.\n\nProtect the places that make the route attractive. Carry out waste, use established rest areas, avoid entering vineyards or olive groves without permission and support local businesses without blocking their entrances with bicycles.\n\n## Family cycling requires a shorter plan\n\nGentle gradients make parts of the trail attractive to families, but suitability depends on each child’s control, stamina and confidence around crossings, tunnels and other users.\n\nChoose a short out-and-back section so turning around remains easy. Give every bicycle working lights, keep adults at the front and back of the group, and avoid peak times. A child seat or trailer must be approved by the rental provider for that bicycle and route.\n\n## One way or return ride?\n\nAn out-and-back trip is simplest because it avoids uncertain transport, but remember that every kilometre outbound must be ridden again. Turn around before anyone becomes tired.\n\nA one-way ride can be enjoyable if the return is arranged in advance. Do not assume ordinary buses accept full-size bicycles; check directly with the operator or book a bicycle transfer.\n\nLeave time for stops. The Parenzana rewards slow travel: a tunnel, a salt-pan view and lunch in a coastal town matter more than a high average speed.\n\n## Why this ride belongs on a Slovenia itinerary\n\nThe Parenzana joins sport, industrial heritage and Mediterranean landscape without demanding an elite cyclist’s fitness. It also demonstrates how old infrastructure can become a low-impact way to experience several destinations in one journey.\n\nPick a realistic section, use the correct bicycle and make room for other people. The railway has disappeared, but its gentle line still offers one of the clearest ways to understand Slovenian Istria.\n\n## Sources\n\n- Slovenian Tourist Board, “The most beautiful biking trails”: https://www.slovenia.info/en/stories/the-most-beautiful-biking-trails\n- Slovenian Tourist Board, official cycling guide: https://www.slovenia.info/en/things-to-do/active-holidays/biking\n- Visit Koper, cycling information and Parenzana FAQ: https://visitkoper.si/en/cycling/ and https://visitkoper.si/en/travel-info/faq/\n- Portorož & Piran, Valeta Tunnel: https://www.portoroz.si/en/what-to-do/natural-landmarks/obj/14051-valeta-tunnel\n- Portorož & Piran, coastal cycling information: https://www.portoroz.si/en/what-to-do/cycling/\n- Strunjan Landscape Park, official visitor guidance: https://parkstrunjan.si/en/plan-a-visit/",
  category: "Šport",
  author: "Uredništvo Blog Lab",
  status: "published",
  createdAt: "2026-09-12T06:58:48.000Z",
  updatedAt: "2026-09-12T06:58:48.000Z"
}, {
  id: "september-strunjan-coast-responsible-day-guide",
  title: "September by the Sea: A Responsible Day in Strunjan",
  excerpt: "Quieter shores, coastal walks and living salt-making heritage make Strunjan a timely September escape—if you visit its protected landscape with care.",
  seoDescription: "Plan a responsible September visit to Strunjan, with coastal walks, swimming, salt-pan heritage, park rules and practical travel advice.",
  content: "# September by the Sea: A Responsible Day in Strunjan\n\nSlovenia’s coast does not close when August ends. In a tourism update published on **2 September 2026**, the Slovenian Tourist Board highlighted early autumn as a rewarding time to visit: the busiest holiday period has passed, while the coast can still suit swimming, walking and cycling.\n\nFor international visitors seeking a calmer alternative to a packed resort day, **Strunjan Landscape Park** brings several versions of the Adriatic into one compact place: a protected natural shore, flysch cliffs, a lagoon, working salt pans and a cultivated Mediterranean landscape.\n\nThis is not a promise of guaranteed sunshine or warm water. September conditions change from day to day. It is an invitation to plan flexibly and experience the coast as a living landscape rather than simply a beach.\n\n## Why Strunjan works in September\n\nStrunjan sits between Izola and Piran on the short Slovenian coastline. The park’s official visitor information describes a landscape where sea, cliffs, salt pans, agriculture and settlement meet.\n\nThat variety matters in shoulder season. If conditions suit swimming, there are coastal places to enter the water. If the sea is rough or rain arrives, the park’s cultural and natural story still provides a worthwhile visit.\n\nThe change of pace is part of the appeal. Walkers can pay attention to terraces, salt-making heritage and views across the Gulf of Trieste instead of rushing between headline attractions.\n\n## A flexible one-day plan\n\n### Morning: begin at the salt pans\n\nStart near the **Saltpan House**, the park’s visitor centre. Its “Park of the Sea” exhibition explains the relationship between the cliffs, lagoon, salt pans and marine environment. The exhibition is presented in Slovenian, Italian and English.\n\nThe park currently lists weekday and weekend opening hours, but it also warns that weather can cause changes. Check the official page on the day of your visit rather than relying on a saved timetable.\n\nFrom here, follow marked routes around the lagoon and salt-pan landscape. Salt production is not a decorative theme added for tourists; it forms part of the area’s working cultural landscape. Observe operational areas and barriers, and never enter places closed to visitors.\n\n### Midday: walk the landscape, not the cliff edge\n\nThe park’s educational paths reveal the peninsula gradually. Choose a distance that fits the weather, footwear and daylight available.\n\nStay on marked paths. Strunjan’s cliffs are made of flysch and are subject to natural erosion and rockfall. Do not stand directly below unstable cliff faces, climb barriers or create a shortcut for a photograph. The official Portorož and Piran destination guide specifically advises visitors to check hazard information for Moon Bay and avoid areas directly beneath steep cliffs.\n\nBring drinking water, sun protection and a light waterproof layer. Even on a mild day, exposed sections can feel very different when wind or rain arrives.\n\n### Afternoon: swim only if conditions are right\n\nSeptember can still offer pleasant sea conditions, but decide at the shore, not from an old social-media post. Consider wind, waves, water temperature, visibility and any local warnings.\n\nUse recognised access points. Do not jump from cliffs, swim close to boats or enter the water alone in uncertain conditions. Natural beaches may have fewer services than organised bathing areas.\n\nNavigation and anchoring are restricted in the central part of the Strunjan Marine Nature Reserve, including the area around Holy Cross Bay and Ronek. Visitors arriving by boat must check the park’s current zoning rules before approaching.\n\nIf swimming is not appealing, continue on foot, visit the exhibition or enjoy a slow meal nearby. A successful coastal day does not need to include the sea.\n\n## Cycling: useful, but know the protected zones\n\nThe coast around Strunjan connects with the **Parenzana**, the former narrow-gauge railway route now popular with walkers and cyclists. The wider Portorož and Piran destination offers routes linking Strunjan with Piran, Portorož and Istrian villages.\n\nWithin the landscape park, however, cycling is not permitted in the nature reserves on the cliff or in the salt pans and lagoon area. Dismount where required and follow signs. A bicycle is a good low-impact way to arrive only when it is used within the rules.\n\n## Arriving without adding to the traffic\n\nThe park encourages visitors to come on foot, by bicycle or by public transport. Regular bus services connect the coastal towns and Strunjan, although timetables vary by day and season.\n\nCheck the current journey planner before leaving. If driving, use designated parking and never block local access, agricultural work or emergency routes. Parking close to a viewpoint is not a reason to stop outside an authorised space.\n\nA practical car-free combination is to base yourself in Piran, Portorož or Izola and make Strunjan the nature-focused part of a wider coastal stay.\n\n## Guided visits need advance planning\n\nVisitors may explore independently, but the park also offers guided tours covering natural and cultural features. Its booking information asks groups to reserve several days ahead; same-day guiding should not be assumed.\n\nThe classic guided walk includes the cliff landscape, lagoon and salt pans, with shorter variants available. Confirm the route, meeting point, availability and price directly with the park before travelling.\n\n## Five rules that protect the experience\n\n1. **Keep to marked paths.** Erosion and repeated shortcuts damage fragile slopes.\n2. **Leave plants, stones and shells in place.** Protected nature is not a souvenir supply.\n3. **Respect reserve restrictions.** Rules differ for walking, cycling, swimming and boating.\n4. **Carry out your waste.** Food scraps also do not belong in the landscape.\n5. **Choose a plan for the conditions.** Wind, rain, heat and rough water can quickly change what is sensible.\n\n## Pair Strunjan with another coastal stop\n\nStrunjan is close enough to combine with Piran’s historic centre, Izola’s harbour or a section of the Parenzana. Resist the temptation to squeeze all three coastal towns and the park into a hurried checklist.\n\nOne protected landscape, one town and one good local meal make a more realistic day. Staying longer supports local accommodation and lets you adjust outdoor plans when the weather changes.\n\n## The September advantage\n\nThe best reason to visit Strunjan now is not that it recreates midsummer with fewer people. It offers something different: softer seasonal rhythms, room for walking and a clearer view of how nature and human work shaped the Slovenian coast.\n\nCheck current information, travel lightly and let the weather decide whether your day centres on a swim, a trail or salt-pan heritage. September rewards visitors who arrive with a plan—and remain willing to change it.\n\n## Sources\n\n- Slovenian Tourist Board, “Why September Is One of the Best Times to Experience Slovenia’s Coast,” published 2 September 2026: https://www.slovenia.info/en/press-centre/news-of-the-tourism-press-agency/39701-why-september-is-one-of-the-best-times-to-experience-slovenia-s-coast\n- Strunjan Landscape Park, official visitor information: https://parkstrunjan.si/en/plan-a-visit/\n- Strunjan Landscape Park, Saltpan House visitor centre: https://parkstrunjan.si/en/at-the-saltpan-house/\n- Portorož & Piran, official beach and coastal-safety information: https://www.portoroz.si/en/what-to-do/beaches/\n- Portorož & Piran, official cycling information: https://www.portoroz.si/en/what-to-do/cycling/",
  category: "Aktualno",
  author: "Uredništvo Blog Lab",
  status: "published",
  createdAt: "2026-09-11T19:02:51.000Z",
  updatedAt: "2026-09-11T19:02:51.000Z"
}, {
  id: "zlatorog-legend-trenta-valley-visitor-guide",
  title: "Zlatorog: The Alpine Legend of Trenta",
  excerpt: "Meet Slovenia’s golden-horned guardian, then explore the real Trenta Valley with a clear line between folklore, landscape and responsible travel.",
  seoDescription: "Discover the Slovenian legend of Zlatorog and plan a responsible visit to Trenta Valley and Triglav National Park in the Julian Alps.",
  content: "# Zlatorog: The Alpine Legend of Trenta\n\nHigh above the emerald Soča, a white ibex with golden horns guards a hidden treasure. That is the world of **Zlatorog**—literally “Goldhorn”—one of Slovenia’s best-known Alpine legends.\n\nThe story belongs to folklore, not documented history. Yet its landscape is real: the Trenta Valley and the Julian Alps, much of them protected within Triglav National Park. For visitors, Zlatorog is a memorable way to read the mountains as more than scenery—as a place where human desire, fragile plants and wild nature meet.\n\n## The legend, clearly told as legend\n\nAccording to the tale, Zlatorog ruled a mountain paradise in the Julian Alps. His golden horns were said to unlock a treasure hidden beneath Mount Bogatin.\n\nA young hunter from Trenta, driven by unhappy love and the promise of wealth, pursued and wounded the animal. From drops of Zlatorog’s blood grew miraculous **Triglav flowers**. After eating them, the ibex recovered, charged the hunter and sent him over a precipice. Zlatorog then destroyed his garden and vanished, leaving the treasure hidden.\n\nVersions and details vary, as they do in living folklore. The Slovenian Tourist Board presents the story as a legend about the relationship between people and nature, and about the consequences of disturbing that balance. It should not be read as evidence that a magical animal or buried treasure existed.\n\n## What is real?\n\nThe **Trenta Valley** is a high Alpine valley along the upper Soča in north-western Slovenia. It lies within the wider landscape of Triglav National Park, Slovenia’s only national park.\n\nThe ibex is also a real Alpine animal, although Zlatorog’s golden horns and healing powers belong to myth. The story’s miraculous flower is symbolic; visitors should never pick protected mountain plants in an attempt to identify it.\n\nThat boundary between fact and story makes the legend more interesting, not less. Zlatorog turns a familiar caution—take only memories and leave the mountain intact—into a narrative visitors remember.\n\n## A practical Zlatorog-themed day in Trenta\n\nBegin with current information rather than a treasure map. Check the **Triglav National Park** website and local Soča Valley visitor information for opening hours, road conditions, weather and suitable walks. Alpine conditions can change quickly, and a route that looks simple on a screen may be inappropriate after rain, snow or strong wind.\n\nIn the valley, focus on three layers of the story:\n\n1. **The river landscape.** Observe how the young Soča shapes the narrow valley and how settlements fit into limited Alpine space.\n2. **Plants and wildlife.** Look without collecting or approaching. Binoculars are more useful—and more respectful—than leaving a marked path.\n3. **Local interpretation.** Visitor information in Trenta can add natural and cultural context that the short version of the legend cannot provide.\n\nYou do not need to climb a summit to understand Zlatorog. A modest valley walk, chosen for the day’s conditions and your ability, can communicate the legend’s message better than an unsafe attempt to “conquer” the mountains.\n\n## Visit like a guest in Zlatorog’s kingdom\n\nTriglav National Park is a protected landscape and a lived-in place. Keep your visit low-impact:\n\n- remain on marked routes and obey temporary closures;\n- carry out all rubbish, including food scraps;\n- do not pick flowers, move rocks or disturb animals;\n- keep noise low and give wildlife space;\n- use designated parking and public transport where available;\n- take weather protection, water, sturdy footwear and an offline map;\n- turn back when conditions or your experience make continuing unsafe.\n\nFor demanding mountain routes, consult current guidance from the Alpine Association of Slovenia and use a qualified guide when appropriate. Rescue services are not a substitute for preparation.\n\n## When to go\n\nEarly autumn can bring clear views and quieter moments, but daylight is shortening and cold fronts can arrive quickly. Check the forecast and trail information on the morning of your visit. Start early enough to finish well before dark.\n\nOutside the main hiking season, some visitor facilities, mountain huts and transport services may operate reduced hours or close. Verify rather than assume. If high routes are unsuitable, stay in the valley and treat the change of plan as part of responsible Alpine travel.\n\n## Why the legend still matters\n\nZlatorog is sometimes used as a picturesque emblem, but the tale is not simply about a fabulous animal. The hunter sees the mountains as something to possess; the result is loss. Read in today’s tourism context, the lesson is strikingly current.\n\nThe real treasure is not hidden gold. It is the chance to encounter a living Alpine landscape without diminishing it for the next visitor—or for the species that live there year-round.\n\nGo to Trenta for the river, mountains and stories. Leave the flowers where they grow, keep the legend in the realm of imagination, and let Zlatorog remain undefeated.\n\n## Sources\n\n- Slovenian Tourist Board, “Explore the world of Slovenian myths and legends”: https://www.slovenia.info/en/stories/explore-the-world-of-slovenian-myths-and-legends\n- Triglav National Park, official visitor information: https://www.tnp.si/en/visit/\n- Soča Valley, official destination information: https://www.soca-valley.com/en/\n- Alpine Association of Slovenia, mountain information and safety resources: https://www.pzs.si/",
  category: "Vodniki",
  author: "Uredništvo Blog Lab",
  status: "published",
  createdAt: "2026-09-11T12:59:04.000Z",
  updatedAt: "2026-09-11T12:59:04.000Z"
}, {
  id: "world-rowing-masters-regatta-bled-2026-visitor-guide",
  title: "World Rowing Masters Regatta 2026: A Visitor’s Guide to Bled",
  excerpt: "Thousands of masters rowers are racing on Lake Bled from 9 to 13 September. Here is how visitors can watch responsibly and enjoy the destination.",
  seoDescription: "Visit the 2026 World Rowing Masters Regatta at Lake Bled from 9–13 September with practical spectator advice, event links and responsible travel tips.",
  content: "# World Rowing Masters Regatta 2026: A Visitor’s Guide to Bled\n\nLake Bled is more than a postcard this week. From **9 to 13 September 2026**, thousands of masters rowers from around the world are gathering for the World Rowing Masters Regatta at one of the sport’s most recognisable venues.\n\nThe event is already under way, and official World Rowing coverage confirms that racing began on 9 September. For travellers in Slovenia, the remaining programme offers a rare chance to see international rowing against the backdrop of Bled Island, the castle cliff and the Julian Alps.\n\n## First, understand the event\n\nDespite the similar names, this is not the elite World Rowing Championships. It is the **World Rowing Masters Regatta**, an international competition for experienced age-group rowers. Masters racing combines serious competition with the social character of a global gathering: athletes represent clubs and communities, reconnect with long-time rivals and race across multiple age categories and boat classes.\n\nBled Rowing states that the 2026 regatta brings together thousands of participants. The scale means frequent racing and a lively atmosphere around the venue rather than only a handful of headline finals.\n\nThe competition runs until Sunday, 13 September. The official event channels provide the current programme, results and live coverage, and visitors should consult them on the day because race times can change.\n\n## Where to watch\n\nTourism Bled lists the event at Lake Bled, with spectator stands in **Velika Zaka** on the western side of the lake. This is the established rowing venue and the logical starting point for anyone who wants to follow the racing.\n\nArrive early and follow temporary signs, barriers and instructions from stewards. A large regatta affects normal movement around the shoreline, and parts of the lake are subject to event-related restrictions. Tourism Bled announced a partial closure connected with the championship from 7 to 13 September.\n\nDo not enter restricted water areas with a paddleboard, kayak or other craft. The race course, warm-up areas and safety lanes must remain clear. Even if a section of water appears empty, crews can approach quickly and event officials need unobstructed access.\n\nOn shore, stay behind marked boundaries and avoid blocking paths used by athletes carrying long racing shells.\n\n## Make a low-impact day of it\n\nBled will be busy, so the easiest visit is one that does not depend on finding a parking space beside the lake. Check current bus and rail-bus connections before leaving, or park only in designated areas and continue on foot where possible.\n\nThe walk around Lake Bled is normally one of the destination’s simplest pleasures, but event infrastructure and crowds may affect the usual rhythm. Allow extra time and treat any detour as part of the day.\n\nBring water, weather protection and a small pair of binoculars. September mornings beside the lake can feel cool, while sunshine becomes warm in exposed spectator areas. Keep reusable bottles and food packaging with you until you reach the correct waste bins.\n\nCheer without interfering with race instructions or disturbing crews immediately before a start. Rowing demands concentration, and the quiet moments can be as important as the finish-line noise.\n\n## What to do between races\n\nThe regatta can anchor a broader Bled visit without turning the day into a rush.\n\nA walk along the shore offers changing views of Bled Island and the castle. Traditional pletna boats continue Bled’s long relationship with the water, although visitors must respect any temporary navigation restrictions during the event. Bled Castle provides a high viewpoint over the lake, while the island and its church remain the destination’s best-known landmarks.\n\nThe final days of Bled Summer also overlap with the regatta. Tourism Bled has announced a Friday “Regatta Special Slovenian Night” and a Saturday open-stage event on the Lakeside Promenade. Check the live programme before attending.\n\nLocal cafés and restaurants will be busy. Eating outside peak times and choosing locally operated businesses can spread visitor spending beyond the immediate grandstand area. The famous Bled cream cake is an obvious finish, but the town and nearby villages offer much more than one dessert.\n\n## Following from elsewhere\n\nTravellers who cannot reach Bled can still follow the competition. Bled Rowing links to official results and live-stream coverage, while World Rowing publishes video from the event.\n\nUse the official sources rather than relying on an old screenshot of the schedule. Weather, race progression and operational decisions can alter the programme.\n\n## Why Bled and rowing belong together\n\nLake Bled’s calm-water setting and compact shoreline make rowing unusually visible to spectators. The sport also reveals a different side of a destination usually photographed for its island church and castle.\n\nWatching a crew move in rhythm across the lake turns the landscape from a static image into an active arena. At the same time, hosting thousands of athletes places pressure on paths, transport and water access. Visitors can help by arriving responsibly, observing closures and giving athletes and officials the space they need.\n\nThe regatta continues through 13 September. If you are already travelling in northern Slovenia, it is a timely reason to see Bled from a sporting perspective—without forgetting that the lake remains a shared natural and public space.\n\n## Sources\n\n- World Rowing, live Day 1 coverage of the 2026 World Rowing Masters Regatta: https://worldrowing.com/video/watch-live-day-1-2026-world-rowing-masters-championships-regatta-bled-slovenia/\n- Bled Rowing, official event information, programme, results and live-stream links: https://www.bledrowing.com/\n- 2026 World Rowing Masters Regatta official site: https://wrmr2026.com/\n- Tourism Bled, official destination and current event information: https://www.bled.si/\n- Slovenian Tourist Board, Bled destination guide: https://www.slovenia.info/en/places-to-go/regions/alpine-slovenia/bled",
  category: "Šport",
  author: "Uredništvo Blog Lab",
  status: "published",
  createdAt: "2026-09-11T06:58:20.000Z",
  updatedAt: "2026-09-11T06:58:20.000Z"
}, {
  id: "vipava-harvest-festival-2026-guide",
  title: "Vipava Harvest Festival 2026: A Weekend of Wine and Tradition",
  excerpt: "Vipava’s annual harvest celebration returns from 11 to 13 September with local wine, food, music, sport and living traditions in the heart of the valley.",
  seoDescription: "Plan a visit to the Vipava Harvest Festival on 11–13 September 2026, with programme highlights, responsible wine-tasting advice and practical travel tips.",
  content: "# Vipava Harvest Festival 2026: A Weekend of Wine and Tradition\n\nThe Vipava Valley enters one of its most atmospheric moments this weekend. From **11 to 13 September 2026**, the town of Vipava will host its annual Harvest Festival, bringing local winemakers, food producers, musicians, athletes and families together in and around the Main Square.\n\nFor international visitors, the festival is an opportunity to experience Slovenian wine culture as a living community tradition rather than simply a formal tasting. The programme stretches across three days and combines wine, regional food, sport, folklore, crafts and entertainment.\n\n## Why harvest matters in the Vipava Valley\n\nVineyards are not merely scenery in the Vipava Valley. Winegrowing is closely connected with family life, local knowledge and the identity of villages across the region. Harvest season marks the point when a year of work in the vineyards moves into the cellar and a new vintage begins.\n\nThe festival turns that agricultural moment into a public celebration. Visitors can meet producers, learn about local varieties and see how contemporary tourism remains connected to the valley’s working landscape.\n\nThe Vipava Valley is particularly associated with indigenous and regionally important grapes. At a festival tasting, ask producers what grows best in their specific part of the valley instead of looking only for familiar international varieties. The conversation is often as memorable as the wine.\n\n## What happens across the weekend\n\nAccording to the organisers’ information published on 10 September, the festival begins on **Friday evening** with a cultural atmosphere as Vipava opens the celebration.\n\n**Saturday** traditionally has a strong sporting component. The programme includes the long-established cycling climb toward Mount Nanos, while children and families can encounter several sports in the Main Square. Music takes over later in the day, turning the centre of Vipava into an evening meeting place.\n\n**Sunday** is the main day for heritage and wine. Dance and folklore performances celebrate local culture, while the traditional blessing of the must symbolically marks the beginning of the new vintage. The Mayor’s Sparkling Wine is also announced as an award for winemakers from the Municipality of Vipava.\n\nA wine fair in Lanthieri Park brings together producers from across the valley, with particular attention to indigenous Vipava grapes. A farmers’ market adds cheeses, cured meats, preserves, crafts and other local products. Exhibitions, children’s workshops and entertainment broaden the programme beyond wine tasting.\n\nThe organisers also highlight Lanthieri Manor, where visitors can encounter a large collection of wines from Vipava Valley producers. Individual activities and times may change, so check the current programme before setting out.\n\n## How to visit well\n\nVipava is compact enough to explore on foot once you arrive. Begin around the Main Square, then continue to Lanthieri Park and the manor. Allow time to wander rather than trying to treat the festival as a checklist.\n\nBring some cash because payment options can differ between small producers and market stalls. A reusable water bottle is useful, and alternating water with wine is both sensible and respectful to the tasting experience.\n\nIf you plan to sample wine, do not drive. Arrange a designated driver, stay overnight in the valley or confirm public transport and return connections in advance. Festival weekends can increase demand for accommodation and taxis, so last-minute availability should not be assumed.\n\nWine tastings are for adults, but the broader event includes food, sport, culture and family activities. Visitors travelling with children should check the latest programme for suitable times and locations.\n\n## Taste with curiosity, not speed\n\nA harvest festival is not a race through as many glasses as possible. Small pours make it easier to compare wines and speak with producers. Ask about the vineyard, the grape variety and the year rather than requesting only “red” or “white.”\n\nDo not enter vineyards or working areas without permission. Harvest is a demanding period, and much of the landscape around Vipava remains an active workplace. Buying directly from local producers, choosing local food and disposing of waste properly are simple ways to make the visit more beneficial to the host community.\n\nWeather in the valley can change, even when early September remains warm. Take sun protection for the daytime, a light layer for the evening and rain protection if the forecast requires it.\n\n## Make it part of a wider Vipava visit\n\nThe festival can anchor a longer stay in the valley. Vipava itself offers historic streets, springs and views toward the surrounding plateaus. Nearby villages are connected with wine estates, local food and walking or cycling routes.\n\nAvoid overloading a single day with distant attractions. A slow weekend based in or near Vipava gives you more time with local producers and removes pressure to drive after tasting.\n\nThe 2026 Harvest Festival is timely, but its appeal is deeper than a three-day programme. It offers a window into how landscape, agriculture and community still meet in one of Slovenia’s most distinctive wine regions.\n\n## Sources\n\n- Slovenia Green, “Vipava Harvest Festival – where wine tells a story, tradition runs deep, and celebration comes naturally,” published 10 September 2026: https://www.slovenia-green.si/magazine/vipava-harvest-festival/\n- Vipava Tourist Board, official visitor portal: https://www.vipava.si/Home?lang=en\n- Vipava Valley official tourism portal: https://www.vipavskadolina.si/\n- Slovenian Tourist Board, wine stories and experiences: https://www.slovenia.info/en/things-to-do/food-and-wine/wine",
  category: "Aktualno",
  author: "Uredništvo Blog Lab",
  status: "published",
  createdAt: "2026-09-10T18:58:37.000Z",
  updatedAt: "2026-09-10T18:58:37.000Z"
}, {
  id: "ljubljana-dragon-legend-walking-guide",
  title: "Why Ljubljana Has Dragons: Legend, History and a Walking Trail",
  excerpt: "Follow Ljubljana’s dragon from the legend of Jason and the Argonauts to the city’s coat of arms, Dragon Bridge and modern streets.",
  seoDescription: "Discover why dragons symbolize Ljubljana, separate the Jason legend from documented history, and follow an easy dragon-themed walking route through the city.",
  content: "# Why Ljubljana Has Dragons: Legend, History and a Walking Trail\n\nA green dragon watches over Ljubljana from the city’s coat of arms. Four larger dragons guard a famous bridge, while smaller versions appear on signs, souvenirs, drain covers and decorations. The creature is so closely tied to Slovenia’s capital that it can feel as if it has always lived here.\n\nThe real story is more interesting because it has two layers: a colourful foundation legend involving the Greek hero Jason, and a documented history showing how the dragon gradually became Ljubljana’s civic symbol.\n\n## The legend: Jason reaches the Ljubljana Marshes\n\nAccording to the story promoted in Ljubljana’s local tradition, Jason and the Argonauts fled with the Golden Fleece aboard the Argo. Their unusual return route took them across the Black Sea, up the Danube and Sava rivers and into the Ljubljanica.\n\nNear the source of the Ljubljanica, the travellers supposedly reached a great lake surrounded by marshland. A dragon lived there. Jason fought the creature, defeated it and continued toward the Adriatic, where the Argonauts rebuilt their ship and sailed home.\n\nThis is a legend, not a verified account of Ljubljana’s foundation. Jason belongs to Greek mythology, and there is no historical evidence that the Argonauts founded the city or fought an animal in the Ljubljana Marshes. The tale matters because communities use legends to explain landscapes and symbols—not because every detail should be read as fact.\n\n## The history: from decoration to city protector\n\nLjubljana Tourism explains that a dragon appeared as a decorative element on the medieval city coat of arms before gaining a more central role. Over time, its meaning changed. Instead of remaining only a monster to be defeated, it became a protector associated with courage, strength and wisdom.\n\nThat transformation is visible across the city. The dragon now stands above Ljubljana Castle on the coat of arms and functions as a civic emblem rather than a warning of danger.\n\nThe symbol’s most dramatic physical form arrived at the beginning of the twentieth century.\n\n## Dragon Bridge: where myth meets engineering\n\nDragon Bridge was constructed between 1900 and 1901. Its original name honoured Emperor Franz Joseph I, and the bridge was built as Ljubljana was embracing modern Art Nouveau design and new construction technology.\n\nThe structure was Ljubljana’s first reinforced-concrete bridge and was among Europe’s largest bridges of its type at the time. Engineer Josef Melan prepared the structural design. Dalmatian architect Jurij Zaninović, a student of Viennese architect Otto Wagner, designed the decorative elements.\n\nEarly plans envisaged winged lions at the bridge ends. The final design replaced them with dragons, creating the landmark visitors know today. The four large copper-sheet statues are theatrical, memorable and perfectly suited to a city already connected with dragon imagery.\n\nThe historical bridge and the Jason story should therefore not be collapsed into a single claim. The legend gave the city a compelling narrative; the documented Art Nouveau bridge gave that narrative one of its most visible monuments.\n\n## A self-guided dragon walk\n\nYou can follow Ljubljana’s dragon story on a compact walk through the historic centre.\n\nBegin at **Dragon Bridge** on Resljeva cesta. Walk around all four corners rather than taking a single photograph: each dragon has a slightly different silhouette depending on the angle, and the bridge’s lamps and balustrades reveal its Art Nouveau character.\n\nContinue toward **Ljubljana Central Market** and the riverside arcades. Look for smaller dragon images on urban details and local products. The point is not to follow a formally marked trail, but to notice how thoroughly the emblem has entered everyday city life.\n\nCross into the old town and climb—or take the funicular—to **Ljubljana Castle**. The castle itself is not proof of the Jason legend, but the dragon on the city coat of arms is displayed prominently, and the site helps explain how the symbol functions as Ljubljana’s guardian.\n\nFinish by looking back over the city from Castle Hill. From above, the Ljubljanica, the marshes to the south and the routes through the historic centre make the geography of the legend easier to imagine.\n\n## Look beyond the souvenir\n\nDragon merchandise is everywhere in Ljubljana, but the symbol rewards closer attention. It connects mythology, medieval heraldry, Habsburg-era urban modernization and contemporary city identity.\n\nFor families, the story offers an easy game: count dragons between the bridge and castle. For architecture enthusiasts, Dragon Bridge is a serious work of technical and artistic heritage. For travellers interested in folklore, it is a reminder that legends are living cultural objects. They change as cities reinterpret them.\n\nLjubljana’s dragon is not historically proven to have lived in the marshes. Yet it is unquestionably real as a symbol—cast in metal, printed on the coat of arms and woven into the way the city presents itself to the world.\n\n## Sources\n\n- Ljubljana Tourism, “Ljubljana, City of Dragons”: https://www.visitljubljana.com/en/visitors/sights-and-activities/ljubljana-city-of-dragons\n- Ljubljana Tourism, Dragon Bridge: https://www.visitljubljana.com/en/poi/dragon-bridge\n- Slovenian Tourist Board, Slovenian myths and legends: https://www.slovenia.info/en/stories/explore-the-world-of-slovenian-myths-and-legends\n- Ljubljana Castle, visitor experiences: https://www.ljubljanskigrad.si/en/experiences/",
  category: "Vodniki",
  author: "Uredništvo Blog Lab",
  status: "published",
  createdAt: "2026-09-10T13:03:45.000Z",
  updatedAt: "2026-09-10T13:03:45.000Z"
}, {
  id: "velika-planina-hiking-guide-september",
  title: "Hiking Velika Planina: A Responsible Day Trip from Ljubljana",
  excerpt: "Walk through high-Alpine pastures and one of Europe’s largest shepherd settlements with this practical, responsible guide to Velika Planina.",
  seoDescription: "Plan a responsible hiking day trip to Velika Planina from Ljubljana, with access advice, trail options, September cable-car times and mountain etiquette.",
  content: "# Hiking Velika Planina: A Responsible Day Trip from Ljubljana\n\nLess than a day’s journey from Ljubljana, Velika Planina combines an accessible mountain walk with one of Slovenia’s most distinctive living landscapes. The high plateau above Kamnik is known for broad pastures, views toward the Kamnik–Savinja Alps and an active shepherd settlement whose oval-roofed huts give the area its unmistakable character.\n\nThis is not an open-air theme park. Velika Planina is a working mountain pasture, a sensitive natural environment and a place where visitors share the paths with shepherds, cattle and other hikers. Approaching it as both a hike and a cultural visit makes for a better day out—and helps protect what makes the plateau special.\n\n## The easiest active route\n\nThe most straightforward option begins at the cable-car lower station in the Kamniška Bistrica valley. The cable car climbs to the upper station, where visitors can either continue by chairlift or walk uphill on the marked route. The official Velika Planina hiking guide estimates the walk from the upper cable-car station at roughly 30–45 minutes of moderate walking. Taking the chairlift instead leaves more time and energy for exploring the plateau itself.\n\nOnce on the upper plateau, a rewarding route links Gradišče, the shepherd settlement and Mala Planina. Exact distance and duration depend on the chosen paths and stops, so visitors should consult the current trail map rather than treating a short online description as navigation.\n\nMore experienced hikers can ascend from lower trailheads, but those routes require more time, fitness and preparation. Trail difficulty should be matched to the least experienced person in the group.\n\n## What makes the walk special\n\nVelika Planina is one of Slovenia’s best-known mountain pastures. The settlement’s traditional huts sit among grazing land rather than along an ordinary village street. The Preskar Museum hut preserves an older architectural form and offers context for the seasonal life of herders.\n\nThe plateau is also a place to slow down. The walk is less about conquering a summit than moving between views, pastureland and cultural landmarks. Fresh dairy products may be available directly from shepherds during the summer grazing season, generally from mid-June to mid-September. Availability varies, and cash is useful because shepherds may not accept cards.\n\nEarly September can be an excellent time to visit: summer crowds may begin to ease, while the grazing season and mountain-hut services can still overlap. Conditions change quickly, however, and a sunny morning in the valley does not guarantee stable weather on the plateau.\n\n## Practical information for September 2026\n\nFor the period from 1 to 30 September, the operator’s published timetable lists the cable car daily from 08:00 to 18:00, departing every full hour. The chairlift is listed from 08:30 to 17:30. These times were checked on 10 September 2026, but visitors should confirm the live timetable and weather immediately before travelling because operations can change.\n\nThe lower cable-car station is in the Kamniška Bistrica valley, about three kilometres before the end of the road. Drivers should use designated parking areas and follow local signs. Travellers without a car should check current public-transport connections to Kamnik and onward options in advance; the final connection to the cable-car station may require additional planning.\n\nBring proper walking shoes, water, sun protection and a warm or waterproof layer. Even an easy plateau walk takes place in a mountain environment. In poor visibility, strong wind or storms, turning back is the correct decision.\n\n## Share the pasture responsibly\n\nOfficial visitor guidance asks hikers to stay on marked paths, avoid picking flowers and carry waste back to the valley. Cattle should be observed from a distance and never fed. Dogs must remain on a leash so they do not disturb livestock, wildlife or other visitors.\n\nCamping and open fires are not permitted on the plateau. Drones, loud music and shortcuts across pasture may also disrupt the working landscape, even when they appear harmless to an individual visitor.\n\nIf you meet cattle on or near a trail, remain calm, give them generous space and avoid walking between cows and calves. A responsible visit is not only about following rules; it is about recognizing that tourism is temporarily entering someone else’s workplace and an animal habitat.\n\n## A day trip that feels much farther away\n\nVelika Planina works particularly well for travellers who want an active day without committing to a technical Alpine ascent. It offers real walking, broad mountain scenery and a direct encounter with Slovenia’s pastoral heritage within reach of Ljubljana.\n\nStart early, check conditions, leave room for unplanned stops and resist the urge to rush from one photo point to the next. The plateau’s strongest impression comes from the combination of movement and stillness: cowbells across the grass, changing clouds above the Alps and footpaths connecting a living landscape.\n\n## Sources\n\n- Slovenian Tourist Board, Velika Planina overview: https://www.slovenia.info/en/places-to-go/attractions/velika-planina\n- Velika Planina official site, walks and hiking: https://www.velikaplanina.si/en/activities/summer-activities/walks-and-hiking/\n- Velika Planina official timetable, checked 10 September 2026: https://www.velikaplanina.si/en/pricelist/\n- Velika Planina official responsible-visit guidance: https://www.velikaplanina.si/en/7-principles-of-responsible-visiting/\n- Velika Planina official directions: https://www.velikaplanina.si/en/about-us/how-to-find-us/",
  category: "Šport",
  author: "Uredništvo Blog Lab",
  status: "published",
  createdAt: "2026-09-10T13:02:15.000Z",
  updatedAt: "2026-09-10T13:02:15.000Z"
}, {
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
  heroImage: null,
  video: null,
  gallery: [],
  sources: [],
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

function InlineMarkdown({ text }) {
  const tokenPattern = /(\*\*[^*]+\*\*|\[[^\]]+\]\(https?:\/\/[^)\s]+\)|`[^`]+`)/g;
  const parts = [];
  let lastIndex = 0;
  let match;

  while ((match = tokenPattern.exec(text)) !== null) {
    if (match.index > lastIndex) parts.push(text.slice(lastIndex, match.index));
    const token = match[0];

    if (token.startsWith("**")) {
      parts.push(<strong key={match.index}>{token.slice(2, -2)}</strong>);
    } else if (token.startsWith("[")) {
      const linkMatch = token.match(/^\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)$/);
      if (linkMatch) {
        parts.push(
          <a key={match.index} href={linkMatch[2]} target="_blank" rel="noopener noreferrer">
            {linkMatch[1]}
          </a>
        );
      }
    } else {
      parts.push(<code key={match.index}>{token.slice(1, -1)}</code>);
    }

    lastIndex = tokenPattern.lastIndex;
  }

  if (lastIndex < text.length) parts.push(text.slice(lastIndex));
  return parts;
}

function ArticleBody({ content }) {
  const lines = content.split("\n");
  const blocks = [];

  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index];

    if (isInlineMediaLine(line)) {
      blocks.push(<InlineArticleMedia line={line} key={index} />);
      continue;
    }

    if (line.startsWith("### ")) {
      blocks.push(<h3 key={index}><InlineMarkdown text={line.slice(4)} /></h3>);
      continue;
    }
    if (line.startsWith("## ")) {
      blocks.push(<h2 key={index}><InlineMarkdown text={line.slice(3)} /></h2>);
      continue;
    }
    if (line.startsWith("# ")) {
      blocks.push(<h1 key={index}><InlineMarkdown text={line.slice(2)} /></h1>);
      continue;
    }
    if (line.startsWith("- ")) {
      const items = [];
      const listKey = index;
      while (index < lines.length && lines[index].startsWith("- ")) {
        items.push(<li key={index}><InlineMarkdown text={lines[index].slice(2)} /></li>);
        index += 1;
      }
      index -= 1;
      blocks.push(<ul key={listKey}>{items}</ul>);
      continue;
    }
    if (/^\d+\.\s/.test(line)) {
      const items = [];
      const listKey = index;
      while (index < lines.length && /^\d+\.\s/.test(lines[index])) {
        items.push(<li key={index}><InlineMarkdown text={lines[index].replace(/^\d+\.\s/, "")} /></li>);
        index += 1;
      }
      index -= 1;
      blocks.push(<ol key={listKey}>{items}</ol>);
      continue;
    }
    if (!line.trim()) {
      blocks.push(<div className="line-space" key={index} />);
      continue;
    }

    blocks.push(<p key={index}><InlineMarkdown text={line} /></p>);
  }

  return <div className="article-body">{blocks}</div>;
}

const DEFAULT_SITE_SETTINGS = {
  brand: "Blog Lab",
  heroEyebrow: "NEODVISNO UREDNIŠTVO",
  heroTitle: "Zgodbe, ki štejejo.",
  heroEmphasis: "Jasno in brez odvečnega hrupa.",
  heroSubtitle: "Vsak dan preverjene zgodbe, napisane z uredniškim standardom, jasnim kontekstom in neposrednimi viri.",
  heroCta: "Odpri uredniški terminal",
  footerText: "Preverjene zgodbe. Jasen kontekst. Neposredni viri.",
  showLivePulse: true
};

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
  const [articles, setArticles] = useState(starterArticles);
  const [rubrics, setRubrics] = useState([]);
  const [siteSettings, setSiteSettings] = useState(DEFAULT_SITE_SETTINGS);
  const [publicCategory, setPublicCategory] = useState("");
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
    // Public content is repository-backed so every browser and device sees
    // exactly the same published articles. Browser storage is never a source
    // of truth for public content.
    setArticles(starterArticles);
    setReady(true);
  }, []);

  useEffect(() => {
    let active = true;
    const base = import.meta.env.BASE_URL || "/";
    fetch(`${base}site-rubrics.json?t=${Date.now()}`, { cache: "no-store" })
      .then((response) => response.ok ? response.json() : [])
      .then((data) => {
        if (!active) return;
        const items = Array.isArray(data) ? data : [];
        setRubrics(items.filter((item) => item && typeof item.name === "string").slice(0, 12));
      })
      .catch(() => { if (active) setRubrics([]); });
    return () => { active = false; };
  }, []);

  useEffect(() => {
    let active = true;
    const base = import.meta.env.BASE_URL || "/";
    fetch(`${base}site-settings.json?t=${Date.now()}`, { cache: "no-store" })
      .then((response) => response.ok ? response.json() : DEFAULT_SITE_SETTINGS)
      .then((data) => {
        if (!active) return;
        const incoming = data && typeof data === "object" ? data : {};
        setSiteSettings({ ...DEFAULT_SITE_SETTINGS, ...incoming });
      })
      .catch(() => { if (active) setSiteSettings(DEFAULT_SITE_SETTINGS); });
    return () => { active = false; };
  }, []);


  useEffect(() => {
    if (!ready) return undefined;

    function syncViewFromUrl() {
      const requestedId = new URLSearchParams(window.location.search).get("article");
      if (requestedId && articles.some((article) => article.id === requestedId)) {
        setSelectedId(requestedId);
        setView("article");
      } else {
        setSelectedId("");
        setView("home");
      }
    }

    syncViewFromUrl();
    window.addEventListener("popstate", syncViewFromUrl);
    return () => window.removeEventListener("popstate", syncViewFromUrl);
  }, [articles, ready]);

  useEffect(() => {
    const selectedArticle = articles.find((article) => article.id === selectedId);
    const description = document.querySelector('meta[name="description"]');

    document.title = selectedArticle ? `${selectedArticle.title} | Blog Lab` : "Blog Lab";
    if (description) {
      description.setAttribute(
        "content",
        selectedArticle?.seoDescription || "Blog Lab – preprosta platforma za pisanje in objavljanje člankov."
      );
    }
  }, [articles, selectedId]);

  useEffect(() => {
    if (!toast) return;
    const timer = setTimeout(() => setToast(""), 2400);
    return () => clearTimeout(timer);
  }, [toast]);

  const published = useMemo(
    () => articles.filter((article) => article.status === "published" && !article.localOnly),
    [articles]
  );

  const visiblePublished = useMemo(() => {
    if (!publicCategory) return published;
    const target = publicCategory.trim().toLowerCase();
    return published.filter((article) => String(article.category || "").trim().toLowerCase() === target);
  }, [published, publicCategory]);

  const shownArticles = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    return articles
      .filter((article) => filter === "Vse" || (filter === "Objavljeno" ? article.status === "published" : article.status === "draft"))
      .filter((article) => !normalized || `${article.title} ${article.excerpt} ${article.category}`.toLowerCase().includes(normalized))
      .sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt));
  }, [articles, filter, query]);

  const selected = articles.find((article) => article.id === selectedId);

  function navigate(nextView) {
    if (nextView !== "article") {
      const url = new URL(window.location.href);
      url.searchParams.delete("article");
      window.history.pushState({}, "", `${url.pathname}${url.search}${url.hash}`);
      setSelectedId("");
    }
    setView(nextView);
    setPreview(false);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function showPublicCategory(name = "") {
    setPublicCategory(name);
    navigate("home");
  }

  function openEditorialTerminal() {
    window.open(TERMINAL_URL, "_blank", "noopener,noreferrer");
  }

  function newArticle() {
    openEditorialTerminal();
  }

  function editArticle() {
    openEditorialTerminal();
  }

  function openArticle(article) {
    const url = new URL(window.location.href);
    url.searchParams.set("article", article.id);
    window.history.pushState({}, "", `${url.pathname}${url.search}${url.hash}`);
    setSelectedId(article.id);
    setView("article");
    setPreview(false);
    window.scrollTo({ top: 0, behavior: "smooth" });
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
    const article = normalizeArticleMedia({
      ...draft,
      id,
      title: draft.title.trim(),
      excerpt: draft.excerpt.trim() || draft.content.replace(/^#+\s*/gm, "").trim().slice(0, 155),
      author: draft.author.trim() || "Uredništvo",
      status,
      localOnly: true,
      createdAt: draft.createdAt || now,
      updatedAt: now
    });
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
        <button className="brand" onClick={() => showPublicCategory("")} aria-label={`${siteSettings.brand} – domov`}>
          <span className="brand-mark">B</span>
          <span>{siteSettings.brand}</span>
        </button>
        <nav aria-label="Glavna navigacija">
          <button className={view === "home" && !publicCategory ? "active" : ""} onClick={() => showPublicCategory("")}>
            <Icon name="home" /> Objave
          </button>
          {rubrics.map((rubric) => (
            <button
              key={rubric.slug || rubric.name}
              className={view === "home" && publicCategory === rubric.name ? "active" : ""}
              onClick={() => showPublicCategory(rubric.name)}
            >
              {rubric.name}
            </button>
          ))}
          <button className={view === "dashboard" ? "active" : ""} onClick={() => navigate("dashboard")}>
            <Icon name="file" /> Arhiv
          </button>
        </nav>
        <button className="primary small" onClick={newArticle} id="new-article-button" data-testid="new-article">
          <span>↗</span> Uredniški terminal
        </button>
      </header>

      {view === "home" && (
        <>
          <section className="hero">
            <div className="eyebrow"><span /> {siteSettings.heroEyebrow}</div>
            <h1>{siteSettings.heroTitle}<br /><em>{siteSettings.heroEmphasis}</em></h1>
            <p>{siteSettings.heroSubtitle}</p>
            <button className="primary" onClick={newArticle}>{siteSettings.heroCta} <Icon name="arrow" /></button>
          </section>

          <div className={`home-content container ${siteSettings.showLivePulse ? "" : "no-live-pulse"}`}>
            {siteSettings.showLivePulse && <LivePulse />}
            <section className="feed">
            <div className="section-heading">
              <div>
                <span className="kicker">{publicCategory ? "RUBRIKA" : "ZADNJE OBJAVE"}</span>
                <h2>{publicCategory || "Sveže iz uredništva"}</h2>
              </div>
              <span className="count">{visiblePublished.length} {visiblePublished.length === 1 ? "objava" : "objav"}</span>
            </div>
            <div className="post-grid">
              {visiblePublished.length ? visiblePublished.slice(0, 12).map((article, index) => (
                <a
                  className={`post-card ${index === 0 ? "featured" : ""}`}
                  href={`?article=${encodeURIComponent(article.id)}`}
                  key={article.id}
                  onClick={(event) => {
                    event.preventDefault();
                    openArticle(article);
                  }}
                >
                  <ArticleHero article={article} compact />
                  <div className="card-copy">
                    <div className="meta"><span>{article.category}</span><span>{readingTime(article.content)} min branja</span></div>
                    <h3>{article.title}</h3>
                    <p>{article.excerpt}</p>
                    <div className="card-foot"><span>{article.author}</span><span>{formatDate(article.updatedAt)}</span></div>
                  </div>
                </a>
              )) : (
                <div className="empty-state">
                  <h3>{publicCategory ? `V rubriki ${publicCategory} še ni objav.` : "Še ni objavljenih člankov."}</h3>
                  <p>{publicCategory ? "Ko bo objavljen članek v tej kategoriji, se bo prikazal tukaj." : "Ustvarite članek in ga objavite — prikazal se bo tukaj."}</p>
                  <button className="secondary" onClick={newArticle}>Ustvari članek</button>
                </div>
              )}
            </div>
            </section>
          </div>
        </>
      )}

      {view === "dashboard" && (
        <section className="dashboard container">
          <div className="page-title">
            <div><span className="kicker">UREDNIK</span><h1>Vsi članki</h1><p>Vsi prikazani članki so trajno shranjeni v GitHub repozitoriju in so enaki na vseh napravah.</p></div>
            <button className="primary" onClick={newArticle}>Odpri uredniški terminal ↗</button>
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
                  <button onClick={openEditorialTerminal}>Upravljaj v terminalu ↗</button>
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
              <MediaEditorFields draft={draft} setDraft={setDraft} />
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
          <ArticleHero article={selected} />
          <ArticleBody content={selected.content} />
          <ArticleVideo video={selected.video} />
          <ArticleGallery items={selected.gallery} />
          <ArticleSources items={selected.sources} />
          <div className="article-end"><span>Konec članka</span><button className="secondary" onClick={openEditorialTerminal}>Uredniški terminal ↗</button></div>
        </article>
      )}

      {preview && (
        <div className="modal-backdrop" onMouseDown={() => setPreview(false)}>
          <div className="preview-modal" onMouseDown={(event) => event.stopPropagation()} role="dialog" aria-modal="true" aria-label="Predogled članka">
            <button className="modal-close" onClick={() => setPreview(false)}><Icon name="close" /></button>
            <span className="article-category">{draft.category}</span>
            <h1>{draft.title || "Naslov članka"}</h1>
            <p className="preview-excerpt">{draft.excerpt || "Kratek povzetek članka bo prikazan tukaj."}</p>
            <ArticleHero article={draft} />
            <ArticleBody content={draft.content || "Vsebina članka bo prikazana tukaj."} />
            <ArticleVideo video={draft.video} />
            <ArticleGallery items={draft.gallery} />
            <ArticleSources items={draft.sources} />
          </div>
        </div>
      )}

      {toast && <div className="toast" role="status">{toast}</div>}

      <footer>
        <span>{siteSettings.brand}</span><p>{siteSettings.footerText}</p><span>Uredniška platforma</span>
      </footer>
    </main>
  );
}
