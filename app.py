import streamlit as st
import requests
from datetime import datetime

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
    </style>
""", unsafe_allow_html=True)

st.title("🌿 Grządkowisko")
st.subheader("Twój inteligentny asystent ogrodowy")

# ==========================================
# 2. LOGIKA: KALENDARZ KSIĘŻYCOWY (FAZY)
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
        url = "http://danepubliczne.imgw.pl/api/data/synop"
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
    
    st.sidebar.metric(label="Temperatura", value=f"{temp} °C")
    st.sidebar.metric(label="Suma opadów", value=f"{opad} mm")
    
    if temp < 4.0:
        st.sidebar.error("⚠️ Ryzyko przymrozku! Chroń wrażliwe rozsady agrowłókniną.")
    elif temp > 25.0 and opad == 0:
        st.sidebar.warning("💧 Susza! Pamiętaj o obfitym podlewaniu wcześnie rano.")
    else:
        st.sidebar.success("🌱 Warunki stabilne dla wzrostu.")
else:
    st.sidebar.warning("Nie udało się załadować danych meteo.")

# ==========================================
# 4. KOMPLETNA BAZA ROŚLIN Z ENCYKLOPEDIĄ
# ==========================================
baza_roslin = {
    "Brokuł": {
        "ph": "6.2 - 7.0", "swiatlo": "Pełne słońce", "woda": "Wysokie", "gleba": "Żyzna, próchnicza",
        "porada": "Młode brokuły osłaniaj siatką przed motylami bielinkami.",
        "korzystne": ["Brukselka", "Jarmuż", "Pasternak", "Pietruszka", "Por", "Ziemniak"],
        "niekorzystne": ["Pomidor", "Cebula"]
    },
    "Brukselka": {
        "ph": "6.5 - 7.5", "swiatlo": "Słoneczne", "woda": "Średnie", "gleba": "Ciężka, gliniasto-gliniasta",
        "porada": "Zrywaj dolne liście jesienią, by przyspieszyć zawiązywanie małych główek.",
        "korzystne": ["Brokuł", "Ziemniak"], "niekorzystne": ["Pomidor"]
    },
    "Burak ćwikłowy": {
        "ph": "6.0 - 7.5", "swiatlo": "Słoneczne do półcienia", "woda": "Średnie", "gleba": "Przepuszczalna",
        "porada": "Buraki uwielbiają bor, rzadko chorują posadzone obok cebuli.",
        "korzystne": ["Cebula", "Cykoria", "Czosnek", "Groch", "Kalarepa", "Kapusta pekińska", "Koper", "Ogórek", "Pomidor", "Por", "Rzepa", "Rzodkiewka", "Sałata", "Seler"],
        "niekorzystne": ["Fasola", "Gorczyca"]
    },
    "Cebula": {
        "ph": "6.5 - 7.0", "swiatlo": "Pełne słońce", "woda": "Niskie", "gleba": "Żyzna, lekka",
        "porada": "Wymieszaj z ziemią fusy z kawy przed sadzeniem dymki – spulchnią glebę i odstraszą szkodniki.",
        "korzystne": ["Burak ćwikłowy", "Cukinie", "Cykoria", "Fasola", "Kalarepa", "Koper", "Marchew", "Ogórek", "Pasternak", "Pomidor", "Por", "Sałata"],
        "niekorzystne": ["Groch", "Fasola tyczna", "Rzodkiewka"]
    },
    "Cukinia": {
        "ph": "6.0 - 7.0", "swiatlo": "Słoneczne, ciepłe", "woda": "Wysokie", "gleba": "Bardzo żyzna, kompostowa",
        "porada": "Podkładaj słomę pod rosnące owoce cukinii, aby uchronić je przed gniciem od wilgotnej ziemi.",
        "korzystne": ["Cebula", "Groch", "Kukurydza", "Szpinak"], "niekorzystne": ["Ziemniak", "Rzodkiewka"]
    },
    "Cykoria": {
        "ph": "6.0 - 6.7", "swiatlo": "Półcień", "woda": "Średnie", "gleba": "Głęboko uprawiona",
        "porada": "Cykoria doskonale drenuje glebę swoimi głębokimi korzeniami.",
        "korzystne": ["Burak ćwikłowy", "Cebula", "Kalarepa", "Marchew", "Pomidor"], "niekorzystne": []
    },
    "Czosnek": {
        "ph": "6.5 - 7.0", "swiatlo": "Słoneczne", "woda": "Niskie", "gleba": "Próchnicza",
        "porada": "Sadź czosnek pod drzewami owocowymi i obok pomidorów – naturalnie ogranicza rozwój chorób grzybowych.",
        "korzystne": ["Burak ćwikłowy", "Marchew", "Pomidor"], "niekorzystne": ["Groch", "Fasola"]
    },
    "Dynia": {
        "ph": "6.0 - 7.0", "swiatlo": "Słoneczne, osłonięte", "woda": "Wysokie", "gleba": "Bardzo bogata w składniki odżywcze",
        "porada": "Dynia świetnie rośnie na pryzmie kompostowej, ocieniając ją swoimi liśćmi.",
        "korzystne": ["Fasola", "Kukurydza"], "niekorzystne": ["Ziemniak"]
    },
    "Endywia": {
        "ph": "6.0 - 6.8", "swiatlo": "Słoneczne", "woda": "Średnie", "gleba": "Żyzna, przepuszczalna",
        "porada": "Związź liście na 2 tygodnie przed zbiorem, aby środek endywii zbladł i stracił gorzki smak.",
        "korzystne": ["Cebula", "Fasola", "Kapusta pekińska", "Koper", "Marchew", "Pomidor", "Por", "Rzodkiewka"], "niekorzystne": []
    },
    "Fasola": {
        "ph": "6.0 - 7.0", "swiatlo": "Słoneczne, osłonięte", "woda": "Średnie", "gleba": "Lekka, ciepła",
        "porada": "Fasola wiąże azot z powietrza w glebie, działając jak darmowy nawóz dla sąsiadów.",
        "korzystne": ["Cebula", "Cukinie", "Endywia", "Groch", "Kalarepa", "Kukurydza", "Ogórek", "Rzepa", "Seler", "Szpinak", "Ziemniak"],
        "niekorzystne": ["Czosnek", "Por", "Burak ćwikłowy"]
    },
    "Groch": {
        "ph": "6.0 - 7.0", "swiatlo": "Słoneczne", "woda": "Średnie", "gleba": "Przepuszczalna, lekka",
        "porada": "Groch poprawia strukturę gleby. Nie sadź go w tym samym miejscu częściej niż co 4 lata.",
        "korzystne": ["Burak ćwikłowy", "Cukinie", "Kalarepa", "Kapusta pekińska", "Kukurydza", "Marchew", "Ogórek", "Rzepa", "Rzodkiewka", "Seler", "Szpinak"],
        "niekorzystne": ["Cebula", "Czosnek", "Por"]
    },
    "Jarmuż": {
        "ph": "6.5 - 7.2", "swiatlo": "Słoneczne do półcienia", "woda": "Średnie", "gleba": "Gliniano-piaszczysta",
        "porada": "Jarmuż smakuje najlepiej po pierwszych przymrozkach – traci wtedy gorycz i zyskuje słodycz.",
        "korzystne": ["Brokuł", "Kapusta pekińska"], "niekorzystne": ["Pomidor"]
    },
    "Kalarepa": {
        "ph": "6.0 - 6.8", "swiatlo": "Słoneczne", "woda": "Regularne", "gleba": "Żyzna, wilgotna",
        "porada": "Nieregularne podlewanie powoduje, że bulwa kalarepy drewnieje i pęka.",
        "korzystne": ["Burak ćwikłowy", "Cebula", "Cykoria", "Fasola", "Groch", "Marchew", "Ogórek", "Pomidor", "Por", "Rzodkiewka", "Seler", "Szpinak", "Ziemniak"],
        "niekorzystne": []
    },
    "Kapusta pekińska": {
        "ph": "6.2 - 7.0", "swiatlo": "Półcień", "woda": "Wysokie", "gleba": "Próchnicza, zasobna",
        "porada": "Uprawiaj ją jako poplon – wysiewana w lipcu rzadziej wybija w pędy kwiatowe.",
        "korzystne": ["Burak ćwikłowy", "Groch", "Jarmuż", "Koper", "Marchew", "Ogórek", "Papryka", "Pietruszka", "Pomidor", "Por", "Sałata", "Seler", "Szpinak"],
        "niekorzystne": ["Rzodkiewka"]
    },
    "Koper": {
        "ph": "6.0 - 7.0", "swiatlo": "Słoneczne", "woda": "Średnie", "gleba": "Przepuszczalna",
        "porada": "Koper ogrodowy wspaniale stymuluje kiełkowanie nasion ogórków posadzonych tuż obok.",
        "korzystne": ["Burak ćwikłowy", "Cebula", "Endywia", "Kapusta pekińska", "Marchew", "Ogórek", "Pietruszka", "Pomidor", "Seler", "Szparag", "Ziemniak"],
        "niekorzystne": []
    },
    "Kukurydza": {
        "ph": "6.0 - 7.0", "swiatlo": "Pełne słońce, gorące", "woda": "Wysokie w okresie kwitnienia", "gleba": "Bardzo bogata, głęboka",
        "porada": "Stanowi naturalną, stabilną tyczkę dla pnącej się fasoli.",
        "korzystne": ["Cukinie", "Dynia", "Fasola", "Groch", "Ogórek", "Pomidor"], "niekorzystne": []
    },
    "Marchew": {
        "ph": "6.0 - 6.8", "swiatlo": "Pełne słońce", "woda": "Średnie", "gleba": "Lekka, piaszczysto-gliniasta",
        "porada": "Siej marchew na przemian z cebulą. Zapachy tych roślin wzajemnie dezorientują ich najgroźniejsze szkodniki.",
        "korzystne": ["Cebula", "Cykoria", "Czosnek", "Groch", "Kalarepa", "Kapusta pekińska", "Koper", "Por", "Rzodkiewka", "Sałata", "Seler", "Szczypiorek", "Szpinak"],
        "niekorzystne": ["Pomidor"]
    },
    "Ogórek": {
        "ph": "6.5 - 7.0", "swiatlo": "Słoneczne, zaciszne", "woda": "Bardzo wysokie (letnia woda!)", "gleba": "Mocno nawożona kompostem",
        "porada": "Zrób nawóz ze skórek bananów (zalej je wodą na 24h) i podlewaj ogórki. Dostarczysz im potas niezbędny do owocowania.",
        "korzystne": ["Burak ćwikłowy", "Cebula", "Fasola", "Groch", "Kalarepa", "Kapusta pekińska", "Koper", "Kukurydza", "Papryka", "Por", "Rzodkiewka", "Sałata", "Seler", "Szpinak"],
        "niekorzystne": ["Pomidor", "Ziemniak"]
    },
    "Papryka": {
        "ph": "6.0 - 6.8", "swiatlo": "Mocno słoneczne, upalne", "woda": "Regularne (wrażliwa na przesuszenie)", "gleba": "Żyzna, próchnicza",
        "porada": "Ściółkuj podłoże wokół papryki, by utrzymać wysoką wilgotność i stałą temperaturę gleby.",
        "korzystne": ["Kapusta pekińska", "Ogórek", "Pomidor"], "niekorzystne": ["Ziemniak"]
    },
    "Pasternak": {
        "ph": "6.0 - 7.0", "swiatlo": "Słoneczne", "woda": "Średnie", "gleba": "Głęboko spulchniona",
        "porada": "Nasiona pasternaku kiełkują bardzo długo – zachowaj cierpliwość, podłoże musi być stale wilgotne.",
        "korzystne": ["Brokuł", "Cebula", "Rzepa", "Rzodkiewka", "Seler", "Szpinak", "Ziemniak"], "niekorzystne": []
    },
    "Pietruszka": {
        "ph": "6.2 - 7.2", "swiatlo": "Słoneczne do półcienia", "woda": "Średnie", "gleba": "Żyzna, przepuszczalna",
        "porada": "Pietruszka rosnąca blisko pomidorów wydajnie poprawia ich ogólny wigor oraz walory smakowe.",
        "korzystne": ["Brokuł", "Kapusta pekińska", "Koper", "Pomidor", "Por", "Rzodkiewka"], "niekorzystne": ["Sałata"]
    },
    "Pomidor": {
        "ph": "5.5 - 6.5", "swiatlo": "Słoneczne, bardzo ciepłe", "woda": "Wysokie (nigdy nie mocz liści!)", "gleba": "Żyzna, próchnicza",
        "porada": "W maju zrób gnojówkę z młodych pokrzyw (1kg na 10L wody). Po rozcieńczeniu 1:10 podlewaj pomidory – dostaną potężnego kopa.",
        "korzystne": ["Aksamitka", "Bazylia", "Burak ćwikłowy", "Cebula", "Cykoria", "Czosnek", "Endywia", "Kalarepa", "Kapusta pekińska", "Koper", "Kukurydza", "Papryka", "Pietruszka", "Por", "Rzodkiewka", "Sałata", "Seler", "Szpinak"],
        "niekorzystne": ["Ziemniak", "Ogórek"]
    },
    "Por": {
        "ph": "6.5 - 7.5", "swiatlo": "Słoneczne", "woda": "Wysokie", "gleba": "Głęboka, żyzna",
        "porada": "Obsypuj pory ziemią w trakcie wzrostu, dzięki czemu uzyskasz dłuższą i grubszą białą część.",
        "korzystne": ["Brokuł", "Burak ćwikłowy", "Cebula", "Endywia", "Kalarepa", "Kapusta pekińska", "Marchew", "Ogórek", "Pietruszka", "Pomidor", "Rzepa", "Rzodkiewka", "Sałata", "Seler", "Szpinak"],
        "niekorzystne": ["Fasola", "Groch"]
    },
    "Rzepa": {
        "ph": "6.0 - 7.0", "swiatlo": "Słoneczne", "woda": "Regularne", "gleba": "Lekka, piaszczysta",
        "porada": "Uprawiaj rzepę wiosną lub jesienią, upały sprawiają, że korzeń staje się łykowaty.",
        "korzystne": ["Burak ćwikłowy", "Fasola", "Groch", "Pasternak", "Por", "Seler"], "niekorzystne": []
    },
    "Rzodkiewka": {
        "ph": "6.0 - 7.0", "swiatlo": "Słoneczne do półcienia", "woda": "Częste, ale oszczędne", "gleba": "Lekka, próchnicza",
        "porada": "Siej rzodkiewkę co 2 tygodnie małymi partiami, aby cieszyć się chrupkimi zbiorami przez cały sezon.",
        "korzystne": ["Burak ćwikłowy", "Endywia", "Groch", "Kalarepa", "Marchew", "Ogórek", "Pasternak", "Pietruszka", "Pomidor", "Por", "Seler", "Szpinak"],
        "niekorzystne": ["Cebula", "Cukinia", "Kapusta pekińska"]
    },
    "Sałata": {
        "ph": "6.0 - 7.0", "swiatlo": "Słoneczne lub delikatny półcień", "woda": "Średnie", "gleba": "Żyzna, przepuszczalna",
        "porada": "Sałata rośnie bardzo szybko, dlatego idealnie sprawdza się jako roślina wskaźnikowa między wolno rosnącymi warzywami.",
        "korzystne": ["Burak ćwikłowy", "Cebula", "Kapusta pekińska", "Marchew", "Ogórek", "Pomidor", "Por", "Szparag"],
        "niekorzystne": ["Pietruszka"]
    },
    "Seler": {
        "ph": "6.5 - 7.5", "swiatlo": "Słoneczne", "woda": "Bardzo wysokie", "gleba": "Bardzo zasobna, próchnicza",
        "porada": "Seler potrzebuje mnóstwa składników odżywczych – ściółkuj go grubą warstwą dojrzałego kompostu.",
        "korzystne": ["Burak ćwikłowy", "Fasola", "Groch", "Kalarepa", "Kapusta pekińska", "Koper", "Marchew", "Ogórek", "Pasternak", "Pomidor", "Por", "Rzepa", "Rzodkiewka", "Szpinak"],
        "niekorzystne": []
    },
    "Skorzonera": {
        "ph": "6.5 - 7.5", "swiatlo": "Słoneczne", "woda": "Średnie", "gleba": "Głęboko przekopana, lekka",
        "porada": "Korzenie skorzonery mogą zimować w gruncie bez przykrycia – zbieraj je na bieżąco zimą.",
        "korzystne": ["Por"], "niekorzystne": []
    },
    "Szczypiorek": {
        "ph": "6.0 - 7.0", "swiatlo": "Słoneczne lub półcień", "woda": "Średnie", "gleba": "Żyzna, wilgotna",
        "porada": "Regularne ścinanie szczypiorku stymuluje go do silniejszego krzewienia się.",
        "korzystne": ["Marchew"], "niekorzystne": []
    },
    "Szparag": {
        "ph": "6.5 - 7.5", "swiatlo": "Pełne słońce", "woda": "Umiarkowane", "gleba": "Piaszczysto-gliniasta, głęboka",
        "porada": "Uprawa szparagów wymaga cierpliwości – pierwsze pełne zbiory przeprowadza się dopiero w 3. roku od posadzenia karp.",
        "korzystne": ["Koper", "Sałata"], "niekorzystne": []
    },
    "Szpinak": {
        "ph": "6.0 - 6.8", "swiatlo": "Półcień", "woda": "Wysokie", "gleba": "Dobra ogrodowa, wilgotna",
        "porada": "Szpinak zawiera saponiny, które stymulują rozwój korzeni innych roślin rosnących w tej samej ziemi.",
        "korzystne": ["Cukinia", "Fasola", "Groch", "Kalarepa", "Kapusta pekińska", "Marchew", "Ogórek", "Pasternak", "Pomidor", "Por", "Rzodkiewka", "Seler"],
        "niekorzystne": []
    },
    "Ziemniak": {
        "ph": "5.0 - 6.0", "swiatlo": "Słoneczne", "woda": "Średnie", "gleba": "Luźna, dobrze napowietrzona",
        "porada": "Nigdy nie sadź ziemniaków po innych psiankowatych, aby zapobiec akumulacji patogenów w glebie.",
        "korzystne": ["Brokuł", "Brukselka", "Fasola", "Koper", "Pasternak"],
        "niekorzystne": ["Cukinia", "Dynia", "Ogórek", "Pomidor", "Papryka"]
    },
    "Aksamitka": {
        "ph": "6.0 - 7.0", "swiatlo": "Słoneczne lub półcień", "woda": "Średnie", "gleba": "Dowolna",
        "porada": "🛡️ Ochronny superbohater! Korzenie aksamitki wydzielają substancje niszczące nicienie glebowe. Zapach zniechęca mszyce i mączliki.",
        "korzystne": ["Pomidor", "Ogórek", "Marchew", "Ziemniak", "Fasola", "Brokuł", "Brukselka", "Burak ćwikłowy", "Cebula", "Cukinia", "Kapusta pekińska", "Papryka", "Por", "Rzodkiewka", "Sałata", "Seler", "Szpinak"],
        "niekorzystne": []
    }
}

# Inteligentne uzupełnianie relacji dwukierunkowych (symetria tabeli)
for roslina, dane in baza_roslin.items():
    for korz in dane["korzystne"]:
        if korz in baza_roslin and roslina not in baza_roslin[korz]["korzystne"]:
            baza_roslin[korz]["korzystne"].append(roslina)
    for niekorz in dane["niekorzystne"]:
        if niekorz in baza_roslin and roslina not in baza_roslin[niekorz]["niekorzystne"]:
            baza_roslin[niekorz]["niekorzystne"].append(roslina)

# ==========================================
# 5. INTERFEJS UŻYTKOWNIKA (KALKULATOR)
# ==========================================
st.markdown("### 🔍 Kalkulator Dobrego Sąsiedztwa Roślin")
st.write("Wybierz dwie rośliny ze swojego ogrodu, aby zweryfikować dopasowanie uprawy współrzędnej.")

lista_roslin = sorted(list(baza_roslin.keys()))

col1, col2 = st.columns(2)
with col1:
    roslina_a = st.selectbox("Roślina główna:", lista_roslin)
with col2:
    lista_sasiadow = [r for r in lista_roslin if r != roslina_a]
    roslina_b = st.selectbox("Sąsiadujące warzywo/zioło:", lista_sasiadow)

if st.button("Sprawdź relację między roślinami 🌿"):
    dane_a = baza_roslin[roslina_a]
    
    st.markdown("---")
    st.markdown(f"### 📊 Wynik analizy dla zestawu: **{roslina_a} + {roslina_b}**")
    
    if roslina_b == "Aksamitka" or roslina_a == "Aksamitka":
        st.success(f"💚 **WYBITNIE KORZYSTNE POŁĄCZENIE!**\n\n🛡️ Ochronny superbohater! Korzenie aksamitki wydzielają substancje niszczące nicienie glebowe, oczyszczając całe podłoże wokół sąsiada. Intensywny zapach dezorientuje mszyce, mączliki oraz śmietki.")
    elif roslina_b in dane_a["korzystne"]:
        st.success(f"💚 **KORZYSTNE SĄSIEDZTWO (Zgodne z tabelą X)!**\n\nTe rośliny doskonale rosną obok siebie. Wykorzystują inne warstwy gleby lub wzajemnie odstraszają swoje szkodniki.")
    elif roslina_b in dane_a["niekorzystne"]:
        st.error(f"❌ **NIEKORZYSTNE SĄSIEDZTWO!**\n\nUnikaj tego połączenia. Rośliny mogą konkurować o te same składniki pokarmowe, wodę lub są podatne na te same choroby (np. zaraza u pomidora i ziemniaka).")
    else:
        st.warning(f"🟡 **STOSUNEK NEUTRALNY.**\n\nRośliny tolerują się wzajemnie na grządce. Nie wpływają negatywnie ani pozytywnie na swój rozwój.")
        
    with st.expander(f"📋 Zobacz pełne wymagania i wskazówki dla: {roslina_a}"):
        st.write(f"• **Odczyn pH gleby:** {dane_a['ph']}")
        st.write(f"• **Wymagane oświetlenie:** {dane_a['swiatlo']}")
        st.write(f"• **Zapotrzebowanie na wodę:** {dane_a['woda']}")
        st.write(f"• **Typ podłoża:** {dane_a['gleba']}")
        st.info(f"💡 **Eko-porada z Grządkowiska:** {dane_a['porada']}")
