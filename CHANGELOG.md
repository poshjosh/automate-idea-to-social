# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.3] - 2025-02-13

### Changed

- No longer add `#shorts` to youtube video title.
- Use text-title as input-file name where applicable.
- Succeed if there are failures marked to be ignored.
- Use `OrderdDict` for `ResultSet`.

### Fixed

- Bug caused by unquoted arg for translation agent.

## [0.2.2] - 2024-12-26

### Added

- Option to specify browser version to use

### Changed

- Properly stop tasks
- Use dynamic form generation, based on the variables set in agent's config.
- Properly use jinja templates

## [0.2.1] - 2024-12-13

### Added

- Extensive result set tests
- Improve display of task HTML (Display a short status per agent)
- Environment variable 'APP_PORT' and fix deployment as 'WEB_APP' to docker.
- Environment variable 'WEB_APP', to enable running as a web app.
- Tasks, and async processing of agent tasks.
- Error results to returned results.
- Sorting of agent names displayed on web page according to `sort-order`
- `CONTENT_DIR` and deprecate `INPUT_DIR`

## [0.2.0] - 2024-12-09

### Added

- Use `agent-type` and `agent-tags` to customize agent work flow.
- Replace VIDEO_DESCRIPTION with VIDEO_DESCRIPTION_FULL
- Replace VIDEO_INPUT_TEXT with VIDEO_DESCRIPTION
- Add run_config which may be provided via yaml file, `sys.argv` or `request.form`
- Transform into web app using flask.
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
