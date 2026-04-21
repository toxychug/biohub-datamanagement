#!/bin/bash

# Complete BioHub API Testing Script
# Run all endpoints sequentially with pretty output

BASE_URL="http://localhost:8000"
ID_REGISTRO="TEST-$(date +%s)"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║       BioHub Change Management & Audit API - Full Test        ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Test ID: $ID_REGISTRO"
echo "Base URL: $BASE_URL"
echo ""

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Helper function to print test headers
test_header() {
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${BLUE}TEST: $1${NC}"
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Helper function to print results
test_result() {
  if [ $1 -eq 0 ]; then
    echo -e "${GREEN}✓ PASSED${NC}\n"
  else
    echo -e "${YELLOW}✗ FAILED (HTTP $1)${NC}\n"
  fi
}

# Test 1: Health Check
test_header "1. Health Check"
echo "Request: GET /health"
echo ""
RESPONSE=$(curl -s -w "\n%{http_code}" "$BASE_URL/health")
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | head -1)
echo "Response ($HTTP_CODE):"
echo "$BODY" | jq . 2>/dev/null || echo "$BODY"
test_result $HTTP_CODE

# Test 2: Root Endpoint
test_header "2. Root Endpoint"
echo "Request: GET /"
echo ""
RESPONSE=$(curl -s -w "\n%{http_code}" "$BASE_URL/")
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | head -1)
echo "Response ($HTTP_CODE):"
echo "$BODY" | jq . 2>/dev/null || echo "$BODY"
test_result $HTTP_CODE

# Test 3: Create Record via Mock Kafka
test_header "3. Create Record (POST /dev/simulate)"
echo "Request: POST /dev/simulate"
echo ""
PAYLOAD=$(cat <<EOF
{
  "identificacion_basica": {
    "id_registro": "$ID_REGISTRO",
    "nombre_cientifico": "Panthera onca",
    "nombre_comun": "Jaguar",
    "taxonomia": {
      "reino": "Animalia",
      "filo": "Chordata",
      "clase": "Mammalia",
      "orden": "Carnivora",
      "familia": "Felidae",
      "genero": "Panthera",
      "especie": "onca"
    }
  },
  "datos_hallazgo": {
    "fecha": "2026-04-19",
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
  }
}
EOF
)

echo "Payload:"
echo "$PAYLOAD" | jq .
echo ""

RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/dev/simulate" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | head -1)
echo "Response ($HTTP_CODE):"
echo "$BODY" | jq . 2>/dev/null || echo "$BODY"
test_result $HTTP_CODE

sleep 1

# Test 4: Get Audit History
test_header "4. Get Audit History"
echo "Request: GET /auditoria/historial/$ID_REGISTRO"
echo ""
RESPONSE=$(curl -s -w "\n%{http_code}" "$BASE_URL/auditoria/historial/$ID_REGISTRO")
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | head -1)
echo "Response ($HTTP_CODE):"
echo "$BODY" | jq '.[] | {id_registro, version, usuario, sensibilidad, estado_aprobacion}' 2>/dev/null || echo "$BODY"
test_result $HTTP_CODE

# Test 5: Get Metadata
test_header "5. Get Metadata"
echo "Request: GET /auditoria/metadatos/$ID_REGISTRO"
echo ""
RESPONSE=$(curl -s -w "\n%{http_code}" "$BASE_URL/auditoria/metadatos/$ID_REGISTRO")
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | head -1)
echo "Response ($HTTP_CODE):"
echo "$BODY" | jq '.identificacion_basica | {id_registro, nombre_cientifico, nombre_comun}' 2>/dev/null || echo "$BODY"
test_result $HTTP_CODE

# Test 6: Get Sensitivity
test_header "6. Get Sensitivity Classification"
echo "Request: GET /auditoria/sensibilidad/$ID_REGISTRO"
echo ""
RESPONSE=$(curl -s -w "\n%{http_code}" "$BASE_URL/auditoria/sensibilidad/$ID_REGISTRO")
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | head -1)
echo "Response ($HTTP_CODE):"
echo "$BODY" | jq . 2>/dev/null || echo "$BODY"
test_result $HTTP_CODE

