"""Soft light/dark palettes and the CSS for the Streamlit interface.

The app switches theme by swapping the CSS variables below; every custom
component and the restyled Streamlit widgets read from these variables.
"""

LIGHT = {
    "bg": "#F7F5F2", "surface": "#FFFFFF", "surface2": "#F2EFEA",
    "text": "#2F2B36", "muted": "#77707F", "border": "#E7E2DB",
    "accent": "#7566C3", "accent-soft": "#ECE8FA", "button-text": "#FFFFFF",
    "sage": "#5E9E87", "sage-soft": "#E3F2EC",
    "peach": "#D98B6C", "peach-soft": "#FCEBE3",
    "sky": "#5F93C4", "sky-soft": "#E4EFF9",
    "rose": "#CC7690", "rose-soft": "#FBE7ED",
    "shadow": "0 1px 2px rgba(47,43,54,.04), 0 6px 20px rgba(47,43,54,.06)",
}

DARK = {
    "bg": "#1B1A21", "surface": "#24232C", "surface2": "#2D2C36",
    "text": "#ECE9F2", "muted": "#A39EAE", "border": "#383642",
    "accent": "#A99BF0", "accent-soft": "#363150", "button-text": "#1B1A21",
    "sage": "#8FCBB6", "sage-soft": "#233730",
    "peach": "#F2B49B", "peach-soft": "#3D2D27",
    "sky": "#9CC3E8", "sky-soft": "#233243",
    "rose": "#EDA9BD", "rose-soft": "#3D2731",
    "shadow": "0 1px 2px rgba(0,0,0,.3), 0 6px 20px rgba(0,0,0,.25)",
}


def variables(dark: bool) -> str:
    palette = DARK if dark else LIGHT
    body = ";".join(f"--{k}:{v}" for k, v in palette.items())
    return f"<style>:root{{{body};color-scheme:{'dark' if dark else 'light'}}}</style>"


