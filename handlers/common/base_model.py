import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(db.INT, primary_key=True, autoincrement=True)
    date_created = db.Column(
        db.DateTime(timezone=True), default=datetime.datetime.utcnow
    )
    date_updated = db.Column(
        db.DateTime(timezone=True),
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
    )
    date_deleted = db.Column(db.DateTime(timezone=True), default=None)

    def save(self):
        db.session.add(self)
        db.session.commit()
