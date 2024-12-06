from dependency_injector.wiring import inject, Provider

from src.application.commands.auth.login_command import LoginCommand, LoginResponse
from src.application.commands.auth.register_command import RegisterCommand
from src.application.ports.message_bus import AbstractMessageBus
from src.application.ports.uow import UnitOfWork
from src.infrastructure.security.jwt_token_generator import JWTTokenGenerator
from src.infrastructure.security.password_hasher import PasswordHasher
from src.infrastructure.uuid.uuid_generator import UUIDv7Generator
from src.interfaces.api import auth_api
from flask import request, jsonify

@auth_api.route('/register', methods=['POST'])
@inject
def register(
    message_bus: AbstractMessageBus = Provider[AbstractMessageBus],
    uow: UnitOfWork = Provider[UnitOfWork],
    password_hasher: PasswordHasher = Provider[PasswordHasher],
    id_generator: UUIDv7Generator = Provider[UUIDv7Generator]
):
    try:
        user_data = request.get_json()
        command = RegisterCommand(
            username=user_data['username'],
            password=user_data['password'],
            _password_hasher=password_hasher,
            _id_generator=id_generator
        )
        user_id = message_bus.handle(command, uow)
        return jsonify({'id': str(user_id)}), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@auth_api.route('/sign-in/', methods=['POST'])
@inject
def authenticate(
    message_bus: AbstractMessageBus = Provider[AbstractMessageBus],
    uow: UnitOfWork = Provider[UnitOfWork],
    password_hasher: PasswordHasher = Provider[PasswordHasher],
    token_generator: JWTTokenGenerator = Provider[JWTTokenGenerator]
):
    try:
        user_data = request.get_json()
        command = LoginCommand(
            username=user_data['username'],
            password=user_data['password'],
            _password_hasher=password_hasher,
            _token_generator=token_generator
        )
        login_response: LoginResponse = message_bus.handle(command, uow)
        return jsonify({
            'access_token': login_response.access_token,
            'token_type': login_response.token_type
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 401