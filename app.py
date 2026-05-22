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
    /* Prawa strona: Pełny, jednolity, gładki kolor seledynowy (zero przezroczystości) */
    .stApp {
        background-color: #e2f7df !important;
    }
    
    /* Lewa strona (panel boczny): Pełny, solidny kolor ciemnozielony (zero przezroczystości) */
    section[data-testid="stSidebar"] {
        background-color: #1e3d19 !important;
    }
    
    /* Kolory nagłówków na głównej stronie */
    h1 {color: #1e3d19; font-family: 'Arial', sans-serif; font-weight: bold;}
    h3 {color: #2e5a27; font-family: 'Arial', sans-serif;}
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

# Wyświetlanie bocznego panelu za pomocą st.sidebar.html (Bezpieczna, niezależna struktura w ciemnej zieleni)
st.sidebar.html(f"""
    <div style="font-family: Arial, sans-serif; color: #ffffff; padding: 5px 0;">
        <h3 style="color: #ffffff; margin-bottom: 10px; font-size: 1.3rem;">📅 Kalendarz</h3>
        <p style="margin: 4px 0; color: #ffffff;"><b>Data:</b> {pelna_data}</p>
        <p style="margin: 4px 0; color: #ffffff;"><b>Dzień roku:</b> {dzien_roku}/365</p>
        <p style="margin: 4px 0; margin-bottom: 25px; color: #ffffff;"><b>Imieniny:</b> {imieniny}</p>
        
        <h3 style="color: #ffffff; margin-bottom: 10px; font-size: 1.3rem;">🌙 Kalendarz Księżycowy</h3>
        <div style="background-color: rgba(255, 255, 255, 0.1); padding: 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.15); margin-bottom: 20px;">
            <p style="margin: 0 0 8px 0; color: #ffffff;"><b>Dzisiejsza faza:</b> {faza_nazwa}</p>
            <p style="margin: 0; font-size: 0.9rem; line-height: 1.4; color: #ffffff;"><b>Wytyczne:</b> {faza_porada}</p>
        </div>
        
        <h3 style="color: #ffffff; margin-bottom: 10px; font-size: 1.1rem;">📋 Legenda symboli biodynamicznych:</h3>
        <div style="background-color: rgba(255, 255, 255, 0.05); padding: 10px; border-radius: 8px; font-size: 0.85rem; color: #ffffff; margin-bottom: 25px;">
            <p style="margin: 4px 0; color: #ffffff;">🥕 — Dni Korzenia (marchew, burak, czosnek)</p>
            <p style="margin: 4px 0; color: #ffffff;">🍃 — Dni Liścia (sałata, zioła, kapusta)</p>
            <p style="margin: 4px 0; color: #ffffff;">🌸 — Dni Kwiatu (kwiaty pożyteczne, kalafior)</p>
            <p style="margin: 4px 0; color: #ffffff;">🍎 — Dni Owocu (pomidor, ogórek, drzewa owocowe)</p>
        </div>
    </div>
""")
 
# ==========================================
# 3. LOGIKA: POGODA DLA TWOJEJ MIEJSCOWOŚCI
# ==========================================
st.sidebar.html("""<h3 style="color: #ffffff !important; margin-top: 5px; margin-bottom: 5px; font-size: 1.3rem; font-family: Arial, sans-serif;">🌤️ Pogoda Lokalna</h3>""")

# Pole tekstowe do wpisania lokalizacji przez działkowicza
lokalizacja = st.sidebar.text_input("📍 Wpisz swoją miejscowość / wieś:", value="Warszawa")

@st.cache_data(ttl=1800)
def pobierz_pogode_lokalna(miasto):
    try:
        # 1. Geokodowanie - zamiana nazwy miejscowości na współrzędne geograficzne
        geo_url = f"https://open-meteo.com{miasto}&count=1&language=pl&format=json"
        geo_res = requests.get(geo_url, timeout=5).json()
        
        if not geo_res.get("results"):
            return None
            
        lat = geo_res["results"][0]["latitude"]
        lon = geo_res["results"][0]["longitude"]
        nazwa_pelna = geo_res["results"][0]["name"]
        
        # 2. Pobieranie dokładnych danych meteo dla tych współrzędnych
        weather_url = f"https://open-meteo.com{lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,precipitation&timezone=auto"
        w_res = requests.get(weather_url, timeout=5).json()
        
        current = w_res["current"]
        return {
            "miasto": nazwa_pelna,
            "temp": float(current["temperature_2m"]),
            "wilgotnosc": float(current["relative_humidity_2m"]),
            "opad": float(current["precipitation"])
        }
    except:
        return None

dane_pogodowe = pobierz_pogode_lokalna(lokalizacja)

if dane_pogodowe:
    temp = dane_pogodowe["temp"]
    opad = dane_pogodowe["opad"]
    wilgotnosc = dane_pogodowe["wilgotnosc"]
    
    st.sidebar.html(f"""
        <p style="color: #d0e1cd !important; font-size: 0.85rem; margin: 0 0 10px 0; font-family: Arial, sans-serif;">Wyniki dla: <b>{dane_pogodowe['miasto']}</b></p>
        <div style="display: flex; justify-content: space-between; font-family: Arial, sans-serif; text-align: center;">
            <div style="background: rgba(255,255,255,0.08); padding: 8px; border-radius: 6px; width: 30%;">
                <span style="font-size: 0.75rem; color: #ccc; display: block;">Temp.</span>
                <span style="font-size: 1.1rem; font-weight: bold; color: #fff;">{temp} °C</span>
            </div>
            <div style="background: rgba(255,255,255,0.08); padding: 8px; border-radius: 6px; width: 30%;">
                <span style="font-size: 0.75rem; color: #ccc; display: block;">Opad</span>
                <span style="font-size: 1.1rem; font-weight: bold; color: #fff;">{opad} mm</span>
            </div>
            <div style="background: rgba(255,255,255,0.08); padding: 8px; border-radius: 6px; width: 30%;">
                <span style="font-size: 0.75rem; color: #ccc; display: block;">Wilg.</span>
                <span style="font-size: 1.1rem; font-weight: bold; color: #fff;">{wilgotnosc} %</span>
            </div>
        </div>
    """)
    
    # Wykrywanie przymrozków, mgły i szadzi
    zjawiska = []
    if temp < 2.0: zjawiska.append("❄️ Przymrozek")
    if wilgotnosc > 95.0 and temp > 0: zjawiska.append("🌫️ Mgła")
    if wilgotnosc > 90.0 and temp <= 0: zjawiska.append("🥶 Szadź")
    
    if zjawiska:
        badges_html = "".join([f"<span style='background:#ff4b4b; color:white; padding:3px 6px; border-radius:4px; font-size:0.75rem; font-weight:bold; margin-right:5px; display:inline-block;'>{z}</span>" for z in zjawiska])
        st.sidebar.html(f"<div style='margin-top:12px; font-family:Arial,sans-serif; color:white;'><span style='font-size:0.85rem; display:block; margin-bottom:5px;'><b>Wykryte zjawiska:</b></span>{badges_html}</div>")
    else:
        st.sidebar.html("<p style='color:#bbb; font-size:0.8rem; font-style:italic; margin-top:10px; font-family:Arial,sans-serif;'>Brak niebezpiecznych zjawisk.</p>")
        
    if temp < 4.0:
        st.sidebar.error("⚠️ Ryzyko przymrozku!")
    elif temp > 25.0 and opad == 0:
        st.sidebar.warning("💧 Susza!")
    else:
        st.sidebar.success("🌱 Warunki stabilne.")
else:
    st.sidebar.html("<p style='color:#ffaa00; font-size:0.85rem; margin-top:10px; font-family:Arial,sans-serif;'>⚠️ Nie znaleziono miejscowości lub błąd pobierania.</p>")


# ==========================================
# 4. INTERFEJS UŻYTKOWNIKA (WYSZUKIWARKA ENCYKLOPEDII)
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
# 5. MIEJSCE NA STOPKĘ AUTORSKĄ I DEDYKACJĘ 
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
            ❤️ „ Aplikację dedykuję Mojemu Tacie, babci Helence i przyjaciółce Dorotce, a także tym którzy kochają swoje grządeczki z serdecznością”
        </p>
        
        <!-- Mała, wyśrodkowana nota autorska i prawna (taki sam rozmiar) -->
        <p style="margin: 0; font-size: 0.72rem; color: #a3c2a0; letter-spacing: 0.5px;">
            Projekt i wykonanie: <span style="color: #ffffff; font-weight: bold;">Emilia Olszewska</span>
        </p>
        <p style="margin: 4px 0 0 0; font-size: 0.68rem; color: #8cb388;">
        © 2026 Grządkowisko 🥕🌸🍃🍎 Wszelkie prawa zastrzeżone
        </p>
    </div>
""")
