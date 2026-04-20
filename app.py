import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Bananita Market", layout="wide")
# --- FUNCIÓN DE CONEXIÓN A LA API DE ALBION PARA REFINACIÓN ---
@st.cache_data(ttl=300) # Guarda los datos 5 minutos
def consultar_api_albion(items_list, locations_list):
    items_str = ",".join(items_list)
    locs_str = ",".join(locations_list)
    url = f"https://www.albion-online-data.com/api/v2/stats/prices/{items_str}?locations={locs_str}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        st.error("Error conectando a la API de Albion.")
    return []

# --- FUNCIÓN DE CONEXIÓN PARA EL HISTORIAL DE PRECIOS ---
@st.cache_data(ttl=3600) # Guardamos el historial 1 hora para no saturar
def consultar_historial(item_id, ciudad):
    # time-scale=1 significa que nos dará el promedio por hora
    url = f"https://www.albion-online-data.com/api/v2/stats/history/{item_id}?locations={ciudad}&time-scale=1"
    
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            datos_json = resp.json()
            # Verificamos que la API nos haya devuelto datos válidos
            if datos_json and len(datos_json) > 0 and 'data' in datos_json[0]:
                historial = datos_json[0]['data']
                df = pd.DataFrame(historial)
                
                # Convertimos la fecha de la API a un formato legible
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                # Usamos la fecha como el índice principal (eje X del gráfico)
                df = df.set_index('timestamp')
                # Renombramos la columna para que se vea bonita en el gráfico
                df = df.rename(columns={'avg_price': 'Precio Promedio'})
                
                return df[['Precio Promedio']]
    except Exception as e:
        pass
    
    return None

