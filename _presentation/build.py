#!/usr/bin/env python3
"""피코쌤 프레젠테이션 가이드 생성기.

_presentation/articles/*.md 원고를 읽어 공개일(publish)이 지난 글만
/presentation/ 아래 HTML로 만들고, 허브·sitemap.xml·llms.txt를 갱신한다.

  python3 _presentation/build.py          # 오늘(한국시간) 기준 공개분만
  python3 _presentation/build.py --all    # 미리보기용: 전부 생성
  python3 _presentation/build.py --date 2026-11-12   # 특정 날짜 기준

외부 라이브러리 없이 동작한다 (GitHub Actions에서 그대로 실행).
"""
import datetime as dt
import html
import json
import re
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "_presentation"
OUT = ROOT / "presentation"
SITE = "https://pcossam.com"
BASE = f"{SITE}/presentation/"
BRAND_COPY = "AI를 깊이 이해하는 프레젠테이션 전문가, 피코쌤"
BRAND_PROOF = "연 200회 기업 강의 · AI 관련 저서 3권"

SERVICES = {
    "presentation-coaching": ("발표 코칭", "/services/presentation-coaching.html",
                              "중요한 발표를 앞둔 개인·임원·CEO를 위한 1:1 맞춤 코칭"),
    "pitchdeck-consulting": ("경쟁 PT·피치덱 컨설팅", "/services/pitchdeck-consulting.html",
                             "청중 분석부터 메시지·스토리라인·질의응답까지 설계"),
    "generative-ai-training": ("생성형 AI 실무교육", "/services/generative-ai-training.html",
                               "AI로 보고서·제안서·PPT를 만드는 기업 실무 교육"),
}

GUIDE_STEPS = [
    ("P", "People", "누구에게 발표하는가", "keyword-intersection"),
    ("C", "Context", "어떤 상황에서 발표하는가", "presentation-context"),
    ("O", "Objective", "발표 후 청중이 무엇을 하게 할 것인가", "presentation-objective"),
    ("S", "Story", "비유로 이해시키는 법", "opening-3-minutes"),
    ("S", "Simulation", "실전처럼 리허설하는 법", "rehearsal"),
    ("A", "Action", "질문을 끌어내는 발표", "qa-preparation"),
    ("M", "Measure", "다음 발표를 더 잘하는 법", "pcossam-method"),
]


