import streamlit as st
import requests
from datetime import datetime

# ========================================================
# AUTOMATYCZNE ŁĄCZENIE BAZ DANYCH Z 5 OSOBNYCH PLIKÓW
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
    .main {background-color: #f4f6f4;}
    h1 {color: #2e5a27; font-family: 'Arial', sans-serif;}
    .stButton>button {background-color: #2e5a27; color: white; border-radius: 10px; width: 100%; font-weight: bold; height: 3em;}
    .stButton>button:hover {background-color: #3d7934; color: white;}
    .card {background-color: white; padding: 20px; border-radius: 10px; box-shadow: 1px 1px 5px rgba(0,0,0,0.05); margin-bottom: 15px;}
    .alert-badge {background-color: #ff4b4b; color: white; padding: 4px 8px; border-radius: 5px; font-weight: bold; font-size: 0.8rem; display: inline-block; margin-right: 5px;}
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
        return "🌑 Nów", "Dni Korzenia. Czas na walkę ze szkodnikami, plewienie i przycinanie pędów. Nie siejemy!"
    elif faza < 0.47:
        return "🌓 Pierwsza kwadra", "Dni Liścia i Kwiatu. Soki idą w górę. Świetny moment na siew sałaty, ziół i rozsad."
    elif faza < 0.53:
        return "🌕 Pełnia", "Dni Owocu. Ziemia odpoczywa. Idealny czas na nawożenie (gnojówki) i zbiory do natychmiastowego spożycia."
    else:
        return "🌗 Ostatnia kwadra", "Dni Korzenia. Soki schodzą w dół. Najlepszy czas na siew marchewki, pietruszki, rzodkiewki."

baza_imienin = {
    1: {1: "Mieszka, Mieczysława", 2: "Makarego, Bazylego", 22: "Wincentego, Anastazego"},
    2: {2: "Marii, Mirosława", 14: "Walentego, Cyryla"},
    3: {4: "Kazimierza, Łucji", 19: "Józefa, Bogdana"},
    4: {23: "Wojciecha, Jerzego", 30: "Mariana, Katarzyny"},
    5: {1: "Józefa, Filipa", 8: "Stanisława, Lizy", 12: "Pankracego (Ogrodnika)", 13: "Serwacego (Ogrodnika)", 14: "Bonifacego (Ogrodnika)", 15: "Zofii (Zimnej Zośki), Izydora", 22: "Heleny, Julii", 23: "Emilii, Iwony"},
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
st.sidebar.markdown("### 📅 Kalendarz")
st.sidebar.markdown(f"**Data:** {pelna_data}\n\n**Dzień roku:** {dzien_roku}/365\n\n**Imieniny:** {imieniny}")

faza_nazwa, faza_porada = pobierz_faze_ksiezyca()
st.sidebar.markdown(f"### 🌙 Kalendarz Księżycowy")
st.sidebar.info(f"**Dzisiejsza faza:** {faza_nazwa}\n\n*Wytyczne:* {faza_porada}")


# ==========================================
# 3. LOGIKA: DANE METEOROLOGICZNE IMGW API
# ==========================================
st.sidebar.markdown("### 🌤️ Pogoda dla Polski (IMGW)")

@st.cache_data(ttl=3600)
def pobierz_pogode_imgw():
    try:
        url = "https://imgw.pl"
        odpowiedz = requests.get(url, timeout=5)
        if odpowiedz.status_code == 200:
            return odpowiedz.json()
    except:
        return None

dane_pogodowe = pobierz_pogode_imgw()

if dane_pogodowe:
    stacje = [stacja['stacja'] for stacja in dane_pogodowe]
    wybrane_miasto = st.sidebar.selectbox("Wybierz stację pomiarową:", sorted(stacje))
    dane_stacji = next(item for item in dane_pogodowe if item["stacja"] == wybrane_miasto)
    
    temp = float(dane_stacji['temperatura'])
    opad = float(dane_stacji['suma_opadu'])
    wilgotnosc = float(dane_stacji.get('wilgotnosc_wzgledna', 0))
    
    col_temp, col_opad, col_wilg = st.sidebar.columns(3)
    col_temp.metric(label="Temp.", value=f"{temp} °C")
    col_opad.metric(label="Opad", value=f"{opad} mm")
    col_wilg.metric(label="Wilg.", value=f"{wilgotnosc} %")
    
    zjawiska = []
    if temp < 2.0:
        zjawiska.append("❄️ Przymrozek")
    if wilgotnosc > 95.0 and temp > 0:
        zjawiska.append("🌫️ Mgła")
    if wilgotnosc > 90.0 and temp <= 0:
        zjawiska.append("🥶 Szadź")
        
    if zjawiska:
        st.sidebar.markdown("**Wykryte zjawiska:**")
        oznaczenia_html = "".join([f"<span class='alert-badge'>{z}</span>" for z in zjawiska])
        st.sidebar.markdown(oznaczenia_html, unsafe_allow_html=True)
    else:
        st.sidebar.markdown("_Brak niebezpiecznych zjawisk._")
        
    if temp < 4.0:
        st.sidebar.error("⚠️ Ryzyko przymrozku! Chroń wrażliwe rozsady agrowłókniną.")
    elif temp > 25.0 and opad == 0:
        st.sidebar.warning("💧 Susza! Pamiętaj o obfitym podlewaniu wcześnie rano.")
    else:
        st.sidebar.success("🌱 Warunki stabilne dla wzrostu.")
else:
    st.sidebar.warning("Nie udało się załadować danych meteo.")


# ==========================================
# 4. INTERFEJS UŻYTKOWNIKA (WYSZUKIWARKA ENCYKLOPEDII)
# ==========================================
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
# 5. MIEJSCE NA STOPKĘ AUTORSKĄ I DEDYKACJĘ
# ==========================================
st.sidebar.markdown("---")
st.sidebar.caption("✍️ Projekt i wykonanie:")
st.sidebar.markdown("Emilia Olszewska maj 2026")

# TUTAJ DODAJEMY ZASTRZEŻENIE O PRAWACH AUTORSKICH
st.sidebar.markdown("<p style='font-size: 0.75rem; color: #888; margin-bottom: 0px;'>© 2026 Grządkowisko. Wszelkie prawa zastrzeżone.</p>", unsafe_allow_html=True)

# Dedykacja z ładną, pochyloną czcionką
st.sidebar.markdown("<p style='font-style: italic; color: #666; font-size: 0.85rem; margin-top: 10px;'>❤️ „Mojemu Tacie, babci Helenie i przyjaciółce Dorotce, a takze tym którzy kochają swoje grządeczki”</p>", unsafe_allow_html=True)

