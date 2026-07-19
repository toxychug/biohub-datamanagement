#!/bin/bash

# Test POST /dev/simulate endpoint

BASE_URL="http://localhost:8000"

echo "Testing POST /dev/simulate endpoint"
echo "===================================="
echo ""

PAYLOAD='{
  "identificacion_basica": {
    "id_registro": "TEST-POST",
    "nombre_cientifico": "Panthera onca",
    "nombre_comun": "Jaguar"
  },
  "datos_hallazgo": {
    "fecha": "2026-04-20",
    "tipo_registro": "Avistamiento"
  },
  "geolocalizacion": {
    "latitud": 5.52,
    "longitud": -74.08,
    "nivel_sensibilidad": "RESTRICTED"
  },
  "informacion_registro": {
    "investigador": "researcher@institute.org",
    "institucion": "Instituto Humboldt"
  },
  "trazabilidad": {
    "version": 0,
    "historial_cambios": []
  }
}'

echo "Payload:"
echo "$PAYLOAD" | jq .
echo ""

echo "Sending POST request..."
echo ""

curl -v -X POST "$BASE_URL/dev/simulate" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD"

echo ""
echo ""
echo "Done."
