from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla.form import AdminModelConverter as Converter
from flask_admin.form import DateTimeField
from flask_admin.model.form import converts
from flask_login import current_user


class AdminModelConverter(Converter):
    @converts("ArrowType")
    def convert_arrow(self, field_args, **extra):
        return DateTimeField(**field_args)


class AdminAccessMixin:
    model_form_converter = AdminModelConverter

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def is_accessible(self):
        if not current_user.is_active:
            return False
        if current_user.is_admin:
            return True
        return False


class ProtectedModelView(AdminAccessMixin, ModelView):
    def _get_endpoint(self, endpoint):
        return 'admin.' + super()._get_endpoint(endpoint)


class ProtectedAdminIndex(AdminAccessMixin, AdminIndexView):
    pass


class UserView(ProtectedModelView):
    def get_edit_form(self):
        form_class = super().get_edit_form()
        del form_class.password
        return form_class


class ContestView(ProtectedModelView):
    form_excluded_columns = (
        'initial_crosswords',
        'stats',
    )


class PyXwordAdmin:
    def __init__(self, db):
        self.admin = None
        self.db = db

    def init_app(self, app):
        session = self.db.session

        # inline imports to prevent circular import
        from pyxword_contest.user.models import User
        from pyxword_contest.crossword.models import Crossword
        import pyxword_contest.contest.models as contest_models

        self.admin = Admin(
            template_mode='bootstrap3',
            index_view=ProtectedAdminIndex(
                url='/funadmin',
            ),
            app=app
        )
        self.admin.add_views(*[
            UserView(User, session, endpoint='users'),
            ProtectedModelView(Crossword, session, endpoint='crosswords'),
            ContestView(
                contest_models.Contest, session, endpoint='contents'
            ),
            ProtectedModelView(
                contest_models.ContestInitialCrosswords, session
            ),
            ProtectedModelView(
                contest_models.ContestStage, session
            ),
            ProtectedModelView(
                contest_models.ContestStageWinner, session
            ),
            ProtectedModelView(contest_models.UserStats, session),
            ProtectedModelView(contest_models.UserCrossword, session),
        ])
