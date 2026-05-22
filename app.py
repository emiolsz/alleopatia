import streamlit as st
import requests
from datetime import datetime

# ========================================================
# 1. AUTOMATYCZNE ŁĄCZENIE I UNIFIKACJA BAZ DANYCH
# ========================================================
baza_roslin = {}

# Funkcja ratunkowa: naprawia błędy w nazwach kluczy w Twoich plikach (.py)
def standaryzuj_baze(surowa_baza):
    zmapowana = {}
    for roslina, dane in surowa_baza.items():
        if isinstance(dane, dict):
            # Zamienia wielkie litery na małe i szuka alternatywnych nazw kluczy
            nazwa_klucz = roslina.lower().strip()
            zmapowana[nazwa_klucz] = {
                'stanowisko': dane.get('stanowisko') or dane.get('slonce') or dane.get('miejsce') or 'Brak danych',
                'podlewanie': dane.get('podlewanie') or dane.get('woda') or dane.get('wilgotnosc') or 'Brak danych',
                'rozstawa': dane.get('rozstawa') or dane.get('odleglosc') or dane.get('sadzenie') or 'Brak danych',
                'notatki': dane.get('notatki') or dane.get('uwagi') or dane.get('notatka') or dane.get('opis') or 'Brak dodatkowych uwag w bazie danych.'
            }
    return zmapowana

# Bezpieczne wczytywanie plików z ignorowaniem błędów i automatyczną naprawą struktury
try:
    from warzywa import warzywa_baza
    baza_roslin.update(standaryzuj_baze(warzywa_baza))
except Exception:
    pass

try:
    from krzewy import krzewy_baza
    baza_roslin.update(standaryzuj_baze(krzewy_baza))
except Exception:
    pass

try:
    from ziola import ziola_baza
    baza_roslin.update(standaryzuj_baze(ziola_baza))
except Exception:
    pass

try:
    from kwiaty import kwiaty_baza
    baza_roslin.update(standaryzuj_baze(kwiaty_baza))
except Exception:
    pass

try:
    from drzewa import drzewa_baza
    baza_roslin.update(standaryzuj_baze(drzewa_baza))
except Exception:
    pass

# AWARYJNA BAZA DANYCH: Jeśli Twoje pliki zwrócą pustkę, aplikacja uruchomi te dane (w tym działający Agrest!)
if not baza_roslin:
    baza_awaryjna = {
        "agrest": {"stanowisko": "Słoneczne", "podlewanie": "Umiarkowane", "rozstawa": "1.5 x 2 m", "notatki": "Odporny na mróz. Wymaga cięcia prześwietlającego wczesną wiosną."},
        "pomidor": {"stanowisko": "Bardzo słoneczne", "podlewanie": "Obfite", "rozstawa": "50 x 60 cm", "notatki": "Wymaga palikowania i regularnego usuwania pędów bocznych."},
        "mięta": {"stanowisko": "Półcień", "podlewanie": "Regularne", "rozstawa": "30 x 40 cm", "notatki": "Bardzo ekspansywna. Najlepiej uprawiać w dużych donicach."}
    }
    baza_roslin.update(baza_awaryjna)

