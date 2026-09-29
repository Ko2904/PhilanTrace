"""
PhilanTrace - Streamlit MVP (donor view)

Run locally:
    pip install streamlit pandas plotly
    streamlit run philantrace_app.py

All organisations, partners, people, invoices and ledger hashes are fictional demo data.
On first start the app writes a small .streamlit/config.toml (theme colours) next to where
you launch it. Restart once so the green accent also applies to radio buttons and checkboxes.
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# ----------------------------------------------------------------------------
# Theme file (so radios / checkboxes use the green accent instead of Streamlit red)
# ----------------------------------------------------------------------------
def ensure_theme_file() -> None:
    cfg = Path(".streamlit") / "config.toml"
    if cfg.exists():
        return
    try:
        cfg.parent.mkdir(exist_ok=True)
        cfg.write_text(
            "[theme]\n"
            'base = "light"\n'
            'primaryColor = "#2E5E4A"\n'
            'backgroundColor = "#F8F9F4"\n'
            'secondaryBackgroundColor = "#EDF5EA"\n'
            'textColor = "#20312A"\n'
        )
    except OSError:
        pass


ensure_theme_file()
st.set_page_config(page_title="PhilanTrace", page_icon="🌿", layout="wide")

# ----------------------------------------------------------------------------
# Palette
# ----------------------------------------------------------------------------
FOREST = "#2E5E4A"
LEAF = "#7FB68A"
SAGE = "#BFDDBE"
MINT = "#E6F2E3"
MUTED = "#6E7F75"
LINE = "#DCE6D8"
SAND = "#E8CF8E"
CHART_COLORS = [FOREST, LEAF, SAGE, SAND, "#A9CFE0", "#F0B9A0", "#B8B0DC", "#9DBBA7"]

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Manrope:wght@700;800&display=swap');
:root{--bg:#F8F9F4;--surface:#FFFFFF;--mint:#E6F2E3;--sage:#BFDDBE;--leaf:#7FB68A;--forest:#2E5E4A;
--ink:#20312A;--muted:#6E7F75;--line:#DCE6D8;--sand:#F6EBC8;--sandink:#8A6A1F;--sandline:#D8B85A;}
.stApp{background:var(--bg);color:var(--ink);}
header[data-testid="stHeader"]{display:none;}
.block-container{padding-top:2.2rem;max-width:1180px;}
section[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"]{display:none;}
[data-testid="stRadio"] [role="radiogroup"]{gap:.25rem;flex-wrap:wrap;}
[data-testid="stRadio"] [role="radiogroup"] label{padding:.5rem .8rem;border:1px solid transparent;border-radius:999px;
 color:var(--forest);font-weight:600;transition:background .18s ease,border-color .18s ease,color .18s ease;}
[data-testid="stRadio"] [role="radiogroup"] label:hover{background:var(--mint);border-color:var(--sage);}
[data-testid="stRadio"] [role="radiogroup"] label:has(input:checked){background:var(--forest);color:#fff;}
div[data-testid="stHorizontalBlock"]:has(.brand){position:relative;z-index:0;background:transparent;border:0;border-radius:0;
 padding:.65rem .75rem;
 align-items:center;margin-bottom:.5rem;}
div[data-testid="stHorizontalBlock"]:has(.brand)::before{content:"";position:absolute;z-index:-1;top:-72px;bottom:0;left:50%;
 width:100vw;transform:translateX(-50%);background:#234B3B;}
div[data-testid="stHorizontalBlock"]:has(.brand) [data-testid="stRadio"] [role="radiogroup"]{
 flex-wrap:nowrap;justify-content:center;white-space:nowrap;overflow-x:auto;scrollbar-width:none;}
div[data-testid="stHorizontalBlock"]:has(.brand) [data-testid="stRadio"] [role="radiogroup"] label{
 flex:0 0 auto;color:#E6F2EC;background:transparent;border-color:transparent;}
div[data-testid="stHorizontalBlock"]:has(.brand) [data-testid="stRadio"] [role="radiogroup"] label [data-testid="stMarkdownContainer"],
div[data-testid="stHorizontalBlock"]:has(.brand) [data-testid="stRadio"] [role="radiogroup"] label p{color:#E6F2EC!important;}
div[data-testid="stHorizontalBlock"]:has(.brand) [data-testid="stRadio"] [role="radiogroup"] label:hover{
 background:transparent!important;border-color:var(--sage)!important;color:#fff!important;}
div[data-testid="stHorizontalBlock"]:has(.brand) [data-testid="stRadio"] [role="radiogroup"] label:hover p{color:#fff!important;}
div[data-testid="stHorizontalBlock"]:has(.brand) [data-testid="stRadio"] [role="radiogroup"] label:has(input:checked){
 background:transparent!important;border-color:transparent!important;color:#fff!important;}
div[data-testid="stHorizontalBlock"]:has(.brand) [data-testid="stRadio"] [role="radiogroup"] label:has(input:checked) p{color:#fff!important;}
div[data-testid="stHorizontalBlock"]:has(.brand) [data-testid="stRadio"] [role="radiogroup"] label>div:first-child{display:none;}
div[data-testid="stHorizontalBlock"]:has(.brand) [data-testid="stPopover"] button{width:46px;height:46px;min-height:46px;padding:0;
 border-radius:50%;background:#D9EFD9;border:1px solid rgba(255,255,255,.65);color:var(--forest);font-weight:800;
 box-shadow:0 2px 8px rgba(18,48,35,.16);transition:background .18s ease,border-color .18s ease,box-shadow .18s ease;}
div[data-testid="stHorizontalBlock"]:has(.brand) [data-testid="stPopover"] button:hover{background:#EAF5E8;border-color:#fff;
 box-shadow:0 3px 10px rgba(18,48,35,.22);}
div[data-testid="stHorizontalBlock"]:has(.brand) [data-testid="stPopover"] button svg{display:none;}
div[data-testid="stHorizontalBlock"]:has(.brand) [data-testid="stPopover"] button p{margin:0;font-weight:800;}
div[data-testid="stHorizontalBlock"]:has(.brand) [data-testid="stPopover"] button:focus-visible{outline:2px solid #fff;outline-offset:2px;}
.account-card{display:flex;align-items:center;gap:.75rem;padding:.85rem 1rem;background:#F4F8F1;border:1px solid #DCE8D8;border-radius:12px;}
.account-avatar{width:42px;height:42px;display:grid;place-items:center;border-radius:50%;background:#D9EFD9;color:var(--forest);font-weight:800;}
.account-copy{display:flex;flex-direction:column;gap:.15rem;}
.account-copy strong{color:var(--ink);font-size:.96rem;}
.account-copy span{color:var(--muted);font-size:.82rem;}
.topbar-rule{height:1px;background:var(--line);margin:.5rem 0 1.6rem;}

/* widgets */
[data-testid="stBaseButton-primary"]{background:var(--forest);border:1px solid var(--forest);color:#fff;
 border-radius:999px;font-weight:600;padding:.55rem 1.4rem;}
[data-testid="stBaseButton-primary"]:hover{background:#244C3B;border-color:#244C3B;color:#fff;}
[data-testid="stBaseButton-secondary"]{background:#fff;border:1px solid var(--sage);color:var(--forest);
 border-radius:999px;font-weight:600;}
[data-testid="stBaseButton-secondary"]:hover{background:var(--mint);border-color:var(--leaf);color:var(--forest);}
div[data-baseweb="select"]>div,div[data-baseweb="input"]>div,[data-testid="stNumberInputContainer"]{
 background:#fff;border-radius:12px;border-color:var(--line);}
[data-testid="stExpander"]{background:#fff;border:1px solid var(--line);border-radius:14px;margin-bottom:1.1rem;}
[data-testid="stExpander"] details{border:none;}

/* typography */
.pt-title{font-family:'Fraunces',Georgia,serif;font-weight:600;font-size:2.3rem;line-height:1.15;color:var(--forest);margin:0;}
.pt-sub{color:var(--muted);margin:.35rem 0 1.6rem;max-width:62ch;font-size:1.02rem;}
.pt-h{font-family:'Fraunces',Georgia,serif;font-weight:600;font-size:1.3rem;color:var(--forest);margin:1.6rem 0 .5rem;}

/* cards */
.pt-card{background:var(--surface);border:1px solid var(--line);border-radius:18px;padding:1.15rem 1.3rem;margin-bottom:.5rem;}
.pt-card.mint{background:var(--mint);border-color:#CFE3CB;}
.row{display:flex;justify-content:space-between;align-items:flex-start;gap:1rem;}
.name{font-family:'Fraunces',Georgia,serif;font-weight:600;font-size:1.25rem;color:var(--ink);}
.meta{color:var(--muted);font-size:.85rem;margin-top:.15rem;}
.amt{font-family:'Fraunces',Georgia,serif;font-weight:600;font-size:1.4rem;color:var(--forest);text-align:right;}
.chip{display:inline-block;padding:.12rem .65rem;border-radius:999px;background:var(--mint);color:var(--forest);
 font-size:.78rem;font-weight:600;margin-right:.35rem;}
.chip.warn{background:var(--sand);color:var(--sandink);}
.blurb{color:var(--ink);margin:.7rem 0 .2rem;line-height:1.5;}
.status{margin-top:.5rem;padding:.65rem .9rem;background:var(--mint);border-radius:12px;font-size:.92rem;}
.status .sep{color:var(--muted);margin-left:.6rem;}
.result{display:flex;align-items:center;gap:.9rem;margin-top:.6rem;padding:.75rem 1rem;background:var(--mint);border-radius:14px;}
.result .ico{font-size:1.7rem;}
.result .r-n{font-family:'Fraunces',Georgia,serif;font-weight:600;font-size:1.35rem;color:var(--forest);line-height:1.1;}
.result .r-s{color:var(--muted);font-size:.82rem;}
.result .chip{margin-left:auto;margin-right:0;}
.note{color:var(--muted);font-size:.8rem;margin-top:.5rem;}

/* traceability ring */
.ring{width:var(--s);height:var(--s);border-radius:50%;flex:none;display:grid;place-items:center;
 background:conic-gradient(var(--forest) calc(var(--p) * 1%), #E1EBDD 0);}
.ring>div{width:calc(var(--s) - 20px);height:calc(var(--s) - 20px);border-radius:50%;background:#fff;display:grid;place-items:center;}
.ring span{font-family:'Fraunces',Georgia,serif;font-weight:600;font-size:calc(var(--s) * .3);color:var(--forest);}
.ring small{font-size:.5em;margin-left:1px;}

/* stepper */
.stepper{display:flex;margin:1.1rem 0 .3rem;}
.step{flex:1;text-align:center;position:relative;padding:0 .25rem;}
.step::before{content:"";position:absolute;top:13px;left:-50%;width:100%;height:2px;background:var(--line);z-index:1;}
.step:first-child::before{display:none;}
.step .dot{width:28px;height:28px;border-radius:50%;margin:0 auto;border:2px solid var(--sage);background:#fff;
 display:grid;place-items:center;font-size:.78rem;font-weight:600;color:var(--muted);position:relative;z-index:2;}
.step .lbl{font-size:.8rem;margin-top:.5rem;color:var(--ink);line-height:1.25;}
.step .when{font-size:.72rem;color:var(--muted);margin-top:.15rem;}
.step.done::before{background:var(--forest);}
.step.done .dot{background:var(--forest);border-color:var(--forest);color:#fff;}
.step.done.self::before{background:var(--sandline);}
.step.done.self .dot{background:var(--sand);border:2px dashed var(--sandline);color:var(--sandink);}
.step.now .dot{box-shadow:0 0 0 5px rgba(127,182,138,.35);animation:pulse 2.4s ease-in-out infinite;}
.step.pending .lbl{color:var(--muted);}
@keyframes pulse{0%,100%{box-shadow:0 0 0 4px rgba(127,182,138,.35);}50%{box-shadow:0 0 0 8px rgba(127,182,138,.12);}}
@media (prefers-reduced-motion:reduce){.step.now .dot{animation:none;}}

/* kpis + impact tiles */
.kpis,.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:.8rem;margin:.3rem 0 1rem;}
.kpi{background:#fff;border:1px solid var(--line);border-radius:16px;padding:.9rem 1.1rem;}
.kpi.lead{background:var(--mint);border-color:#CFE3CB;}
.k-l{color:var(--muted);font-size:.85rem;}
.k-v{font-family:'Fraunces',Georgia,serif;font-weight:600;font-size:1.75rem;color:var(--forest);line-height:1.2;margin-top:.15rem;}
.k-s{color:var(--muted);font-size:.8rem;margin-top:.1rem;}
.tiles{grid-template-columns:repeat(auto-fit,minmax(170px,1fr));}
.tile{background:#fff;border:1px solid var(--line);border-radius:16px;padding:.9rem 1.1rem;display:flex;gap:.8rem;align-items:center;}
.tile .ico{font-size:1.6rem;background:var(--mint);width:46px;height:46px;border-radius:14px;display:grid;place-items:center;flex:none;}
.tile .num{font-family:'Fraunces',Georgia,serif;font-weight:600;font-size:1.5rem;color:var(--forest);line-height:1.1;}
.tile .unit{color:var(--muted);font-size:.82rem;line-height:1.2;}
.story{background:var(--mint);border-radius:16px;padding:1rem 1.2rem;font-size:1.02rem;line-height:1.55;}

/* ledger table */
.ledger{width:100%;border-collapse:collapse;font-size:.85rem;}
.ledger th,.ledger td{padding:.5rem .6rem;border-bottom:1px solid var(--line);text-align:left;vertical-align:top;}
.ledger th{color:var(--muted);font-weight:600;}
.ledger code{background:var(--mint);padding:.05rem .35rem;border-radius:6px;font-size:.78rem;}

/* top navigation */
.brand{display:flex;align-items:center;width:100%;max-width:300px;margin:.2rem 0;}
.brand-logo{display:block;width:100%;height:auto;overflow:visible;}
.user{display:flex;align-items:center;gap:.7rem;background:#fff;border:1px solid var(--line);border-radius:14px;padding:.55rem .75rem;
 margin:.2rem 0 0 auto;width:max-content;transition:background .18s ease,border-color .18s ease;}
.user:hover{background:var(--mint);border-color:var(--leaf);}
.user .av{width:36px;height:36px;border-radius:50%;background:var(--sage);color:var(--forest);font-weight:700;display:grid;place-items:center;}
.user .n{font-weight:600;font-size:.92rem;}
.user .r{color:var(--muted);font-size:.78rem;}
.sync{display:flex;align-items:center;gap:.5rem;color:var(--muted);font-size:.8rem;margin-top:.15rem;}
.sync i{width:8px;height:8px;border-radius:50%;background:var(--leaf);display:inline-block;}
@media (max-width: 760px){
 .block-container{padding-top:1rem;}
 .brand .word{font-size:1.25rem;}
 [data-testid="stRadio"] [role="radiogroup"] label{padding:.4rem .6rem;font-size:.88rem;}
 div[data-testid="stHorizontalBlock"]:has(.brand) [data-testid="stRadio"] [role="radiogroup"]{justify-content:flex-start;}
 div[data-testid="stHorizontalBlock"]:has(.brand)>div[data-testid="column"]:nth-child(3){
  position:absolute;top:0;right:0;width:46px!important;min-width:46px!important;z-index:2;}
}
</style>
"""


