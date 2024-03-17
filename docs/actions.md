# Actions

Actions may be global, browser or element specific.

### Global actions

| Action                 | Argument type(s)              | Remarks                                           |
|------------------------|-------------------------------|---------------------------------------------------|
| wait                   | None                          |                                                   |
| get_newest_file_in_dir | str, int (directory, timeout) | Example: `get_newest_file_in_dir /path/to/dir 30` |

### Browser actions

| Action         | Argument type(s) | Remarks                       |
|----------------|------------------|-------------------------------|
| accept_alert   | int (timeout)    |                               |
| dismiss_alert  | int (timeout)    |                               |

### Element Actions

| Action                          | Argument type(s)                                                            | Remarks                               |
|---------------------------------|-----------------------------------------------------------------------------|---------------------------------------|
| click                           | None                                                                        | default action                        |
| click_and_hold                  | None                                                                        |                                       |
| click_and_hold_current_position | None                                                                        |                                       |
| get_text                        | None                                                                        |                                       |    
| enter_text                      | text                                                                        |                                       |
| is_displayed                    | None                                                                        |                                       |
| move_to_offset                  | str [center,top-left,top-right,bottom-right,bottom-left], int, int (pixels) | Example: `move_to_offset center -8 8` |
| move_to_element                 | None                                                                        |                                       |
| release                         | None                                                                        |                                       |
| run_stages                      | List[str] (stage names)                                                     |                                       |
