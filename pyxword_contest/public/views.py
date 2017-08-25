# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user

from pyxword_contest.extensions import login_manager
from pyxword_contest.public.forms import LoginForm
from pyxword_contest.user.forms import RegisterForm
from pyxword_contest.user.models import User
from pyxword_contest.utils import flash_errors

blueprint = Blueprint('public', __name__, static_folder='../static')


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    return User.get_by_id(int(user_id))


@blueprint.route('/')
def home():
    """Home page."""
    return render_template('public/home.html')


@blueprint.route('/logout/')
@login_required
def logout():
    """Logout."""
    logout_user()
    flash('You are logged out.', 'info')
    return redirect(
        request.args.get('next') or '/'
    )


@blueprint.route('/login/', methods=['GET', 'POST'])
def login():
    """Register new user."""
    form = LoginForm(request.form)
    # Handle logging in
    if request.method == 'POST':
        if form.validate_on_submit():
            login_user(form.user)
            flash('You are logged in.', 'success')
            return redirect(
                request.args.get('next') or '/'
            )
        else:
            flash_errors(form)
    return render_template('public/login.html', login_form=form)


@blueprint.route('/register/', methods=['GET', 'POST'])
def register():
    """Register new user."""
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        user = User.create(
            email=form.email.data, password=form.password.data,
            active=True,
            display_name=form.display_name.data,
        )
        flash('Thank you for registering, now lets play!', 'success')
        login_user(user)
        return redirect(url_for('public.home'))
    else:
        flash_errors(form)
    return render_template('public/register.html', form=form)