# 1. EL NUEVO CATÁLOGO UNIVERSAL (Puedes agregar lo que quieras aquí)
catalogo = {
    "Recursos Básicos": {
        "Mineral (Crudo)": "ORE", "Lingote (Refinado)": "METALBAR",
        "Madera (Cruda)": "WOOD", "Tablas (Refinadas)": "PLANKS",
        "Piel (Cruda)": "HIDE", "Cuero (Refinado)": "LEATHER",
        "Algodón (Crudo)": "FIBER", "Tela (Refinada)": "CLOTH"
    },

    # --- BLOQUE DE ESPADAS ---
    "Armas - Espadas": {
        "Espada Ancha": "MAIN_SWORD",
        "Claymore": "2H_CLAYMORE",
        "Espadas Dobles": "2H_DUALSWORD",
        "Espada Clarent": "MAIN_SCIMITAR_MORGANA",
        "Espada Tallada (Carving)": "2H_CLEAVER_HELL",
        "Pares Galatinos": "2H_DUALSCIMITAR_UNDEAD",
        "Hacedor de Reyes (Kingmaker)": "2H_CLAYMORE_AVALON",
        "Espada del Infinito (Infinity)": "MAIN_SWORD_CRYSTAL"
    },
    
    # --- BLOQUE DE HACHAS ---
    "Armas - Hachas": {
        "Hacha de Batalla": "MAIN_AXE",
        "Gran Hacha": "2H_AXE",
        "Alabarda": "2H_HALBERD",
        "Hacha de la Carroña": "MAIN_HALBERD_MORGANA",
        "Hacha Desgarradora (Infernal)": "2H_SCYTHE_HELL",
        "Patas de Oso (Bear Paws)": "2H_DUALAXE_KEEPER",
        "Romperreinos (Realmbreaker)": "2H_AXE_AVALON",
        "Segador de Cristal (Crystal Reaper)": "2H_AXE_CRYSTAL"
    },

    # --- BLOQUE DE MAZAS ---
    "Armas - Mazas": {
        "Maza (Una mano)": "MAIN_MACE",
        "Maza Pesada": "2H_MACE",
        "Lucero del Alba (Morning Star)": "2H_FLAIL",
        "Maza de Camlann": "2H_MACE_MORGANA",
        "Maza del Súcubo (Bedrock)": "MAIN_MACE_HELL",
        "Incinerador (Incubus)": "MAIN_MACE_KEEPER",
        "Mano de Justicia": "2H_MACE_AVALON",
        "Vanguardia de Cristal": "MAIN_MACE_CRYSTAL"
    },

    # --- BLOQUE DE MARTILLOS ---
    "Armas - Martillos": {
        "Martillo (Una mano)": "MAIN_HAMMER",
        "Martillo de Poste": "2H_POLEHAMMER",
        "Gran Martillo": "2H_HAMMER",
        "Martillo de Tumba (Tombhammer)": "2H_TOMBHAMMER_UNDEAD",
        "Martillos de Forja": "2H_DUALHAMMER_HELL",
        "Guardián de la Arboleda (Grovekeeper)": "2H_RAM_KEEPER",
        "Mano de la Justicia": "2H_HAMMER_AVALON",
        "Triturador de Cristal (Crystal Crusher)": "MAIN_HAMMER_CRYSTAL"
    },

    # --- BLOQUE DE GUANTES DE GUERRA ---
    "Armas - Guantes de Guerra": {
        "Guantes de Peleador": "2H_KNUCKLES_SET1",
        "Brazaletes de Batalla": "2H_KNUCKLES_SET2",
        "Guanteletes de Púas": "2H_KNUCKLES_SET3",
        "Desgarradores Osunos": "2H_KNUCKLES_KEEPER",
        "Manos de Fuego Infernal": "2H_KNUCKLES_HELL",
        "Cestus Golpe de Cuervo": "2H_KNUCKLES_UNDEAD",
        "Puños de Avalon": "2H_KNUCKLES_AVALON",
        "Puños de Cristal": "2H_KNUCKLES_CRYSTAL"
    },

    # --- BLOQUE DE BALLESTAS ---
    "Armas - Ballestas": {
        "Ballesta Ligera": "MAIN_CROSSBOW",
        "Ballesta (Normal)": "2H_CROSSBOW",
        "Ballesta Pesada": "2H_CROSSBOWLARGE",
        "Llorón (Weeping Repeater)": "2H_REPEATINGCROSSBOW_UNDEAD",
        "Ballesta de Asedio (Siegebow)": "2H_DUALCROSSBOW_HELL",
        "Hacedor de Energía (Energy Shaper)": "2H_CROSSBOW_CANNON_AVALON",
        "Blásteres de Luz (Arclight)": "MAIN_CROSSBOW_CRYSTAL"
    },

    # --- BLOQUE DE ARCOS ---
    "Armas - Arcos": {
        "Arco Normal": "2H_BOW",
        "Arco de Guerra": "2H_WARBOW",
        "Arco Largo": "2H_LONGBOW",
        "Arco Susurrante (No-Muerto)": "2H_LONGBOW_UNDEAD",
        "Arco Plañidero (Infernal)": "2H_BOW_HELL",
        "Arco de Badon (Guardián)": "2H_BOW_KEEPER",
        "Perforanieblas (Avalon)": "2H_BOW_AVALON",
        "Arco de Cristal (Cristal)": "2H_BOW_CRYSTAL"
    },

    # --- BLOQUE DE DAGAS ---
    "Armas - Dagas": {
        "Daga (Una mano)": "MAIN_DAGGER",
        "Dagas Dobles": "2H_DAGGERPAIR",
        "Garras": "2H_CLAWPAIR",
        "Sangradora (Morgana)": "MAIN_RAPIER_MORGANA",
        "Exigentes (No-Muerto)": "2H_DUALSICKLE_UNDEAD",
        "Colmillos Demoníacos (Infernal)": "MAIN_DAGGER_HELL",
        "Furia Desatada (Avalon)": "2H_DAGGER_KATAR_AVALON",
        "Daga de Cristal (Cristal)": "MAIN_DAGGER_CRYSTAL"
    },

    # --- BLOQUE DE LANZAS ---
    "Armas - Lanzas": {
        "Lanza (Una mano)": "MAIN_SPEAR",
        "Pica": "2H_SPEAR",
        "Guja (Glaive)": "2H_GLAIVE",
        "Lanza de Garza (Guardián)": "MAIN_SPEAR_KEEPER",
        "Cazaespíritus (Infernal)": "2H_HARPOON_HELL",
        "Tridente Demoníaco (No-Muerto)": "2H_TRIDENT_UNDEAD",
        "Rompealbores (Avalon)": "MAIN_SPEAR_LANCE_AVALON",
        "Lanza de Cristal (Cristal)": "MAIN_SPEAR_CRYSTAL"
    },
    
    # --- BLOQUE DE VARAS (Quarterstaffs) ---
    "Armas - Varas": {
        "Vara (Normal)": "2H_QUARTERSTAFF",
        "Vara de Hierro": "2H_IRONCLADEDSTAFF",
        "Vara de Doble Filo": "2H_DOUBLEBLADEDSTAFF",
        "Bastón de Monje Negro (Morgana)": "2H_COMBATSTAFF_MORGANA",
        "Guadaña de Almas (Infernal)": "2H_TWINSCYTHE_HELL",
        "Bastón de Equilibrio (Guardián)": "2H_ROCKSTAFF_KEEPER",
        "Buscagriales (Avalon)": "2H_QUARTERSTAFF_AVALON",
        "Vara de Cristal (Cristal)": "2H_QUARTERSTAFF_CRYSTAL"
    },

    # --- BLOQUE DE BASTONES CAMBIAFORMAS (Shapeshifter) ---
    "Armas - Cambiaformas": {
        "Bastón Acechador (Pantera)": "2H_SHAPESHIFTER_SET1",
        "Bastón Silvano (Ent)": "2H_SHAPESHIFTER_SET2",
        "Bastón de Ave del Alba (Pájaro)": "2H_SHAPESHIFTER_SET3",
        "Bastón de Luna Sangrienta (Hombre Lobo)": "2H_SHAPESHIFTER_MORGANA",
        "Bastón de Tejesombras (Guardián)": "2H_SHAPESHIFTER_KEEPER",
        "Bastón de Arrancarraíces (Infernal)": "2H_SHAPESHIFTER_HELL",
        "Bastón Clamastros (Avalon)": "2H_SHAPESHIFTER_AVALON",
        "Bastón Cambiaformas de Cristal": "2H_SHAPESHIFTER_CRYSTAL"
    },

    # --- BLOQUE DE BASTONES DE NATURALEZA ---
    "Armas - Bastones de Naturaleza": {
        "Bastón de Naturaleza": "MAIN_NATURESTAFF",
        "Gran Bastón de Naturaleza": "2H_NATURESTAFF",
        "Bastón Salvaje": "2H_WILDSTAFF",
        "Bastón Druídico (Morgana)": "MAIN_NATURESTAFF_MORGANA",
        "Bastón de Plaga (Infernal)": "2H_NATURESTAFF_HELL",
        "Bastón Desenfrenado (Guardián)": "2H_NATURESTAFF_KEEPER",
        "Báculo de Vida (Avalon)": "MAIN_NATURESTAFF_AVALON",
        "Bastón de Naturaleza de Cristal": "MAIN_NATURESTAFF_CRYSTAL"
    },

    # --- BLOQUE DE BASTONES DE FUEGO (Piromante) ---
    "Armas - Bastones de Fuego": {
        "Bastón de Fuego (Una mano)": "MAIN_FIRESTAFF",
        "Gran Bastón de Fuego": "2H_FIRESTAFF",
        "Bastón Infernal": "2H_INFERNOSTAFF",
        "Fuego Salvaje (Guardián)": "MAIN_FIRESTAFF_KEEPER",
        "Bastón de Azufre (Infernal)": "2H_FIRESTAFF_HELL",
        "Bastón Abrasador (Morgana)": "2H_INFERNOSTAFF_MORGANA",
        "Canto del Alba (Avalon)": "2H_FIRE_RINGPAIR_AVALON",
        "Bastón de Fuego de Cristal": "MAIN_FIRESTAFF_CRYSTAL"
    },

    # --- BLOQUE DE BASTONES SAGRADOS (Sacerdote) ---
    "Armaduras - Bastones Sagrados": {
        "Bastón Sagrado (Una mano)": "MAIN_HOLYSTAFF",
        "Gran Bastón Sagrado": "2H_HOLYSTAFF",
        "Bastón Divino": "2H_DIVINESTAFF",
        "Bastón de Vida (Morgana)": "MAIN_HOLYSTAFF_MORGANA",
        "Bastón de Caído (Infernal)": "2H_HOLYSTAFF_HELL",
        "Bastón de Redención (No-Muerto)": "2H_HOLYSTAFF_UNDEAD",
        "Bastón Hueco (Avalon)": "MAIN_HOLYSTAFF_AVALON",
        "Bastón Sagrado de Cristal": "2H_HOLYSTAFF_CRYSTAL"
    },

    # --- BLOQUE DE BASTONES ARCANOS ---
    "Armas - Bastones Arcanos": {
        "Bastón Arcano (Una mano)": "MAIN_ARCANESTAFF",
        "Gran Bastón Arcano": "2H_ARCANESTAFF",
        "Bastón Enigmático": "2H_ENIGMATICSTAFF",
        "Bastón de Brujería (Morgana)": "MAIN_ARCANESTAFF_MORGANA",
        "Bastón de Ocultismo (Infernal)": "2H_ARCANESTAFF_HELL",
        "Bastón de Vacío (No-Muerto)": "2H_ENIGMATICORB_UNDEAD",
        "Segador Estelar (Avalon)": "2H_ARCANESTAFF_AVALON",
        "Bastón Arcano de Cristal": "MAIN_ARCANESTAFF_CRYSTAL"
    },

    # --- BLOQUE DE BASTONES DE ESCARCHA (Hielo) ---
    "Armas - Bastones de Escarcha": {
        "Bastón de Escarcha (Una mano)": "MAIN_FROSTSTAFF",
        "Gran Bastón de Escarcha": "2H_FROSTSTAFF",
        "Bastón Glacial": "2H_GLACIALSTAFF",
        "Bastón de Congelación (Guardián)": "MAIN_FROSTSTAFF_KEEPER",
        "Bastón de Carámbano (Infernal)": "2H_ICEGAUNTLETS_HELL",
        "Prisma de Escarcha (No-Muerto)": "2H_ICECRYSTAL_UNDEAD",
        "Aullido Invernal (Avalon)": "MAIN_FROSTSTAFF_AVALON",
        "Bastón de Escarcha de Cristal": "2H_FROSTSTAFF_CRYSTAL"
    },

    # --- BLOQUE DE BASTONES MALDITOS (Brujo) ---
    "Armas - Bastones Malditos": {
        "Bastón Maldito (Una mano)": "MAIN_CURSEDSTAFF",
        "Gran Bastón Maldito": "2H_CURSEDSTAFF",
        "Bastón de Siniestro": "2H_DEMONICSTAFF",
        "Bastón de Vida Maldita (Morgana)": "MAIN_CURSEDSTAFF_MORGANA",
        "Bastón de Sangre (Infernal)": "2H_SKULL_HELL",
        "Bastón de Plaga (No-Muerto)": "2H_CURSEDSTAFF_UNDEAD",
        "Cosecha Sombría (Avalon)": "2H_CURSEDSTAFF_AVALON",
        "Bastón Maldito de Cristal": "MAIN_CURSEDSTAFF_CRYSTAL"
    },

    # --- BLOQUE DE OFF-HANDS (Placas / Metal) ---
    "Off-Hands - Escudos": {
        "Escudo (Normal)": "OFF_SHIELD",
        "Sarcófago (No-Muerto)": "OFF_TOWERSHIELD_UNDEAD",
        "Escudo de Villano (Infernal)": "OFF_SHIELD_HELL",
        "Quebrantador (Morgana)": "OFF_SPIKEDSHIELD_MORGANA",
        "Égida Astral (Avalon)": "OFF_SHIELD_AVALON"
    },

    # --- BLOQUE DE OFF-HANDS (Cuero / Madera) ---
    "Off-Hands - Antorchas": {
        "Antorcha (Normal)": "OFF_TORCH",
        "Invocanieblas (Guardián)": "OFF_HORN_KEEPER",
        "Bastón de Mofas (Infernal)": "OFF_JESTERCANE_HELL",
        "Vela de la Cripta (No-Muerto)": "OFF_LAMP_UNDEAD",
        "Incensario Celestial (Avalon)": "OFF_CENSER_AVALON"
    },

    # --- BLOQUE DE OFF-HANDS (Tela / Magia) ---
    "Off-Hands - Libros (Tomos)": {
        "Tomo de Hechizos (Normal)": "OFF_BOOK",
        "Ojo de los Secretos (Morgana)": "OFF_ORB_MORGANA",
        "Muisak (Infernal)": "OFF_DEMONSKULL_HELL",
        "Raíz de la Naturaleza (Guardián)": "OFF_TOTEM_KEEPER",
        "Talismán de Avalon (Avalon)": "OFF_TALISMAN_AVALON"
    },

    # --- BLOQUE DE PLACAS (CASCOS) ---
    "Armaduras - Cascos de Placas": {
        "Casco de Soldado": "HEAD_PLATE_SET1",
        "Casco de Caballero": "HEAD_PLATE_SET2",
        "Casco de Guardián": "HEAD_PLATE_SET3",
        "Casco de Guardatumbas (Artefacto)": "HEAD_PLATE_UNDEAD",
        "Casco Demoníaco (Artefacto)": "HEAD_PLATE_HELL",
        "Casco de Juez (Artefacto)": "HEAD_PLATE_MORGANA",
        "Casco de Valor (Avalon)": "HEAD_PLATE_AVALON",
        "Casco de Tejeocaso (Fey)": "HEAD_PLATE_FEY"
    },

    # --- BLOQUE DE PLACAS (PECHOS) ---
    "Armaduras - Pechos de Placas": {
        "Armadura de Soldado": "ARMOR_PLATE_SET1",
        "Armadura de Caballero": "ARMOR_PLATE_SET2",
        "Armadura de Guardián": "ARMOR_PLATE_SET3",
        "Armadura de Guardatumbas (Artefacto)": "ARMOR_PLATE_UNDEAD",
        "Armadura Demoníaca (Artefacto)": "ARMOR_PLATE_HELL",
        "Armadura de Juez (Artefacto)": "ARMOR_PLATE_MORGANA",
        "Armadura de Valor (Avalon)": "ARMOR_PLATE_AVALON",
        "Armadura de Tejeocaso (Fey)": "ARMOR_PLATE_FEY"
    },

    # --- BLOQUE DE PLACAS (BOTAS) ---
    "Armaduras - Botas de Placas": {
        "Botas de Soldado": "SHOES_PLATE_SET1",
        "Botas de Caballero": "SHOES_PLATE_SET2",
        "Botas de Guardián": "SHOES_PLATE_SET3",
        "Botas de Guardatumbas (Artefacto)": "SHOES_PLATE_UNDEAD",
        "Botas Demoníacas (Artefacto)": "SHOES_PLATE_HELL",
        "Botas de Juez (Artefacto)": "SHOES_PLATE_MORGANA",
        "Botas de Valor (Avalon)": "SHOES_PLATE_AVALON",
        "Botas de Tejeocaso (Fey)": "SHOES_PLATE_FEY"
    },

    # --- BLOQUE DE CUERO (CAPUCHAS) ---
    "Armaduras - Capuchas de Cuero": {
        "Capucha de Mercenario": "HEAD_LEATHER_SET1",
        "Capucha de Cazador": "HEAD_LEATHER_SET2",
        "Capucha de Asesino": "HEAD_LEATHER_SET3",
        "Capucha de Acechador (Morgana)": "HEAD_LEATHER_MORGANA",
        "Capucha de Hellion (Infernal)": "HEAD_LEATHER_HELL",
        "Capucha de Espectro (No-Muerto)": "HEAD_LEATHER_UNDEAD",
        "Capucha de Caminante de la Niebla (Avalon)": "HEAD_LEATHER_AVALON",
        "Capucha de Tejeocaso (Fey)": "HEAD_LEATHER_FEY"
    },

    # --- BLOQUE DE CUERO (CHAQUETAS) ---
    "Armaduras - Chaquetas de Cuero": {
        "Chaqueta de Mercenario": "ARMOR_LEATHER_SET1",
        "Chaqueta de Cazador": "ARMOR_LEATHER_SET2",
        "Chaqueta de Asesino": "ARMOR_LEATHER_SET3",
        "Chaqueta de Acechador (Morgana)": "ARMOR_LEATHER_MORGANA",
        "Chaqueta de Hellion (Infernal)": "ARMOR_LEATHER_HELL",
        "Chaqueta de Espectro (No-Muerto)": "ARMOR_LEATHER_UNDEAD",
        "Chaqueta de Caminante de la Niebla (Avalon)": "ARMOR_LEATHER_AVALON",
        "Chaqueta de Tejeocaso (Fey)": "ARMOR_LEATHER_FEY"
    },

    # --- BLOQUE DE CUERO (ZAPATOS) ---
    "Armaduras - Zapatos de Cuero": {
        "Zapatos de Mercenario": "SHOES_LEATHER_SET1",
        "Zapatos de Cazador": "SHOES_LEATHER_SET2",
        "Zapatos de Asesino": "SHOES_LEATHER_SET3",
        "Zapatos de Acechador (Morgana)": "SHOES_LEATHER_MORGANA",
        "Zapatos de Hellion (Infernal)": "SHOES_LEATHER_HELL",
        "Zapatos de Espectro (No-Muerto)": "SHOES_LEATHER_UNDEAD",
        "Zapatos de Caminante de la Niebla (Avalon)": "SHOES_LEATHER_AVALON",
        "Zapatos de Tejeocaso (Fey)": "SHOES_LEATHER_FEY"
    },

    # --- BLOQUE DE TELA (CAPUCHAS/CABEZAS) ---
    "Armaduras - Capuchas de Tela": {
        "Capucha de Erudito": "HEAD_CLOTH_SET1",
        "Capucha de Clérigo": "HEAD_CLOTH_SET2",
        "Capucha de Mago": "HEAD_CLOTH_SET3",
        "Capucha de Druida (Guardián)": "HEAD_CLOTH_KEEPER",
        "Capucha Demoníaca (Infernal)": "HEAD_CLOTH_HELL",
        "Capucha de Sectario (No-Muerto)": "HEAD_CLOTH_UNDEAD",
        "Capucha de Pureza (Avalon)": "HEAD_CLOTH_AVALON",
        "Capucha de Escamasféericas (Fey)": "HEAD_CLOTH_FEY"
    },

    # --- BLOQUE DE TELA (TÚNICAS/PECHOS) ---
    "Armaduras - Túnicas de Tela": {
        "Túnica de Erudito": "ARMOR_CLOTH_SET1",
        "Túnica de Clérigo": "ARMOR_CLOTH_SET2",
        "Túnica de Mago": "ARMOR_CLOTH_SET3",
        "Túnica de Druida (Guardián)": "ARMOR_CLOTH_KEEPER",
        "Túnica Demoníaca (Infernal)": "ARMOR_CLOTH_HELL",
        "Túnica de Sectario (No-Muerto)": "ARMOR_CLOTH_UNDEAD",
        "Túnica de Pureza (Avalon)": "ARMOR_CLOTH_AVALON",
        "Túnica de Escamasféericas (Fey)": "ARMOR_CLOTH_FEY"
    },

    # --- BLOQUE DE TELA (SANDALIAS/ZAPATOS) ---
    "Armaduras - Sandalias de Tela": {
        "Sandalias de Erudito": "SHOES_CLOTH_SET1",
        "Sandalias de Clérigo": "SHOES_CLOTH_SET2",
        "Sandalias de Mago": "SHOES_CLOTH_SET3",
        "Sandalias de Druida (Guardián)": "SHOES_CLOTH_KEEPER",
        "Sandalias Demoníacas (Infernal)": "SHOES_CLOTH_HELL",
        "Sandalias de Sectario (No-Muerto)": "SHOES_CLOTH_UNDEAD",
        "Sandalias de Pureza (Avalon)": "SHOES_CLOTH_AVALON",
        "Sandalias de Escamasféericas (Fey)": "SHOES_CLOTH_FEY"
    },

}

