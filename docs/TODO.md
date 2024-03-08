Add a kind of temp directory which should be git ignored
Save video link to a file for each agent, as necessary, then use it rather than the current environment variable `video.link`
Consider changing blog_updater to blog
  * Think of how to resolve `blog_updater/blog` which now becomes `blog/blog`
All nested variables in env and configs
Change config.app.name to self.app.name in agent yaml files
When we successfully find an element. We should update the xpath
through which the element was found.
Use a working.dir
Make cookie location a variable
Allow variables in yaml ${}
  * Process all ${} variables at app load time
  * Document variables in yaml
    * There are 2 types ${} processed at app load time and @ processed at time of use

Allow variables in .env file


Handle pictory file-download:
  - Auto it - https://www.quora.com/I-am-trying-to-automate-uploading-a-file-from-a-Finder-window-and-close-the-window-afterwards-in-Mac-OS-using-Selenium-WebDriver-How-do-I-do-that
  - https://www.reddit.com/r/learnpython/comments/qw6aze/solved_how_to_close_a_windows_file_explorer/

Don't log passwords
  - Implement app property which gives option to not log while in action handler.

Hide from servers, the fact that our browser is automated
   - Consider using [Undetected Chromedriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver)