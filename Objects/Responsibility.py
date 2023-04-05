class Responsibility:

    def __init__(self, id = -1, description = "", id_project = 0, id_screen = 0, id_controller = -1, list_of_ssc=[]):
        self.id = id  # INTEGER PRIMARY KEY AUTOINCREMENT
        self.description = description  # TEXT NOT NULL
        self.id_project = id_project
        self.id_screen = id_screen
        self.id_controller = id_controller  # INTEGER NOT NULL
        self.list_of_ssc = list_of_ssc  # Object

class Responsibility_ssc:

    def __init__(self, id = -1, id_responsibility = -1, id_constraint = -1, id_constraint_screen = 0):
        self.id = id  # INTEGER PRIMARY KEY AUTOINCREMENT
        self.id_responsibility = id_responsibility  # INTEGER NOT NULL
        self.id_constraint = id_constraint  # INTEGER NOT NULL
        self.id_constraint_screen = id_constraint_screen