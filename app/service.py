import json
import uuid
from fastapi import HTTPException
from .platform import database, fingerprint
from .domain import assess

class Rollouts:
    def __init__(self, path):
        self.path = path
        with database(path) as db:
            db.execute('CREATE TABLE IF NOT EXISTS evaluations(tenant TEXT,id TEXT,idem TEXT,digest TEXT,result TEXT,PRIMARY KEY(tenant,id),UNIQUE(tenant,idem))')

    def evaluate(self, tenant, command):
        digest = fingerprint(command.model_dump(exclude={'idempotency_key'}))
        with database(self.path) as db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute('SELECT * FROM evaluations WHERE tenant=? AND idem=?', (tenant, command.idempotency_key)).fetchone()
            if row:
                if row['digest'] != digest: raise HTTPException(409, 'Idempotency conflict')
                return json.loads(row['result'])
            result = {'id': str(uuid.uuid4()), 'service': command.service,
                      **assess(command.baseline_ms, command.candidate_ms, command.max_regression)}
            db.execute('INSERT INTO evaluations VALUES(?,?,?,?,?)', (tenant, result['id'], command.idempotency_key, digest, json.dumps(result)))
            return result

    def history(self, tenant):
        with database(self.path) as db:
            return [json.loads(r[0]) for r in db.execute('SELECT result FROM evaluations WHERE tenant=? ORDER BY rowid DESC LIMIT 50', (tenant,))]
