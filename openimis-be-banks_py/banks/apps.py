from django.apps import AppConfig

MODULE_NAME = "banks"

DEFAULT_CFG = {
    "gql_query_prBanks_perms": ["131001"],
    "gql_query_prBank_perms": ["131001"],
    "gql_mutation_create_prBank_perms": ["131002"],
    "gql_mutation_update_prBank_perms": ["131003"],
    "gql_mutation_delete_prBank_perms": ["131004"],
}


class BanksConfig(AppConfig):
    name = 'banks'


    gql_query_prBanks_perms = []
    gql_query_prBank_perms = []
    gql_mutation_create_prBanks_perms = []
    gql_mutation_update_prBanks_perms = []
    gql_mutation_delete_prBanks_perms = []



    def _configure_permissions(self, cfg):
        BanksConfig.gql_query_prBanks_perms = cfg["gql_query_prBanks_perms"]
        BanksConfig.gql_query_prBank_perms = cfg["gql_query_prBank_perms"]
        BanksConfig.gql_mutation_create_prBanks_perms = cfg["gql_mutation_create_prBank_perms"]
        BanksConfig.gql_mutation_update_prBanks_perms = cfg["gql_mutation_update_prBank_perms"]
        BanksConfig.gql_mutation_delete_prBanks_perms = cfg["gql_mutation_delete_prBank_perms"]


    def ready(self):
        from core.models import ModuleConfiguration
        cfg = ModuleConfiguration.get_or_default(MODULE_NAME, DEFAULT_CFG)
        self._configure_permissions(cfg)