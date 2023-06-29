from cs50 import SQL

db = SQL("sqlite:///themeparkify.db")


def execute(sql, *args, **kwargs):
    return db.execute(sql, *args, **kwargs)
