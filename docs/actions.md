# Actions

Actions may be global, browser or element specific.

### Global actions

| Action                 | Argument type(s)                     | Remarks                                           |
|------------------------|--------------------------------------|---------------------------------------------------|
| get_file_content       | str (file path)                      |                                                   |
| get_files              |                                      |                                                   |
| get_first_file         | str, str (file path, file extension) |                                                   |
| get_newest_file_in_dir | str, int (directory, timeout)        | Example: `get_newest_file_in_dir /path/to/dir 30` |
| log                    | str, str (log level, log message)    |                                                   |
| save_file              | str                                  |                                                   |
| save_to_file           | str                                  |                                                   |
| starts_with            |                                      |                                                   |
| wait                   | None                                 |                                                   |

### Browser actions

| Action         | Argument type(s)        | Remarks |
|----------------|-------------------------|---------|
| accept_alert   | int (timeout)           |         |
| delete_cookies | none                    |         |
| disable_cursor | none                    |         |
| dismiss_alert  | int (timeout)           |         |
| enable_cursor  | none                    |         |
| execute_script | str (javascript)        |         |
| move_by_offset | int, int (px, px)       |         |
| refresh        | None                    |         |

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
