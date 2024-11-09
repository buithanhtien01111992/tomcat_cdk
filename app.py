import yaml
import boto3
from aws_cdk import App, SecretValue
from my_java_tomcat_cdk.network_stack import NetworkStack
from my_java_tomcat_cdk.app_stack import MyJavaTomcatStack
from my_java_tomcat_cdk.pipeline_stack import PipelineStack
from my_java_tomcat_cdk.cdk_pipeline_stack import CDKPipelineStack

# Load parameters.yaml
with open("parameters.yaml", 'r') as f:
    config = yaml.safe_load(f)

# Truy xuất token từ Secrets Manager
def get_secret(secret_name):
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_name)
    return response['SecretString']

app = App()

# Khởi tạo các stack cho từng môi trường
for env_name in ["dev", "test", "prod"]:
    params = config.get(env_name)
    if params is None:
        raise ValueError(f"Missing configuration for environment: {env_name}")

    secret_name = params.get("github_secret_name")
    if secret_name is None:
        raise ValueError(f"Missing 'github_secret_name' for environment: {env_name}")

    params["github_token"] = get_secret(secret_name)

    network_stack = NetworkStack(app, f"NetworkStack-{env_name}", params=params)
    MyJavaTomcatStack(app, f"MyJavaTomcatStack-{env_name}", network_stack=network_stack, params=params)

# Khởi tạo PipelineStack cho ứng dụng Java Tomcat
pipeline_params = {
    "github_owner": config["dev"]["github_owner"],
    "github_repo": config["dev"]["github_repo"],
    "github_token": SecretValue.secrets_manager(config["dev"]["github_secret_name"]),  # Sử dụng SecretValue
    "github_branch": config["dev"]["github_branch"],
    "deployment_group": config["dev"]["deployment_group"]
}
PipelineStack(app, "PipelineStack", params=pipeline_params)

# Khởi tạo CDKPipelineStack cho CDK source code
cdk_pipeline_params = {
    "github_owner": config["dev"]["github_owner"],
    "github_repo": config["dev"]["github_repo"],
    "github_token": SecretValue.secrets_manager(config["dev"]["github_secret_name"]),  # Sử dụng SecretValue
    "github_branch": config["dev"]["github_branch"],
    "dev": config["dev"],
    "test": config["test"],
    "prod": config["prod"]
}
CDKPipelineStack(app, "CDKPipelineStack", params=cdk_pipeline_params)

app.synth()
