import nox


@nox.session(python="3.8")
def run_linters(session: nox.Session) -> None:
    """Run pre-commit hooks on all files in the repository."""
    session.install("pre-commit")
    session.run("pre-commit", "install")
    session.run("pre-commit", "run", "-a")


@nox.session(python=["3.8", "3.9", "3.10", "3.11", "3.12"])
def run_tests(session: nox.Session) -> None:
    """Run tests in different Django versions"""
    for version in range(2):
        session.install(f"django>=4.{version + 1},<4.{version + 2}")
        session.install("pytest-django", "django-redis", "celery")
        session.run("pytest", "./tests", "-vv")
