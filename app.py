import yaml
from aws_cdk import App, Stack
from my_java_tomcat_cdk.network_stack import NetworkStack
from my_java_tomcat_cdk.app_stack import MyJavaTomcatStack

# Load parameters.yaml
with open("parameters.yaml", 'r') as f:
    config = yaml.safe_load(f)

app = App()

# Khởi tạo các stack cho từng môi trường
for env_name in ["dev", "test", "prod"]:
    params = config[env_name]
    
    network_stack = NetworkStack(app, f"NetworkStack-{env_name}", params=params)
    MyJavaTomcatStack(app, f"MyJavaTomcatStack-{env_name}", network_stack=network_stack, params=params)

app.synth()
