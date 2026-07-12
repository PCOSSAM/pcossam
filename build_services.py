import urllib.parse

def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def q(s):
    return urllib.parse.quote(s)

TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{meta_desc}">
<link rel="canonical" href="https://pcossam.com/services/{slug}-en.html">
<link rel="alternate" hreflang="ko" href="https://pcossam.com/services/{slug}.html">
<link rel="alternate" hreflang="en" href="https://pcossam.com/services/{slug}-en.html">
<meta property="og:type" content="website">
<meta property="og:site_name" content="PCOSSAM">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{og_desc}">
<meta property="og:url" content="https://pcossam.com/services/{slug}-en.html">
<meta property="og:image" content="https://pcossam.com/{img}">
<meta property="og:image:width" content="800">
<meta property="og:image:height" content="450">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="service.css">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"Service","name":"{schema_name}","provider":{{"@type":"Person","name":"Mingu Kim (Pico Saem)"}},"areaServed":["South Korea","Global Online"],"serviceType":"{schema_type}","url":"https://pcossam.com/services/{slug}-en.html"}}</script>
</head>
<body>
<nav class="service-nav">
  <a class="brand" href="/pcossam_en.html#hero"><img src="/assets/inline/pcossam-logo.png" alt="PCOSSAM logo">PCOSSAM</a>
  <div class="nav-actions"><a class="nav-link" href="/pcossam_en.html#services">Services</a><a class="nav-cta" href="/pcossam_en.html?service={service_q}#contact">Contact</a></div>
</nav>
<main>
  <section class="hero">
    <div>
      <p class="eyebrow">{eyebrow}</p>
      <h1>{h1}</h1>
      <p class="lead">{lead}</p>
      <div class="hero-actions"><a class="btn primary" href="/pcossam_en.html?service={service_q}#contact">{cta1_label}</a><a class="btn secondary" href="/pcossam_en.html#services">Service List</a></div>
    </div>
    <div class="hero-card"><img src="/{img}" alt="{img_alt}"><div class="hero-note">{hero_note}</div></div>
  </section>
{extra_sections}
  <section class="cta-band"><h2>{cta_h2}</h2><p>{cta_p}</p><a class="btn primary" href="/pcossam_en.html?service={service_q}#contact">Get a Quote</a></section>
