<div align="center">

# AWS Tag Tools

AWS 资源的统一标签管理器

![PyPI - Version](https://img.shields.io/pypi/v/aws-tag-tools?color=a1b858&style=for-the-badge)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/aws-tag-Tools?&style=for-the-badge)
![PyPI - License](https://img.shields.io/pypi/l/aws-tag-tools?color=&style=for-the-badge)
![Static Badge](https://img.shields.io/badge/author-AnyIons-violet?&style=for-the-badge)

<img src="docs/app.png" alt="awstt" />

[![English](https://img.shields.io/badge/English-d9d9d9?style=for-the-badge)](README.md) ![简体中文](https://img.shields.io/badge/中文介绍-454545?style=for-the-badge)

</div>

<br />

## 概述

AWS Tag Tools (AWSTT) 是一款功能强大且通用的工具，旨通过统一的操作管理 AWS 服务的资源标签。

使用该工具，您可以通过单一命令在多个区域轻松设置或取消多个资源的标签，或根据标签键/值以及资源特性（如 EC2 实例类型）批量列出匹配的资源。

## 特性

- 支持命令行界面 (CLI) 或 AWS Lambda 函数两种使用方式。
- 支持多种 AWS 服务，详细列表请查看[支持的服务](docs/en_US/Supported-Services.md)。
- 支持 AWS 分区: 'aws'、'aws-gov' 和 'aws-cn'。
- 使用 [JMESPath](https://jmespath.org/) 表达式过滤或选择资源，详见[使用选择器](docs/en_US/Use-Selector.md)。
- 支持对键或值使用 Python 表达式，详见[使用表达式](docs/en_US/Use-Expression.md)。
- 可选择忽略已存在键的标签或在强制覆盖时自动记录原始值。
- 取消标签时自动记录原始键/值。
- 可选择将日志信息记录到文件。

## 使用方法

### 前提条件

- 需要 Python 3.11 或更高版本。
- 如果未明确指定凭证信息（如 AK/SK 或 profile），则需要配置 AWS CLI 凭证。
- 具有指定 AWS 服务权限的 IAM 角色。例如，要为 Amazon EC2 实例添加标签，您必须具有以下权限:
    - ec2:DescribeInstances
    - ec2:CreateTags
    - tag:TagResource

### 安装

```bash
pip install -U aws-tag-tools
```

### 命令

```shell
# 为所有区域中的任何支持的资源添加标签 'tagged_by=awstt'
awstt set --tag tagged_by=awstt
# 为 'us-east-1' 和 'us-west-1' 区域中的 EC2 实例添加两个标签: 'tagged_by=awstt' 和 'owner=AnyIons'
awstt set --tag tagged_by=awstt,owner=AnyIons --region us-east-1,us-west-1 --resource ec2:instance
# 使用名为 'china' 的 AWS CLI 凭证配置文件,从 'aws-cn' 分区中的任何 VPC 取消标签键为 'tagged_by' 和 'owner' 的标签
awstt unset --tag tagged_by,owner --resource arn:aws-cn:ec2:*:*:vpc/* --profile china
# 从 'Engine' 为 'mysql' 的 RDS 实例中取消标签键为 'owner' 的标签
awstt unset --tag owner --resource rds:instance --filter spec[?Engine=='mysql']
# 列出所有在 5 天前创建且标签键为 'created_at' 的资源,通过将值与动态表达式进行比较
awstt list --filter tags[?key=='created_at' && value < '${(now() + timedelta(days=-5)).strftime('%Y-%m-%d_%H:%M:%S')}']
# 使用配置文件和 AK/SK 执行操作
awstt exec --config action.json --access_key YOUR_AWS_ACCESS_KEY_ID --access_key YOUR_AWS_SECRET_ACCESS_KEY
```

> [!TIP]
> 使用 `awstt --help` 获取更多详细信息

### 复杂用法

您可以使用 [JSON 配置文件](docs/zh_CN/JSON-Config.md)进行复杂操作，例如强制为所有资源添加 `owner=AnyIons` 标签，但不允许覆盖
EC2 实例上已存在的 `owner`
标签，与此同时仅为 RDS 资源添加 `env=dev` 标签。

请参阅 [action-set-example](examples/action-set.json) 和 [action-unset-example](examples/action-unset.json)。

> [!WARNING]
> 目前还不支持进行标签删除时使用特定的资源标签选择器覆盖全局标签。例如:
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
> 此标签选择器 `"tags[?key=='owner' && value == 'aws-tag-tools'].key"` 将不会生效，所有键为 `'owner'` 的标签都将被取消。

## 许可证

[MIT](./LICENSE) 许可证 © 2020 [AnyIons](https://github.com/anyions)