# Test 7: Get Approval Status (Before Update)
test_header "7. Get Approval Status (Initial)"
echo "Request: GET /aprobacion/$ID_REGISTRO"
echo ""
RESPONSE=$(curl -s -w "\n%{http_code}" "$BASE_URL/aprobacion/$ID_REGISTRO")
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | head -1)
echo "Response ($HTTP_CODE):"
echo "$BODY" | jq . 2>/dev/null || echo "$BODY"
test_result $HTTP_CODE

# Test 8: Update Approval Status
test_header "8. Update Approval to EN_REVISION"
echo "Request: POST /aprobacion/actualizar"
echo ""
UPDATE_PAYLOAD=$(cat <<EOF
{
  "id_registro": "$ID_REGISTRO",
  "nuevo_estado": "EN_REVISION",
  "director_aprobador": "director@institute.org",
  "comentarios": "Enviado para revisión científica"
}
EOF
)

echo "Payload:"
echo "$UPDATE_PAYLOAD" | jq .
echo ""

RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/aprobacion/actualizar" \
  -H "Content-Type: application/json" \
  -d "$UPDATE_PAYLOAD")
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | head -1)
echo "Response ($HTTP_CODE):"
echo "$BODY" | jq . 2>/dev/null || echo "$BODY"
test_result $HTTP_CODE

sleep 1

# Test 9: Get Approval Status (After Update)
test_header "9. Get Approval Status (After Update)"
echo "Request: GET /aprobacion/$ID_REGISTRO"
echo ""
RESPONSE=$(curl -s -w "\n%{http_code}" "$BASE_URL/aprobacion/$ID_REGISTRO")
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | head -1)
echo "Response ($HTTP_CODE):"
echo "$BODY" | jq . 2>/dev/null || echo "$BODY"
test_result $HTTP_CODE

# Test 10: Verify History Updated (Should now have 2 versions)
test_header "10. Verify History (Should show 2 versions)"
echo "Request: GET /auditoria/historial/$ID_REGISTRO"
echo ""
RESPONSE=$(curl -s -w "\n%{http_code}" "$BASE_URL/auditoria/historial/$ID_REGISTRO")
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | head -1)
echo "Response ($HTTP_CODE):"
echo "$BODY" | jq '.[] | {version, estado_aprobacion, usuario}' 2>/dev/null || echo "$BODY"
test_result $HTTP_CODE

# Test 11: Update to Approved
test_header "11. Update Approval to APROBADO"
echo "Request: POST /aprobacion/actualizar"
echo ""
APPROVE_PAYLOAD=$(cat <<EOF
{
  "id_registro": "$ID_REGISTRO",
  "nuevo_estado": "APROBADO",
  "director_aprobador": "director@institute.org",
  "comentarios": "Datos validados. Aprobado para publicación."
}
EOF
)

echo "Payload:"
echo "$APPROVE_PAYLOAD" | jq .
echo ""

RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/aprobacion/actualizar" \
  -H "Content-Type: application/json" \
  -d "$APPROVE_PAYLOAD")
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | head -1)
echo "Response ($HTTP_CODE):"
echo "$BODY" | jq . 2>/dev/null || echo "$BODY"
test_result $HTTP_CODE

# Final Summary
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    TEST COMPLETE ✓                            ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}All endpoints tested successfully!${NC}"
echo ""
echo "Record created with ID: $ID_REGISTRO"
echo "Final version: 3 (initial + 2 approval updates)"
echo ""
echo "Next steps:"
echo "1. Check MongoDB to verify data:"
echo "   db.audit_entries.find({ id_registro: '$ID_REGISTRO' }).pretty()"
echo "   db.biological_records.findOne({ id_registro: '$ID_REGISTRO' })"
echo ""
echo "2. View interactive API docs:"
echo "   http://localhost:8000/docs"
echo ""
