from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, RedisDsn, HttpUrl, SecretStr

class Settings(BaseSettings):
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_KEY_HEADER: str = "X-API-Key"
    SECRET_KEY: SecretStr

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    DATABASE_URL: Optional[PostgresDsn] = None

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_URL: Optional[RedisDsn] = None

    CHROMA_HOST: str
    CHROMA_PORT: int
    CHROMA_URL: Optional[HttpUrl] = None

    OPENAI_API_KEY: SecretStr
    ANTHROPIC_API_KEY: SecretStr

    AWS_ACCESS_KEY_ID: Optional[SecretStr] = None
    AWS_SECRET_ACCESS_KEY: Optional[SecretStr] = None
    AWS_REGION: Optional[str] = "us-west-2"

    AGENT_TEMPERATURE: float = 0.7
    AGENT_MODEL: str = "gpt-4"
    HUMAN_REVIEW_REQUIRED: bool = True
    SIMILARITY_THRESHOLD: float = 0.85
    MAX_RETRIES: int = 3
    TIMEOUT_SECONDS: int = 300

    EMBEDDING_MODEL: str = "text-embedding-ada-002"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.DATABASE_URL:
            self.DATABASE_URL = PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_HOST,
                port=self.POSTGRES_PORT,
                path=self.POSTGRES_DB,
            )
        
        if not self.REDIS_URL:
            self.REDIS_URL = RedisDsn.build(
                scheme="redis",
                host=self.REDIS_HOST,
                port=self.REDIS_PORT,
            )

        if not self.CHROMA_URL:
            self.CHROMA_URL = HttpUrl(
                f"http://{self.CHROMA_HOST}:{self.CHROMA_PORT}"
            )

@lru_cache()
def get_settings() -> Settings:
    return Settings()

class TierInfo:
    def __init__(self, name: str, description: str, min_experience_months: int = 0):
        self.name = name
        self.description = description
        self.min_experience_months = min_experience_months

class ContentTypeInfo:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

class StateInfo:
    def __init__(self, name: str, description: str, allows_editing: bool = True):
        self.name = name
        self.description = description
        self.allows_editing = allows_editing

class SandboxTypeInfo:
    def __init__(self, name: str, description: str, isolation_level: str):
        self.name = name
        self.description = description
        self.isolation_level = isolation_level

class PersonaInfo:
    def __init__(self, name: str, description: str, primary_focus: str):
        self.name = name
        self.description = description
        self.primary_focus = primary_focus

class CostCategoryInfo:
    def __init__(self, name: str, description: str, aws_service_prefix: str = ""):
        self.name = name
        self.description = description
        self.aws_service_prefix = aws_service_prefix

class ReviewTypeInfo:
    def __init__(self, name: str, description: str, required: bool = True):
        self.name = name
        self.description = description
        self.required = required

class AnalysisTypeInfo:
    def __init__(self, name: str, description: str, frequency: str = "on_demand"):
        self.name = name
        self.description = description
        self.frequency = frequency

class ResourceTagInfo:
    def __init__(self, name: str, description: str, prefix: str = "learn"):
        self.name = name
        self.description = description
        self.prefix = prefix

