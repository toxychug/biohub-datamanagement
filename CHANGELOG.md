# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-07-19

### Added
- Initial release of BioHub Change Management & Audit Service
- MongoDB audit trail storage (immutable records)
- REST API endpoints for audit history, metadata, and sensitivity
- Approval workflow state machine
- Kafka consumer integration
- Mock Kafka simulator for development
- Redis caching layer with in-memory fallback
- Web-based mock data input form
- Comprehensive API documentation (Swagger/OpenAPI)
- Docker and docker-compose support
- GitHub Actions CI/CD pipeline
- Pytest unit tests

### Features
- `/auditoria/historial/{id_registro}` - Change history
- `/auditoria/metadatos/{id_registro}` - Latest metadata
- `/auditoria/sensibilidad/{id_registro}` - Sensitivity classification
- `/aprobacion/{id_registro}` - Approval status
- `/aprobacion/actualizar` - Update approval workflow
- `/dev/simulate` - Mock Kafka event injection
- `/ui/mock-input.html` - Interactive record input form
- `/health` - Service health check

### Technical Stack
- FastAPI 0.100+
- Motor (async MongoDB)
- aiokafka (async Kafka)
- Redis (optional caching)
- Alpine.js (frontend)

## [Unreleased]

### Planned
- Batch record import API
- Advanced filtering and search
- Audit trail export (CSV, JSON)
- Real-time WebSocket updates
- Database replication configuration
- Kubernetes deployment manifests
- API rate limiting

---

For detailed API documentation, visit `/docs` when running the service.
