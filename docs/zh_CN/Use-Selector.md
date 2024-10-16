# 使用选择器

AWS Tag Tools 支持使用 [JMESPath](https://www.jmespath.org) 表达式作为选择器来过滤资源或选择标签。

当作为标签选择器使用时，选择器根元素为 `tags`，tags 字典结构如下：

```json
[
  {
    "key": "key_string_1",
    "name": "value_string_1"
  },
  {
    "key": "key_string_2",
    "name": "value_string_2"
  }
]
```

选择器执行结果可能为 `None`、`List[str]`、`List[Dict]` 或 `Dict`，仅当满足以下情况时标签才被选中：

- 当结果为 `List[str]` 时，使用列表中的所有值
- 当结果为 `List[Dict]` 时，使用列表中每个字典中键为 `'key'` 的非空元素值为标签键
- 当结果为 `Dict` 时，使用字典键为 `'key'` 的非空值为标签键

当作为资源选择器使用时，可以使用 `tags` 或 `spec` 作为过滤条件，`spec`
字典每个服务均不相同，具体参考 [规格说明](SPEC.md)。

资源选择器返回结果可能为 `None`、`List`、`str` 或 `bool`，仅当 `List` 或 `str` 非空或 `bool` 值为 `True` 时才被选中。

资源选择器支持叠加，即全局选择器会附加到特定资源的选择器之上，且仅当所有条件满足时才视为资源被选中。例如：

```json
{
  "filter": "!(tags[?key == 'owner'])",
  "resources": [
    "rds:cluster",
    {
      "target": "rds:instance",
      "filter": "spec.Engine == 'mysql'"
    }
  ]
}
```

对于 RDS Clusters，将使用 `"!(tags[?key == 'owner'])"` 作为选择器，选择任何不具备标签键为 `'owner'` 的实例。

对于 RDS Instances，将使用  `"!(tags[?key == 'owner'])"` 和 `"spec.Engine == 'mysql'"`
作为选择器，选择任何不具备标签键为 `'owner'` 且规格参数中 `Engine` 类型为 `'mysql'` 的实例。 