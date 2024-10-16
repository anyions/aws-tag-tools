# 支持服务列表

AWS Tag Tools 现在支持以下 AWS 服务，您可以使用类别名称或 ARN 模式执行操作。

在 ARN 模式中，可以使用 '\*' 来通配匹配 \<region\>、\<account-id\> 和 \<resource\>。例如:<br/>
'arn:aws:ec2:\*:\*:instance/*' 将匹配任何可用区域和账户中的所有 AWS EC2 实例。

> [!NOTE]
> AWS Tag Tools 暂不支持在 \<resource\> 中进行子项的通配匹配。

| Category Name           | AWS Service/Resource             | ARN Pattern                                                                                | Resource Format                                  |
|-------------------------|----------------------------------|--------------------------------------------------------------------------------------------|--------------------------------------------------|
| CloudFormation:Stack    | CloudFormation Stack             | arn:\<partition\>:cloudformation:\<region\>:\<account-id\>:stack/\<resource\>              | \<stack-name\>/\<stack-id\>                      |
| Cloudfront:Distribution | Cloudfront Distribution          | arn:\<partition\>:cloudfront::\<account-id\>:distribution/\<resource\>                     | \<distribution-id\>                              |
| CloudTrail              | CloudTrail                       | arn:\<partition\>:cloudtrail:\<region\>:\<account-id\>:trail/\<resource\>                  | \<trail-name\>                                   |
| CloudWatch:Alarm        | CloudWatch Alarm                 | arn:\<partition\>:cloudwatch:\<region\>:\<account-id\>:alarm:\<resource\>                  | \<alarm-name\>                                   |
| CloudWatch:LogGroup     | CloudWatch LogGroup              | arn:\<partition\>:logs:\<region\>:\<account-id\>:log-group:\<resource\>                    | \<log-group-name\>                               |
| CloudWatch:Rules        | CloudWatch Rules                 | arn:\<partition\>:events:\<region\>:\<account-id\>:rule/\<resource\>                       | \<rule-name\>                                    |
| DynamoDB:Table          | DynamoDB Table                   | arn:\<partition\>:dynamodb:\<region\>:\<account-id\>:table/\<resource\>                    | \<table-name\>                                   |
| EC2:AMI                 | Machine Images (AMI)             | arn:\<partition\>:ec2:\<region\>:\<account-id\>:image/\<resource\>                         | \<image-id\>                                     |
| EC2:AutoScaling         | AutoScaling Group                | arn:\<partition\>:autoscaling:\<region\>:\<account-id\>:autoScalingGroup:\<resource\>      | \<group-id\>:autoScalingGroupName/\<group-name\> |
| EC2:EBS                 | Elastic Block Store (EBS)        | arn:\<partition\>:ec2:\<region\>:\<account-id\>:volume/\<resource\>                        | \<volume-id\>                                    |
| EC2:EIP                 | Elastic IP (EIP)                 | arn:\<partition\>:ec2:\<region\>:\<account-id\>:eip/\<resource\>                           | \<eip-allocation-id\>                            |
| EC2:ENI                 | Elastic network interfaces (ENI) | arn:\<partition\>:ec2:\<region\>:\<account-id\>:network-interface/\<resource\>             | \<network-interface-id\>                         |
| EC2:Instance            | EC2 Instance                     | arn:\<partition\>:ec2:\<region\>:\<account-id\>:instance/\<resource\>                      | \<instance-id\>                                  |
| EC2:InternetGateway     | Internet Gateway                 | arn:\<partition\>:ec2:\<region\>:\<account-id\>:internet-gateway/\<resource\>              | \<internet-gateway-id\>                          |
| EC2:NATGateway          | NAT Gateway                      | arn:\<partition\>:ec2:\<region\>:\<account-id\>:nat-gateway/\<resource\>                   | \<nat-gateway-id\>                               |
| EC2:NetworkACL          | Network ACL                      | arn:\<partition\>:ec2:\<region\>:\<account-id\>:network-acl/\<resource\>                   | \<network-acl-id\>                               |
| EC2:RouteTable          | RouteTable                       | arn:\<partition\>:ec2:\<region\>:\<account-id\>:route-table/\<resource\>                   | \<route-table-id\>                               |
| EC2:SecurityGroup       | Security Group                   | arn:\<partition\>:ec2:\<region\>:\<account-id\>:security-group/\<resource\>                | \<security-group-id\>                            |
| EC2:Snapshot            | EC2 Snapshot                     | arn:\<partition\>:ec2:\<region\>:\<account-id\>:snapshot/\<resource\>                      | \<snapshot-id\>                                  |
| EC2:Subnet              | VPC Subnet                       | arn:\<partition\>:ec2:\<region\>:\<account-id\>:subnet/\<resource\>                        | \<subnet-id\>                                    |
| EC2:VPCPeering          | VPC Peering                      | arn:\<partition\>:ec2:\<region\>:\<account-id\>:vpc-peering-connection/\<resource\>        | \<vpc-peering-connection-id\>                    |
| EC2:VPC                 | VPC                              | arn:\<partition\>:ec2:\<region\>:\<account-id\>:vpc/\<resource\>                           | \<vpc-id\>                                       |
| EC2:VPNGateway          | VPN Gateway                      | arn:\<partition\>:ec2:\<region\>:\<account-id\>:vpn-gateway/\<resource\>                   | \<vpn-gateway-id\>                               |
| EFS                     | Elastic File System (EFS)        | arn:\<partition\>:efs:\<region\>:\<account-id\>:file-system/\<resource\>                   | \<file-system-id\>                               |
| ElastiCache:Cluster     | ElastiCache Cluster              | arn:\<partition\>:elasticache:\<region\>:\<account-id\>:cluster/\<resource\>               | \<cluster-name\>                                 |
| ElastiCache:Snapshot    | ElastiCache Snapshot             | arn:\<partition\>:elasticache:\<region\>:\<account-id\>:snapshot/\<resource\>              | \<snapshot-name\>                                |
| Elasticsearch:Domain    | Elasticsearch Domain             | arn:\<partition\>:es:\<region\>:\<account-id\>:domain/\<resource\>                         | \<domain-name\>                                  |
| ELB                     | Elastic Load Balancing (ELB)     | arn:\<partition\>:elasticloadbalancing:\<region\>:\<account-id\>:loadbalancer/\<resource\> | \<load-balancer-name\>                           |
| EMR:Cluster             | EMR Cluster                      | arn:\<partition\>:emb:\<region\>:\<account-id\>:cluster/\<resource\>                       | \<cluster-id\>                                   |
| EMR:Studio              | EMR Studio                       | arn:\<partition\>:emb:\<region\>:\<account-id\>:studio/\<resource\>                        | \<studio-id\>                                    |
| IAM:Policy              | IAM Policy                       | arn:\<partition\>:iam::\<account-id\>:policy/\<resource\>                                  | \<policy-name\>                                  |
| IAM:Role                | IAM Role                         | arn:\<partition\>:iam::\<account-id\>:role/\<resource\>                                    | \<role-name\>                                    |
| IAM:User                | IAM User                         | arn:\<partition\>:iam::\<account-id\>:user/\<resource\>                                    | \<user-name\>                                    |
| KMS                     | KMS Key                          | arn:\<partition\>:kms:\<region\>:\<account-id\>:key/\<resource\>                           | \<key-id\>                                       |
| Lambda:Function         | Lambda Function                  | arn:\<partition\>:lambda:\<region\>:\<account-id\>:function/\<resource\>                   | \<function-name\>                                |
| Lightsail:Instance      | Lightsail Instance               | arn:\<partition\>:lightsail:\<region\>:\<account-id\>:Instance/\<resource\>                | \<instance-name\>                                |
| OpenSearch:Domain       | OpenSearch Domain                | arn:\<partition\>:opensearch:\<region\>:\<account-id\>:domain/\<resource\>                 | \<domain-name\>                                  |
| RDS:Cluster             | RDS Cluster                      | arn:\<partition\>:rds:\<region\>:\<account-id\>:cluster:\<resource\>                       | \<cluster-name\>                                 |
| RDS:Instance            | RDS Instance                     | arn:\<partition\>:rds:\<region\>:\<account-id\>:db:\<resource\>                            | \<instance-name\>                                |
| S3:Bucket               | S3 Bucket                        | arn:\<partition\>:s3:::\<resource\>                                                        | \<bucket-name\>                                  |

> [!TIP]
> 你可以使用 `awstt info resources` 命令来获取受支持的服务列表.