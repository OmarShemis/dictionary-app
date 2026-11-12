# Architecture

```mermaid
flowchart LR
Search --> WorkerThread
WorkerThread --> DictionaryAPI
DictionaryAPI --> FormattedResults
```

See the source modules and tests for implementation details. External model/API availability is independent of offline test success.
