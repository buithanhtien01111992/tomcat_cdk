from aws_cdk import (
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_codebuild as codebuild,
    pipelines as pipelines,
    Stack
)
from constructs import Construct

class CDKPipelineStack(Stack):
    def __init__(self, scope: Construct, id: str, params: dict, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Source Stage - GitHub source action
        source_output = codepipeline.Artifact()
        source_action = codepipeline_actions.GitHubSourceAction(
            action_name="GitHub_Source",
            owner=params["github_owner"],
            repo=params["github_repo"],
            oauth_token=params["github_token"],
            output=source_output,
            branch=params["github_branch"]
        )

        # Define the pipeline
        pipeline = codepipeline.Pipeline(self, "Pipeline")
        pipeline.add_stage(
            stage_name="Source",
            actions=[source_action]
        )

        # Build Stage
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

        # Add Build stage to the pipeline
        pipeline.add_stage(
            stage_name="Build",
            actions=[build_action]
        )

        # CDK Pipeline definition with the synth step
        cdk_pipeline = pipelines.CodePipeline(
            self, "CDKPipeline",
            synth=pipelines.ShellStep("Synth",
                input=build_output,  # Đảm bảo input là artifact từ Build
                commands=[
                    "npm install -g aws-cdk", 
                    "pip install -r requirements.txt", 
                    "cdk synth"
                ],
                primary_output_directory="cdk.out"
            )
        )

        # Add stages for different environments
        cdk_pipeline.add_stage(MyJavaTomcatStack(self, "Dev", params=params["dev"]))
        cdk_pipeline.add_stage(MyJavaTomcatStack(self, "Test", params=params["test"]))
        cdk_pipeline.add_stage(MyJavaTomcatStack(self, "Prod", params=params["prod"]))
