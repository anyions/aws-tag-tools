## 1.0.0

### BREAKING CHANGE

- rewrite project to version 1.0.0

### Feat

- **tagger**: log original tags when untag
- *****: implement exec action
- *****: implement untag action
- **executor**: always show config in cli mode
- **cli**: help message of supported resources
- **thread**: handle tagger rate exceeded in batch mode
- **scanner**: support more resources
- **output**: set log level optional
- **scanner**: init account_id only when executing
- **tagger**: handle "rate exceed" when tagging
- *****: rewrite to new version 1.0.0

### Fix

- **scanner**: wrong element name of subnet
- **scanner**: wrong element name of lambda
- **scanner**: wrong list api of opensearch
- **util**: dict value of filtered tags
- **tagger**: filter tags with raw key name
- **config**: detect region with partition
- **scanner**: wrong resource type
- **scanner**: wrong categories
- **scanner**: aws-cn partition support
- **executor**: tagging with config file
- **scanner**: inconsistent name format
- **scanner**: duplicate scan s3 bucket

### Refactor

- **evals**: remove unused methods
- **thread**: exception messages
- **evals**: direct access to datetime methods
- **config**: lower string for action/partition/regions
- **scanner**: clean invalid code
- **scanner**: update hints for IDE
- **thread**: remove unused codes
- **registrable**: change shadowed param name
- *****: rename selector to filter
- **scanner**: rename cloudfront scanner
- **output**: style config console output
- **output**: console output with logging level
- **executor**: adjust progress bar style

### Perf

- **scanner**: init available regions when executed

## 0.1.1 (2024-05-16)

### Fix

- **scanner**: timeout for CloudFront

## 0.1.0 (2024-05-16)

### BREAKING CHANGE

- first public release

### Feat

- *****: init commit
