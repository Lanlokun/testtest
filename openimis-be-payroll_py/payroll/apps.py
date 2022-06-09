from django.apps import AppConfig

MODULE_NAME = "payroll"

DEFAULT_CFG = {
    "gql_query_payroll_perms": ["130005"],
    "gql_mutation_create_payroll_perms": ["130006"],
    "gql_mutation_update_payroll_perms": ["130007"],
    "gql_mutation_delete_payroll_perms": ["130008"],
}

class PayrollConfig(AppConfig):
    name = MODULE_NAME

    gql_query_payroll_cycle_perms = []
    gql_mutation_create_payroll_perms = []
    gql_mutation_update_payroll_perms = []
    gql_mutation_delete_payroll_perms = []

    def _configure_permissions(self, cfg):
        PayrollConfig.gql_query_payroll_perms = cfg["gql_query_payroll_perms"]
        PayrollConfig.gql_mutation_create_payroll_perms = cfg["gql_mutation_create_payroll_perms"]
        PayrollConfig.gql_mutation_update_payroll_perms = cfg["gql_mutation_update_payroll_perms"]
        PayrollConfig.gql_mutation_delete_payroll_perms = cfg["gql_mutation_delete_payroll_perms"]

    def ready(self):
        from core.models import ModuleConfiguration
        cfg = ModuleConfiguration.get_or_default(MODULE_NAME, DEFAULT_CFG)
        self._configure_permissions(cfg)
