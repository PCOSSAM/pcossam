#!/usr/bin/env python3
"""캐릭터 쇼츠 → 웹사이트 자동 반영기.

유튜브 채널 RSS(새 영상 목록)를 읽어, 시리즈 제목 규칙에 맞는 새 회차가 있으면
해당 시리즈 페이지(예: /shorts/han-daeri.html)에 회차 블록을 추가하고
구조화 데이터(JSON-LD)·sitemap.xml 날짜를 갱신한다.

인스타그램은 로그인 없이 읽을 수 없어서, 버퍼(Buffer)가 같은 영상을 함께 올리는
유튜브를 원본으로 쓴다.

  python3 _shorts/sync.py                     # 실제 RSS 읽기
  python3 _shorts/sync.py --feed sample.xml   # 저장한 RSS 파일로 시험

이미 반영한 영상 ID는 _shorts/series.json 의 "done" 목록에 기록되므로,
손으로 다듬은 회차 내용은 다시 덮어쓰지 않는다.
외부 라이브러리 없이 동작한다 (GitHub Actions에서 그대로 실행).
"""
import datetime as dt
import html
import json
import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
CONF = ROOT / "_shorts" / "series.json"
SITE = "https://pcossam.com"
KST = ZoneInfo("Asia/Seoul")
NS = {"a": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015",
      "m": "http://search.yahoo.com/mrss/"}
UA = {"User-Agent": "Mozilla/5.0 (pcossam-shorts-sync)"}
def esc(x):  # 본문 글자용 (따옴표는 그대로 둔다)
    return html.escape(x, quote=False)


def attr(x):  # 속성값용
    return html.escape(x, quote=True)


def fetch(url, tries=3):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20) as r:
                return r.read().decode("utf-8")
        except Exception as e:  # 유튜브 RSS는 가끔 일시 오류가 난다
            print(f"  읽기 실패({i + 1}/{tries}): {e}")
            time.sleep(5)
    return None


def read_feed(text):
    root = ET.fromstring(text)
    out = []
    for e in root.findall("a:entry", NS):
        out.append({
            "id": e.findtext("yt:videoId", namespaces=NS),
            "title": e.findtext("a:title", namespaces=NS) or "",
            "published": e.findtext("a:published", namespaces=NS),
            "desc": e.findtext("m:group/m:description", namespaces=NS) or "",
        })
    return out


def video_seconds(vid):
    page = fetch(f"https://www.youtube.com/watch?v={vid}", tries=1)
    m = re.search(r'"lengthSeconds":"(\d+)"', page or "")
    return int(m.group(1)) if m else None


def parse_desc(desc, speaker):
    """설명란 규칙: 면접관/한대리 대사 → 빈 줄 → 원칙(+보충, ✔항목) → … → 다음 화: … → #해시태그"""
    lines = [l.strip() for l in desc.splitlines()]
    tags = [t.lstrip("#") for l in lines if l.startswith("#") for t in l.split() if t.startswith("#")]
    nxt = next((l.split(":", 1)[1].strip() for l in lines if l.startswith("다음 화")), None)
    body = [l for l in lines if not l.startswith("#") and not l.startswith("다음 화")]
    paras, cur = [], []
    for l in body + [""]:
        if l:
            cur.append(l)
        elif cur:
            paras.append(cur)
            cur = []
    ep = {"question": None, "answer": None, "principle": None, "sub": [], "checks": [], "extra": [],
          "next": nxt, "tags": tags, "raw": paras}
    rest = paras
    if paras and any(l.startswith("면접관") for l in paras[0]):
        for l in paras[0]:
            if l.startswith("면접관"):
                ep["question"] = l.split(":", 1)[-1].strip()
            elif l.startswith(speaker):
                ep["answer"] = l.split(":", 1)[-1].strip()
        rest = paras[1:]
    if rest:
        first = rest[0]
        ep["principle"] = first[0]
        for l in first[1:]:
            (ep["checks"] if l.startswith("✔") else ep["sub"]).append(l.lstrip("✔ ").strip())
        ep["extra"] = [" ".join(p) for p in rest[1:]]
    return ep


def episode_html(s, v, ep, no, date_kst, secs):
    eid = f"ep{no:02d}"
    headline = v["title"].split("|")[0].strip()
    alias = " · ".join(t for t in ep["tags"] if t not in s["skip_tags"])[:60]
    dur = f'<span class="dur">{secs // 60}:{secs % 60:02d}</span>' if secs else ""
    parts = [
        f'    <article class="ep" id="{eid}">',
        f'      <button class="player" type="button" data-yt="{v["id"]}" aria-label="{attr(s["name"])} {no}화 영상 재생">',
        f'        <img src="https://i.ytimg.com/vi/{v["id"]}/hqdefault.jpg" alt="{attr(s["name"])} {no}화 {attr(headline)} 영상 썸네일" loading="lazy">',
        '        <span class="ai-tag">AI 활용 제작</span>',
        '        <span class="play"><i></i></span>',
        f'        {dur}' if dur else None,
        '      </button>',
        '      <div>',
        f'        <p class="no">#{no:02d} · {date_kst:%Y.%m.%d}</p>',
        f'        <h2>{esc(headline)}</h2>',
        f'        <p class="alias">{esc(alias)}</p>' if alias else None,
    ]
    if ep["question"]:
        parts.append(f'        <div class="qa"><span class="who">면접관</span><p>{esc(ep["question"])}</p></div>')
    if ep["answer"]:
        parts.append(f'        <div class="qa bad"><span class="who">{esc(s["speaker"])}의 답</span><p>{esc(ep["answer"])}</p></div>')
    if ep["principle"]:
        sub = f'<span>{esc(" ".join(ep["sub"]))}</span>' if ep["sub"] else ""
        parts += ['        <div class="principle">', '          <p class="tag">피코쌤 원칙</p>',
                  f'          <p>{esc(ep["principle"])}{sub}</p>', '        </div>']
    if ep["checks"]:
        parts += ['        <div class="better">', '          <p class="tag">이렇게 바꿔 말하기</p>', '          <ul>']
        parts += [f'            <li>{esc(c)}</li>' for c in ep["checks"]]
        parts += ['          </ul>', '        </div>']
    for x in ep["extra"]:
        parts.append(f'        <p class="trap">{esc(x)}</p>')
    if not ep["principle"]:  # 형식이 다르면 설명란을 그대로 보여준다
        parts += [f'        <p class="trap">{esc(" ".join(p))}</p>' for p in ep["raw"]]
    parts += [
        '        <div class="ep-actions">',
        f'          <button class="share" type="button" data-share="{eid}" data-title="{attr(headline)} — {attr(s["page_title"])}">이 답변 친구에게 보내기</button>',
        f'          <a class="watch" href="https://youtube.com/shorts/{v["id"]}" target="_blank" rel="noopener">유튜브에서 보기</a>',
        '        </div>', '      </div>', '    </article>', '', '    <!-- ep:end -->']
    return "\n".join(p for p in parts if p is not None)


