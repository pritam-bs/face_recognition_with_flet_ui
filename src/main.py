import flet
from flet import Page
from ui.app import App
from ui.screens import view_builders
from logger import logger
import logging


def main(page: Page):
    logging.getLogger("flet_core").setLevel(logging.ERROR)
    logging.getLogger("flet_runtime").setLevel(logging.ERROR)
    logging.getLogger("flet").setLevel(logging.ERROR)
    logging.basicConfig(level=logging.ERROR)

    page.theme = flet.Theme(color_scheme_seed="blue")
    page.window_min_height = 600
    page.window_min_width = 800
    app = App(page, custom_state=True)
    app.add_view_builders(view_builders)
    page.go("/login")
    logger.debug("Called main")


flet.app(target=main, port=6464, view=flet.FLET_APP)