</main>
<button class="top-button" type="button" aria-label="Back to top">TOP</button>
<footer>&copy; PCOSSAM. Generative AI training and presentation consulting.</footer>
<script src="service.js"></script>
</body>
</html>
'''

def card_grid(title, cards):
    items = ''.join(f'<div class="card"><strong>{esc(h)}</strong><p>{esc(p)}</p></div>' for h,p in cards)
    return f'  <section class="section"><div class="section-inner"><h2 class="section-title">{esc(title)}</h2><div class="grid">{items}</div></div></section>\n'

def ul_list(title, items):
    lis = ''.join(f'<li>{esc(i)}</li>' for i in items)
    return f'  <section class="section"><div class="section-inner"><h2 class="section-title">{esc(title)}</h2><ul class="list">{lis}</ul></div></section>\n'

def ol_process(title, steps):
    lis = ''.join(f'<li>{esc(i)}</li>' for i in steps)
    return f'  <section class="section"><div class="section-inner"><h2 class="section-title">{esc(title)}</h2><ol class="process">{lis}</ol></div></section>\n'

pages = []

pages.append(dict(
    slug="ai-marketing-website",
    title="AI Marketing Website Creation Training | PCOSSAM",
    meta_desc="A hands-on course where you organize your customers, services, and FAQs with ChatGPT, then build an AEO/GEO-structured AI marketing website yourself using Claude's vibe coding.",
    og_desc="Plan an AI marketing website with ChatGPT and build it yourself with Claude's vibe coding.",
    img="assets/inline/pcossam-inline-04.jpg",
    img_alt="Vibe coding case-study training session",
    schema_name="AI Marketing Website Creation Training",
    schema_type="Generative AI Training",
    service_q=q("AI Marketing Website Creation Training (4H/7H)"),
    eyebrow="CORE SERVICE",
    h1="AI Marketing Website Creation Training",
    lead="Building a website isn't the goal by itself. We organize your message with ChatGPT, then you build it yourself with Claude &mdash; structured to perform well in AI search and customer inquiries.",
    cta1_label="Ask About Training",
    hero_note="Best for: solo consultants, trainers, coaches, small business owners, and marketers. You'll leave with your own service website.",
    extra_sections=(
        card_grid("You need this when", [
            ("Your product story is scattered", "Your strengths, customers, pricing, and FAQs live only in your head — there's no structure an AI or search engine can read."),
            ("You don't show up in AI answers", "You're missing the question-answer format, service descriptions, and structured data that AEO/GEO require."),
            ("You want to experiment fast, without an agency", "You need a marketing asset you can edit and improve yourself, not a finished site you can't touch."),
        ]) +
        ul_list("What the training covers", [
            "Define your customers, buying reasons, service copy, and FAQs with ChatGPT.",
            "Vibe-code the HTML structure, sections, inquiry flow, and responsive layout with Claude.",
            "Apply titles, descriptions, FAQs, and Schema.org JSON-LD to match AEO/GEO structure.",
            "Understand OG meta tags and hero-image structure for social sharing.",
        ]) +
        ol_process("How it works", [
            "Summarize your service and customer in one sentence.",
            "Design your site sections and inquiry conversion flow.",
            "Build a first version with Claude, then refine the copy with ChatGPT.",
            "Run a pre-launch checklist for speed, sharing, and search structure.",
        ])
    ),
    cta_h2="Want to build your own AI marketing website?",
    cta_p="Available as a 4-hour intro session, a 7-hour hands-on session, or a custom corporate format.",
))

pages.append(dict(
    slug="generative-ai-training",
    title="Generative AI Hands-On Training | PCOSSAM",
    meta_desc="Corporate AI training that applies ChatGPT and Claude directly to your workflow — reports, presentations, meeting notes, and planning drafts.",
    og_desc="Corporate AI training that applies ChatGPT and Claude directly to business documents, reports, and presentations.",
    img="assets/inline/pcossam-inline-05.jpg",
    img_alt="Corporate AI presentation training session",
    schema_name="Generative AI Hands-On Training",
    schema_type="Corporate AI Training",
    service_q=q("Generative AI Hands-On Training"),
    eyebrow="CORPORATE TRAINING",
    h1="Generative AI Hands-On Training",
    lead="This isn't a tool-intro lecture — it's training that produces work your team can use the next day. Hands-on practice with reports, presentations, meeting notes, and planning drafts.",
    cta1_label="Ask About Training",
    hero_note="Best for: public agencies, corporate teams, training institutions, and any organization looking to boost document productivity.",
    extra_sections=(
        card_grid("Training goals", [
            ("Cuts your work time", "Reduces time spent on drafting, summarizing, organizing materials, and polishing sentences."),
            ("Raises output quality", "Builds thinking order and review standards, not just prompt tricks."),
            ("Creates a shared team language", "Aligns how different departments use AI around a common work standard."),
        ]) +
        ul_list("Core curriculum", [
            "When to use ChatGPT vs. Claude, and how to choose in practice.",
            "Hands-on practice with report outlines, summaries, tables, and sentence editing.",
            "Planning presentation structure and drafting a storyline.",
            "Security, verification, source-checking, and internal AI usage guidelines.",
        ]) +
        ol_process("How it works", [
            "Confirm your organization's work types and training audience.",
            "Build practice exercises around real work examples.",
            "Mix lecture and hands-on practice to produce real output.",
            "Provide ready-to-use prompts and checklists after training.",
        ])
    ),
    cta_h2="You need an organization that works with AI, not just one that knows about it.",
    cta_p="Available as a 60-90 minute lecture, a 2-4 hour workshop, or a 1-day intensive session.",
))

pages.append(dict(
    slug="pitchdeck-consulting",
    title="AI Presentation &amp; Pitch Deck Consulting | PCOSSAM",
    meta_desc="Presentation consulting that diagnoses and improves your message structure, storyline, and slide flow for fundraising, business proposals, and bid presentations.",
    og_desc="We rebuild the message and storyline of your IR deck, proposal, or presentation into a persuasive structure.",
    img="assets/inline/pcossam-inline-06.jpg",
    img_alt="Presentation strategy and pitch deck consulting",
    schema_name="AI Presentation & Pitch Deck Consulting",
    schema_type="Presentation Consulting",
    service_q=q("AI Presentation & Pitch Deck Consulting"),
    eyebrow="PITCH DECK",
    h1="AI Presentation &amp; Pitch Deck Consulting",
    lead="What matters more than pretty slides is the order in which a decision-maker understands them. We organize your purpose, audience, key message, and supporting logic into a persuasive deck.",
    cta1_label="Ask About Consulting",
    hero_note="Best for: startups, bid-proposal teams, IR presenters, and any organization that needs to improve its business plan or pitch deck.",
    extra_sections=(
        card_grid("Where we improve things", [
            ("Message compression", "Cut what you want to say down to only what needs to be heard."),
            ("Storyline reordering", "Redesign the order of problem, opportunity, solution, evidence, and ask."),
            ("Slide role clarity", "Set a clear reason for each slide to exist, and cut the redundant ones."),
        ]) +
        ul_list("What's included", [
            "Diagnosis of your current materials and feedback on the core problem.",
            "Redesigned outline and flow matched to your presentation purpose.",
            "Improved message sentences and supporting logic, slide by slide.",
            "Preparation for tough Q&A, with likely risk questions mapped out.",
        ]) +
        ol_process("How it works", [
            "Review your materials and presentation context first.",
            "Define your key audience and their decision criteria.",
            "Improve the structure and messaging of your materials.",
            "Provide a final checklist before your rehearsal.",
        ])
    ),
    cta_h2="If you have plenty of material but weak persuasion, start with structure.",
    cta_p="Available as a one-time diagnostic, a package consulting engagement, or focused IR consulting, depending on scope and purpose.",
))

pages.append(dict(
    slug="presentation-coaching",
    title="Presentation &amp; Pitch Deck Coaching | PCOSSAM",
    meta_desc="1:1 presentation and pitch deck coaching that improves your delivery, message structure, rehearsal, and Q&A handling.",
    og_desc="1:1 coaching on your message, delivery, rehearsal, and Q&A handling, built around real presentation conditions.",
    img="assets/inline/pcossam-inline-07.jpg",
    img_alt="1:1 speech coaching session",
    schema_name="Presentation & Pitch Deck Coaching",
    schema_type="Speech Coaching",
    service_q=q("Presentation & Pitch Deck Coaching (1:1)"),
    eyebrow="1:1 COACHING",
    h1="Presentation &amp; Pitch Deck Coaching",
    lead="A presentation isn't time spent reading slides — it's time spent changing someone's judgment. We refine your words, eye contact, pacing, key sentences, and Q&A handling to real presentation standards.",
    cta1_label="Ask About Coaching",
    hero_note="Best for: individuals, founders, executives, IR presenters, and bid-proposal speakers preparing for an important presentation.",
    extra_sections=(
        card_grid("What we work on", [
            ("Structure of your talk", "We check whether your opening, key message, evidence, and closing are clear."),
            ("Delivery", "We check whether pace, pauses, emphasis, eye contact, and gestures fit your audience."),
            ("Q&amp;A", "We practice answering expected and tough questions briefly and accurately."),
        ]) +
        ul_list("What's included", [
            "Script and key-sentence review.",
            "Feedback on a rehearsal video or a live run-through.",
            "Slide-by-slide talking points.",
            "Anticipated Q&A questions and answer direction.",
        ]) +
        ol_process("How it works", [
            "Confirm your presentation purpose and materials.",
            "Organize your flow and key message.",
            "Present as if it were real, and get feedback.",
            "Repeat practice with a revised script and Q&A handling.",
        ])
    ),
    cta_h2="An important presentation needs a different way of practicing.",
    cta_p="Available as a single session, a 3-session package, a 5-session package, or executive coaching.",
))

pages.append(dict(
    slug="ai-report-proposal",
    title="AI Report &amp; Proposal Writing Training | PCOSSAM",
    meta_desc="Corporate training on the full business-document workflow with ChatGPT and Claude — research, outline design, executive summaries, report drafts, and proposal writing.",
    og_desc="Learn to research, outline, summarize, draft, and write persuasive proposals with ChatGPT and Claude, matched to real business workflow.",
    img="assets/inline/pcossam-inline-05.jpg",
    img_alt="AI report and proposal writing training",
    schema_name="AI Report & Proposal Writing Training",
    schema_type="Corporate AI Document Training",
    service_q=q("AI Report & Proposal Writing Training"),
    eyebrow="BUSINESS DOCUMENTS",
    h1="AI Report &amp; Proposal Writing Training",
    lead="Reports and proposals need structure before they need good writing. Learn the real workflow — researching material, building an outline, summarizing the key points, and writing persuasive sentences — with ChatGPT and Claude.",
    cta1_label="Ask About Training",
    hero_note="Best for: employees who write frequent reports, public-sector staff, and anyone who needs to quickly upgrade proposals and planning documents.",
    extra_sections=(
        card_grid("This is for you if", [
            ("Report drafts take too long", "A good fit for teams that spend too much time on research, outlining, and editing."),
            ("Your proposals lack persuasive structure", "We give you structure when the problem, solution, expected impact, and action plan are scattered."),
            ("AI output feels inconsistent", "You'll learn review standards and a revision workflow, not just a handful of prompts."),
        ]) +
        ul_list("What the training covers", [
            "Build research questions and organize key sources with ChatGPT and Claude.",
            "Design an outline, summary, and action items matched to your report's purpose.",
            "Turn your proposal's problem definition, solution, expected impact, and differentiators into strong sentences.",
            "Learn to review AI-drafted content and fix exaggeration, gaps, and weak evidence.",
        ]) +
        card_grid("What you'll walk away with", [
            ("Report draft", "A draft with outline, summary, body flow, and key sentences included."),
            ("Proposal structure", "A proposal flow that clearly connects the customer's problem to your solution."),
            ("Document-writing prompts", "Reusable prompts and a review checklist for repeat tasks."),
        ]) +
        ol_process("How it works", [
            "Confirm your organization's report and proposal types.",
            "Design a document-writing workflow around real work examples.",
            "Draft with ChatGPT and Claude, then revise against review standards.",
            "Provide ready-to-use prompts and checklists after training.",
        ])
    ),
    cta_h2="Writing fast with AI matters less than knowing how to fix it properly.",
    cta_p="Available as a 2-hour briefing, a 4-hour hands-on session, or a custom corporate workshop.",
))

pages.append(dict(
    slug="ai-transformation-partnership",
    title="Custom AI Transformation Partnership | PCOSSAM",
    meta_desc="A monthly partnership that designs and runs your organization's AI workflow across presentations, reports, marketing, and website-building — not just a one-off lecture.",
    og_desc="We design your organization's presentation, report, marketing, and website workflow as a monthly AI transformation project.",
    img="assets/inline/pcossam-inline-09.jpg",
    img_alt="Long-term partnership meeting",
    schema_name="Custom AI Transformation Partnership",
    schema_type="AI Transformation Consulting",
    service_q=q("Custom AI Transformation Partnership"),
    eyebrow="MONTHLY PARTNERSHIP",
    h1="Custom AI Transformation Partnership",
    lead="An organization's AI adoption rarely finishes with a single lecture. We design and run it monthly, matched to your real workflow — presentations, reports, marketing, and website-building.",
    cta1_label="Ask About Partnership",
    hero_note="Best for: companies, institutions, and training organizations that want to build a department-level AI workflow.",
    extra_sections=(
        card_grid("Scope of the partnership", [
            ("Training design", "We build an AI training roadmap matched to your organization's level and work types."),
            ("Applied to real work", "We apply AI to reports, presentations, proposals, and marketing content."),
            ("Ongoing output improvement", "We don't stop at training — we keep improving your actual deliverables together."),
        ]) +
        ul_list("What's included", [
            "A monthly AI training and consulting operating plan.",
            "Hands-on design based on each department's real work cases.",
            "Support for AI reports, presentations, and website-building.",
            "Prompts and checklists organized for internal rollout.",
        ]) +
        ol_process("How it works", [
            "Diagnose your organization's current AI usage level.",
            "Decide which work and deliverables to apply it to first.",
            "Run training, workshops, and consulting on a monthly basis.",
            "Review output and design the next round of improvements.",
        ])
    ),
    cta_h2="AI transformation is an operating system, not a lecture.",
    cta_p="Run on a custom monthly quote, scoped to your training frequency and consulting range.",
))

import os
outdir = "/sessions/gallant-charming-ride/mnt/outputs/services_en"
for p in pages:
    html = TEMPLATE.format(**p)
    fname = f"{p['slug']}-en.html"
    with open(os.path.join(outdir, fname), "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote", fname, len(html))
