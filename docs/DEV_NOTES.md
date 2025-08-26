### Directory Structure

Run the app with the working directory set to `${PROJECT_DIR}/src/aideas`

Run tests with the working directory set to `${PROJECT_DIR}/src`
- Tests need to be able to access both test and main sources.

Agents use yaml configurations in `${PROJECT_DIR}/src/aideas/resources/config/agent`

### Run args

Each run argument is represented as a form field. This makes it possible
to provide the value via a html form. The form fields are located at:
`${PROJECT_DIR}/src/aideas/templates/automate/form/`

#### To introduce a new run arg

For example to introduce a new `bool` variable named `ignore-fools`, do the following:

- Add `IGNORE_FOOLS = 'ignore-fools'` to enum `src/aideas/app/config.RunArg`

- Specify `ignore-fools` in the config which will be run using that variable, e.g. in `src/resources/config/agent/fake.config.yml`:
```yaml
form-field-ignore-fools: $IGNORE_FOOLS 
```

- Add the appropriate form input HTML `ignore-fools.html` in `src/aideas/templates/automate/form`, e.g.:
```html
<label for="ignore-fools">Ignore fools</label>
<input type="checkbox" id="ignore-fools" name="ignore-fools" class="control" value="true"/>
```

- Add the value in:
  - `docs/run-options.md` 
  - `src/resources/config/run.config.yaml`
  - `src/test/resources/config/run.config.yaml`

### Tips & Tricks

- Disable 2-factor authentication on your accounts.

- Use chrome Profile

- Use `send_keys` (which sends the chars one by one) rather than `enter_text`
Do this for websites which go the extra mile to detect bots and automated software

- Use undetected Chrome browser by adding `browser-mode: undetected` 
to your agent's configuration.


### Requirements

#### python requirements:

See `src/aideas/requirements.txt`

#### other requirements:

- docker
- git

### Some Known Errors

On macos, if you encounter error: 

```
Error: “chromedriver” cannot be opened because the developer cannot be verified
```
Then run either of the following commands (not both):

```bash 
spctl --add --label 'Approved' chromedriver
xattr -d com.apple.quarantine chromedriver
```
See https://stackoverflow.com/questions/60362018/macos-catalinav-10-15-3-error-chromedriver-cannot-be-opened-because-the-de
