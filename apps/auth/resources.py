from flask import request
from flask_restful import Resource
from flask_login import login_user, logout_user, login_required, current_user
from ..models import db, User
from .validators import SignupValidator, LoginValidator, ChangePasswordValidator


class SignupResource(Resource):
    """User signup resource."""

    validator = SignupValidator()

    def post(self):
        data = request.get_json()
        # Validation
        is_valid, message = self.validator.validate(data)
        if not is_valid:
            return {"error_message": message}, 400  # Bad Request
        # Create new user
        username = data["username"]
        password = data["password"]
        new_user = User(username=username)
        new_user.password = password
        db.session.add(new_user)
        db.session.commit()
        # return {"message": "ユーザー登録が成功しました。"}, 201  # Created
        return {"message": "User registration successful."}, 201  # Created


class LoginResource(Resource):
    """User login resource."""

    validator = LoginValidator()

    def post(self):
        data = request.get_json()
        # Validation
        is_valid, message = self.validator.validate(data)
        if not is_valid:
            return {"error_message": message}, 400  # Bad Request
        # Authenticate user
        username = data["username"]
        password = data["password"]
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            # return {"message": "ログインに成功しました。"}, 200  # OK
            return {"message": "Login successful."}, 200  # OK
        # return {"error_message": "ユーザー名またはパスワードが正しくありません。"}, 401  # Unauthorized
        return {"error_message": "Invalid username or password."}, 401  # Unauthorized


class ChangePasswordResource(Resource):
    """Change user password resource."""

    validator = ChangePasswordValidator()

    @login_required
    def post(self):
        data = request.get_json()
        # Validation
        is_valid, message = self.validator.validate(data)
        if not is_valid:
            return {"error_message": message}, 400  # Bad Request
        # Change password
        old_password = data["old_password"]
        new_password = data["new_password"]
        if current_user and current_user.check_password(old_password):
            current_user.password = new_password
            db.session.commit()
            # return {"message": "パスワードが正常に変更されました。"}, 200  # OK
            return {"message": "Password changed successfully."}, 200  # OK
        # return {"error_message": "古いパスワードが正しくありません。"}, 401  # Unauthorized
        return {"error_message": "Old password is incorrect."}, 401  # Unauthorized


class LogoutResource(Resource):
    """User logout resource."""

    @login_required
    def post(self):
        logout_user()
        # return {"message": "ログアウトに成功しました。"}, 200  # OK
        return {"message": "Logout successful."}, 200  # OK


class UserDetailResource(Resource):
    """Get user details resource."""

    @login_required
    def get(self):
        if current_user:
            return {
                "id": current_user.id,
                "username": current_user.username,
            }, 200  # OK
        # return {"error_message": "ユーザーが見つかりません。"}, 404  # Not Found
        return {"error_message": "User not found."}, 404  # Not Found


class DeleteUserResource(Resource):
    """Delete user resource."""

    @login_required
    def delete(self):
        user = current_user
        if user:
            db.session.delete(user)
            db.session.commit()
            logout_user()
            # return {"message": "ユーザーが正常に削除されました。"}, 200  # OK
            return {"message": "User deleted successfully."}, 200  # OK
        # return {"error_message": "ユーザーが見つかりません。"}, 404  # Not Found
        return {"error_message": "User not found."}, 404  # Not Found
