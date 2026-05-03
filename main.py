"""Root launcher for the app package entry point."""

from app.main import main, run

__all__ = ["main", "run"]


if __name__ == "__main__":
    main()
