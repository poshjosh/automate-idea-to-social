# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Mount browser profile dir for use within docker.

## [0.1.2] - 2024-07-01

### Changed

- docker compose file to make environment variables overridable.

## [0.1.1] - 2024-06-21

### Fixed

- Bug which caused undetected chromedriver to crash when chrome version is mis-matched.

## [0.1.0] - 2024-06-09

### Added

- Secrets masking for log records.

## [0.0.7] - 2024-06-07

### Added 

- Language option.
- Automation events.

### Fixed

- Bug which caused blog agent to publish to wrong dir.

## [0.0.8] - 2024-06-01

### Added

- Dependency to [pyu v0.1.4](https://github.com/poshjosh/pyu/tree/v0.1.4)

## [0.0.7] - 2024-06-01

### Added

- CHANGELOG.md
- setup.py
- Containerization, using docker.

### Changed

- Directory structure.
- Updated run, run test scripts
