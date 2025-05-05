from PyQt5.QtCore import QSettings

settings = QSettings("Liris", "IACollaborative")
print("Langue stockée:", settings.value("language", "AUCUNE"))
print("Autres clés:", settings.allKeys())