# ───────────────────────── 원고 읽기 ─────────────────────────
def parse(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        raise SystemExit(f"frontmatter 없음: {path}")
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    body = m.group(2)
    todos = re.findall(r"<!--\s*TODO:(.*?)-->", body, re.S)
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
    faq = []
    if "## 자주 묻는 질문" in body:
        body, faq_txt = body.split("## 자주 묻는 질문", 1)
        for q, a in re.findall(r"^Q:\s*(.+?)\nA:\s*(.+?)(?=\n\s*\nQ:|\Z)", faq_txt.strip(), re.S | re.M):
            faq.append((q.strip(), " ".join(a.split())))
    meta["body"], meta["faq"], meta["todos"] = body.strip(), faq, [t.strip() for t in todos]
    return meta


# ───────────────────────── 마크다운 일부 → HTML ─────────────────────────
def inline(s, published):
    s = html.escape(s, quote=False)

    def link(mt):
        slug, label = mt.group(1), mt.group(2)
        if slug in published:
            return f'<a href="/presentation/{slug}.html">{label}</a>'
        return label  # 아직 공개 전인 글은 링크 없이 글자만

    s = re.sub(r"\[\[([a-z0-9-]+)\|(.+?)\]\]", link, s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    return s


def md(text, published):
    out, lines, i = [], text.splitlines(), 0
    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            i += 1
            continue
        if ln.startswith(":::case"):
            title = ln[len(":::case"):].strip() or "현장 사례"
            buf = []
            i += 1
            while i < len(lines) and lines[i].strip() != ":::":
                buf.append(lines[i])
                i += 1
            i += 1
            out.append(f'<aside class="case-box"><div class="case-label">피코쌤 현장 사례</div>'
                       f'<h3>{inline(title, published)}</h3>{md(chr(10).join(buf), published)}</aside>')
            continue
        if ln.startswith("### "):
            out.append(f"<h3>{inline(ln[4:], published)}</h3>")
        elif ln.startswith("## "):
            h = ln[3:]
            out.append(f'<h2 id="{re.sub(r"[^0-9A-Za-z가-힣]+", "-", h).strip("-")}">{inline(h, published)}</h2>')
        elif ln.startswith("> "):
            buf = []
            while i < len(lines) and lines[i].startswith("> "):
                buf.append(inline(lines[i][2:], published))
                i += 1
            out.append("<blockquote>" + "<br>".join(buf) + "</blockquote>")
            continue
        elif re.match(r"^- ", ln):
            buf = []
            while i < len(lines) and lines[i].startswith("- "):
                buf.append(f"<li>{inline(lines[i][2:], published)}</li>")
                i += 1
            out.append("<ul>" + "".join(buf) + "</ul>")
            continue
        elif re.match(r"^\d+\. ", ln):
            buf = []
            while i < len(lines) and re.match(r"^\d+\. ", lines[i]):
                item = re.sub(r"^\d+\. ", "", lines[i])
                buf.append(f"<li>{inline(item, published)}</li>")
                i += 1
            out.append("<ol>" + "".join(buf) + "</ol>")
            continue
        else:
            buf = []
            while i < len(lines) and lines[i].strip() and not re.match(r"^(#|> |- |\d+\. |:::)", lines[i]):
                buf.append(lines[i].strip())
                i += 1
            out.append(f"<p>{inline(' '.join(buf), published)}</p>")
            continue
        i += 1
    return "\n".join(out)


# ───────────────────────── 공통 조각 ─────────────────────────
CSS = """
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--black:#0a0a0a;--white:#fafaf8;--gray-100:#f4f3f0;--gray-200:#e8e7e2;--gray-400:#9e9c97;--gray-600:#5e5c57;--accent:#1a3a5c;--gold:#c8973a;--ink:#2c2b28}
html{scroll-behavior:smooth}
body{font-family:'Noto Sans KR',sans-serif;background:var(--white);color:var(--black);line-height:1.8;word-break:keep-all}
.site-header{position:sticky;top:0;z-index:100;background:rgba(250,250,248,.95);backdrop-filter:blur(10px);border-bottom:1px solid var(--gray-200);padding:16px 40px;display:flex;align-items:center;justify-content:space-between;gap:16px}
.header-logo{font-weight:900;font-size:18px;text-decoration:none;color:var(--black);letter-spacing:.05em}
.header-nav{display:flex;gap:22px;align-items:center}
.header-nav a{text-decoration:none;color:var(--gray-600);font-size:14px}
.header-nav a:hover,.header-nav a[aria-current]{color:var(--black)}
.header-cta{padding:8px 20px;background:var(--black);color:var(--white)!important;border-radius:50px;font-size:13px;font-weight:700}
.wrap{max-width:760px;margin:0 auto;padding:56px 24px 100px}
.crumbs{font-size:13px;color:var(--gray-400);margin-bottom:28px}
.crumbs a{color:var(--gray-600);text-decoration:none}
.eyebrow{font-size:12px;font-weight:700;letter-spacing:.1em;color:var(--gold);margin-bottom:14px}
h1{font-family:'Noto Serif KR',serif;font-size:clamp(26px,4.2vw,40px);line-height:1.35;margin-bottom:18px}
.meta{font-size:13px;color:var(--gray-400);padding-bottom:26px;border-bottom:1px solid var(--gray-200);margin-bottom:34px}
.answer{background:#fff;border:1px solid var(--gray-200);border-left:4px solid var(--gold);border-radius:14px;padding:24px 26px;margin-bottom:44px}
.answer-label{font-size:12px;font-weight:700;color:var(--accent);letter-spacing:.08em;margin-bottom:8px}
.answer p{font-size:16.5px;line-height:1.85;color:var(--ink)}
.body h2{font-family:'Noto Serif KR',serif;font-size:24px;line-height:1.45;margin:52px 0 18px;scroll-margin-top:90px}
.body h3{font-size:18px;margin:32px 0 12px}
.body p{font-size:17px;line-height:1.95;color:var(--ink);margin-bottom:22px}
.body ul,.body ol{margin:0 0 24px 22px;color:var(--ink);font-size:16.5px;line-height:1.85}
.body li{margin-bottom:8px}
.body blockquote{margin:0 0 24px;padding:18px 22px;background:var(--gray-100);border-radius:12px;font-size:16.5px;color:var(--ink);line-height:1.85}
.body a{color:var(--accent);text-underline-offset:3px}
.body strong{color:var(--black)}
.case-box{margin:40px 0;padding:26px 28px;background:var(--accent);color:#fff;border-radius:18px}
.case-box .case-label{font-size:12px;font-weight:700;letter-spacing:.1em;color:var(--gold);margin-bottom:6px}
.case-box h3{color:#fff;margin:0 0 12px;font-size:19px}
.case-box p{color:rgba(255,255,255,.9);font-size:16px;margin-bottom:12px}
.case-box p:last-child{margin-bottom:0}
.faq{margin-top:64px}
.faq h2{font-family:'Noto Serif KR',serif;font-size:24px;margin-bottom:18px}
.faq details{border-top:1px solid var(--gray-200);padding:18px 4px}
.faq details:last-child{border-bottom:1px solid var(--gray-200)}
.faq summary{cursor:pointer;font-weight:700;font-size:16.5px;list-style:none;display:flex;justify-content:space-between;gap:12px}
.faq summary::after{content:"+";color:var(--gold);font-weight:700}
.faq details[open] summary::after{content:"−"}
.faq details p{margin-top:12px;color:var(--ink);font-size:16px;line-height:1.85}
.author{margin-top:64px;display:flex;gap:18px;align-items:flex-start;padding:24px;border:1px solid var(--gray-200);border-radius:18px;background:#fff}
.author-badge{flex:0 0 52px;height:52px;border-radius:50%;background:var(--black);color:var(--gold);display:flex;align-items:center;justify-content:center;font-weight:900;font-size:13px}
.author-copy{font-weight:700;font-size:16px;margin-bottom:2px}
.author-proof{font-size:13.5px;color:var(--gold);font-weight:700;margin-bottom:8px}
.author p{font-size:14.5px;color:var(--gray-600);line-height:1.75}
.author a{color:var(--accent)}
.svc{margin-top:28px;padding:30px 32px;background:var(--black);border-radius:20px;color:#fff}
.svc .eyebrow{margin-bottom:8px}
.svc h3{font-size:20px;margin-bottom:8px}
.svc p{font-size:15px;color:rgba(255,255,255,.75);margin-bottom:20px;line-height:1.7}
.btns{display:flex;flex-wrap:wrap;gap:10px}
.btn{display:inline-flex;padding:12px 24px;border-radius:50px;font-size:14px;font-weight:700;text-decoration:none}
.btn-gold{background:var(--gold);color:#fff}
.btn-line{border:1px solid rgba(255,255,255,.4);color:#fff}
.pager{margin-top:44px;display:grid;grid-template-columns:1fr 1fr;gap:12px}
.pager a{display:block;padding:18px 20px;border:1px solid var(--gray-200);border-radius:14px;text-decoration:none;color:var(--black);background:#fff;font-size:14.5px;line-height:1.55}
.pager span{display:block;font-size:12px;color:var(--gray-400);margin-bottom:4px}
.pager .next{text-align:right;grid-column:2}
.steps{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px;margin:8px 0 48px}
.step{padding:16px;border-radius:14px;background:#fff;border:1px solid var(--gray-200);text-decoration:none;color:var(--black);display:block}
.step b{display:block;font-size:26px;font-weight:900;color:var(--gold);line-height:1}
.step em{display:block;font-style:normal;font-weight:700;font-size:14px;margin:6px 0 2px}
.step small{font-size:12.5px;color:var(--gray-600);line-height:1.5;display:block}
.list{display:grid;gap:12px;margin-bottom:24px}
.card{display:block;padding:22px 24px;border:1px solid var(--gray-200);border-radius:16px;background:#fff;text-decoration:none;color:var(--black)}
.card:hover{border-color:var(--gold)}
.card .eyebrow{margin-bottom:6px}
.card h3{font-size:17.5px;line-height:1.5;margin-bottom:6px}
.card p{font-size:14.5px;color:var(--gray-600);line-height:1.7}
footer{background:var(--black);color:rgba(255,255,255,.5);text-align:center;padding:40px 24px;font-size:13px;line-height:1.9}
footer a{color:var(--gold);text-decoration:none}
@media(max-width:640px){.site-header{padding:14px 16px}.header-nav{gap:12px}.header-nav .hide-m{display:none}.wrap{padding:36px 16px 80px}.answer,.case-box,.svc{padding:22px 20px}.pager{grid-template-columns:1fr}.pager .next{grid-column:1}}
"""

GA = """<script async src="https://www.googletagmanager.com/gtag/js?id=G-SDVHD2TD0K"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-SDVHD2TD0K');</script>"""

HEADER = """<header class="site-header">
  <a href="/" class="header-logo">PCOSSAM</a>
  <nav class="header-nav">
    <a href="/#services" class="hide-m">서비스</a>
    <a href="/presentation/"{cur}>발표 가이드</a>
    <a href="/blog/" class="hide-m">블로그</a>
    <a href="/#contact" class="header-cta">문의하기</a>
  </nav>
</header>"""

FOOTER = f"""<footer>
  <p>© 2026 PCOSSAM · 피코쌤(김민구) · {BRAND_COPY}<br>
  <a href="/">pcossam.com</a> · pcossam@pcossam.com</p>
</footer>"""

PERSON = {
    "@type": "Person", "name": "김민구", "alternateName": "피코쌤",
    "jobTitle": "AI 프레젠테이션 컨설턴트 · 발표 코치", "url": SITE,
    "sameAs": ["https://www.youtube.com/@pcossam", "https://www.instagram.com/pcossam/",
               "https://blog.naver.com/specskillscontents"],
}


def author_box():
    return f"""<section class="author">
  <div class="author-badge">PCO</div>
  <div>
    <div class="author-copy">{BRAND_COPY}</div>
    <div class="author-proof">{BRAND_PROOF}</div>
    <p>피코쌤(김민구)은 2007년부터 경쟁 PT·입찰 발표 컨설팅과 발표 코칭을 해온 AI 프레젠테이션 컨설턴트입니다. 이 가이드는 피코쌤이 현장에서 직접 겪고 검증한 내용을 정리했습니다. <a href="/#about">프로필 보기</a></p>
  </div>
</section>"""


def head(title, desc, keywords, url, ogtype, ld, published_date=None):
    extra = f'\n<meta property="article:published_time" content="{published_date}">' if published_date else ""
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
{GA}
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<meta name="keywords" content="{html.escape(keywords)}">
<meta name="author" content="피코쌤 (김민구)">
<link rel="canonical" href="{url}">
<link rel="icon" href="/favicon.ico">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="{ogtype}">
<meta property="og:url" content="{url}">
<meta property="og:site_name" content="PCOSSAM — 피코쌤">
<meta property="og:locale" content="ko_KR">{extra}
<script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=1)}
</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&family=Noto+Serif+KR:wght@400;700&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>"""


def faq_html(faq):
    if not faq:
        return ""
    items = "".join(f"<details><summary>{html.escape(q)}</summary><p>{html.escape(a)}</p></details>" for q, a in faq)
    return f'<section class="faq"><h2>자주 묻는 질문</h2>{items}</section>'


def faq_ld(faq):
    return {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}


# ───────────────────────── 글 페이지 ─────────────────────────
def article_page(a, published, prev_a, next_a, today):
    url = f"{BASE}{a['slug']}.html"
    svc_name, svc_url, svc_desc = SERVICES.get(a.get("service"), SERVICES["presentation-coaching"])
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "Article", "headline": a["title"], "description": a["description"],
         "datePublished": a["publish"], "dateModified": a["publish"], "inLanguage": "ko",
         "author": PERSON, "publisher": {"@type": "Organization", "name": "PCOSSAM", "url": SITE},
         "mainEntityOfPage": url, "keywords": a["keywords"],
         "isPartOf": {"@type": "CollectionPage", "name": "피코쌤 프레젠테이션 가이드", "url": BASE},
         "abstract": a["answer"]},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "홈", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "프레젠테이션 가이드", "item": BASE},
            {"@type": "ListItem", "position": 3, "name": a["title"], "item": url}]},
    ]}
    if a["faq"]:
        ld["@graph"].append(faq_ld(a["faq"]))
    pager = ""
    if prev_a or next_a:
        pager = '<nav class="pager">'
        if prev_a:
            pager += f'<a href="/presentation/{prev_a["slug"]}.html"><span>← 이전 글</span>{html.escape(prev_a["title"].split(" — ")[0])}</a>'
        if next_a:
            pager += f'<a class="next" href="/presentation/{next_a["slug"]}.html"><span>다음 글 →</span>{html.escape(next_a["title"].split(" — ")[0])}</a>'
        pager += "</nav>"
    pub = dt.date.fromisoformat(a["publish"])
    return f"""{head(a['seo_title'], a['description'], a['keywords'], url, 'article', ld, a['publish'])}
