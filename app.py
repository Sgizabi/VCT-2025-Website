import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import ast
import re
import os

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="VCT 2025 Intel Hub",
    layout="wide",
    page_icon="🎯",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  CUSTOM CSS  — dark esports aesthetic
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700&family=Inter:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0d0e14;
    border-right: 1px solid #1f2130;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span { color: #a0a8c0 !important; font-size: 13px; }

/* Headers */
h1 { font-family: 'Barlow Condensed', sans-serif !important; font-weight: 700 !important;
     font-size: 2.4rem !important; letter-spacing: 0.02em; color: #ffffff !important; }
h2 { font-family: 'Barlow Condensed', sans-serif !important; font-weight: 600 !important;
     font-size: 1.6rem !important; color: #e2e6f0 !important; }
h3 { font-family: 'Barlow Condensed', sans-serif !important; font-weight: 600 !important;
     font-size: 1.25rem !important; color: #c4cbdc !important; }

/* Tab bar */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: #0d0e14;
    border-bottom: 1px solid #1f2130;
    padding: 0 4px;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 14px;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #6b7494;
    padding: 10px 18px;
    border-radius: 4px 4px 0 0;
}
.stTabs [aria-selected="true"] {
    color: #ff4655 !important;
    border-bottom: 2px solid #ff4655 !important;
    background: transparent !important;
}

/* Metric cards */
[data-testid="stMetric"] {
    background: #13141e;
    border: 1px solid #1f2130;
    border-radius: 8px;
    padding: 12px 16px;
}
[data-testid="stMetricValue"] { color: #ff4655 !important; font-family: 'Barlow Condensed', sans-serif !important; font-size: 2rem !important; }
[data-testid="stMetricLabel"] { color: #6b7494 !important; font-size: 11px !important; text-transform: uppercase; letter-spacing: 0.08em; }

/* Divider */
hr { border-color: #1f2130 !important; }

/* Dataframe */
[data-testid="stDataFrame"] { border: 1px solid #1f2130; border-radius: 6px; }

/* Section label pill */
.pill {
    display: inline-block;
    background: #ff4655;
    color: #fff;
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 3px 10px;
    border-radius: 3px;
    margin-bottom: 6px;
}

/* Hero banner */
.hero {
    background: linear-gradient(135deg, #0d0e14 0%, #13141e 50%, #1a1020 100%);
    border: 1px solid #1f2130;
    border-left: 3px solid #ff4655;
    border-radius: 8px;
    padding: 20px 28px;
    margin-bottom: 20px;
}
.hero h1 { margin: 0 !important; font-size: 2.8rem !important; }
.hero p { color: #6b7494; font-size: 14px; margin: 4px 0 0 0; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────
AGENT_ROLES = {
    'Jett':'Duelist','Raze':'Duelist','Reyna':'Duelist','Yoru':'Duelist',
    'Phoenix':'Duelist','Neon':'Duelist','Iso':'Duelist','Waylay':'Duelist',
    'Omen':'Controller','Astra':'Controller','Brimstone':'Controller',
    'Viper':'Controller','Harbor':'Controller','Clove':'Controller',
    'Sova':'Initiator','Breach':'Initiator','Skye':'Initiator',
    'KAY/O':'Initiator','Fade':'Initiator','Gekko':'Initiator','Tejo':'Initiator',
    'Killjoy':'Sentinel','Cypher':'Sentinel','Sage':'Sentinel',
    'Chamber':'Sentinel','Deadlock':'Sentinel','Vyse':'Sentinel',
}
ROLE_COLORS = {
    'Duelist':'#ff4655','Controller':'#4fc3f7',
    'Initiator':'#81c784','Sentinel':'#ffb74d','Flex':'#ce93d8',
}
REGION_COLORS = {
    'Americas':'#ff4655','EMEA':'#4fc3f7',
    'Pacific':'#81c784','China':'#ffb74d','International':'#ce93d8',
}
EVENT_ORDER = [
    'VCT 2025 Americas Kickoff_csvs','VCT 2025 EMEA Kickoff_csvs',
    'VCT 2025 Pacific Kickoff_csvs','VCT 2025 China Kickoff_csvs',
    'Valorant Masters Bangkok 2025_csvs',
    'VCT 2025 Americas Stage 1_csvs','VCT 2025 EMEA Stage 1_csvs',
    'VCT 2025 Pacific Stage 1_csvs','VCT 2025 China Stage 1_csvs',
    'Valorant Masters Toronto 2025_csvs',
    'VCT 2025 Americas Stage 2_csvs','VCT 2025 EMEA Stage 2_csvs',
    'VCT 2025 Pacific Stage 2_csvs','VCT 2025 China Stage 2_csvs',
    'Valorant Champions 2025_csvs',
]
EVENT_LABELS = {
    'VCT 2025 Americas Kickoff_csvs':'Americas KO',
    'VCT 2025 EMEA Kickoff_csvs':'EMEA KO',
    'VCT 2025 Pacific Kickoff_csvs':'Pacific KO',
    'VCT 2025 China Kickoff_csvs':'China KO',
    'Valorant Masters Bangkok 2025_csvs':'Masters Bangkok',
    'VCT 2025 Americas Stage 1_csvs':'Americas S1',
    'VCT 2025 EMEA Stage 1_csvs':'EMEA S1',
    'VCT 2025 Pacific Stage 1_csvs':'Pacific S1',
    'VCT 2025 China Stage 1_csvs':'China S1',
    'Valorant Masters Toronto 2025_csvs':'Masters Toronto',
    'VCT 2025 Americas Stage 2_csvs':'Americas S2',
    'VCT 2025 EMEA Stage 2_csvs':'EMEA S2',
    'VCT 2025 Pacific Stage 2_csvs':'Pacific S2',
    'VCT 2025 China Stage 2_csvs':'China S2',
    'Valorant Champions 2025_csvs':'Champions 2025',
}
TEAM_NAME_MAP = {
    '100 Thieves':'100T','2Game Esports':'2G','All Gamers':'AG','Apeks':'APK',
    'BBL Esports':'BBL','BOOM Esports':'BME','Bilibili Gaming':'BLG',
    'Cloud9':'C9','DRX':'DRX','DetonatioN FocusMe':'DFM',
    'Dragon Ranger Gaming':'DRG','EDward Gaming':'EDG','Evil Geniuses':'EG',
    'FNATIC':'FNC','FURIA':'FUR','FUT Esports':'FUT','FunPlus Phoenix':'FPX',
    'G2 Esports':'G2','GIANTX':'GX','Gen.G':'GEN','Gentle Mates':'M8',
    'Global Esports':'GE','JDG Esports':'JDG','KOI':'MKOI',
    'KRÜ Esports':'KRÜ','Karmine Corp':'KC','LEVIATÁN':'LEV',
    'LOUD':'LOUD','MIBR':'MIBR','NRG':'NRG','Natus Vincere':'NAVI',
    'Nongshim RedForce':'NS','Nova Esports':'NOVA','Paper Rex':'PRX',
    'Rex Regum Qeon':'RRQ','Sentinels':'SEN','T1':'T1','TALON':'TLN',
    'TYLOO':'TYL','Team Heretics':'TH','Team Liquid':'TL',
    'Team Secret':'TS','Team Vitality':'VIT','Xi Lai Gaming':'XLG',
    'ZETA DIVISION':'ZETA','Titan Esports Club':'TEC','Trace Esports':'TE',
    'Wolves Esports':'WOL',
}
ABBREV_TO_FULL = {v: k for k, v in TEAM_NAME_MAP.items()}

PLOTLY_DARK = dict(
    template='plotly_dark',
    paper_bgcolor='#13141e',
    plot_bgcolor='#0d0e14',
    font_color='#c4cbdc',
    font_family='Inter',
)


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def safe_parse_agents(val):
    if pd.isna(val) or val == "":
        return []
    try:
        return ast.literal_eval(val)
    except (ValueError, SyntaxError):
        clean = str(val).replace('[','').replace(']','').replace("'","").replace('"','')
        return [a.strip() for a in clean.split(',') if a.strip()]

def get_region(event_key):
    if 'Americas' in event_key: return 'Americas'
    if 'EMEA' in event_key: return 'EMEA'
    if 'Pacific' in event_key: return 'Pacific'
    if 'China' in event_key: return 'China'
    return 'International'

def parse_eco_col(val):
    try:
        m = re.search(r'(\d+)\s*\((\d+)\)', str(val))
        return (int(m.group(1)), int(m.group(2))) if m else (0, 0)
    except:
        return (0, 0)

def pct_to_float(val):
    try:
        return float(str(val).replace('%','').strip())
    except:
        return np.nan

def normalize_series(s):
    mn, mx = s.min(), s.max()
    if mx == mn:
        return pd.Series([50.0]*len(s), index=s.index)
    return (s - mn) / (mx - mn) * 100

def apply_layout(fig, title="", height=420):
    fig.update_layout(
        title=title,
        height=height,
        margin=dict(l=20, r=20, t=50, b=20),
        **PLOTLY_DARK,
    )
    return fig


# ─────────────────────────────────────────────
#  DATA LOADING  (cached)
# ─────────────────────────────────────────────
@st.cache_data
def load_all_data(data_dir="VCT_data"):
    """
    Try local VCT_data/ folder first, then fall back to flat CSVs
    in the working directory (original single-file layout).
    """
    base_candidates = ["VCT_data", "vct_data", "data"]
    base = None
    for candidate in base_candidates:
        if os.path.isdir(candidate):
            subdirs = [d for d in os.listdir(candidate) if os.path.isdir(os.path.join(candidate, d))]
            if subdirs:
                base = candidate
                break

    if base is None:
        # Fall back to flat single CSV files (original layout)
        return _load_flat_data()

    events = [d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d))]

    def concat_all(filename):
        frames = []
        for ev in events:
            path = os.path.join(base, ev, filename)
            if os.path.exists(path):
                df = pd.read_csv(path)
                df['event'] = ev
                df['region'] = get_region(ev)
                frames.append(df)
        return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

    return {
        'players':    concat_all('player_stats.csv'),
        'matches':    concat_all('matches.csv'),
        'maps_stats': concat_all('maps_stats.csv'),
        'det_maps':   concat_all('detailed_matches_maps.csv'),
        'economy':    concat_all('economy_data.csv'),
        'performance':concat_all('performance_data.csv'),
        'agents':     concat_all('agents_stats.csv'),
        'det_player': concat_all('detailed_matches_player_stats.csv'),
    }


def _load_flat_data():
    """Original single-file fallback."""
    def _safe(path):
        try: return pd.read_csv(path)
        except: return pd.DataFrame()

    p = _safe('player_stats.csv')
    if not p.empty and 'event' in p.columns:
        p['region'] = p['event'].apply(get_region)
    m = _safe('matches.csv')
    if not m.empty and 'event' in m.columns:
        m['region'] = m['event'].apply(get_region)
    ms = _safe('maps_stats.csv')
    if not ms.empty and 'event' in ms.columns:
        ms['region'] = ms['event'].apply(get_region)
    dm = _safe('detailed_matches_maps.csv')
    if not dm.empty and 'event' in dm.columns:
        dm['region'] = dm['event'].apply(get_region)
    eco = _safe('economy_data.csv')
    if not eco.empty and 'event' in eco.columns:
        eco['region'] = eco['event'].apply(get_region)
    return {
        'players': p, 'matches': m, 'maps_stats': ms, 'det_maps': dm,
        'economy': eco, 'performance': pd.DataFrame(),
        'agents': pd.DataFrame(), 'det_player': pd.DataFrame(),
    }


raw = load_all_data()


# ─────────────────────────────────────────────
#  DATA PROCESSING
# ─────────────────────────────────────────────
@st.cache_data
def process_players(df):
    df = df.copy()
    df = df[df['rounds'] > 50]
    df['agent_list'] = df['agents'].apply(safe_parse_agents)
    df['primary_agent'] = df['agent_list'].apply(lambda x: x[0] if x else None)
    df['role'] = df['primary_agent'].apply(lambda a: AGENT_ROLES.get(a, 'Flex'))
    df['pool_size'] = df['agent_list'].apply(len)
    # Clutch parsing: "5/29" -> won=5, att=29
    def parse_clutch(v):
        try:
            parts = str(v).split('/')
            return int(parts[0]), int(parts[1])
        except:
            return 0, 0
    df[['clutch_won','clutch_att']] = df['clutches'].apply(
        lambda x: pd.Series(parse_clutch(x)))
    df['clutch_rate'] = df.apply(
        lambda r: r['clutch_won']/r['clutch_att'] if r['clutch_att'] > 0 else 0, axis=1)
    # Region from event
    if 'region' not in df.columns:
        df['region'] = df['event'].apply(get_region)
    # Clean display name: team abbrev → full name where possible
    df['team_full'] = df['team'].map(ABBREV_TO_FULL).fillna(df['team'])
    # Numeric cleaning — force ALL stat columns to float
    num_cols = ['acs','kd_ratio','kast','adr','kpr','apr','fkpr','fdpr',
                'hs_percent','cl_percent','rating','rounds','kills','deaths',
                'assists','first_kills','first_deaths','k_max','agents_count']
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

@st.cache_data
def process_economy(df):
    if df.empty: return df, pd.DataFrame()
    df = df.copy()
    df = df[df['map'] != 'All Maps']
    for c in ['Eco (won)','Semi-eco (won)','Semi-buy (won)','Full buy(won)']:
        if c in df.columns:
            parsed = df[c].apply(parse_eco_col)
            df[c+'_Att'] = parsed.apply(lambda x: x[0])
            df[c+'_Won'] = parsed.apply(lambda x: x[1])
    # Team-level aggregation
    agg = df.groupby('Team', as_index=False).agg(
        eco_att=('Eco (won)_Att','sum'),
        eco_won=('Eco (won)_Won','sum'),
        seco_att=('Semi-eco (won)_Att','sum'),
        seco_won=('Semi-eco (won)_Won','sum'),
        sbuy_att=('Semi-buy (won)_Att','sum') if 'Semi-buy (won)_Att' in df.columns else ('Eco (won)_Att','sum'),
        sbuy_won=('Semi-buy (won)_Won','sum') if 'Semi-buy (won)_Won' in df.columns else ('Eco (won)_Won','sum'),
        fbuy_att=('Full buy(won)_Att','sum'),
        fbuy_won=('Full buy(won)_Won','sum'),
        pistol_won=('Pistol Won','sum'),
        map_count=('map','count'),
    )
    agg['eco_win_pct']    = agg.apply(lambda r: (r.eco_won+r.seco_won)/(r.eco_att+r.seco_att)*100 if (r.eco_att+r.seco_att)>0 else 0, axis=1)
    agg['fbuy_win_pct']   = agg.apply(lambda r: r.fbuy_won/r.fbuy_att*100 if r.fbuy_att>0 else 0, axis=1)
    agg['pistol_win_pct'] = agg.apply(lambda r: r.pistol_won/(r.map_count*2)*100 if r.map_count>0 else 0, axis=1)
    agg['Team_upper'] = agg['Team'].str.upper().str.strip()
    return df, agg

@st.cache_data
def process_maps(maps_df, det_df, matches_df):
    # Clean pct columns
    if not maps_df.empty:
        for col in ['attack_win_percent','defense_win_percent']:
            if col in maps_df.columns:
                maps_df[col] = maps_df[col].apply(pct_to_float)
    # Build map win-rate per team using detailed_maps + matches
    team_map_wr = pd.DataFrame()
    if not det_df.empty and not matches_df.empty:
        try:
            det = det_df.copy()
            mat = matches_df[['match_id','team1','team2']].drop_duplicates()
            merged = det.merge(mat, on='match_id', how='left')
            # Each row is one map played; expand to team perspective
            records = []
            for _, row in merged.iterrows():
                for team in [row['team1'], row['team2']]:
                    if pd.notna(team):
                        records.append({
                            'team': team,
                            'map': row['map_name'],
                            'won': 1 if row['winner'] == team else 0,
                        })
            exp = pd.DataFrame(records)
            if not exp.empty:
                team_map_wr = exp.groupby(['team','map']).agg(
                    wins=('won','sum'), played=('won','count')).reset_index()
                team_map_wr['win_rate'] = team_map_wr['wins'] / team_map_wr['played'] * 100
                team_map_wr['team_abbrev'] = team_map_wr['team'].map(TEAM_NAME_MAP).fillna(team_map_wr['team'])
        except Exception as e:
            pass
    return maps_df, team_map_wr

@st.cache_data
def process_performance(df):
    if df.empty: return df
    df = df.copy()
    for col in ['2K','3K','4K','5K','1v1','1v2','1v3','1v4','1v5','ECON','PL','DE']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    if 'event' in df.columns:
        df['region'] = df['event'].apply(get_region)
    return df

@st.cache_data
def build_master(players_df, eco_agg):
    df = players_df.copy()
    for col in ['kd_ratio','acs','adr','fkpr','cl_percent','kast','rating']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    team_play = df.groupby('team').agg(
        kd_ratio=('kd_ratio','mean'),
        acs=('acs','mean'),
        adr=('adr','mean'),
        fkpr=('fkpr','mean'),
        cl_percent=('cl_percent','mean'),
        kast=('kast','mean'),
        rating=('rating','mean'),
    ).reset_index()
    team_play['team_upper'] = team_play['team'].str.upper().str.strip()
    merged = team_play.merge(eco_agg, left_on='team_upper', right_on='Team_upper', how='inner')
    merged['team_full'] = merged['team'].map(ABBREV_TO_FULL).fillna(merged['team'])
    if 'region' not in merged.columns:
        # infer from team
        def infer_region(abbrev):
            americas = {'100T','EG','C9','LOUD','MIBR','NRG','LEV','KRÜ','FUR','2G'}
            emea = {'FNC','G2','TH','VIT','NAVI','KC','M8','GX','BBL','FUT','MKOI','APK'}
            pacific = {'T1','PRX','DRX','GEN','RRQ','TLN','DFM','NS','ZETA','BME','GE','TS'}
            china = {'EDG','BLG','FPX','JDG','XLG','DRG','NOVA','TYL','TE','WOL','TEC'}
            if abbrev in americas: return 'Americas'
            if abbrev in emea: return 'EMEA'
            if abbrev in pacific: return 'Pacific'
            if abbrev in china: return 'China'
            return 'Other'
        merged['region'] = merged['team'].apply(infer_region)
    return merged


# Run processing
df_players  = process_players(raw['players'])
df_eco_raw, df_eco_agg = process_economy(raw['economy'])
df_maps, df_team_map_wr = process_maps(raw['maps_stats'], raw['det_maps'], raw['matches'])
df_perf     = process_performance(raw['performance'])
df_master   = build_master(df_players, df_eco_agg)
df_matches  = raw['matches'].copy()
df_det_maps = raw['det_maps'].copy()
df_agents   = raw['agents'].copy()
df_det_player = raw['det_player'].copy()

# Mark high-stakes matches
if not df_matches.empty and 'week' in df_matches.columns:
    HIGH_STAKE_KW = ['lower','elimination','grand final','decider','final','semifinal','quarterfinal','playoff']
    def is_high_stakes(row):
        w = (str(row.get('week','')).lower() + ' ' + str(row.get('stage','')).lower())
        return any(kw in w for kw in HIGH_STAKE_KW)
    df_matches['is_high_stakes'] = df_matches.apply(is_high_stakes, axis=1)


# ─────────────────────────────────────────────
#  SIDEBAR — GLOBAL FILTERS
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎯 VCT 2025 Intel")
    st.markdown("---")

    all_regions = ['All Regions'] + sorted(df_players['region'].dropna().unique().tolist())
    sel_region = st.selectbox("Region Filter", all_regions)

    all_events_sorted = [e for e in EVENT_ORDER if e in df_players['event'].unique()]
    event_display = ['All Events'] + [EVENT_LABELS.get(e, e) for e in all_events_sorted]
    sel_event_label = st.selectbox("Event Filter", event_display)
    sel_event = None
    if sel_event_label != 'All Events':
        label_to_key = {v: k for k, v in EVENT_LABELS.items()}
        sel_event = label_to_key.get(sel_event_label)

    min_rounds = st.slider("Min Rounds Played", 50, 300, 100, 25)

    st.markdown("---")
    st.markdown("<p style='color:#6b7494;font-size:12px'>Data: Kaggle VCT 2025 Dataset<br>Covering 15 events across all 4 regions + internationals</p>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  FILTER HELPERS
# ─────────────────────────────────────────────
def filter_players(df):
    d = df[df['rounds'] >= min_rounds].copy()
    if sel_region != 'All Regions':
        d = d[d['region'] == sel_region]
    if sel_event:
        d = d[d['event'] == sel_event]
    return d

def filter_matches(df):
    if df.empty: return df
    d = df.copy()
    if sel_region != 'All Regions':
        d = d[d.get('region', pd.Series(dtype=str)) == sel_region] if 'region' in d.columns else d
    if sel_event:
        d = d[d['event'] == sel_event]
    return d


# ─────────────────────────────────────────────
#  HERO BANNER
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>VCT 2025 INTEL HUB</h1>
  <p>Full-season analytics across 15 events · 4 regions · 50 teams · 324 players</p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  TOP KPI STRIP
# ─────────────────────────────────────────────
fp = filter_players(df_players)
fm = filter_matches(df_matches)

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Players", f"{fp['player_name'].nunique():,}")
k2.metric("Teams", f"{fp['team'].nunique():,}")
k3.metric("Matches", f"{len(fm):,}" if not fm.empty else "—")
k4.metric("Avg ACS", f"{fp['acs'].mean():.0f}" if not fp.empty else "—")
k5.metric("Avg K/D", f"{fp['kd_ratio'].mean():.2f}" if not fp.empty else "—")

st.markdown("---")


# ─────────────────────────────────────────────
#  TABS
# ─────────────────────────────────────────────
tabs = st.tabs([
    "🔬 Overview",
    "👤 Player Scouting",
    "📈 Season Arcs",
    "🛡️ Team Analysis",
    "🗺️ Map Mastery",
    "💥 Clutch & Pressure",
    "🎯 Agent Meta",
    "📊 Report Card",
])


# ══════════════════════════════════════════════
#  TAB 1 — OVERVIEW  (scatter: team bubble)
# ══════════════════════════════════════════════
with tabs[0]:
    st.markdown('<div class="pill">TEAM COMMAND CENTER</div>', unsafe_allow_html=True)
    st.markdown("### Team Performance Landscape")

    # build filtered master
    fp_t = filter_players(df_players)
    team_agg = fp_t.groupby('team').agg(
        kd_ratio=('kd_ratio','mean'), acs=('acs','mean'),
        adr=('adr','mean'), fkpr=('fkpr','mean'),
        cl_percent=('cl_percent','mean'), kast=('kast','mean'),
        players=('player_name','nunique'),
    ).reset_index()
    team_agg['region'] = team_agg['team'].apply(
        lambda t: fp_t[fp_t['team']==t]['region'].mode()[0] if len(fp_t[fp_t['team']==t])>0 else 'Other')

    METRICS = {
        'Avg ACS':'acs','K/D Ratio':'kd_ratio','ADR':'adr',
        'FK/Round':'fkpr','Clutch %':'cl_percent','KAST %':'kast',
    }
    c1, c2, c3 = st.columns(3)
    x_met = c1.selectbox("X-Axis", list(METRICS.keys()), index=0)
    y_met = c2.selectbox("Y-Axis", list(METRICS.keys()), index=1)
    s_met = c3.selectbox("Bubble Size", list(METRICS.keys()), index=2)

    if not team_agg.empty:
        fig = px.scatter(
            team_agg, x=METRICS[x_met], y=METRICS[y_met],
            size=METRICS[s_met], color='region',
            hover_name='team', hover_data={METRICS[x_met]:':.2f', METRICS[y_met]:':.2f'},
            color_discrete_map=REGION_COLORS,
            size_max=50,
        )
        apply_layout(fig, f"{x_met} vs {y_met} — Team Bubbles", height=500)
        fig.update_traces(marker=dict(opacity=0.85, line=dict(width=1, color='#1f2130')))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data for current filters.")

    # Bottom: top-5 per metric strip
    st.markdown("### League Leaders")
    lc = st.columns(3)
    lead_metrics = [('ACS','acs'), ('K/D','kd_ratio'), ('ADR','adr')]
    for col, (label, col_key) in zip(lc, lead_metrics):
        top5 = (fp_t.groupby('player_name')[col_key].mean()
                .sort_values(ascending=False).head(5).reset_index())
        top5.columns = ['Player', label]
        top5[label] = top5[label].round(2)
        col.markdown(f"**Top 5 — {label}**")
        col.dataframe(top5, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════
#  TAB 2 — PLAYER SCOUTING
# ══════════════════════════════════════════════
with tabs[1]:
    st.markdown('<div class="pill">PLAYER SCOUTING</div>', unsafe_allow_html=True)

    fp2 = filter_players(df_players)
    if fp2.empty:
        st.warning("No players match current filters.")
    else:
        sc1, sc2 = st.columns([1, 3])
        with sc1:
            team_list = ['All Teams'] + sorted(fp2['team'].unique())
            sel_team = st.selectbox("Filter by Team", team_list)
            role_list = ['All Roles'] + sorted(fp2['role'].unique())
            sel_role = st.selectbox("Filter by Role", role_list)

            plot_metric = st.selectbox("Scatter Y-Axis", [
                'acs','kd_ratio','adr','kast','fkpr','fdpr','hs_percent',
                'cl_percent','clutch_rate','rating',
            ])

        filtered_scout = fp2.copy()
        if sel_team != 'All Teams':
            filtered_scout = filtered_scout[filtered_scout['team'] == sel_team]
        if sel_role != 'All Roles':
            filtered_scout = filtered_scout[filtered_scout['role'] == sel_role]

        with sc2:
            if not filtered_scout.empty:
                fig_s = px.scatter(
                    filtered_scout, x='rounds', y=plot_metric,
                    color='role', hover_name='player_name',
                    hover_data={'team':True,'rounds':True, plot_metric:':.2f','primary_agent':True},
                    color_discrete_map=ROLE_COLORS,
                )
                apply_layout(fig_s, f"Rounds Played vs {plot_metric.upper()}", height=420)
                fig_s.update_traces(marker=dict(size=8, opacity=0.8, line=dict(width=0.5, color='#0d0e14')))
                st.plotly_chart(fig_s, use_container_width=True)

        # Detailed player stats table
        st.markdown("### Player Stats Table")
        display_cols = ['player_name','team','role','primary_agent','rounds',
                        'rating','acs','kd_ratio','adr','kast','fkpr','hs_percent','clutch_rate']
        display_cols = [c for c in display_cols if c in filtered_scout.columns]
        show_df = filtered_scout[display_cols].sort_values('acs', ascending=False).reset_index(drop=True)
        show_df.columns = [c.replace('_',' ').upper() for c in show_df.columns]
        # Round floats
        for col in show_df.select_dtypes(include='float').columns:
            show_df[col] = show_df[col].round(3)
        st.dataframe(show_df, use_container_width=True, height=320)

        # Head-to-head comparison
        st.markdown("---")
        st.markdown("### Head-to-Head Comparison")
        all_players_sorted = sorted(filtered_scout['player_name'].unique())
        hc1, hc2 = st.columns(2)
        p1 = hc1.selectbox("Player A", all_players_sorted, key='p1')
        p2 = hc2.selectbox("Player B", all_players_sorted,
                            index=min(1, len(all_players_sorted)-1), key='p2')

        radar_metrics = ['acs','kd_ratio','kast','adr','fkpr','cl_percent']
        radar_labels  = ['ACS','K/D','KAST','ADR','FK/R','Clutch%']

        def player_radar_vals(name, df, metrics):
            row = df[df['player_name']==name]
            if row.empty: return [0]*len(metrics)
            vals = []
            for m in metrics:
                col_data = df[m].dropna()
                if col_data.empty or col_data.max()==col_data.min():
                    vals.append(50.0)
                else:
                    v = row[m].values[0]
                    vals.append((v - col_data.min())/(col_data.max()-col_data.min())*100)
            return vals

        v1 = player_radar_vals(p1, filtered_scout, radar_metrics)
        v2 = player_radar_vals(p2, filtered_scout, radar_metrics)

        fig_r = go.Figure()
        for vals, name, color in [(v1, p1, '#ff4655'), (v2, p2, '#4fc3f7')]:
            fig_r.add_trace(go.Scatterpolar(
                r=vals+[vals[0]], theta=radar_labels+[radar_labels[0]],
                fill='toself', name=name, line_color=color, opacity=0.85,
            ))
        apply_layout(fig_r, "Normalized Skill Radar (100 = league best)", height=420)
        fig_r.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0,100], tickfont=dict(size=9)),
                       angularaxis=dict(tickfont=dict(size=11, color='#c4cbdc'))),
        )
        st.plotly_chart(fig_r, use_container_width=True)


# ══════════════════════════════════════════════
#  TAB 3 — SEASON ARCS
# ══════════════════════════════════════════════
with tabs[2]:
    st.markdown('<div class="pill">SEASON ARCS</div>', unsafe_allow_html=True)
    st.markdown("### Player ACS Trajectory Across the Season")

    # Build per-event player data — only events player appeared in
    event_player_data = []
    for ev in EVENT_ORDER:
        ev_df = df_players[df_players['event'] == ev]
        if ev_df.empty: continue
        ev_df = ev_df[ev_df['rounds'] >= 50][['player_name','team','region','acs','kd_ratio','adr','rating']].copy()
        ev_df['event_key'] = ev
        ev_df['event_label'] = EVENT_LABELS.get(ev, ev)
        ev_df['event_idx'] = EVENT_ORDER.index(ev)
        event_player_data.append(ev_df)

    if event_player_data:
        arc_df = pd.concat(event_player_data, ignore_index=True)
        # filter by sidebar
        if sel_region != 'All Regions':
            arc_df = arc_df[arc_df['region'] == sel_region]

        # Find players with >=2 events
        multi_event = arc_df.groupby('player_name')['event_idx'].nunique()
        multi_players = multi_event[multi_event >= 2].index.tolist()

        arc_col1, arc_col2 = st.columns([1, 3])
        with arc_col1:
            arc_metric = st.selectbox("Metric", ['acs','kd_ratio','adr','rating'], key='arc_metric',
                                      format_func=lambda x: {'acs':'ACS','kd_ratio':'K/D','adr':'ADR','rating':'Rating'}[x])
            top_n = st.slider("Show Top N Players", 3, 20, 8)
            show_avg = st.checkbox("Show Region Average", value=True)

            # Rank by final event performance
            final_ev = arc_df[arc_df['event_idx'] == arc_df['event_idx'].max()]
            top_players = (final_ev.groupby('player_name')[arc_metric].mean()
                           .sort_values(ascending=False).head(top_n).index.tolist())
            # intersect with multi-event
            top_players = [p for p in top_players if p in multi_players]

        with arc_col2:
            if top_players:
                arc_plot = arc_df[arc_df['player_name'].isin(top_players)].copy()
                arc_plot['team_label'] = arc_plot['player_name'] + ' (' + arc_plot['team'] + ')'

                fig_arc = px.line(
                    arc_plot.sort_values('event_idx'),
                    x='event_label', y=arc_metric,
                    color='player_name',
                    markers=True, hover_name='player_name',
                    hover_data={'team':True, arc_metric:':.2f'},
                )
                if show_avg:
                    avg_by_event = arc_df.groupby(['event_label','event_idx'])[arc_metric].mean().reset_index()
                    fig_arc.add_trace(go.Scatter(
                        x=avg_by_event['event_label'], y=avg_by_event[arc_metric],
                        mode='lines', name='League Avg',
                        line=dict(dash='dot', color='#ffffff', width=1.5),
                        opacity=0.5,
                    ))
                apply_layout(fig_arc, f"{arc_metric.upper()} Across Season", height=440)
                fig_arc.update_layout(
                    xaxis_tickangle=-30,
                    legend=dict(orientation='v', font=dict(size=10)),
                )
                st.plotly_chart(fig_arc, use_container_width=True)
            else:
                st.info("No multi-event players found in current filter.")

    # Performance trajectory classification
    st.markdown("---")
    st.markdown("### Season Arc Classification")

    if event_player_data and multi_players:
        arc_full = pd.concat(event_player_data, ignore_index=True)
        if sel_region != 'All Regions':
            arc_full = arc_full[arc_full['region'] == sel_region]

        MIN_EV = 3
        qualified = arc_full[arc_full['player_name'].isin(multi_players)]
        ev_counts = qualified.groupby('player_name')['event_idx'].nunique()
        qualified_players = ev_counts[ev_counts >= MIN_EV].index.tolist()

        arc_classes = []
        for p in qualified_players:
            p_df = qualified[qualified['player_name']==p].sort_values('event_idx')
            vals = p_df['acs'].values
            if len(vals) < 3: continue
            x = np.arange(len(vals))
            z = np.polyfit(x, vals, 2)
            slope_first = vals[len(vals)//2:].mean() - vals[:len(vals)//2].mean()
            concavity = z[0]  # positive = U shape, negative = hump
            last_acs = vals[-1]; first_acs = vals[0]
            if slope_first > 15 and last_acs > first_acs:
                arc_type = '🚀 Rocket Ship'
            elif slope_first < -15 and last_acs < first_acs:
                arc_type = '🔥 Burnout'
            elif concavity < -0.5 and vals[len(vals)//2] > first_acs and last_acs < vals[len(vals)//2]:
                arc_type = '⬇️ Peaked Early'
            elif last_acs - first_acs > 5 and abs(slope_first) <= 15:
                arc_type = '📈 Steady Climb'
            else:
                arc_type = '➡️ Consistent'
            team = p_df['team'].iloc[-1]
            arc_classes.append({'Player': p, 'Team': team, 'Arc Type': arc_type,
                                 'Start ACS': round(first_acs,1), 'End ACS': round(last_acs,1),
                                 'Change': round(last_acs - first_acs, 1)})

        if arc_classes:
            arc_class_df = pd.DataFrame(arc_classes).sort_values('Change', ascending=False)
            # Summary counts
            type_counts = arc_class_df['Arc Type'].value_counts().reset_index()
            type_counts.columns = ['Arc Type','Count']
            fig_arc_bar = px.bar(type_counts, x='Arc Type', y='Count',
                                 color='Arc Type', text='Count',
                                 color_discrete_sequence=['#ff4655','#4fc3f7','#81c784','#ffb74d','#ce93d8'])
            apply_layout(fig_arc_bar, "Season Arc Distribution", height=280)
            fig_arc_bar.update_traces(textposition='outside')
            st.plotly_chart(fig_arc_bar, use_container_width=True)
            st.dataframe(arc_class_df, use_container_width=True, hide_index=True)
        else:
            st.info("Not enough events per player to classify arcs in current filter.")


# ══════════════════════════════════════════════
#  TAB 4 — TEAM ANALYSIS
# ══════════════════════════════════════════════
with tabs[3]:
    st.markdown('<div class="pill">TEAM ANALYSIS</div>', unsafe_allow_html=True)

    subtabs = st.tabs(["Style Radar", "Economy Deep-Dive", "Team Heatmap"])

    with subtabs[0]:
        st.markdown("### Team Style Radar")
        # Use master for full-name teams
        if not df_master.empty:
            team_opts = sorted(df_master['team_full'].unique())
            tc1, tc2 = st.columns(2)
            t_a = tc1.selectbox("Team A", team_opts, key='ra')
            t_b = tc2.selectbox("Team B", ['None'] + [t for t in team_opts if t != t_a], key='rb')

            r_cols    = ['kd_ratio','fkpr','cl_percent','eco_win_pct','pistol_win_pct','fbuy_win_pct']
            r_labels  = ['K/D','First Kills/R','Clutch %','Eco Win %','Pistol Win %','Full Buy Win %']

            def team_normed(tname):
                row = df_master[df_master['team_full']==tname]
                if row.empty: return [0]*len(r_cols)
                vals = []
                for c in r_cols:
                    if c not in df_master.columns:
                        vals.append(50.0); continue
                    col_data = df_master[c].dropna()
                    v = row[c].values[0]
                    mn, mx = col_data.min(), col_data.max()
                    vals.append((v-mn)/(mx-mn)*100 if mx!=mn else 50.0)
                return vals

            fig_tr = go.Figure()
            for tname, color in [(t_a,'#ff4655'), (t_b,'#4fc3f7')]:
                if tname == 'None': continue
                v = team_normed(tname)
                fig_tr.add_trace(go.Scatterpolar(
                    r=v+[v[0]], theta=r_labels+[r_labels[0]],
                    fill='toself', name=tname, line_color=color, opacity=0.8,
                ))
            apply_layout(fig_tr, "Team Style Comparison (normalized 0–100)", height=460)
            fig_tr.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0,100])),
            )
            st.plotly_chart(fig_tr, use_container_width=True)

    with subtabs[1]:
        st.markdown("### Economy Win Rates by Team")
        if not df_eco_agg.empty:
            eco_plot = df_eco_agg.copy()
            eco_plot['team_full'] = eco_plot['Team'].map(ABBREV_TO_FULL).fillna(eco_plot['Team'])
            eco_plot = eco_plot.sort_values('eco_win_pct', ascending=False).head(30)

            eco_melt = eco_plot.melt(
                id_vars='team_full',
                value_vars=['eco_win_pct','fbuy_win_pct','pistol_win_pct'],
                var_name='Round Type', value_name='Win Rate %'
            )
            eco_melt['Round Type'] = eco_melt['Round Type'].map({
                'eco_win_pct':'Eco/Semi-Eco',
                'fbuy_win_pct':'Full Buy',
                'pistol_win_pct':'Pistol',
            })
            fig_eco = px.bar(
                eco_melt, x='team_full', y='Win Rate %', color='Round Type',
                barmode='group', text_auto='.0f',
                color_discrete_map={'Eco/Semi-Eco':'#ff4655','Full Buy':'#4fc3f7','Pistol':'#ffb74d'},
            )
            apply_layout(fig_eco, "Round Economy Win Rates (%)", height=440)
            fig_eco.update_layout(xaxis_tickangle=-40, bargap=0.15)
            st.plotly_chart(fig_eco, use_container_width=True)

            # Pistol vs full-buy scatter
            st.markdown("#### Pistol Impact vs Full Buy Dominance")
            fig_pf = px.scatter(
                eco_plot, x='pistol_win_pct', y='fbuy_win_pct',
                color='eco_win_pct', hover_name='team_full',
                text='Team',
                color_continuous_scale='RdYlGn',
                labels={'pistol_win_pct':'Pistol Win %','fbuy_win_pct':'Full Buy Win %','eco_win_pct':'Eco Win %'},
            )
            apply_layout(fig_pf, "Pistol Win % vs Full Buy Win % (colour = Eco Win %)", height=420)
            fig_pf.update_traces(textposition='top center', textfont_size=9)
            fig_pf.add_hline(y=50, line_dash='dot', line_color='#6b7494', line_width=1)
            fig_pf.add_vline(x=50, line_dash='dot', line_color='#6b7494', line_width=1)
            st.plotly_chart(fig_pf, use_container_width=True)

    with subtabs[2]:
        st.markdown("### Team Report Card Heatmap")
        if not df_master.empty:
            heat_cols = [c for c in ['kd_ratio','fkpr','cl_percent','eco_win_pct','pistol_win_pct','fbuy_win_pct','acs','adr'] if c in df_master.columns]
            heat_labels = {
                'kd_ratio':'K/D Ratio','fkpr':'FK/Round','cl_percent':'Clutch %',
                'eco_win_pct':'Eco Win %','pistol_win_pct':'Pistol Win %',
                'fbuy_win_pct':'Full Buy Win %','acs':'Avg ACS','adr':'ADR',
            }
            df_h = df_master.set_index('team_full')[heat_cols].copy()
            df_norm_h = df_h.apply(normalize_series)
            fig_heat = go.Figure(data=go.Heatmap(
                z=df_norm_h.T.values,
                x=df_norm_h.index.tolist(),
                y=[heat_labels.get(c,c) for c in heat_cols],
                colorscale='RdYlGn',
                showscale=True,
                text=[[f"{df_h.loc[team, col]:.1f}" for team in df_h.index] for col in heat_cols],
                hovertemplate='<b>%{x}</b><br>%{y}: %{text}<extra></extra>',
            ))
            apply_layout(fig_heat, "All Teams — Normalized Performance Heatmap", height=max(360, len(heat_cols)*45))
            fig_heat.update_layout(xaxis_tickangle=-40)
            st.plotly_chart(fig_heat, use_container_width=True)


# ══════════════════════════════════════════════
#  TAB 5 — MAP MASTERY
# ══════════════════════════════════════════════
with tabs[4]:
    st.markdown('<div class="pill">MAP MASTERY</div>', unsafe_allow_html=True)

    map_subtabs = st.tabs(["Attack vs Defense Bias", "Team Map Pool", "Map Pick Rates"])

    with map_subtabs[0]:
        st.markdown("### Map Side Bias")
        if not df_maps.empty and 'attack_win_percent' in df_maps.columns:
            all_map_events = ['All Events (weighted)'] + sorted(df_maps['event'].unique())
            map_ev_label = [EVENT_LABELS.get(e,e) if e!='All Events (weighted)' else e for e in all_map_events]
            ev_sel_label = st.selectbox("Event", map_ev_label)
            ev_sel_key = all_map_events[map_ev_label.index(ev_sel_label)]

            plot_maps = df_maps.copy()
            for c in ['attack_win_percent','defense_win_percent','times_played']:
                plot_maps[c] = pd.to_numeric(plot_maps[c].astype(str).str.replace('%',''), errors='coerce').fillna(0)

            if ev_sel_key == 'All Events (weighted)':
                def w_avg(x, weights):
                    try: return np.average(x, weights=weights.loc[x.index])
                    except: return x.mean()
                map_grp = plot_maps.groupby('map_name')
                agg_maps = map_grp.apply(lambda g: pd.Series({
                    'attack_win_percent': np.average(g['attack_win_percent'], weights=g['times_played']+1e-9),
                    'defense_win_percent': np.average(g['defense_win_percent'], weights=g['times_played']+1e-9),
                    'times_played': g['times_played'].sum(),
                })).reset_index()
                title = "Global Map Side Bias (All Events — Weighted)"
            else:
                agg_maps = plot_maps[plot_maps['event']==ev_sel_key].copy()
                title = f"Map Side Bias — {ev_sel_label}"

            if not agg_maps.empty:
                melt = agg_maps.melt(
                    id_vars='map_name',
                    value_vars=['attack_win_percent','defense_win_percent'],
                    var_name='Side', value_name='Win %',
                )
                melt['Side'] = melt['Side'].map({'attack_win_percent':'⚔️ Attack','defense_win_percent':'🛡️ Defense'})
                fig_mb = px.bar(
                    melt.sort_values('Win %', ascending=False),
                    x='map_name', y='Win %', color='Side', barmode='group',
                    text_auto='.1f',
                    color_discrete_map={'⚔️ Attack':'#ff4655','🛡️ Defense':'#4fc3f7'},
                )
                apply_layout(fig_mb, title, height=400)
                fig_mb.add_hline(y=50, line_dash='dot', line_color='white', line_width=1)
                fig_mb.update_layout(xaxis_title="Map", yaxis_title="Win Rate %")
                st.plotly_chart(fig_mb, use_container_width=True)

    with map_subtabs[1]:
        st.markdown("### Team Map Win Rate Radar")
        if not df_team_map_wr.empty:
            active_teams = (df_team_map_wr.groupby('team')['played'].sum()
                            .where(lambda x: x >= 5).dropna().index.tolist())
            active_teams_sorted = sorted(active_teams)
            sel_teams_map = st.multiselect(
                "Select Teams", active_teams_sorted,
                default=active_teams_sorted[:3] if len(active_teams_sorted)>=3 else active_teams_sorted,
            )
            all_maps = sorted(df_team_map_wr['map'].unique())
            if sel_teams_map:
                fig_mr = go.Figure()
                colors = ['#ff4655','#4fc3f7','#81c784','#ffb74d','#ce93d8','#ff8c00','#00e5ff']
                for i, team in enumerate(sel_teams_map):
                    t_data = df_team_map_wr[df_team_map_wr['team']==team].set_index('map')
                    vals = [float(t_data.loc[m,'win_rate']) if m in t_data.index else 0.0 for m in all_maps]
                    vals_closed = vals + [vals[0]]
                    theta_closed = all_maps + [all_maps[0]]
                    fig_mr.add_trace(go.Scatterpolar(
                        r=vals_closed, theta=theta_closed,
                        fill='toself', name=team,
                        line_color=colors[i % len(colors)], opacity=0.75,
                    ))
                apply_layout(fig_mr, "Map Win Rate % by Team", height=480)
                fig_mr.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0,100],
                                               tickvals=[0,25,50,75,100])),
                )
                st.plotly_chart(fig_mr, use_container_width=True)
                # Table
                pivot = df_team_map_wr[df_team_map_wr['team'].isin(sel_teams_map)].pivot_table(
                    index='team', columns='map', values='win_rate', aggfunc='mean').round(1)
                pivot.columns.name = None
                st.dataframe(pivot, use_container_width=True)
        else:
            st.info("No map win-rate data available.")

    with map_subtabs[2]:
        st.markdown("### Map Pick & Play Rates")
        if not df_det_maps.empty:
            # Play frequency
            map_counts = df_det_maps.groupby('map_name').size().reset_index(name='times_played')
            # Picks vs deciders
            if 'picked_by' in df_det_maps.columns:
                pick_df = df_det_maps.copy()
                pick_df['is_decider'] = pick_df['picked_by'].str.lower().str.contains('decider', na=False)
                decider_counts = pick_df.groupby('map_name')['is_decider'].sum().reset_index(name='decider_count')
                map_counts = map_counts.merge(decider_counts, on='map_name', how='left')
                map_counts['pick_count'] = map_counts['times_played'] - map_counts['decider_count'].fillna(0)
                map_counts['pct_picked'] = map_counts['pick_count'] / map_counts['times_played'] * 100

            fig_mp = px.bar(
                map_counts.sort_values('times_played', ascending=False),
                x='map_name', y='times_played', color='times_played',
                text='times_played', color_continuous_scale='Reds',
                labels={'map_name':'Map','times_played':'Maps Played'},
            )
            apply_layout(fig_mp, "Total Maps Played per Map", height=360)
            fig_mp.update_traces(textposition='outside')
            st.plotly_chart(fig_mp, use_container_width=True)

            # Top teams by pick
            if 'picked_by' in df_det_maps.columns:
                picks_only = df_det_maps[~df_det_maps['picked_by'].str.lower().str.contains('decider', na=True)]
                top_pickers = (picks_only.groupby(['picked_by','map_name']).size()
                               .reset_index(name='picks')
                               .sort_values('picks', ascending=False).head(20))
                fig_tp = px.bar(
                    top_pickers, x='picked_by', y='picks', color='map_name',
                    barmode='stack',
                    labels={'picked_by':'Team','picks':'Times Picked'},
                )
                apply_layout(fig_tp, "Top Map Pickers by Team", height=380)
                fig_tp.update_layout(xaxis_tickangle=-35)
                st.plotly_chart(fig_tp, use_container_width=True)


