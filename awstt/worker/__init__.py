#  Copyright (c) 2024 AnyIons, All rights reserved.
#  This file is part of aws-tag-tools, released under the MIT license.
#  See the LICENSE file in the project root for full license details.

from awstt.worker.scanners.cloudformation import CloudFormationScanner
from awstt.worker.scanners.cloudfront_distribution import CloudFrontScanner
from awstt.worker.scanners.cloudtrail import CloudTrailScanner
from awstt.worker.scanners.cloudwatch_alarm import CloudWatchAlarmScanner
from awstt.worker.scanners.cloudwatch_loggroup import CloudWatchLogGroupScanner
from awstt.worker.scanners.cloudwatch_rules import CloudWatchRulesScanner
from awstt.worker.scanners.dynamodb_table import DynamoDBScanner
from awstt.worker.scanners.ec2_ami import AMIScanner
from awstt.worker.scanners.ec2_autoscaling import AutoScalingGroupScanner
from awstt.worker.scanners.ec2_ebs import EBSScanner
from awstt.worker.scanners.ec2_eip import EIPScanner
from awstt.worker.scanners.ec2_instance import EC2Scanner
from awstt.worker.scanners.ec2_internet_gateway import InternetGatewayScanner
from awstt.worker.scanners.ec2_nat_gateway import NATGatewayScanner
from awstt.worker.scanners.ec2_network_acl import NetworkACLScanner
from awstt.worker.scanners.ec2_routetable import RouteTableScanner
from awstt.worker.scanners.ec2_securitygroup import SecurityGroupScanner
from awstt.worker.scanners.ec2_snapshot import SnapshotScanner
from awstt.worker.scanners.ec2_vpc import VPCScanner
from awstt.worker.scanners.ec2_vpc_peering import VPCPeeringScanner
from awstt.worker.scanners.ec2_vpn_gateway import VPNGatewayScanner
from awstt.worker.scanners.efs import EFSScanner
from awstt.worker.scanners.elasticache_cluster import ElastiCacheClusterScanner
from awstt.worker.scanners.elasticache_snapshot import ElastiCacheSnapshotScanner
from awstt.worker.scanners.elasticsearch import ElasticsearchScanner
from awstt.worker.scanners.elb import ELBScanner
from awstt.worker.scanners.emr_cluster import EMRClusterScanner
from awstt.worker.scanners.emr_studio import EMRStudioScanner
from awstt.worker.scanners.iam_policy import IAMPolicyScanner
from awstt.worker.scanners.iam_role import IAMRoleScanner
from awstt.worker.scanners.iam_user import IAMUserScanner
from awstt.worker.scanners.kms import KMSScanner
from awstt.worker.scanners.lambda_function import LambdaFunctionScanner
from awstt.worker.scanners.lightsail_instance import LightsailScanner
from awstt.worker.scanners.opensearch import OpenSearchScanner
from awstt.worker.scanners.rds_cluster import RDSClusterScanner
from awstt.worker.scanners.rds_instance import RDSInstanceScanner
from awstt.worker.scanners.s3_bucket import S3BucketScanner
