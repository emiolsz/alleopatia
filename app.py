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

import requests
import streamlit as st

st.sidebar.markdown("### 🌤️ Pogoda dla Polski (IMGW)")
# Bezpieczna konwersja na float
def safe_float(value, default=0):
    try:
        return float(value)
    except:
        return default
# Pobieranie danych pogodowych
@st.cache_data(ttl=3600)
def pobierz_pogode_imgw():
    try:
        url = "https://danepubliczne.imgw.pl/api/data/synop"

        odpowiedz = requests.get(url, timeout=5)

        if odpowiedz.status_code == 200:
            return odpowiedz.json()
        else:
            return None

    except Exception as e:
        st.sidebar.error(f"Błąd API IMGW: {e}")
        return None


# Pobranie danych
dane_pogodowe = pobierz_pogode_imgw()


# Jeśli dane istnieją
if dane_pogodowe:

    # Lista stacji
    stacje = [stacja['stacja'] for stacja in dane_pogodowe]

    # Wybór miasta
    wybrane_miasto = st.sidebar.selectbox(
        "Wybierz stację pomiarową:",
        sorted(stacje)
    )

    # Dane wybranej stacji
    dane_stacji = next(
        (
            item for item in dane_pogodowe
            if item["stacja"] == wybrane_miasto
        ),
        None
    )

    if dane_stacji:

        # Pobranie parametrów
        temp = safe_float(dane_stacji.get('temperatura'))
        opad = safe_float(dane_stacji.get('suma_opadu'))
        wilgotnosc = safe_float(
            dane_stacji.get('wilgotnosc_wzgledna')
        )

        # METRYKI
        col_temp, col_opad, col_wilg = st.sidebar.columns(3)

        col_temp.metric(
            label="Temp.",
            value=f"{temp} °C"
        )

        col_opad.metric(
            label="Opad",
            value=f"{opad} mm"
        )

        col_wilg.metric(
            label="Wilg.",
            value=f"{wilgotnosc} %"
        )

        # Wykrywanie zjawisk
        zjawiska = []

        # Przymrozek
        if temp < 2.0:
            zjawiska.append("❄️ Przymrozek")

        # Mgła
        if wilgotnosc > 95.0 and temp > 0:
            zjawiska.append("🌫️ Mgła")

        # Szadź
        if wilgotnosc > 90.0 and temp <= 0:
            zjawiska.append("🥶 Szadź")

        # Wyświetlanie zjawisk
        if zjawiska:

            st.sidebar.markdown("**Wykryte zjawiska:**")

            for zjawisko in zjawiska:
                st.sidebar.markdown(
                    f"<span class='alert-badge'>{zjawisko}</span>",
                    unsafe_allow_html=True
                )

        else:
            st.sidebar.markdown(
                "_Brak niebezpiecznych zjawisk._"
            )

        # Komunikaty rolnicze
        if temp < 4.0:

            st.sidebar.error(
                "⚠️ Ryzyko przymrozku! "
                "Chroń rozsady agrowłókniną."
            )

        elif temp > 25.0 and opad == 0:

            st.sidebar.warning(
                "💧 Susza! "
                "Pamiętaj o podlewaniu rano."
            )

        else:

            st.sidebar.success(
                "🌱 Warunki stabilne dla wzrostu."
            )

else:
    st.sidebar.warning(
        "Nie udało się załadować danych meteo."
    )
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
# 5. INTERFEJS UŻYTKOWNIKA (WYSZUKIWARKA ENCYKLOPEDII)
# ==========================================
st.markdown("<br>", unsafe_allow_html=True)
if baza_roslin:
    wybrana_roslina = st.selectbox("🔍 Wybierz obiekt z encyklopedii:", list(baza_roslin.keys()))
    
    if wybrana_roslina:
        dane = baza_roslin[wybrana_roslina]
        
        st.markdown(f"### 📖 Karta obiektu: {wybrana_roslina} ({dane.get('typ', 'Roślina')})")
        
        with st.container():
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**🧪 Wymagane pH gleby:** {dane['ph']}")
                st.write(f"**☀️ Stanowisko / Światło:** {dane['swiatlo']}")
            with col2:
                st.write(f"**💧 Zapotrzebowanie na wodę:** {dane['woda']}")
                st.write(f"**🌱 Preferowany rodzaj gleby:** {dane['gleba']}")
                
        st.info(f"💡 **Porada eksperta i uprawa:** {dane['porada']}")
        
        col_k, col_nk = st.columns(2)
        with col_k:
            st.success("👍 **Dobre sąsiedztwo / Dobre pary:**\n\n" + ", ".join(dane["korzystne"]) if dane["korzystne"] else "Brak szczególnych partnerów")
        with col_nk:
            st.error("👎 **Złe sąsiedztwo (Unikać):**\n\n" + ", ".join(dane["niekorzystne"]) if dane["niekorzystne"] else "Brak wyraźnych wrogów")
else:
    st.info("Dodaj bazy danych na GitHubie (`warzywa.py`, `krzewy.py`, `ziola.py`, `kwiaty.py`, `drzewa.py`), aby encyklopedia zaczęła działać.")


# ==========================================
# 6. MIEJSCE NA STOPKĘ AUTORSKĄ I DEDYKACJĘ 
# ==========================================
# ========================================================
# INFORMACJE O PROJEKCIE GRZĄDKOWISKO
# WYTYCZNE DO APLIKACJI POWSTAWAŁY W LATACH 2023 DO 2026 roku
# Data zaprojektowania aplikacji: 19-22 maja 2026 roku
# Status: Wersja PODSTAWOWA UKOŃCZONA 22 MAJA 2026 ROKU
# ========================================================

st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
st.sidebar.markdown("---")

st.sidebar.html("""
<div style="text-align: center; font-family: Arial, sans-serif; background-color: #1e3d19 !important; padding: 10px 0; width: 100%;">
    <!-- Dedykacja -->
    <p style="font-style: italic; color: #d0e1cd; font-size: 0.82rem; line-height: 1.5; margin: 0 0 25px 0;">
        🌿 „Aplikację dedykuję Mojemu Tacie, babci Helence i przyjaciółce Dorotce, a także tym którzy kochają swoje grządeczki z serdecznością”
    </p>
    
    <!-- Mała, wyśrodkowana nota autorska i prawna -->
    <p style="margin: 0; font-size: 0.72rem; color: #a3c2a0; letter-spacing: 0.5px;">
        Projekt i wykonanie: <span style="color: #ffffff; font-weight: bold;">Emilia Olszewska</span>
    </p>
    <p style="margin: 4px 0 0 0; font-size: 0.68rem; color: #8cb388;">
        © 2026 Grządkowisko 🥕🌸🍃🍎
        Wszelkie prawa zastrzeżone
    </p>
</div>
""")