# ══════════════════════════════════════════════
#  TAB 6 — CLUTCH & PRESSURE
# ══════════════════════════════════════════════
with tabs[5]:
    st.markdown('<div class="pill">CLUTCH & PRESSURE</div>', unsafe_allow_html=True)

    c_subtabs = st.tabs(["Big Game Hunters", "Pressure Gauge", "Multi-Kill Stars"])

    with c_subtabs[0]:
        st.markdown("### Big Game Hunters — Regional vs International ACS")
        fp3 = filter_players(df_players)
        if not fp3.empty:
            hunt_metric = st.selectbox("Metric", ['acs','kd_ratio','adr','rating'],
                                       format_func=lambda x: {'acs':'ACS','kd_ratio':'K/D','adr':'ADR','rating':'Rating'}[x],
                                       key='hunt_met')
            intl_events = [e for e in EVENT_ORDER if 'Masters' in e or 'Champions' in e]
            reg_events  = [e for e in EVENT_ORDER if e not in intl_events]

            intl_df = df_players[(df_players['event'].isin(intl_events)) & (df_players['rounds']>=50)]
            reg_df  = df_players[(df_players['event'].isin(reg_events)) & (df_players['rounds']>=50)]

            intl_avg = intl_df.groupby('player_name')[hunt_metric].mean().rename('International')
            reg_avg  = reg_df.groupby('player_name')[hunt_metric].mean().rename('Regional')

            hunter = pd.concat([intl_avg, reg_avg], axis=1).dropna()
            if sel_region != 'All Regions':
                regional_players = df_players[df_players['region']==sel_region]['player_name'].unique()
                hunter = hunter[hunter.index.isin(regional_players)]

            if not hunter.empty:
                hunter['Diff'] = hunter['International'] - hunter['Regional']
                hunter.index.name = 'Player'
                hunter = hunter.reset_index()
                hunter['team'] = hunter['Player'].map(
                    df_players.groupby('player_name')['team'].last())
                hunter['role'] = hunter['Player'].map(
                    fp3.groupby('player_name')['role'].last())

                fig_hunt = px.scatter(
                    hunter, x='Regional', y='International',
                    color='role', hover_name='Player',
                    hover_data={'team':True,'Diff':':.2f'},
                    color_discrete_map=ROLE_COLORS, size_max=10,
                )
                mn = min(hunter['Regional'].min(), hunter['International'].min())
                mx = max(hunter['Regional'].max(), hunter['International'].max())
                fig_hunt.add_shape(type='line', x0=mn, y0=mn, x1=mx, y1=mx,
                                   line=dict(dash='dot', color='white', width=1))
                apply_layout(fig_hunt, f"Regional vs International {hunt_metric.upper()} — above line = elevates at events", height=440)
                fig_hunt.add_annotation(x=mx*0.98, y=mx, text="⬆ Performs better at internationals",
                                        showarrow=False, font=dict(size=10, color='#81c784'), xanchor='right')
                fig_hunt.add_annotation(x=mx*0.98, y=mn+(mx-mn)*0.05,
                                        text="⬇ Better in regional play",
                                        showarrow=False, font=dict(size=10, color='#ff4655'), xanchor='right')
                st.plotly_chart(fig_hunt, use_container_width=True)

                st.markdown("#### Performance Matrix")
                st.dataframe(
                    hunter.sort_values('Diff', ascending=False)
                          .rename(columns={'Player':'Player','team':'Team','role':'Role'})
                          .assign(International=lambda d: d['International'].round(2),
                                  Regional=lambda d: d['Regional'].round(2),
                                  Diff=lambda d: d['Diff'].round(2))
                          .reset_index(drop=True),
                    use_container_width=True, height=300,
                )

    with c_subtabs[1]:
        st.markdown("### Tournament Pressure Gauge")
        st.caption("Teams above the diagonal win proportionally more high-stakes matches than regular matches.")
        if not df_matches.empty and 'is_high_stakes' in df_matches.columns:
            fm2 = filter_matches(df_matches)
            hs_wins = fm2[fm2['is_high_stakes']].groupby('winner').size().rename('High Stakes Wins')
            reg_wins = fm2[~fm2['is_high_stakes']].groupby('winner').size().rename('Regular Wins')
            hs_total = fm2[fm2['is_high_stakes']].groupby('winner').size().rename('hs_total')
            hs_played = fm2[fm2['is_high_stakes']].apply(
                lambda r: [r['team1'], r['team2']], axis=1
            ).explode().value_counts().rename('hs_played')
            reg_played = fm2[~fm2['is_high_stakes']].apply(
                lambda r: [r['team1'], r['team2']], axis=1
            ).explode().value_counts().rename('reg_played')

            pressure_df = pd.concat([hs_wins, reg_wins, hs_played, reg_played], axis=1).fillna(0)
            # Use RATES not raw counts
            pressure_df['hs_win_rate']  = pressure_df['High Stakes Wins'] / pressure_df['hs_played'].clip(lower=1) * 100
            pressure_df['reg_win_rate'] = pressure_df['Regular Wins'] / pressure_df['reg_played'].clip(lower=1) * 100
            pressure_df['pressure_score'] = pressure_df['hs_win_rate'] - pressure_df['reg_win_rate']
            pressure_df = pressure_df[pressure_df['hs_played'] >= 3].copy()
            pressure_df.index.name = 'Team'
            pressure_df = pressure_df.reset_index()
            pressure_df['total_hs'] = pressure_df['High Stakes Wins']

            fig_pres = px.scatter(
                pressure_df, x='reg_win_rate', y='hs_win_rate',
                text='Team', size='total_hs', size_max=35,
                color='pressure_score', color_continuous_scale='RdYlGn',
                labels={'reg_win_rate':'Regular Win Rate %','hs_win_rate':'High Stakes Win Rate %'},
                hover_data={'pressure_score':':.1f','total_hs':True},
            )
            mn = min(pressure_df['reg_win_rate'].min(), pressure_df['hs_win_rate'].min())-5
            mx = max(pressure_df['reg_win_rate'].max(), pressure_df['hs_win_rate'].max())+5
            fig_pres.add_shape(type='line', x0=mn, y0=mn, x1=mx, y1=mx,
                               line=dict(dash='dot', color='white', width=1))
            apply_layout(fig_pres, "High Stakes Win Rate vs Regular Win Rate (colour = improvement at high stakes)", height=460)
            fig_pres.update_traces(textposition='top center', textfont_size=9, marker_opacity=0.85)
            st.plotly_chart(fig_pres, use_container_width=True)

    with c_subtabs[2]:
        st.markdown("### Multi-Kill & Clutch Stars")
        if not df_perf.empty:
            perf_plot = df_perf.copy()
            if sel_region != 'All Regions' and 'region' in perf_plot.columns:
                perf_plot = perf_plot[perf_plot['region'] == sel_region]

            # Aggregate per player
            perf_agg = perf_plot.groupby(['Player','Team']).agg(
                aces=('5K','sum'), quads=('4K','sum'), triples=('3K','sum'),
                v1=('1v1','sum'), v2=('1v2','sum'), v3=('1v3','sum'),
                v4=('1v4','sum'), v5=('1v5','sum'),
                plants=('PL','sum'), defuses=('DE','sum'),
            ).reset_index()
            perf_agg['total_clutches'] = perf_agg[['v1','v2','v3','v4','v5']].sum(axis=1)
            perf_agg['multikill_score'] = (perf_agg['aces']*5 + perf_agg['quads']*3 + perf_agg['triples'])

            pc1, pc2 = st.columns(2)
            with pc1:
                st.markdown("#### 🎯 Ace Leaders (5K)")
                top_aces = perf_agg.nlargest(10, 'aces')[['Player','Team','aces','quads','triples']]
                st.dataframe(top_aces.reset_index(drop=True), use_container_width=True, hide_index=True)
            with pc2:
                st.markdown("#### 💪 Clutch Masters")
                top_clutch = perf_agg.nlargest(10, 'total_clutches')[['Player','Team','v1','v2','v3','v4','v5','total_clutches']]
                top_clutch.columns = ['Player','Team','1v1','1v2','1v3','1v4','1v5','Total']
                st.dataframe(top_clutch.reset_index(drop=True), use_container_width=True, hide_index=True)

            # Scatter: clutches vs aces
            fig_mk = px.scatter(
                perf_agg[perf_agg['total_clutches'] > 0], 
                x='total_clutches', y='aces',
                size='multikill_score', hover_name='Player',
                color='multikill_score', color_continuous_scale='Hot',
                text='Player',
                labels={'total_clutches':'Total Clutches Won','aces':'Aces (5K)'},
            )
            apply_layout(fig_mk, "Clutch Wins vs Aces — bubble size = overall multikill score", height=420)
            fig_mk.update_traces(textposition='top center', textfont_size=8, marker_opacity=0.85)
            st.plotly_chart(fig_mk, use_container_width=True)
        else:
            st.info("Performance data not available.")


