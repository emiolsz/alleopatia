import streamlit as st
import requests
from datetime import datetime

# ========================================================
# AUTOMATYCZNE ŁĄCZENIE BAZ DANYCH Z 5 OSOBNYCH PLIKÓW (ORYGINALNE)
# ========================================================
baza_roslin = {}

# 1. Import z warzywa.py
try:
    from warzywa import warzywa_baza
    baza_roslin.update(warzywa_baza)
except ImportError:
    pass

# 4. Import z krzewy.py
try:
    from krzewy import krzewy_baza
    baza_roslin.update(krzewy_baza)
except ImportError:
    pass

# 2. Import z ziola.py
try:
    from ziola import ziola_baza
    baza_roslin.update(ziola_baza)
except ImportError:
    pass

# 3. Import z kwiaty.py
try:
    from kwiaty import kwiaty_baza
    baza_roslin.update(kwiaty_baza)
except ImportError:
    pass

# 5. Import z drzewa.py
try:
    from drzewa import drzewa_baza
    baza_roslin.update(drzewa_baza)
except ImportError:
    pass

# ==========================================
# 1. KONFIGURACJA STRONY I WIZUALNEGO STYLU
# ==========================================
st.set_page_config(page_title="Grządkowisko", page_icon="🌿", layout="centered")

