from aws_cdk import Stack, SecretValue
from aws_cdk import aws_codebuild as codebuild
from aws_cdk import aws_codepipeline as codepipeline
from aws_cdk import aws_codepipeline_actions as codepipeline_actions
from aws_cdk import aws_codedeploy as codedeploy
from constructs import Construct

class PipelineStack(Stack):
    def __init__(self, scope: Construct, id: str, params: dict, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Source Stage (GitHub)
        source_output = codepipeline.Artifact()
        source_action = codepipeline_actions.GitHubSourceAction(
            action_name="GitHub_Source",
            owner=params["github_owner"],
            repo=params["github_repo"],
            oauth_token=params["github_token"],  # Sử dụng github_token dưới dạng SecretValue
            output=source_output,
            branch=params["github_branch"]
        )

        # Build Stage (CodeBuild)
        build_project = codebuild.PipelineProject(
            self, "BuildProject",
            build_spec=codebuild.BuildSpec.from_source_filename("buildspec.yml"),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_5_0,
                compute_type=codebuild.ComputeType.SMALL
            )
        )
        build_output = codepipeline.Artifact("BuildOutput")
        build_action = codepipeline_actions.CodeBuildAction(
            action_name="Build",
            project=build_project,
            input=source_output,
            outputs=[build_output]
        )

        # Deploy Stage (CodeDeploy)
        deployment_group = codedeploy.ServerDeploymentGroup(
            self, "DeploymentGroup",
            application=codedeploy.ServerApplication(self, "MyCodeDeployApplication", application_name="MyTomcatApp"),
            deployment_group_name=params["deployment_group"]
        )

        deploy_action = codepipeline_actions.CodeDeployServerDeployAction(
            action_name="Deploy",
            deployment_group=deployment_group,
            input=build_output
        )

        # Pipeline
        pipeline = codepipeline.Pipeline(
            self, "Pipeline",
            stages=[
                codepipeline.StageProps(stage_name="Source", actions=[source_action]),
                codepipeline.StageProps(stage_name="Build", actions=[build_action]),
                codepipeline.StageProps(stage_name="Deploy", actions=[deploy_action])
            ]
        )