diccionario_calidades = {
    "Normal": 1, "Bueno": 2, "Notable": 3, 
    "Sobresaliente": 4, "Obra Maestra": 5
}

# 2. Función de API actualizada para aceptar Calidad
def obtener_precios_api(item_id, calidad=None):
    ciudades = "Caerleon,Thetford,Fort Sterling,Lymhurst,Bridgewatch,Martlock,Brecilien"
    url = f"https://www.albion-online-data.com/api/v2/stats/prices/{item_id}?locations={ciudades}"
    
    # Si el ítem tiene calidad, le pedimos a la API solo esa calidad específica
    if calidad:
        url += f"&qualities={calidad}"
        
    try:
        respuesta = requests.get(url)
        if respuesta.status_code == 200:
            return respuesta.json()
        return None
    except:
        return None

# --- BARRA LATERAL (SIDEBAR) ---
st.sidebar.header("⚙️ Creador de Ítems")

# Selectores en cascada (El segundo cambia según lo que elijas en el primero)
categoria_elegida = st.sidebar.selectbox("Categoría:", list(catalogo.keys()))
item_elegido = st.sidebar.selectbox("Ítem:", list(catalogo[categoria_elegida].keys()))
codigo_base = catalogo[categoria_elegida][item_elegido]

tier = st.sidebar.slider("Tier (Nivel):", min_value=4, max_value=8, value=5)
encantamiento = st.sidebar.selectbox("Encantamiento (.X):", [0, 1, 2, 3, 4])