# ==========================================
# 2. KONFIGURACJA STRONY I WIZUALNEGO STYLU
# ==========================================
st.set_page_config(page_title="Grządkowisko", page_icon="🌿", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #F3F7F4 !important; }
    section[data-testid="stSidebar"] { background-color: #1A3322 !important; }
    section[data-testid="stSidebar"] .stMarkdown, section[data-testid="stSidebar"] p { color: #E2EFE5 !important; }
    div[data-baseweb="select"] { background-color: rgba(255, 255, 255, 0.08) !important; border-radius: 8px !important; }
    h1 { color: #1A3322 !important; font-family: 'Helvetica Neue', sans-serif; font-weight: 800 !important; }
    h3 { color: #2D5237 !important; font-family: 'Helvetica Neue', sans-serif; font-weight: 600 !important; }
    .geo-card { background: #ffffff; padding: 20px; border-radius: 14px; box-shadow: 0 4px 12px rgba(0,0,0,0.04); margin-bottom: 20px; border: 1px solid #E2EFE5; }
    .sidebar-card { background: rgba(255, 255, 255, 0.06); padding: 16px; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 18px; }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div style="margin-top: -30px; margin-bottom: 25px;">
        <h1 style="font-size: 2.8rem; margin-bottom: 0;">🌿 Grządkowisko</h1>
        <p style="color: #5A7361; font-size: 1.1rem; margin-top: 5px;">Twój inteligentny asystent nowoczesnego ogrodnictwa</p>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 3. LOGIKA: KALENDARZ (DATA ORAZ LUNAR)
# ==========================================
def pobierz_faze_ksiezyca():
    dzis = datetime.now()
    rok, miesiac, dzien = dzis.year, dzis.month, dzis.day
    if miesiac < 3: rok -= 1; miesiac += 12
    miesiac += 1
    jd = int(365.25 * rok) + int(30.6 * miesiac) + dzien - 694039.09
    jd /= 29.530588853
    faza = jd - int(jd)
    
    if faza < 0.03 or faza > 0.97:
        return "🌑 Nów", "Dni Korzenia (🥕). Czas na walkę ze szkodnikami i odchwaszczanie. Unikaj siewu!"
    elif faza < 0.47:
        return "🌓 Pierwsza kwadra", "Dni Liścia (🍃) i Kwiatu (🌸). Soki krążą w górze. Świetny czas na siew sałaty i ziół."
    elif faza < 0.53:
        return "🌕 Pełnia", "Dni Owocu (🍎). Ziemia odpoczywa. Czas na nawożenie organiczne i zbiory do szybkiego spożycia."
    else:
        return "🌗 Ostatnia kwadra", "Dni Korzenia (🥕). Soki schodzą w dół. Idealny moment na siew marchwi i rzodkiewki."

baza_imienin = {1: {1: "Mieszka"}, 5: {22: "Heleny, Wiesławy, Julii", 23: "Emilii, Iwony"}}

def pobierz_dane_kalendarza():
    dzis = datetime.now()
    dni_tygodnia = ["Poniedziałek", "Wtorek", "Środa", "Czwartek", "Piątek", "Sobota", "Niedziela"]
    miesiace = ["stycznia", "lutego", "marca", "kwietnia", "maja", "czerwca", "lipca", "sierpnia", "września", "października", "listopada", "grudnia"]
    pelna_data = f"{dni_tygodnia[dzis.weekday()]}, {dzis.day} {miesiace[dzis.month - 1]}"
    imieniny = baza_imienin.get(dzis.month, {}).get(dzis.day, "Brak danych")
    return pelna_data, dzis.timetuple().tm_yday, imieniny

pelna_data, dzien_roku, imieniny = pobierz_dane_kalendarza()
faza_nazwa, faza_porada = pobierz_faze_ksiezyca()

st.sidebar.html(f"""
    <div style="font-family: 'Helvetica Neue', sans-serif;">
        <h3 style="color: #ffffff !important; margin-bottom: 14px; font-size: 1.25rem; font-weight:600;">📅 Kalendarz</h3>
        <div class="sidebar-card">
            <p style="margin: 3px 0;"><b>Data:</b> <span style="color:#A9DFBF;">{pelna_data}</span></p>
            <p style="margin: 3px 0; opacity:0.85;"><b>Dzień roku:</b> {dzien_roku}/365</p>
            <p style="margin: 3px 0; opacity:0.85;"><b>Imieniny:</b> {imieniny}</p>
        </div>
        <h3 style="color: #ffffff !important; margin-top: 20px; margin-bottom: 14px; font-size: 1.25rem; font-weight:600;">🌙 Biodynamika</h3>
        <div class="sidebar-card" style="border-left: 3px solid #A9DFBF;">
            <p style="margin: 0 0 6px 0; color:#A9DFBF;"><b>{faza_nazwa}</b></p>
            <p style="margin: 0; font-size: 0.85rem; line-height: 1.4;">{faza_porada}</p>
        </div>
    </div>
""")

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
# 5. PANEL GŁÓWNY: INTERFEJS WYSZUKIWANIA ROŚLIN
# ==========================================
st.markdown('<div class="geo-card">', unsafe_allow_html=True)
st.markdown("### 🔍 Znajdź roślinę w swojej bazie")

# Tworzenie listy rozwijanej na podstawie załadowanych słowników
lista_roslin = sorted(list(baza_roslin.keys())) if baza_roslin else []

if lista_roslin:
    wybrana_roslina = st.selectbox("Wyszukaj:", lista_roslin, label_visibility="collapsed")
    
    if wybrana_roslina:
        dane = baza_roslin[wybrana_roslina]
        
        st.markdown(f"<h2 style='color: #1A3322; margin-top: 15px;'>🌿 {str(wybrana_roslina).capitalize()}</h2>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1: st.metric(label="☀️ Stanowisko", value=dane.get('stanowisko', 'Brak danych'))
        with col2: st.metric(label="💧 Podlewanie", value=dane.get('podlewanie', 'Brak danych'))
        with col3: st.metric(label="🌱 Rozstawa", value=dane.get('rozstawa', 'Brak danych'))
            
        st.markdown(f"""
            <div style="background-color: #F9FBF9; padding: 15px; border-radius: 10px; border-left: 4px solid #2D5237; margin-top: 25px;">
                <h4 style="margin: 0 0 8px 0; color: #2D5237; font-weight: 600;">💡 Wskazówki i porady uprawowe:</h4>
                <p style="margin: 0; color: #4A5D4E; font-size: 0.95rem; line-height: 1.5;">{dane.get('notatki', 'Brak dodatkowych uwag w bazie danych.')}</p>
            </div>
        """, unsafe_allow_html=True)
else:
    st.warning("Nie znaleziono żadnych roślin. Upewnij się, że Twoje pliki (np. warzywa.py, ziola.py) znajdują się w tym samym folderze.")

st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 6. WYSUWANA "PORADA NA DZIEŃ" 
# ==========================================
st.markdown('<div class="geo-card">', unsafe_allow_html=True)
st.markdown("### 📅 Dzisiejsze zalecenia")

with st.expander("💡 Zobacz: Porada na dzień (Kliknij, aby wysunąć)", expanded=False):
    
    def pobierz_porade_z_zewnatrz():
        try:
            url = "https://imgw.pl"
            r = requests.get(url, timeout=3)
            if r.status_code == 200 and "<item>" in r.text:
                tekst = r.text
                item_start = tekst.find("<item>")
                start = tekst.find("<title>", item_start) + 7
                koniec = tekst.find("</title>", start)
                wynik = tekst[start:koniec]
                
                wynik = wynik.replace("<![CDATA[", "").replace("]]>", "")
                while "<" in wynik and ">" in wynik:
                    s_idx = wynik.find("<")
                    e_idx = wynik.find(">") + 1
                    wynik = wynik.replace(wynik[s_idx:e_idx], "")
                
                if len(wynik.strip()) > 5:
                    return f"📖 <b>Aktualności z bloga IMGW:</b> {wynik.strip()}. Sprawdź prognozy przed planowaniem prac."
        except Exception:
            pass
        
        # SYSTEM ZAPASOWY
        dzis = datetime.now()
        if dzis.month in [5, 6, 7, 8]:
            return "🌞 <b>Letnia rutyna:</b> Podlewaj grządki wyłącznie wczesnym rankiem lub wieczorem. Unikaj zraszania liści w pełnym słońcu, aby zapobiec poparzeniom."
        elif dzis.month in [9, 10, 11]:
            return "🍁 <b>Jesienne porządki:</b> Czas na ściółkowanie gleby kompostem, aby zabezpieczyć korzenie przed przymrozkami."
        else:
            return "❄️ <b>Zimowy odpoczynek:</b> Kontroluj stan przechowywanych nasion. Zaplanuj płodozmian na nowy sezon."

    akt_porada = pobierz_porade_z_zewnatrz()
    
    st.markdown(f"""
        <div style="padding: 5px; color: #2D5237; font-size: 1rem; line-height: 1.6;">
            {akt_porada}
        </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 7. STOPKA Z TWOJĄ ORYGINALNĄ TREŚCIĄ I STYLIZACJĄ
# ==========================================
st.markdown("""
    <div style="text-align: center; margin-top: 50px; padding: 25px; background-color: #1A3322; border-radius: 14px; box-shadow: 0 4px 12px rgba(0,0,0,0.02);">
        <!-- Dedykacja -->
        <p style="font-style: italic; color: #d0e1cd; font-size: 0.82rem; line-height: 1.5; margin: 0 0 25px 0;">
            🌿 „Aplikację dedykuję Mojemu Tacie, babci Helence i przyjaciółce Dorotce, a także tym którzy kochają swoje grządeczki z serdecznością”
        </p>
        
        <!-- Mała, wyśrodkowana nota autorska i prawna -->
        <p style="margin: 0; font-size: 0.72rem; color: #a3c2a0; letter-spacing: 0.5px;">
            Projekt i wykonanie: <span style="color: #ffffff; font-weight: bold;">Emilia Olszewska</span>
        </p>
        <p style="margin: 4px 0 0 0; font-size: 0.68rem; color: #8cb388;">
            © 2026 Grządkowisko 🥕🌸🍃🍎<br>
            Wszelkie prawa zastrzeżone
        </p>
    </div>
""", unsafe_allow_html=True)

