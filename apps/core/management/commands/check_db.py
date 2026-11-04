from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import connections


class Command(BaseCommand):
    help = "Testa a ligação à base MySQL partilhada e compara as colunas com os models."

    def handle(self, *args, **opts):
        conn = connections["selfcheckout"]
        try:
            conn.ensure_connection()
        except Exception as exc:  # noqa: BLE001
            self.stderr.write(self.style.ERROR(f"Falha na ligação: {exc}"))
            raise SystemExit(1)
        self.stdout.write(self.style.SUCCESS(f"Ligação OK -> {conn.settings_dict['HOST']}/{conn.settings_dict['NAME']}"))
        ok = True
        with conn.cursor() as cur:
            tables = set(conn.introspection.table_names(cur))
            for model in apps.get_models():
                if model._meta.app_label not in ("customers", "products", "sales", "payments"):
                    continue
                t = model._meta.db_table
                if t not in tables:
                    ok = False
                    self.stdout.write(self.style.ERROR(f"  ✗ tabela em falta: {t}"))
                    continue
                cols = {c.name for c in conn.introspection.get_table_description(cur, t)}
                want = {f.column for f in model._meta.concrete_fields}
                missing = want - cols
                if missing:
                    ok = False
                    self.stdout.write(self.style.ERROR(f"  ✗ {t}: colunas em falta {sorted(missing)}"))
                else:
                    cur.execute(f"SELECT COUNT(*) FROM `{t}`")
                    self.stdout.write(f"  ✓ {t}: {cur.fetchone()[0]} registos")
        if not ok:
            raise SystemExit(1)