# --- LÓGICA INTELIGENTE DE CALIDAD ---
calidad_api = None
nombre_calidad = "N/A"
# NUEVO: Agregamos "Off-Hands" para que también tengan calidad
if "Armas" in categoria_elegida or "Armaduras" in categoria_elegida or "Off-Hands" in categoria_elegida:
    nombre_calidad = st.sidebar.selectbox("Calidad del ítem:", list(diccionario_calidades.keys()))
    calidad_api = diccionario_calidades[nombre_calidad]

# --- CONSTRUCCIÓN DEL ID ---
if categoria_elegida == "Recursos Básicos":
    # Los recursos usan _LEVEL
    item_id_real = f"T{tier}_{codigo_base}" if encantamiento == 0 else f"T{tier}_{codigo_base}_LEVEL{encantamiento}@{encantamiento}"
else:
    # Las armas y consumibles NO usan _LEVEL
    item_id_real = f"T{tier}_{codigo_base}" if encantamiento == 0 else f"T{tier}_{codigo_base}@{encantamiento}"

st.sidebar.info(f"🔍 Código API generado: {item_id_real}")

st.sidebar.divider()
st.sidebar.write("Configuración de Rentabilidad:")
cantidad_items = st.sidebar.number_input("Cantidad a vender:", min_value=1, value=1, step=1)
tipo_venta = st.sidebar.radio("Método de Venta:", ["Orden de Venta (Paciencia)", "Venta Directa (Rápida)"])
tiene_premium = st.sidebar.checkbox("¿Tienes Premium Activo?", value=True)
costo_materiales = st.sidebar.number_input("Costo Total de Materiales (Plata):", min_value=0, value=0, step=100)

# --- PANEL PRINCIPAL ---
st.title("🍌 Bananita Market - Chanchito Xupalo 🍆")

if 'mis_datos' not in st.session_state:
    st.session_state.mis_datos = None

# Pasamos también la calidad a la función de la API
if st.button("Descargar Precios Actuales", type="primary"):
    with st.spinner(f"Consultando el mercado para {item_id_real}..."):
        st.session_state.mis_datos = obtener_precios_api(item_id_real, calidad_api)
        
    if not st.session_state.mis_datos:
        st.error("No se pudieron obtener los datos. La API podría estar caída o el ítem no tiene registros recientes.")

if st.session_state.mis_datos:
    st.success("¡Datos obtenidos correctamente!")
    
    df = pd.DataFrame(st.session_state.mis_datos)
    
    if tipo_venta == "Orden de Venta (Paciencia)":
        df['Precio Unitario'] = df['sell_price_min']
        tasa_impuesto = 0.065 if tiene_premium else 0.105 
    else:
        df['Precio Unitario'] = df['buy_price_max']
        tasa_impuesto = 0.04 if tiene_premium else 0.08
        
    df = df[df['Precio Unitario'] > 0]
    
    if df.empty:
        st.warning("No hay órdenes de mercado registradas para este ítem actualmente.")
    else:
        df['Encantamiento'] = encantamiento
        df['Calidad'] = nombre_calidad # Agregamos la columna de calidad visualmente
        
        df['Ingreso Bruto'] = df['Precio Unitario'] * cantidad_items
        df['Impuestos'] = df['Ingreso Bruto'] * tasa_impuesto
        df['Ganancia Neta'] = df['Ingreso Bruto'] - df['Impuestos'] - costo_materiales
        
        df['Impuestos'] = df['Impuestos'].astype(int)
        df['Ganancia Neta'] = df['Ganancia Neta'].astype(int)
        df['Ingreso Bruto'] = df['Ingreso Bruto'].astype(int)

        df = df.rename(columns={
            'city': 'Ciudad', 
            'sell_price_min_date': 'Última Actualización'
        })
        
        st.divider()
        st.subheader("📊 Tabla de Precios y Rentabilidad")
        
        mostrar_fecha = st.checkbox("Mostrar fecha de última actualización")
        
        # Agregamos 'Calidad' a las columnas que se muestran
        if mostrar_fecha:
            columnas_finales = ['Ciudad', 'Encantamiento', 'Calidad', 'Precio Unitario', 'Ingreso Bruto', 'Impuestos', 'Ganancia Neta', 'Última Actualización']
        else:
            columnas_finales = ['Ciudad', 'Encantamiento', 'Calidad', 'Precio Unitario', 'Ingreso Bruto', 'Impuestos', 'Ganancia Neta']
            
        def pintar_ganancia(valor):
            color = '#2ecc71' if valor > 0 else '#e74c3c'
            return f'color: {color}; font-weight: bold;'
        
        tabla_estilizada = df[columnas_finales].style.map(pintar_ganancia, subset=['Ganancia Neta'])
        
        st.dataframe(tabla_estilizada, use_container_width=True, hide_index=True)

