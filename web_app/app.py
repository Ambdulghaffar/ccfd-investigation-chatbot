# web_app/app.py
"""
Semaine 4 — Interface Graphique : Chatbot d'Investigation Anti-Fraude CCFD
Auteur : Projet Master S3 Sécurité
"""

import json
import os
import sys
import time
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

DATA_DIR = ROOT / "data"
RESULTS_S2 = ROOT / "results" / "semaine2"
RESULTS_S3 = ROOT / "results" / "semaine3"

from src.chat_history import ChatHistory
from src.chatbot import ChatbotInvestigation
from src.context_manager import InvestigationState

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CCFD — Chatbot Anti-Fraude",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS Premium ───────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
/* ── Imports ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background: #050b18 !important;
    font-family: 'Inter', sans-serif !important;
    color: #e2e8f0 !important;
}

/* hide default header/footer */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem 2rem 2rem !important; max-width: 100% !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1b2a 0%, #0a1628 100%) !important;
    border-right: 1px solid rgba(59,130,246,0.15) !important;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stSelectbox div,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span { color: #cbd5e1 !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(15, 23, 42, 0.8) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    gap: 4px !important;
    border: 1px solid rgba(59,130,246,0.2) !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    padding: 8px 20px !important;
    color: #94a3b8 !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
    transition: all 0.2s ease !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #1e40af, #3b82f6) !important;
    color: #ffffff !important;
    box-shadow: 0 0 20px rgba(59,130,246,0.4) !important;
}
[data-testid="stTabsContent"] {
    background: transparent !important;
    padding-top: 1.5rem !important;
}

