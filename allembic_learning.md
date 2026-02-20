Modify: Change your SQLAlchemy models in app/models/.

Generate: Run alembic revision --autogenerate -m "what changed".

Inspect: Open the new file in alembic/versions/. Always scan the upgrade() function to ensure it’s only doing what you expect.

Apply: Run alembic upgrade head.

```
alembic revision --autogenerate -m "baseline_existing_schema"
 1108  alembic revision --autogenerate -m "baseline_existing_schema"
 1109  alembic revision --autogenerate -m "baseline_existing_schema"
 1110  alembic revision --autogenerate -m "baseline_existing_schema"
 1111  alembic revision --autogenerate -m "baseline_existing_schema"
 1112  alembic stamp head
 1113  alembic current
 1114  alembic revision --autogenerate -m "add middle_name to users"
 1115  alembic revision --autogenerate -m "add middle_name to users"
 1116  alembic revision --autogenerate -m "add middle_name to users"
 1117  alembic stamp base
 1118  alembic upgrade head
 1119  alembic current
 1120  alembic stamp 8b4a05c39346
 1121  alembic upgrade head
 1122  alembic current


```