<body>
{HEADER.format(cur='')}
<main class="wrap">
  <nav class="crumbs" aria-label="경로"><a href="/">홈</a> › <a href="/presentation/">프레젠테이션 가이드</a></nav>
  <div class="eyebrow">{html.escape(a['category'])}</div>
  <h1>{html.escape(a['title'])}</h1>
  <div class="meta">피코쌤(김민구) · {BRAND_COPY} · <time datetime="{a['publish']}">{pub.year}.{pub.month}.{pub.day}</time></div>
  <section class="answer">
    <div class="answer-label">한 줄 답</div>
    <p>{html.escape(a['answer'])}</p>
  </section>
  <article class="body">
{md(a['body'], published)}
  </article>
  {faq_html(a['faq'])}
  {author_box()}
  <section class="svc">
    <div class="eyebrow">이 주제와 관련된 서비스</div>
    <h3>{svc_name}</h3>
    <p>{svc_desc}. 발표 일정과 상황을 알려주시면 맞춤으로 안내해 드립니다.</p>
    <div class="btns"><a class="btn btn-gold" href="/#contact">문의하기</a><a class="btn btn-line" href="{svc_url}">서비스 자세히 보기</a></div>
  </section>
  {pager}
  <p style="margin-top:36px"><a href="/presentation/" style="color:var(--gray-600);font-size:14px">← 프레젠테이션 가이드 전체 보기</a></p>