# ══════════════════════════════════════════════
#  TAB 7 — AGENT META
# ══════════════════════════════════════════════
with tabs[6]:
    st.markdown('<div class="pill">AGENT META</div>', unsafe_allow_html=True)

    meta_subtabs = st.tabs(["Pick Rates", "Agent × Map", "Role Balance"])

    with meta_subtabs[0]:
        st.markdown("### Agent Pick Rates Across the Season")
        # Build from player agent lists
        fp4 = filter_players(df_players)
        agent_rows = []
        for _, row in fp4.iterrows():
            for agent in row['agent_list']:
                agent_rows.append({'agent': agent, 'region': row['region'],
                                   'role': AGENT_ROLES.get(agent,'Flex'),
                                   'event': row['event']})
        if agent_rows:
            agent_pick_df = pd.DataFrame(agent_rows)
            pick_counts = agent_pick_df.groupby(['agent','role']).size().reset_index(name='picks')
            pick_counts = pick_counts.sort_values('picks', ascending=False)

            fig_ap = px.bar(
                pick_counts.head(25), x='agent', y='picks', color='role',
                color_discrete_map=ROLE_COLORS, text='picks',
            )
            apply_layout(fig_ap, "Top 25 Agents by Player-Event Appearances", height=400)
            fig_ap.update_traces(textposition='outside', textfont_size=9)
            fig_ap.update_layout(xaxis_tickangle=-35)
            st.plotly_chart(fig_ap, use_container_width=True)

    with meta_subtabs[1]:
        st.markdown("### Agent Utilization by Map")
        if not df_agents.empty:
            map_cols_ag = [c for c in df_agents.columns if c not in ['agent_name','total_utilization','event']]
            if sel_event:
                agents_filt = df_agents[df_agents['event'] == sel_event]
            else:
                agents_filt = df_agents
            if not agents_filt.empty and map_cols_ag:
                # Force numeric on all map columns before aggregation
                agents_filt = agents_filt.copy()
                for c in map_cols_ag:
                    agents_filt[c] = pd.to_numeric(agents_filt[c], errors='coerce')
                # Average utilization per agent per map
                ag_map = agents_filt.groupby('agent_name')[map_cols_ag].mean().fillna(0)
                # Filter to agents with meaningful presence
                ag_map = ag_map[ag_map.max(axis=1) > 10]
                fig_ag_heat = go.Figure(data=go.Heatmap(
                    z=ag_map.values,
                    x=ag_map.columns.tolist(),
                    y=ag_map.index.tolist(),
                    colorscale='YlOrRd',
                    showscale=True,
                    text=[[f"{v:.0f}%" for v in row] for row in ag_map.values],
                    hovertemplate='<b>%{y}</b> on %{x}: %{text}<extra></extra>',
                ))
                apply_layout(fig_ag_heat, "Agent Utilization % by Map", height=max(400, len(ag_map)*22))
                st.plotly_chart(fig_ag_heat, use_container_width=True)

    with meta_subtabs[2]:
        st.markdown("### Role Balance by Region")
        fp5 = filter_players(df_players)
        role_region = fp5.groupby(['region','role']).size().reset_index(name='count')
        region_total = fp5.groupby('region').size().rename('total')
        role_region = role_region.merge(region_total, on='region')
        role_region['pct'] = role_region['count'] / role_region['total'] * 100

        fig_rb = px.bar(
            role_region, x='region', y='pct', color='role',
            barmode='stack', text_auto='.0f',
            color_discrete_map=ROLE_COLORS,
            labels={'pct':'% of Players','region':'Region'},
        )
        apply_layout(fig_rb, "Role Distribution per Region (%)", height=380)
        st.plotly_chart(fig_rb, use_container_width=True)


