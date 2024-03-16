### Tips & Tricks

- Disable 2-factor authentication on your accounts.
- Use chrome Profile

### Requirements

- Add `.env` file to your path.
- No need to add `blog.env` file to your path

#### python requirements:

See `src/python/main/requirements.txt`

#### other requirements:

- docker
- git

### Directory Structure

Run the app with the working directory set to `${PROJECT_DIR}/src/python/main`
RUN tests with the working directory set to `${PROJECT_DIR}/src`
  - Tests need to be able to access both test and main sources.

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