</main>
{FOOTER}
</body>
</html>
"""


# ───────────────────────── 허브 페이지 ─────────────────────────
def hub_page(hub, arts, published):
    steps = ""
    for letter, en, ko, slug in GUIDE_STEPS:
        inner = f"<b>{letter}</b><em>{en}</em><small>{ko}</small>"
        steps += (f'<a class="step" href="/presentation/{slug}.html">{inner}</a>' if slug in published
                  else f'<div class="step">{inner}</div>')
    cards = "".join(
        f'<a class="card" href="/presentation/{a["slug"]}.html"><div class="eyebrow">{html.escape(a["category"])}</div>'
        f'<h3>{html.escape(a["title"])}</h3><p>{html.escape(a["description"])}</p></a>' for a in arts)
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "CollectionPage", "name": hub["title"], "description": hub["description"], "url": BASE,
         "inLanguage": "ko", "author": PERSON, "about": "프레젠테이션, 발표 준비, 발표 코칭"},
        {"@type": "ItemList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "url": f"{BASE}{a['slug']}.html", "name": a["title"]}
            for i, a in enumerate(arts)]},
        {"@type": "DefinedTerm", "name": "PCOSSAM Method",
         "description": "피코쌤(김민구)이 만든 발표 준비 7단계 방법론: People(청중), Context(상황), Objective(목적), "
                        "Story(비유), Simulation(리허설), Action(질문 유도), Measure(측정).",
         "url": f"{BASE}pcossam-method.html"},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "홈", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "프레젠테이션 가이드", "item": BASE}]},
    ]}
    if hub["faq"]:
        ld["@graph"].append(faq_ld(hub["faq"]))
    return f"""{head(hub['seo_title'], hub['description'], hub['keywords'], BASE, 'website', ld)}
