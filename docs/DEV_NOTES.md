### Directory Structure

Run the app with the working directory set to `${PROJECT_DIR}/src`

Run tests with the working directory set to `${PROJECT_DIR}/src`
- Tests need to be able to access both test and main sources.

Agents use yaml configurations in `${PROJECT_DIR}/src/aideas/config/agent`

### Run args

Each run argument is represented as a form field. This makes it possible
to provide the value via a html form. The form fields are located at:
`${PROJECT_DIR}/src/aideas/templates/automate/form/`



### Tips & Tricks

- Videos with less than 150 words are less than one minute long. 

- Disable 2-factor authentication on your accounts.

- Use chrome Profile

- Use `send_keys` (which sends the chars one by one) rather than `enter_text`
Do this for websites which go the extra mile to detect bots and automated software

- Use undetected Chrome browser by adding `browser.chrome.undetected: true` 
to your agent's configuration.


### Requirements

- Add `.env` file to your path.
- No need to add `blog.env` file to your path

#### python requirements:

See `src/python/main/requirements.txt`

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
