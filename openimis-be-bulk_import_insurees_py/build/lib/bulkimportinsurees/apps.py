from django.apps import AppConfig

MODULE_NAME = "bulkimportinsurees"

DEFAULT_CFG = {
    "gql_query_bulkimportinsurees_perms": ["130010"],
}

class BulkimportinsureesConfig(AppConfig):
    name = MODULE_NAME

    gql_query_bulkimportinsurees_perms = []

    def _configure_permissions(self, cfg):
        BulkimportinsureesConfig.gql_query_bulkimportinsurees_perms = cfg["gql_query_bulkimportinsurees_perms"]
        

    def ready(self):
        from core.models import ModuleConfiguration
        cfg = ModuleConfiguration.get_or_default(MODULE_NAME, DEFAULT_CFG)
        self._configure_permissions(cfg)
