# Actions

Actions may be global, browser or element specific.

### Global actions

| Action | Argument type(s) | Remarks |
|--------|------------------|---------|
| wait   | None             |         |

### Browser actions

| Action         | Argument type(s)  | Remarks                       |
|----------------|-------------------|-------------------------------|
| accept_alert   | None              |                               |
| dismiss_alert  | None              |                               |

### Element Actions

| Action                          | Argument type(s)  | Remarks                       |
|---------------------------------|-------------------|-------------------------------|
| click                           | None              | default action                |
| click_and_hold                  | None              |                               |
| click_and_hold_current_position | None              |                               |
| get_text                        | None              |                               |    
| enter_text                      | text              |                               |
| move_to_center_offset           | int, int (pixels) | Example: `move_to_offset 8 8` |
| move_to_element                 | None              |                               |
| release                         | None              |                               |
