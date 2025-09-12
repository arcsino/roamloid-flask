from flask_restful import Api
from .resources import (
    SignupResource,
    LoginResource,
    ChangePasswordResource,
    LogoutResource,
    UserDetailResource,
    DeleteUserResource,
)


auth_api = Api(prefix="/api/auth")
auth_api.add_resource(SignupResource, "/signup")
auth_api.add_resource(LoginResource, "/login")
auth_api.add_resource(ChangePasswordResource, "/change-password")
auth_api.add_resource(LogoutResource, "/logout")
auth_api.add_resource(UserDetailResource, "/detail")
auth_api.add_resource(DeleteUserResource, "/delete")
