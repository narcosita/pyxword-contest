# -*- coding: utf-8 -*-
"""User models."""
import arrow
from flask_login import UserMixin
from sqlalchemy_utils import ArrowType

from pyxword_contest.database import (
    Column,
    db,
    Model,
    reference_col,
    relationship,
    SurrogatePK,
)
from pyxword_contest.extensions import bcrypt


class Role(SurrogatePK, Model):
    """A role for a user."""

    __tablename__ = 'roles'
    name = Column(db.String(80), unique=True, nullable=False)
    user_id = reference_col('users', nullable=True)
    user = relationship('User', backref='roles')

    def __init__(self, name, **kwargs):
        """Create instance."""
        db.Model.__init__(self, name=name, **kwargs)

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<Role({name})>'.format(name=self.name)


class User(UserMixin, SurrogatePK, Model):
    """A user of the app."""

    __tablename__ = 'users'
    email = Column(db.String(80), unique=True, nullable=False)
    #: The hashed password
    password = Column(db.Binary(128), nullable=True)
    created_at = Column(
        ArrowType, nullable=False, default=arrow.utcnow
    )
    display_name = Column(db.String(80), nullable=True)
    full_name = Column(db.String(100), nullable=True)
    active = Column(db.Boolean(), default=False)
    is_admin = Column(db.Boolean(), default=False)

    def __init__(self, email, password=None, **kwargs):
        """Create instance."""
        db.Model.__init__(self, email=email, **kwargs)
        if password:
            self.set_password(password)
        else:
            self.password = None

    def set_password(self, password):
        """Set password."""
        self.password = bcrypt.generate_password_hash(password)

    def check_password(self, value):
        """Check password."""
        return bcrypt.check_password_hash(self.password, value)

    def __repr__(self):
        """Represent instance as a unique string."""
        return f'<User({self.email!r})>'

    def __eq__(self, other):
        return other and self.id == other.id
