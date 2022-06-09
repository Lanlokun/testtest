from django.apps import AppConfig

MODULE_NAME = "payrollcycle"

DEFAULT_CFG = {
    "gql_query_payroll_cycles_perms": ["130001"],
    "gql_query_payroll_cycle_perms": ["130001"],
    "gql_mutation_create_payroll_cycle_perms": ["130002"],
    "gql_mutation_update_payroll_cycle_perms": ["130003"],
    "gql_mutation_delete_payroll_cycle_perms": ["130004"],
}

class PayrollCycleConfig(AppConfig):
    name = MODULE_NAME

    gql_query_payroll_cycles_perms = []
    gql_query_payroll_cycle_perms = []
    gql_mutation_create_payroll_cycle_perms = []
    gql_mutation_update_payroll_cycle_perms = []
    gql_mutation_delete_payroll_cycle_perms = []

    def _configure_permissions(self, cfg):
        PayrollCycleConfig.gql_query_payroll_cycles_perms = cfg["gql_query_payroll_cycles_perms"]
        PayrollCycleConfig.gql_query_payroll_cycle_perms = cfg["gql_query_payroll_cycle_perms"]
        PayrollCycleConfig.gql_mutation_create_payroll_cycle_perms = cfg["gql_mutation_create_payroll_cycle_perms"]
        PayrollCycleConfig.gql_mutation_update_payroll_cycle_perms = cfg["gql_mutation_update_payroll_cycle_perms"]
        PayrollCycleConfig.gql_mutation_delete_payroll_cycle_perms = cfg["gql_mutation_delete_payroll_cycle_perms"]

    def ready(self):
        from core.models import ModuleConfiguration
        cfg = ModuleConfiguration.get_or_default(MODULE_NAME, DEFAULT_CFG)
        self._configure_permissions(cfg)