# -*- coding: utf-8 -*-
"""User forms."""
from flask_wtf import Form
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired, Email, Length

from .models import User


class RegisterForm(Form):
    """Register form."""

    email = StringField(
        'Email',
        validators=[DataRequired(), Email(), Length(min=6, max=75)],
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=6, max=100)],
    )
    display_name = StringField(
        'Publicly shown name',
        validators=[DataRequired(), Length(min=3, max=25)],
    )

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        """Validate the form."""
        initial_validation = super(RegisterForm, self).validate()
        if not initial_validation:
            return False

        user = User.query.filter_by(
            display_name=self.display_name.data
        ).first()
        if user:
            self.display_name.errors.append(
                "Someone is already using this name"
            )
        user = User.query.filter_by(email=self.email.data).first()
        if user:
            self.email.errors.append("Email already registered")

        if self.email.errors or self.display_name.errors:
            return False
        return True


class UserEdit(Form):
    """Register form."""
    display_name = RegisterForm.display_name

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super().__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        """Validate the form."""
        initial_validation = super().validate()
        if not initial_validation:
            return False

        user = User.query.filter_by(
            display_name=self.display_name.data
        ).first()
        if user and user != self.user:
            self.display_name.errors.append(
                "Someone is already using this name"
            )
        return True
