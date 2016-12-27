class MapLoadingError(Exception):
    def __init__(self):
        self.msg = 'Map loading failed'

    #def __str__(self):
    #    return self.msg