# --- NUEVO MÓDULO: RECOMENDADOR DE INVERSIONES ---
st.divider()
st.header("📈 Recomendador de Inversiones")

tab1, tab2, tab3 = st.tabs(["🔨 Refinación", "🏝️ Gestión de Islas", "⚖️ Mercado Negro"])

with tab1:
    st.subheader("🚀 Escáner de Arbitraje Inteligente")
    st.markdown("Usa la API para buscar la mejor ruta, o ingresa los precios manualmente si el mercado no está actualizado.")

    # --- PRESUPUESTO EXCLUSIVO DE ESTA PESTAÑA ---
    capital = st.number_input("💰 Presupuesto de Inversión (Plata)", min_value=0, value=1000000, step=100000, key="capital_tab1")
    st.divider()

    # 1. Configuración de la búsqueda
    c_mat, c_tier, c_enc = st.columns(3)
    with c_mat:
        material = st.selectbox("Material a analizar", ["Mineral (Lingotes)", "Madera (Tablas)", "Fibra (Tela)", "Piel (Cuero)", "Piedra (Bloques)"])
    with c_tier:
        tier_ref = st.selectbox("Tier Crudo", ["T4", "T5", "T6", "T7", "T8"], key="smart_tier")
    with c_enc:
        enc_ref = st.selectbox("Encantamiento", [".0", ".1", ".2", ".3", ".4"], key="smart_enc")

    # Mapeo estático
    map_ids = {
        "Mineral (Lingotes)": {"raw": "ORE", "ref": "METALBAR", "bono": "Thetford", "compra": "Fort Sterling", "venta": "Bridgewatch"},
        "Madera (Tablas)": {"raw": "WOOD", "ref": "PLANKS", "bono": "Fort Sterling", "compra": "Lymhurst", "venta": "Lymhurst"},
        "Fibra (Tela)": {"raw": "FIBER", "ref": "CLOTH", "bono": "Lymhurst", "compra": "Thetford", "venta": "Fort Sterling"},
        "Piel (Cuero)": {"raw": "HIDE", "ref": "LEATHER", "bono": "Martlock", "compra": "Bridgewatch", "venta": "Thetford"},
        "Piedra (Bloques)": {"raw": "ROCK", "ref": "STONEBLOCK", "bono": "Bridgewatch", "compra": "Martlock", "venta": "Caerleon"}
    }
    
    # --- CONSTRUCCIÓN INTELIGENTE DE IDs (CORRECCIÓN DEFINITIVA) ---
    base_raw = map_ids[material]["raw"]
    base_ref = map_ids[material]["ref"]
    tier_num = int(tier_ref[1])
    
    if enc_ref == ".0":
        id_crudo = f"{tier_ref}_{base_raw}"
        id_final = f"{tier_ref}_{base_ref}"
        id_previo = f"T{tier_num-1}_{base_ref}"
    else:
        num_enc = enc_ref.replace(".", "") # "1", "2", "3", "4"
        
        # En la API, TANTO crudos como refinados usan _LEVEL y @ para los encantamientos
        id_crudo = f"{tier_ref}_{base_raw}_LEVEL{num_enc}@{num_enc}"
        id_final = f"{tier_ref}_{base_ref}_LEVEL{num_enc}@{num_enc}"
        
        # Regla de Albion: Refinar T5.1 o superior exige el material anterior también encantado (Ej: T4.1)
        # La única excepción es refinar T4, que siempre usa T3 plano.
        if tier_num == 4:
            id_previo = f"T3_{base_ref}" 
        else:
            id_previo = f"T{tier_num-1}_{base_ref}_LEVEL{num_enc}@{num_enc}"

    # 2. Inicializar variables en Memoria
    if "ruta_compra" not in st.session_state: st.session_state.ruta_compra = map_ids[material]["compra"]
    if "ruta_refina" not in st.session_state: st.session_state.ruta_refina = map_ids[material]["bono"]
    if "ruta_venta" not in st.session_state: st.session_state.ruta_venta = map_ids[material]["venta"]
    if "p_crudo" not in st.session_state: st.session_state.p_crudo = 0
    if "p_previo" not in st.session_state: st.session_state.p_previo = 0
    if "p_final" not in st.session_state: st.session_state.p_final = 0

    # 3. BOTÓN DE LA API
    if st.button("📡 Buscar Precios Automáticos (API)", use_container_width=True):
        with st.spinner("Escaneando las 6 ciudades..."):
            ciudades_royal = ["Thetford", "Fort Sterling", "Lymhurst", "Bridgewatch", "Martlock", "Caerleon"]
            data = consultar_api_albion([id_crudo, id_previo, id_final], ciudades_royal)

            if data:
                df_api = pd.DataFrame(data)
                df_compras = df_api[df_api['sell_price_min'] > 0]
                df_ventas = df_api[df_api['buy_price_max'] > 0]

                try:
                    best_raw = df_compras[df_compras['item_id'] == id_crudo].sort_values('sell_price_min').iloc[0]
                    best_prev = df_compras[df_compras['item_id'] == id_previo].sort_values('sell_price_min').iloc[0]
                    best_sell = df_ventas[df_ventas['item_id'] == id_final].sort_values('buy_price_max', ascending=False).iloc[0]

                    st.session_state.ruta_compra = best_raw['city']
                    st.session_state.ruta_venta = best_sell['city']
                    st.session_state.p_crudo = int(best_raw['sell_price_min'])
                    st.session_state.p_previo = int(best_prev['sell_price_min'])
                    st.session_state.p_final = int(best_sell['buy_price_max'])
                    
                    st.success("✅ ¡Datos actualizados desde la API!")
                except IndexError:
                    st.warning("⚠️ Faltan datos en la API para este ítem. Ingresa los precios manualmente abajo.")
            else:
                st.error("❌ Error de conexión con Albion Data Project. Usa el modo manual.")

    # 4. CAJAS MANUALES Y LOGÍSTICA
    st.divider()
    st.markdown("### 📍 Ruta de Logística y Precios")
    
    # Lógica de visualización dinámica
    mostrar_origen = st.session_state.ruta_compra if st.session_state.p_crudo > 0 else "--- (Sin datos)"
    mostrar_venta = st.session_state.ruta_venta if st.session_state.p_final > 0 else "--- (Sin datos)"
    
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        st.info(f"**Origen:** {mostrar_origen}")
        precio_crudo = st.number_input("Precio Crudo", value=st.session_state.p_crudo, step=10)
        precio_previo = st.number_input("Precio Tier Anterior", value=st.session_state.p_previo, step=10)
    with col_p2:
        # La ciudad de refinación siempre se muestra porque el bono es una regla fija del juego
        st.warning(f"**Refinación (Bono):** {map_ids[material]['bono']}")
        tiene_premium = st.checkbox("Uso Foco (36.7% RRR)", value=True)
        tasa_tienda = st.number_input("Tasa Tienda (Fee)", value=450)
    with col_p3:
        st.success(f"**Venta:** {mostrar_venta}")
        precio_final = st.number_input("Precio de Venta Final", value=st.session_state.p_final, step=10)
        costo_tp = st.number_input("Costo TP (por item)", value=0)

    # 5. CÁLCULO Y RESULTADOS AUTOMÁTICOS
    if precio_crudo > 0 and precio_final > 0:
        rrr = 36.7 if tiene_premium else 15.2
        ratio = {"T4": 2, "T5": 3, "T6": 4, "T7": 5, "T8": 5}[tier_ref]
        
        costo_unidad = (precio_crudo * ratio) + precio_previo
        cant_recetas = capital // costo_unidad if costo_unidad > 0 else 0
        
        if cant_recetas > 0:
            inv_total = cant_recetas * costo_unidad
            total_creado = cant_recetas * (1 + (rrr/100))
            
            venta_directa = (total_creado * precio_final) * 0.96 
            venta_orden = (total_creado * precio_final) * 0.935 
            
            ganancia_directa = venta_directa - inv_total - (cant_recetas * (tasa_tienda/100)) - (cant_recetas * costo_tp)
            ganancia_orden = venta_orden - inv_total - (cant_recetas * (tasa_tienda/100)) - (cant_recetas * costo_tp)

            # Resultados visuales
            st.markdown("#### 📦 Resultados de la Producción:")
            c1, c2, c3 = st.columns(3)
            c1.metric(f"Comprar Crudo", f"{int(cant_recetas * ratio):,}")
            c2.metric(f"Comprar Tier Anterior", f"{int(cant_recetas):,}")
            extra_por_rrr = total_creado - cant_recetas
            c3.metric(f"Refinados Finales", f"{int(total_creado):,}", delta=f"+{int(extra_por_rrr):,} por Devolución")

            st.divider()
            st.subheader("💰 Análisis de Rentabilidad Neta")
            
            costos_operativos = (cant_recetas * (tasa_tienda/100)) + (cant_recetas * costo_tp)
            inversion_total_real = inv_total + costos_operativos
            
            col_fin1, col_fin2 = st.columns(2)
            with col_fin1:
                st.write("**Opción: Orden de Venta (Paciencia)**")
                porcentaje_orden = (ganancia_orden / inversion_total_real) * 100 if inversion_total_real > 0 else 0
                st.metric("Ganancia Pura", f"{int(ganancia_orden):,} Plata", delta=f"{porcentaje_orden:.1f}% Retorno")
            with col_fin2:
                st.write("**Opción: Venta Directa (Rápido)**")
                porcentaje_directa = (ganancia_directa / inversion_total_real) * 100 if inversion_total_real > 0 else 0
                st.metric("Ganancia Pura", f"{int(ganancia_directa):,} Plata", delta=f"{porcentaje_directa:.1f}% Retorno")

            st.write(f"⚠️ **Inversión total:** {int(inversion_total_real):,} Plata")

            if ganancia_directa < 0 and ganancia_orden < 0:
                st.error("📉 Esta operación NO es rentable con los precios actuales.")

            # --- RADAR DE TENDENCIAS ---
            st.divider()
            st.subheader("📊 Radar de Tendencias (Timing del Mercado)")
            
            ciudad_compra = st.session_state.ruta_compra
            ciudad_venta = st.session_state.ruta_venta
            
            grafico_ver = st.radio("Analizar historial de:", 
                                  [f"Crudo en {ciudad_compra}", f"Refinado en {ciudad_venta}"],
                                  horizontal=True)
            
            with st.spinner("Dibujando historial y volumen..."):
                if "Crudo" in grafico_ver:
                    df_hist = consultar_historial(id_crudo, ciudad_compra)
                    color_linea = "#e74c3c"
                else:
                    df_hist = consultar_historial(id_final, ciudad_venta)
                    color_linea = "#2ecc71"
                    
                if df_hist is not None and not df_hist.empty:
                    st.line_chart(df_hist[['Precio Promedio']], color=color_linea, height=200)
                    if 'Cantidad Vendida (Volumen)' in df_hist.columns:
                        st.bar_chart(df_hist[['Cantidad Vendida (Volumen)']], color="#f39c12", height=150)
                else:
                    st.info("No hay datos históricos suficientes para mostrar el gráfico.")
        else:
            st.error("❌ Tu capital no alcanza para fabricar ni una sola pieza.")


