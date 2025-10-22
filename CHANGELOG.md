# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added (v2.1.0)
- **Typed Event Schema**: Event TypedDict with `ts`, `level`, `job_id`, `type`, `step`, `data` fields
- **ISO8601 Timestamps**: All events include UTC timestamps with 'Z' suffix
- **LLM Tracking Events**: `llm.request` and `llm.response` events for observability
- **File Operation Events**: `file.written` events with path, SHA256, wrote status, and reason
- **Cache Events**: `cache.hit` and `cache.miss` events for cache observability
- **Resume-from-Failure**: `run_dag(resume=True)` skips completed steps based on `events.jsonl`
- **Deterministic Caching**: SHA256-based cache keys with code version tracking
- **Cache Integration**: All orchestrator steps (architect, builder, docs, qa) use caching
- **Event Filtering**: Filter events by `level` (INFO/WARN/ERROR) in addition to type and step
- **Manifest Resume Fields**: `completed_steps` and `pending_steps` tracking in `manifest.json`
- **Comprehensive Tests**: Resume and cache test suites with integration scenarios

### Changed
- **FileStore Return Type**: `safe_write()` now returns `WriteResult` dict with `{path, sha256, size_bytes, wrote, reason}`
- **Event Field Rename**: `timestamp` → `ts` for consistency
- **Event Validation**: `emit()` now validates required fields (`type`, `job_id`)
- **Cache Storage**: Responses cached in `runs/<job_id>/.cache/<key>.json`
- **Git Versioning**: Cache keys include git commit or source file hash for automatic invalidation

### Fixed
- FileStore idempotency: Duplicate writes correctly return `wrote=False` and `reason="nochange"`
- Event emission: All file operations now emit `file.written` events

## [2.0.0] - 2025-10-15

### Added
- DAG-based parallel execution engine
- Provider abstraction layer (Ollama, OpenAI, Anthropic, MLX)
- Event logging system with ND-JSON format
- Run manifest with comprehensive metadata
- Safe file I/O with SHA256 hashing and locking
- CLI with `run` and `show` commands
- Pydantic v2 models for type safety
- Async/await throughout for concurrency
- Golden tests for output validation

### Changed
- Replaced linear execution with DAG-based orchestration
- Migrated from sequential to parallel step execution

## [1.0.0] - 2025-09-01

### Added
- Initial release with basic orchestration
- CrewAI integration
- Simple agent workflow

[Unreleased]: https://github.com/USER/unified_orchestrator/compare/v2.0.0...HEAD
[2.0.0]: https://github.com/USER/unified_orchestrator/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/USER/unified_orchestrator/releases/tag/v1.0.0
