import streamlit as st
import pandas as pd
import folium
from folium.features import DivIcon
from streamlit_folium import st_folium
from PIL import Image
import os
import time

# 1. ตั้งค่าหน้าเว็บ Streamlit
st.set_page_config(
    page_title="MSU Smart Mobility - Compact Map Markers",
    page_icon="🟡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize Session State
if "theme" not in st.session_state:
    st.session_state.theme = "☀️ โหมดสว่าง (Light)"

if "points" not in st.session_state:
    st.session_state.points = 250

if "selected_map_coords" not in st.session_state:
    st.session_state.selected_map_coords = [16.246732, 103.247629]

if "new_event_alert" not in st.session_state:
    st.session_state.new_event_alert = None

if "alert_timestamp" not in st.session_state:
    st.session_state.alert_timestamp = 0

if "hazards" not in st.session_state:
    st.session_state.hazards = [
        {
            "location": "อาคารเรียนรวม RN (ราชนครินทร์)", 
            "type": "🌊 น้ำขังบนพื้นผิวถนน",
            "desc": "น้ำขังตรงหน้าทางเข้าตึก RN ฝั่งจอดรถจักรยานยนต์ ระวังลื่น", 
            "time": "10 นาทีที่แล้ว", 
            "coords": [16.246732, 103.247629],
            "image": None
        },
        {
            "location": "🚗 จุดตรวจจราจร ฝั่งวงเวียน", 
            "type": "🕳️ ฝาท่อชำรุด",
            "desc": "ฝาท่อเหล็กทรุดตัว บริเวณทางออกวงเวียนมุ่งหน้าคณะวิศวฯ", 
            "time": "25 นาทีที่แล้ว", 
            "coords": [16.242165, 103.252897],
            "image": None
        }
    ]

# 2. Dynamic Custom CSS
is_dark = "Dark" in st.session_state.theme or "มืด" in st.session_state.theme

if is_dark:
    bg_color = "#0F172A"
    card_bg = "#1E293B"
    text_color = "#F8FAFC"
    sub_text = "#94A3B8"
    border_color = "#334155"
    tab_bg = "#0F172A"
    tab_text = "#CBD5E1"
    tab_active_bg = "#FACC15"
    tab_active_text = "#0F172A"
    parking_card_bg = "#1E293B"
    info_box_bg = "#0F172A"
    extra_css = ""
else:
    bg_color = "#F8FAFC"
    card_bg = "#FFFFFF"
    text_color = "#000000"
    sub_text = "#1E293B"
    border_color = "#CBD5E1"
    tab_bg = "#1E293B"
    tab_text = "#E2E8F0"
    tab_active_bg = "#EAB308"
    tab_active_text = "#000000"
    parking_card_bg = "#FFFFFF"
    info_box_bg = "#F1F5F9"
    extra_css = """
        .stMarkdown, p, span, label, div[data-baseweb="radio"] label, .stSelectbox label, .stTextArea label, .stTextInput label {
            color: #000000 !important;
            font-weight: 500;
        }
    """

st.markdown(f"""
    <style>
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
        font-family: 'Kanit', 'Prompt', sans-serif;
    }}

    {extra_css}

    .msu-header-card {{
        background-color: {card_bg};
        border-radius: 16px;
        padding: 18px 24px;
        border: 2px solid {border_color};
        border-bottom: 6px solid #EAB308;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        margin-bottom: 12px;
    }}

    .msu-title-main {{
        color: {text_color} !important;
        font-size: 2.1rem;
        font-weight: 800;
        margin: 0;
        line-height: 1.2;
    }}

    .msu-sub-main {{
        color: {sub_text} !important;
        font-size: 0.95rem;
        font-weight: 700;
        margin-top: 4px;
    }}

    .content-box-contrast {{
        background-color: {card_bg};
        padding: 24px;
        border-radius: 16px;
        border: 2px solid {border_color};
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-top: 12px;
        color: {text_color};
    }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background-color: {tab_bg};
        padding: 8px 12px;
        border-radius: 12px;
    }}

    .stTabs [data-baseweb="tab"] {{
        border-radius: 8px;
        padding: 10px 18px;
        color: {tab_text} !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
    }}

    .stTabs [aria-selected="true"] {{
        background-color: {tab_active_bg} !important;
        color: {tab_active_text} !important;
        font-weight: 800 !important;
    }}

    .stButton>button {{
        background-color: #1E293B !important;
        color: #FACC15 !important;
        font-weight: 700;
        font-size: 1rem;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 1.2rem;
        width: 100%;
        transition: all 0.2s ease-in-out;
    }}
    .stButton>button:hover {{
        background-color: #0F172A !important;
        color: #FFFFFF !important;
        transform: translateY(-1px);
    }}

    .parking-card {{
        background-color: {parking_card_bg};
        border: 2px solid {border_color};
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        color: {text_color};
    }}

    .ai-badge {{
        background-color: #0284C7;
        color: #FFFFFF !important;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 700;
    }}

    .traffic-card {{
        background: #0F172A;
        color: #FFFFFF !important;
        padding: 14px;
        border-radius: 12px;
        border: 2px solid #334155;
        text-align: center;
        margin-bottom: 10px;
    }}

    .traffic-card * {{
        color: #FFFFFF !important;
    }}

    .auto-badge {{
        background-color: #16A34A;
        color: #FFFFFF !important;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
        display: inline-block;
    }}
    </style>
""", unsafe_allow_html=True)

# 3. ฟังก์ชันสร้าง Emoji Map Marker (ปรับขนาดย่อลง)
def create_emoji_marker(emoji_char, bg_color="#FFFFFF", border_color="#0F172A"):
    html_code = f"""
    <div style="
        font-size: 14px;
        background-color: {bg_color};
        border: 2px solid {border_color};
        border-radius: 50%;
        width: 26px;
        height: 26px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 2px 6px rgba(0,0,0,0.25);
        cursor: pointer;
    ">
        {emoji_char}
    </div>
    """
    return DivIcon(html=html_code, icon_size=(26, 26), icon_anchor=(13, 13))

# 4. ฐานข้อมูลพิกัด GPS ความละเอียดสูง 20 ตำแหน่ง
MSU_LOCATIONS = {
    "🚗 จุดตรวจจราจร หน้า มมส.": [16.248466, 103.254209],
    "🚗 จุดตรวจจราจร ซอยกู่แก้ว": [16.249972, 103.252184],
    "🚗 จุดตรวจจราจร หน้าคณะบัญชี": [16.249274, 103.247171],
    "🚗 จุดตรวจจราจร สี่แยกขามเรียง": [16.246961, 103.245512],
    "🚗 จุดตรวจจราจร ฝั่งวงเวียน": [16.242165, 103.252897],

    "อาคารวิทยาศาสตร์ SC1": [16.247433, 103.250882],
    "คณะวิทยาการสารสนเทศ (IT)": [16.246672, 103.251629],
    "คณะวิศวกรรมศาสตร์": [16.247334, 103.252796],
    "คณะเภสัชศาสตร์": [16.243996, 103.251437],
    "คณะพยาบาลศาสตร์": [16.245147, 103.252238],
    "คณะสิ่งแวดล้อมและทรัพยากรศาสตร์": [16.243384, 103.252163],
    "คณะสาธารณสุขศาสตร์": [16.248220, 103.253070],
    "คณะเทคโนโลยี": [16.249145, 103.251864],
    "วิทยาลัยการเมืองการปกครอง": [16.245634, 103.249997],
    "วิทยาลัยดุริยางคศิลป์": [16.244776, 103.250511],
    "คณะสถาปัตยกรรมศาสตร์ ผังเมืองและนฤมิตศิลป์": [16.247203, 103.249235],
    "คณะศิลปกรรมศาสตร์และวัฒนธรรมศาสตร์": [16.247801, 103.248374],
    "คณะการบัญชีและการจัดการ": [16.248332, 103.247580],
    "อาคารเรียนรวม RN (ราชนครินทร์)": [16.246732, 103.247629],
    "คณะมนุษยศาสตร์และสังคมศาสตร์": [16.246163, 103.248492],
}

MSU_PARKING_LOTS = {
    "ลานจอดรถอาคารเรียนรวม RN": [16.246800, 103.247400],
    "ลานจอดรถคณะ IT": [16.246500, 103.251900],
    "ลานจอดรถคณะวิศวกรรมศาสตร์": [16.247500, 103.252500],
    "ลานจอดรถคณะการบัญชี": [16.248500, 103.247300]
}

INTERSECTION_OFFSETS = {
    "🚗 จุดตรวจจราจร หน้า มมส.": 0,
    "🚗 จุดตรวจจราจร ซอยกู่แก้ว": 1,
    "🚗 จุดตรวจจราจร หน้าคณะบัญชี": 2,
    "🚗 จุดตรวจจราจร สี่แยกขามเรียง": 0,
    "🚗 จุดตรวจจราจร ฝั่งวงเวียน": 1
}

def get_auto_traffic_status(offset=0, tick_sec=None):
    if tick_sec is None:
        tick_sec = int(time.time()) // 20
    step = (tick_sec + offset) % 3
    if step == 0:
        return {"status": "🟢 การจราจรคล่องตัว", "emoji": "🟢", "label": "🟢 คล่องตัว", "bg": "#F0FDF4", "border": "#22C55E"}
    elif step == 1:
        return {"status": "🟡 การจราจรชะลอตัว", "emoji": "🟡", "label": "🟡 ชะลอตัว", "bg": "#FFFBEB", "border": "#F59E0B"}
    else:
        return {"status": "🔴 รถติดสะสมหนาแน่น", "emoji": "🔴", "label": "🔴 ติดขัดหนาแน่น", "bg": "#FEF2F2", "border": "#EF4444"}

# 5. HEADER ZONE WITH MSU LOGO & THEME SWITCHER
st.markdown('<div class="msu-header-card">', unsafe_allow_html=True)
col_logo, col_title, col_ctrl = st.columns([1, 4, 2])

with col_logo:
    logo_filename = None
    for fname in ["images_2.png", "images.png", "msu_logo.png", "logo.png"]:
        if os.path.exists(fname):
            logo_filename = fname
            break
            
    if logo_filename:
        st.image(logo_filename, width=90)
    else:
        st.markdown("""
            <div style="background:#1E293B; color:#FFFFFF; border-radius:12px; padding:12px; text-align:center;">
                <div style="font-size: 2rem; line-height: 1;">🏛️</div>
                <div style="font-size: 0.75rem; font-weight: 800; margin-top: 4px;">MSU</div>
            </div>
        """, unsafe_allow_html=True)

with col_title:
    st.markdown("""
        <div>
            <h1 class="msu-title-main">MSU Smart Mobility</h1>
            <p class="msu-sub-main">🏛️ มหาวิทยาลัยมหาสารคาม (Maha Sarakham University) | ระบบจัดการจราจรและลานจอดรถอัจฉริยะ</p>
        </div>
    """, unsafe_allow_html=True)

with col_ctrl:
    selected_theme = st.radio(
        "🎨 เลือกธีม UI",
        ["☀️ โหมดสว่าง (Light)", "🌙 โหมดมืด (Dark)"],
        horizontal=True,
        key="theme_radio_selector"
    )
    if selected_theme != st.session_state.theme:
        st.session_state.theme = selected_theme
        st.rerun()

    st.markdown(f"""
        <div style="background:#1E293B; color:#FFFFFF; border:2px solid #0F172A; padding:6px 14px; border-radius:10px; text-align:center; font-weight:700; font-size:0.9rem; margin-top:6px;">
            🪙 แต้มสะสม: <span style="color:#FACC15; font-weight:800; font-size:1.05rem;">{st.session_state.points} PTS</span>
        </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# --- POP-UP ALERT BANNER (เตือนด่วน 5 วินาที) ---
if st.session_state.new_event_alert:
    elapsed_time = time.time() - st.session_state.alert_timestamp
    if elapsed_time <= 5:
        col_alt_txt, col_alt_btn = st.columns([6, 1])
        with col_alt_txt:
            st.warning(f"🚨 **[แจ้งเตือนด่วน!]** {st.session_state.new_event_alert} *(แสดงเตือน 5 วินาที)*")
        with col_alt_btn:
            if st.button("❌ ปิดเตือน", key="close_alert_banner"):
                st.session_state.new_event_alert = None
                st.rerun()
    else:
        st.session_state.new_event_alert = None

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🗺️ แผนที่นำทาง (Campus Map)", 
    "🅿️ AI ค้นหาที่จอดรถ & ระดับรถติด", 
    "🚨 เพื่อนเตือนเพื่อน (แจ้งเหตุพร้อมรูป)", 
    "🎟️ สแกนเข้าลานจอด (QR Gate)", 
    "🎁 สะสมแต้ม (Traffic Rewards)"
])

# --- TAB 1: CAMPUS MAP WITH AUTOMATIC 20-SECOND MAP FRAGMENT SYNC ---
with tab1:
    st.markdown('<div class="content-box-contrast">', unsafe_allow_html=True)
    st.markdown(f"<h3 style='color:{text_color}; font-size:1.2rem; font-weight:800; margin-bottom:14px;'>📍 แผนที่ มมส. ขามเรียง (หมุดจราจรอัปเดตสดอัตโนมัติทุก 20 วินาที)</h3>", unsafe_allow_html=True)
    
    @st.fragment(run_every="20s")
    def render_auto_updating_map():
        sec_tick = int(time.time()) // 20
        msu_center = [16.246500, 103.250000]
        m = folium.Map(location=msu_center, zoom_start=16)

        folium.TileLayer(
            tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
            attr='Google Maps Satellite',
            name='Google Satellite (ภาพดาวเทียมคมชัด)',
            max_zoom=20
        ).add_to(m)

        folium.TileLayer(
            tiles='OpenStreetMap',
            name='OpenStreetMap (แผนที่ถนน)'
        ).add_to(m)

        folium.LatLngPopup().add_to(m)

        # 1. ปักหมุดสัญลักษณ์รถติด
        for name, offset in INTERSECTION_OFFSETS.items():
            coords = MSU_LOCATIONS[name]
            info = get_auto_traffic_status(offset, tick_sec=sec_tick)
            
            folium.Marker(
                coords,
                popup=f"<b>{name}</b><br>ระดับการจราจร: <b>{info['status']}</b>",
                tooltip=f"{name} [{info['label']}]",
                icon=create_emoji_marker(info['emoji'], bg_color=info['bg'], border_color=info['border'])
            ).add_to(m)

        # 2. ปักหมุดอาคาร คณะวิชา
        faculty_emojis = {
            "อาคารวิทยาศาสตร์ SC1": "🧪",
            "คณะวิทยาการสารสนเทศ (IT)": "💻",
            "คณะวิศวกรรมศาสตร์": "⚙️",
            "คณะเภสัชศาสตร์": "💊",
            "คณะพยาบาลศาสตร์": "🩺",
            "คณะสิ่งแวดล้อมและทรัพยากรศาสตร์": "🍃",
            "คณะสาธารณสุขศาสตร์": "🏥",
            "คณะเทคโนโลยี": "🔬",
            "วิทยาลัยการเมืองการปกครอง": "🏛️",
            "วิทยาลัยดุริยางคศิลป์": "🎵",
            "คณะสถาปัตยกรรมศาสตร์ ผังเมืองและนฤมิตศิลป์": "📐",
            "คณะศิลปกรรมศาสตร์และวัฒนธรรมศาสตร์": "🎨",
            "คณะการบัญชีและการจัดการ": "📊",
            "อาคารเรียนรวม RN (ราชนครินทร์)": "📚",
            "คณะมนุษยศาสตร์และสังคมศาสตร์": "🎓",
        }

        for name, coords in MSU_LOCATIONS.items():
            if "🚗" not in name:
                emoji_icon = faculty_emojis.get(name, "🏫")
                folium.Marker(
                    coords, 
                    popup=f"<b>{name}</b><br><code>{coords[0]:.6f}, {coords[1]:.6f}</code>", 
                    tooltip=name,
                    icon=create_emoji_marker(emoji_icon, bg_color="#FFFFFF", border_color="#1E293B")
                ).add_to(m)

        # 3. ปักหมุดลานจอดรถ 🅿️
        for p_name, p_coords in MSU_PARKING_LOTS.items():
            folium.Marker(
                p_coords,
                popup=f"<b>{p_name}</b>",
                tooltip=p_name,
                icon=create_emoji_marker("🅿️", bg_color="#E0F2FE", border_color="#0284C7")
            ).add_to(m)

        # 4. ปักหมุดจุดเสี่ยงภัย 🚨
        for hazard in st.session_state.hazards:
            folium.Marker(
                hazard["coords"],
                popup=f"🚨 <b>{hazard['location']}</b><br><b>ประเภท:</b> {hazard.get('type','')}<br>{hazard['desc']}<br><i>({hazard['time']})</i>",
                tooltip=f"🚨 จุดเสี่ยงภัย: {hazard['location']}",
                icon=create_emoji_marker("🚨", bg_color="#FEF2F2", border_color="#EF4444")
            ).add_to(m)

        folium.LayerControl().add_to(m)
        
        map_output = st_folium(m, width="100%", height=500, key="msu_tab1_live_map_fragment", returned_objects=["last_clicked"])
        
        if map_output and map_output.get("last_clicked"):
            click_lat = map_output["last_clicked"]["lat"]
            click_lng = map_output["last_clicked"]["lng"]
            st.session_state.selected_map_coords = [click_lat, click_lng]
            st.info(f"🎯 **พิกัดที่คุณจิ้มบนแผนที่:** `[{click_lat:.6f}, {click_lng:.6f}]` (สามารถนำไปใช้ปักหมุดในแท็บ 'เพื่อนเตือนเพื่อน')")

    render_auto_updating_map()
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 2: AUTOMATED REAL-TIME METRICS & PARKING PHOTO ---
with tab2:
    st.markdown('<div class="content-box-contrast">', unsafe_allow_html=True)
    
    col_t_title, col_t_badge = st.columns([2, 1])
    with col_t_title:
        st.markdown(f"<h3 style='color:{text_color}; font-size:1.2rem; font-weight:800; margin-bottom:0;'>🚗 ระดับความหนาแน่นการจราจร & AI CCTV ลานจอดรถ</h3>", unsafe_allow_html=True)
    with col_t_badge:
        st.markdown("<div style='text-align:right;'><span class='auto-badge'>🟢 Live Dynamic Sync (20s)</span></div>", unsafe_allow_html=True)

    st.write("")
    
    @st.fragment(run_every="20s")
    def render_tab2_live_metrics():
        current_tick = int(time.time()) // 20
        
        st.markdown(f"<h4 style='color:{text_color}; font-size:1.05rem; font-weight:800;'>📊 สรุประดับความหนาแน่นรถติดประจำแยกใน มมส. ขามเรียง (อัปเดตสดทุก 20 วินาที)</h4>", unsafe_allow_html=True)
        
        cols = st.columns(5)
        for idx, (name, offset) in enumerate(INTERSECTION_OFFSETS.items()):
            info = get_auto_traffic_status(offset, tick_sec=current_tick)
            short_name = name.replace("🚗 จุดตรวจจราจร ", "")
            with cols[idx]:
                st.markdown(f"""
                    <div class="traffic-card" style="border-top: 6px solid {info['border']};">
                        <div style="font-size:0.85rem; font-weight:700; color:#94A3B8;">{short_name}</div>
                        <div style="font-size:1.4rem; margin:6px 0;">{info['emoji']}</div>
                        <div style="font-size:0.8rem; font-weight:800; color:#F1F5F9;">{info['label'].split()[1]}</div>
                    </div>
                """, unsafe_allow_html=True)

        st.write("")
        st.markdown("---")
        
        parking_rn_auto = 5 + ((current_tick * 7) % 22)
        parking_it_auto = 1 + ((current_tick * 3) % 12)
        eta_rn_auto = f"{3 + (current_tick % 4)} นาที"
        eta_it_auto = f"{5 + (current_tick % 6)} นาที"

        col_cam, col_video = st.columns([1, 2])
        
        with col_cam:
            st.markdown(f"<b style='color:{text_color};'>📹 เลือกแหล่งข้อมูลวิดีโอ/ภาพสด CCTV:</b>", unsafe_allow_html=True)
            video_source = st.radio(
                "แหล่งวิดีโอ",
                ["🎥 กล้อง CCTV สด (ระบบจำลอง)", "📁 อัปโหลดวิดีโอจากเครื่อง (.mp4)"],
                label_visibility="collapsed"
            )
            
            uploaded_video = None
            if video_source == "📁 อัปโหลดวิดีโอจากเครื่อง (.mp4)":
                uploaded_video = st.file_uploader("เลือกไฟล์วิดีโอลานจอดรถ", type=["mp4", "mov", "avi"])
            else:
                selected_cctv = st.selectbox("เลือกโซนกล้อง CCTV", ["โซนอาคารเรียนรวม RN (ลานจอดรถจักรยานยนต์)", "โซนคณะ IT"])

            st.markdown("---")
            st.markdown("<span class='ai-badge'>🤖 AI Vision Detection Status</span>", unsafe_allow_html=True)
            st.write("")
            
            st.markdown(f"""
                <div style="background:{info_box_bg}; padding:14px; border-radius:10px; border:1px solid {border_color}; color:{text_color};">
                    <p style="margin:2px 0;">🟢 <b>อัลกอริทึม:</b> YOLOv8 Deep Learning</p>
                    <p style="margin:2px 0;">🎯 <b>ความแม่นยำ AI:</b> 98.4% Accuracy</p>
                    <p style="margin:2px 0;">🚗 <b>ตรวจจับรถจักรยานยนต์/รถยนต์:</b> {30 - parking_rn_auto} คัน</p>
                    <p style="margin:2px 0;">🟩 <b>ช่องจอดว่าง (Empty):</b> <b style="color:#16A34A; font-size:1.1rem;">{parking_rn_auto} คัน</b></p>
                </div>
            """, unsafe_allow_html=True)

        with col_video:
            st.markdown(f"<b style='color:{text_color};'>📡 ภาพสตรีมกล้อง CCTV ประมวลผลลานจอดรถ (AI Overlay)</b>", unsafe_allow_html=True)
            
            if uploaded_video is not None:
                st.video(uploaded_video, autoplay=True, loop=True)
                st.caption("🎬 กำลังเล่นวิดีโอที่คุณอัปโหลดพร้อมระบบวิเคราะห์ AI")
            else:
                current_zone = locals().get("selected_cctv", "RN")
                if "RN" in current_zone:
                    rn_img = None
                    for img_fn in ["parking.jpg", "parkingjpg.jpg"]:
                        if os.path.exists(img_fn):
                            rn_img = img_fn
                            break
                            
                    if rn_img:
                        st.image(rn_img, caption="📷 ภาพสดกล้อง CCTV ลานจอดรถจักรยานยนต์ อาคารเรียนรวม RN (มมส.)", use_container_width=True)
                    else:
                        st.info("💡 *(วางไฟล์ `parking.jpg` หรือ `parkingjpg.jpg` ในโฟลเดอร์เพื่อแสดงภาพ)*")
                        st.image("https://images.unsplash.com/photo-1558981806-ec527fa84c39?q=80&w=1000", caption="📷 ภาพถ่ายจำลองลานจอดรถ", use_container_width=True)
                else:
                    local_video_fn = "cctv_it.mp4"
                    if os.path.exists(local_video_fn):
                        st.video(local_video_fn, autoplay=True, loop=True)
                        st.caption(f"📁 เล่นไฟล์วิดีโอโซน IT: `{local_video_fn}`")
                    else:
                        demo_url = "https://www.w3schools.com/html/mov_bbb.mp4"
                        st.video(demo_url, autoplay=True, loop=True, muted=True)
                        st.caption("💡 *(สตรีม Demo โซนคณะ IT)*")

        st.write("")
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
                <div class="parking-card" style="border-left: 6px solid #16A34A;">
                    <h4 style="margin:0; font-size:1.1rem; font-weight:800; color:{text_color};">อาคารเรียนรวม RN (ลานจอดรถจักรยานยนต์)</h4>
                    <p style="font-size:0.95rem; margin-top:6px; margin-bottom:0; font-weight:600; color:{text_color};">
                        สถานะ: <b style="color:#16A34A; font-weight:800;">ว่าง {parking_rn_auto} คัน</b> | 🚗 เวลาเดินทาง: <b>{eta_rn_auto}</b>
                    </p>
                </div>
            """, unsafe_allow_html=True)
            st.progress(min(1.0, max(0.0, 1.0 - (parking_rn_auto / 30))))
            if st.button("นำทางไปโซน RN", key="btn_rn"):
                st.toast(f"กำลังนำทางไปอาคารเรียนรวม RN (ใช้เวลาประมาณ {eta_rn_auto})...")

        with col2:
            st.markdown(f"""
                <div class="parking-card" style="border-left: 6px solid #D97706;">
                    <h4 style="margin:0; font-size:1.1rem; font-weight:800; color:{text_color};">คณะวิทยาการสารสนเทศ</h4>
                    <p style="font-size:0.95rem; margin-top:6px; margin-bottom:0; font-weight:600; color:{text_color};">
                        สถานะ: <b style="color:#D97706; font-weight:800;">ว่าง {parking_it_auto} คัน</b> | 🚗 เวลาเดินทาง: <b>{eta_it_auto}</b>
                    </p>
                </div>
            """, unsafe_allow_html=True)
            st.progress(min(1.0, max(0.0, 1.0 - (parking_it_auto / 15))))
            if st.button("นำทางไปโซน IT", key="btn_it"):
                st.toast(f"กำลังนำทางไปคณะวิทยาการสารสนเทศ (ใช้เวลาประมาณ {eta_it_auto})...")

    render_tab2_live_metrics()
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 3: HAZARD REPORTING FORM WITH DELETE OPTION ---
with tab3:
    st.markdown('<div class="content-box-contrast">', unsafe_allow_html=True)
    st.markdown(f"<h3 style='color:{text_color}; font-size:1.2rem; font-weight:800; margin-bottom:16px;'>🚨 เพื่อนเตือนเพื่อน (รายงานจุดเสี่ยงพร้อมรูปถ่าย & พิกัด GPS)</h3>", unsafe_allow_html=True)
    
    with st.form("hazard_form_with_photo", clear_on_submit=True):
        col_f1, col_f2 = st.columns(2)
        
        with col_f1:
            loc_option = st.radio("เลือกวิธีระบุตำแหน่งเกิดเหตุ:", ["เลือกจากสถานที่หลักใน มมส.", "ใช้พิกัดที่จิ้มบนแผนที่ (Tab 1)"])
            
            if loc_option == "เลือกจากสถานที่หลักใน มมส.":
                selected_loc_name = st.selectbox("ระบุอาคาร / บริเวณ", list(MSU_LOCATIONS.keys()))
                target_coords = MSU_LOCATIONS[selected_loc_name]
            else:
                selected_loc_name = f"จุดพิกัดกำหนดเอง ({st.session_state.selected_map_coords[0]:.5f}, {st.session_state.selected_map_coords[1]:.5f})"
                target_coords = st.session_state.selected_map_coords
                st.success(f"📍 พิกัดปัจจุบันที่จะถูกปักหมุด: `{target_coords[0]:.6f}, {target_coords[1]:.6f}`")

        with col_f2:
            hazard_type = st.selectbox("ประเภทจุดเสี่ยงภัย / อุปสรรค", [
                "🌊 น้ำขังบนพื้นผิวถนน / ถนนลื่น",
                "🕳️ ถนนชำรุด / เป็นหลุมเป็นบ่อ",
                "💥 เกิดอุบัติเหตุ / มีรถเสีย",
                "🚧 พื้นที่ซ่อมบำรุง / ก่อสร้าง",
                "💡 ไฟส่องสว่างดับ / จุดอับสายตา"
            ])
            
            uploaded_file = st.file_uploader("📸 แนบรูปถ่ายจุดเกิดเหตุ (JPG, PNG)", type=["jpg", "jpeg", "png"])

        desc = st.text_area("รายละเอียดเหตุการณ์เพิ่มเติม", placeholder="ระบุรายละเอียด เช่น หลุมกว้าง ลึกประมาณ 10 ซม., เลนซ้ายใกล้ทางโค้ง...")
        submitted = st.form_submit_button("🚨 ส่งรายงานแจ้งเตือนไปบนแผนที่")
        
        if submitted and desc:
            img_data = None
            if uploaded_file is not None:
                img_data = Image.open(uploaded_file)

            new_hazard = {
                "location": selected_loc_name,
                "type": hazard_type,
                "desc": desc,
                "time": "เมื่อสักครู่",
                "coords": target_coords,
                "image": img_data
            }
            st.session_state.hazards.insert(0, new_hazard)
            st.session_state.new_event_alert = f"{hazard_type} บริเวณ {selected_loc_name} ({desc[:30]}...)"
            st.session_state.alert_timestamp = time.time()
            st.toast(f"🚨 ประกาศเด้งด่วน (5วิ): เพิ่มรายงาน '{hazard_type}' เรียบร้อยแล้ว!", icon="🔔")
            st.rerun()

    st.write("")
    st.markdown(f"<h4 style='color:{text_color}; font-size:1.1rem; font-weight:800;'>📢 รายงานสภาพถนน & จุดเสี่ยงภัยล่าสุดในระบบ (สามารถกดลบได้)</h4>", unsafe_allow_html=True)
    
    for idx, h in enumerate(st.session_state.hazards):
        col_card, col_del = st.columns([5, 1])
        with col_card:
            st.markdown(f"""
                <div style="background-color:{info_box_bg}; border-left:6px solid #EF4444; padding:16px; border-radius:12px; margin-bottom:12px; border:1px solid {border_color}; color:{text_color};">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <b style="font-size:1.05rem;">{h.get('type','🚨 แจ้งเตือนภัย')} — {h['location']}</b>
                        <span style="color:#64748B; font-size:0.85rem;">🕒 {h['time']}</span>
                    </div>
                    <p style="margin:6px 0; font-size:0.95rem;"><b>รายละเอียด:</b> {h['desc']}</p>
                    <p style="margin:0; font-size:0.85rem;">📍 <b>พิกัด GPS:</b> <code>{h['coords'][0]:.6f}, {h['coords'][1]:.6f}</code></p>
                </div>
            """, unsafe_allow_html=True)
            if h.get("image") is not None:
                st.image(h["image"], caption=f"📷 ภาพถ่ายจุดเกิดเหตุ: {h['location']}", width=320)
                
        with col_del:
            st.write("")
            if st.button("🗑️ ลบรายงาน", key=f"btn_delete_hazard_{idx}"):
                deleted_item = st.session_state.hazards.pop(idx)
                st.toast(f"🗑️ ลบรายการ '{deleted_item['location']}' เรียบร้อยแล้ว!", icon="✅")
                st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 4: STUDENT QR GATE SCAN ---
with tab4:
    st.markdown('<div class="content-box-contrast">', unsafe_allow_html=True)
    st.markdown(f"<h3 style='color:{text_color}; font-size:1.2rem; font-weight:800; margin-bottom:12px;'>🎟️ สแกนบัตรนิสิต / QR Gate เปิดไม้กั้น</h3>", unsafe_allow_html=True)
    st.write("แตะบัตรนิสิตหรือสแกน QR Code ที่ตู้สแกนเพื่อเปิดไม้กั้นอัตโนมัติ")
    
    col_qr, col_info = st.columns([1, 2])
    with col_qr:
        st.image("https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=MSU-STUDENT-64000000", width=180)
    with col_info:
        st.markdown(f"""
            <div style="background:{info_box_bg}; padding:16px; border-radius:12px; border:1px solid {border_color}; color:{text_color};">
                <b>สถานะบัตรนิสิต:</b> <span style="color:#16A34A; font-weight:700;">🟢 พร้อมใช้งาน</span><br>
                <b>รหัสนิสิต:</b> 6401xxxxxxxx<br>
                <b>สิทธิ์เข้าจอด:</b> ลานจอดรถนิสิต มมส. ขามเรียง
            </div>
        """, unsafe_allow_html=True)
    
    st.write("")
    if st.button("🟢 [Demo] จำลองสแกน QR Code เข้าลานจอด", key="btn_gate"):
        st.balloons()
        st.success("สแกนสำเร็จ! ไม้กั้นเปิดออก — ช่องจอดว่างแนะนำ: A-12")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 5: TRAFFIC REWARDS SYSTEM ---
with tab5:
    st.markdown('<div class="content-box-contrast">', unsafe_allow_html=True)
    st.markdown(f"<h3 style='color:{text_color}; font-size:1.2rem; font-weight:800; margin-bottom:12px;'>🎁 สะสมแต้มวินัยการจราจร (MSU Rewards)</h3>", unsafe_allow_html=True)
    st.write("สแกน QR Code ณ จุดจอดรถถูกระเบียบเพื่อรับคะแนนสะสมแลกสิทธิพิเศษ")
    
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        if st.button("สแกน QR จอดถูกระเบียบ (+50 PTS)", key="btn_reward"):
            st.session_state.points += 50
            st.toast("🎉 รับเพิ่ม +50 แต้มสำเร็จ!")
            st.rerun()
            
    with col_r2:
        if st.button("แลกส่วนลดคูปองร้านค้า ตลาดน้อย (-100 PTS)", key="btn_redeem"):
            if st.session_state.points >= 100:
                st.session_state.points -= 100
                st.success("แลกคูปองส่วนลด 20 บาท สำเร็จ!")
                st.rerun()
            else:
                st.warning("แต้มสะสมของคุณไม่พอสำหรับการแลกส่วนลด")
                
    st.markdown('</div>', unsafe_allow_html=True)