from aws_cdk import Stack, CfnOutput
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_autoscaling as autoscaling
from aws_cdk import aws_elasticloadbalancingv2 as elbv2
from aws_cdk import core

class MyJavaTomcatStack(Stack):
    def __init__(self, scope: core.Construct, id: str, network_stack: 'NetworkStack', params: dict, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Cài đặt UserData để tự động cài Tomcat khi EC2 khởi động
        user_data = ec2.UserData.for_linux()

        # Thêm script cài Tomcat vào UserData
        user_data.add_commands(
            "sudo yum update -y",
            "sudo yum install -y java-1.8.0-openjdk wget",
            "cd /usr/local",
            "sudo wget https://archive.apache.org/dist/tomcat/tomcat-9/v9.0.62/bin/apache-tomcat-9.0.62.tar.gz",  # Tải Tomcat
            "sudo tar -xvzf apache-tomcat-9.0.62.tar.gz",
            "sudo ln -s /usr/local/apache-tomcat-9.0.62 /usr/local/tomcat",
            "sudo chown -R ec2-user:ec2-user /usr/local/tomcat",
            "cd /usr/local/tomcat/bin",
            "sudo ./startup.sh",
        )

        # Tạo EC2 instance với UserData
        ec2_instance = ec2.Instance(
            self, "TomcatInstance",
            instance_type=ec2.InstanceType(params["instance_type"]),
            machine_image=ec2.AmazonLinuxImage(),
            vpc=network_stack.vpc,
            vpc_subnets=ec2.SubnetSelection(subnets=network_stack.vpc.private_subnets),
            security_group=network_stack.security_group,
            key_name="java_tomcat",
            user_data=user_data
        )

        # Tạo Auto Scaling Group (ASG) cho EC2 instance của ứng dụng Tomcat
        asg = autoscaling.AutoScalingGroup(
            self, "ASG",
            instance_type=ec2.InstanceType(params["instance_type"]),
            machine_image=ec2.AmazonLinuxImage(),
            vpc=network_stack.vpc,
            vpc_subnets=ec2.SubnetSelection(subnets=network_stack.vpc.private_subnets),
            security_group=network_stack.security_group,
            min_capacity=params["min_capacity"],
            max_capacity=params["max_capacity"],
            desired_capacity=params.get("desired_capacity", params["min_capacity"]),
            key_name="java_tomcat",
            user_data=user_data
        )

        # Tạo Load Balancer
        alb = elbv2.ApplicationLoadBalancer(
            self, "ALB",
            vpc=network_stack.vpc,
            internet_facing=True,
            security_group=network_stack.security_group
        )

        listener = alb.add_listener("Listener", port=80)
        listener.add_targets("AppFleet", port=8080, targets=[asg])

        # Output ALB DNS
        CfnOutput(self, "LoadBalancerDNS", value=alb.load_balancer_dns_name)
