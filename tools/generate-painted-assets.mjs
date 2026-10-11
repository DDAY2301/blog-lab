/* Original, deterministic painted BlogLab illustrations — no external stock. */
import {mkdirSync,writeFileSync} from "node:fs";
import {join} from "node:path";
const out=join(process.cwd(),"public","art","generated");mkdirSync(out,{recursive:true});
function rng(seed){let n=seed>>>0;return ()=>{n=(Math.imul(n,1664525)+1013904223)>>>0;return n/4294967296;};}
function scene(name,seed){
const rand=rng(seed), r=(a,b)=>a+(b-a)*rand(), pick=a=>a[Math.floor(rand()*a.length)],fix=v=>v.toFixed(1);
const e=(x,y,rx,ry,col,a,rot)=>'<ellipse cx="'+fix(x)+'" cy="'+fix(y)+'" rx="'+fix(rx)+'" ry="'+fix(ry)+'" fill="'+col+'" opacity="'+fix(a)+'" transform="rotate('+fix(rot)+' '+fix(x)+' '+fix(y)+')"/>';
const b=(x,y,w,h,col,a)=>'<path d="M'+fix(x)+' '+fix(y)+' Q'+fix(x+w*.45)+' '+fix(y+h*.7)+' '+fix(x+w)+' '+fix(y+h)+'" stroke="'+col+'" stroke-width="'+fix(r(2,12))+'" stroke-linecap="round" opacity="'+fix(a)+'" fill="none"/>';
const sky=["#a8b9b8","#b8b8a2","#d5c39e","#819aa1","#d6c7a3","#718f96","#e4cda4"],
mountain=["#516e79","#6b8081","#8e9180","#b5a98b","#d1bc95","#394d56"],
water=["#466b74","#63848a","#91a4a1","#345961","#b8b399","#d1b886","#e0c8a3"],
leaf=["#222f2c","#304338","#3b4a3b","#536048","#757951","#a18b54","#be985b","#c8a36d","#dbbc77"],
land=["#293c33","#405043","#61735c","#898264","#af976e","#d0b586","#ab874e"];
const x=[];
x.push('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900" preserveAspectRatio="xMidYMid slice">');
x.push('<title>'+name+' — izvirna slikarska ilustracija BlogLab</title>');
x.push('<defs><linearGradient id="sky" x2=".3" y2="1"><stop stop-color="#aabbb9"/><stop offset=".53" stop-color="#d6c6a1"/><stop offset="1" stop-color="#d6bc94"/></linearGradient><linearGradient id="lake" x2=".12" y2="1"><stop stop-color="#6f8c8c"/><stop offset=".56" stop-color="#426c74"/><stop offset="1" stop-color="#425c59"/></linearGradient><filter id="grain" x="-10%" y="-10%" width="120%" height="120%"><feTurbulence type="fractalNoise" baseFrequency=".15" numOctaves="3" seed="'+(seed%17+2)+'" stitchTiles="stitch"/><feColorMatrix type="saturate" values="0"/><feComponentTransfer><feFuncA type="linear" slope=".25"/></feComponentTransfer></filter></defs>');
x.push('<rect width="1600" height="900" fill="url(#sky)"/>');
for(let i=0;i<(name==="hero"?165:62);i++)x.push(b(r(0,1600),r(-50,370),r(22,160),r(-15,23),pick(sky),r(.10,.41)));
x.push('<path d="M0 384L118 304 254 354 413 220 574 309 733 137 868 230 1083 96 1202 189 1334 142 1480 220 1600 180V658H0Z" fill="#9da8a1"/>');
x.push('<path d="M0 445L148 360 307 405 490 239 630 330 758 224 874 274 1087 136 1240 215 1360 182 1525 280 1600 247V651H0Z" fill="#687f82"/>');
x.push('<path d="M438 279l52-40 67 90-67-42-24 17M720 275l38-49 78 76-62-26-23 13M1020 198l67-62 99 78-73-26-25 17M1315 217l45-35 80 71-64-29-25 11" fill="#e7d8b9" opacity=".89"/>');
x.push('<path d="M0 510Q240 453 470 478T910 458Q1223 420 1600 490V669H0Z" fill="#4a665f"/>');
for(let i=0;i<(name==="hero"?220:75);i++)x.push(b(r(0,1600),r(250,508),r(8,78),r(-13,18),pick(mountain),r(.19,.68)));
x.push('<path d="M0 523Q240 502 489 508T966 506Q1278 493 1600 514V900H0Z" fill="url(#lake)"/>');
for(let i=0;i<(name==="hero"?305:86);i++)x.push(b(r(-80,1580),r(530,910),r(12,190),r(-5,4),pick(water),r(.16,.63)));
x.push('<path d="M761 543Q903 444 1125 450Q1290 446 1600 490V598Q1360 560 1273 592Q1100 530 996 568Z" fill="#3d5745"/><path d="M845 531Q941 468 1078 481L1278 526L1150 557Z" fill="#5b6e4b"/>');
for(let i=0;i<(name==="hero"?145:53);i++)x.push(b(r(700,1580),r(433,589),r(9,55),r(-30,17),pick(leaf),r(.28,.82)));
x.push('<path d="M987 485L1020 437 1099 437 1127 486V555H985Z" fill="#e2c99b" stroke="#806d53" stroke-width="6"/><path d="M972 445L1057 402 1142 447L1131 467 1057 431 985 465Z" fill="#a16645"/><rect x="1035" y="469" width="27" height="85" fill="#83745b"/><rect x="1081" y="476" width="20" height="36" fill="#68746b"/><path d="M1055 407V336L1066 329 1080 336V407Z" fill="#e2d0aa" stroke="#796d54" stroke-width="5"/><path d="M1044 337L1067 287 1091 337Z" fill="#8c5840"/><path d="M1067 287v-23" stroke="#ddd3aa" stroke-width="6"/><path d="M1279 502l48-61 60 7 57 53v60h-165z" fill="#ceb48a"/><path d="M1258 470l89-56 113 74-26 11-87-57-75 52Z" fill="#925b42"/>');
x.push('<path d="M0 611Q256 514 421 619Q520 683 632 671Q791 713 915 709L1104 791 0 900Z" fill="#4a5c42"/><path d="M0 737Q212 642 343 701Q453 740 547 778Q696 824 797 821L950 900H0Z" fill="#847653"/><path d="M0 826Q183 756 330 807Q486 846 638 864L750 900H0Z" fill="#b49b71"/>');
for(let i=0;i<(name==="hero"?220:75);i++)x.push(b(r(-20,955),r(619,916),r(-30,88),r(-28,30),pick(land),r(.25,.82)));
x.push('<path d="M0 639C48 540 88 408 91 292C97 195 69 106 5 0H149C222 140 220 244 206 351C199 448 180 544 226 647L159 698Q128 544 111 523L79 666Z" fill="#594737" stroke="#725640" stroke-width="11"/><path d="M118 322C296 179 457 91 699 73L912 34 777 4C485 16 279 78 154 209Z" fill="#524737"/><path d="M117 234Q240 125 445 80M146 364Q279 191 624 94M124 527Q157 243 119 110" stroke="#a57d4b" stroke-width="29" opacity=".83" fill="none" stroke-linecap="round"/><path d="M127 421Q167 242 229 82M154 192Q322 99 581 53" stroke="#2b302a" stroke-width="11" fill="none" opacity=".8"/>');
for(let i=0;i<(name==="hero"?360:115);i++){let xx=r(-35,900),y=r(-68,260);if(xx>600&&y>160&&rand()>.4)continue;x.push(e(xx,y,r(14,70),r(7,31),pick(leaf),r(.32,.9),r(-54,42)));}
for(let i=0;i<(name==="hero"?225:65);i++)x.push(b(r(-20,900),r(-25,290),r(15,66),r(-20,17),pick(leaf),r(.3,.81)));
if(name==="gourmet")x.push('<path d="M330 701L1444 667V900H308Z" fill="#ba976d"/><ellipse cx="940" cy="780" rx="440" ry="99" fill="#e3caa1" stroke="#765f49" stroke-width="20"/><path d="M685 736V544Q687 519 729 520L777 542V744Z" fill="#b37e51" stroke="#5c5645" stroke-width="13"/><ellipse cx="733" cy="532" rx="57" ry="29" fill="#d7b483"/><path d="M1063 739L1035 600h110l-29 139" fill="#986847" stroke="#534e44" stroke-width="10"/><path d="M1090 738v66m-56 0h111" stroke="#e6ceb0" stroke-width="15"/><ellipse cx="918" cy="748" rx="140" ry="53" fill="#b78e53"/><ellipse cx="918" cy="734" rx="114" ry="41" fill="#dbc18d"/>');
if(name==="vodniki")x.push('<path d="M440 645L835 615Q937 615 1007 666L1128 653 1387 646 1453 883 1013 858Q909 827 815 863L423 878Z" fill="#dfc9a1" stroke="#766750" stroke-width="15"/><path d="M955 666L993 844M498 718L847 702M1070 721L1318 703M533 772L807 749" stroke="#a78a63" stroke-width="7" opacity=".67"/><path d="M561 707Q681 630 777 784M1130 787Q1221 648 1311 778" stroke="#73877b" stroke-width="11" fill="none"/>');
if(name==="kolesarstvo")x.push('<path d="M550 899Q690 728 803 676Q913 624 1170 613" stroke="#cbb184" stroke-width="95" fill="none" opacity=".87"/><circle cx="1044" cy="730" r="86" stroke="#353d36" stroke-width="15" fill="none"/><circle cx="1258" cy="730" r="86" stroke="#353d36" stroke-width="15" fill="none"/><path d="M1044 730l102-135 112 135h-214l98-139m-27-4h86m-45 0l-31-43" stroke="#e5cc97" stroke-width="15" fill="none" stroke-linejoin="round"/>');
if(name==="dediscina")x.push('<path d="M495 599L650 480 821 600V784H495Z" fill="#debe8d" stroke="#79674c" stroke-width="14"/><path d="M457 575L651 416 864 580L825 600 651 468 495 607Z" fill="#925d3c"/><path d="M592 785V657h74v128" fill="#645743"/><path d="M733 642h49v53h-49z" fill="#5b787e"/>');
if(name==="sezonsko")for(let i=0;i<100;i++)x.push(e(r(0,1600),r(0,895),r(4,13),r(2,8),pick(["#d0aa58","#b58a43","#d7ba71","#a36c45"]),r(.25,.71),r(-90,90)));
if(name==="gore-traili")x.push('<path d="M620 900Q796 711 926 655T1251 591" fill="none" stroke="#d6c6a0" stroke-width="91" opacity=".73"/>');
for(let i=0;i<(name==="hero"?225:65);i++)x.push(b(r(0,1600),r(0,900),r(6,90),r(-9,9),pick(["#efdbb5","#1d3435","#8e865f"]),r(.03,.19)));
x.push('<rect width="1600" height="900" fill="#d8c7a2" filter="url(#grain)" opacity=".15" style="mix-blend-mode:multiply"/></svg>');
return x.join("\n");}
for(const [name,seed] of [["hero",1063],["kolesarstvo",1070],["dediscina",1083],["sezonsko",1096],["gore-traili",1101],["gourmet",1111],["vodniki",1121]]){const svg=scene(name,seed);writeFileSync(join(out,name+".svg"),svg,"utf8");console.log("painted "+name+" "+(svg.length/1024).toFixed(1)+" KiB");}