with tab2:
    st.subheader("🏝️ Imperio de Islas y Gestión de Trabajadores")
    st.markdown("Configura tus islas para renta o maximiza el beneficio de tus trabajadores de alto nivel.")

    # --- SECCIÓN 1: GESTOR DE ALQUILERES ---
    st.markdown("### 🏘️ Administración de Rentas")
    col_rent1, col_rent2 = st.columns(2)
    with col_rent1:
        islas_propias = st.number_input("Total de Islas para renta", min_value=0, value=3)
        nivel_isla = st.selectbox("Nivel de cada Isla", ["Nivel 4 (2 Parcelas)", "Nivel 5 (3 Parcelas)", "Nivel 6 (5 Parcelas)"], index=2)
    with col_rent2:
        precio_parcela = st.number_input("Precio diario por parcela (Plata)", value=35000)
        tasa_ocupacion = st.slider("Ocupación Real %", 0, 100, 100)

    # Cálculo de renta
    num_parcelas_map = {"Nivel 4 (2 Parcelas)": 2, "Nivel 5 (3 Parcelas)": 3, "Nivel 6 (5 Parcelas)": 5}
    renta_mensual = (islas_propias * num_parcelas_map[nivel_isla] * (tasa_ocupacion/100)) * precio_parcela * 30
    st.metric("Ingreso Mensual por Rentas", f"{int(renta_mensual):,} Plata", help="Basado en 30 días de ocupación.")

    # --- SECCIÓN 2: TRABAJADORES (LABORERS) PROFESIONAL ---
    st.divider()
    st.markdown("### 👷 Calculadora de Trabajadores y Diarios")
    
    # Lista completa de trabajadores de Albion
    lista_trabajadores = [
        "Leñador (Madera)", "Cantero (Piedra)", "Prospector (Mineral)", 
        "Cosechador (Fibra)", "Montería (Piel)", "Mercenario", 
        "Herrero (Equipo Metal)", "Flechero (Arcos/Cuero)", 
        "Imbuido (Varas/Tela)", "Hojalatero (Herramientas/Capas)"
    ]

    c_t1, c_t2, c_t3 = st.columns(3)
    with c_t1:
        tipo_t = st.selectbox("Especialidad del Trabajador", lista_trabajadores)
        tier_t = st.selectbox("Tier del Trabajador", ["T2", "T3", "T4", "T5", "T6", "T7", "T8"], index=4) # T6 por defecto
    with c_t2:
        num_t = st.number_input("Cantidad de Trabajadores", value=15, step=3)
        retorno_pct = st.number_input("Retorno de Felicidad %", value=150, help="El porcentaje que te marca el trabajador al entregarle el diario (normalmente entre 100% y 150%).")
    with c_t3:
        precio_lleno = st.number_input("Precio Diario Lleno", value=25000)
        precio_vacio = st.number_input("Precio Diario Vacío", value=5000)

    # Input del valor promedio que devuelve
    valor_loot = st.number_input(f"Valor promedio del Loot devuelto ({tier_t})", value=45000, help="Suma el valor promedio de los recursos que trae el trabajador según su Tier.")

    # Matemáticas de Trabajadores
    # Costo neto = (Diario Lleno - Diario Vacio) ya que recuperas el frasco
    costo_diario_neto = (precio_lleno - precio_vacio) * num_t
    
    # El retorno afecta directamente a la cantidad de loot
    ingreso_bruto_t = (valor_loot * (retorno_pct / 100)) * num_t
    ganancia_neta_t = ingreso_bruto_t - costo_diario_neto

    st.markdown(f"#### 📊 Análisis de Rentabilidad: {tipo_t} {tier_t}")
    t_col1, t_col2, t_col3 = st.columns(3)
    
    t_col1.metric("Costo Neto de Diarios", f"{int(costo_diario_neto):,} Plata")
    t_col2.metric("Ganancia Diaria Neta", f"{int(ganancia_neta_t):,} Plata")
    
    # Proyección a largo plazo (Muy importante para tu estrategia de islas)
    ganancia_mensual_t = ganancia_neta_t * 30
    t_col3.metric("Ganancia Mensual Est.", f"{int(ganancia_mensual_t):,} Plata", delta=f"{retorno_pct}% Yield")

    if ganancia_neta_t <= 0:
        st.error("⚠️ Los diarios están demasiado caros o el loot es muy bajo. Estás perdiendo plata con esta configuración.")
    else:
        st.success(f"Configuración rentable. Cada trabajador te deja **{int(ganancia_neta_t / num_t):,}** de plata pura al día.")

    # --- SECCIÓN 2: AGRICULTURA CON BONOS REGIONALES ---
    st.divider()
    st.markdown("### 🧑‍🌾 Agricultura Eficiente (Bonos Regionales)")
    
    # Definición de bonos por ciudad (Datos oficiales de Albion)
    bonos_ciudad = {
        "Martlock": "Papas (T6)",
        "Bridgewatch": "Maíz (T7)",
        "Lymhurst": "Zanahorias (T3) / Calabazas (T8)",
        "Fort Sterling": "Nabos (T4)",
        "Thetford": "Coles (T5)",
        "Caerleon": "Ninguno (Bono en comida/pociones)"
    }

    c_city, c_cult = st.columns(2)
    with c_city:
        ciudad_isla = st.selectbox("Ciudad de la Isla", ["Martlock", "Bridgewatch", "Lymhurst", "Fort Sterling", "Thetford", "Caerleon"])
    with c_cult:
        cultivo = st.selectbox("Cultivo a sembrar", ["Zanahorias (T3)", "Nabos (T4)", "Coles (T5)", "Papas (T6)", "Maíz (T7)", "Calabazas (T8)"])

    # Verificar si hay bono
    tiene_bono_ciudad = False
    if cultivo.split(" (")[0] in bonos_ciudad[ciudad_isla]:
        tiene_bono_ciudad = True
        st.success(f"✨ **Bono detectado:** {ciudad_isla} tiene bono para {cultivo}. Rendimiento aumentado en +10%.")
    else:
        st.info(f"💡 Tip: {cultivo} tiene bono en **{ [k for k, v in bonos_ciudad.items() if cultivo.split(' (')[0] in v][0] if any(cultivo.split(' (')[0] in v for v in bonos_ciudad.values()) else 'ninguna ciudad' }**.")

    # Cálculos de Granja
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        n_parcelas = st.number_input("Cantidad de Parcelas", value=5)
        costo_s = st.number_input("Costo Semilla", value=2500)
    with col_g2:
        venta_c = st.number_input("Precio Venta Cultivo", value=400)
        retorno_s = st.slider("Retorno Semillas %", 0, 150, 91)

    # El bono de ciudad suele dar un ~10% más de producto final
    multiplicador_bono = 1.10 if tiene_bono_ciudad else 1.0
    total_items = (n_parcelas * 9 * 9) * multiplicador_bono # 9 espacios * ~9 items por espacio
    
    inversion = (n_parcelas * 9) * costo_s
    recuperacion_s = (n_parcelas * 9 * (retorno_s/100)) * costo_s
    venta_total = (total_items * venta_c) * 0.935 # -6.5% impuesto
    ganancia_granja = venta_total - (inversion - recuperacion_s)

    st.metric("Ganancia Diaria Estimada", f"{int(ganancia_granja):,} Plata", delta=f"{'+10% Bono' if tiene_bono_ciudad else 'Sin bono'}")

    # --- SECCIÓN 3: GANADERÍA CON BONOS DE CIUDAD ---
    st.divider()
    st.markdown("### 🐄 Ganadería y Crianza con Bonos de Ciudad")
    
    # Mapeo oficial de bonos ganaderos por ciudad
    bonos_ganaderia = {
        "Lymhurst": ["Pollo", "Gallinas (Huevos)"],
        "Bridgewatch": ["Cabrito", "Cabras (Leche)"],
        "Fort Sterling": ["Oveja", "Ovejas (Lana)"],
        "Thetford": ["Cerdito", "Cerdos (Carne)"],
        "Martlock": ["Ternero", "Vacas (Leche)"],
        "Caerleon": ["Ninguno"]
    }

    col_g_city, col_g_mode = st.columns(2)
    with col_g_city:
        ciudad_ganado = st.selectbox("Ciudad de la Granja", ["Lymhurst", "Bridgewatch", "Fort Sterling", "Thetford", "Martlock", "Caerleon"])
    with col_g_mode:
        modo_ganado = st.radio("Estrategia:", ["Producción de Recursos", "Crianza Final (Venta)"], horizontal=True)

    # Identificar bono
    if modo_ganado == "Producción de Recursos":
        animal_prod = st.selectbox("Animal Productor", ["Gallinas (Huevos)", "Cabras (Leche)", "Ovejas (Lana)", "Cerdos (Carne)", "Vacas (Leche)"])
        tiene_bono_g = any(animal_prod in b for b in bonos_ganaderia[ciudad_ganado])
        
        if tiene_bono_g:
            st.success(f"✨ **Bono detectado:** {ciudad_ganado} tiene un bono del +10% para {animal_prod}.")
        else:
            ciudad_correcta = [k for k, v in bonos_ganaderia.items() if any(animal_prod in s for s in v)][0]
            st.warning(f"💡 Tip: Para {animal_prod}, obtendrías un 10% más de recursos si estuvieras en **{ciudad_correcta}**.")

        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            cant_a = st.number_input("Cantidad de animales", value=9)
            unidades_base = st.number_input("Unidades/día por animal", value=10)
        with col_p2:
            precio_r = st.number_input("Precio venta recurso", value=450)
            costo_c = st.number_input("Costo comida/día/animal", value=2200)
        with col_p3:
            usa_foco_p = st.checkbox("Usar Foco", value=True)
        
        # Matemáticas con bono (10% extra de producto)
        mult_bono = 1.10 if tiene_bono_g else 1.0
        total_prod = (cant_a * unidades_base) * mult_bono
        ingreso_d = (total_prod * precio_r) * 0.935 # -6.5% impuesto
        costo_d = cant_a * costo_c
        ganancia_d = ingreso_d - costo_d

        st.metric("Ganancia Neta Diaria", f"{int(ganancia_d):,} Plata", delta=f"{int(ganancia_d * 30):,} mensual")

    else:
        # Crianza Final (Monturas/Carne)
        animal_cria = st.selectbox("Animal a criar", ["Pollo", "Cabrito", "Cerdito", "Ternero", "Potro (Caballo)", "Buey joven"])
        tiene_bono_c = any(animal_cria in b for b in bonos_ganaderia[ciudad_ganado])
        
        if tiene_bono_c:
            st.success(f"✨ **Bono detectado:** {ciudad_ganado} acelera el crecimiento de {animal_cria} (+10%).")
        
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            dias_c = st.number_input("Días de crecimiento", value=1, min_value=1)
            costo_b = st.number_input("Costo Cría/Bebé", value=12000)
        with col_c2:
            precio_a = st.number_input("Precio Adulto", value=28000)
            costo_com = st.number_input("Comida total diaria", value=2500)
        with col_c3:
            usa_foco_c = st.checkbox("Cuidar con Foco", value=True)
            prob_b = st.slider("Prob. nueva cría %", 0, 150, 95 if usa_foco_c else 45)

        # Matemáticas de crianza
        costo_total_comida = costo_com * dias_c
        # El bono de ciudad en crianza suele reducir el tiempo o aumentar la probabilidad base
        valor_retorno_bebe = costo_b * (prob_b / 100)
        ganancia_animal = (precio_a * 0.935 + valor_retorno_bebe) - (costo_b + costo_total_comida)
        
        st.metric("Ganancia por Animal", f"{int(ganancia_animal):,} Plata", delta=f"{int(ganancia_animal * 9):,} por parcela")


