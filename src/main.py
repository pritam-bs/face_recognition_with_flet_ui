import flet
from flet import Page
from ui.app import App
from ui.screens import view_builders
from logger import logger
import logging


def main(page: Page):
    logging.getLogger("flet_core").setLevel(logging.CRITICAL)
    logging.getLogger("flet").setLevel(logging.CRITICAL)
    page.window_min_height = 500
    page.window_min_width = 750
    app = App(page, custom_state=True)
    app.add_view_builders(view_builders)
    page.go("/login")
    logger.debug("Called main")


flet.app(target=main, port=6464)
