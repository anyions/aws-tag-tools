# JSON Configuration

AWS Tag Tools can perform complex operations using a JSON configuration file with the following format:

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

Parameter descriptions:

- action (string) - **[REQUIRED]** Operation instruction
    * "set" - Set tags
    * "unset" - Unset tags
    * "list" - List tags
- partition (string) - AWS partition, only supports `'aws'` | `'aws-cn'` | `'aws-gov'`
- regions (list) - List of regions for the operation, e.g., ['us-east-1', 'us-west-1']. If not specified, the operation
  will be performed across all supported regions based on the AWS service type
- tags (list) - List of tags, the content will be applied to all operated resources, you can specify the `'tags'`
  parameter for specific resources to add additional operations
    * When performing the `'set'` operation, use a dictionary type, formatted as `{'key': 'string', 'value': 'string'}`,
      the key-value content can use [expressions](Use-Expression.md)
    * When performing the `'unset'` operation, use a string type, which can be a tag key name
      or [tag selector](Use-Selector.md)
- filters (list) - Resource filter conditions, see [Using Selectors](Use-Selector.md). Currently, multiple conditions
  only support `and` operations.
- resources (list) - List of target resources, can **mix** `string` and `dict` types. If not specified, the operation
  will be performed on all resources of the [supported services](Supported-Services.md)
    * string - Can be a resource type or resource ARN, ARNs support using wildcards
    * dict - Formatted as `{ "target": "<string>", "tags": [ <tag_dict> | "<string>"], "force": false | true }`
        * target (string) - **[REQUIRED]** Resource type or resource ARN, ARNs support using wildcards
        * tags (list) - List of tags, when performing "set" or "list" operations, tags with the same key name as the
          current resource will override the global tag properties, "unset" does not yet support property overriding
        * filters (list) - Resource filter conditions, can be stacked with global resource filters.
        * force (bool) - Whether to overwrite existing tags with the same key name, defaults to not overwrite. When
          performing "set" and "unset" operations, the resource's property value takes precedence
- force (bool) - Whether to overwrite existing tags with the same key name, defaults to not overwrite
- credential (dict) <br/> AWS credential information
    * access_key (string) <br/> Access Key of AWS Credential
    * secret_key <br/> Secret Key of AWS Credential
    * profile <br/> Profile name of AWS Credential

> [!Caution]
> Using AK/SK (Access Key/Secret Key) in the configuration file may lead to privacy leaks or security risks. It is
> strongly recommended to pass credential information through environment variables or command-line parameters.
>
> Supported credential environment variables are
> * 'AWS_ACCESS_KEY_ID'
> * 'AWS_SECRET_ACCESS_KEY'
> * 'AWS_PROFILE'