<body>
{HEADER.format(cur=' aria-current="page"')}
<main class="wrap">
  <nav class="crumbs" aria-label="경로"><a href="/">홈</a> › 프레젠테이션 가이드</nav>
  <div class="eyebrow">PRESENTATION GUIDE</div>
  <h1>{html.escape(hub['title'])}</h1>
  <div class="meta">피코쌤(김민구) · {BRAND_COPY} · {BRAND_PROOF}</div>
  <section class="answer">
    <div class="answer-label">한 줄 답</div>
    <p>{html.escape(hub['answer'])}</p>
  </section>
  <article class="body">
{md(hub['body'], published)}
  <h2 id="method">발표 준비 7단계, PCOSSAM Method</h2>
  </article>
  <div class="steps">{steps}</div>
  <article class="body"><h2 id="all">질문별로 찾아보기</h2></article>
  <div class="list">{cards}</div>
  {faq_html(hub['faq'])}
  {author_box()}
  <section class="svc">
    <div class="eyebrow">중요한 발표를 앞두고 있다면</div>
    <h3>발표 코칭 · 경쟁 PT 컨설팅</h3>
    <p>청중 분석부터 메시지 설계, 리허설, 질의응답까지 피코쌤이 함께 준비합니다.</p>
    <div class="btns"><a class="btn btn-gold" href="/#contact">문의하기</a><a class="btn btn-line" href="/services/presentation-coaching.html">발표 코칭 보기</a></div>
  </section>
