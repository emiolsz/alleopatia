import streamlit as st
import requests
from datetime import datetime

# ========================================================
# AUTOMATYCZNE ŁĄCZENIE BAZ DANYCH Z 5 OSOBNYCH PLIKÓW
# ========================================================
baza_roslin = {}

try:
    from warzywa import warzywa_baza
    baza_roslin.update(warzywa_baza)
except ImportError:
    pass

try:
    from krzewy import krzewy_baza
    baza_roslin.update(krzewy_baza)
except ImportError:
    pass

try:
    from ziola import ziola_baza
    baza_roslin.update(ziola_baza)
except ImportError:
    pass

try:
    from kwiaty import kwiaty_baza
    baza_roslin.update(kwiaty_baza)
except ImportError:
    pass

try:
    from drzewa import drzewa_baza
    baza_roslin.update(drzewa_baza)
except ImportError:
    pass

# ==========================================
# 1. KONFIGURACJA STRONY I NOWOCZESNEGO STYLU
# ==========================================
st.set_page_config(page_title="Grządkowisko", page_icon="🌿", layout="centered")

# Zaawansowany CSS dla nowoczesnego interfejsu (Modern Eco UI)
st.markdown("""
    <style>
    /* Tło głównej strony - delikatna, czysta szałwia */
    .stApp {
        background-color: #F3F7F4 !important;
    }
    
    /* Panel boczny - głęboka, elegancka zieleń botaniczna */
    section[data-testid="stSidebar"] {
        background-color: #1A3322 !important;
    }
    section[data-testid="stSidebar"] .stMarkdown, section[data-testid="stSidebar"] p {
        color: #E2EFE5 !important;
    }
    
    /* Selektory i komponenty Streamlit w panelu bocznym */
    div[data-baseweb="select"] {
        background-color: rgba(255, 255, 255, 0.08) !important;
        border-radius: 8px !important;
    }
    
    /* Główne nagłówki */
    h1 {
        color: #1A3322 !important; 
        font-family: 'Helvetica Neue', sans-serif; 
        font-weight: 800 !important;
        letter-spacing: -0.5px;
    }
    h3 {
        color: #2D5237 !important; 
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 600 !important;
    }
    
    /* Karty informacyjne (Cards) */
    .geo-card {
        background: #ffffff;
        padding: 20px;
        border-radius: 14px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
        margin-bottom: 20px;
        border: 1px solid #E2EFE5;
    }
    .sidebar-card {
        background: rgba(255, 255, 255, 0.06);
        padding: 16px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 18px;
    }
    </style>
""", unsafe_allow_html=True)