CSS = """
<style>
/* ---------- app shell ---------- */
.stApp, [data-testid="stAppViewContainer"] { background: var(--bg); color: var(--text); transition: background .25s ease; }
[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 2.2rem; max-width: 1200px; }
.stApp p, .stApp li, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4 { color: var(--text); }

/* ---------- action buttons ---------- */
[data-testid="stButton"] > button {
  min-height: 2.7rem; padding: .55rem 1rem; border: 1px solid transparent !important;
  border-radius: 11px !important; background: var(--accent) !important;
  color: var(--button-text) !important; font-weight: 700 !important;
  box-shadow: var(--shadow); transition: transform .15s ease, box-shadow .15s ease, filter .15s ease;
}
[data-testid="stButton"] > button p, [data-testid="stButton"] > button span {
  color: var(--button-text) !important;
}
[data-testid="stButton"] > button:hover {
  filter: brightness(1.08); transform: translateY(-1px);
  box-shadow: 0 5px 14px rgba(0, 0, 0, .16);
}
[data-testid="stButton"] > button:focus-visible {
  outline: 3px solid var(--sky) !important; outline-offset: 2px;
}

/* ---------- sidebar ---------- */
section[data-testid="stSidebar"] { background: var(--surface); border-right: 1px solid var(--border); }
section[data-testid="stSidebar"] p, [data-testid="stWidgetLabel"] p { color: var(--text) !important; }
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p { color: var(--muted) !important; }
[data-testid="stSidebarCollapseButton"] *, [data-testid="stExpandSidebarButton"] * { color: var(--muted) !important; }

/* multiselect (react-aria combobox) */
[data-testid="stMultiSelect"] .react-aria-ComboBox > div[role="group"] { background: var(--surface2) !important;
  border-color: var(--border) !important; border-radius: 12px !important; }
[data-testid="stMultiSelect"] input { color: var(--text) !important; }
[data-testid="stMultiSelect"] input::placeholder { color: var(--muted) !important; }
[data-testid="stMultiSelect"] button svg { color: var(--muted) !important; fill: var(--muted) !important; }
[data-testid="stMultiSelect"] span[data-tag] { background: var(--accent-soft) !important; color: var(--text) !important;
  border-radius: 8px !important; }
[data-testid="stMultiSelect"] span[data-tag] span { color: var(--text) !important; }
[data-testid="stMultiSelect"] span[data-tag] button svg { color: var(--text) !important; fill: var(--text) !important; }
.react-aria-Popover, [role="listbox"] { background: var(--surface) !important; border-color: var(--border) !important; }
[role="listbox"] [role="option"] { color: var(--text) !important; background: transparent !important; }
[role="listbox"] [role="option"][data-focused], [role="listbox"] [role="option"]:hover { background: var(--surface2) !important; }

/* tabs */
[role="tablist"] { gap: 1.6rem; }
[data-testid="stTab"] p { color: var(--muted) !important; font-weight: 600; font-size: .95rem; }
[data-testid="stTab"][aria-selected="true"] p { color: var(--accent) !important; }
[data-testid="stTab"] .react-aria-SelectionIndicator { background: var(--accent) !important; }

/* expander */
[data-testid="stExpander"] details { background: var(--surface); border: 1px solid var(--border) !important; border-radius: 14px; }
[data-testid="stExpander"] summary, [data-testid="stExpander"] summary * { color: var(--text) !important; }

/* alerts */
[data-testid="stAlert"] { border-radius: 14px; }

/* ---------- custom components ---------- */
.hero { background: linear-gradient(135deg, var(--accent-soft), var(--sky-soft) 55%, var(--sage-soft));
  border: 1px solid var(--border); border-radius: 22px; padding: 1.8rem 2rem; margin-bottom: 1.4rem; }
.hero .eyebrow { font-size: .85rem; color: var(--muted); font-weight: 600; }
.hero h1 { font-size: 2.1rem; font-weight: 800; margin: .3rem 0 .4rem; color: var(--text); letter-spacing: -.02em; padding: 0; }
.hero p { color: var(--muted) !important; margin: 0 0 1rem; max-width: 46rem; }

.chips { display: flex; flex-wrap: wrap; gap: .4rem; }
.chip { display: inline-flex; align-items: center; gap: .35rem; padding: .28rem .7rem; border-radius: 999px;
  font-size: .82rem; font-weight: 600; background: var(--surface); color: var(--text); border: 1px solid var(--border); }
.chip.accent { background: var(--accent-soft); border-color: transparent; }
.chip.sage { background: var(--sage-soft); color: var(--sage); border-color: transparent; }
.chip.rose { background: var(--rose-soft); color: var(--rose); border-color: transparent; }
.chip small { font-weight: 500; opacity: .75; }

.metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 1.6rem; }
.metric { background: var(--surface); border: 1px solid var(--border); border-radius: 18px; padding: 1.1rem 1.25rem;
  box-shadow: var(--shadow); position: relative; overflow: hidden; }
.metric::before { content: ""; position: absolute; inset: 0 auto 0 0; width: 4px; background: var(--tone); }
.metric .label { font-size: .8rem; color: var(--muted); font-weight: 600; }
.metric .value { font-size: 1.9rem; font-weight: 800; color: var(--text); line-height: 1.2; margin-top: .2rem; }
.metric .sub { font-size: .8rem; color: var(--muted); }

.section-title { font-size: 1.15rem; font-weight: 700; color: var(--text); margin: 1.4rem 0 .8rem; }
.section-note { color: var(--muted); font-size: .88rem; margin: -.5rem 0 .9rem; }

.months { display: grid; grid-template-columns: repeat(auto-fill, minmax(270px, 1fr)); gap: 1rem; }
.month { background: var(--surface); border: 1px solid var(--border); border-radius: 18px; padding: 1.1rem;
  box-shadow: var(--shadow); display: flex; flex-direction: column; gap: .65rem; }
[data-testid="stColumn"]:has(.month) [data-testid="stButton"] { margin-top: .55rem; }
.month-head { display: flex; justify-content: space-between; align-items: baseline; }
.month-name { font-weight: 700; font-size: 1.05rem; color: var(--text); }
.month-hours { font-size: .82rem; color: var(--muted); font-weight: 600; }
.bar { height: 8px; background: var(--surface2); border-radius: 99px; overflow: hidden; }
.bar > div { height: 100%; border-radius: 99px; background: linear-gradient(90deg, var(--accent), var(--sky)); }

.act { border-radius: 12px; padding: .7rem .8rem; background: var(--surface2); border-left: 4px solid var(--tone); }
.act-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: .25rem; }
.act-name { font-weight: 650; color: var(--text); font-size: .93rem; }
.act-meta { color: var(--muted); font-size: .8rem; margin-top: .15rem; }
.act-val { font-weight: 700; font-size: .82rem; color: var(--tone); }
.pill { font-size: .74rem; font-weight: 700; padding: .15rem .55rem;
  border-radius: 6px; background: var(--tone-soft); color: var(--tone); }
.empty { color: var(--muted); font-size: .85rem; text-align: center; padding: 1rem; border: 1px dashed var(--border); border-radius: 12px; }

.t-course { --tone: var(--sky); --tone-soft: var(--sky-soft); }
.t-project { --tone: var(--sage); --tone-soft: var(--sage-soft); }
.t-internship { --tone: var(--peach); --tone-soft: var(--peach-soft); }
.t-accent { --tone: var(--accent); --tone-soft: var(--accent-soft); }
.t-rose { --tone: var(--rose); --tone-soft: var(--rose-soft); }
.t-muted { --tone: var(--muted); --tone-soft: var(--surface2); }

.legend { display: flex; gap: 1rem; flex-wrap: wrap; margin: -.3rem 0 1rem; font-size: .82rem; color: var(--muted); }
.legend span { display: inline-flex; align-items: center; gap: .35rem; }
.dot { width: 10px; height: 10px; border-radius: 50%; background: var(--tone); display: inline-block; }

.list { background: var(--surface); border: 1px solid var(--border); border-radius: 18px; box-shadow: var(--shadow); overflow: hidden; }
.row { display: grid; grid-template-columns: 4.5rem 1fr auto; gap: .8rem; align-items: center; padding: .8rem 1.1rem;
  border-bottom: 1px solid var(--border); }
.row:last-child { border-bottom: none; }
.row:hover { background: var(--surface2); }
.row .id { font-weight: 700; color: var(--muted); font-size: .82rem; }
.row .main { color: var(--text); font-weight: 600; font-size: .92rem; }
.row .sub { color: var(--muted); font-size: .8rem; font-weight: 500; margin-top: .15rem; }
.row .right { font-weight: 700; color: var(--text); font-size: .9rem; white-space: nowrap; }
.reason { max-width: 20rem; padding: .35rem .65rem; border-radius: 7px; text-align: center;
  font-size: .68rem; line-height: 1.35; font-weight: 800; letter-spacing: .035em; text-transform: uppercase; }
.reason.t-rose { background: var(--rose-soft); color: var(--rose); }
.reason.t-peach { background: var(--peach-soft); color: var(--peach); }
.reason.t-sage { background: var(--sage-soft); color: var(--sage); }
.reason.t-muted { background: var(--surface2); color: var(--muted); }

.trace { font-family: ui-monospace, 'Cascadia Code', Consolas, monospace; font-size: .82rem; line-height: 1.7; }
.trace .take { color: var(--sage); } .trace .skip { color: var(--muted); }

.test { background: var(--surface); border: 1px solid var(--border); border-radius: 18px; padding: 1rem 1.2rem;
  box-shadow: var(--shadow); margin-bottom: .9rem; }
.test h4 { margin: 0 0 .5rem; font-size: 1rem; font-weight: 700; color: var(--text); padding: 0; }
.check { display: flex; gap: .6rem; align-items: flex-start; font-size: .88rem; color: var(--text); padding: .2rem 0; }
.check .mark { flex: none; width: 1.3rem; height: 1.3rem; border-radius: 50%; display: grid; place-items: center;
  font-size: .75rem; font-weight: 800; background: var(--tone-soft); color: var(--tone); }
.banner { border-radius: 14px; padding: .8rem 1.1rem; font-weight: 700; background: var(--tone-soft); color: var(--tone); margin-bottom: 1rem; }

.brand { font-weight: 800; font-size: 1.15rem; color: var(--text); margin-bottom: .1rem; }
.brand-sub { color: var(--muted); font-size: .82rem; margin-bottom: 1rem; }
/* ---------- roadmap guide ---------- */
.act-head { display: flex; justify-content: space-between; align-items: center; gap: .6rem; flex-wrap: wrap; }
.act-title { font-weight: 750; font-size: 1.08rem; color: var(--text); margin: .35rem 0 .15rem; }
.act-sub { color: var(--muted); font-size: .85rem; margin-bottom: .6rem; }
.callout { border-left: 4px solid var(--tone); background: var(--tone-soft); border-radius: 10px; padding: .6rem .85rem;
  font-size: .9rem; color: var(--text); margin: .4rem 0 .7rem; }
.callout b { color: var(--tone); }
.block-label { font-weight: 700; font-size: .92rem; color: var(--text); margin: .7rem 0 .2rem; }
.hint { color: var(--muted); font-size: .85rem; }
.mini { display: flex; justify-content: space-between; gap: .5rem; font-size: .85rem; color: var(--text); padding: .15rem 0; }
.mini span:last-child { color: var(--muted); white-space: nowrap; }
.tag { font-size: .72rem; font-weight: 700; padding: .12rem .5rem; border-radius: 6px; background: var(--tone-soft); color: var(--tone); white-space: nowrap; }
.row.compact { grid-template-columns: 4.5rem 1fr auto auto; }
[data-testid="stVerticalBlockBorderWrapper"] { border-color: var(--border) !important; background: var(--surface); border-radius: 16px !important; }

@media (max-width: 720px) {
  .row, .row.compact { grid-template-columns: 3rem minmax(0, 1fr); gap: .45rem .7rem; padding: .8rem; }
  .row .reason, .row .tag, .row .right { grid-column: 2; justify-self: start; }
  .reason { max-width: 100%; text-align: left; }
}
</style>
"""
