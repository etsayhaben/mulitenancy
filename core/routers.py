# core/routers.py

class TenantRouter:
    """
    A router to control all database operations on models in the tenant_db application.
    """

    route_app_labels = {'tenant_db'}

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            # Get current tenant from middleware/thread local/request
            # This is simplified — you need to store current tenant info globally per request
            return self.get_current_tenant_db()
        return 'default'

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return self.get_current_tenant_db()
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        # Allow relations if both models are in the same app or one is in master
        if (
            obj1._meta.app_label in self.route_app_labels and
            obj2._meta.app_label in self.route_app_labels
        ):
            return True
        elif (
            obj1._meta.app_label not in self.route_app_labels and
            obj2._meta.app_label not in self.route_app_labels
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.route_app_labels:
            # Only allow tenant models to migrate on tenant DBs
            # You must run migrate manually per tenant DB
            return db != 'default'
        return db == 'default'

    def get_current_tenant_db(self):
        # You need to implement a way to get current tenant DB name
        # e.g., from thread local storage set by middleware
        # For demo, return a fixed name — YOU MUST IMPLEMENT THIS
        return 'tenant_company_a'