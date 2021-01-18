import environs

# Load operating system environment variables and then prepare to use them
env = environs.Env()


class BaseConfig:
    """Base configuration."""
    # Swagger
    SWAGGER_UI = env.bool("SWAGGER_UI", default=False)
    SERVE_SPEC = env.bool("SERVE_SPEC", default=False)

    # Database
    DB_NAME = env('POSTGRES_DB')
    DB_USERNAME = env('POSTGRES_USER')
    DB_PASSWORD = env('POSTGRES_PASSWORD')
    DB_HOSTNAME = env('POSTGRES_HOSTNAME')
    DB_PORT = env('POSTGRES_PORT')

    SQLALCHEMY_ECHO = env.bool("SQLALCHEMY_ECHO", default=False)
    SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOSTNAME}:{DB_PORT}/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = env.bool('SQLALCHEMY_TRACK_MODIFICATIONS', default=False)


class ProductionConfig(BaseConfig):
    """Production configuration."""
    SQLALCHEMY_ECHO = False


class StagingConfig(BaseConfig):
    """Staging configuration."""
    SQLALCHEMY_ECHO = False


class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    SQLALCHEMY_ECHO = env.bool("SQLALCHEMY_ECHO", default=True)


class TestingConfig(BaseConfig):
    """Test configuration."""
    TESTING = True
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SQLALCHEMY_DATABASE_URI = f'postgresql://{BaseConfig.DB_USERNAME}:{BaseConfig.DB_PASSWORD}@{BaseConfig.DB_HOSTNAME}:{BaseConfig.DB_PORT}/test_{BaseConfig.DB_NAME}'
    SQLALCHEMY_ECHO = False


app_config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'staging': StagingConfig,
    'production': ProductionConfig,
}
