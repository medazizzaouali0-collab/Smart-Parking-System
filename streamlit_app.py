import streamlit as st
import json
import time
import os
import sqlite3
import hashlib
import base64

# ============================================
# 1. BASE DE DONNÉES (AUTHENTIFICATION)
# ============================================
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)''')
    conn.commit()
    conn.close()

def make_hash(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username=?", (username,))
    result = c.fetchone()
    conn.close()
    return result and result[0] == make_hash(password)

def add_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, make_hash(password)))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

init_db()

# ============================================
# 2. LOGO EN BASE64
# ============================================
# 2. On charge le logo (assurez-vous que le nom du fichier correspond exactement)
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()
# Mettez le chemin complet vers votre fichier
image_path = r"C:/Users/User/Desktop/smart_parking_app/EPT_logo-removebg-preview.png"

LOGO_B64 = get_base64_image(image_path)
# ============================================
# 3. FONCTIONS DE LECTURE DES DONNÉES CV
# ============================================
def check_parking_config():
    return os.path.exists('parking_config.json')

def load_parking_config():
    with open('parking_config.json', 'r') as f:
        data = json.load(f)
        return data['spots']

def load_parking_status():
    dossier_actuel = os.path.dirname(os.path.abspath(__file__))
    fichier = os.path.join(dossier_actuel, 'parking_status.json')
    if os.path.exists(fichier):
        try:
            age_fichier = time.time() - os.path.getmtime(fichier)
            if age_fichier < 15:
                with open(fichier, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        if 'status' in data:
                            return data['status']
                        else:
                            return data
        except:
            pass
    return None


# ============================================
# 4. STYLE CSS — NEON BRIGHT
# ============================================
st.set_page_config(page_title="EPT SmartPark", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600&display=swap');

    :root {
        --bg-deep:     #060818;
        --bg-card:     #0d1230;
        --border:      rgba(100,149,255,.28);
        --neon-blue:   #4d9fff;
        --neon-cyan:   #00e5ff;
        --neon-pink:   #ff4db8;
        --neon-green:  #00f5a0;
        --neon-amber:  #ffcc00;
        --neon-violet: #b04dff;
        --text:        #e8f0ff;
        --muted:       #7a90c0;
        --glow-blue:   0 0 24px rgba(77,159,255,.7),  0 0 70px rgba(77,159,255,.25);
        --glow-cyan:   0 0 24px rgba(0,229,255,.7),   0 0 70px rgba(0,229,255,.25);
        --glow-pink:   0 0 24px rgba(255,77,184,.7),  0 0 70px rgba(255,77,184,.25);
        --glow-green:  0 0 24px rgba(0,245,160,.7),   0 0 70px rgba(0,245,160,.25);
    }

    html, body, [class*="css"] {
        font-family: 'Rajdhani', sans-serif;
        color: var(--text);
    }

    .stApp {
        background-color: var(--bg-deep);
        background-image:
            radial-gradient(ellipse 90% 55% at 5%  0%,   rgba(77,159,255,.28)  0%, transparent 55%),
            radial-gradient(ellipse 70% 45% at 95% 100%,  rgba(176,77,255,.28)  0%, transparent 55%),
            radial-gradient(ellipse 55% 65% at 50% 50%,   rgba(0,229,255,.10)   0%, transparent 65%),
            radial-gradient(ellipse 40% 30% at 80% 20%,   rgba(0,245,160,.12)   0%, transparent 50%),
            repeating-linear-gradient(
                0deg, transparent, transparent 47px,
                rgba(100,149,255,.06) 47px, rgba(100,149,255,.06) 48px
            ),
            repeating-linear-gradient(
                90deg, transparent, transparent 47px,
                rgba(100,149,255,.06) 47px, rgba(100,149,255,.06) 48px
            );
        min-height: 100vh;
    }

    #MainMenu, footer, header { visibility: hidden; }

    /* ── INPUTS ─────────────────────────────── */
    .stTextInput > div > div > input {
        background: rgba(77,159,255,.07) !important;
        border: 1px solid rgba(77,159,255,.35) !important;
        border-radius: 8px !important;
        color: var(--text) !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 1rem !important;
        padding: 10px 14px !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: var(--neon-cyan) !important;
        box-shadow: 0 0 0 2px rgba(0,229,255,.18) !important;
    }
    .stTextInput label { color: var(--muted) !important; font-size: .82rem !important; }

    /* ── BUTTONS ─────────────────────────────── */
    .stButton > button {
        background: transparent !important;
        border: 1px solid var(--neon-cyan) !important;
        color: var(--neon-cyan) !important;
        border-radius: 6px !important;
        padding: 10px 22px !important;
        font-family: 'Orbitron', sans-serif !important;
        font-size: .72rem !important;
        font-weight: 700 !important;
        letter-spacing: 1.5px !important;
        text-transform: uppercase !important;
        transition: all .25s ease !important;
        box-shadow: 0 0 14px rgba(0,229,255,.22) !important;
        width: 100% !important;
    }
    .stButton > button:hover {
        background: var(--neon-cyan) !important;
        color: var(--bg-deep) !important;
        box-shadow: var(--glow-cyan) !important;
    }

    /* ── AUTH PAGE ───────────────────────────── */
    .page-hero {
        text-align: center;
        padding: 44px 20px 36px;
    }
    .hero-logo {
        width: 110px;
        height: 110px;
        object-fit: contain;
        margin: 0 auto 20px;
        display: block;
        filter: drop-shadow(0 0 18px rgba(77,159,255,.9)) drop-shadow(0 0 40px rgba(0,229,255,.5));
        animation: logoGlow 3s ease-in-out infinite;
    }
    @keyframes logoGlow {
        0%,100% { filter: drop-shadow(0 0 18px rgba(77,159,255,.9)) drop-shadow(0 0 40px rgba(0,229,255,.5)); }
        50%      { filter: drop-shadow(0 0 28px rgba(77,159,255,1))  drop-shadow(0 0 60px rgba(0,229,255,.8)); }
    }
    .hero-eyebrow {
        display: inline-block;
        border: 1px solid var(--neon-cyan);
        color: var(--neon-cyan);
        font-family: 'Orbitron', sans-serif;
        font-size: .65rem;
        font-weight: 700;
        letter-spacing: 3px;
        text-transform: uppercase;
        padding: 5px 16px;
        border-radius: 3px;
        margin-bottom: 18px;
        box-shadow: var(--glow-cyan);
    }
    .hero-title {
        font-family: 'Orbitron', sans-serif;
        font-size: clamp(1.5rem, 3.5vw, 2.6rem);
        font-weight: 900;
        line-height: 1.18;
        color: var(--text);
        letter-spacing: -.5px;
        margin: 0 auto 12px;
        text-shadow: 0 0 50px rgba(77,159,255,.5);
    }
    .hero-title span {
        background: linear-gradient(90deg, var(--neon-cyan), var(--neon-blue), var(--neon-violet));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 0 12px rgba(0,229,255,.6));
    }
    .hero-sub {
        color: var(--muted);
        font-size: 1.05rem;
        font-weight: 300;
        letter-spacing: .5px;
    }
    .hero-divider {
        width: 80px; height: 2px;
        background: linear-gradient(90deg, transparent, var(--neon-cyan), transparent);
        margin: 20px auto;
        box-shadow: 0 0 10px var(--neon-cyan);
    }

    .auth-card {
        background: rgba(13,18,48,.85);
        border: 1px solid rgba(77,159,255,.3);
        border-radius: 18px;
        padding: 30px 26px;
        margin-bottom: 16px;
        box-shadow: 0 0 50px rgba(77,159,255,.08), inset 0 1px 0 rgba(255,255,255,.05);
        position: relative;
        overflow: hidden;
    }
    .auth-card::before {
        content: '';
        position: absolute; top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--neon-cyan), transparent);
        box-shadow: 0 0 12px var(--neon-cyan);
    }
    .auth-label {
        font-family: 'Orbitron', sans-serif;
        font-weight: 700;
        font-size: .85rem;
        letter-spacing: 1.5px;
        margin-bottom: 18px;
        color: var(--neon-cyan);
        text-transform: uppercase;
        text-shadow: 0 0 14px rgba(0,229,255,.5);
    }

    /* ── TOP BAR ─────────────────────────────── */
    .topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 16px 0 12px;
        border-bottom: 1px solid rgba(77,159,255,.2);
        margin-bottom: 28px;
    }
    .topbar-brand { display: flex; align-items: center; gap: 14px; }
    .topbar-logo {
        width: 36px; height: 36px;
        object-fit: contain;
        filter: drop-shadow(0 0 8px rgba(77,159,255,.8));
    }
    .topbar-dot {
        width: 9px; height: 9px;
        border-radius: 50%;
        background: var(--neon-green);
        box-shadow: var(--glow-green);
        animation: pulse 2s infinite;
        margin-left: 4px;
    }
    @keyframes pulse {
        0%,100% { opacity:1; transform:scale(1); }
        50%      { opacity:.4; transform:scale(1.6); }
    }
    .topbar-title {
        font-family: 'Orbitron', sans-serif;
        font-weight: 900;
        font-size: 1rem;
        letter-spacing: .5px;
        color: var(--text);
        text-shadow: 0 0 16px rgba(77,159,255,.5);
    }
    .topbar-sub { font-size: .78rem; color: var(--muted); letter-spacing: .3px; }
    .topbar-user { display: flex; align-items: center; gap: 10px; }
    .avatar {
        width: 34px; height: 34px;
        border-radius: 50%;
        background: linear-gradient(135deg, var(--neon-blue), var(--neon-violet));
        display: flex; align-items: center; justify-content: center;
        color: white;
        font-family: 'Orbitron', sans-serif;
        font-size: .8rem; font-weight: 700;
        box-shadow: var(--glow-blue);
    }
    .topbar-username { font-size: .9rem; font-weight: 600; color: var(--text); }

    /* ── METRIC CARDS ────────────────────────── */
    .metrics-row {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 14px;
        margin-bottom: 24px;
    }
    .metric-card {
        background: rgba(13,18,48,.75);
        border: 1px solid rgba(77,159,255,.22);
        border-radius: 14px;
        padding: 20px 18px;
        display: flex;
        align-items: center;
        gap: 14px;
        position: relative;
        overflow: hidden;
    }
    .metric-card::after {
        content: '';
        position: absolute; bottom: 0; left: 0; right: 0;
        height: 1px;
    }
    .metric-card.blue-card  { box-shadow: 0 0 35px rgba(77,159,255,.12); }
    .metric-card.blue-card::after  { background: linear-gradient(90deg, transparent, var(--neon-blue),  transparent); }
    .metric-card.green-card { box-shadow: 0 0 35px rgba(0,245,160,.12); }
    .metric-card.green-card::after { background: linear-gradient(90deg, transparent, var(--neon-green), transparent); }
    .metric-card.cyan-card  { box-shadow: 0 0 35px rgba(0,229,255,.12); }
    .metric-card.cyan-card::after  { background: linear-gradient(90deg, transparent, var(--neon-cyan),  transparent); }

    .metric-icon {
        font-size: 1.4rem;
        width: 46px; height: 46px;
        border-radius: 10px;
        display: flex; align-items: center; justify-content: center;
        flex-shrink: 0;
    }
    .metric-icon.blue  { background: rgba(77,159,255,.14); border: 1px solid rgba(77,159,255,.4); }
    .metric-icon.green { background: rgba(0,245,160,.14);  border: 1px solid rgba(0,245,160,.4);  }
    .metric-icon.cyan  { background: rgba(0,229,255,.14);  border: 1px solid rgba(0,229,255,.4);  }

    .metric-title {
        font-size: .72rem; font-weight: 600;
        color: var(--muted);
        text-transform: uppercase; letter-spacing: 1px;
        margin-bottom: 3px;
    }
    .metric-value {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.75rem; font-weight: 900; line-height: 1;
    }
    .metric-value.blue  { color: var(--neon-blue);  text-shadow: 0 0 22px rgba(77,159,255,.7);  }
    .metric-value.green { color: var(--neon-green); text-shadow: 0 0 22px rgba(0,245,160,.7); }
    .metric-value.cyan  { color: var(--neon-cyan);  text-shadow: 0 0 22px rgba(0,229,255,.7);  }
    .metric-value span  { font-size: .85rem; color: var(--muted); font-family: 'Rajdhani', sans-serif; font-weight: 300; }

    /* ── STATUS BAR ──────────────────────────── */
    .status-bar {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-size: .78rem;
        color: var(--muted);
        margin-bottom: 20px;
        padding: 7px 14px;
        background: rgba(13,18,48,.75);
        border: 1px solid rgba(77,159,255,.2);
        border-radius: 6px;
        letter-spacing: .3px;
    }
    .status-dot { width: 7px; height: 7px; border-radius: 50%; }
    .status-dot.ok  { background: var(--neon-green); box-shadow: 0 0 10px var(--neon-green); }
    .status-dot.err { background: var(--neon-pink);  box-shadow: 0 0 10px var(--neon-pink);  }

    /* ── PARKING MAP ─────────────────────────── */
    .park-wrapper {
        display: flex;
        justify-content: center;
        margin-top: 8px; margin-bottom: 32px;
    }

    .nature-zone {
        background: linear-gradient(160deg, #081c10 0%, #030d07 100%);
        padding: 28px;
        border-radius: 20px;
        border: 1px solid rgba(0,245,160,.25);
        box-shadow:
            0 0 0 1px rgba(0,245,160,.08),
            0 30px 80px rgba(0,0,0,.6),
            0 0 70px rgba(0,245,160,.08) inset;
    }

    .asphalt-road {
        background: #080810;
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        padding: 24px 20px;
        border-radius: 10px;
        width: 460px;
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,.07);
        box-shadow: inset 0 0 60px rgba(0,0,0,.6);
    }
    .asphalt-road::before {
        content: '';
        position: absolute; inset: 0;
        background-image:
            repeating-linear-gradient(45deg, transparent, transparent 6px, rgba(255,255,255,.014) 6px, rgba(255,255,255,.014) 12px);
        pointer-events: none;
    }

    .col-gauche, .col-droite {
        display: flex; flex-direction: column; gap: 10px;
    }
    .col-gauche { justify-content: flex-end; }

    .spot {
        width: 104px; height: 56px;
        border: 1px solid rgba(255,255,255,.1);
        display: flex; align-items: center; justify-content: center;
        border-radius: 4px;
        transition: all .3s ease;
    }
    .spot-left  { border-right: none; border-radius: 6px 0 0 6px; }
    .spot-right { border-left:  none; border-radius: 0 6px 6px 0; }

    .spot.free {
        background: rgba(0,245,160,.07);
        border-color: rgba(0,245,160,.5);
        box-shadow: inset 0 0 14px rgba(0,245,160,.07), 0 0 10px rgba(0,245,160,.15);
    }
    .spot.occupied {
        background: rgba(255,77,184,.08);
        border-color: rgba(255,77,184,.5);
        box-shadow: inset 0 0 14px rgba(255,77,184,.07), 0 0 10px rgba(255,77,184,.15);
    }

    .car { font-size: 26px; filter: drop-shadow(0 0 10px rgba(255,77,184,1)); }
    .car-right { transform: rotate(90deg); }
    .car-left  { transform: rotate(-90deg); }

    .p-label {
        font-family: 'Orbitron', sans-serif;
        color: rgba(0,245,160,.75);
        font-weight: 700; font-size: .65rem;
        letter-spacing: 1.5px;
        text-shadow: 0 0 12px rgba(0,245,160,.6);
    }

    .middle-lane {
        width: 3px;
        background-image: repeating-linear-gradient(
            to bottom,
            transparent, transparent 12px,
            rgba(255,204,0,.75) 12px, rgba(255,204,0,.75) 38px
        );
        border-radius: 2px;
        align-self: stretch;
        margin: 0 6px;
        filter: drop-shadow(0 0 5px rgba(255,204,0,.6));
    }

    .triangle-deco {
        width: 0; height: 0;
        border-top: 60px solid transparent;
        border-bottom: 60px solid transparent;
        border-right: 90px solid rgba(0,245,160,.1);
        margin-bottom: 24px;
        filter: drop-shadow(0 0 10px rgba(0,245,160,.4));
    }

    /* ── CONFIG MISSING ──────────────────────── */
    .config-missing {
        background: rgba(13,18,48,.85);
        border: 1px solid rgba(255,204,0,.35);
        border-left: 3px solid var(--neon-amber);
        padding: 36px 32px;
        border-radius: 14px;
        text-align: center;
        margin: 60px auto; max-width: 520px;
        box-shadow: 0 0 50px rgba(255,204,0,.07);
    }
    .config-missing h2 {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.1rem; font-weight: 700;
        margin-bottom: 14px;
        color: var(--neon-amber);
        text-shadow: 0 0 22px rgba(255,204,0,.5);
    }
    .config-missing code {
        display: inline-block;
        background: rgba(255,255,255,.04);
        border: 1px solid rgba(77,159,255,.3);
        padding: 6px 14px; border-radius: 6px;
        font-size: .9rem; margin: 10px 0;
        color: var(--neon-cyan);
    }
    </style>
    """, unsafe_allow_html=True)

# ============================================
# 5. PAGE PRINCIPALE
# ============================================
if not check_parking_config():
    st.markdown("""
    <div class="config-missing">
        <h2>⚠️ Configuration manquante</h2>
        <p>Le système de parking n'a pas encore été configuré.</p>
        <p>Veuillez exécuter d'abord dans un terminal :</p>
        <code>python computer_vision.py</code>
        <p>Pour calibrer les places de parking.</p>
        <p>Après calibration, rafraîchissez cette page (F5).</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

SPOTS_CONFIG = load_parking_config()

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# ── AUTH PAGE ────────────────────────────────────────────────────────────────
if not st.session_state['logged_in']:
    st.markdown(f"""
<div class="page-hero">
    <img class="hero-logo" src="data:image/png;base64,{LOGO_B64}" alt="Logo EPT">
    <div class="hero-title">Système Parking intelligent<br><span> École Polytechnique de Tunisie</span></div>
    <div class="hero-divider"></div>
    <div class="hero-sub">Surveillance en temps réel</div>
</div>
""", unsafe_allow_html=True)
    
    _, col1, col2, _ = st.columns([1, 4, 4, 1])
    with col1:
        st.markdown('<div class="auth-card"><div class="auth-label">Connexion</div>', unsafe_allow_html=True)
        u = st.text_input("Identifiant", key="l_u", label_visibility="collapsed", placeholder="Identifiant")
        p = st.text_input("Mot de passe", type="password", key="l_p", label_visibility="collapsed", placeholder="Mot de passe")
        if st.button("Accéder →"):
            if check_user(u, p):
                st.session_state['logged_in'] = True
                st.session_state['username'] = u
                st.rerun()
            else:
                st.error("Identifiants incorrects")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="auth-card"><div class="auth-label">Inscription</div>', unsafe_allow_html=True)
        nu = st.text_input("Nouvel Identifiant", key="r_u", label_visibility="collapsed", placeholder="Nouvel identifiant")
        np_val = st.text_input("Nouveau Mot de passe", type="password", key="r_p", label_visibility="collapsed", placeholder="Nouveau mot de passe")
        if st.button("S'inscrire →"):
            if nu and np_val:
                if add_user(nu, np_val):
                    st.success("Compte créé ! Veuillez vous connecter.")
                else:
                    st.error("Utilisateur existant.")
            else:
                st.warning("Remplissez tous les champs.")
        st.markdown('</div>', unsafe_allow_html=True)

# ── DASHBOARD ────────────────────────────────────────────────────────────────
else:
    initial = st.session_state['username'][0].upper()
    c_titre, c_btn = st.columns([9, 1])
    with c_titre:
        st.markdown(f"""
<div class="topbar">
    <div class="topbar-brand">
        <img class="topbar-logo" src="data:image/png;base64,{LOGO_B64}" alt="EPT"/>
        <div>
            <div class="topbar-title">EPT Parking System</div>
            <div class="topbar-sub">Tableau de bord — surveillance en temps réel</div>
        </div>
        <div class="topbar-dot"></div>
    </div>
    <div class="topbar-user">
        <div class="avatar">{initial}</div>
        <div class="topbar-username">{st.session_state['username']}</div>
    </div>
</div>
""", unsafe_allow_html=True)
        
    with c_btn:
        st.write(""); st.write("")
        if st.button("Quitter"):
            st.session_state['logged_in'] = False
            st.rerun()

    status_dict = {spot['id']: False for spot in SPOTS_CONFIG}
    metrics_ph = st.empty()
    status_ph  = st.empty()
    view_p     = st.empty()
    refresh_ph = st.empty()

    while st.session_state.get('logged_in', False):
        current_status = load_parking_status()
        if current_status is None:
            cv_ok = False
        else:
            cv_ok = True
            for key, value in current_status.items():
                status_dict[int(key)] = value

        free_droite = sum(1 for s in SPOTS_CONFIG if s['rangee'] == 1 and not status_dict.get(s['id'], False))
        free_gauche = sum(1 for s in SPOTS_CONFIG if s['rangee'] == 2 and not status_dict.get(s['id'], False))
        free_total  = free_gauche + free_droite

        metrics_ph.markdown(f"""
        <div class="metrics-row">
            <div class="metric-card blue-card">
                <div class="metric-icon blue">🅿️</div>
                <div>
                    <div class="metric-title">Places disponibles</div>
                    <div class="metric-value blue">{free_total}<span> / 15</span></div>
                </div>
            </div>
            <div class="metric-card green-card">
                <div class="metric-icon green">◀</div>
                <div>
                    <div class="metric-title">Colonne Gauche (6)</div>
                    <div class="metric-value green">{free_gauche}<span> libres</span></div>
                </div>
            </div>
            <div class="metric-card cyan-card">
                <div class="metric-icon cyan">▶</div>
                <div>
                    <div class="metric-title">Colonne Droite (9)</div>
                    <div class="metric-value cyan">{free_droite}<span> libres</span></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        dot_cls = "ok" if cv_ok else "err"
        dot_txt = "Connecté au système de vision — mise à jour en temps réel" if cv_ok else "En attente du système de vision (computer_vision.py)"
        status_ph.markdown(f"""
        <div class="status-bar">
            <div class="status-dot {dot_cls}"></div>
            {dot_txt} &nbsp;·&nbsp; {time.strftime('%H:%M:%S')}
        </div>
        """, unsafe_allow_html=True)

        html_g = '<div class="col-gauche"><div class="triangle-deco"></div>'
        for i in range(10, 16):
            is_occupied = status_dict.get(i, False)
            cls = "occupied" if is_occupied else "free"
            content = '<span class="car car-left">🚗</span>' if is_occupied else f'<span class="p-label">P{i}</span>'
            html_g += f'<div class="spot spot-left {cls}">{content}</div>'
        html_g += '</div>'

        html_d = '<div class="col-droite">'
        for i in range(1, 10):
            is_occupied = status_dict.get(i, False)
            cls = "occupied" if is_occupied else "free"
            content = '<span class="car car-right">🚗</span>' if is_occupied else f'<span class="p-label">P{i}</span>'
            html_d += f'<div class="spot spot-right {cls}">{content}</div>'
        html_d += '</div>'

        view_p.markdown(f"""
        <div class="park-wrapper">
            <div class="nature-zone">
                <div class="asphalt-road">
                    {html_g}
                    <div class="middle-lane"></div>
                    {html_d}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        refresh_ph.empty()
        time.sleep(2)