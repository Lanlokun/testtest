
from django.apps import AppConfig

MODULE_NAME = "payrollbulkimport"

DEFAULT_CFG = {
    "gql_query_payrollbulkimport_perms": ["131010"],
}

class PayrollBulkimportConfig(AppConfig):
    name = MODULE_NAME

    gql_query_bulkimportinsurees_perms = []

    def _configure_permissions(self, cfg):
        PayrollBulkimportConfig.gql_query_payrollbulkimport_perms = cfg["gql_query_payrollbulkimport_perms"]
        

    def ready(self):
        from core.models import ModuleConfiguration
        cfg = ModuleConfiguration.get_or_default(MODULE_NAME, DEFAULT_CFG)
        self._configure_permissions(cfg)
