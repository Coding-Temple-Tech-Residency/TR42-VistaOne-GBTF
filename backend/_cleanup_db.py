"""Temporary script to clean up all tables and types from the database."""
from app import create_app
from app.extensions import db

app = create_app()
with app.app_context():
    # Drop all tables except PostGIS ones
    result = db.session.execute(db.text(
        "SELECT tablename FROM pg_tables "
        "WHERE schemaname='public' "
        "AND tablename NOT IN ('spatial_ref_sys')"
    ))
    tables = [r[0] for r in result]
    for t in tables:
        db.session.execute(db.text(f'DROP TABLE IF EXISTS "{t}" CASCADE'))

    # Drop all custom types/domains
    result = db.session.execute(db.text(
        "SELECT typname, typtype FROM pg_type "
        "JOIN pg_namespace ON pg_type.typnamespace = pg_namespace.oid "
        "WHERE nspname = 'public' AND typtype IN ('e', 'd') "
        "ORDER BY typname"
    ))
    types = [(r[0], r[1]) for r in result]
    for name, tt in types:
        if tt == 'd':
            db.session.execute(db.text(f'DROP DOMAIN IF EXISTS {name} CASCADE'))
        else:
            db.session.execute(db.text(f'DROP TYPE IF EXISTS {name} CASCADE'))

    db.session.commit()
    print(f'Dropped {len(tables)} tables and {len(types)} types')
