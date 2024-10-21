<div align="center">

# AWS Tag Tools

The Unified Tag Manager for AWS Resources

![PyPI - Version](https://img.shields.io/pypi/v/aws-tag-tools?color=a1b858&style=for-the-badge)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/aws-tag-Tools?&style=for-the-badge)
![PyPI - License](https://img.shields.io/pypi/l/aws-tag-tools?color=&style=for-the-badge)
![Static Badge](https://img.shields.io/badge/author-AnyIons-violet?&style=for-the-badge)

<img src="docs/app.png" alt="awstt" />

![English](https://img.shields.io/badge/English-454545?style=for-the-badge) [![简体中文](https://img.shields.io/badge/中文介绍-d9d9d9?style=for-the-badge)](README_zh_CN.md)

</div>

<br />

## Overview

AWS Tag Tools (AWSTT) is a powerful and versatile tool designed to manage resource tags of AWS services through a
unified operation.

With this tool, you can easily set or unset tags for multiple resources across multiple regions with a single command,
or list resources in bulk matching specific tag keys/values and resource attributes (e.g., EC2 instance types).

## Features

- Supports both command-line interface (CLI) and AWS Lambda function.
- Supports various AWS services, see the detailed list in [Supported Services](docs/en_US/Supported-Services.md).
- Supports AWS partitions: 'aws', 'aws-gov', and 'aws-cn'.
- Use [JMESPath](https://jmespath.org/) expressions to filter or select resources,
  see [Using Selectors](docs/en_US/Use-Selector.md).
- Support using Python expressions for keys or values, see [Using Expressions](docs/en_US/Use-Expression.md).
- Option to ignore existing tags or automatically record original values when force overwriting.
- Automatically record original key/values when unsetting tags.
- Option to log information to a file.

## Usage

### Prerequisites

- Python 3.11 or higher is required.
- If not explicitly specifying credentials (e.g., AK/SK or profile), AWS CLI credentials must be configured.
- IAM role with permissions for the specified AWS services. For example, to add tags to Amazon EC2 instances, you
  must have the following permissions:
    - ec2:DescribeInstances
    - ec2:CreateTags
    - tag:TagResource

### Installation

```bash
pip install -U aws-tag-tools
```

### Commands

```shell
# Add the tag 'tagged_by=awstt' to any supported resources across all regions
awstt set --tag tagged_by=awstt
# Add two tags 'tagged_by=awstt' and 'owner=AnyIons' to EC2 instances in 'us-east-1' and 'us-west-1' regions
awstt set --tag tagged_by=awstt,owner=AnyIons --region us-east-1,us-west-1 --resource ec2:instance
# Using the AWS CLI credential profile named 'china', unset tags with keys 'tagged_by' and 'owner' from any VPCs in the 'aws-cn' partition
awstt unset --tag tagged_by,owner --resource arn:aws-cn:ec2:*:*:vpc/* --profile china
# Unset tags with key 'owner' from RDS instances with 'Engine' as 'mysql'
awstt unset --tag owner --resource rds:instance --filter spec[?Engine=='mysql']
# List resources created 5 days ago with tag key 'created_at', comparing the value with a dynamic expression
awstt list --filter tags[?key=='created_at' && value < '${(now() + timedelta(days=-5)).strftime('%Y-%m-%d_%H:%M:%S')}']
# Execute operations using a configuration file and AK/SK
awstt exec --config action.json --access_key YOUR_AWS_ACCESS_KEY_ID --access_key YOUR_AWS_SECRET_ACCESS_KEY
```

> [!TIP]
> Use `awstt --help` for more detailed information

### Advanced Usage

You can use a [JSON configuration file](docs/en_US/JSON-Config.md) for complex operations, such as adding the
tag `owner=AnyIons` to all
resources, but not allowing overwriting existing `owner` tags on EC2 instances, while also adding the tag `env=dev` only
for RDS resources.

Please refer to [action-set-example](examples/action-set.json) and [action-unset-example](examples/action-unset.json).

> [!WARNING]
> Currently, it does not support overriding global tags with specific resource tag selectors when unsetting tags. For
> example:
>
> ```json
> {
>   "tags": [
>     "owner"
>   ],
>   "resources": [
>     {
>       "target": "arn:aws:ec2:*:*:volume/*",
>       "tags": [
>         "tags[?key=='owner' && value == 'aws-tag-tools'].key"
>       ]
>     }
>   ]
> } 
> ```
> This tag selector `"tags[?key=='owner' && value == 'aws-tag-tools'].key"` will not take effect, and all tags with the
> key `'owner'` will be unset.

## License

[MIT](./LICENSE) © 2020 [AnyIons](https://github.com/anyions)