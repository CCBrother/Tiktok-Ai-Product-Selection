from __future__ import annotations

from backend.app.database.session import SessionLocal
from backend.app.services.mock_data_service import generate_mock_data


def main() -> None:
    with SessionLocal() as db:
        result = generate_mock_data(db)
    print(result)


if __name__ == "__main__":
    main()
