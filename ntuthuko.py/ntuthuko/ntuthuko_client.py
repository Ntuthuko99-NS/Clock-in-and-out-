"""ntuthukoClient - data access layer (replaces the old base44Client).

Usage:
    from ntuthuko_client import ntuthukoClient
    ntuthukoClient.entities.Employee.filter(status="active")
    ntuthukoClient.entities.Alert.create(title="Hello")
"""
from database import get_db
from entities import ALL_SCHEMAS


class EntityManager:
    def __init__(self, schema):
        self.schema = schema
        self.table = schema["table"]
        self.fields = set(schema["fields"])

    # ---- helpers
    def _clean(self, data):
        return {k: v for k, v in data.items() if k in self.fields}

    def _order(self, order_by):
        if not order_by:
            return ""
        desc = order_by.startswith("-")
        col = order_by.lstrip("-")
        if col not in self.fields and col not in ("id", "created_at", "updated_at"):
            raise ValueError(f"Cannot order {self.schema['name']} by {col!r}")
        return f" ORDER BY {col} {'DESC' if desc else 'ASC'}"

    # ---- reads
    def list(self, order_by="-created_at", limit=None):
        return self.query("", (), order_by, limit)

    def query(self, where="", params=(), order_by=None, limit=None):
        sql = f"SELECT * FROM {self.table}"
        if where:
            sql += f" WHERE {where}"
        sql += self._order(order_by)
        if limit:
            sql += f" LIMIT {int(limit)}"
        return [dict(r) for r in get_db().execute(sql, params).fetchall()]

    def filter(self, order_by="-created_at", limit=None, **conditions):
        where, params = [], []
        for key, val in conditions.items():
            if key not in self.fields and key != "id":
                raise ValueError(f"Unknown field {key!r} on {self.schema['name']}")
            if val is None:
                where.append(f"{key} IS NULL")
            elif isinstance(val, (list, tuple)):
                where.append(f"{key} IN ({','.join('?' * len(val))})")
                params += list(val)
            else:
                where.append(f"{key} = ?")
                params.append(val)
        return self.query(" AND ".join(where), params, order_by, limit)

    def get(self, id_):
        row = get_db().execute(f"SELECT * FROM {self.table} WHERE id=?", (id_,)).fetchone()
        return dict(row) if row else None

    def first(self, **conditions):
        rows = self.filter(limit=1, **conditions)
        return rows[0] if rows else None

    def count(self, where="", params=()):
        sql = f"SELECT COUNT(*) FROM {self.table}" + (f" WHERE {where}" if where else "")
        return get_db().execute(sql, params).fetchone()[0]

    # ---- writes
    def create(self, **data):
        data = {**self.schema.get("defaults", {}), **self._clean(data)}
        missing = [f for f in self.schema.get("required", []) if data.get(f) in (None, "")]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")
        db = get_db()
        cur = db.execute(
            f"INSERT INTO {self.table} ({','.join(data)}) VALUES ({','.join('?' * len(data))})",
            list(data.values()))
        db.commit()
        return self.get(cur.lastrowid)

    def update(self, id_, **data):
        data = self._clean(data)
        if not data:
            return self.get(id_)
        sets = ", ".join(f"{k}=?" for k in data) + ", updated_at=datetime('now')"
        db = get_db()
        db.execute(f"UPDATE {self.table} SET {sets} WHERE id=?", [*data.values(), id_])
        db.commit()
        return self.get(id_)

    def delete(self, id_):
        db = get_db()
        db.execute(f"DELETE FROM {self.table} WHERE id=?", (id_,))
        db.commit()


class _Entities:
    def __init__(self):
        for name, schema in ALL_SCHEMAS.items():
            setattr(self, name, EntityManager(schema))


class _Client:
    def __init__(self):
        self.entities = _Entities()

    @staticmethod
    def raw(sql, params=()):
        return [dict(r) for r in get_db().execute(sql, params).fetchall()]


ntuthukoClient = _Client()
