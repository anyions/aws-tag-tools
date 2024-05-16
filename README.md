# AWS-Tag-Tools

![PyPI - Version](https://img.shields.io/pypi/v/aws-tag-tools?color=a1b858&label=)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/aws-tag-tools)
![PYPI License](https://img.shields.io/pypi/l/aws-tag-tools)
![Static Badge](https://img.shields.io/badge/author-AnyIons-violet)

**A bulk management tool for the tags of AWS resources**

- Support multiple services/resources
- Faster operations using multiple processes

## Usage

### Install

```bash
pip install -U aws-tag-tools
```

### Command

```shell
# tag resources use tag 'tag-key':'tag-value', ignore if 'tag-key' is existed in resource tags
awstt --key tag-key --value tag-value
# tag resources use tag 'tag-key':'tag-value', overwrite the tag value with 'tag-value' if 'tag-key' is existed
awstt --key tag-key --value tag-value --overwrite
# tag resources in regions 'us-east-1' and 'us-west-1'
awstt --key tag-key --value tag-value --regions us-east-1,us-west-1
# use credentials profile 'tagger' to execute
awstt --key tag-key --value tag-value --profile tagger
# tag resources in AWS China Regions ('aws-cn')
awstt --key tag-key --value tag-value --partition aws-cn
# list all supported resources
awstt --list-services
# show help
awstt --help
```

#### Options

| option                              | description                                                               |
|-------------------------------------|---------------------------------------------------------------------------|
| -h, --help                          | show this help message and exit                                           |
| --key KEY                           | the key of tag will be tagged to resources                                |
| --value VALUE                       | the value of tag will be tagged to resources                              |
| --overwrite                         | whether to overwrite exists tag when key is existed<br>default to `False` |
| --regions REGIONS                   | the AWS regions to execute actions<br>will auto detect if not set         |
| --profile PROFILE                   | the name of AWS credentials profile to use                                |
| --partition {aws,aws-cn,aws-us-gov} | the partition to execute actions<br/>default to `'aws'`                   |
| --list-services                     | list all supported services by this tool and exit                         |

> [!NOTE]
> use `awstt --help` to get more details

## TODO

- [] Support for Untagging Resources
- [] Deploying to Lambda with CloudFormation
- [] Tag or untag resources with specified type(s）
- [] Tag or untag resources with specified ARN(s)

## License

[MIT](./LICENSE) License © 2020 [AnyIons](https://github.com/anyions)