def video_ld(s, v, ep, no, secs):
    url = f'{SITE}{s["page"]}'
    transcript = " ".join(" ".join(p) for p in ep["raw"])
    d = {
        "@type": "VideoObject",
        "@id": f"{url}#ep{no:02d}-video",
        "name": v["title"].replace("#shorts", "").strip(),
        "description": transcript[:300],
        "thumbnailUrl": f'https://i.ytimg.com/vi/{v["id"]}/hqdefault.jpg',
        "uploadDate": dt.datetime.fromisoformat(v["published"]).astimezone(KST).isoformat(),
        "embedUrl": f'https://www.youtube.com/embed/{v["id"]}',
        "contentUrl": f'https://youtube.com/shorts/{v["id"]}',
        "inLanguage": "ko",
        "creator": {"@id": f"{SITE}/#person"},
        "transcript": transcript,
    }
    if secs:
        d["duration"] = f"PT{secs}S"
    return d


def sync_series(s, videos, today):
    page = ROOT / s["page"].lstrip("/")
    src = page.read_text(encoding="utf-8")
    pat = re.compile(re.escape(s["title_match"]) + r"\s*(\d+)\s*화")
    new = []
    for v in videos:
        m = pat.search(v["title"])
        if m and v["id"] not in s["done"]:
            new.append((int(m.group(1)), v))
    if not new:
        print(f'- {s["name"]}: 새 회차 없음')
        return False
    new.sort(key=lambda x: x[0])
    last_next = None
    for no, v in new:
        ep = parse_desc(v["desc"], s["speaker"])
        secs = video_seconds(v["id"])
        date_kst = dt.datetime.fromisoformat(v["published"]).astimezone(KST)
        src = src.replace("    <!-- ep:end -->", episode_html(s, v, ep, no, date_kst, secs), 1)
        chip = f'      <a href="#ep{no:02d}">#{no:02d} {esc(v["title"].split("|")[0].strip())}</a>\n      <!-- toc:end -->'
        src = src.replace("      <!-- toc:end -->", chip, 1)
        m = re.search(r'<script type="application/ld\+json">(.*?)</script>', src, re.S)
        ld = json.loads(m.group(1))
        g = ld["@graph"]
        g.insert(max(i for i, x in enumerate(g) if x["@type"] in ("VideoObject", "CreativeWorkSeries")) + 1,
                 video_ld(s, v, ep, no, secs))
        for x in g:
            if x["@type"] == "CreativeWorkSeries":
                x["hasPart"].append({"@id": f'{SITE}{s["page"]}#ep{no:02d}-video'})
            if x["@type"] == "WebPage":
                x["dateModified"] = today
        src = src[:m.start(1)] + "\n" + json.dumps(ld, ensure_ascii=False, indent=2) + "\n" + src[m.end(1):]
        s["done"].append(v["id"])
        last_next = (no, ep["next"])
        print(f'- {s["name"]} {no}화 추가: {v["title"]}')
    if last_next and last_next[1]:
        no, nxt = last_next
        src = re.sub(r"<!-- next:start -->.*?<!-- next:end -->",
                     f"<!-- next:start -->다음 화 · {esc(nxt)}<!-- next:end -->", src, flags=re.S)
        src = re.sub(r'<a class="soon" href="#next">.*?</a>',
                     f'<a class="soon" href="#next">#{no + 1:02d} {esc(nxt)} · 곧 공개</a>', src)
    page.write_text(src, encoding="utf-8")
    sm = ROOT / "sitemap.xml"
    t = sm.read_text(encoding="utf-8")
    t = re.sub(rf"(<loc>{re.escape(SITE + s['page'])}</loc>\s*<lastmod>)[^<]+", rf"\g<1>{today}", t)
    sm.write_text(t, encoding="utf-8")
    return True


def main():
    conf = json.loads(CONF.read_text(encoding="utf-8"))
    if "--feed" in sys.argv:
        text = Path(sys.argv[sys.argv.index("--feed") + 1]).read_text(encoding="utf-8")
    else:
        text = fetch(f'https://www.youtube.com/feeds/videos.xml?channel_id={conf["channel_id"]}')
        if text is None:
            print("RSS를 읽지 못해 이번에는 건너뜀")
            return
    videos = read_feed(text)
    today = dt.datetime.now(KST).strftime("%Y-%m-%d")
    changed = False
    for s in conf["series"]:
        changed |= sync_series(s, videos, today)
    if changed:
        CONF.write_text(json.dumps(conf, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