with tab3:
    st.subheader("⚖️ Radar Masivo con Filtro de Liquidez")
    st.markdown("Busca las mejores oportunidades filtrando por **Volumen Diario** para asegurar que tus ítems se vendan rápido.")

    import time 

    # 1. Filtros de Búsqueda
    col_bm1, col_bm2, col_bm3, col_bm4 = st.columns(4)
    with col_bm1:
        tier_bm = st.selectbox("Tier Objetivo", ["T4", "T5", "T6", "T7", "T8"], index=3, key="liq_tier")
    with col_bm2:
        enc_bm = st.selectbox("Encantamiento", [".0", ".1", ".2", ".3", ".4"], index=1, key="liq_enc")
    with col_bm3:
        calidad_bm = st.selectbox("Calidad", ["Normal (1)", "Bueno (2)", "Notable (3)", "Sobresaliente (4)", "Obra Maestra (5)"], key="liq_cal")
    with col_bm4:
        vol_min = st.number_input("Ventas diarias mínimas", value=5, step=1, help="Ignora ítems que se vendan menos de X veces al día.")

    capital_bm = st.number_input("Presupuesto Total (Plata)", value=5000000, step=500000, key="liq_cap")
    premium_bm = st.checkbox("Tengo Premium", value=True, key="liq_prem")

    if st.button("🏴‍☠️ Escanear con Filtro de Volumen", type="primary", use_container_width=True):
        calidad_num = int(calidad_bm.split("(")[1].replace(")", ""))
        
        # Mapeo de nombres e IDs
        nombres_map = {}
        for categoria, items in catalogo.items():
            if "Recursos" not in categoria: 
                for nombre_item, codigo_base in items.items():
                    enc_api = enc_bm.replace(".", "@") if enc_bm != ".0" else ""
                    id_completo = f"{tier_bm}_{codigo_base}{enc_api}"
                    nombres_map[id_completo] = f"{nombre_item} {tier_bm}{enc_bm}"

        ids_totales = list(nombres_map.keys())
        
        def dividir_en_lotes(lista, tamano=40):
            return [lista[i:i + tamano] for i in range(0, len(lista), tamano)]

        lotes = dividir_en_lotes(ids_totales)
        ciudades_todas = ["Thetford", "Fort Sterling", "Lymhurst", "Bridgewatch", "Martlock", "Caerleon", "Black Market"]
        
        resultados_radar = []
        impuesto_directa = 0.04 if premium_bm else 0.08
        impuesto_orden = 0.065 if premium_bm else 0.105

        barra_prog = st.progress(0)
        texto_estado = st.empty()
        
        # --- PASO 1: Descarga de Precios ---
        datos_completos = []
        for i, lote in enumerate(lotes):
            texto_estado.text(f"Escaneando precios... (Lote {i+1} de {len(lotes)})")
            data_lote = consultar_api_albion(lote, ciudades_todas)
            if data_lote: datos_completos.extend(data_lote)
            barra_prog.progress((i + 1) / (len(lotes) + 1)) # Guardamos espacio para el paso de volumen
            time.sleep(0.3) 

        if datos_completos:
            df_bm = pd.DataFrame(datos_completos)
            rentables_preliminares = []

            # Filtrado inicial por rentabilidad
            for item_id in ids_totales:
                df_item = df_bm[(df_bm['item_id'] == item_id) & (df_bm['quality'] == calidad_num)]
                if not df_item.empty:
                    df_origen = df_item[(df_item['city'] != 'Black Market') & (df_item['sell_price_min'] > 0)]
                    df_black = df_item[(df_item['city'] == 'Black Market')]

                    if not df_origen.empty and not df_black.empty:
                        mejor_compra = df_origen.sort_values('sell_price_min').iloc[0]
                        precio_compra = mejor_compra['sell_price_min']
                        pago_directo = df_black['buy_price_max'].max()

                        if pago_directo > 0:
                            ingreso_n = pago_directo * (1 - impuesto_directa)
                            ganancia_u = ingreso_n - precio_compra
                            if ganancia_u > 0:
                                rentables_preliminares.append({
                                    'id': item_id, 'compra': precio_compra, 'venta': pago_directo, 
                                    'city': mejor_compra['city'], 'ganancia': ganancia_u
                                })

            #--- PASO 2: Verificación de Volumen (Solo para los rentables) ---
            texto_estado.text("Verificando liquidez en el Mercado Negro...")
            final_oportunidades = []
            
            # Para no saturar, solo revisamos el volumen de los 15 más rentables
            rentables_preliminares = sorted(rentables_preliminares, key=lambda x: x['ganancia'], reverse=True)[:15]

            for op in rentables_preliminares:
                hist = consultar_historial(op['id'], "Black Market")
                if hist is not None and not hist.empty:
                    # 🛡️ ESCUDO ANTI-ERRORES: Verificamos que la columna realmente exista
                    if 'Cantidad Vendida (Volumen)' in hist.columns:
                        volumen_diario = hist['Cantidad Vendida (Volumen)'].tail(24).sum()
                    else:
                        volumen_diario = 0 # Si la API falla o no hay volumen, asumimos 0
                    
                    if volumen_diario >= vol_min:
                        cant_a_comprar = int(capital_bm // op['compra'])
                        # Ajustamos la cantidad sugerida para no saturar el mercado
                        cant_recomendada = min(cant_a_comprar, int(volumen_diario * 0.5)) 
                        
                        if cant_recomendada > 0:
                            ganancia_t = op['ganancia'] * cant_recomendada
                            final_oportunidades.append({
                                "Ítem": nombres_map[op['id']],
                                "Ventas/Día": int(volumen_diario),
                                "Tus Unidades": cant_recomendada,
                                "Compra en": op['city'],
                                "Precio Compra": op['compra'],
                                "Ganancia Total": ganancia_t,
                                "Retorno": (ganancia_t / (op['compra'] * cant_recomendada)) * 100
                            })
                time.sleep(0.2)
            barra_prog.progress(1.0)
            texto_estado.empty()

            if final_oportunidades:
                st.success(f"### 🏆 Oportunidades con Alta Liquidez (Mín. {vol_min} ventas/día)")
                df_res = pd.DataFrame(final_oportunidades).sort_values(by="Ganancia Total", ascending=False)
                
                # Formateo visual
                df_res['Precio Compra'] = df_res['Precio Compra'].apply(lambda x: f"{int(x):,}")
                df_res['Ganancia Total'] = df_res['Ganancia Total'].apply(lambda x: f"{int(x):,}")
                df_res['Retorno'] = df_res['Retorno'].apply(lambda x: f"{x:.1f}%")
                
                st.dataframe(df_res, use_container_width=True, hide_index=True)
                st.caption("💡 'Tus Unidades' está limitado al 50% del volumen diario para asegurar venta rápida.")
            else:
                st.warning("No hay ítems rentables que cumplan con el volumen mínimo de ventas.")