from aws_cdk import Stack
from aws_cdk import aws_ec2 as ec2
from constructs import Construct

class NetworkStack(Stack):
    def __init__(self, scope: Construct, id: str, params: dict, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Tạo VPC
        self.vpc = ec2.Vpc(
            self, "MyVpc",
            max_azs=2,  # Sử dụng tối đa 2 Availability Zones
            cidr="10.0.0.0/16",
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="public-subnet",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="private-subnet",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT,
                    cidr_mask=24
                )
            ]
        )

        # Tạo Security Group cho Load Balancer và các instances trong private subnet
        self.security_group = ec2.SecurityGroup(
            self, "AppSecurityGroup",
            vpc=self.vpc,
            description="Allow HTTP and SSH",
            allow_all_outbound=True
        )

        # Thêm quy tắc cho Security Group của Load Balancer
        self.security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(), ec2.Port.tcp(8080), "Allow HTTP traffic"
        )
        self.security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(), ec2.Port.tcp(22), "Allow SSH traffic"
        )
