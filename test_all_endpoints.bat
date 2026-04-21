@echo off
REM Complete BioHub API Testing Script (Windows)
REM Run all endpoints sequentially

setlocal enabledelayedexpansion

set BASE_URL=http://localhost:8000

REM Generate unique test ID
for /f "tokens=*" %%A in ('powershell get-date -format yyyyMMddHHmmss') do set TIMESTAMP=%%A
set ID_REGISTRO=TEST-%TIMESTAMP%

echo.
echo ========================================================================
echo        BioHub Change Management ^& Audit API - Full Test
echo ========================================================================
echo.
echo Test ID: %ID_REGISTRO%
echo Base URL: %BASE_URL%
echo.
pause

REM Test 1: Health Check
echo.
echo TEST 1: Health Check
echo --------
echo Request: GET /health
curl -s %BASE_URL%/health
echo.
pause

REM Test 2: Create Record
echo.
echo TEST 2: Create Record ^(POST /dev/simulate^)
echo --------
echo Request: POST /dev/simulate
echo.

set PAYLOAD={^
  "identificacion_basica": {^
    "id_registro": "%ID_REGISTRO%",^
    "nombre_cientifico": "Panthera onca",^
    "nombre_comun": "Jaguar"^
  },^
  "geolocalizacion": {^
    "latitud": 5.52,^
    "nivel_sensibilidad": "RESTRICTED"^
  },^
  "informacion_registro": {^
    "investigador": "researcher@institute.org",^
    "institucion": "Instituto Humboldt"^
  }^
}

curl -X POST %BASE_URL%/dev/simulate ^
  -H "Content-Type: application/json" ^
  -d "%PAYLOAD%"
echo.
pause

REM Test 3: Get Audit History
echo.
echo TEST 3: Get Audit History
echo --------
echo Request: GET /auditoria/historial/%ID_REGISTRO%
curl -s %BASE_URL%/auditoria/historial/%ID_REGISTRO%
echo.
pause

REM Test 4: Get Metadata
echo.
echo TEST 4: Get Metadata
echo --------
echo Request: GET /auditoria/metadatos/%ID_REGISTRO%
curl -s %BASE_URL%/auditoria/metadatos/%ID_REGISTRO%
echo.
pause

REM Test 5: Get Sensitivity
echo.
echo TEST 5: Get Sensitivity
echo --------
echo Request: GET /auditoria/sensibilidad/%ID_REGISTRO%
curl -s %BASE_URL%/auditoria/sensibilidad/%ID_REGISTRO%
echo.
pause

REM Test 6: Get Approval Status
echo.
echo TEST 6: Get Approval Status
echo --------
echo Request: GET /aprobacion/%ID_REGISTRO%
curl -s %BASE_URL%/aprobacion/%ID_REGISTRO%
echo.
pause

REM Test 7: Update Approval
echo.
echo TEST 7: Update Approval to EN_REVISION
echo --------
echo Request: POST /aprobacion/actualizar
echo.

set UPDATE_PAYLOAD={^
  "id_registro": "%ID_REGISTRO%",^
  "nuevo_estado": "EN_REVISION",^
  "director_aprobador": "director@institute.org",^
  "comentarios": "Enviado para revisión"^
}

curl -X POST %BASE_URL%/aprobacion/actualizar ^
  -H "Content-Type: application/json" ^
  -d "%UPDATE_PAYLOAD%"
echo.
pause

REM Test 8: Verify History Updated
echo.
echo TEST 8: Verify History Updated ^(Should show 2 versions^)
echo --------
echo Request: GET /auditoria/historial/%ID_REGISTRO%
curl -s %BASE_URL%/auditoria/historial/%ID_REGISTRO%
echo.
pause

echo.
echo ========================================================================
echo                    TEST COMPLETE
echo ========================================================================
echo.
echo All endpoints tested!
echo Record ID: %ID_REGISTRO%
echo.
echo Next steps:
echo 1. Check MongoDB to verify data
echo 2. View OpenAPI docs at http://localhost:8000/docs
echo.
pause
