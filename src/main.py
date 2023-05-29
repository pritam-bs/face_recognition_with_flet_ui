import flet
from flet import Page
from ui.app import App
from ui.screens import view_builders
from logger import logger


def main(page: Page):
    app = App(page, custom_state=True)
    app.add_view_builders(view_builders)
    page.go("/login")
    logger.debug("Called main")


flet.app(target=main)
