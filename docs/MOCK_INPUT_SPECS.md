# Especificaciones del Formulario Mock - Campos Requeridos

## 📋 Campos Obligatorios (Requeridos con *)

### **Identificación Básica**
| Campo | Tipo | Ejemplo | Descripción |
|-------|------|---------|------------|
| **ID Registro*** | Texto | REG-001 | Identificador único del registro biológico |
| **Nombre Científico*** | Texto | Panthera onca | Nombre científico de la especie |
| Nombre Común | Texto | Jaguar | Nombre común de la especie |

### **Taxonomía**
| Campo | Tipo | Ejemplo |
|-------|------|---------|
| Reino | Texto | Animalia |
| Filo | Texto | Chordata |
| Clase | Texto | Mammalia |
| Orden | Texto | Carnivora |
| Familia | Texto | Felidae |
| Género | Texto | Panthera |
| Especie | Texto | P. onca |
| Autoridad Taxonómica | Texto | Linnaeus, 1758 |
| Estado Taxonómico | Select | Accepted, Synonym, Unresolved |

### **Geolocalización**
| Campo | Tipo | Ejemplo | Descripción |
|-------|------|---------|------------|
| **Latitud*** | Número | 5.52 | Coordenada Y |
| **Longitud*** | Número | -74.08 | Coordenada X |
| **Nivel de Sensibilidad*** | Select | PUBLIC, RESTRICTED, CONFIDENTIAL | Clasificación de acceso |

### **Información de Registro**
| Campo | Tipo | Ejemplo |
|-------|------|---------|
| **Email del Investigador*** | Email | test@example.com |
| Institución | Texto | Universidad Nacional de Colombia |
| Equipo de Expedición | Texto | Equipo Amazonia Norte |
| ID Expedición | Texto | EXP-2026-001 |

### **Trazabilidad**
| Campo | Tipo | Ejemplo | Descripción |
|-------|------|---------|------------|
| **Motivo/Razón de Cambio*** | Texto | Registro inicial de hallazgo | Por qué se crea o modifica |

---

## ✅ Validaciones

- **ID Registro**: No puede estar vacío
- **Nombre Científico**: Requerido
- **Latitud**: Número decimal, requerida
- **Longitud**: Número decimal, requerida
- **Email**: Debe ser formato válido
- **Motivo**: No puede estar vacío

---

## 📦 Estructura JSON Enviada

```json
{
  "identificacion_basica": {
    "id_registro": "REG-001",
    "nombre_cientifico": "Panthera onca",
    "nombre_comun": "Jaguar",
    "taxonomia": {
      "reino": "Animalia",
      "filo": "Chordata",
      "clase": "Mammalia",
      "orden": "Carnivora",
      "familia": "Felidae",
      "genero": "Panthera",
      "especie": "P. onca"
    },
    "autoridad_taxonomica": "Linnaeus, 1758",
    "estado_taxonomico": "Accepted"
  },
  "geolocalizacion": {
    "latitud": 5.52,
    "longitud": -74.08,
    "nivel_sensibilidad": "RESTRICTED"
  },
  "informacion_registro": {
    "investigador": "test@example.com",
    "institucion": "Universidad Nacional de Colombia",
    "equipo_expedicion": "Equipo Amazonia Norte",
    "id_expedicion": "EXP-2026-001"
  },
  "trazabilidad": {
    "motivo": "Registro inicial de hallazgo"
  }
}
```

---

## 🎯 Respuesta Esperada

```json
{
  "status": "ok",
  "id_registro": "REG-001",
  "version": 1,
  "timestamp": "2026-07-19T10:30:00Z"
}
```
