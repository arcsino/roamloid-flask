from ..models import User
import re


class SignupValidator:
    """Validator for user signup data."""

    def validate(self, data: dict) -> tuple[bool, str]:
        username = data.get("username")
        password = data.get("password")

        # Username and password are required
        if not username or not password:
            # return False, "ユーザー名とパスワードは必須です。"
            return False, "Username and password are required."
        # Username must be alphanumeric with underscores
        if not re.match(r"^\w+$", username):
            # return False, "ユーザー名には英数字とアンダースコアのみ利用できます。"
            return (
                False,
                "Username can only contain alphanumeric characters and underscores.",
            )
        # Username must be unique
        if User.query.filter_by(username=username).first():
            # return False, "このユーザー名は既に使用されています。"
            return False, "This username is already taken."
        # Password must be at least 8 characters
        if len(password) < 8:
            # return False, "パスワードは8文字以上である必要があります。"
            return False, "Password must be at least 8 characters long."
        # Password must contain both letters and numbers
        if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
            # return False, "パスワードには英字と数字の両方を含める必要があります。"
            return False, "Password must contain both letters and numbers."

        return True, "Validation passed."


class LoginValidator:
    """Validator for user login data."""

    def validate(self, data: dict) -> tuple[bool, str]:
        username = data.get("username")
        password = data.get("password")

        # Username and password are required
        if not username or not password:
            # return False, "ユーザー名とパスワードは必須です。"
            return False, "Username and password are required."

        return True, "Validation passed."


class ChangePasswordValidator:
    """Validator for changing user password."""

    def validate(self, data: dict) -> tuple[bool, str]:
        old_password = data.get("old_password")
        new_password = data.get("new_password")

        # Both old and new passwords are required
        if not old_password or not new_password:
            # return False, "古いパスワードと新しいパスワードは必須です。"
            return False, "Old password and new password are required."
        # New password must be different from old password
        if old_password == new_password:
            # return False, "新しいパスワードは古いパスワードと異なる必要があります。"
            return False, "New password must be different from old password."
        # New password must be at least 8 characters
        if len(new_password) < 8:
            # return False, "新しいパスワードは8文字以上である必要があります。"
            return False, "New password must be at least 8 characters long."
        # New password must contain both letters and numbers
        if not re.search(r"[A-Za-z]", new_password) or not re.search(
            r"\d", new_password
        ):
            # return False, "新しいパスワードには英字と数字の両方を含める必要があります。"
            return False, "New password must contain both letters and numbers."

        return True, "Validation passed."
