"""
Seed script: posts 10 biological records to POST /dev/simulate.
Run with: python seed_data.py
The API must be running at http://localhost:8000 (development mode).
"""

import json
import urllib.request
import urllib.error

BASE_URL = "http://localhost:8000/dev/simulate"

RECORDS = [
    {
        "identificacion_basica": {
            "id_registro": "REG-001",
            "nombre_cientifico": "Panthera onca",
            "nombre_comun": "Jaguar",
            "taxonomia": {
                "reino": "Animalia", "filo": "Chordata", "clase": "Mammalia",
                "orden": "Carnivora", "familia": "Felidae",
                "genero": "Panthera", "especie": "P. onca"
            },
            "estado_taxonomico": "Aceptado",
            "autoridad_taxonomica": "Linnaeus, 1758",
            "fecha_clasificacion": "2026-01-15"
        },
        "datos_hallazgo": {
            "fecha": "2026-04-19", "hora": "08:30:00",
            "tipo_registro": "Avistamiento", "metodo_observacion": "Fotográfico",
            "cantidad_individuos": 1, "comportamiento": "Caza"
        },
        "geolocalizacion": {
            "latitud": 1.2345, "longitud": -76.5432, "altitud": 320,
            "region": "Amazonas", "ecosistema": "Selva húmeda tropical",
            "precision": "Alta", "nivel_sensibilidad": "RESTRICTED"
        },
        "datos_ambientales": {
            "temperatura": 28.5, "humedad": 85, "ph_suelo": 6.2,
            "tipo_suelo": "Latosol", "clima": "Tropical húmedo",
            "precipitacion": 3200, "cobertura_vegetal": "Densa",
            "condiciones_entorno": "Óptimas"
        },
        "caracteristicas_fisicas": {
            "tamano": "Grande", "peso": "80kg", "coloracion": "Amarillo con manchas negras",
            "edad_aproximada": "Adulto", "sexo": "Macho", "estado_salud": "Saludable",
            "caracteristicas_distintivas": "Roseta característica en flanco derecho"
        },
        "evidencia": {
            "fotografias": ["foto_reg001_001.jpg", "foto_reg001_002.jpg"],
            "videos": ["video_reg001.mp4"], "audios": [], "archivos_adjuntos": [],
            "metadatos": {"fecha_captura": "2026-04-19T08:30:00", "gps": "1.2345,-76.5432", "dispositivo": "Nikon D850"}
        },
        "estado_conservacion": {
            "categoria_amenaza": "NT", "nivel_riesgo": "Moderado",
            "listas_oficiales": ["IUCN", "CITES Apéndice I"],
            "observaciones": "Población estable en la región"
        },
        "informacion_registro": {
            "investigador": "m.garcia@unal.edu.co",
            "equipo_expedicion": "Equipo Amazonia Norte",
            "institucion": "Universidad Nacional de Colombia",
            "id_expedicion": "EXP-2026-001",
            "fecha_registro": "2026-04-19", "estado_registro": "ACTIVO"
        },
        "validacion_cientifica": {
            "director_aprobador": "", "estado_validacion": "PENDIENTE",
            "comentarios": "", "fecha_validacion": ""
        },
        "trazabilidad": {
            "version": 1,
            "historial_cambios": [{"usuario": "m.garcia@unal.edu.co", "fecha": "2026-04-19",
                                   "cambio": "Registro inicial", "motivo": "Primera observación documentada"}]
        },
        "datos_analiticos": {
            "incluido_mapa_calor": True, "frecuencia_avistamiento": 1,
            "tendencias": "Estable", "indicadores_ecologicos": ["Depredador ápex"]
        },
        "datos_consumo_externo": {
            "anonimizado": False, "visible_publico": False,
            "version_api": "1.0", "restricciones_acceso": "Solo investigadores autorizados"
        }
    },
    {
        "identificacion_basica": {
            "id_registro": "REG-002",
            "nombre_cientifico": "Vultur gryphus",
            "nombre_comun": "Cóndor andino",
            "taxonomia": {
                "reino": "Animalia", "filo": "Chordata", "clase": "Aves",
                "orden": "Cathartiformes", "familia": "Cathartidae",
                "genero": "Vultur", "especie": "V. gryphus"
            },
            "estado_taxonomico": "Aceptado",
            "autoridad_taxonomica": "Linnaeus, 1758",
            "fecha_clasificacion": "2026-02-10"
        },
        "datos_hallazgo": {
            "fecha": "2026-03-05", "hora": "11:15:00",
            "tipo_registro": "Avistamiento", "metodo_observacion": "Visual directo",
            "cantidad_individuos": 3, "comportamiento": "Vuelo territorial"
        },
        "geolocalizacion": {
            "latitud": 1.9823, "longitud": -77.4215, "altitud": 3800,
            "region": "Nariño", "ecosistema": "Páramo andino",
            "precision": "Alta", "nivel_sensibilidad": "CONFIDENTIAL"
        },
        "datos_ambientales": {
            "temperatura": 8.0, "humedad": 72, "ph_suelo": 5.8,
            "tipo_suelo": "Andosol", "clima": "Frío de alta montaña",
            "precipitacion": 1200, "cobertura_vegetal": "Frailejonal",
            "condiciones_entorno": "Ventoso, cielos despejados"
        },
        "caracteristicas_fisicas": {
            "tamano": "Muy grande", "peso": "11kg", "coloracion": "Negro con collar blanco",
            "edad_aproximada": "Adulto", "sexo": "Macho", "estado_salud": "Saludable",
            "caracteristicas_distintivas": "Carúncula nasal prominente, envergadura ~3m"
        },
        "evidencia": {
            "fotografias": ["foto_reg002_condor_001.jpg"],
            "videos": [], "audios": ["audio_reg002_vuelo.mp3"], "archivos_adjuntos": [],
            "metadatos": {"fecha_captura": "2026-03-05T11:15:00", "gps": "1.9823,-77.4215", "dispositivo": "Canon EOS R5"}
        },
        "estado_conservacion": {
            "categoria_amenaza": "VU", "nivel_riesgo": "Alto",
            "listas_oficiales": ["IUCN", "CITES Apéndice I", "Libro Rojo Colombia"],
            "observaciones": "Nidificación confirmada en acantilado rocoso"
        },
        "informacion_registro": {
            "investigador": "c.rodriguez@humboldt.org.co",
            "equipo_expedicion": "Equipo Andes Sur",
            "institucion": "Instituto Humboldt",
            "id_expedicion": "EXP-2026-002",
            "fecha_registro": "2026-03-05", "estado_registro": "ACTIVO"
        },
        "validacion_cientifica": {
            "director_aprobador": "", "estado_validacion": "PENDIENTE",
            "comentarios": "", "fecha_validacion": ""
        },
        "trazabilidad": {
            "version": 1,
            "historial_cambios": [{"usuario": "c.rodriguez@humboldt.org.co", "fecha": "2026-03-05",
                                   "cambio": "Registro inicial", "motivo": "Monitoreo anual de cóndores"}]
        },
        "datos_analiticos": {
            "incluido_mapa_calor": True, "frecuencia_avistamiento": 3,
            "tendencias": "Recuperación lenta", "indicadores_ecologicos": ["Carroñero ápex", "Bioindicador de salud ecosistémica"]
        },
        "datos_consumo_externo": {
            "anonimizado": True, "visible_publico": False,
            "version_api": "1.0", "restricciones_acceso": "Solo investigadores autorizados"
        }
    },
    {
        "identificacion_basica": {
            "id_registro": "REG-003",
            "nombre_cientifico": "Cattleya trianae",
            "nombre_comun": "Orquídea de Colombia / Flor de Navidad",
            "taxonomia": {
                "reino": "Plantae", "filo": "Tracheophyta", "clase": "Liliopsida",
                "orden": "Asparagales", "familia": "Orchidaceae",
                "genero": "Cattleya", "especie": "C. trianae"
            },
            "estado_taxonomico": "Aceptado",
            "autoridad_taxonomica": "Linden & Rchb.f., 1860",
            "fecha_clasificacion": "2026-01-20"
        },
        "datos_hallazgo": {
            "fecha": "2026-02-14", "hora": "09:00:00",
            "tipo_registro": "Colecta botánica", "metodo_observacion": "Fotográfico",
            "cantidad_individuos": 12, "comportamiento": "Floración"
        },
        "geolocalizacion": {
            "latitud": 4.7110, "longitud": -74.0721, "altitud": 1800,
            "region": "Cundinamarca", "ecosistema": "Bosque andino húmedo",
            "precision": "Alta", "nivel_sensibilidad": "PUBLIC"
        },
        "datos_ambientales": {
            "temperatura": 18.5, "humedad": 80, "ph_suelo": 6.0,
            "tipo_suelo": "Oxisol", "clima": "Templado húmedo",
            "precipitacion": 2800, "cobertura_vegetal": "Bosque secundario denso",
            "condiciones_entorno": "Epífita sobre roble andino"
        },
        "caracteristicas_fisicas": {
            "tamano": "Mediano", "peso": "N/A", "coloracion": "Pétalos lila con labelo carmesí",
            "edad_aproximada": "Adulto reproductivo", "sexo": "N/A", "estado_salud": "Saludable",
            "caracteristicas_distintivas": "Flores grandes de hasta 20cm, fragancia intensa"
        },
        "evidencia": {
            "fotografias": ["foto_reg003_cattleya_001.jpg", "foto_reg003_cattleya_002.jpg", "foto_reg003_cattleya_003.jpg"],
            "videos": [], "audios": [], "archivos_adjuntos": ["herbario_reg003.pdf"],
            "metadatos": {"fecha_captura": "2026-02-14T09:00:00", "gps": "4.7110,-74.0721", "dispositivo": "Sony A7IV"}
        },
        "estado_conservacion": {
            "categoria_amenaza": "VU", "nivel_riesgo": "Alto",
            "listas_oficiales": ["IUCN", "CITES Apéndice II"],
            "observaciones": "Especie nacional de Colombia, presión por extracción ilegal"
        },
        "informacion_registro": {
            "investigador": "l.perez@botanica.unal.edu.co",
            "equipo_expedicion": "Equipo Flora Andina",
            "institucion": "Universidad Nacional de Colombia - Herbario Nacional",
            "id_expedicion": "EXP-2026-003",
            "fecha_registro": "2026-02-14", "estado_registro": "ACTIVO"
        },
        "validacion_cientifica": {
            "director_aprobador": "", "estado_validacion": "PENDIENTE",
            "comentarios": "", "fecha_validacion": ""
        },
        "trazabilidad": {
            "version": 1,
            "historial_cambios": [{"usuario": "l.perez@botanica.unal.edu.co", "fecha": "2026-02-14",
                                   "cambio": "Registro inicial", "motivo": "Inventario flora endémica andina"}]
        },
        "datos_analiticos": {
            "incluido_mapa_calor": True, "frecuencia_avistamiento": 12,
            "tendencias": "Decreciente", "indicadores_ecologicos": ["Epífita indicadora de calidad de bosque"]
        },
        "datos_consumo_externo": {
            "anonimizado": False, "visible_publico": True,
            "version_api": "1.0", "restricciones_acceso": "Público general"
        }
    },
    {
        "identificacion_basica": {
            "id_registro": "REG-004",
            "nombre_cientifico": "Inia geoffrensis",
            "nombre_comun": "Delfín rosado / Boto",
            "taxonomia": {
                "reino": "Animalia", "filo": "Chordata", "clase": "Mammalia",
                "orden": "Artiodactyla", "familia": "Iniidae",
                "genero": "Inia", "especie": "I. geoffrensis"
            },
            "estado_taxonomico": "Aceptado",
            "autoridad_taxonomica": "de Blainville, 1817",
            "fecha_clasificacion": "2026-01-10"
        },
        "datos_hallazgo": {
            "fecha": "2026-04-02", "hora": "06:45:00",
            "tipo_registro": "Avistamiento", "metodo_observacion": "Visual directo y acústico",
            "cantidad_individuos": 4, "comportamiento": "Alimentación y juego social"
        },
        "geolocalizacion": {
            "latitud": -3.4653, "longitud": -70.1174, "altitud": 90,
            "region": "Amazonas", "ecosistema": "Río amazónico - igapó",
            "precision": "Alta", "nivel_sensibilidad": "RESTRICTED"
        },
        "datos_ambientales": {
            "temperatura": 30.2, "humedad": 92, "ph_suelo": 6.8,
            "tipo_suelo": "Aluvial", "clima": "Tropical húmedo ecuatorial",
            "precipitacion": 3800, "cobertura_vegetal": "Bosque inundable",
            "condiciones_entorno": "Aguas negras, caudal alto por temporada de lluvias"
        },
        "caracteristicas_fisicas": {
            "tamano": "Mediano-grande", "peso": "185kg", "coloracion": "Rosado intenso en adulto",
            "edad_aproximada": "Adulto", "sexo": "Hembra", "estado_salud": "Saludable",
            "caracteristicas_distintivas": "Aleta dorsal vestigial, coloración rosa característica"
        },
        "evidencia": {
            "fotografias": ["foto_reg004_boto_001.jpg", "foto_reg004_boto_002.jpg"],
            "videos": ["video_reg004_nado.mp4"], "audios": ["audio_reg004_ecoloc.wav"],
            "archivos_adjuntos": [],
            "metadatos": {"fecha_captura": "2026-04-02T06:45:00", "gps": "-3.4653,-70.1174", "dispositivo": "GoPro Hero 12"}
        },
        "estado_conservacion": {
            "categoria_amenaza": "EN", "nivel_riesgo": "Alto",
            "listas_oficiales": ["IUCN", "CITES Apéndice II", "Libro Rojo Colombia"],
            "observaciones": "Amenazado por pesca incidental y contaminación por mercurio"
        },
        "informacion_registro": {
            "investigador": "a.torres@sinchi.org.co",
            "equipo_expedicion": "Equipo Mamíferos Acuáticos Amazonia",
            "institucion": "Instituto Sinchi",
            "id_expedicion": "EXP-2026-004",
            "fecha_registro": "2026-04-02", "estado_registro": "ACTIVO"
        },
        "validacion_cientifica": {
            "director_aprobador": "", "estado_validacion": "PENDIENTE",
            "comentarios": "", "fecha_validacion": ""
        },
        "trazabilidad": {
            "version": 1,
            "historial_cambios": [{"usuario": "a.torres@sinchi.org.co", "fecha": "2026-04-02",
                                   "cambio": "Registro inicial", "motivo": "Monitoreo población de botos río Amazonas"}]
        },
        "datos_analiticos": {
            "incluido_mapa_calor": True, "frecuencia_avistamiento": 4,
            "tendencias": "Decreciente", "indicadores_ecologicos": ["Indicador salud río", "Mamífero acuático tope"]
        },
        "datos_consumo_externo": {
            "anonimizado": True, "visible_publico": False,
            "version_api": "1.0", "restricciones_acceso": "Solo investigadores autorizados"
        }
    },
    {
        "identificacion_basica": {
            "id_registro": "REG-005",
            "nombre_cientifico": "Tremarctos ornatus",
            "nombre_comun": "Oso de anteojos / Oso andino",
            "taxonomia": {
                "reino": "Animalia", "filo": "Chordata", "clase": "Mammalia",
                "orden": "Carnivora", "familia": "Ursidae",
                "genero": "Tremarctos", "especie": "T. ornatus"
            },
            "estado_taxonomico": "Aceptado",
            "autoridad_taxonomica": "F.G. Cuvier, 1825",
            "fecha_clasificacion": "2026-01-22"
        },
        "datos_hallazgo": {
            "fecha": "2026-03-18", "hora": "16:20:00",
            "tipo_registro": "Trampa cámara", "metodo_observacion": "Cámara trampa infrarrojo",
            "cantidad_individuos": 1, "comportamiento": "Forrajeo"
        },
        "geolocalizacion": {
            "latitud": 5.8102, "longitud": -73.0152, "altitud": 2650,
            "region": "Boyacá", "ecosistema": "Bosque andino subpáramo",
            "precision": "Media", "nivel_sensibilidad": "RESTRICTED"
        },
        "datos_ambientales": {
            "temperatura": 12.0, "humedad": 88, "ph_suelo": 5.5,
            "tipo_suelo": "Andosol húmico", "clima": "Frío húmedo",
            "precipitacion": 2100, "cobertura_vegetal": "Bosque de niebla",
            "condiciones_entorno": "Alta nubosidad, vegetación densa"
        },
        "caracteristicas_fisicas": {
            "tamano": "Mediano-grande", "peso": "130kg", "coloracion": "Negro con manchas blancas periorbitales",
            "edad_aproximada": "Adulto joven", "sexo": "Macho", "estado_salud": "Saludable",
            "caracteristicas_distintivas": "Patrón facial único tipo antifaz, garras largas"
        },
        "evidencia": {
            "fotografias": ["foto_reg005_oso_camtrap_001.jpg", "foto_reg005_oso_camtrap_002.jpg"],
            "videos": ["video_reg005_camtrap.mp4"], "audios": [], "archivos_adjuntos": [],
            "metadatos": {"fecha_captura": "2026-03-18T16:20:00", "gps": "5.8102,-73.0152", "dispositivo": "Bushnell Core 30MP"}
        },
        "estado_conservacion": {
            "categoria_amenaza": "VU", "nivel_riesgo": "Alto",
            "listas_oficiales": ["IUCN", "CITES Apéndice I", "Libro Rojo Colombia"],
            "observaciones": "Único úrsido sudamericano, corredor biológico activo"
        },
        "informacion_registro": {
            "investigador": "j.medina@wcs.org",
            "equipo_expedicion": "Equipo Mamíferos Andinos WCS",
            "institucion": "Wildlife Conservation Society Colombia",
            "id_expedicion": "EXP-2026-005",
            "fecha_registro": "2026-03-18", "estado_registro": "ACTIVO"
        },
        "validacion_cientifica": {
            "director_aprobador": "", "estado_validacion": "PENDIENTE",
            "comentarios": "", "fecha_validacion": ""
        },
        "trazabilidad": {
            "version": 1,
            "historial_cambios": [{"usuario": "j.medina@wcs.org", "fecha": "2026-03-18",
                                   "cambio": "Registro inicial", "motivo": "Red de cámaras trampa corredor Boyacá-Casanare"}]
        },
        "datos_analiticos": {
            "incluido_mapa_calor": False, "frecuencia_avistamiento": 1,
            "tendencias": "Estable", "indicadores_ecologicos": ["Paraguas de conservación", "Dispersor de semillas"]
        },
        "datos_consumo_externo": {
            "anonimizado": True, "visible_publico": False,
            "version_api": "1.0", "restricciones_acceso": "Solo investigadores autorizados"
        }
    },
    {
        "identificacion_basica": {
            "id_registro": "REG-006",
            "nombre_cientifico": "Heliconia wagneriana",
            "nombre_comun": "Ave del paraíso / Platanillo rojo",
            "taxonomia": {
                "reino": "Plantae", "filo": "Tracheophyta", "clase": "Liliopsida",
                "orden": "Zingiberales", "familia": "Heliconiaceae",
                "genero": "Heliconia", "especie": "H. wagneriana"
            },
            "estado_taxonomico": "Aceptado",
            "autoridad_taxonomica": "Peters, 1912",
            "fecha_clasificacion": "2026-02-01"
        },
        "datos_hallazgo": {
            "fecha": "2026-02-28", "hora": "10:30:00",
            "tipo_registro": "Colecta botánica", "metodo_observacion": "Fotográfico",
            "cantidad_individuos": 35, "comportamiento": "Floración masiva"
        },
        "geolocalizacion": {
            "latitud": 6.2442, "longitud": -75.5812, "altitud": 600,
            "region": "Antioquia", "ecosistema": "Bosque húmedo tropical premontano",
            "precision": "Alta", "nivel_sensibilidad": "PUBLIC"
        },
        "datos_ambientales": {
            "temperatura": 24.0, "humedad": 78, "ph_suelo": 6.5,
            "tipo_suelo": "Ultisol", "clima": "Tropical premontano",
            "precipitacion": 2600, "cobertura_vegetal": "Bosque ripario",
            "condiciones_entorno": "Ribera de quebrada, suelo rico en materia orgánica"
        },
        "caracteristicas_fisicas": {
            "tamano": "Grande", "peso": "N/A", "coloracion": "Brácteas rojo brillante con amarillo",
            "edad_aproximada": "Adulto reproductivo", "sexo": "N/A", "estado_salud": "Saludable",
            "caracteristicas_distintivas": "Inflorescencia erecta de hasta 1.5m, brácteas vistosas"
        },
        "evidencia": {
            "fotografias": ["foto_reg006_heliconia_001.jpg", "foto_reg006_heliconia_002.jpg"],
            "videos": [], "audios": [], "archivos_adjuntos": [],
            "metadatos": {"fecha_captura": "2026-02-28T10:30:00", "gps": "6.2442,-75.5812", "dispositivo": "iPhone 15 Pro Max"}
        },
        "estado_conservacion": {
            "categoria_amenaza": "LC", "nivel_riesgo": "Bajo",
            "listas_oficiales": ["IUCN"],
            "observaciones": "Población abundante, importante para colibríes y murciélagos polinizadores"
        },
        "informacion_registro": {
            "investigador": "s.vargas@udea.edu.co",
            "equipo_expedicion": "Equipo Etnobotánica Antioquia",
            "institucion": "Universidad de Antioquia",
            "id_expedicion": "EXP-2026-006",
            "fecha_registro": "2026-02-28", "estado_registro": "ACTIVO"
        },
        "validacion_cientifica": {
            "director_aprobador": "", "estado_validacion": "PENDIENTE",
            "comentarios": "", "fecha_validacion": ""
        },
        "trazabilidad": {
            "version": 1,
            "historial_cambios": [{"usuario": "s.vargas@udea.edu.co", "fecha": "2026-02-28",
                                   "cambio": "Registro inicial", "motivo": "Inventario flora ribereña cuenca Medellín"}]
        },
        "datos_analiticos": {
            "incluido_mapa_calor": True, "frecuencia_avistamiento": 35,
            "tendencias": "Estable", "indicadores_ecologicos": ["Planta nodriza", "Recurso néctar para polinizadores"]
        },
        "datos_consumo_externo": {
            "anonimizado": False, "visible_publico": True,
            "version_api": "1.0", "restricciones_acceso": "Público general"
        }
    },
    {
        "identificacion_basica": {
            "id_registro": "REG-007",
            "nombre_cientifico": "Tapirus terrestris",
            "nombre_comun": "Tapir amazónico / Danta",
            "taxonomia": {
                "reino": "Animalia", "filo": "Chordata", "clase": "Mammalia",
                "orden": "Perissodactyla", "familia": "Tapiridae",
                "genero": "Tapirus", "especie": "T. terrestris"
            },
            "estado_taxonomico": "Aceptado",
            "autoridad_taxonomica": "Linnaeus, 1758",
            "fecha_clasificacion": "2026-01-30"
        },
        "datos_hallazgo": {
            "fecha": "2026-04-10", "hora": "19:50:00",
            "tipo_registro": "Trampa cámara", "metodo_observacion": "Cámara trampa nocturna",
            "cantidad_individuos": 2, "comportamiento": "Bebedero nocturno"
        },
        "geolocalizacion": {
            "latitud": 0.8667, "longitud": -76.2167, "altitud": 250,
            "region": "Putumayo", "ecosistema": "Selva húmeda de llanura",
            "precision": "Alta", "nivel_sensibilidad": "RESTRICTED"
        },
        "datos_ambientales": {
            "temperatura": 27.0, "humedad": 90, "ph_suelo": 6.0,
            "tipo_suelo": "Oxisol", "clima": "Tropical húmedo",
            "precipitacion": 3500, "cobertura_vegetal": "Selva primaria",
            "condiciones_entorno": "Colpa mineral cerca a quebrada"
        },
        "caracteristicas_fisicas": {
            "tamano": "Grande", "peso": "260kg", "coloracion": "Pardo oscuro uniforme",
            "edad_aproximada": "Adulto", "sexo": "Hembra con cría",
            "estado_salud": "Saludable",
            "caracteristicas_distintivas": "Probóscide prensil, cría con rayas y manchas blancas"
        },
        "evidencia": {
            "fotografias": ["foto_reg007_tapir_001.jpg", "foto_reg007_tapir_002.jpg"],
            "videos": ["video_reg007_bebedero.mp4"], "audios": [], "archivos_adjuntos": [],
            "metadatos": {"fecha_captura": "2026-04-10T19:50:00", "gps": "0.8667,-76.2167", "dispositivo": "Reconyx HyperFire 2"}
        },
        "estado_conservacion": {
            "categoria_amenaza": "VU", "nivel_riesgo": "Moderado-alto",
            "listas_oficiales": ["IUCN", "CITES Apéndice II"],
            "observaciones": "Avistamiento de madre con cría, signo positivo de reproducción"
        },
        "informacion_registro": {
            "investigador": "f.restrepo@sinchi.org.co",
            "equipo_expedicion": "Equipo Fauna Amazonia Sur",
            "institucion": "Instituto Sinchi",
            "id_expedicion": "EXP-2026-007",
            "fecha_registro": "2026-04-10", "estado_registro": "ACTIVO"
        },
        "validacion_cientifica": {
            "director_aprobador": "", "estado_validacion": "PENDIENTE",
            "comentarios": "", "fecha_validacion": ""
        },
        "trazabilidad": {
            "version": 1,
            "historial_cambios": [{"usuario": "f.restrepo@sinchi.org.co", "fecha": "2026-04-10",
                                   "cambio": "Registro inicial", "motivo": "Monitoreo megafauna río Putumayo"}]
        },
        "datos_analiticos": {
            "incluido_mapa_calor": True, "frecuencia_avistamiento": 2,
            "tendencias": "Estable", "indicadores_ecologicos": ["Jardinero del bosque", "Dispersor de semillas grandes"]
        },
        "datos_consumo_externo": {
            "anonimizado": True, "visible_publico": False,
            "version_api": "1.0", "restricciones_acceso": "Solo investigadores autorizados"
        }
    },
    {
        "identificacion_basica": {
            "id_registro": "REG-008",
            "nombre_cientifico": "Trichechus manatus",
            "nombre_comun": "Manatí del Caribe",
            "taxonomia": {
                "reino": "Animalia", "filo": "Chordata", "clase": "Mammalia",
                "orden": "Sirenia", "familia": "Trichechidae",
                "genero": "Trichechus", "especie": "T. manatus"
            },
            "estado_taxonomico": "Aceptado",
            "autoridad_taxonomica": "Linnaeus, 1758",
            "fecha_clasificacion": "2026-01-05"
        },
        "datos_hallazgo": {
            "fecha": "2026-03-22", "hora": "07:15:00",
            "tipo_registro": "Avistamiento", "metodo_observacion": "Buceo y fotográfico",
            "cantidad_individuos": 2, "comportamiento": "Pastoreo de pastos marinos"
        },
        "geolocalizacion": {
            "latitud": 10.3997, "longitud": -75.5144, "altitud": 0,
            "region": "Bolívar", "ecosistema": "Ecosistema marino-costero - Bahía de Cartagena",
            "precision": "Alta", "nivel_sensibilidad": "CONFIDENTIAL"
        },
        "datos_ambientales": {
            "temperatura": 29.5, "humedad": 82, "ph_suelo": 8.1,
            "tipo_suelo": "Sedimento marino", "clima": "Tropical costero árido",
            "precipitacion": 900, "cobertura_vegetal": "Pastos marinos (Thalassia testudinum)",
            "condiciones_entorno": "Aguas someras turbulentas, presión por tráfico náutico"
        },
        "caracteristicas_fisicas": {
            "tamano": "Grande", "peso": "380kg", "coloracion": "Gris pizarra uniforme",
            "edad_aproximada": "Adulto", "sexo": "Hembra", "estado_salud": "Regular - cicatriz por hélice",
            "caracteristicas_distintivas": "Cicatriz helicoidal en dorso, aleta caudal en paleta"
        },
        "evidencia": {
            "fotografias": ["foto_reg008_manati_001.jpg", "foto_reg008_manati_002.jpg"],
            "videos": ["video_reg008_pastoreo.mp4"], "audios": [], "archivos_adjuntos": ["ficha_medica_reg008.pdf"],
            "metadatos": {"fecha_captura": "2026-03-22T07:15:00", "gps": "10.3997,-75.5144", "dispositivo": "GoPro Hero 12 subacuático"}
        },
        "estado_conservacion": {
            "categoria_amenaza": "VU", "nivel_riesgo": "Alto",
            "listas_oficiales": ["IUCN", "CITES Apéndice I", "Libro Rojo Colombia"],
            "observaciones": "Herida reciente por embarcación, bajo seguimiento veterinario remoto"
        },
        "informacion_registro": {
            "investigador": "p.quintero@invemar.org.co",
            "equipo_expedicion": "Equipo Mamíferos Marinos Caribe",
            "institucion": "INVEMAR",
            "id_expedicion": "EXP-2026-008",
            "fecha_registro": "2026-03-22", "estado_registro": "ACTIVO"
        },
        "validacion_cientifica": {
            "director_aprobador": "", "estado_validacion": "PENDIENTE",
            "comentarios": "", "fecha_validacion": ""
        },
        "trazabilidad": {
            "version": 1,
            "historial_cambios": [{"usuario": "p.quintero@invemar.org.co", "fecha": "2026-03-22",
                                   "cambio": "Registro inicial", "motivo": "Programa de monitoreo manatíes Caribe colombiano"}]
        },
        "datos_analiticos": {
            "incluido_mapa_calor": True, "frecuencia_avistamiento": 2,
            "tendencias": "Decreciente", "indicadores_ecologicos": ["Herbivorismo de pastos marinos", "Indicador salud litoral"]
        },
        "datos_consumo_externo": {
            "anonimizado": True, "visible_publico": False,
            "version_api": "1.0", "restricciones_acceso": "Solo investigadores autorizados"
        }
    },
    {
        "identificacion_basica": {
            "id_registro": "REG-009",
            "nombre_cientifico": "Cedrela odorata",
            "nombre_comun": "Cedro rosado / Cedro español",
            "taxonomia": {
                "reino": "Plantae", "filo": "Tracheophyta", "clase": "Magnoliopsida",
                "orden": "Sapindales", "familia": "Meliaceae",
                "genero": "Cedrela", "especie": "C. odorata"
            },
            "estado_taxonomico": "Aceptado",
            "autoridad_taxonomica": "L., 1759",
            "fecha_clasificacion": "2026-01-08"
        },
        "datos_hallazgo": {
            "fecha": "2026-01-25", "hora": "08:00:00",
            "tipo_registro": "Inventario forestal", "metodo_observacion": "DAP y medición directa",
            "cantidad_individuos": 8, "comportamiento": "Fructificación"
        },
        "geolocalizacion": {
            "latitud": 3.8667, "longitud": -73.0333, "altitud": 180,
            "region": "Meta", "ecosistema": "Bosque de galería - Orinoquía",
            "precision": "Alta", "nivel_sensibilidad": "PUBLIC"
        },
        "datos_ambientales": {
            "temperatura": 31.0, "humedad": 70, "ph_suelo": 6.8,
            "tipo_suelo": "Inceptisol", "clima": "Tropical de sabana",
            "precipitacion": 2400, "cobertura_vegetal": "Bosque de galería",
            "condiciones_entorno": "Ribera río Meta, suelos aluviales"
        },
        "caracteristicas_fisicas": {
            "tamano": "Muy grande", "peso": "N/A", "coloracion": "Corteza gris-parda fisurada",
            "edad_aproximada": "Maduro (>80 años)", "sexo": "N/A", "estado_salud": "Saludable",
            "caracteristicas_distintivas": "DAP promedio 65cm, altura total 28m, madera aromática"
        },
        "evidencia": {
            "fotografias": ["foto_reg009_cedro_001.jpg", "foto_reg009_cedro_002.jpg"],
            "videos": [], "audios": [], "archivos_adjuntos": ["inventario_reg009.xlsx"],
            "metadatos": {"fecha_captura": "2026-01-25T08:00:00", "gps": "3.8667,-73.0333", "dispositivo": "Trimble GeoXH"}
        },
        "estado_conservacion": {
            "categoria_amenaza": "VU", "nivel_riesgo": "Alto",
            "listas_oficiales": ["IUCN", "CITES Apéndice III"],
            "observaciones": "Alta presión maderera histórica, individuos maduros escasos"
        },
        "informacion_registro": {
            "investigador": "r.castillo@cormacarena.gov.co",
            "equipo_expedicion": "Equipo Inventario Forestal Orinoquía",
            "institucion": "CORMACARENA",
            "id_expedicion": "EXP-2026-009",
            "fecha_registro": "2026-01-25", "estado_registro": "ACTIVO"
        },
        "validacion_cientifica": {
            "director_aprobador": "", "estado_validacion": "PENDIENTE",
            "comentarios": "", "fecha_validacion": ""
        },
        "trazabilidad": {
            "version": 1,
            "historial_cambios": [{"usuario": "r.castillo@cormacarena.gov.co", "fecha": "2026-01-25",
                                   "cambio": "Registro inicial", "motivo": "Inventario forestal cuenca media río Meta"}]
        },
        "datos_analiticos": {
            "incluido_mapa_calor": False, "frecuencia_avistamiento": 8,
            "tendencias": "Decreciente", "indicadores_ecologicos": ["Especie maderable amenazada", "Refugio de fauna"]
        },
        "datos_consumo_externo": {
            "anonimizado": False, "visible_publico": True,
            "version_api": "1.0", "restricciones_acceso": "Público general"
        }
    },
    {
        "identificacion_basica": {
            "id_registro": "REG-010",
            "nombre_cientifico": "Eunectes murinus",
            "nombre_comun": "Anaconda verde",
            "taxonomia": {
                "reino": "Animalia", "filo": "Chordata", "clase": "Reptilia",
                "orden": "Squamata", "familia": "Boidae",
                "genero": "Eunectes", "especie": "E. murinus"
            },
            "estado_taxonomico": "Aceptado",
            "autoridad_taxonomica": "Linnaeus, 1758",
            "fecha_clasificacion": "2026-02-05"
        },
        "datos_hallazgo": {
            "fecha": "2026-04-15", "hora": "14:00:00",
            "tipo_registro": "Captura temporal", "metodo_observacion": "Captura manual con biometría",
            "cantidad_individuos": 1, "comportamiento": "Termorregulación en orilla"
        },
        "geolocalizacion": {
            "latitud": 2.9273, "longitud": -68.1940, "altitud": 95,
            "region": "Vichada", "ecosistema": "Río de aguas blancas - Llanos inundables",
            "precision": "Alta", "nivel_sensibilidad": "RESTRICTED"
        },
        "datos_ambientales": {
            "temperatura": 33.5, "humedad": 88, "ph_suelo": 6.9,
            "tipo_suelo": "Entisol aluvial", "clima": "Tropical de sabana",
            "precipitacion": 2200, "cobertura_vegetal": "Vegetación de rebalse",
            "condiciones_entorno": "Orilla lodosa con macrófitas, temporada seca"
        },
        "caracteristicas_fisicas": {
            "tamano": "Muy grande", "peso": "72kg", "coloracion": "Verde oliva con manchas negras ovales",
            "edad_aproximada": "Adulto", "sexo": "Hembra", "estado_salud": "Saludable",
            "caracteristicas_distintivas": "Longitud total 6.2m, circunferencia máxima 42cm"
        },
        "evidencia": {
            "fotografias": ["foto_reg010_anaconda_001.jpg", "foto_reg010_anaconda_002.jpg", "foto_reg010_anaconda_003.jpg"],
            "videos": ["video_reg010_captura.mp4"], "audios": [], "archivos_adjuntos": ["biometria_reg010.pdf"],
            "metadatos": {"fecha_captura": "2026-04-15T14:00:00", "gps": "2.9273,-68.1940", "dispositivo": "Canon PowerShot G7X III"}
        },
        "estado_conservacion": {
            "categoria_amenaza": "LC", "nivel_riesgo": "Bajo",
            "listas_oficiales": ["IUCN", "CITES Apéndice II"],
            "observaciones": "Serpiente más pesada del mundo, marcada con PIT-tag #EUN-2026-VIC-001"
        },
        "informacion_registro": {
            "investigador": "d.ospina@uniandes.edu.co",
            "equipo_expedicion": "Equipo Herpetología Llanos",
            "institucion": "Universidad de los Andes",
            "id_expedicion": "EXP-2026-010",
            "fecha_registro": "2026-04-15", "estado_registro": "ACTIVO"
        },
        "validacion_cientifica": {
            "director_aprobador": "", "estado_validacion": "PENDIENTE",
            "comentarios": "", "fecha_validacion": ""
        },
        "trazabilidad": {
            "version": 1,
            "historial_cambios": [{"usuario": "d.ospina@uniandes.edu.co", "fecha": "2026-04-15",
                                   "cambio": "Registro inicial", "motivo": "Estudio biometría anacondas río Orinoco"}]
        },
        "datos_analiticos": {
            "incluido_mapa_calor": True, "frecuencia_avistamiento": 1,
            "tendencias": "Estable", "indicadores_ecologicos": ["Depredador semiacuático ápex", "Regulador de fauna acuática"]
        },
        "datos_consumo_externo": {
            "anonimizado": False, "visible_publico": False,
            "version_api": "1.0", "restricciones_acceso": "Solo investigadores autorizados"
        }
    },
]


def post_record(record: dict) -> dict:
    data = json.dumps(record).encode("utf-8")
    req = urllib.request.Request(
        BASE_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def main():
    print(f"Seeding {len(RECORDS)} biological records to {BASE_URL}\n")
    ok = 0
    for record in RECORDS:
        reg_id = record["identificacion_basica"]["id_registro"]
        nombre = record["identificacion_basica"]["nombre_cientifico"]
        try:
            result = post_record(record)
            print(f"[OK] {reg_id} - {nombre} | version {result['version']} @ {result['timestamp']}")
            ok += 1
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            print(f"[ERROR] {reg_id} - {nombre} | HTTP {e.code}: {body}")
        except Exception as e:
            print(f"[ERROR] {reg_id} - {nombre} | {e}")

    print(f"\nDone: {ok}/{len(RECORDS)} records inserted successfully.")


if __name__ == "__main__":
    main()
