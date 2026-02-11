import reflex as rx
from typing import Optional
from sqlmodel import select
from ..models.user import User
from ..utils.security import verify_password, decrypt_data

class AuthState(rx.State):
    current_user: Optional[User] = None
    email_field: str = ""
    password_field: str = ""
    error_message: str = ""

    def set_email_field(self, value: str):
        self.email_field = value

    def set_password_field(self, value: str):
        self.password_field = value

    @rx.var
    def clear_name(self) -> str:
        if self.current_user:
            try:
                return decrypt_data(self.current_user.name)
            except Exception:
                return "User"
        return ""

    @rx.var
    def clear_initials(self) -> str:
        name = self.clear_name
        if name:
            parts = name.split()
            if len(parts) >= 2:
                return (parts[0][0] + parts[1][0]).upper()
            return name[0:2].upper()
        return ""

    def login(self):
        with rx.session() as session:
            # Since emails are hashed (salted/randomized), we cannot use a deterministic lookup.
            # We must load users and verify each one. 
            # Consistent with UserState.add_user check.
            all_users = session.exec(select(User).where(User.status == "active")).all()
            
            authenticated_user = None
            for user in all_users:
                # Check email hash with legacy support
                email_match = False
                try:
                    if verify_password(self.email_field, user.mail):
                        email_match = True
                except Exception:
                    if self.email_field == user.mail:
                        email_match = True
                
                if email_match:
                    # Check password hash
                    if verify_password(self.password_field, user.password):
                        authenticated_user = user
                        break
            
            if authenticated_user:
                self.current_user = authenticated_user
                self.error_message = ""
                return rx.redirect("/")
            else:
                self.error_message = "Invalid email or password"

    def logout(self):
        self.reset()
        return rx.redirect("/login")

    def check_login(self):
        if self.current_user is None:
            return rx.redirect("/login")

    @rx.var
    def is_admin(self) -> bool:
        if self.current_user:
            return self.current_user.role == "admin"
        return False

    def check_admin(self):
        if not self.is_admin:
            return rx.redirect("/")
