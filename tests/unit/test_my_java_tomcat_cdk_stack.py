import aws_cdk as core
import aws_cdk.assertions as assertions

from my_java_tomcat_cdk.my_java_tomcat_cdk_stack import MyJavaTomcatCdkStack

# example tests. To run these tests, uncomment this file along with the example
# resource in my_java_tomcat_cdk/my_java_tomcat_cdk_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = MyJavaTomcatCdkStack(app, "my-java-tomcat-cdk")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
