## TODO

Allow nested variables in env and configs

When we successfully find an element. We should update
the xpath through which the element was found.

Use a working.dir ???

!!! Allow variables in .env file -> PROBABLY NOT!!!

Document variables in yaml: `self`, `context` and `results`

## Misc


For ResultSet introduce composition and de-composition
from and to dict. Use this when saving results to disc.
Example de-composition:

```python
    def decompose(self) -> dict[str, RESULT]:
        output = {}
        for key in self.__results.keys():
            value = self.__results[key]
            output[key] = value.results() if isinstance(value, ResultSet) else value
        return output
```

Checkout https://github.com/Mozilla-Ocho/llamafile

Handle file-download:
- Auto it - https://www.quora.com/I-am-trying-to-automate-uploading-a-file-from-a-Finder-window-and-close-the-window-afterwards-in-Mac-OS-using-Selenium-WebDriver-How-do-I-do-that
- https://www.reddit.com/r/learnpython/comments/qw6aze/solved_how_to_close_a_windows_file_explorer/

Don't log passwords
- Implement app property which gives option to not log while in action handler.

Hide from servers, the fact that our browser is automated
- Consider using [Undetected Chromedriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver)