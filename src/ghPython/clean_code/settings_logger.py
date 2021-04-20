class Settings():
    def __init__(self):
        self._print_settings
        self._pattern_settings
        self._geometry_settings
    
    @property
    def print_settings(self):
        return self._print_settings

    @print_settings.setter
    def print_settings(self, other):
        self._print_settings = other

    @property
    def pattern_settings(self):
        return self._pattern_settings

    @pattern_settings.setter
    def pattern_settings(self, other):
        self._pattern_settings = other

    @property
    def geometry_settings(self):
        return self._geometry_settings

    @geometry_settings.setter
    def geometry_settings(self, other):
        self._geometry_settings = other