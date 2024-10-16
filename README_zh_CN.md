<div align="center">
# AWS Tag Tools: AWS 资源标签管理工具

![PyPI - Version](https://img.shields.io/pypi/v/aws-tag-tools?color=a1b858&style=for-the-badge)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/aws-tag-Tools?&style=for-the-badge)
![PyPI - License](https://img.shields.io/pypi/l/aws-tag-tools?color=&style=for-the-badge)
![Static Badge](https://img.shields.io/badge/author-AnyIons-violet?&style=for-the-badge)

<img src="docs/app.png" alt="awstt" />

[English](README.md) | 简体中文
</div>
<br />

## 关于

AWS Tag Tools 是一个功能强大且通用的工具,旨在管理各种 AWS
服务中的资源标签。使用此工具,您可以轻松地在单个命令中为多个区域中的多个资源设置或取消设置标签,或者使用该工具根据标签键/值或其他规范 (
如 EC2 实例类型) 跨多个区域批量列出匹配的资源。

## 特性

- 支持在命令行界面或作为 AWS Lambda 函数使用。
- 支持多种 AWS 服务，请参阅支持的[服务列表](docs/zh_CN/Supported-Services.md)获取详细列表。
- 支持 AWS 分区：'aws'、'aws-gov' 和 'aws-cn'。
- 使用 [JMESPath](https://jmespath.org/) 表达式选择或过滤资源，请参阅[使用选择器](docs/zh_CN/Use-Selector.md)。
- 支持为键或值使用 Python 表达式，请参阅使用[参数表达式](docs/zh_CN/Use-Expression.md)。
- 如果键已存在则忽略标签，强制覆盖时将记录原始值。
- 取消设置标签时记录原始键/值。
- 按需将执行过程输出到日志文件。

## 使用方法

### 先决条件

- 需要 Python 3.11 或更高版本。
- 如果未明确指定凭证信息，则需要配置 AWS CLI 凭证。
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
# 为所有区域中的任何支持的资源添加标签
awstt set --tag tagged_by=awstt
# 为 'us-east-1' 和 'us-west-1' 区域中的 EC2 实例添加两个标签: 'tagged_by=awstt' 和 'owner=AnyIons'
awstt set --tag tagged_by=awstt,owner=AnyIons --region us-east-1,us-west-1 --resource ec2:instance
# 从 'aws-cn' 分区中任何 VPC 上删除键为 ['tagged_by', 'owner'] 的标签,并使用命名的 AWS CLI 凭证配置文件
awstt unset --tag tagged_by,owner --resource arn:aws-cn:ec2:*:*:vpc/* --profile china
# 从具有 'Engine' 为 'mysql' 规范的 RDS 实例上删除键为 'owner' 的标签
awstt unset --tag owner --resource rds:instance --filter spec[?Engine=='mysql']
# 列出所有在 5 天前创建的具有键为 'created_at' 的标签的资源，通过将值与动态表达式进行比较
awstt list --filter tags[?key=='created_at' && value < '${(now() + timedelta(days=-5)).strftime('%Y-%m-%d_%H:%M:%S')}']
# 使用配置文件和 AK/SK 执行操作
awstt exec --config action.json --access_key YOUR_AWS_ACCESS_KEY_ID --access_key YOUR_AWS_SECRET_ACCESS_KEY
```

> [!TIP]
> 使用 `awstt --help` 获取更多详细信息

### 复杂场景

您可以使用 json 配置文件执行复杂的操作，例如强制在所有资源上设置 'owner=AnyIons' 标签，但不允许覆盖 EC2
实例的现有 'owner' 标签，并且同时仅在 RDS 上设置标签 'env=dev'。

参见示例 [action-set-example](examples/action-set.json) 和 [action-unset-example](examples/action-unset.json).

> [!WARNING]
> 尚不支持删除标签时使用资源目标标签选择器覆盖全局目标标签。例如：
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
> EBS 上的标签选择器 `"tags[?key=='owner' && value == 'aws-tag-tools'].key"` 不会生效, 所有键为 `'owner'` 的标签均会被删除。

## License

[MIT](./LICENSE) License © 2020 [AnyIons](https://github.com/anyions)