def html(s: str) -> None:
    """Render an HTML snippet (lines are stripped so Markdown never sees code blocks)."""
    st.markdown(" ".join(line.strip() for line in s.strip().splitlines()), unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# Fictional organisations (renamed look-alikes of well-known charities)
# ----------------------------------------------------------------------------
@dataclass(frozen=True)
class Charity:
    id: str
    name: str
    cause: str
    country: str
    blurb: str
    rating: int          # traceability rating 0-100
    unit: str            # what one impact unit is
    icon: str
    cost: float          # CHF per impact unit
    partner: str         # local partner receiving the transfer
    supplier: str        # supplier paid by the partner
    purchase: str        # what is bought
    staff: str           # who is paid locally

    @property
    def traced_steps(self) -> int:
        """How many of the 6 steps carry linked, verifiable evidence."""
        if self.rating >= 90:
            return 6
        if self.rating >= 80:
            return 5
        if self.rating >= 70:
            return 4
        return 3

    @property
    def tier(self) -> str:
        if self.rating >= 90:
            return "Full trace"
        if self.rating >= 80:
            return "High trace"
        if self.rating >= 70:
            return "Partial trace"
        return "Limited trace"


CHARITIES = [
    Charity("dbb", "Doctors Beyond Borders", "Health", "Global",
            "Emergency medical care and vaccination campaigns in crisis regions.",
            94, "vaccinations", "💉", 6.5, "Nairobi Community Clinic", "MediPharm East Africa",
            "vaccines", "vaccination nurses"),
    Charity("crr", "Crimson Cross Relief", "Emergency aid", "Global",
            "Food, shelter and first aid after disasters and conflicts.",
            91, "food parcels", "📦", 28.0, "Beirut Relief Hub", "Levant Wholesale Foods",
            "food parcels", "distribution volunteers"),
    Charity("dhn", "Direct Hands", "Poverty relief", "East Africa",
            "Unconditional cash grants sent straight to families' mobile wallets.",
            96, "months of household income", "🏠", 45.0, "Kampala Mobile Wallet", "Uganda Mobile Money Ltd",
            "mobile-money credit", "field agents"),
    Charity("ucf", "Unity Children's Fund", "Children", "South Asia",
            "Schooling, nutrition and protection for children in vulnerable communities.",
            86, "school days", "🎒", 1.8, "Dhaka Learning Centres", "Bengal Books & Supplies",
            "school materials", "teachers"),
    Charity("wpf", "Wild Planet Fund", "Environment", "South America",
            "Reforestation and habitat protection with local cooperatives.",
            88, "trees planted", "🌳", 1.2, "Andes Reforestation Co-op", "Cusco Seedling Nursery",
            "tree seedlings", "planting crews"),
    Charity("rka", "Rescue Kids Alliance", "Children", "South-East Asia",
            "Daily meals and shelter for street-connected children.",
            79, "meals", "🍲", 0.9, "Manila Feeding Program", "Luzon Fresh Produce",
            "groceries", "kitchen staff"),
    Charity("awa", "Alpina Water Aid", "Water", "Horn of Africa",
            "Wells, pumps and sanitation for rural villages.",
            83, "people with clean water", "💧", 35.0, "Tigray Well Builders", "AquaPipe Trading",
            "pumps and pipes", "drilling technicians"),
    Charity("gwv", "Greenwave", "Climate", "West Africa",
            "Solar lighting and clean cooking for off-grid households.",
            68, "solar lamps", "💡", 14.0, "Lagos Solar Collective", "SunCell Manufacturing",
            "solar lamps", "installation crews"),
    Charity("nat", "Natura Alpina", "Environment", "Switzerland",
            "Restoring alpine meadows and wetlands across Swiss cantons.",
            77, "m² of habitat restored", "🌿", 0.6, "Engadin Habitat Trust", "Graubünden Native Seeds",
            "native seeds and materials", "rangers"),
    Charity("hpb", "Helping Paws Basel", "Animals", "Switzerland",
            "Veterinary care and rehoming for abandoned and injured animals.",
            72, "animals treated", "🐾", 55.0, "Basel Animal Clinic", "VetSupply AG",
            "veterinary supplies", "veterinary staff"),
]
CH = {c.id: c for c in CHARITIES}

STEP_SHORT = ["Donation", "Received", "Partner", "Purchase", "Payroll", "Impact"]
EVIDENCE_FILES = ["receipt", "confirmation", "transfer_contract", "invoice", "payroll", "field_report"]


def step_labels(c: Charity, impact: int) -> list[str]:
    return [
        "Donation made",
        f"Received by {c.name}",
        f"Transferred to {c.partner}",
        f"Bought {c.purchase}",
        f"Paid {c.staff}",
        f"Impact achieved: {impact:,} {c.unit}",
    ]


# ----------------------------------------------------------------------------
# Donations (session state)
# ----------------------------------------------------------------------------
@dataclass
class Donation:
    id: str
    charity_id: str
    amount: float
    method: str
    created: datetime
    times: list                     # 6 entries: datetime when the step happened, else None
    hashes: list                    # 6 fake ledger transaction hashes
    impact: int

    @property
    def stage(self) -> int:
        return sum(t is not None for t in self.times)

    @property
    def done(self) -> bool:
        return self.stage == 6


def fake_hash(rng: random.Random) -> str:
    return "0x" + f"{rng.getrandbits(256):064x}"


def short_hash(h: str) -> str:
    return f"{h[:8]}…{h[-6:]}"


def est_impact(c: Charity, amount: float) -> int:
    return max(1, round(amount / c.cost))


def build_donation(rng, now, did, c, amount, want_days_ago, stage, scale=1.0) -> Donation:
    offsets = [0, rng.uniform(0.02, 0.8), rng.uniform(1, 4), rng.uniform(3, 9), rng.uniform(5, 12), rng.uniform(10, 28)]
    cum, total = [], 0.0
    for o in offsets:
        total += o * scale
        cum.append(total)
    days_ago = max(want_days_ago, cum[stage - 1] + rng.uniform(0.3, 1.5))
    created = now - timedelta(days=days_ago)
    times = [created + timedelta(days=cum[i]) if i < stage else None for i in range(6)]
    return Donation(
        id=f"PT-{did}", charity_id=c.id, amount=float(amount),
        method=rng.choice(["Card", "TWINT", "Bank transfer", "USDC stablecoin"]),
        created=created, times=times, hashes=[fake_hash(rng) for _ in range(6)],
        impact=est_impact(c, amount),
    )


def seed_donations() -> list[Donation]:
    rng = random.Random(11)
    now = datetime.now().replace(microsecond=0)
    amounts = [20, 25, 30, 50, 50, 75, 100, 100, 150, 200, 250, 500]
    weights = [3, 3, 3, 2, 2, 2, 2, 2, 1, 1]
    out, did = [], 10001
    for _ in range(44):                                   # history, up to five years back
        days = 100 + (rng.random() ** 1.4) * 1700
        c = rng.choices(CHARITIES, weights=weights)[0]
        out.append(build_donation(rng, now, did, c, rng.choice(amounts), days, 6))
        did += 1
    for _ in range(4):                                    # recent, quickly completed
        c = rng.choices(CHARITIES, weights=weights)[0]
        out.append(build_donation(rng, now, did, c, rng.choice(amounts), rng.uniform(8, 80), 6, scale=0.35))
        did += 1
    active = [("dbb", 100, 1), ("crr", 250, 2), ("wpf", 50, 3), ("awa", 150, 4), ("dhn", 200, 5), ("rka", 75, 3)]
    for cid, amount, stage in active:                     # in progress
        out.append(build_donation(rng, now, did, CH[cid], amount, rng.uniform(0.1, 3), stage, scale=0.6))
        did += 1
    out.sort(key=lambda d: d.created, reverse=True)
    return out


def init_state() -> None:
    if "donations" not in st.session_state:
        st.session_state.donations = seed_donations()
        st.session_state.next_id = 10000 + len(st.session_state.donations) + 1
    st.session_state.setdefault("page", PAGES[0])
    st.session_state.setdefault("past_limit", 6)


def new_donation(c: Charity, amount: float, method: str) -> Donation:
    rng = random.Random()
    now = datetime.now().replace(microsecond=0)
    d = Donation(
        id=f"PT-{st.session_state.next_id}", charity_id=c.id, amount=float(amount), method=method,
        created=now, times=[now] + [None] * 5, hashes=[fake_hash(rng) for _ in range(6)],
        impact=est_impact(c, amount),
    )
    st.session_state.next_id += 1
    st.session_state.donations.insert(0, d)
    return d


def advance(d: Donation) -> None:
    if not d.done:
        d.times[d.stage] = datetime.now().replace(microsecond=0)


def goto(page: str) -> None:
    st.session_state["page"] = page


# ----------------------------------------------------------------------------
# Formatting helpers
# ----------------------------------------------------------------------------
def chf(x: float, dec: int = 0) -> str:
    return "CHF " + f"{x:,.{dec}f}".replace(",", "’")


def num(x: float) -> str:
    return f"{x:,.0f}".replace(",", "’")


def header(title: str, sub: str) -> None:
    html(f'<div class="pt-title">{title}</div><div class="pt-sub">{sub}</div>')


def section(title: str) -> None:
    html(f'<div class="pt-h">{title}</div>')


def kpis(items: list[tuple]) -> None:
    cards = "".join(
        f'<div class="kpi{" lead" if i == 0 else ""}"><div class="k-l">{l}</div><div class="k-v">{v}</div><div class="k-s">{s}</div></div>'
        for i, (l, v, s) in enumerate(items)
    )
    html(f'<div class="kpis">{cards}</div>')


def ring(score: int, size: int = 92) -> str:
    return f'<div class="ring" style="--p:{score};--s:{size}px"><div><span>{score}<small>%</small></span></div></div>'


def tier_chip(c: Charity) -> str:
    return f'<span class="chip{"" if c.rating >= 80 else " warn"}">{c.tier}</span>'


# ----------------------------------------------------------------------------
# Reusable visual blocks
# ----------------------------------------------------------------------------
def stepper(d: Donation) -> str:
    c = CH[d.charity_id]
    parts = []
    for i, label in enumerate(step_labels(c, d.impact)):
        if i < d.stage:
            cls = "done" if i < c.traced_steps else "done self"
            if i == d.stage - 1 and not d.done:
                cls += " now"
            when, dot = d.times[i].strftime("%d %b"), "✓"
        else:
            cls, when, dot = "pending", "Pending", str(i + 1)
        parts.append(f'<div class="step {cls}"><div class="dot">{dot}</div><div class="lbl">{label}</div><div class="when">{when}</div></div>')
    note = ""
    if c.traced_steps < d.stage:
        note = f'<div class="note">Dashed steps are reported by {c.name} without linked evidence.</div>'
    return f'<div class="stepper">{"".join(parts)}</div>{note}'


def donation_card(d: Donation) -> None:
    c = CH[d.charity_id]
    labels = step_labels(c, d.impact)
    if d.done:
        verified = c.traced_steps == 6
        chip = f'<span class="chip{"" if verified else " warn"}">{"Impact verified" if verified else "Impact reported by charity"}</span>'
        foot = (f'<div class="result"><span class="ico">{c.icon}</span><div><div class="r-n">{num(d.impact)} {c.unit}</div>'
                f'<div class="r-s">Impact achieved</div></div>{chip}</div>')
    else:
        foot = (f'<div class="status"><b>Now at step {d.stage} of 6:</b> {labels[d.stage - 1]}'
                f'<span class="sep">Next: {labels[d.stage]}</span></div>')
    html(f"""
    <div class="pt-card">
      <div class="row">
        <div><div class="name">{c.name}</div>
          <div class="meta">{d.id} · {d.created.strftime("%d %b %Y")} · paid by {d.method}</div></div>
        <div><div class="amt">{chf(d.amount)}</div><div style="text-align:right">{tier_chip(c)}</div></div>
      </div>
      {stepper(d)}
      {foot}
    </div>
    """)


def ledger_html(d: Donation) -> str:
    c = CH[d.charity_id]
    details = [
        f"{d.method}, {chf(d.amount)}",
        f"Credited to {c.name}",
        f"To {c.partner}",
        f"Supplier: {c.supplier}",
        f"Paid to {c.staff}",
        f"{num(d.impact)} {c.unit} " + ("confirmed by independent field check" if c.traced_steps == 6 else f"reported by {c.name}"),
    ]
    rows = []
    for i, label in enumerate(step_labels(c, d.impact)):
        if i >= d.stage:
            status, when, tx, ev = "Pending", "-", "-", "-"
        elif i < c.traced_steps:
            status = '<span class="chip">Verified on-chain</span>'
            when = d.times[i].strftime("%d %b %Y, %H:%M")
            tx = f"<code>{short_hash(d.hashes[i])}</code>"
            ev = f"{EVIDENCE_FILES[i]}_{d.id}.pdf"
        else:
            status = '<span class="chip warn">Reported by charity</span>'
            when = d.times[i].strftime("%d %b %Y, %H:%M")
            tx, ev = "-", "No evidence linked"
        rows.append(f"<tr><td>{i + 1}. {label}</td><td>{details[i]}</td><td>{status}</td><td>{when}</td><td>{tx}</td><td>{ev}</td></tr>")
    return ('<div style="overflow-x:auto"><table class="ledger"><tr><th>Step</th><th>Detail</th><th>Status</th>'
            '<th>Time</th><th>Ledger transaction</th><th>Evidence (off-chain, hash-linked)</th></tr>' + "".join(rows) + "</table></div>")


def render_donation(d: Donation, actions: bool = False) -> None:
    donation_card(d)
    if actions and not d.done:
        if st.button("Simulate next step", key=f"adv_{d.id}"):
            advance(d)
            st.rerun()
    with st.expander("Ledger and evidence"):
        html(ledger_html(d))


def style_fig(fig: go.Figure, height: int = 330) -> go.Figure:
    fig.update_layout(
        height=height, margin=dict(l=8, r=8, t=16, b=8), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Source Sans Pro, sans-serif", color="#20312A", size=13),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0), hoverlabel=dict(bgcolor="white"),
    )
    fig.update_xaxes(showgrid=False, linecolor=LINE)
    fig.update_yaxes(gridcolor="#E7EFE3", zeroline=False)
    return fig


# ----------------------------------------------------------------------------
# Pages
# ----------------------------------------------------------------------------
PAGES = ["Donate", "Active donations", "Past donations", "My impact"]


def page_donate() -> None:
    header("Donate with clarity",
           "Choose an organisation and amount, then follow verified progress through each stage of your donation.")
    left, right = st.columns([1, 1.1], gap="large")

    with left:
        causes = ["All causes"] + sorted({c.cause for c in CHARITIES})
        cause = st.selectbox("Cause", causes)
        pool = [c for c in sorted(CHARITIES, key=lambda x: -x.rating) if cause in ("All causes", c.cause)]
        cid = st.selectbox("Organisation", [c.id for c in pool],
                           format_func=lambda i: f"{CH[i].name}  ({CH[i].rating}% traceable)")
        c = CH[cid]
        preset = st.radio("Amount in CHF", [25, 50, 100, 250, 500, "Other"], index=2, horizontal=True)
        amount = (st.number_input("Your amount in CHF", min_value=5, max_value=100_000, value=100, step=5)
                  if preset == "Other" else preset)
        method = st.selectbox("Payment method", ["Card", "TWINT", "Bank transfer", "USDC stablecoin"])
        st.checkbox("Message me whenever my money reaches the next step", value=True)
        st.write("")
        if st.button(f"Donate {chf(amount)}", type="primary"):
            d = new_donation(c, amount, method)
            st.toast("Donation recorded on the ledger", icon="🌿")
            html(f"""
            <div class="pt-card mint">
              <div class="name">Thank you. Your donation is on its way.</div>
              <div class="meta">{d.id} · ledger transaction <code>{short_hash(d.hashes[0])}</code></div>
              <div class="blurb">{chf(amount)} to {c.name} is now step 1 of 6. You can follow every step from here.</div>
            </div>""")
            st.button("Track this donation", on_click=goto, args=("Active donations",))

    with right:
        est = est_impact(c, amount)
        mini = "".join(
            f'<div class="step done{"" if i < c.traced_steps else " self"}"><div class="dot">✓</div><div class="lbl">{s}</div></div>'
            for i, s in enumerate(STEP_SHORT)
        )
        html(f"""
        <div class="pt-card">
          <div class="row">
            <div><div class="name">{c.name}</div>
              <div style="margin-top:.4rem"><span class="chip">{c.cause}</span>{tier_chip(c)}</div>
              <div class="meta" style="margin-top:.4rem">Active in {c.country}</div></div>
            {ring(c.rating)}
          </div>
          <div class="blurb">{c.blurb}</div>
          <div class="pt-h" style="font-size:1.05rem;margin-top:1.1rem">What we can prove for this organisation</div>
          <div class="stepper" style="margin-top:.3rem">{mini}</div>
          <div class="note">Solid steps carry linked invoices, contracts or reports. Dashed steps are reported by the charity only.</div>
          <div class="status" style="margin-top:1rem"><b>{chf(amount)}</b> funds about <b>{num(est)} {c.unit}</b>
            <span class="sep">{chf(c.cost, 2)} per unit</span></div>
          <div class="note">Money flow: {c.name} to {c.partner}, who buy {c.purchase} from {c.supplier} and pay {c.staff}.</div>
        </div>""")

    section("How organisations compare on traceability")
    ranked = sorted(CHARITIES, key=lambda x: x.rating)
    fig = go.Figure(go.Bar(
        x=[x.rating for x in ranked], y=[x.name for x in ranked], orientation="h",
        marker_color=[FOREST if x.id == cid else SAGE for x in ranked],
        text=[f"{x.rating}%" for x in ranked], textposition="outside", cliponaxis=False,
        hovertemplate="%{y}: %{x}% of the donation is traceable<extra></extra>",
    ))
    fig.update_xaxes(range=[0, 108], visible=False)
    fig.update_yaxes(gridcolor="rgba(0,0,0,0)")
    st.plotly_chart(style_fig(fig, 380))


def page_active() -> None:
    header("Active donations", "Follow each donation from your payment to the final expense, step by step.")
    active = [d for d in st.session_state.donations if not d.done]
    if not active:
        st.info("Nothing is on its way right now. Make a donation and it will appear here.")
        return
    in_transit = sum(d.amount for d in active)
    expected = {}
    for d in active:
        expected[CH[d.charity_id].unit] = expected.get(CH[d.charity_id].unit, 0) + d.impact
    top = max(expected, key=expected.get)
    kpis([
        ("Still on its way", chf(in_transit), f"{len(active)} donations in progress"),
        ("Average progress", f"{sum(d.stage for d in active) / len(active):.1f} of 6 steps", "across active donations"),
        ("Impact expected", f"{num(expected[top])} {top}", f"largest expected result of {len(expected)} kinds"),
    ])
    c1, c2 = st.columns([1, 3])
    if c1.button("Fast-forward all by one step"):
        for d in active:
            advance(d)
        st.rerun()
    c2.caption("Demo control. In the live product, steps are written to the ledger when the organisation uploads evidence.")
    for d in active:
        render_donation(d, actions=True)


def page_past() -> None:
    header("Past donations", "Every completed donation, from your payment to the impact it created.")
    done = [d for d in st.session_state.donations if d.done]
    if not done:
        st.info("No donation has reached its final step yet.")
        return
    days = [(d.times[5] - d.created).days for d in done]
    verified = sum(CH[d.charity_id].traced_steps == 6 for d in done)
    kpis([
        ("Completed donations", num(len(done)), f"to {len({d.charity_id for d in done})} organisations"),
        ("Total given", chf(sum(d.amount for d in done)), "fully delivered"),
        ("Average time to impact", f"{sum(days) / len(days):.0f} days", "from payment to final result"),
        ("Verified impact", f"{verified / len(done):.0%}", "of donations with evidence at every step"),
    ])
    f1, f2 = st.columns(2)
    cause = f1.selectbox("Cause", ["All causes"] + sorted({CH[d.charity_id].cause for d in done}), key="past_cause")
    sort = f2.selectbox("Sort by", ["Newest first", "Oldest first", "Largest first"], key="past_sort")
    items = [d for d in done if cause == "All causes" or CH[d.charity_id].cause == cause]
    if sort == "Oldest first":
        items.sort(key=lambda d: d.created)
    elif sort == "Largest first":
        items.sort(key=lambda d: -d.amount)
    else:
        items.sort(key=lambda d: d.created, reverse=True)
    limit = st.session_state.past_limit
    for d in items[:limit]:
        render_donation(d)
    if len(items) > limit:
        st.button(f"Show more ({len(items) - limit} left)", on_click=lambda: st.session_state.update(past_limit=limit + 8))


def donations_df() -> pd.DataFrame:
    rows = []
    for d in st.session_state.donations:
        c = CH[d.charity_id]
        rows.append(dict(
            id=d.id, charity=c.name, cause=c.cause, amount=d.amount, created=d.created, date=d.created.date(),
            done=d.done, impact=d.impact, unit=c.unit, icon=c.icon, rating=c.rating,
            impact_date=d.times[5].date() if d.times[5] else None,
        ))
    return pd.DataFrame(rows)


def page_impact() -> None:
    header("My impact", "See what your giving has achieved over the period you choose.")
    choice = st.radio("Period", ["1M", "3M", "6M", "1Y", "5Y", "Custom"], index=3, horizontal=True,
                      label_visibility="collapsed", key="period")
    today = date.today()
    if choice == "Custom":
        a, b = st.columns(2)
        start = a.date_input("From", value=today - timedelta(days=365), min_value=date(2015, 1, 1), max_value=today)
        end = b.date_input("To", value=today, min_value=date(2015, 1, 1), max_value=today)
        if start > end:
            st.error("The start date must be before the end date.")
            return
    else:
        start = today - timedelta(days={"1M": 30, "3M": 91, "6M": 182, "1Y": 365, "5Y": 1826}[choice])
        end = today

    df = donations_df()
    sub = df[(df["date"] >= start) & (df["date"] <= end)].copy()
    if sub.empty:
        st.info("No donations in this period. Try a longer range.")
        return

    total = sub["amount"].sum()
    reached = sub.loc[sub["done"], "amount"].sum()
    pending = total - reached
    weighted = (sub["amount"] * sub["rating"]).sum() / total
    kpis([
        ("Donated", chf(total), f"{len(sub)} donations to {sub['charity'].nunique()} organisations"),
        ("Reached impact", chf(reached), f"{reached / total:.0%} of your giving"),
        ("Still on its way", chf(pending), f"{int((~sub['done']).sum())} donations in progress"),
        ("Traceable share", f"{weighted:.0f}%", "of the value, weighted by donation size"),
    ])

    section("What your giving became")
    units = (sub[sub["done"]].groupby(["icon", "unit"])["impact"].sum().reset_index().sort_values("impact", ascending=False))
    if units.empty:
        html('<div class="story">Nothing has reached its final step in this period yet. '
             'Impact appears here as soon as it is confirmed.</div>')
    else:
        tiles = "".join(
            f'<div class="tile"><div class="ico">{r.icon}</div><div><div class="num">{num(r.impact)}</div><div class="unit">{r.unit}</div></div></div>'
            for r in units.itertuples()
        )
        html(f'<div class="tiles">{tiles}</div>')
        top3 = ", ".join(f"{num(r.impact)} {r.unit}" for r in units.head(3).itertuples())
        more = " and more" if len(units) > 3 else ""
        html(f'<div class="story">Between {start:%d %b %Y} and {end:%d %b %Y}, {chf(reached)} of your giving became {top3}{more}.</div>')
    waiting = sub[~sub["done"]].groupby("unit")["impact"].sum().sort_values(ascending=False)
    if not waiting.empty:
        txt = ", ".join(f"{num(v)} {k}" for k, v in waiting.head(3).items())
        st.caption(f"Still expected from donations on their way: {txt}.")

    span = (end - start).days
    freq = "D" if span <= 35 else "W" if span <= 140 else "MS" if span <= 800 else "QS"
    tick = "%d %b" if freq in ("D", "W") else "%b %Y"

    c1, c2 = st.columns(2, gap="large")
    with c1:
        section("Giving over time")
        d = sub.copy()
        d["dt"] = pd.to_datetime(d["created"])
        d["status"] = d["done"].map({True: "Reached impact", False: "On its way"})
        g = (d.groupby([pd.Grouper(key="dt", freq=freq), "status"])["amount"].sum().unstack(fill_value=0)
             .reindex(columns=["Reached impact", "On its way"], fill_value=0))
        fig = go.Figure()
        for col, color in [("Reached impact", FOREST), ("On its way", SAGE)]:
            fig.add_bar(x=g.index, y=g[col], name=col, marker_color=color,
                        hovertemplate="%{x|" + tick + "}: CHF %{y:,.0f}<extra>" + col + "</extra>")
        fig.update_layout(barmode="stack", bargap=0.35)
        fig.update_xaxes(tickformat=tick)
        fig.update_yaxes(title="CHF")
        st.plotly_chart(style_fig(fig), use_container_width=True)
    with c2:
        section("By cause")
        by_cause = sub.groupby("cause")["amount"].sum().sort_values(ascending=False)
        fig = go.Figure(go.Pie(labels=by_cause.index, values=by_cause.values, hole=0.62, sort=False,
                               marker=dict(colors=CHART_COLORS, line=dict(color="#F8F9F4", width=2)),
                               textinfo="percent", hovertemplate="%{label}: CHF %{value:,.0f}<extra></extra>"))
        fig.add_annotation(text=f"<b>{chf(total)}</b>", showarrow=False, font=dict(size=15, color=FOREST))
        fig.update_layout(showlegend=True, legend=dict(orientation="v", x=1.0))
        st.plotly_chart(style_fig(fig), use_container_width=True)

    c3, c4 = st.columns(2, gap="large")
    with c3:
        section("By organisation")
        by_org = sub.groupby(["charity", "rating"])["amount"].sum().reset_index().sort_values("amount")
        fig = go.Figure(go.Bar(
            x=by_org["amount"], y=[f"{n} ({r}%)" for n, r in zip(by_org["charity"], by_org["rating"])], orientation="h",
            marker_color=[FOREST if r >= 90 else LEAF if r >= 80 else SAGE if r >= 70 else SAND for r in by_org["rating"]],
            text=[chf(v) for v in by_org["amount"]], textposition="outside", cliponaxis=False,
            hovertemplate="%{y}: CHF %{x:,.0f}<extra></extra>"))
        fig.update_xaxes(visible=False, range=[0, by_org["amount"].max() * 1.35])
        fig.update_yaxes(gridcolor="rgba(0,0,0,0)")
        st.plotly_chart(style_fig(fig), use_container_width=True)
        st.caption("Traceability rating in brackets. Darker green means more of the journey can be proven.")
    with c4:
        section("Donated versus reached impact")
        last_impact = max([x for x in sub["impact_date"].dropna()], default=end)
        idx = pd.date_range(start, min(today, max(end, last_impact)), freq="D")
        keys = idx.date
        donated = sub.groupby("date")["amount"].sum().reindex(keys, fill_value=0).cumsum()
        landed = sub[sub["done"]].groupby("impact_date")["amount"].sum().reindex(keys, fill_value=0).cumsum()
        fig = go.Figure()
        fig.add_scatter(x=idx, y=donated.values, name="Donated", mode="lines", line=dict(color=LEAF, width=2),
                        fill="tozeroy", fillcolor="rgba(191,221,190,.55)")
        fig.add_scatter(x=idx, y=landed.values, name="Reached impact", mode="lines", line=dict(color=FOREST, width=2.5),
                        fill="tozeroy", fillcolor="rgba(46,94,74,.35)")
        fig.update_yaxes(title="CHF, cumulative")
        st.plotly_chart(style_fig(fig), use_container_width=True)
        st.caption("The gap between the two lines is money that is still moving through the process.")


# ----------------------------------------------------------------------------
# App shell
# ----------------------------------------------------------------------------
def main() -> None:
    st.markdown(CSS.replace("\n", " "), unsafe_allow_html=True)
    init_state()
    block = 19_400_000 + int((datetime.now() - datetime(2026, 1, 1)).total_seconds() // 12)

    brand_col, nav_col, account_col = st.columns([2.6, 5.0, 0.65])
    with brand_col:
        html('<div class="brand"><svg class="brand-logo" viewBox="0 0 1200 250" role="img" aria-label="PhilanTrace">'
             '<path d="M112 218C64 203 31 169 28 125c48-20 99-5 125 33-4 29-18 49-41 60Z" fill="#A5E98D"/>'
             '<path d="M124 201C102 128 120 59 183 20c40 47 46 112 12 161-18 19-42 27-71 20Z" fill="#48C4B5"/>'
             '<path d="M139 216c17-59 59-101 119-116 2 62-27 111-78 136-17 3-31-4-41-20Z" fill="#32AFC0"/>'
             '<path d="M45 214c19-56 67-92 116-102 35-7 57-30 70-69" fill="none" stroke="#F5F6EC" '
             'stroke-width="8" stroke-linecap="round"/><circle cx="45" cy="214" r="12" fill="#8DE9A2"/>'
             '<circle cx="231" cy="43" r="12" fill="#F5F6EC"/>'
             '<text x="275" y="180" font-family="Manrope, sans-serif" font-size="136" font-weight="800">'
             '<tspan fill="#F5F6EF">Philan</tspan><tspan fill="#83E8A1">Trace</tspan></text></svg></div>')
    with nav_col:
        page = st.radio("Navigation", PAGES, key="page", horizontal=True, label_visibility="collapsed")
    with account_col:
        with st.popover("AM", help="Open profile"):
            html('<div class="account-card"><div class="account-avatar">AM</div><div class="account-copy">'
                 '<strong>Alex Muster</strong><span>Individual donor</span></div></div>')

    html(f'<div class="sync"><i></i>Ledger synced, block {block:,}</div>'.replace(",", "’"))
    html('<div class="topbar-rule"></div>')

    {"Donate": page_donate, "Active donations": page_active,
    "Past donations": page_past, "My impact": page_impact}[page]()
    st.caption("Demo with fictional organisations and data.")


main()