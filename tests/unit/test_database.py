import app.database as database


class FakeSession:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


def test_get_db_yields_session_and_closes_it(monkeypatch):
    fake_session = FakeSession()
    monkeypatch.setattr(database, "SessionLocal", lambda: fake_session)

    db_generator = database.get_db()
    yielded_session = next(db_generator)

    assert yielded_session is fake_session

    try:
        next(db_generator)
    except StopIteration:
        pass

    assert fake_session.closed is True
