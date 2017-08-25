import markdown
from markupsafe import Markup


class Markdown(object):
    def __init__(self, app=None):
        self.app = app

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """
        Mutate the application passed in as explained here:
        http://flask.pocoo.org/docs/0.10/extensiondev/

        :param app: Flask application
        :return: None
        """
        app.add_template_global(self.markdown)

    def markdown(self, markdown_txt: str):
        """
        Render markdown

        :param markdown_txt: markdown markup to be rendered
        :return: rendered markdown markup
        """

        return Markup(markdown.markdown(markdown_txt))
