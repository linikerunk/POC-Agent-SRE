from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    deployments_files_dir: str = "deployments"
    mcp_deployment_namespace: str = "mcp-deployment-space"
    app_name: str = "SRE Agent API"
    environment: str = "development"
    log_level: str = "INFO"

    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"

    # Path to the skills-repo folder (SRE skills/runbooks), relative to the backend dir
    skills_repo_path: str = "skills-repo"

    class Config:
        env_file = ".env"


settings = Settings()
