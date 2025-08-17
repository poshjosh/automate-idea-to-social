# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Move the resources directory to within the application directory.
- The default output directory. Also, create it if need.

## [0.3.1] - 2025-08-16

### Added

- Run arg `--save-screens` (`-ss`), a string to specify when screenshots and web pages 
should be saved. Possible values are: `always|never|onerror|onfailure|onsuccess|onstart`.
The default value is `onerror`.

### Changed

- Mask secrets only when in production mode.

## [0.3.0] - 2025-08-15

### Added

- Action: `ask_for_help` so agents can ask for help. ([See docs](./docs/actions.md))
- Run arg `--browser-mode` (`-bm`), with possible values `visible|undetected`.

### Changed

- Run args/options may now be passed via ENV variables, e.g. `RUN_ARGS="--browser-mode undetected"`.
- Improve parsing of config action signatures and others.
- Make config extension applicable to all config types.
- Separate browser config from app config.

## [0.2.5] - 2025-08-11

### CHANGED

- Python (in Dockerfile) to v3.9.23-bullseye
- Blog app (automate-jamstack) to v0.1.6

### Added

- Environment variable `BLOG_APP_VERSION` to specify the blog app version to use.
- Extension of configs, using the `extends` keyword.
- Ordering to configs which are merged
- Option to specify external config dir
- Bump blog app to v0.1.5
- Publishing multiple translations of blog posts.
- Turkish and Ukrainian to supported languages.
- Dynamic generation of language options in the UI.

### Changed

- Increase blog update timeout to 60 minutes.
- SUBTITLES_OUTPUT_LANGUAGES to TRANSLATION_OUTPUT_LANGUAGE_CODES

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