</main>
{FOOTER}
</body>
</html>
"""


# ───────────────────────── sitemap / llms ─────────────────────────
def replace_block(text, start, end, block, anchor):
    if start in text:
        return re.sub(re.escape(start) + r".*?" + re.escape(end), start + block + end, text, flags=re.S)
    return text.replace(anchor, start + block + end + "\n" + anchor, 1)


def update_sitemap(arts, today):
    p = ROOT / "sitemap.xml"
    entries = [(BASE, max([a["publish"] for a in arts] + [today]), "0.9")] + \
              [(f"{BASE}{a['slug']}.html", a["publish"], "0.8") for a in arts]
    block = "\n" + "".join(
        f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{d}</lastmod>\n    <changefreq>monthly</changefreq>\n"
        f"    <priority>{pr}</priority>\n  </url>\n" for u, d, pr in entries) + "  "
    t = replace_block(p.read_text(encoding="utf-8"), "<!-- presentation-guide:start -->",
                      "<!-- presentation-guide:end -->", block, "</urlset>")
    p.write_text(t, encoding="utf-8")


def update_llms(arts):
    p = ROOT / "llms.txt"
    lines = ["\n## 프레젠테이션 가이드 (AI 시대, 결국 다시 프레젠테이션)\n",
             f"- [프레젠테이션 가이드 허브]({BASE}): 피코쌤의 발표 준비 7단계 PCOSSAM Method와 질문별 발표 노하우 모음"]
    lines += [f"- [{a['title']}]({BASE}{a['slug']}.html): {a['answer']}" for a in arts]
    t = replace_block(p.read_text(encoding="utf-8"), "<!-- presentation-guide:start -->",
                      "<!-- presentation-guide:end -->", "\n".join(lines) + "\n", "## Expert profile")
    p.write_text(t, encoding="utf-8")


# ───────────────────────── 실행 ─────────────────────────
def main():
    args = sys.argv[1:]
    today = dt.datetime.now(ZoneInfo("Asia/Seoul")).date().isoformat()
    if "--date" in args:
        today = args[args.index("--date") + 1]
    show_all = "--all" in args

    allarts = sorted((parse(p) for p in (SRC / "articles").glob("*.md")), key=lambda a: int(a["order"]))
    arts = [a for a in allarts if show_all or a["publish"] <= today]
    published = {a["slug"] for a in arts}
    hub = parse(SRC / "hub.md")

    OUT.mkdir(exist_ok=True)
    for a in allarts:  # 공개 전 글은 혹시 남아 있어도 지운다
        f = OUT / f"{a['slug']}.html"
        if a["slug"] not in published and f.exists():
            f.unlink()
    for i, a in enumerate(arts):
        prev_a = arts[i - 1] if i > 0 else None
        next_a = arts[i + 1] if i + 1 < len(arts) else None
        (OUT / f"{a['slug']}.html").write_text(article_page(a, published, prev_a, next_a, today), encoding="utf-8")
    (OUT / "index.html").write_text(hub_page(hub, arts, published), encoding="utf-8")
    update_sitemap(arts, today)
    update_llms(arts)

    print(f"기준일 {today} · 공개 {len(arts)}/{len(allarts)}편")
    for a in allarts:
        mark = "공개" if a["slug"] in published else "대기"
        print(f"  [{mark}] {a['publish']}  {a['slug']}")
    for a in allarts:
        for t in a["todos"]:
            print(f"  ※ 보강 필요 · {a['slug']}: {t}")


if __name__ == "__main__":
    main()
