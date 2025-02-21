# Actions

Actions may be global, browser or element specific.

### Global actions

| Action                 | Argument type(s)                            | Remarks                                                                         |
|------------------------|---------------------------------------------|---------------------------------------------------------------------------------|
| eval                   | str (python code to evaluate)               | `importlib` will be automatically imported before each eval                     |
| exec                   | str (python code to execute)                |                                                                                 |
| get_file_content       | str (file path)                             |                                                                                 |
| get_files              |                                             |                                                                                 |
| get_first_file         | str, str (file path, file extension)        |                                                                                 |
| get_newest_file_in_dir | str, int (directory, timeout)               | Example: `get_newest_file_in_dir /path/to/dir 30`                               |
| log                    | str, str (log level, log message)           |                                                                                 |
| run_subprocess         | str with multiple values separated by space | subprocess.run with the provided str values as args                             |
| save_file              | str                                         | Save arg[0] (file) to the action's result dir, app input dir and user input dir |
| save_text              | str                                         | Save arg[0] (text) to the action's result dir, app input dir and user input dir |
| set_context_values     | str (key-value pairs)                       | Example `set_context_values k0=v0 k1="value with space"`                        |
| starts_with            |                                             |                                                                                 |
| wait                   | None                                        |                                                                                 |

### Browser actions

| Action          | Argument type(s)  | Remarks |
|-----------------|-------------------|---------|
| accept_alert    | int (timeout)     |         |
| browse_to       | str (url/link)    |         |
| delete_cookies  | none              |         |
| disable_cursor  | none              |         |
| dismiss_alert   | int (timeout)     |         |
| enable_cursor   | none              |         |
| execute_script  | str (javascript)  |         |
| move_by_offset  | int, int (px, px) |         |
| refresh         | None              |         |
| save_screenshot | None              |         |
| save_webpage    | None              |         |

### Element Actions

| Action                          | Argument type(s)                                                          | Remarks                                   |
|---------------------------------|---------------------------------------------------------------------------|-------------------------------------------|
| clear_text                      | None                                                                      |                                           |
| click                           | bool (click on element, true by default)                                  | default action                            |
| click_and_hold                  | None                                                                      |                                           |
| click_and_hold_current_position | None                                                                      |                                           |
| enter                           | None                                                                      |                                           |
| enter_text                      | text                                                                      |                                           |
| execute_script_on               | str (javascript)                                                          | execute the script on the current element |
| get_attribute                   | str (attribute name)                                                      |                                           |
| get_text                        | None                                                                      |                                           |    
| is_displayed                    | None                                                                      |                                           |
| move_to_element                 | None                                                                      |                                           |
| move_to_element_offset          | str [center,top-left,top-right,bottom-right,bottom-left], int, int [px,%] | Example: `move_to_offset center -8 8`     |
| release                         | None                                                                      |                                           |
| run_stages                      | List[str] (stage names)                                                   |                                           |
| send_keys                       | text                                                                      |                                           |
