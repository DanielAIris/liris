from PyQt5.QtCore import QSettings

settings = QSettings("Liris", "IACollaborative")
settings.remove("language")
settings.sync()
print("✓ Langue effacée, la fenêtre de sélection réapparaîtra")
