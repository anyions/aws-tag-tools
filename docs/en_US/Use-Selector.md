# Using Selectors

AWS Tag Tools supports using [JMESPath](https://www.jmespath.org) expression as selectors to filter resources or select
tags.

When used as a tag selector, the root element of the selector is `tags`, and the structure of the `tags` dictionary is
as follows:

```json lines
[
  {
    "key": "key_string_1",
    "name": "value_string_1"
  },
  {
    "key": "key_string_2",
    "name": "value_string_2"
  },
  ...
]
```

The result of executing the selector may be `None`, `List[str]`, `List[Dict]`, or `Dict`. A tag is only selected when it
meets the following conditions:

- When the result is `List[str]`, all values in the list are used.
- When the result is `List[Dict]`, the non-empty element values with the key `'key'` in each dictionary in the list are
  used as tag keys.
- When the result is `Dict`, the non-empty value with the key `'key'` is used as the tag key.

When used as a resource selector, `tags` and `spec` can be used as filtering conditions. The `spec` dictionary is
different for each service, and you can refer to the [Spec Description](SPEC.md) for more details.

The result of the resource selector may be `None`, `List`, `str`, or `bool`. A resource is only selected when the `List`
or `str` is non-empty, or the `bool` value is `True`.

Resource selectors support stacking, meaning that the global selector will be appended to the selector for a specific
resource, and a resource is only considered selected when all conditions are met. For example:

```json lines
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

For RDS Clusters, the selector `"!(tags[?key == 'owner'])"` will be used to select any instances that do not have a tag
with the key `'owner'`.

For RDS Instances, the selectors `"!(tags[?key == 'owner'])"` and `"spec.Engine == 'mysql'"` will be used to select any
instances that do not have a tag with the key `'owner'` and have the `Engine` parameter set to `'mysql'` in the spec.