st.markdown("""
    <style>
    /* Nowoczesne, jasne tło szałwiowe strony głównej */
    .stApp {
        background-color: #F3F7F4 !important;
    }
    
    /* Panel boczny: Solidna, głęboka zieleń botaniczna */
    section[data-testid="stSidebar"] {
        background-color: #1A3322 !important;
    }
    section[data-testid="stSidebar"] .stMarkdown, section[data-testid="stSidebar"] p {
        color: #E2EFE5 !important;
    }
    
    /* Kolory nagłówków na głównej stronie */
    h1 {color: #1A3322; font-family: 'Arial', sans-serif; font-weight: bold;}
    h3 {color: #2D5237; font-family: 'Arial', sans-serif; font-weight: bold;}
    
    /* Estetyczne białe karty na zawartość strony głównej */
    .geo-card {
        background: #ffffff;
        padding: 22px;
        border-radius: 14px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        margin-bottom: 20px;
        border: 1px solid #E2EFE5;
    }
    
    /* Czyste kontenery informacyjne dla panelu bocznego */
    .sidebar-card {
        background: rgba(255, 255, 255, 0.06);
        padding: 14px;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🌿 Grządkowisko")
st.subheader("Twój inteligentny asystent ogrodowy")

# ==========================================
# 2. LOGIKA: KALENDARZ (DATA, DZIEŃ, IMIENINY) i KSIĘŻYC
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
        return "🌑 Nów", "Dni 🥕. Czas na walkę ze szkodnikami, plewienie i przycinanie pędów. Nie siejemy!"
    elif faza < 0.47:
        return "🌓 Pierwsza kwadra", "Dni 🍃 i 🌸. Soki idą w górę. Świetny moment na siew sałaty, ziół i rozsad."
    elif faza < 0.53:
        return "🌕 Pełnia", "Dni 🍎. Ziemia odpoczywa. Idealny czas na nawożenie (gnojówki) i zbiory do natychmiastowego spożycia."
    else:
        return "🌗 Ostatnia kwadra", "Dni 🥕. Soki schodzą w dół. Najlepszy czas na siew marchewki, pietruszki, rzodkiewki."

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
    
    pelna_data = f"{dzien_tyg}, {dzis.day} {nazwa_miesiaca} {dzis.year}"
    dzien_roku = dzis.timetuple().tm_yday
    
    imieniny = baza_imienin.get(dzis.month, {}).get(dzis.day, "Brak popularnych imienin w bazie")
    return pelna_data, dzien_roku, imieniny

pelna_data, dzien_roku, imieniny = pobierz_dane_kalendarza()
faza_nazwa, faza_porada = pobierz_faze_ksiezyca()

st.sidebar.html(f"""
    <div style="font-family: Arial, sans-serif; color: #ffffff; padding: 5px 0;">
        <h3 style="color: #ffffff; margin-bottom: 10px; font-size: 1.2rem;">📅 Kalendarz</h3>
        <div class="sidebar-card">
            <p style="margin: 4px 0;"><b>Data:</b> {pelna_data}</p>
            <p style="margin: 4px 0;"><b>Dzień roku:</b> {dzien_roku}/365</p>
            <p style="margin: 4px 0;"><b>Imieniny:</b> {imieniny}</p>
        </div>
        
        <h3 style="color: #ffffff; margin-bottom: 10px; font-size: 1.2rem;">🌙 Kalendarz Księżycowy</h3>
        <div class="sidebar-card" style="border-left: 3px solid #A9DFBF;">
            <p style="margin: 0 0 6px 0; color: #ffffff;"><b>Dzisiejsza faza:</b> {faza_nazwa}</p>
            <p style="margin: 0; font-size: 0.88rem; line-height: 1.4; color: #ffffff;"><b>Wytyczne:</b> {faza_porada}</p>
        </div>
    </div>
""")

# ==========================================
# 3. LOGIKA: DANE METEOROLOGICZNE IMGW API
# ==========================================
st.sidebar.html("""<h3 style="color: #ffffff !important; margin-top: 15px; margin-bottom: 5px; font-size: 1.2rem; font-family: Arial, sans-serif;">🌤️ Pogoda IMGW</h3>""")

@st.cache_data(ttl=600)
def pobierz_pogode_imgw():
    try:
        url = "https://imgw.pl"
        odpowiedz = requests.get(url, timeout=3)
        if odpowiedz.status_code == 200:
            return odpowiedz.json()
    except:
        return None

dane_pogodowe = pobierz_pogode_imgw()

if dane_pogodowe:
    stacje = sorted([stacja['stacja'] for stacja in dane_pogodowe])
    
    domyslny_indeks = 0
    for i, s in enumerate(stacje):
        if "legionowo" in s.lower() or "warszawa" in s.lower():
            domyslny_indeks = i
            break
            
    wybrane_miasto = st.sidebar.selectbox("Wybierz stację:", stacje, index=domyslny_indeks, label_visibility="collapsed")
    
    dane_stacji = next(item for item in dane_pogodowe if item["stacja"] == wybrane_miasto)
    
    temp = dane_stacji.get('temperatura', '0')
    opad = dane_stacji.get('suma_opadu', '0')
    wilgotnosc = dane_stacji.get('wilgotnosc_wzgledna', '0')
    cisnienie = dane_stacji.get('cisnienie', 'Brak danych')
    
    st.sidebar.html(f"""
        <div class="sidebar-card" style="background: rgba(0, 0, 0, 0.15);">
            <div style="font-size: 1.5rem; font-weight: bold; color: #ffffff; margin-bottom: 5px;">{temp}°C</div>
            <p style="margin: 3px 0; font-size: 0.88rem;">💧 <b>Wilgotność:</b> {wilgotnosc}%</p>
            <p style="margin: 3px 0; font-size: 0.88rem;">🌧️ <b>Suma opadu:</b> {opad} mm</p>
            <p style="margin: 3px 0; font-size: 0.88rem;">📉 <b>Ciśnienie:</b> {cisnienie} hPa</p>
        </div>
    """)
else:
    st.sidebar.html("""
        <div class="sidebar-card" style="background: rgba(255, 0, 0, 0.05); border-left: 3px solid #ff4b4b;">
            <p style="margin: 0; font-size: 0.85rem; color: #ff8888;">⚠️ Serwer IMGW zajęty. Odśwież stronę.</p>
        </div>
    """)
# ==========================================
# 4. PANEL BOCZNY: LEGENDA SYMBOLI
# ==========================================
st.sidebar.html("""
    <h3 style="color: #ffffff !important; margin-top: 20px; margin-bottom: 5px; font-size: 1.1rem; font-family: Arial, sans-serif;">📋 Legenda oznaczeń:</h3>
    <div class="sidebar-card" style="font-size: 0.85rem; line-height: 1.5; background: rgba(255, 255, 255, 0.03);">
        <p style="margin: 4px 0;">🥕 — Dni Korzenia (marchew, burak, czosnek)</p>
        <p style="margin: 4px 0;">🍃 — Dni Liścia (sałata, zioła, kapusta)</p>
        <p style="margin: 4px 0;">🌸 — Dni Kwiatu (kwiaty, kalafior)</p>
        <p style="margin: 4px 0;">🍎 — Dni Owocu (pomidor, ogórek, drzewa)</p>
    </div>
""")

# ==========================================
# 5. PANEL GŁÓWNY: WYSZUKIWARKA ROŚLIN
# ==========================================
st.markdown('<div class="geo-card">', unsafe_allow_html=True)
st.markdown("### 🔍 Znajdź roślinę w swojej bazie")

lista_roslin = sorted(list(baza_roslin.keys()))

if lista_roslin:
    wybrana_roslina = st.selectbox("Wybierz roślinę:", lista_roslin, label_visibility="collapsed")
    
    if wybrana_roslina:
        dane = baza_roslin[wybrana_roslina]
        
        st.markdown(f"<h2 style='color: #1A3322; margin-top: 15px; margin-bottom: 15px;'>🌿 {str(wybrana_roslina).capitalize()}</h2>", unsafe_allow_html=True)
        
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
    st.info("Baza roślin jest pusta lub pliki nie zostały znalezione w folderze głównym.")

st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 6. WYSUWANA SEKCJA: PORADA NA DZIEŃ
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
                    return f"📖 <b>Aktualności z bloga IMGW:</b> {wynik.strip()}. Sprawdź prognozy krótkoterminowe przed planowaniem prac."
        except:
            pass
        
        return "🌞 <b>Bieżące zalecenia:</b> Podlewaj rośliny wyłącznie wczesnym rankiem lub wieczorem, unikając moczenia liści w pełnym słońcu. Regularnie sprawdzaj wilgotność gleby pod osłonami."

    akt_porada = pobierz_porade_z_zewnatrz()
    
    st.markdown(f"""
        <div style="padding: 5px; color: #2D5237; font-size: 1rem; line-height: 1.6;">
            {akt_porada}
        </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 7. STOPKA Z TWOJĄ ORYGINALNĄ TREŚCIĄ I DEDYKACJĄ
# ==========================================
st.markdown("""
    <div style="text-align: center; margin-top: 50px; padding: 25px; background-color: #1A3322; border-radius: 14px;">
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

