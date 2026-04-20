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
st.markdown("Estrategias para multiplicar tu plata usando capital inicial.")

capital = st.number_input("💰 ¿Cuál es tu presupuesto para invertir? (Plata)", min_value=100000, value=1000000, step=100000)

tab1, tab2, tab3 = st.tabs(["🔨 Refinación", "🏝️ Gestión de Islas", "⚖️ Mercado Negro"])

with tab1:
    st.subheader("🚀 Escáner de Arbitraje Inteligente")
    st.markdown("Usa la API para buscar la mejor ruta, o ingresa los precios manualmente si el mercado no está actualizado.")

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
    st.markdown(f"### 📍 Ruta de Logística y Precios")
    
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        st.info(f"**Origen:** {st.session_state.ruta_compra}")
        precio_crudo = st.number_input(f"Precio Crudo", value=st.session_state.p_crudo, step=10)
        precio_previo = st.number_input(f"Precio Tier Anterior", value=st.session_state.p_previo, step=10)
    with col_p2:
        st.warning(f"**Refinación:** {map_ids[material]['bono']}")
        tiene_premium = st.checkbox("Uso Foco (36.7% RRR)", value=True)
        tasa_tienda = st.number_input("Tasa Tienda (Fee)", value=450)
    with col_p3:
        st.success(f"**Venta:** {st.session_state.ruta_venta}")
        precio_final = st.number_input(f"Precio de Venta Final", value=st.session_state.p_final, step=10)
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
    st.subheader("Ingresos Pasivos: Trabajadores y Alquileres")
    st.write("Destina tu capital a estructurar una economía de casas y trabajadores.")
    st.markdown("""
    * **Trabajadores (Laborers):** Compra Diarios y entrégalos.
    * **Alquileres:** Ofrece tu isla a otros jugadores para cultivo.
    * **Riesgo:** Nulo (tras recuperar inversión).
    """)

with tab3:
    st.subheader("Alto Riesgo: Mercado Negro")
    st.write("Compra equipo barato y llévalo a Caerleon.")
    st.markdown("""
    * Compra T4.1 o T5 en ciudades reales.
    * Transporta por zona roja hacia **Caerleon**.
    * Vende al NPC del Mercado Negro por sobreprecio.
    * **Riesgo:** Alto (Gankers).
    """)