# ══════════════════════════════════════════════
#  TAB 8 — REPORT CARD
# ══════════════════════════════════════════════
with tabs[7]:
    st.markdown('<div class="pill">REPORT CARD</div>', unsafe_allow_html=True)
    st.markdown("### Full League Leaderboard")

    fp6 = filter_players(df_players)

    # Summary table: one row per player, best stats
    summary_cols = ['player_name','team','region','role','rounds','rating','acs','kd_ratio',
                    'adr','kast','fkpr','hs_percent','clutch_rate','pool_size']
    summary_cols = [c for c in summary_cols if c in fp6.columns]
    summary = fp6[summary_cols].copy()
    for c in summary.select_dtypes(include='float').columns:
        summary[c] = summary[c].round(3)
    summary.columns = [c.replace('_',' ').upper() for c in summary.columns]
    summary = summary.sort_values('ACS', ascending=False).reset_index(drop=True)

    st.dataframe(summary, use_container_width=True, height=420)

    st.markdown("---")
    st.markdown("### Season Leaders by Category")
    lead_cols2 = [
        ('ACS King','acs'),('K/D King','kd_ratio'),('Damage Machine','adr'),
        ('KAST Leader','kast'),('Entry Fragger','fkpr'),('Headshot Artist','hs_percent'),
        ('Clutch God','clutch_rate'),('Agent Versatility','pool_size'),
    ]
    rows = [lead_cols2[:4], lead_cols2[4:]]
    for row_items in rows:
        cols_out = st.columns(len(row_items))
        for col_out, (title, met) in zip(cols_out, row_items):
            if met in fp6.columns and fp6[met].notna().any():
                try:
                    best = fp6.loc[fp6[met].idxmax()]
                    col_out.metric(
                        label=title,
                        value=best['player_name'],
                        delta=f"{best[met]:.2f} | {best['team']}",
                    )
                except (ValueError, KeyError):
                    col_out.metric(label=title, value='N/A', delta='No data')
