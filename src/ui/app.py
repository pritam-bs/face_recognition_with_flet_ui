from fletched.routed_app import CustomAppState, RoutedApp


class AppState(CustomAppState):
    is_loged_in = False
    pass


class App(RoutedApp):
    state: AppState = AppState()
