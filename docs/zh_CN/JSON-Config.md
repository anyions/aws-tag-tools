# JSON 配置

AWS Tag Tools 可以使用 JSON 配置文件进行复杂操作，格式如下：

```pycon
{
  "action": "set" | "unset" | "list",
  "partition": "<string>",
  "regions": [
    "<string>"
  ],
  "tags": [ <tag_dict> | "<string>" ],
  "filters": [ "<string>" ],
  "resources": [ "<string>" | <resource_dict> ],
  "force": false | true
}
```

参数说明：

- action (string) - **[REQUIRED]** 操作指令
    * "set" - 设置标签
    * "unset" - 取消标签
    * "list" - 列出标签
- partition (string) - AWS partition，仅支持 `'aws'` | `'aws-cn'` | `'aws-gov'`
- regions (list) - 操作区域列表，如 ['us-east-1', 'us-west-1']。如果未指定区域，将按 AWS 服务类型在所有受支持的区域中执行操作
- tags (list) - 标签列表，列表内容将对应用于所有被操作资源，可以为特定资源指定 `'tags'` 参数添加额外操作
    * 当执行 `'set'` 操作时，使用字典类型，格式为 `{'key': 'string', 'value': '
      string'}`，键值内容可以使用[计算式](Use-Expression.md)
    * 当执行 `'unset'` 操作时，使用字符串类型，字符串可以为标签键名或[标签选择器](Use-Selector.md)
- filters (list) - 资源过滤条件，参见[使用选择器](Use-Selector.md)。当前多个条件仅支持 `and` 操作。
- resources (list) - 目标资源列表，可以**混合**使用 `string` 或 `dict`
  两种类型。如果未指定，将在所有[受支持的服务](Supported-Services.md)资源上执行操作
    * string - 可以为资源类型或资源 ARN，ARN 支持使用通配符
    * dict - 格式为 `{ "target": "<string>", "tags": [ <tag_dict> | "<string>"], "force": false | true }`
        * target (string) - **[REQUIRED]** 资源类型或资源 ARN，ARN 支持使用通配符
        * tags (list) - 标签列表，当执行 "set" 或 "list" 操作时，当前资源键名相同的标签将覆盖全局标签属性，"unset"
          尚不支持属性覆盖
        * filters (list) - 资源过滤条件，可以与全局资源过滤条件叠加。
        * force (bool) - 是否覆盖键名存在的标签，默认为不覆盖。执行 "set" 和 "unset" 时优先使用资源的属性值进行操作
- force (bool) - 是否覆盖键名存在的标签，默认为不覆盖
