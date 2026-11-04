"""Encaminha as tabelas do Self-Checkout para a base partilhada e impede migrations nela."""
BUSINESS_APPS = {"customers", "products", "sales", "payments"}
SHARED = "selfcheckout"


class SelfCheckoutRouter:
    def db_for_read(self, model, **hints):
        return SHARED if model._meta.app_label in BUSINESS_APPS else None

    db_for_write = db_for_read

    def allow_relation(self, a, b, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if db == SHARED or app_label in BUSINESS_APPS:
            return False
        return db == "default"
