# Events

Events are synchronously executed.

| Events    | Default value | Possible values                         | Remarks |
|-----------|---------------|-----------------------------------------|---------|
| onstart   | continue      | continue, fail, run_stages, wait        |         |
| onerror   | fail          | continue, fail, retry, run_stages, wait |         |
| onsuccess | continue      | continue, fail, retry, run_stages, wait |         |


| Event action | Events             | Default value | Remarks                     |
|--------------|--------------------|---------------|-----------------------------|
| continue     | all                |               |                             |
| fail         | all                |               |                             |
| retry        | onerror, onsuccess |               |                             |
| run_stages   | all                |               |                             |
| wait         | all                |               | [see Actions](./actions.md) | 

```
Given: `current agent` = instagram and current stage = `login-via-fb`
Event: `run_stages facebook.login` will run the `login` stage of the `facebook` agent.
Event: `run_stages login` will run the `login` stage of the current (i.e. `instagram`) agent.
```
