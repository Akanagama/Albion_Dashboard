import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Albion Econ", layout="wide")

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
st.title("📈 Analizador de Mercado Universal")

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