# Nagłówek główny aplikacji
st.markdown("""
    <div style="margin-top: -30px; margin-bottom: 25px;">
        <h1 style="font-size: 2.8rem; margin-bottom: 0;">🌿 Grządkowisko</h1>
        <p style="color: #5A7361; font-size: 1.1rem; margin-top: 5px;">Twój inteligentny asystent nowoczesnego ogrodnictwa</p>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 2. LOGIKA: KALENDARZ I FAZY KSIĘŻYCA
# ==========================================
def pobierz_faze_ksiezyca():
    dzis = datetime.now()
    rok, miesiac, dzien = dzis.year, dzis.month, dzis.day
    if miesiac < 3:
        rok -= 1
        miesiac += 12
    miesiac += 1
    c = int(365.25 * rok)
    e = int(30.6 * miesiac)
    jd = c + e + dzien - 694039.09
    jd /= 29.530588853
    faza = jd - int(jd)
    
    if faza < 0.03 or faza > 0.97:
        return "🌑 Nów", "Dni Korzenia (🥕). Idealny moment na walkę ze szkodnikami, odchwaszczanie i przycinanie. Unikaj siewu!"
    elif faza < 0.47:
        return "🌓 Pierwsza kwadra", "Dni Liścia (🍃) i Kwiatu (🌸). Soki intensywnie krążą w górnych partiach. Świetny czas na siew sałaty, ziół i przygotowanie rozsad."
    elif faza < 0.53:
        return "🌕 Pełnia", "Dni Owocu (🍎). Ziemia odpoczywa. Najlepszy czas na zasilanie roślin gnojówkami oraz zbiory do natychmiastowego spożycia."
    else:
        return "🌗 Ostatnia kwadra", "Dni Korzenia (🥕). Soki schodzą do podłoża. Idealny moment na siew marchwi, pietruszki, rzodkiewki i przesadzanie."

baza_imienin = {
    1: {1: "Mieszka, Mieczysława", 2: "Makarego, Bazylego", 22: "Wincentego, Anastazego"},
    2: {2: "Marii, Mirosława", 14: "Walentego, Cyryla"},
    3: {4: "Kazimierza, Łucji", 19: "Józefa, Bogdana"},
    4: {23: "Wojciecha, Jerzego", 30: "Mariana, Katarzyny"},
    5: {1: "Józefa, Filipa", 8: "Stanisława, Lizy", 12: "Pankracego (Ogrodnika)", 13: "Serwacego (Ogrodnika)", 14: "Bonifacego (Ogrodnika)", 15: "Zofii (Zimnej Zośki), Izydora", 22: "Heleny, Wiesławy, Julii", 23: "Emilii, Iwony"},
    6: {1: "Jakuba, Konrada", 24: "Jana, Danuty", 29: "Piotra, Pawła"},
    7: {22: "Magdaleny, Bolesława", 26: "Anny, Mirosławy"},
    8: {15: "Marii, Napoleona", 26: "Marii, Częstochowskiej"},
    9: {17: "Franciszka, Roberta", 30: "Zofii, Hieronima"},
    10: {4: "Franciszka, Rozalii", 25: "Darii, Sambora"},
    11: {1: "Wszystkich Świętych", 11: "Marcina, Bartłomieja", 30: "Andrzeja, Maurycego"},
    12: {4: "Barbary, Krystiana", 6: "Mikołaja, Jacynty", 24: "Adama, Ewy"}
}

def pobierz_dane_kalendarza():
    dzis = datetime.now()
    dni_tygodnia = ["Poniedziałek", "Wtorek", "Środa", "Czwartek", "Piątek", "Sobota", "Niedziela"]
    miesiace = ["stycznia", "lutego", "marca", "kwietnia", "maja", "czerwca", "lipca", "sierpnia", "września", "października", "listopada", "grudnia"]
    
    dzien_tyg = dni_tygodnia[dzis.weekday()]
    nazwa_miesiaca = miesiace[dzis.month - 1]
    
    pelna_data = f"{dzien_tyg}, {dzis.day} {nazwa_miesiaca}"
    dzien_roku = dzis.timetuple().tm_yday
    
    imieniny = baza_imienin.get(dzis.month, {}).get(dzis.day, "Brak popularnych imienin")
    return pelna_data, dzien_roku, imieniny

pelna_data, dzien_roku, imieniny = pobierz_dane_kalendarza()
faza_nazwa, faza_porada = pobierz_faze_ksiezyca()

# Wyświetlanie bocznego panelu (Kalendarz)
st.sidebar.html(f"""
    <div style="font-family: 'Helvetica Neue', sans-serif; padding: 5px 0;">
        <h3 style="color: #ffffff !important; margin-bottom: 14px; font-size: 1.25rem; font-weight:600; display:flex; align-items:center; gap:8px;">
            <span>📅</span> Kalendarz rynkowy
        </h3>
        <div class="sidebar-card">
            <p style="margin: 3px 0; font-size:0.95rem;"><b>Data:</b> <span style="color:#A9DFBF;">{pelna_data}</span></p>
            <p style="margin: 3px 0; font-size:0.9rem; opacity:0.85;"><b>Dzień roku:</b> {dzien_roku}/365</p>
            <p style="margin: 3px 0; font-size:0.9rem; opacity:0.85;"><b>Imieniny:</b> {imieniny}</p>
        </div>
        
        <h3 style="color: #ffffff !important; margin-top: 20px; margin-bottom: 14px; font-size: 1.25rem; font-weight:600; display:flex; align-items:center; gap:8px;">
            <span>🌙</span> Biodynamika
        </h3>
        <div class="sidebar-card" style="border-left: 3px solid #A9DFBF;">
            <p style="margin: 0 0 6px 0; font-size:1rem; color:#A9DFBF;"><b>{faza_nazwa}</b></p>
            <p style="margin: 0; font-size: 0.85rem; line-height: 1.4; opacity:0.9;">{faza_porada}</p>
        </div>
    </div>
""")

# ==========================================
# 3. LOGIKA: DANE METEOROLOGICZNE IMGW API (Oficjalne API)
# ==========================================
st.sidebar.html("""
    <h3 style="color: #ffffff !important; margin-top: 25px; margin-bottom: 10px; font-size: 1.25rem; font-weight:600; font-family: 'Helvetica Neue', sans-serif; display:flex; align-items:center; gap:8px;">
        <span>🌤️</span> Pogoda IMGW
    </h3>
""")

@st.cache_data(ttl=1800)
def pobierz_pogode_imgw():
    try:
        # Oficjalne darmowe API IMGW dla stacji synoptycznych
        url = "https://imgw.pl"
        odpowiedz = requests.get(url, timeout=5)
        if odpowiedz.status_code == 200:
            return odpowiedz.json()
    except:
        return None

dane_pogodowe = pobierz_pogode_imgw()

if dane_pogodowe:
    stacje = sorted([stacja['stacja'] for stacja in dane_pogodowe])
    
    domyslny_indeks = 0
    for i, s in enumerate(stacje):
        if "warszawa" in s.lower():
            domyslny_indeks = i
            break
            
    wybrane_miasto = st.sidebar.selectbox("Wybierz stację pomiarową:", stacje, index=domyslny_indeks, label_visibility="collapsed")
    
    dane_stacji = next(item for item in dane_pogodowe if item["stacja"] == wybrane_miasto)
    
    temp = dane_stacji.get('temperatura', '0')
    opad = dane_stacji.get('suma_opadu', '0')
    wilgotnosc = dane_stacji.get('wilgotnosc_wzgledna', '0')
    cisnienie = dane_stacji.get('cisnienie', 'Nieznane')
    
    st.sidebar.html(f"""
        <div class="sidebar-card" style="margin-top: 10px; background: rgba(0,0,0,0.15);">
            <div style="font-size: 1.6rem; font-weight: bold; color: #ffffff; margin-bottom: 8px;">{temp}°C</div>
            <div style="font-size: 0.85rem; opacity: 0.8; line-height: 1.5;">
                💧 <b>Wilgotność:</b> {wilgotnosc}%<br>
                🌧️ <b>Suma opadu:</b> {opad} mm<br>
                📉 <b>Ciśnienie:</b> {cisnienie} hPa
            </div>
        </div>
    """)
else:
    st.sidebar.warning("Nie udało się pobrać aktualnych danych z IMGW.")
# ==========================================
# 4. PANEL BOCZNY: LEGENDA SYMBOLI
# ==========================================
st.sidebar.html("""
    <h3 style="color: #ffffff !important; margin-top: 25px; margin-bottom: 10px; font-size: 1.1rem; font-weight:600; font-family: 'Helvetica Neue', sans-serif;">
        📋 Legenda dni księżycowych
    </h3>
    <div class="sidebar-card" style="font-size: 0.85rem; line-height: 1.6; background: rgba(255,255,255,0.03);">
        <div style="margin-bottom: 4px;"><b>🥕 Dni Korzenia</b> — marchew, burak, czosnek</div>
        <div style="margin-bottom: 4px;"><b>🍃 Dni Liścia</b> — sałata, zioła, kapusta</div>
        <div style="margin-bottom: 4px;"><b>🌸 Dni Kwiatu</b> — kwiaty, kalafior, brokuł</div>
        <div><b>🍎 Dni Owocu</b> — pomidor, ogórek, drzewa</div>
    </div>
""")

# ==========================================
# 5. PANEL GŁÓWNY: INTERFEJS WYSZUKIWANIA I WIZYTÓWKI
# ==========================================

# Kontener wyszukiwarki roślin
st.markdown('<div class="geo-card">', unsafe_allow_html=True)
st.markdown("### 🔍 Znajdź roślinę w swojej bazie")

if baza_roslin:
    lista_roslin = sorted(list(baza_roslin.keys()))
    wybrana_roslina = st.selectbox("Wpisz lub wybierz roślinę z listy:", lista_roslin)
    
    if wybrana_roslina:
        dane = baza_roslin[wybrana_roslina]
        
        st.markdown(f"## 🌿 {wybrana_roslina.capitalize()}")
        
        # Nowoczesny układ kolumnowy dla parametrów uprawy
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(label="☀️ Stanowisko", value=dane.get('stanowisko', 'Brak danych'))
        with col2:
            st.metric(label="💧 Podlewanie", value=dane.get('podlewanie', 'Brak danych'))
        with col3:
            st.metric(label="🌱 Rozstawa", value=dane.get('rozstawa', 'Brak danych'))
            
        # Szczegółowy opis w eleganckim boksie
        st.markdown("""
            <div style="background-color: #F9FBF9; padding: 15px; border-radius: 10px; border-left: 4px solid #2D5237; margin-top: 15px;">
                <h4 style="margin: 0 0 5px 0; color: #2D5237;">💡 Wskazówki i porady uprawowe:</h4>
                <p style="margin: 0; color: #4A5D4E; font-size: 0.95rem;">' + dane.get('notatki', 'Brak dodatkowych uwag w bazie danych.') + '</p>
            </div>
        """, unsafe_allow_html=True)
else:
    st.info("Twoja baza roślin jest obecnie pusta. Dodaj pliki danych (np. warzywa.py, ziola.py), aby zasilić aplikację wiedzą.")

st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 6. STOPKA (FOOTER) APLIKACJI
# ==========================================
st.markdown("""
    <div style="text-align: center; margin-top: 50px; padding: 20px 0; border-top: 1px solid #E2EFE5;">
        <p style="color: #8CA392; font-size: 0.85rem; margin: 0;">
            <b>Grządkowisko App</b> © 2026 • Zaprojektowane z pasją do natury 🌿
        </p>
        <p style="color: #B2C4B7; font-size: 0.75rem; margin: 5px 0 0 0;">
            Dane meteorologiczne dostarcza Instytut Meteorologii i Gospodarki Wodnej (IMGW-PIB)
        </p>
    </div>
""", unsafe_allow_html=True)