/* ── Cards ── */
.glass-card {
    background: rgba(15, 23, 42, 0.7);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(59, 130, 246, 0.15);
    border-radius: 16px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
}
.metric-card {
    background: linear-gradient(135deg, rgba(15,23,42,0.9) 0%, rgba(17,24,39,0.9) 100%);
    border: 1px solid rgba(59,130,246,0.2);
    border-radius: 14px;
    padding: 1.1rem 1.2rem;
    text-align: center;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.metric-card:hover { transform: translateY(-2px); box-shadow: 0 8px 32px rgba(59,130,246,0.15); }
.metric-card .val { font-size: 2rem; font-weight: 800; }
.metric-card .lbl { font-size: 0.75rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 2px; }

/* ── Transaction card ── */
.tx-card {
    background: linear-gradient(135deg, rgba(15,23,42,0.95) 0%, rgba(17,24,39,0.95) 100%);
    border-radius: 16px;
    padding: 1.4rem;
    border: 1px solid rgba(59,130,246,0.2);
    box-shadow: 0 4px 24px rgba(0,0,0,0.4);
}
.tx-id { font-size: 0.7rem; color: #475569; letter-spacing: 0.12em; text-transform: uppercase; }
.tx-amount { font-size: 2.2rem; font-weight: 800; color: #f1f5f9; line-height: 1.1; }
.tx-src { font-size: 0.8rem; color: #64748b; }
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}
.badge-high { background: rgba(239,68,68,0.15); color: #f87171; border: 1px solid rgba(239,68,68,0.3); }
.badge-medium { background: rgba(245,158,11,0.15); color: #fbbf24; border: 1px solid rgba(245,158,11,0.3); }
.badge-low { background: rgba(34,197,94,0.15); color: #4ade80; border: 1px solid rgba(34,197,94,0.3); }
.badge-fraud { background: rgba(239,68,68,0.2); color: #f87171; border: 1px solid rgba(239,68,68,0.4); }
.badge-legit { background: rgba(34,197,94,0.2); color: #4ade80; border: 1px solid rgba(34,197,94,0.4); }
.badge-unknown { background: rgba(100,116,139,0.2); color: #94a3b8; border: 1px solid rgba(100,116,139,0.3); }

/* ── Chat bubbles ── */
.chat-area {
    max-height: 460px;
    overflow-y: auto;
    padding: 0.5rem 0.2rem;
    display: flex;
    flex-direction: column;
    gap: 0.7rem;
    scrollbar-width: thin;
    scrollbar-color: rgba(59,130,246,0.3) transparent;
}
.chat-area::-webkit-scrollbar { width: 4px; }
.chat-area::-webkit-scrollbar-thumb { background: rgba(59,130,246,0.3); border-radius: 4px; }

.bubble-bot {
    background: linear-gradient(135deg, rgba(30,64,175,0.25) 0%, rgba(59,130,246,0.15) 100%);
    border: 1px solid rgba(59,130,246,0.3);
    border-radius: 0 14px 14px 14px;
    padding: 0.85rem 1rem;
    max-width: 85%;
    align-self: flex-start;
    position: relative;
}
.bubble-user {
    background: linear-gradient(135deg, rgba(17,24,39,0.9) 0%, rgba(30,41,59,0.9) 100%);
    border: 1px solid rgba(148,163,184,0.15);
    border-radius: 14px 0 14px 14px;
    padding: 0.85rem 1rem;
    max-width: 75%;
    align-self: flex-end;
    text-align: right;
}
.bubble-label { font-size: 0.65rem; color: #475569; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.1em; }
.bubble-text { font-size: 0.9rem; line-height: 1.5; color: #e2e8f0; }
.bubble-decision-fraud {
    background: linear-gradient(135deg, rgba(239,68,68,0.2) 0%, rgba(185,28,28,0.15) 100%);
    border: 1px solid rgba(239,68,68,0.4);
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
}
.bubble-decision-legit {
    background: linear-gradient(135deg, rgba(34,197,94,0.2) 0%, rgba(21,128,61,0.15) 100%);
    border: 1px solid rgba(34,197,94,0.4);
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
}

/* ── Signal tags ── */
.signal-fraud { background: rgba(239,68,68,0.1); color: #f87171; border: 1px solid rgba(239,68,68,0.25); border-radius: 20px; padding: 2px 8px; font-size: 0.72rem; display: inline-block; margin: 2px; }
.signal-legit { background: rgba(34,197,94,0.1); color: #4ade80; border: 1px solid rgba(34,197,94,0.25); border-radius: 20px; padding: 2px 8px; font-size: 0.72rem; display: inline-block; margin: 2px; }
.signal-none { color: #475569; font-size: 0.8rem; font-style: italic; }

/* ── Verdict box ── */
.verdict-fraud {
    background: linear-gradient(135deg, rgba(239,68,68,0.15), rgba(185,28,28,0.1));
    border: 2px solid rgba(239,68,68,0.5);
    border-radius: 20px;
    padding: 2rem;
    text-align: center;
    box-shadow: 0 0 40px rgba(239,68,68,0.2);
    animation: glowRed 2s ease-in-out infinite alternate;
}
.verdict-legit {
    background: linear-gradient(135deg, rgba(34,197,94,0.15), rgba(21,128,61,0.1));
    border: 2px solid rgba(34,197,94,0.5);
    border-radius: 20px;
    padding: 2rem;
    text-align: center;
    box-shadow: 0 0 40px rgba(34,197,94,0.2);
    animation: glowGreen 2s ease-in-out infinite alternate;
}
.verdict-emoji { font-size: 3.5rem; margin-bottom: 0.5rem; }
.verdict-title { font-size: 2rem; font-weight: 800; margin-bottom: 0.3rem; }
.verdict-conf { font-size: 1rem; color: #94a3b8; margin-bottom: 1rem; }
.verdict-just { font-size: 0.88rem; color: #cbd5e1; line-height: 1.6; }

@keyframes glowRed {
    from { box-shadow: 0 0 20px rgba(239,68,68,0.15); }
    to   { box-shadow: 0 0 50px rgba(239,68,68,0.35); }
}
@keyframes glowGreen {
    from { box-shadow: 0 0 20px rgba(34,197,94,0.15); }
    to   { box-shadow: 0 0 50px rgba(34,197,94,0.35); }
}

/* ── Progress / gauge bar ── */
.gauge-wrap { margin: 0.6rem 0; }
.gauge-label { display: flex; justify-content: space-between; font-size: 0.75rem; color: #64748b; margin-bottom: 4px; }
.gauge-bar { height: 8px; border-radius: 4px; background: rgba(30,41,59,0.8); overflow: hidden; }
.gauge-fill { height: 100%; border-radius: 4px; transition: width 0.5s ease; }

/* ── Section titles ── */
.section-title {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #475569;
    margin-bottom: 0.5rem;
    padding-bottom: 4px;
    border-bottom: 1px solid rgba(59,130,246,0.1);
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #1e40af, #3b82f6) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 0.6rem 1.4rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 15px rgba(59,130,246,0.3) !important;
    width: 100% !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(59,130,246,0.45) !important;
}

/* ── Input ── */
.stTextInput input, .stChatInput textarea {
    background: rgba(15,23,42,0.8) !important;
    border: 1px solid rgba(59,130,246,0.3) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', sans-serif !important;
}

/* ── Selectbox ── */
.stSelectbox [data-testid="stWidgetLabel"] { color: #94a3b8 !important; font-size: 0.8rem !important; }
.stSelectbox > div > div {
    background: rgba(15,23,42,0.8) !important;
    border: 1px solid rgba(59,130,246,0.25) !important;
    border-radius: 8px !important;
    color: #e2e8f0 !important;
}

/* ── Transcript ── */
.transcript-line-bot { color: #93c5fd; font-size: 0.82rem; margin: 6px 0; }
.transcript-line-user { color: #94a3b8; font-size: 0.82rem; margin: 6px 0 6px 20px; }

/* ── Plotly ── */
.js-plotly-plot { border-radius: 14px; overflow: hidden; }

/* ── Spinner ── */
[data-testid="stSpinner"] { color: #3b82f6 !important; }
</style>
""",
    unsafe_allow_html=True,
)

# ══════════════════════════════════════════════════════════════════════════════
# HELPERS — UI
# ══════════════════════════════════════════════════════════════════════════════

def _badge_risk(level: str) -> str:
    m = {"HIGH": "badge-high", "MEDIUM": "badge-medium", "LOW": "badge-low"}
    return f'<span class="badge {m.get(level, "badge-low")}">{level}</span>'


def _badge_truth(is_fraud) -> str:
    if is_fraud == 1:
        return '<span class="badge badge-fraud">⚠ Fraude</span>'
    elif is_fraud == 0:
        return '<span class="badge badge-legit">✓ Légitime</span>'
    return '<span class="badge badge-unknown">? Inconnu</span>'


def _confidence_bar(label: str, value: int, color: str) -> str:
    pct = min(100, max(0, value))
    return f"""
<div class="gauge-wrap">
  <div class="gauge-label"><span>{label}</span><span>{pct}%</span></div>
  <div class="gauge-bar">
    <div class="gauge-fill" style="width:{pct}%;background:{color};"></div>
  </div>
</div>"""


def _signal_tags(signals: list, css: str) -> str:
    if not signals:
        return '<span class="signal-none">Aucun signal détecté</span>'
    return " ".join(f'<span class="{css}">{s}</span>' for s in signals)


def _chat_bubble_bot(text: str) -> str:
    return f"""
<div class="bubble-bot">
  <div class="bubble-label">🤖 Analyste IA</div>
  <div class="bubble-text">{text}</div>
</div>"""


def _chat_bubble_user(text: str) -> str:
    return f"""
<div class="bubble-user">
  <div class="bubble-label">Vous</div>
  <div class="bubble-text">{text}</div>
</div>"""


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS — DATA
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(show_spinner=False)
def load_transactions() -> pd.DataFrame:
    """Charge les transactions depuis context_examples (fichier léger 5KB)."""
    path = DATA_DIR / "context_examples_with_risk.csv"
    df = pd.read_csv(path)
    return df


@st.cache_data(show_spinner=False)
def load_metrics() -> dict:
    path = RESULTS_S3 / "metriques_semaine3.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data(show_spinner=False)
def load_all_logs() -> list:
    logs = []
    for i in range(1, 40): # Modifié à 40 au cas où, mais 31 était bien aussi
        p = RESULTS_S3 / f"log_s3_{i:02d}.json"
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                log_data = json.load(f)
                log_data["log_id"] = i
                logs.append(log_data)
    return logs


def save_live_investigation(record: dict):
    path = DATA_DIR / "live_history.json"
    history = []
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                history = []
    
    # Assign a rough log_id based on count
    record["log_id"] = len(history) + 1
    history.append(record)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def load_live_history() -> list:
    path = DATA_DIR / "live_history.json"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                pass
    return []


# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE INIT
# ══════════════════════════════════════════════════════════════════════════════

def _init_session():
    defaults = {
        "inv_active": False,
        "inv_state": None,
        "inv_history": None,
        "inv_chatbot": None,
        "inv_messages": [],   # [{"role": "bot"|"user", "text": str}]
        "inv_decision": None,
        "inv_tx": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


_init_session()


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
<div style="text-align:center;margin-bottom:1.5rem;padding-bottom:1rem;border-bottom:1px solid rgba(59,130,246,0.15)">
  <div style="font-size:2.5rem">🛡️</div>
  <div style="font-size:1.1rem;font-weight:800;color:#f1f5f9;margin-top:0.3rem">CCFD Investigator</div>
  <div style="font-size:0.72rem;color:#475569;margin-top:2px;letter-spacing:0.08em">CHATBOT ANTI-FRAUDE · SEMAINE 4</div>
</div>
""", unsafe_allow_html=True)

    # Charger les données
    df_tx = load_transactions()

    # Filtres
    st.markdown('<div class="section-title">🔎 Sélection transaction</div>', unsafe_allow_html=True)

    filter_source = st.selectbox(
        "Source",
        ["Toutes", "PaySim (Mobile)", "ULB (Carte Bancaire)"],
        key="filter_source",
    )
    if filter_source == "PaySim (Mobile)":
        df_filtered = df_tx[df_tx["source"] == "paysim"]
    elif filter_source == "ULB (Carte Bancaire)":
        df_filtered = df_tx[df_tx["source"] == "ulb"]
    else:
        df_filtered = df_tx

    filter_risk = st.selectbox(
        "Niveau de risque",
        ["Tous", "HIGH", "MEDIUM", "LOW"],
        key="filter_risk",
    )
    if filter_risk != "Tous":
        df_filtered = df_filtered[df_filtered["risk_level"] == filter_risk]

    if df_filtered.empty:
        df_filtered = df_tx  # fallback

    # Sélection transaction
    tx_options = df_filtered["transaction_id"].tolist()
    selected_tx_id = st.selectbox(
        "Transaction ID",
        tx_options,
        format_func=lambda x: f"{'🔴' if df_tx[df_tx['transaction_id']==x]['risk_level'].values[0]=='HIGH' else '🟡' if df_tx[df_tx['transaction_id']==x]['risk_level'].values[0]=='MEDIUM' else '🟢'} {x}",
        key="selected_tx_id",
    )

    row = df_tx[df_tx["transaction_id"] == selected_tx_id].iloc[0].to_dict()

    # Transaction preview card
    st.markdown(f"""
<div class="tx-card" style="margin-top:1rem">
  <div class="tx-id">{row['transaction_id']}</div>
  <div class="tx-amount">{float(row['amount']):,.2f}</div>
  <div class="tx-src">{'📱 Mobile (PaySim)' if row['source']=='paysim' else '💳 Carte Bancaire (ULB)'}</div>
  <div style="margin-top:0.8rem;display:flex;gap:6px;flex-wrap:wrap">
    {_badge_risk(row['risk_level'])}
    {_badge_truth(int(row['is_fraud']))}
  </div>
  {_confidence_bar("Score de risque", int(float(row['risk_score'])*100), "#3b82f6")}
</div>
""", unsafe_allow_html=True)

    # Infos modèle
    st.markdown("""
<div style="margin-top:1.5rem;padding-top:1rem;border-top:1px solid rgba(59,130,246,0.1)">
  <div class="section-title">⚙️ Modèle LLM</div>
  <div style="font-size:0.78rem;color:#64748b">
    🤖 Llama 3.3 70B Versatile<br>
    🌐 Groq Cloud API<br>
    🧠 Context dynamique activé
  </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN HEADER
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div style="display:flex;align-items:center;gap:1rem;margin-bottom:1.5rem">
  <div>
    <h1 style="margin:0;font-size:1.8rem;font-weight:800;
               background:linear-gradient(135deg,#60a5fa,#a78bfa);
               -webkit-background-clip:text;-webkit-text-fill-color:transparent">
      🛡️ Chatbot d'Investigation CCFD
    </h1>
    <p style="margin:0;color:#475569;font-size:0.85rem">
      Context Engineering + LLM · Détection de Fraude Cartes Bancaires
    </p>
  </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════

tab_live, tab_metrics, tab_history = st.tabs([
    "💬 Investigation Live",
    "📊 Analyse & Métriques",
    "📖 Historique Live"
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — INVESTIGATION LIVE
# ══════════════════════════════════════════════════════════════════════════════

with tab_live:
    col_left, col_right = st.columns([4, 6], gap="large")

    # ── Colonne gauche — transaction + état ──────────────────────────────────
    with col_left:
        st.markdown('<div class="section-title">📋 Transaction sélectionnée</div>', unsafe_allow_html=True)
        st.markdown(f"""
<div class="glass-card">
  <div style="display:flex;justify-content:space-between;align-items:flex-start">
    <div>
      <div style="font-size:0.65rem;color:#475569;text-transform:uppercase;letter-spacing:0.1em">{row['transaction_id']}</div>
      <div style="font-size:2rem;font-weight:800;color:#f1f5f9;margin:4px 0">{float(row['amount']):,.2f}</div>
      <div style="font-size:0.8rem;color:#64748b">{'📱 PaySim' if row['source']=='paysim' else '💳 ULB'}</div>
    </div>
    <div style="text-align:right">{_badge_risk(row['risk_level'])}<br><br>{_badge_truth(int(row['is_fraud']))}</div>
  </div>
  {_confidence_bar("Risque Initial", int(float(row['risk_score'])*100), "linear-gradient(90deg,#1e40af,#3b82f6)")}
</div>
""", unsafe_allow_html=True)

        # ── État dynamique de l'investigation ──
        st.markdown('<div class="section-title" style="margin-top:0.3rem">⚡ Contexte Dynamique</div>', unsafe_allow_html=True)

        state: InvestigationState | None = st.session_state.inv_state
        if state is None:
            st.markdown("""
<div class="glass-card" style="color:#475569;text-align:center;padding:2rem 1rem">
  <div style="font-size:1.8rem">💤</div>
  <div style="font-size:0.85rem;margin-top:0.5rem">Aucune investigation active.<br>Lancez-en une à droite.</div>
</div>
""", unsafe_allow_html=True)
        else:
            # Confidence gauge
            conf_color = (
                "linear-gradient(90deg,#ef4444,#f87171)" if state.confidence >= 60
                else "linear-gradient(90deg,#f59e0b,#fbbf24)" if state.confidence >= 40
                else "linear-gradient(90deg,#22c55e,#4ade80)"
            )
            st.markdown(f"""
<div class="glass-card">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.8rem">
    <span style="font-size:0.75rem;color:#64748b;text-transform:uppercase;letter-spacing:0.08em">Confiance Fraude</span>
    <span style="font-size:1.3rem;font-weight:800;color:#f1f5f9">{state.confidence}%</span>
  </div>
  {_confidence_bar("", state.confidence, conf_color)}
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.5rem;margin-top:0.8rem">
    <div style="text-align:center;background:rgba(239,68,68,0.05);border:1px solid rgba(239,68,68,0.15);border-radius:8px;padding:0.5rem">
      <div style="font-size:1.4rem;font-weight:800;color:#f87171">{len(state.signals_fraud)}</div>
      <div style="font-size:0.65rem;color:#64748b">Signaux fraude</div>
    </div>
    <div style="text-align:center;background:rgba(34,197,94,0.05);border:1px solid rgba(34,197,94,0.15);border-radius:8px;padding:0.5rem">
      <div style="font-size:1.4rem;font-weight:800;color:#4ade80">{len(state.signals_legit)}</div>
      <div style="font-size:0.65rem;color:#64748b">Signaux légit.</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

            # Fraud signals
            st.markdown(f"""
<div class="glass-card" style="padding:1rem 1.2rem">
  <div class="section-title">🔴 Signaux Fraude</div>
  <div>{_signal_tags(state.signals_fraud, "signal-fraud")}</div>
</div>
""", unsafe_allow_html=True)

            # Legit signals
            st.markdown(f"""
<div class="glass-card" style="padding:1rem 1.2rem">
  <div class="section-title">🟢 Signaux Légitimes</div>
  <div>{_signal_tags(state.signals_legit, "signal-legit")}</div>
</div>
""", unsafe_allow_html=True)

            # Progress
            max_q = 6
            pct_q = min(100, int(state.nb_questions / max_q * 100))
            st.markdown(f"""
<div class="glass-card" style="padding:1rem 1.2rem">
  {_confidence_bar(f"Progression ({state.nb_questions}/{max_q} questions)", pct_q, "linear-gradient(90deg,#7c3aed,#a78bfa)")}
</div>
""", unsafe_allow_html=True)

        # ── Boutons ──────────────────────────────────────────────────────────
        if not st.session_state.inv_active:
            if st.button("🚀 Lancer l'Investigation", key="btn_start"):
                with st.spinner("Connexion au LLM en cours..."):
                    try:
                        chatbot = ChatbotInvestigation(max_questions=6)
                        inv_state, inv_history, first_q = chatbot.start_investigation(row)
                        st.session_state.inv_active = True
                        st.session_state.inv_state = inv_state
                        st.session_state.inv_history = inv_history
                        st.session_state.inv_chatbot = chatbot
                        st.session_state.inv_messages = [{"role": "bot", "text": first_q}]
                        st.session_state.inv_decision = None
                        st.session_state.inv_tx = selected_tx_id
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erreur : {e}")
        else:
            if st.button("🔄 Nouvelle Investigation", key="btn_reset"):
                for k in ["inv_active","inv_state","inv_history","inv_chatbot",
                          "inv_messages","inv_decision","inv_tx"]:
                    st.session_state[k] = None if k != "inv_active" else False
                    if k == "inv_messages":
                        st.session_state[k] = []
                st.rerun()

    # ── Colonne droite — chat ────────────────────────────────────────────────
    with col_right:
        st.markdown('<div class="section-title">💬 Dialogue d\'Investigation</div>', unsafe_allow_html=True)

        if not st.session_state.inv_active and not st.session_state.inv_decision:
            st.markdown("""
<div class="glass-card" style="text-align:center;padding:4rem 2rem">
  <div style="font-size:3rem;margin-bottom:1rem">🔍</div>
  <div style="font-size:1.1rem;font-weight:600;color:#94a3b8;margin-bottom:0.5rem">
    Prêt à investiguer
  </div>
  <div style="font-size:0.85rem;color:#475569">
    Sélectionnez une transaction dans la barre latérale<br>puis cliquez sur <strong style="color:#60a5fa">Lancer l'Investigation</strong>.
  </div>
</div>
""", unsafe_allow_html=True)

        else:
            # ── Afficher les bulles de chat ──
            msgs = st.session_state.inv_messages
            bubbles_html = '<div class="chat-area">'
            for m in msgs:
                if m["role"] == "bot":
                    bubbles_html += _chat_bubble_bot(m["text"])
                else:
                    bubbles_html += _chat_bubble_user(m["text"])
            bubbles_html += "</div>"
            st.markdown(bubbles_html, unsafe_allow_html=True)

            # ── Décision finale ──
            if st.session_state.inv_decision is not None:
                dec = st.session_state.inv_decision
                is_fraud = dec["decision"] == "FRAUDE"
                css = "verdict-fraud" if is_fraud else "verdict-legit"
                emoji = "🚨" if is_fraud else "✅"
                key_signals_html = " ".join(
                    f'<span class="{"signal-fraud" if is_fraud else "signal-legit"}">{s}</span>'
                    for s in (dec.get("key_signals") or [])
                )
                st.markdown(f"""
<div class="{css}" style="margin-top:1.2rem">
  <div class="verdict-emoji">{emoji}</div>
  <div class="verdict-title" style="color:{'#f87171' if is_fraud else '#4ade80'}">
    {dec['decision']}
  </div>
  <div class="verdict-conf">Confiance : <strong>{dec['confidence']}%</strong></div>
  <div style="margin-bottom:0.8rem">{key_signals_html}</div>
  <div class="verdict-just">{dec['justification']}</div>
</div>
""", unsafe_allow_html=True)

            # ── Input utilisateur (si investigation toujours active) ──
            elif st.session_state.inv_active:
                st.markdown("<div style='margin-top:0.8rem'></div>", unsafe_allow_html=True)
                reply = st.chat_input(
                    "Votre réponse... (ex: Oui c'est moi / Non je ne reconnais pas cette transaction)",
                    key="chat_input",
                )
                if reply:
                    # Ajouter message utilisateur
                    st.session_state.inv_messages.append({"role": "user", "text": reply})

                    with st.spinner("L'analyste IA réfléchit..."):
                        result = st.session_state.inv_chatbot.process_answer(
                            reply,
                            st.session_state.inv_state,
                            st.session_state.inv_history,
                        )

                    if result["type"] == "question":
                        st.session_state.inv_messages.append(
                            {"role": "bot", "text": result["content"]}
                        )
                    else:
                        # Décision finale
                        st.session_state.inv_decision = result["content"]
                        st.session_state.inv_active = False
                        st.session_state.inv_messages.append(
                            {"role": "bot", "text": "J'ai réuni suffisamment d'éléments. Voici ma décision finale :"}
                        )
                        
                        # Sauvegarder dans l'historique
                        save_live_investigation({
                            "timestamp": time.time(),
                            "transaction": row,
                            "conversation": [
                                {"role": m["role"], "content": m["text"]} for m in st.session_state.inv_messages
                            ],
                            "decision": st.session_state.inv_decision
                        })

                    st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — ANALYSE & MÉTRIQUES
# ══════════════════════════════════════════════════════════════════════════════

with tab_metrics:
    metrics = load_metrics()
    logs = load_all_logs()

    perf = metrics["performance"]
    conv = metrics["convergence"]
    conf_m = metrics["confidence"]

    # ── KPI row ──────────────────────────────────────────────────────────────
    st.markdown('<div class="section-title" style="font-size:0.8rem">📈 Métriques de Performance — Semaine 3 (30 investigations)</div>', unsafe_allow_html=True)

    k1, k2, k3, k4, k5, k6 = st.columns(6)

    def _kpi(col, value, label, color):
        col.markdown(f"""
<div class="metric-card">
  <div class="val" style="color:{color}">{value}</div>
  <div class="lbl">{label}</div>
</div>
""", unsafe_allow_html=True)

    _kpi(k1, f"{perf['accuracy']*100:.0f}%", "🎯 Accuracy", "#60a5fa")
    _kpi(k2, f"{perf['precision']*100:.0f}%", "🔬 Precision", "#a78bfa")
    _kpi(k3, f"{perf['recall']*100:.0f}%", "📡 Recall", "#f472b6")
    _kpi(k4, f"{perf['f1_score']:.2f}", "⚖️ F1 Score", "#34d399")
    _kpi(k5, f"{conv['nb_questions_mean']:.1f}", "❓ Moy. Questions", "#fbbf24")
    _kpi(k6, f"{conf_m['mean_all']:.0f}%", "🧠 Confiance Moy.", "#94a3b8")

    st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)

    # ── Charts row ───────────────────────────────────────────────────────────
    ch1, ch2, ch3 = st.columns([1, 1.5, 1])

    # Confusion Matrix
    with ch1:
        st.markdown('<div class="section-title">🧩 Matrice de Confusion</div>', unsafe_allow_html=True)
        cm = perf["confusion_matrix"]
        z = [[cm["TN"], cm["FP"]], [cm["FN"], cm["TP"]]]
        fig_cm = go.Figure(go.Heatmap(
            z=z,
            x=["Prédit Légitime", "Prédit Fraude"],
            y=["Réel Légitime", "Réel Fraude"],
            colorscale=[[0, "#0f172a"], [0.5, "#1e3a5f"], [1, "#3b82f6"]],
            text=[[str(z[i][j]) for j in range(2)] for i in range(2)],
            texttemplate="%{text}",
            textfont={"size": 22, "color": "white"},
            showscale=False,
        ))
        fig_cm.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={"color": "#94a3b8", "family": "Inter"},
            margin={"t": 10, "b": 10, "l": 10, "r": 10},
            height=260,
            xaxis={"tickfont": {"size": 11}},
            yaxis={"tickfont": {"size": 11}},
        )
        st.plotly_chart(fig_cm, use_container_width=True, config={"displayModeBar": False})

    # Confidence per log
    with ch2:
        st.markdown('<div class="section-title">📊 Confiance par Investigation</div>', unsafe_allow_html=True)
        log_ids = [l["log_id"] for l in logs]
        confs = [l["confidence_score"] for l in logs]
        corrects = [l.get("correct", l["ground_truth"] == l["prediction"]) for l in logs]
        colors = ["#3b82f6" if c else "#ef4444" for c in corrects]

        fig_conf = go.Figure(go.Bar(
            x=[f"#{i}" for i in log_ids],
            y=confs,
            marker_color=colors,
            text=confs,
            textposition="outside",
            textfont={"size": 8, "color": "#94a3b8"},
        ))
        fig_conf.add_hline(y=conf_m["mean_all"], line_dash="dot",
                           line_color="#fbbf24", annotation_text=f"Moy: {conf_m['mean_all']:.0f}%")
        fig_conf.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(5,11,24,0.5)",
            font={"color": "#94a3b8", "family": "Inter"},
            margin={"t": 10, "b": 10, "l": 10, "r": 10},
            height=260,
            xaxis={"showgrid": False, "tickfont": {"size": 8}},
            yaxis={"gridcolor": "rgba(59,130,246,0.08)", "range": [0, 110]},
            showlegend=False,
        )
        st.plotly_chart(fig_conf, use_container_width=True, config={"displayModeBar": False})
        st.markdown(
            '<div style="font-size:0.72rem;color:#475569;text-align:center">'
            '🔵 Correct &nbsp;&nbsp; 🔴 Incorrect</div>',
            unsafe_allow_html=True,
        )

    # Donut verdict breakdown
    with ch3:
        st.markdown('<div class="section-title">🥧 Répartition Verdicts</div>', unsafe_allow_html=True)
        tp = cm["TP"]; fp = cm["FP"]; tn = cm["TN"]; fn = cm["FN"]
        fig_pie = go.Figure(go.Pie(
            labels=["Vrais Positifs", "Faux Positifs", "Vrais Négatifs", "Faux Négatifs"],
            values=[tp, fp, tn, fn],
            hole=0.55,
            marker_colors=["#22c55e", "#ef4444", "#3b82f6", "#f59e0b"],
            textfont={"size": 11},
        ))
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={"color": "#94a3b8", "family": "Inter"},
            margin={"t": 10, "b": 10, "l": 10, "r": 10},
            height=260,
            legend={"font": {"size": 9}},
            showlegend=True,
        )
        fig_pie.add_annotation(
            text=f"<b>{tp+tn}</b><br><span style='font-size:10px'>corrects</span>",
            x=0.5, y=0.5, showarrow=False,
            font={"size": 16, "color": "#f1f5f9"},
        )
        st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})

    # ── Transcript Explorer ──────────────────────────────────────────────────
    st.markdown("<hr style='border-color:rgba(59,130,246,0.1);margin:1.5rem 0'>", unsafe_allow_html=True)
    st.markdown('<div class="section-title" style="font-size:0.8rem">📜 Explorateur de Transcriptions — 30 Dialogues S3</div>', unsafe_allow_html=True)

    t_col1, t_col2 = st.columns([1, 2.5], gap="large")

    with t_col1:
        # Liste des logs
        log_options = {
            f"#{l['log_id']:02d} {'🔴' if l['ground_truth']=='FRAUDE' else '🟢'} {l['transaction_id'][:20]} "
            f"({'✓' if l.get('correct', l['ground_truth']==l['prediction']) else '✗'} {l['confidence_score']}%)": i
            for i, l in enumerate(logs)
        }
        sel_log_key = st.selectbox("Sélectionner une session", list(log_options.keys()), key="sel_log")
        sel_log_idx = log_options[sel_log_key]
        sel_log = logs[sel_log_idx]
        
        # Safe access to nb_questions which might be inside context or missing
        nb_questions = sel_log.get("nb_questions")
        if nb_questions is None and "context" in sel_log:
            nb_questions = sel_log["context"].get("nb_questions", "N/A")
        elif nb_questions is None:
            nb_questions = "N/A"

        correct = sel_log.get("correct", sel_log["ground_truth"] == sel_log["prediction"])
        st.markdown(f"""
<div class="glass-card">
  <div class="section-title">Détails</div>
  <table style="width:100%;font-size:0.78rem;border-collapse:collapse">
    <tr><td style="color:#64748b;padding:3px 0">Transaction</td><td style="color:#e2e8f0;text-align:right">{sel_log['transaction_id']}</td></tr>
    <tr><td style="color:#64748b;padding:3px 0">Vérité terrain</td><td style="text-align:right">{_badge_truth(1 if sel_log['ground_truth']=='FRAUDE' else 0)}</td></tr>
    <tr><td style="color:#64748b;padding:3px 0">Prédiction</td><td style="text-align:right">{_badge_truth(1 if sel_log['prediction']=='FRAUDE' else 0)}</td></tr>
    <tr><td style="color:#64748b;padding:3px 0">Confiance</td><td style="color:#e2e8f0;text-align:right">{sel_log['confidence_score']}%</td></tr>
    <tr><td style="color:#64748b;padding:3px 0">Questions</td><td style="color:#e2e8f0;text-align:right">{nb_questions}</td></tr>
    <tr><td style="color:#64748b;padding:3px 0">Résultat</td><td style="text-align:right"><span class="badge {'badge-legit' if correct else 'badge-fraud'}">{'✓ Correct' if correct else '✗ Incorrect'}</span></td></tr>
  </table>
</div>
""", unsafe_allow_html=True)

    with t_col2:
        st.markdown('<div class="section-title">Conversation complète</div>', unsafe_allow_html=True)
        conv_data = sel_log.get("conversation", [])
        
        rendered = '<div class="glass-card" style="max-height:400px;overflow-y:auto;padding:1rem">'
        rendered += '<div class="chat-area" style="max-height:none">'

        if isinstance(conv_data, str):
            # Ancien format : Une seule grande chaîne avec des émojis
            lines = conv_data.split("\n")
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                if line.startswith("🤖"):
                    text = line[2:].strip().replace(": ", "", 1).strip()
                    if "```json" not in text:
                        rendered += _chat_bubble_bot(text)
                elif line.startswith("👤"):
                    text = line[2:].strip().replace(": ", "", 1).strip()
                    if text and not text.startswith("Contexte") and not text.startswith("Prends"):
                        rendered += _chat_bubble_user(text)
        elif isinstance(conv_data, list):
            # Nouveau format Kaggle : Liste de dictionnaires {"role": ..., "content": ...}
            for msg in conv_data:
                role = msg.get("role", "")
                text = msg.get("content", "").strip()
                if not text:
                    continue
                
                if role == "assistant":
                    # On ignore les bulles contenant du JSON (la décision finale technique)
                    if "```json" not in text and not text.startswith("{"):
                        rendered += _chat_bubble_bot(text)
                elif role == "user":
                    if text and not text.startswith("Contexte") and not text.startswith("Prends"):
                        rendered += _chat_bubble_user(text)

        rendered += "</div></div>"
        st.markdown(rendered, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — HISTORIQUE LIVE
# ══════════════════════════════════════════════════════════════════════════════

with tab_history:
    st.markdown('<div class="section-title" style="font-size:0.8rem">📖 Historique des Investigations Live</div>', unsafe_allow_html=True)
    
    live_logs = load_live_history()
    
    if not live_logs:
        st.markdown("""
<div class="glass-card" style="text-align:center;padding:4rem 2rem;color:#64748b">
  <div style="font-size:3rem;margin-bottom:1rem">📭</div>
  <div>Aucune investigation n'a encore été enregistrée.</div>
</div>
""", unsafe_allow_html=True)
    else:
        # ── Filtres Historique ──
        h_col1, h_col2, h_col3 = st.columns(3)
        with h_col1:
            h_src = st.selectbox("Filtrer par Source", ["Toutes", "PaySim", "ULB"], key="h_src")
        with h_col2:
            h_risk = st.selectbox("Filtrer par Risque Initial", ["Tous", "HIGH", "MEDIUM", "LOW"], key="h_risk")
        with h_col3:
            h_sort = st.selectbox("Trier par", ["Plus récents", "Plus anciens"], key="h_sort")

        # Appliquer les filtres
        filtered_live = []
        for l in live_logs:
            tx = l.get("transaction", {})
            src = tx.get("source", "").lower()
            risk = tx.get("risk_level", "")
            
            if h_src == "PaySim" and "paysim" not in src: continue
            if h_src == "ULB" and "ulb" not in src: continue
            if h_risk != "Tous" and risk != h_risk: continue
            
            filtered_live.append(l)

        if h_sort == "Plus récents":
            filtered_live.reverse()

        st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)

        h_left, h_right = st.columns([1, 2.5], gap="large")

        with h_left:
            if not filtered_live:
                st.warning("Aucun résultat pour ces filtres.")
            else:
                log_options = {}
                for l in filtered_live:
                    tx = l.get("transaction", {})
                    dec = l.get("decision", {})
                    tx_id = tx.get("transaction_id", "Inconnu")[:15]
                    is_fraud = (dec.get("decision") == "FRAUDE")
                    icon = "🔴" if is_fraud else "🟢"
                    label = f"#{l.get('log_id', '?')} {icon} {tx_id} ({dec.get('confidence', 0)}%)"
                    log_options[label] = l
                
                sel_history_key = st.selectbox("Sélectionner une investigation", list(log_options.keys()), key="sel_history_log")
                sel_history = log_options[sel_history_key]

                tx_data = sel_history.get("transaction", {})
                st.markdown(f"""
<div class="glass-card">
  <div class="section-title">Détails de la Transaction</div>
  <table style="width:100%;font-size:0.78rem;border-collapse:collapse">
    <tr><td style="color:#64748b;padding:3px 0">Transaction</td><td style="color:#e2e8f0;text-align:right">{tx_data.get('transaction_id')}</td></tr>
    <tr><td style="color:#64748b;padding:3px 0">Montant</td><td style="color:#e2e8f0;text-align:right">{float(tx_data.get('amount', 0)):,.2f}</td></tr>
    <tr><td style="color:#64748b;padding:3px 0">Source</td><td style="color:#e2e8f0;text-align:right">{tx_data.get('source')}</td></tr>
    <tr><td style="color:#64748b;padding:3px 0">Risque Initial</td><td style="text-align:right">{_badge_risk(tx_data.get('risk_level', 'LOW'))}</td></tr>
    <tr><td style="color:#64748b;padding:3px 0">Vérité terrain</td><td style="text-align:right">{_badge_truth(int(tx_data.get('is_fraud', -1)))}</td></tr>
  </table>
</div>
""", unsafe_allow_html=True)

        with h_right:
            if filtered_live:
                st.markdown('<div class="section-title">Conversation & Verdict</div>', unsafe_allow_html=True)
                
                conv_data = sel_history.get("conversation", [])
                rendered_h = '<div class="glass-card" style="max-height:400px;overflow-y:auto;padding:1rem">'
                rendered_h += '<div class="chat-area" style="max-height:none">'

                for msg in conv_data:
                    role = msg.get("role", "")
                    text = msg.get("content", "").strip()
                    if not text: continue
                    
                    if role == "bot" or role == "assistant":
                        if "```json" not in text and not text.startswith("{"):
                            rendered_h += _chat_bubble_bot(text)
                    elif role == "user":
                        if text and not text.startswith("Contexte") and not text.startswith("Prends"):
                            rendered_h += _chat_bubble_user(text)

                rendered_h += "</div></div>"
                st.markdown(rendered_h, unsafe_allow_html=True)

                # Afficher la décision
                dec = sel_history.get("decision")
                if dec:
                    is_fraud = dec.get("decision") == "FRAUDE"
                    css = "verdict-fraud" if is_fraud else "verdict-legit"
                    emoji = "🚨" if is_fraud else "✅"
                    key_signals_html = " ".join(
                        f'<span class="{"signal-fraud" if is_fraud else "signal-legit"}">{s}</span>'
                        for s in (dec.get("key_signals") or [])
                    )
                    st.markdown(f"""
<div class="{css}" style="margin-top:1.2rem;padding:1.5rem">
  <div class="verdict-emoji" style="font-size:2.5rem">{emoji}</div>
  <div class="verdict-title" style="color:{'#f87171' if is_fraud else '#4ade80'};font-size:1.5rem">
    {dec.get('decision')}
  </div>
  <div class="verdict-conf">Confiance : <strong>{dec.get('confidence')}%</strong></div>
  <div style="margin-bottom:0.8rem">{key_signals_html}</div>
  <div class="verdict-just">{dec.get('justification')}</div>
</div>
""", unsafe_allow_html=True)