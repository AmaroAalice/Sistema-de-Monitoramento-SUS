import os


class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLITE_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "instance", "sus_monitor.db"))
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{SQLITE_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