class BuilderConstants:
    class TIERS:
        T1 = TierInfo("T1", "Foundational", 0)
        T2 = TierInfo("T2", "Intermediate", 6)
        T3 = TierInfo("T3", "Advanced", 12)
        T4 = TierInfo("T4", "Expert", 24)
        @classmethod
        def get_names(cls) -> list[str]:
            return [tier.name for tier in [cls.T1, cls.T2, cls.T3, cls.T4]]

    class CONTENT_TYPES:
        LESSON = ContentTypeInfo("lesson", "Individual learning unit")
        MODULE = ContentTypeInfo("module", "Collection of related lessons")
        SESSION = ContentTypeInfo("session", "Time-boxed learning period")
        EXERCISE = ContentTypeInfo("exercise", "Hands-on practice activity")
        ASSESSMENT = ContentTypeInfo("assessment", "Knowledge evaluation")
        EXPERIMENT = ContentTypeInfo("experiment", "Exploratory learning activity")

        @classmethod
        def get_names(cls) -> list[str]:
            return [content_type.name for content_type in [cls.LESSON, cls.MODULE, cls.SESSION, cls.EXERCISE, cls.ASSESSMENT, cls.EXPERIMENT]]

    class STATES:
        DRAFT = StateInfo("draft", "Initial creation phase", True)
        STAGED = StateInfo("staged", "Ready for review", True)
        IN_REVIEW = StateInfo("in_review", "Under review", False)
        APPROVED = StateInfo("approved", "Passed review", False)
        REJECTED = StateInfo("rejected", "Needs revision", True)
        ARCHIVED = StateInfo("archived", "No longer active", False)

        @classmethod
        def get_names(cls) -> list[str]:
            return [state.name for state in [cls.DRAFT, cls.STAGED, cls.IN_REVIEW, cls.APPROVED, cls.REJECTED, cls.ARCHIVED]]

    class SANDBOX_TYPES:
        INDIVIDUAL = SandboxTypeInfo("individual", "Single learner environment", "high")
        SHARED = SandboxTypeInfo("shared", "Multi-learner shared environment", "low")
        ISOLATED = SandboxTypeInfo("isolated", "Completely isolated environment", "maximum")
        MANAGED = SandboxTypeInfo("managed", "Instructor-managed environment", "medium")

        @classmethod
        def get_names(cls) -> list[str]:
            return [sandbox.name for sandbox in [cls.INDIVIDUAL, cls.SHARED, cls.ISOLATED, cls.MANAGED]]

    class PERSONAS:
        DEV = PersonaInfo("developer", "Software Developer", "code")
        ARCH = PersonaInfo("architect", "Solution Architect", "design")
        OPS = PersonaInfo("operations", "Operations Engineer", "infrastructure")
        SEC = PersonaInfo("security", "Security Engineer", "security")
        DATA = PersonaInfo("data_engineer", "Data Engineer", "data")
        ML = PersonaInfo("ml_engineer", "Machine Learning Engineer", "ml")
        ALL = PersonaInfo("all_roles", "All Roles", "general")

        @classmethod
        def get_names(cls) -> list[str]:
            return [persona.name for persona in [cls.DEV, cls.ARCH, cls.OPS, cls.SEC, cls.DATA, cls.ML, cls.ALL]]

    class COST_CATEGORIES:
        COMPUTE = CostCategoryInfo("compute_resources", "Computation resources", "ec2")
        STORAGE = CostCategoryInfo("storage_resources", "Data storage resources", "s3")
        NETWORK = CostCategoryInfo("network_resources", "Network resources", "vpc")
        MANAGED = CostCategoryInfo("managed_services", "AWS managed services", "")
        OTHER = CostCategoryInfo("other_resources", "Miscellaneous resources", "")

        @classmethod
        def get_names(cls) -> list[str]:
            return [category.name for category in [cls.COMPUTE, cls.STORAGE, cls.NETWORK, cls.MANAGED, cls.OTHER]]

    class REVIEW_TYPES:
        TECHNICAL = ReviewTypeInfo("technical_review", "Technical accuracy review")
        EDITORIAL = ReviewTypeInfo("editorial_review", "Content quality review")
        COST = ReviewTypeInfo("cost_review", "Resource cost review")
        ACCESSIBILITY = ReviewTypeInfo("accessibility_review", "Accessibility compliance review")
        AI_ASSISTED = ReviewTypeInfo("ai_review", "AI-powered automated review", False)

        @classmethod
        def get_names(cls) -> list[str]:
            return [review.name for review in [cls.TECHNICAL, cls.EDITORIAL, cls.COST, cls.ACCESSIBILITY, cls.AI_ASSISTED]]

    class ANALYSIS_TYPES:
        COVERAGE = AnalysisTypeInfo("coverage_analysis", "Content coverage analysis")
        GAPS = AnalysisTypeInfo("gap_analysis", "Missing content analysis")
        OVERLAP = AnalysisTypeInfo("content_overlap", "Duplicate content detection")
        COST = AnalysisTypeInfo("cost_analysis", "Resource cost analysis")
        PREREQUISITES = AnalysisTypeInfo("prerequisite_analysis", "Learning path requirements")
        PATHWAY = AnalysisTypeInfo("learning_pathway_analysis", "Learning journey optimization")

        @classmethod
        def get_names(cls) -> list[str]:
            return [analysis.name for analysis in [cls.COVERAGE, cls.GAPS, cls.OVERLAP, cls.COST, cls.PREREQUISITES, cls.PATHWAY]]

    class AWS_TAGS:
        ENVIRONMENT = ResourceTagInfo("environment", "Deployment environment tag")
        TIER = ResourceTagInfo("tier", "Learning content tier tag")
        ROLE = ResourceTagInfo("role", "Target persona role tag")
        LESSON = ResourceTagInfo("lesson", "Associated lesson tag")
        COST_CENTER = ResourceTagInfo("cost-center", "Billing category tag")
        LEARNER_ID = ResourceTagInfo("learner-id", "Individual learner tag")

        @classmethod
        def get_names(cls) -> list[str]:
            return [tag.name for tag in [cls.ENVIRONMENT, cls.TIER, cls.ROLE, cls.LESSON, cls.COST_CENTER, cls.LEARNER_ID]]

settings = get_settings()