from typing import Dict

from src.infrastructure.security.jwt_token_generator import JWTTokenGenerator
from src.infrastructure.security.password_hasher import PasswordHasher


class SecurityFactory:
    password_hasher_factory = {
        'bcrypt': PasswordHasher
    }

    @classmethod
    def create_password_hashser(cls, configuration: Dict) -> PasswordHasher:
        password_hasher_section = configuration['security']['password_hasher']
        password_hasher_type = password_hasher_section['type']
        password_hasher_config = password_hasher_section['config']

        creator = cls.password_hasher_factory.get(password_hasher_type)
        if not creator:
            raise ValueError(f"Unsupported password hasher type: {password_hasher_type}")

        return creator(**password_hasher_config)
    
    jwt_token_generator_factory = {
        'jwt': JWTTokenGenerator
    }
    
    @classmethod
    def create_jwt_token_generator(cls, configuration: Dict) -> JWTTokenGenerator:
        jwt_token_generator_section = configuration['security']['jwt_generator']
        jwt_token_generator_type = jwt_token_generator_section['type']
        jwt_token_generator_config = jwt_token_generator_section['config']

        creator = cls.jwt_token_generator_factory.get(jwt_token_generator_type)
        if not creator:
            raise ValueError(f"Unsupported jwt token generato type: {jwt_token_generator_type}")

        return creator(**jwt_token_generator_config)