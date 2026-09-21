Warning: truncated output (original token count: 95502)
Total output lines: 2721

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
    "id": "cycling-bohinj-family-car-light-guide",
    "title": "Cycling Bohinj: A Family-Friendly Car-Light Guide",
    "excerpt": "Plan a gentle ride through the Bohinj valleys with practical guidance on route character, bike-and-train access, equipment and respectful cycling.",
    "seoDescription": "Cycle Bohinj without a car: route character, bike-and-train access, safety, equipment and responsible riding in the Julian Alps.",
    "content": "Bohinj is a rewarding place to explore by bicycle without committing to a technical mountain-bike tour. Its official destination website describes the **Bohinj Cycling Route** as a paved, well-marked connection between the Lower and Upper Bohinj valleys, combining gentle flat stretches with some short climbs and descents. This guide helps visitors decide whether the ride suits them and how to plan it without relying on a car.\n\n## What the ride is like\n\nThe route passes Alpine villages and open valley scenery rather than making a complete traffic-free circuit around Lake Bohinj. Expect a mixture of dedicated cycling infrastructure and places shared with other users. The Na Rju bridge, inspired by the form of a hayrack, is one of the route's distinctive modern landmarks.\n\nThis is generally a good choice for recreational riders and families who are already comfortable controlling a bicycle, but **family-friendly does not mean risk-free**. Conditions, traffic and individual ability still matter.\n\n### Before setting out\n\n1. Check the current forecast and any local notices on the [official Bohinj cycling page](https://www.bohinj.si/en/cycling/).\n2. Choose a roadworthy bicycle with working front and rear brakes.\n3. Carry water, a basic repair kit and a charged phone.\n4. Wear a helmet; it is sensible for every rider even where not legally required for an adult.\n5. Save your intended return connection before leaving, especially outside the main visitor season.\n\n## Arriving without a car\n\nBohinjska Bistrica railway station is a practical starting point for the valley. Slovenian Railways permits accompanied bicycles only on services marked with a bicycle symbol in its timetable. A bicycle ticket costs **€3 per single journey**, is bought from train staff, and does not reserve a space. Capacity is limited and staff may refuse a bicycle when the train is full.\n\nFor a car-light day, use this order:\n\n- find a train marked for bicycles in the [live Slovenian Railways timetable](https://potniski.sz.si/en/);\n- avoid weekday peaks from 06:00–08:00 and 14:00–16:00 when possible;\n- confirm that no replacement bus is operating, because bicycles are not accepted on replacement buses;\n- arrive early enough to load your own bicycle safely;\n- if bringing an e-bike, keep its original undamaged battery fitted, switch it off aboard the train and do not charge it.\n\nTreat the timetable result and the bicycle pictogram as the final check. Search for \u0060Bohinjska Bistrica\u0060, not merely “Lake Bohinj.”\n\n## Riding safely and responsibly\n\nBohinj lies within a sensitive Alpine landscape. The destination's cycling rules ask riders to use only open routes, stay away from protected habitats and meadows, respect private property, avoid skidding and take all rubbish away.\n\n- Slow down before blind bends and whenever walkers, children, livestock or agricultural machinery are present.\n- Give way to other path users unless signs clearly grant cyclists priority.\n- Use a bell or a friendly verbal warning before passing, then leave generous space.\n- Do not create shortcuts or ride muddy paths where tyres can cause lasting damage.\n- Carry lights and reflectors for low visibility; weather can change quickly in an Alpine valley.\n- Turn back if rain, fatigue, mechanical trouble or fading daylight makes the plan unsafe.\n\nMandatory bicycle equipment in Slovenia includes effective brakes, a bell, appropriate lights and reflectors. Riders under 14 and children carried as passengers must wear a helmet; this guide recommends one for everyone.\n\n## A sensible half-day plan\n\nStart in Bohinjska Bistrica, join the signed valley route and ride toward the lake at a relaxed pace. Pause at villages and viewpoints without blocking the path. Decide your turnaround point according to the least confident rider, the weather and your confirmed return connection. A short out-and-back ride is often better than forcing a long itinerary.\n\nBike rental is available from several operators listed by Bohinj Tourism. Prices and opening hours vary, so contact the selected provider directly rather than relying on an old listing. Ask whether a helmet, lock, repair kit and roadside support are included.\n\n## Direct sources\n\n- [Bohinj Tourism: Cycling, route description and cycling rules](https://www.bohinj.si/en/cycling/)\n- [Slovenian Railways: Taking a bicycle on the train](https://potniski.sz.si/en/useful-information/take-your-bike-on-the-train/)\n- [Slovenian Railways: Live timetable](https://potniski.sz.si/en/)\n\nRoute guidance, transport rules and prices were last checked on **21 September 2026**. Recheck live conditions before departure.",
    "category": "Šport",
    "author": "Uredništvo Blog Lab",
    "status": "published",
    "heroImage": null,
    "video": null,
    "gallery": [],
    "sources": [
      {
        "label": "Bohinj Tourism — Cycling",
        "url": "https://www.bohinj.si/en/cycling/"
      },
      {
        "label": "Slovenian Railways — Take your bike on board",
        "url": "https://potniski.sz.si/en/useful-information/take-your-bike-on-the-train/"
      },
      {
        "label": "Slovenian Railways — Timetable",
        "url": "https://potniski.sz.si/en/"
      }
    ],
    "createdAt": "2026-09-21T08:57:07+02:00",
    "updatedAt": "2026-09-21T08:57:07+02:00"
  },

  {
    "id": "anja-rakusa-brus-pomemben-argument-za-mojo-kandidaturo-je-izkusnja-z-aktualno-vlado-ki-str-2c38f7cd",
    "title": "Anja Rakuša Brus: Pomemben argument za mojo kandidaturo je izkušnja z aktualno vlado, ki stroke ne posluša dovolj…",
    "excerpt": "Aktualno: pregled preverljivih informacij iz današnjih virov, z osrednjo zgodbo »Anja Rakuša Brus: Pomemben argument za mojo kandidaturo je izkušnja z aktualno vlado, ki stroke ne posluša dovolj…«.",
    "seoDescription": "Aktualno: pregled preverljivih informacij iz današnjih virov, z osrednjo zgodbo »Anja Rakuša Brus: Pomemben argument za mojo kandidaturo je izkušnja z aktualn",
    "content": "**Aktualno, 20. 9. 2026.** Anja Rakuša Brus: Pomemben argument za mojo kandidaturo je izkušnja z aktualno vlado, ki stroke ne posluša dovolj Nova24TV\n\nSpodaj so zbrane le informacije, ki jih je mogoče neposredno povezati z objavljenimi viri. Kjer vir ne ponuja dovolj podrobnosti, besedilo ne zapolnjuje vrzeli z ugibanjem.\n\nVir: Nova24TV. Objavljeno: Mon, 16 Mar 2026 07:00:00 GMT. [Odpri izvirni vir](https://news.google.com/rss/articles/CBMizAFBVV95cUxObkJrTGhvMXhVSkJUcExOWUg0cWlVYmM5R0J6eXdTZ1dmdGRVSHVTek9EM09mUy0xdGF1eEo5X196dy1McUlFUjJwRUpjeTJYNGt0OUxqaG4zOTZBTkhqc1RCZkgtOTZQV29qQmQ3QXU5REFCOWEydXlCT0hLWTdZUVRpR19razFPVy1SMndKaGZUNUVKcXFCM05feHNmN2dqcTdJT1h3ekw1RG5Gd2F3NzI0c2NObloyd2plV0MtX056U0JGTTY4QlZBQXk?oc=5)\n\n## Dopolnitev vira 2: Demokracija\n\n(AKTUALNO) V novi številki revije Demokracija preberite: Izključujejo in zavirajo razvoj! Janša: Osamosvojitvena Slovenija ne bo nikoli več nastavljala drugega lica! Razsipna Golobova ministrstva! Intervjuja: Monika Kirbiš Rojs in Jože Plut Demokracija\n\n Vir: Demokracija. Objavljeno: Wed, 01 Jul 2026 07:00:00 GMT. [Odpri izvirni vir](https://news.google.com/rss/articles/CBMixgJBVV95cUxNZTY0M3ozT2IxZ2U2Y1YwSVhudWFEWjRUMWFoX2RHcjd3MnFHVDN4aVZQbUYyZmNGZmxhc1ZqSVlxOFJKbVBWS2VvUDNoOVlhbDBwS0ZVQUQzRGpsZWx3SGlYVkRBUGtTa2wwU3VzV2xxejR2ajNXbEJOWkZ3dEJpVXdMWTFsVTMtaXdHSVVxcXlPbUNXOVVBQnd5MTM4VF9FTnhuaUJTLXRuMFBNMnVzTFB5bWxHTnVPenM4aDIxZm5FLVJIUFp1MVZqbTVlR2tRLTc3elp5bTVCUm1ybEtva2VBRnliNUhmTVhVWi15clNuV3lHMDJ5SGl2WDR1X2JxWWVzdGZtYzJpSVZHYm9qMnlSamphdlBHNWpicTI5eUc3UVFwT1VxUnF5azZESENJd09QV3dJLVlzSmJOOWVzM3l3RGJuQQ?oc=5)\n\n## Dopolnitev vira 3: Demokracija\n\n(AKTUALNO) Varuhinja človekovih pravic Simona Drenik Bavdek: Pravica do dostojnega pokopa temeljna človekova pravica Demokracija\n\n Vir: Demokracija. Objavljeno: Sat, 16 May 2026 07:00:00 GMT. [Odpri izvirni vir](https://news.google.com/rss/articles/CBMi4AFBVV95cUxPT0h6RW5mbWxIa2Q1QlBERy1lNmlfZzFhbWR2UFdyd1RCUl9KUzdWT2xIS3ZQMEtHX1c1ZEVkcjNqUGNJQlBNOGFnendXX0J4Q1dyeEcyM0QtZVVQbFdNZUhwQTdpN19UdG05UzhndGo4bEJwQlZ3SXFqR2tlcXBiWGF4LWR6bkhIU3o3cUNTTlFWR25jS0l3b0gtMUdSSVdnVU9Cd05SbVBNUFBZMlpVNk1wOWoteEVheEZxUVlNNkRPUXJQQkJ6VXVod3BaWGlkeTlCZm1hSjc5andBZk1PZg?oc=5)\n\n## Dopolnitev vira 4: Demokracija\n\n(AKTUALNO) Hudo bolni slovenski otroci ostajajo brez dostopa do zdravila, odobrenega s strani evropske agencije EMA Demokracija\n\n Vir: Demokracija. Objavljeno: Fri, 18 Sep 2026 03:16:14 GMT. [Odpri izvirni vir](https://news.google.com/rss/articles/CBMi2gFBVV95cUxPYWxLZXNLUVFwWkNrd09YU1J6TFNMdUEwazAxRUNkeVltMHlTdGxTNVJLbWtnNVhsXzNGWmdrR3N5MHpxeGY5eG9WcWFvZDcxdUNlTGpFcUdhN3RPcVFsSFNtOXFzZjNkcWlSRHVzYXg1UkZLSC1ILWFndUtPcFJ3cVNXbXlfSWt6UDZtRXhONm01d0NwdmhNeVdPWnFScW50QUpWTEVJbU1HbkFUb2F1UG45TUI2MlpsaEIyalhwa2tyS185bTJWU1VkZHUtTkNXRUIxSHBTSDJidw?oc=5)\n\n## Dopolnitev vira 5: Nova24TV\n\n[Video] Afera vseh afer: Švarc Pipanova v prisluhih o nedotakljivem Jankoviću in Golobu, ki še vedno vodi Gen-I Nova24TV\n\n Vir: Nova24TV. Objavljeno: Wed, 11 Mar 2026 07:00:00 GMT. [Odpri izvirni vir](https://news.google.com/rss/articles/CBMiwwFBVV95cUxNQVgtV3ZQVzdBS0NLOFBtWkNtQjQ0YWJvRkhfdlgybnhxNjJTckJlaS1hbG5jWEswVTN1eHNzcEl5VWR2REs3WTdCYUpFSmJYRDc2czdkUnMyRkdWTTQzY1B3cjl3Tl9NX1NWVV9xSmJIamlXc0JwSjlMczdnaDZIU1NHcEVneEtxZXk0SV9oMFBwdDh1UkN5UzB2V2JLbUtTYXVoTHBoSHRid3BoaEI4LTVodU1JZ0hkLTlkX1R0NFVHdmc?oc=5)\n\n## Kaj spremljati naprej\n\nZgodbe se lahko po prvi objavi še dopolnijo z novimi podatki, popravki ali odzivi. Za spremembe, ki še niso zajete v teh virih, je smiselno preveriti neposredne povezave in poznejše objave istih uredništev.",
    "category": "Aktualno",
    "author": "Blog Lab Publisher",
    "status": "published",
    "heroImage": null,
    "video": null,
    "gallery": [],
    "sources": [
      {
        "label": "Nova24TV — Anja Rakuša Brus: Pomemben argument za mojo kandidaturo je izkušnja z aktualno vlado, ki stroke ne posluša dovolj -…",
        "url": "https://news.google.com/rss/articles/CBMizAFBVV95cUxObkJrTGhvMXhVSkJUcExOWUg0cWlVYmM5R0J6eXdTZ1dmdGRVSHVTek9EM09mUy0xdGF1eEo5X196dy1McUlFUjJwRUpjeTJYNGt0OUxqaG4zOTZBTkhqc1RCZkgtOTZQV29qQmQ3QXU5REFCOWEydXlCT0hLWTdZUVRpR19razFPVy1SMndKaGZUNUVKcXFCM05feHNmN2dqcTdJT1h3ekw1RG5Gd2F3NzI0c2NObloyd2plV0MtX056U0JGTTY4QlZBQXk?oc=5"
      },
      {
        "label": "Demokracija — (AKTUALNO) V novi številki revije Demokracija preberite: Izključujejo in zavirajo razvoj! Janša: Osamosvojitvena…",
        "url": "https://news.google.com/rss/articles/CBMixgJBVV95cUxNZTY0M3ozT2IxZ2U2Y1YwSVhudWFEWjRUMWFoX2RHcjd3MnFHVDN4aVZQbUYyZmNGZmxhc1ZqSVlxOFJKbVBWS2VvUDNoOVlhbDBwS0ZVQUQzRGpsZWx3SGlYVkRBUGtTa2wwU3VzV2xxejR2ajNXbEJOWkZ3dEJpVXdMWTFsVTMtaXdHSVVxcXlPbUNXOVVBQnd5MTM4VF9FTnhuaUJTLXRuMFBNMnVzTFB5bWxHTnVPenM4aDIxZm5FLVJIUFp1MVZqbTVlR2tRLTc3elp5bTVCUm1ybEtva2VBRnliNUhmTVhVWi15clNuV3lHMDJ5SGl2WDR1X2JxWWVzdGZtYzJpSVZHYm9qMnlSamphdlBHNWpicTI5eUc3UVFwT1VxUnF5azZESENJd09QV3dJLVlzSmJOOWVzM3l3RGJuQQ?oc=5"
      },
      {
        "label": "Demokracija — (AKTUALNO) Varuhinja človekovih pravic Simona Drenik Bavdek: Pravica do dostojnega pokopa temeljna človekova pravica -…",
        "url": "https://news.google.com/rss/articles/CBMi4AFBVV95cUxPT0h6RW5mbWxIa2Q1QlBERy1lNmlfZzFhbWR2UFdyd1RCUl9KUzdWT2xIS3ZQMEtHX1c1ZEVkcjNqUGNJQlBNOGFnendXX0J4Q1dyeEcyM0QtZVVQbFdNZUhwQTdpN19UdG05UzhndGo4bEJwQlZ3SXFqR2tlcXBiWGF4LWR6bkhIU3o3cUNTTlFWR25jS0l3b0gtMUdSSVdnVU9Cd05SbVBNUFBZMlpVNk1wOWoteEVheEZxUVlNNkRPUXJQQkJ6VXVod3BaWGlkeTlCZm1hSjc5andBZk1PZg?oc=5"
      },
      {
        "label": "Demokracija — (AKTUALNO) Hudo bolni slovenski otroci ostajajo brez dostopa do zdravila, odobrenega s strani evropske agencije EMA -…",
        "url": "https://news.google.com/rss/articles/CBMi2gFBVV95cUxPYWxLZXNLUVFwWkNrd09YU1J6TFNMdUEwazAxRUNkeVltMHlTdGxTNVJLbWtnNVhsXzNGWmdrR3N5MHpxeGY5eG9WcWFvZDcxdUNlTGpFcUdhN3RPcVFsSFNtOXFzZjNkcWlSRHVzYXg1UkZLSC1ILWFndUtPcFJ3cVNXbXlfSWt6UDZtRXhONm01d0NwdmhNeVdPWnFScW50QUpWTEVJbU1HbkFUb2F1UG45TUI2MlpsaEIyalhwa2tyS185bTJWU1VkZHUtTkNXRUIxSHBTSDJidw?oc=5"
      },
      {
        "label": "Nova24TV — [Video] Afera vseh afer: Švarc Pipanova v prisluhih o nedotakljivem Jankoviću in Golobu, ki še vedno vodi Gen-I -…",
        "url": "https://news.google.com/rss/articles/CBMiwwFBVV95cUxNQVgtV3ZQVzdBS0NLOFBtWkNtQjQ0YWJvRkhfdlgybnhxNjJTckJlaS1hbG5jWEswVTN1eHNzcEl5VWR2REs3WTdCYUpFSmJYRDc2czdkUnMyRkdWTTQzY1B3cjl3Tl9NX1NWVV9xSmJIamlXc0JwSjlMczdnaDZIU1NHcEVneEtxZXk0SV9oMFBwdDh1UkN5UzB2V2JLbUtTYXVoTHBoSHRid3BoaEI4LTVodU1JZ0hkLTlkX1R0NFVHdmc?oc=5"
      }
    ],
    "createdAt": "2026-09-20T21:00:40+02:00",
    "updatedAt": "2026-09-20T21:00:40+02:00"
  },

  {
    "id": "politika-si-odpira-vrata-v-medije-vlada-kriticne-medije-s-profesionalnimi-novinarji-dojema-eeca644f",
    "title": "Politika si odpira vrata v medije: \"Vlada kritične medije s profesionalnimi novinarji dojema kot sovražnike…",
    "excerpt": "Politika: pregled preverljivih informacij iz današnjih virov, z osrednjo zgodbo »Politika si odpira vrata v medije: \"Vlada kritične medije s profesionalnimi novinarji dojema kot sovražnike…«.",
    "seoDescription": "Politika: pregled preverljivih informacij iz današnjih virov, z osrednjo zgodbo »Politika si odpira vrata v medije: \"Vlada kritične medije s profesionalnimi n",
    "content": "**Politika, 20. 9. 2026.** Politika si odpira vrata v medije: \"Vlada kritične medije s profesionalnimi novinarji dojema kot sovražnike oblasti\" Večer\n\nSpodaj so zbrane le informacije, ki jih je mogoče neposredno povezati z objavljenimi viri. Kjer vir ne ponuja dovolj podrobnosti, besedilo ne zapolnjuje vrzeli z ugibanjem.\n\nPri političnih temah Blog Lab ne podpira kandidatov, strank ali političnih odločitev; izjave in ocene so predstavljene kot stališča njihovih avtorjev ali virov, ne kot uredniška presoja.\n\nVir: Večer. Objavljeno: Thu, 27 Aug 2026 07:00:00 GMT. [Odpri izvirni vir](https://news.google.com/rss/articles/CBMi5AFBVV95cUxQQXpscDRpWVZUM3huT1ViaGczb3kxNjNyVlhuYkxGbUYwMkgxMzRWTVlqYVg3ejF2ZElpUVZwQVM0QnUzSWFRLW14a0ZYUUZZSkFFTkFxRnVTX0FDU1V3cWtaU2Y1ZDJhMHNmMWxnWWw0aFF4ZG1BeGZJLWJ0NWRqU2dPV0s4dkkxR3lEUHQ2azE2eV9hUDkzSzZCdkptR1dzTElWN1ZxbTN6WTIxNDY5c2ZSN3lQMXJxQm5jQjhmcTJzWWQ5N19QYWFPcE1idy1wb2FWQTlCSHAxeEN1QTRuMk1qelg?oc=5)\n\n## Dopolnitev vira 2: rtvslo.si\n\nIzhodišče vira: Vlada da pečat zunanji politiki, a težnja k mednarodnemu pravu in človekovim pravicam naj ostane. - rtvslo.si.\n\nVlada da pečat zunanji politiki, a težnja k mednarodnemu pravu in človekovim pravicam naj ostane. rtvslo.si\n\n Vir: rtvslo.si. Objavljeno: Wed, 09 Sep 2026 10:03:07 GMT. [Odpri izvirni vir](https://news.google.com/rss/articles/CBMi2wFBVV95cUxQY3JQWHJGQjlaYWlIajVNWnJWbE9iS01Ydk9FMXRrWmUtX3pxdUZjWTNkRW5SSEc2bnI3SEJQVlk4cF9ZWk9oUm5aY1JTazZUOHllOHhtNVFnRVgxbWUtZHBQQnp4RmJHd1JWNHY2b3VJZ2xDXzhER2JvcHNZZ2dfSjZnaG91b0h1UWJLbFJIS3hfUWE3RFpQTkJKZzdmSjZSbmhpaUhVNzFoU3l6UHN2QjZtU3BJWTc5SnJvQ2pMZ3lDYUMxaUxyV083Uy1nRlNFWHlmRmpTYzh2ekU?oc=5)\n\n## Dopolnitev vira 3: Slovenske novice\n\nIzhodišče vira: Janša: Zunanjo politiko vodi vlada, v ozadju spor: kdo določa smer te politike? (VIDEO) - Slovenske novice.\n\nJanša: Zunanjo politiko vodi vlada, v ozadju spor: kdo določa smer te politike? (VIDEO) Slovenske novice\n\n Vir: Slovenske novice. Objavljeno: Thu, 27 Aug 2026 07:00:00 GMT. [Odpri izvirni vir](https://news.google.com/rss/articles/CBMi7AFBVV95cUxPYVRmbnVGUnhNc2cwdk1Rc1J1UFZYYUhMQk51TWR5ZXYxVTR3RXY4V1dxd0NTdEdLTnp0Nkp2Z3dDMUNiRWNhRWVrQThQTnFiR2hJcEhjb0VXOUllaHR1alFQT2N0RGZiRzc1dnZGUGRQUko1NkhJX2xyak1sOW9BSjF2QlFIa2tLTTFRNEl6aDVUYXVwVmE2Y2VveGRuV19GMUpuM1ZKSW00ZjhMd2gxdDdUMkF1ZkJOeEQ0NHdEYl9wbzhwcE9hMGMwck9JZGtiT1Bna3hYMDNZa1BicXNSTDNDRExEdENyREw2cg?oc=5)\n\n## Dopolnitev vira 4: rtvslo.si\n\nIzhodišče vira: Kajzer: Zunanja politika se osredotoča na okvire, v katerih ima Slovenija možnosti vplivanja - rtvslo.si.\n\nKajzer: Zunanja politika se osredotoča na okvire, v katerih ima Slovenija možnosti vplivanja rtvslo.si\n\n Vir: rtvslo.si. Objavljeno: Tue, 01 Sep 2026 18:15:47 GMT. [Odpri izvirni vir](https://news.google.com/rss/articles/CBMiyAFBVV95cUxPZHdORGVzV0tCcTM4ZlNVWXFHS2s5QjRXODJNM3Z5aUVlYXVZdmxZRXRsaW1OUkoxYUpHckhVLUJNV2Q0bGlfLWFkZUZHeTF3bW55RkhHTEpfSFg0QWRwYUpNMEIyZXFmQ2dqRkNsYm96Qjk0MEljbmJ4aUNRaUgzOGlveGMwY2plT0ZZR3Nfc0Zta0hkLUlZaWJVMnRpRkd0UTRBcHZfTW45MUU5Y0sybXM3ZkxvVnZ6OEtBclI1RGkybmJWZ0ZzWg?oc=5)\n\n## Dopolnitev vira 5: N1 Slovenija\n\nIzhodišče vira: Z univerz opozorila, da se politiki sistematično izogibajo in ignorirajo novinarje RTVS - N1 Slovenija.\n\nZ univerz opozorila, da se politiki sistematično izogibajo in ignorirajo novinarje RTVS N1 Slovenija\n\n Vir: N1 Slovenija. Objavljeno: Mon, 14 Sep 2026 13:48:47 GMT. [Odpri izvirni vir](https://news.google.com/rss/articles/CBMiUEFVX3lxTFB4bXlURjB4SWhSRWI0Y003WVhLZHJDWUJNb2NIQ21IT1RTcmt1YklLenZpemlWOEVhRHB5MkJnTTNDUUxQUzJHQ1BnTlBRY2ZV?oc=5)\n\n## Kaj spremljati naprej\n\nZgodbe se lahko po prvi objavi še dopolnijo z novimi podatki, popravki ali odzivi. Za spremembe, ki še niso zajete v teh virih, je smiselno preveriti neposredne povezave in poznejše objave istih uredništev.",
    "category": "Politika",
    "author": "Blog Lab Publisher",
    "status": "published",
    "heroImage": null,
    "video": null,
    "gallery": [],
    "sources": [
      {
        "label": "Večer — Politika si odpira vrata v medije: \"Vlada kritične medije s profesionalnimi novinarji dojema kot sovražnike oblasti\" -…",
        "url": "https://news.google.com/rss/articles/CBMi5AFBVV95cUxQQXpscDRpWVZUM3huT1ViaGczb3kxNjNyVlhuYkxGbUYwMkgxMzRWTVlqYVg3ejF2ZElpUVZwQVM0QnUzSWFRLW14a0ZYUUZZSkFFTkFxRnVTX0FDU1V3cWtaU2Y1ZDJhMHNmMWxnWWw0aFF4ZG1BeGZJLWJ0NWRqU2dPV0s4dkkxR3lEUHQ2azE2eV9hUDkzSzZCdkptR1dzTElWN1ZxbTN6WTIxNDY5c2ZSN3lQMXJxQm5jQjhmcTJzWWQ5N19QYWFPcE1idy1wb2FWQTlCSHAxeEN1QTRuMk1qelg?oc=5"
      },
      {
        "label": "rtvslo.si — Vlada da pečat zunanji politiki, a težnja k mednarodnemu pravu in človekovim pravicam naj ostane. - rtvslo.si",
        "url": "https://news.google.com/rss/articles/CBMi2wFBVV95cUxQY3JQWHJGQjlaYWlIajVNWnJWbE9iS01Ydk9FMXRrWmUtX3pxdUZjWTNkRW5SSEc2bnI3SEJQVlk4cF9ZWk9oUm5aY1JTazZUOHllOHhtNVFnRVgxbWUtZHBQQnp4RmJHd1JWNHY2b3VJZ2xDXzhER2JvcHNZZ2dfSjZnaG91b0h1UWJLbFJIS3hfUWE3RFpQTkJKZzdmSjZSbmhpaUhVNzFoU3l6UHN2QjZtU3BJWTc5SnJvQ2pMZ3lDYUMxaUxyV083Uy1nRlNFWHlmRmpTYzh2ekU?oc=5"
      },
      {
        "label": "Slovenske novice — Janša: Zunanjo politiko vodi vlada, v ozadju spor: kdo določa smer te politike? (VIDEO) - Slovenske novice",
        "url": "https://news.google.com/rss/articles/CBMi7AFBVV95cUxPYVRmbnVGUnhNc2cwdk1Rc1J1UFZYYUhMQk51TWR5ZXYxVTR3RXY4V1dxd0NTdEdLTnp0Nkp2Z3dDMUNiRWNhRWVrQThQTnFiR2hJcEhjb0VXOUllaHR1alFQT2N0RGZiRzc1dnZGUGRQUko1NkhJX2xyak1sOW9BSjF2QlFIa2tLTTFRNEl6aDVUYXVwVmE2Y2VveGRuV19GMUpuM1ZKSW00ZjhMd2gxdDdUMkF1ZkJOeEQ0NHdEYl9wbzhwcE9hMGMwck9JZGtiT1Bna3hYMDNZa1BicXNSTDNDRExEdENyREw2cg?oc=5"
      },
      {
        "label": "rtvslo.si — Kajzer: Zunanja politika se osredotoča na okvire, v katerih ima Slovenija možnosti vplivanja - rtvslo.si",
        "url": "https://news.google.com/rss/articles/CBMiyAFBVV95cUxPZHdORGVzV0tCcTM4ZlNVWXFHS2s5QjRXODJNM3Z5aUVlYXVZdmxZRXRsaW1OUkoxYUpHckhVLUJNV2Q0bGlfLWFkZUZHeTF3bW55RkhHTEpfSFg0QWRwYUpNMEIyZXFmQ2dqRkNsYm96Qjk0MEljbmJ4aUNRaUgzOGlveGMwY2plT0ZZR3Nfc0Zta0hkLUlZaWJVMnRpRkd0UTRBcHZfTW45MUU5Y0sybXM3ZkxvVnZ6OEtBclI1RGkybmJWZ0ZzWg?oc=5"
      },
      {
        "label": "N1 Slovenija — Z univerz opozorila, da se politiki sistematično izogibajo in ignorirajo novinarje RTVS - N1 Slovenija",
        "url": "https://news.google.com/rss/articles/CBMiUEFVX3lxTFB4bXlURjB4SWhSRWI0Y003WVhLZHJDWUJNb2NIQ21IT1RTcmt1YklLenZpemlWOEVhRHB5MkJnTTNDUUxQUzJHQ1BnTlBRY2ZV?oc=5"
      }
    ],
    "createdAt": "2026-09-20T16:59:34+02:00",
    "updatedAt": "2026-09-20T16:59:34+02:00"
  },

  {
    "id": "23-septembra-od-leta-2000-praznujemo-dan-slovenskega-sporta-becf2d35",
    "title": "23. septembra od leta 2000 praznujemo Dan slovenskega športa",
    "excerpt": "Šport: pregled preverljivih informacij iz današnjih virov, z osrednjo zgodbo »23. septembra od leta 2000 praznujemo Dan slovenskega športa«.",
    "seoDescription": "Šport: pregled preverljivih informacij iz današnjih virov, z osrednjo zgodbo »23. septembra od leta 2000 praznujemo Dan slovenskega športa«.",
    "content": "**Šport, 20. 9. 2026.** 23. septembra od leta 2000 praznujemo Dan slovenskega športa Olimpijski Komite Slovenije\n\nSpodaj so zbrane le informacije, ki jih je mogoče neposredno povezati z objavljenimi viri. Kjer vir ne ponuja dovolj podrobnosti, besedilo ne zapolnjuje vrzeli z ugibanjem.\n\nVir: Olimpijski Komite Slovenije. Objavljeno: Sun, 20 Sep 2026 12:29:11 GMT. [Odpri izvirni vir](https://news.google.com/rss/articles/CBMiywFBVV95cUxQNFRyRWxCOGpZbFRhTFkwandHeXBFRXlDSVRFeE1NUEk3Y0ljSmU5RzJmbVFaRzRDVkVPdnhITlk0V3dmWkxyZGRxRXRLT0h4dGJaWWUxLVpGXy1tWmYxY1YxMkNoNkxEZGk3M0hWd1RYN3NTaVpDOUx5MzhWNDVFSWE4bXR6QzVuenFEdTR1eldvazk3RmlCVUwzblBRWGpKckc5YWlIN0FsSWlPWnlrVnNPc2dpalA5S0N0VnVkdkZaQU9BTVlHbDdMOA?oc=5)\n\n## Dopolnitev vira 2: Delo.si\n\nIzhodišče vira: Poleg Slovenije se za evropsko prvenstvo zanima veliko držav - Delo.si.\n\nPoleg Slovenije se za evropsko prvenstvo zanima veliko držav Delo.si\n\n Vir: Delo.si. Objavljeno: Fri, 18 Sep 2026 07:46:01 GMT. [Odpri izvirni vir](https://news.google.com/rss/articles/CBMimgFBVV95cUxONm5TMzN0ekY3bUZoWTI5eTVGemNQek5TNURPaGtTQVp4WWk1QlZNemVPWC1nZG1hbHotMEZTdlZ5elRqT3R1S2RZWGhKb1E5VGpwUGcwTFBha196TDJwdERyZGJnakxSdVBDUkZ1WjhYQ3NNbVhZa0xDX3JkY3N0S1RHNzRWejdSYWJHdW4tMzdrR1NWaUhJWnl3?oc=5)\n\n## Dopolnitev vira 3: Delo.si\n\nIzhodišče vira: Luka Dončić zapustil Slovenijo, sprejel bo velikanski izziv - Delo.si.\n\nLuka Dončić zapustil Slovenijo, sprejel bo velikanski izziv Delo.si\n\n Vir: Delo.si. Objavljeno: Sun, 20 Sep 2026 07:20:00 GMT. [Odpri izvirni vir](https://news.google.com/rss/articles/CBMikAFBVV95cUxPZkh4WEdOemZkNFJVSVR3d1lobFAyeFJyZUd5bldXbmNmb3hNbzdRaHk0YUtPbUVfVXVtdUp2a25lT043d0NXaC1MQ3dKMEgyeVpDTUwwMy1BNXlGMEVEY3pEdlYxWWhSNkIzUmU2SkkxdDVwTmVlMHIwc3pPQ3F6OWNYbHZkVmw1QWk4YlVRTGg?oc=5)\n\n## Dopolnitev vira 4: Šport TV\n\nIzhodišče vira: Znova diši po slovenskem začetku dirke po Franciji - Šport TV.\n\nZnova diši po slovenskem začetku dirke po Franciji Šport TV\n\n Vir: Šport TV. Objavljeno: Thu, 17 Sep 2026 17:26:30 GMT. [Odpri izvirni vir](https://news.google.com/rss/articles/CBMigAFBVV95cUxPYm9NMmdKZGMtbjZRMkNNNkJBZjB5LXh5bGMwaUxlZUdQTWdpeEw5U1RBSWJ0SEs0b1BjTmF4VjQwQVhIaXQ3dlhndUh4V1RIdG5VV2RCVHN5LWJmeV9VeUphZG9jNXFybWxXc29pYU1DbjdfTVVZeklqWWRhMG9wbg?oc=5)\n\n## Kaj spremljati naprej\n\nZgodbe se lahko po prvi objavi še dopolnijo z novimi podatki, popravki ali odzivi. Za spremembe, ki še niso zajete v teh virih, je smiselno preveriti neposredne povezave in poznejše objave istih uredništev.",
    "category": "Šport",
    "author": "Blog Lab Publisher",
    "status": "published",
    "heroImage": null,
    "video": null,
    "gallery": [],
    "sources": [
      {
        "label": "Olimpijski Komite Slovenije — 23. septembra od leta 2000 praznujemo Dan slovenskega športa - Olimpijski Komite Slovenije",
        "url": "https://news.google.com/rss/articles/CBMiywFBVV95cUxQNFRyRWxCOGpZbFRhTFkwandHeXBFRXlDSVRFeE1NUEk3Y0ljSmU5RzJmbVFaRzRDVkVPdnhITlk0V3dmWkxyZGRxRXRLT0h4dGJaWWUxLVpGXy1tWmYxY1YxMkNoNkxEZGk3M0hWd1RYN3NTaVpDOUx5MzhWNDVFSWE4bXR6QzVuenFEdTR1eldvazk3RmlCVUwzblBRWGpKckc5YWlIN0FsSWlPWnlrVnNPc2dpalA5S0N0VnVkdkZaQU9BTVlHbDdMOA?oc=5"
      },
      {
        "label": "Delo.si — Poleg Slovenije se za evropsko prvenstvo zanima veliko držav - Delo.si",
        "url": "https://news.google.com/rss/articles/CBMimgFBVV95cUxONm5TMzN0ekY3bUZoWTI5eTVGemNQek5TNURPaGtTQVp4WWk1QlZNemVPWC1nZG1hbHotMEZTdlZ5elRqT3R1S2RZWGhKb1E5VGpwUGcwTFBha196TDJwdERyZGJnakxSdVBDUkZ1WjhYQ3NNbVhZa0xDX3JkY3N0S1RHNzRWejdSYWJHdW4tMzdrR1NWaUhJWnl3?oc=5"
      },
      {
        "label": "Delo.si — Luka Dončić zapustil Slovenijo, sprejel bo velikanski izziv - Delo.si",
        "url": "https://news.google.com/rss/articles/CBMikAFBVV95cUxPZkh4WEdOemZkNFJVSVR3d1lobFAyeFJyZUd5bldXbmNmb3hNbzdRaHk0YUtPbUVfVXVtdUp2a25lT043d0NXaC1MQ3dKMEgyeVpDTUwwMy1BNXlGMEVEY3pEdlYxWWhSNkIzUmU2SkkxdDVwTmVlMHIwc3pPQ3F6OWNYbHZkVmw1QWk4YlVRTGg?oc=5"
      },
      {
        "label": "Šport TV — Znova diši po slovenskem začetku dirke po Franciji - Šport TV",
        "url": "https://news.google.com/rss/articles/CBMigAFBVV95cUxPYm9NMmdKZGMtbjZRMkNNNkJBZjB5LXh5bGMwaUxlZUdQTWdpeEw5U1RBSWJ0SEs0b1BjTmF4VjQwQVhIaXQ3dlhndUh4V1RIdG5VV2RCVHN5LWJmeV9VeUphZG9jNXFybWxXc29pYU1DbjdfTVVZeklqWWRhMG9wbg?oc=5"
      }
    ],
    "createdAt": "2026-09-20T16:57:18+02:00",
    "updatedAt": "2026-09-20T16:57:18+02:00"
  },

  {
    "id": "odbojka-m-italija-slovenija-evropsko-prvenstvo-2026-skupina-a-508b7209",
    "title": "Odbojka (M): Italija - Slovenija, Evropsko prvenstvo 2026, Skupina A",
    "excerpt": "Šport: pregled preverljivih informacij iz današnjih virov, z osrednjo zgodbo »Odbojka (M): Italija - Slovenija, Evropsko prvenstvo 2026, Skupina A«.",
    "seoDescription": "Šport: pregled preverljivih informacij iz današnjih virov, z osrednjo zgodbo »Odbojka (M): Italija - Slovenija, Evropsko prvenstvo 2026, Skupina A«.",
    "content": "**Šport, 20. 9. 2026.** Odbojka (M): Italija - Slovenija, Evropsko prvenstvo 2026, Skupina A Siol.net\n\nSpodaj so zbrane le informacije, ki jih je mogoče neposredno povezati z objavljenimi viri. Kjer vir ne ponuja dovolj podrobnosti, besedilo ne zapolnjuje vrzeli z ugibanjem.\n\nVir: Siol.net. Objavljeno: Sun, 20 Sep 2026 01:48:09 GMT. [Odpri izvirni vir](https://news.google.com/rss/articles/CBMi1wFBVV95cUxNdDlTU0hlTksyeFlzRHZVMWtGc0pOQmVVdEVxWnI0OGxkU25vUXJEbkJ6Z3hjS0RNNzNpMk5naWhheTROMnhCenMwOTd1X0J0QzlFM0dsOXhFeVJGbTFZMGtUc25QQVBDbjkzOTc3LWdoM1RLMzczU2M5OExyX0xPeFU1czM3MjYtZjlEcWtTaHZ5TlN6X0hFdmw5Y0NmVU9uR2V4TDBxUWVYWnl2NjhBdVZsU3FTb2s4VmVVQzI3ZnhsQlJjQTZoVHg1d3E5ZElxYjgxV280cw?oc=5)\n\n## Dopolnitev vira 2: Šport TV\n\nIzhodišče vira: Slovenija po 24 letih znova v finalu evropskega prvenstva U18, za zlato na Šport TV proti Italiji! - Šport TV.\n\nSlovenija po 24 letih znova v finalu evropskega prvenstva U18, za zlato na Šport TV proti Italiji! Šport TV\n\n Vir: Šport TV. Objavljeno: Sun, 02 Aug 2026 07:00:00 GMT. [Odpri izvirni vir](https://news.google.com/rss/articles/CBMivgFBVV95cUxPeHhldDVwLWdCYUhzOXhiQ0l5Zml6Qml0UG42R3pFSTFzX1BFV1NNOS1mLVdUNWJRMFdTMjZfbk9wODgwdG9Oa3k1azZSTHBHZzNhZEJPdUZLd1hrZDVpNDJPcWRQdFBCcVFzVjJHNkNKMWRwMXF0anNGZXU1RmZxbVBfaXlSa3ltLXFxUUlTOXBGbjUwR3R4NXJzMFdyYTQtdDg1bkdzbVBOdWV0R09NdlhNb0lZb1NVNmt2bHhR?oc=5)\n\n## Dopolnitev vira 3: Šport TV\n\nIzhodišče vira: Slovenski odbojkarji so preizkusili dvorano v Torinu, kjer jih bo pričakala Srbija - Šport TV.\n\nSlovenski odbojkarji so preizkusili dvorano v Torinu, kjer jih bo pričakala Srbija Šport TV\n\n Vir: Šport TV. Objavljeno: Sun, 20 Sep 2026 10:38:31 GMT. [Odpri izvirni vir](https://news.google.com/rss/articles/CBMiqgFBVV95cUxOME9hbTR6eFZsaUNsckdFTktpUU1Dd0FzV1RLanQtZ2IzbjAzUG9BU3J6a3VndzdTcHpGY0RmTzN4SkF0N3BMakw1Rl9XZjl1T19XS3lmUGFZZ1RNaWZWM2FLT21vbVFGcUxXLUhjLXlqOEZXN1JWNVdnSThSdl91T3JSTjZBdWozQUFtQ3oyb1lSWWZsVzhtOGhmZTcxZ3ZHU2V5VGx3TnNUUQ?oc=5)\n\n## Dopolnitev vira 4: Žurnal24\n\nIzhodišče vira: Mlada Slovenka na evropskem prestolu: \"Pred prvo me je vedno strah, nato pa …\" - Žurnal24.\n\nMlada Slovenka na evropskem prestolu: \"Pred prvo me je vedno strah, nato pa …\" Žurnal24\n\n Vir: Žurnal24. Objavljeno: Sun, 20 Sep 2026 04:48:00 GMT. [Odpri izvirni vir](https://news.google.com/rss/articles/CBMiwgFBVV95cUxPX2haSWR2alJrQ3U5QnpJckplX0QwZWMtaVBON2xWNjRlSDZQN01PWDhkRU0wMDJUdjh0d3ZIZ1hDX05CR2pVVGc3ejAySGplUzhXbFZSZ1JhdFZOVHVHNG9KT2xySGh3cmgtR1ZJdjJmUkxaTWFaSjF0MVhIVjFqdjZPMC1QTXgwT0xSU3hudHRUQ0FxbDMzM2VQUDdGbmZaaEJGRnpYcVZ3bDdNVE14TzFOc3RoMlZ2UHBpSFlsOWMwd9IBxwFBVV95cUxPYS1YeXpueG1TbVhxUDNQcXB2YzIzZHM3eTNZeW16aTJMVWx0OHRZOHZsejBneEdDVVhUeWYzREhpWmxtLW52eVVTSlNWX293V2hqZTBXYUlNOU8yUWNBbWRvREZxT0pUaC1fbUN5dVNudXZCYnpIUnAwNkVjMmVLMFNlaF9QYjlydloyV1NLcjdJXzhETDlGcUVxbjhBMkJ6enFXTmR3ZUdGZWVqS01HNGlCcWhVcUM1SmY5MkY3OThxYXlOdWo0?oc=5)\n\n## Dopolnitev vira 5: rtvslo.si\n\nIzhodišče vira: Slovenija je dobro začela izločilne boje na evropskem prvenstvu v odbojki - rtvslo.si.\n\nSlovenija je dobro začela izločilne boje na evropskem prvenstvu v odbojki rtvslo.si\n\n Vir: rtvslo.si. Objavljeno: Fri, 18 Sep 2026 06:49:00 GMT. [Odpri izvirni vir](https://news.google.com/rss/articles/CBMiugFBVV95cUxPT2tLd0VQaThZaXJrVnh2SU1Rd3NHc2JJQUl4N3Q2V0w0bFduQks4M0JORjVTR2JDOGdTamJMSmI0UjlDNld6ZFdaTFMzX3dNakpteF9TbW80U1RBbWVGVHpDRk5qR0F5OXgzRnZVLW4xRWJtd3dnY0dPUzdjZzg0XzgyNGtQaUtROURvV1g5eERMXzh0YlloelBrTF8tRW1iMUd3THhWeXZEMEJvMHFQdDNJRU9mOGh3ZVE?oc=5)\n\n## Kaj spremljati naprej\n\nZgodbe se lahko po prvi objavi še dopolnijo z novimi podatki, popravki ali odzivi. Za spremembe, ki še niso zajete v teh virih, je smiselno preveriti neposredne povezave in poznejše objave istih uredništev.",
    "category": "Šport",
    "author": "Blog Lab Publisher",
    "status": "published",
    "heroImage": null,
    "video": null,
    "gallery": [],
    "sources": [
      {
        "label": "Siol.net — Odbojka (M): Italija - Slovenija, Evropsko prvenstvo 2026, Skupina A - Siol.net",
        "url": "https://news.google.com/rss/articles/CBMi1wFBVV95cUxNdDlTU0hlTksyeFlzRHZVMWtGc0pOQmVVdEVxWnI0OGxkU25vUXJEbkJ6Z3hjS0RNNzNpMk5naWhheTROMnhCenMwOTd1X0J0QzlFM0dsOXhFeVJGbTFZMGtUc25QQVBDbjkzOTc3LWdoM1RLMzczU2M5OExyX0xPeFU1czM3MjYtZjlEcWtTaHZ5TlN6X0hFdmw5Y0NmVU9uR2V4TDBxUWVYWnl2NjhBdVZsU3FTb2s4VmVVQzI3ZnhsQlJjQTZoVHg1d3E5ZElxYjgxV280cw?oc=5"
      },
      {
        "label": "Šport TV — Slovenija po 24 letih znova v finalu evropskega prvenstva U18, za zlato na Šport TV proti Italiji! - Šport TV",
        "url": "https://news.google.com/rss/articles/CBMivgFBVV95cUxPeHhldDVwLWdCYUhzOXhiQ0l5Zml6Qml0UG42R3pFSTFzX1BFV1NNOS1mLVdUNWJRMFdTMjZfbk9wODgwdG9Oa3k1azZSTHBHZzNhZEJPdUZLd1hrZDVpNDJPcWRQdFBCcVFzVjJHNkNKMWRwMXF0anNGZXU1RmZxbVBfaXlSa3ltLXFxUUlTOXBGbjUwR3R4NXJzMFdyYTQtdDg1bkdzbVBOdWV0R09NdlhNb0lZb1NVNmt2bHhR?oc=5"
      },
      {
        "label": "Šport TV — Slovenski odbojkarji so preizkusili dvorano v Torinu, kjer jih bo pričakala Srbija - Šport TV",
        "url": "https://news.google.com/rss/articles/CBMiqgFBVV95cUxOME9hbTR6eFZsaUNsckdFTktpUU1Dd0FzV1RLanQtZ2IzbjAzUG9BU3J6a3VndzdTcHpGY0RmTzN4SkF0N3BMakw1Rl9XZjl1T19XS3lmUGFZZ1RNaWZWM2FLT21vbVFGcUxXLUhjLXlqOEZXN1JWNVdnSThSdl91T3JSTjZBdWozQUFtQ3oyb1lSWWZsVzhtOGhmZTcxZ3ZHU2V5VGx3TnNUUQ?oc=5"
      },
      {
        "label": "Žurnal24 — Mlada Slovenka na evropskem prestolu: \"Pred prvo me je vedno strah, nato pa …\" - Žurnal24",
        "url": "https://news.google.com/rss/articles/CBMiwgFBVV95cUxPX2haSWR2alJrQ3U5QnpJckplX0QwZWMtaVBON2xWNjRlSDZQN01PWDhkRU0wMDJUdjh0d3ZIZ1hDX05CR2pVVGc3ejAySGplUzhXbFZSZ1JhdFZOVHVHNG9KT2xySGh3cmgtR1ZJdjJmUkxaTWFaSjF0MVhIVjFqdjZPMC1QTXgwT0xSU3hudHRUQ0FxbDMzM2VQUDdGbmZaaEJGRnpYcVZ3bDdNVE14TzFOc3RoMlZ2UHBpSFlsOWMwd9IBxwFBVV95cUxPYS1YeXpueG1TbVhxUDNQcXB2YzIzZHM3eTNZeW16aTJMVWx0OHRZOHZsejBneEdDVVhUeWYzREhpWmxtLW52eVVTSlNWX293V2hqZTBXYUlNOU8yUWNBbWRvREZxT0pUaC1fbUN5dVNudXZCYnpIUnAwNkVjMmVLMFNlaF9QYjlydloyV1NLcjdJXzhETDlGcUVxbjhBMkJ6enFXTmR3ZUdGZWVqS01HNGlCcWhVcUM1SmY5MkY3OThxYXlOdWo0?oc=5"
      },
      {
        "label": "rtvslo.si — Slovenija je dobro začela izločilne boje na evropskem prvenstvu v odbojki - rtvslo.si",
        "url": "https://news.google.com/rss/articles/CBMiugFBVV95cUxPT2tLd0VQaThZaXJrVnh2SU1Rd3NHc2JJQUl4N3Q2V0w0bFduQks4M0JORjVTR2JDOGdTamJMSmI0UjlDNld6ZFdaTFMzX3dNakpteF9TbW80U1RBbWVGVHpDRk5qR0F5OXgzRnZVLW4xRWJtd3dnY0dPUzdjZzg0XzgyNGtQaUtROURvV1g5eERMXzh0YlloelBrTF8tRW1iMUd3THhWeXZEMEJvMHFQdDNJRU9mOGh3ZVE?oc=5"
      }
    ],
    "createdAt": "2026-09-20T16:56:15+02:00",
    "updatedAt": "2026-09-20T16:56:15+02:00"
  },

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
    "updatedAt": "2026-09-20T09:10:00+02:00"
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
    excerpt: "Trajna testna objava za preverjanje, da javni Blog Lab, zasebni terminal i…45502 tokens truncated…rent guidance from the Alpine Association of Slovenia and use a qualified guide when appropriate. Rescue services are not a substitute for preparation.\n\n## When to go\n\nEarly autumn can bring clear views and quieter moments, but daylight is shortening and cold fronts can arrive quickly. Check the forecast and trail information on the morning of your visit. Start early enough to finish well before dark.\n\nOutside the main hiking season, some visitor facilities, mountain huts and transport services may operate reduced hours or close. Verify rather than assume. If high routes are unsuitable, stay in the valley and treat the change of plan as part of responsible Alpine travel.\n\n## Why the legend still matters\n\nZlatorog is sometimes used as a picturesque emblem, but the tale is not simply about a fabulous animal. The hunter sees the mountains as something to possess; the result is loss. Read in today’s tourism context, the lesson is strikingly current.\n\nThe real treasure is not hidden gold. It is the chance to encounter a living Alpine landscape without diminishing it for the next visitor—or for the species that live there year-round.\n\nGo to Trenta for the river, mountains and stories. Leave the flowers where they grow, keep the legend in the realm of imagination, and let Zlatorog remain undefeated.\n\n## Sources\n\n- Slovenian Tourist Board, “Explore the world of Slovenian myths and legends”: https://www.slovenia.info/en/stories/explore-the-world-of-slovenian-myths-and-legends\n- Triglav National Park, official visitor information: https://www.tnp.si/en/visit/\n- Soča Valley, official destination information: https://www.soca-valley.com/en/\n- Alpine Association of Slovenia, mountain information and safety resources: https://www.pzs.si/",
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
