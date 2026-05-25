import streamlit as st
import requests
from datetime import datetime
# zmniejszenie marginesow na telefonie
st.markdown(
    """
    <style>
    /* Zmniejsza boczne marginesy aplikacji na telefonie */
    .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        padding-top: 1rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

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

# 6. Import z porady_dnia.py oraz definicja funkcji
try:
    from porady_dnia import porady_dnia
    
    # Wklejamy funkcję tutaj, żeby była dostępna w całym pliku!
    def pobierz_porade_dnia():
        dzis = datetime.now()
        numer_dnia = dzis.timetuple().tm_yday
        
        # Bezpiecznik: jeśli słownik jest pusty, zwróć domyślny tekst
        if not porady_dnia:
            return "Udanej pracy w ogrodzie!"
            
        # Jeśli porady_dnia to słownik, bierzemy klucz, jeśli lista - indeks
        if isinstance(porady_dnia, dict):
            return porady_dnia.get(numer_dnia, "Dbaj o swoje rośliny!")
        
        indeks = numer_dnia % len(porady_dnia)
        return porady_dnia[indeks]

except ImportError:
    porady_dnia = {}
    def pobierz_porade_dnia():
        return "Udanej pracy w ogrodzie!"

# ==========================================
# 1. KONFIGURACJA STRONY I WIZUALNEGO STYLU
# ==========================================
st.set_page_config(
    page_title="Grządkowisko",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown("""
<style>

/* ==========================================
   TŁO CAŁEJ APLIKACJI
========================================== */

.stApp {
    background-color: #F4F7F4 !important;
}

/* ==========================================
   SIDEBAR - GŁĘBOKA ZIELEŃ
========================================== */

section[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #0D2B16 0%,
        #14361F 45%,
        #1B4027 100%
    ) !important;

    width: 33vw !important;
    min-width: 370px !important;
    max-width: 520px !important;

    border-right: 2px solid rgba(255,255,255,0.06);
}

/* poprawka szerokości */
section[data-testid="stSidebar"] > div {
    width: 100% !important;
    color: white !important;
}

/* ==========================================
   BIAŁE LITERKI W SIDEBAR
========================================== */

section[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
}

/* selectbox w sidebar */
section[data-testid="stSidebar"] .stSelectbox label {
    color: #FFFFFF !important;
}

/* metryki */
section[data-testid="stSidebar"] [data-testid="metric-container"] {
    background: rgba(255,255,255,0.08) !important;

    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.08);

    padding: 12px;
}

/* ==========================================
   KARTY SIDEBAR
========================================== */

.sidebar-card {
    background: rgba(255,255,255,0.08);

    border-radius: 18px;
    padding: 18px;

    border: 1px solid rgba(255,255,255,0.08);

    margin-bottom: 16px;

    box-shadow: 0 6px 18px rgba(0,0,0,0.18);
}

/* ==========================================
   GŁÓWNA TREŚĆ
========================================== */

.main .block-container {
    max-width: 1400px;

    padding-top: 2rem;
    padding-left: 4rem;
    padding-right: 4rem;
    padding-bottom: 2rem;
}

/* ==========================================
   NAGŁÓWKI
========================================== */

h1 {
    color: #18311E !important;
    font-size: 2.4rem !important;
    font-weight: 800 !important;
}

h2, h3 {
    color: #26452E !important;
}

/* ==========================================
   SELECTBOX GŁÓWNY
========================================== */

.stSelectbox > div > div {
    border-radius: 12px !important;
}

/* ==========================================
   INFO BOX
========================================== */

[data-testid="stInfo"] {
    border-radius: 16px !important;
}

[data-testid="stSuccess"] {
    border-radius: 16px !important;
}

[data-testid="stError"] {
    border-radius: 16px !important;
}

/* ==========================================
   TABLET
========================================== */

@media (max-width: 1024px) {

    section[data-testid="stSidebar"] {
        width: 38vw !important;
        min-width: 300px !important;
    }

    .main .block-container {
        padding-left: 2rem;
        padding-right: 2rem;
    }
}

/* ==========================================
   TELEFON
========================================== */

@media (max-width: 768px) {

    section[data-testid="stSidebar"] {
        width: 88vw !important;
        min-width: unset !important;
    }

    .main .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }

    h1 {
        font-size: 1.8rem !important;
        text-align: center;
    }

    h3 {
        font-size: 1rem !important;
    }

    .sidebar-card {
        padding: 14px;
    }
}

</style>
""", unsafe_allow_html=True)

st.title("🌿 Grządkowisko")
st.subheader("Twój inteligentny asystent ogrodowy")

# wywołanie funkcji "pobierz_porade_dnia()"
porada_dnia = pobierz_porade_dnia()  

st.markdown("### 🌿 Porada dnia")
st.info(f"**{porada_dnia}**")
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
            value=f"{temp:.1f}°C"
        )

        col_opad.metric(
            label="Opad",
            value=f"{opad:.1f}mm"
        )

        col_wilg.metric(
            label="Wilg.",
            value=f"{wilgotnosc:.0f}%"
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

