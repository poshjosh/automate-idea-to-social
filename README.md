# automate-idea-to-social

### Sample Input

### Automate generating and publishing content from ideas to social media.

Automation is done via agents. Each agent runs one or more stages. 
Each stage involves taking one or more actions. 

### Agents

See [Agents](./docs/agents.md)

### Events

See [Events](./docs/events.md)

### Actions

See [Actions](./docs/actions.md)

### Environment

- For a complete list of environment variables, see: [Environment](./docs/environment.md)

- For a complete list of run options, see [Run Options](docs/run-options.md).

### Installation

- To install, run the [shell/install.sh](shell/install.sh) script (_Run this script any time you update dependencies_).

### Quick Start

1. Install the app by running [shell/install.sh](shell/install.sh) in a command prompt.

2. Set required environment variables: For a full ist of environment variables, see [Environment](docs/environment.md).

3. Set the required run options: For a full list of run options, see [Run Options](docs/run-options.md). 
Run options may be provided in various ways and are resolved in the following order, from least to highest precedence:
   * Yaml file `run.config.yaml` in directory determined by the `CONFIG_DIR` environment variable (default `resources/config`).
   * Environment variables e.g: `RUN_ARGS="--agents twitter --browser-mode undetected"`
   * Passed as command line arguments e.g: `python3 aideas/web.py --agents twitter --browser-mode visible`

4. Run the app by running [shell/run.sh](shell/run.sh) in a command prompt.

### Development

- If you want to do some development or run tests, run the [shell/install.dev.sh](shell/install.dev.sh) script (only once).
- &#10060; &#9888; Do not update `requirements.txt` directly. Rather update `requirements.in` and run [shell/install.sh](shell/install.sh)
- &#9989; Update the [CHANGELOG.md](CHANGELOG.md) file, with your changes.

### Testing

- To run the tests, run the [shell/run.tests.sh](shell/run.tests.sh) script.