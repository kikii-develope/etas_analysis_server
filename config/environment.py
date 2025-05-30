from enum import Enum
import os

class Environment(str, Enum):
    development = "development"
    staging = "staging"
    production = "production"

def get_env() -> Environment:
    env = os.getenv("ENV")
    
    if env is None:
        raise EnvironmentError("ENV 환경변수가 설정되지 않았습니다.")
    try:
        env_enum = Environment(env)
        return env_enum
    except ValueError:
        raise ValueError(f"지원하지 않는 ENV 값입니다.: {env}")

