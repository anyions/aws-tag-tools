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
  "force": false | true,
  "credential": {
    "access_key": "<string>",
    "secret_key": "<string>",
    "profile": "<string>"
  }
}
```

参数说明：

- action (string) <br/> **[REQUIRED]** 操作指令
    * "set" - 设置标签
    * "unset" - 取消标签
    * "list" - 列出标签
- partition (string) <br/> AWS partition，仅支持 `'aws'` | `'aws-cn'` | `'aws-gov'`
- regions (list) <br/> 操作区域列表，如 ['us-east-1', 'us-west-1']。如果未指定区域，将按 AWS 服务类型在所有受支持的区域中执行操作
- tags (list) <br/> 标签列表，列表内容将对应用于所有被操作资源，可以为特定资源指定 `'tags'` 参数添加额外操作
    * 当执行 `'set'` 操作时，使用字典类型，格式为 `{'key': 'string', 'value': '
      string'}`，键值内容可以使用[计算式](Use-Expression.md)
    * 当执行 `'unset'` 操作时，使用字符串类型，字符串可以为标签键名或[标签选择器](Use-Selector.md)
- filters (list) <br/> 资源过滤条件，参见[使用选择器](Use-Selector.md)。当前多个条件仅支持 `and` 操作。
- resources (list) <br/> 目标资源列表，可以**混合**使用 `string` 或 `dict`
  两种类型。如果未指定，将在所有[受支持的服务](Supported-Services.md)资源上执行操作
    * string 类型 <br/> 可以为资源类型或资源 ARN，ARN 支持使用通配符
    * dict 类型 <br/> 格式为 `{ "target": "<string>", "tags": [ <tag_dict> | "<string>"], "force": false | true }`
        * target (string) <br/> **[REQUIRED]** 资源类型或资源 ARN，ARN 支持使用通配符
        * tags (list) <br/> 标签列表，当执行 "set" 或 "list" 操作时，当前资源键名相同的标签将覆盖全局标签属性，"unset"
          尚不支持属性覆盖
        * filters (list) <br/> 资源过滤条件，可以与全局资源过滤条件叠加。
        * force (bool) <br/> 是否覆盖键名存在的标签，默认为不覆盖。执行 "set" 和 "unset" 时优先使用资源的属性值进行操作
- force (bool) <br/> 是否覆盖键名存在的标签，默认为不覆盖
- credential (dict) <br/> AWS 凭证信息
    * access_key (string) <br/> AWS 凭证 Access Key
    * secret_key <br/> AWS 凭证 Secret Key
    * profile <br/> AWS 凭证 Profile

> [!Caution]
> 在配置文件中使用 AK/SK 可能导致隐私泄露或产生安全风险，强烈建议使用凭证环境变量或命令行参数传入凭证信息
>
> 凭证环境变量支持
> * 'AWS_ACCESS_KEY_ID'
> * 'AWS_SECRET_ACCESS_KEY'
> * 'AWS_PROFILE'