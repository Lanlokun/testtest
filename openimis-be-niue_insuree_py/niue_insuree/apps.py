from django.apps import AppConfig

MODULE_NAME = "niue_insuree"

DEFAULT_CFG = {
    "gql_query_niue_insurees_perms": ["139001"],
    "gql_query_niue_insuree_perms": ["139001"],
    "gql_mutation_create_niue_insuree_perms": ["139002"],
    "gql_mutation_update_niue_insuree_perms": ["139003"],
    "gql_mutation_delete_niue_insuree_perms": ["139004"],
}

class NiueInsureeConfig(AppConfig):
    name = MODULE_NAME

    gql_query_niue_insurees_perms = []
    gql_query_niue_insuree_perms = []
    gql_mutation_create_niue_insuree_perms = []
    gql_mutation_update_niue_insuree_perms = []
    gql_mutation_delete_niue_insuree_perms = []

    def _configure_permissions(self, cfg):
        NiueInsureeConfig.gql_query_niue_insurees_perms = cfg["gql_query_niue_insurees_perms"]
        NiueInsureeConfig.gql_query_niue_insuree_perms = cfg["gql_query_niue_insuree_perms"]
        NiueInsureeConfig.gql_mutation_create_niue_insuree_perms = cfg["gql_mutation_create_niue_insuree_perms"]
        NiueInsureeConfig.gql_mutation_update_niue_insuree_perms = cfg["gql_mutation_update_niue_insuree_perms"]
        NiueInsureeConfig.gql_mutation_delete_niue_insuree_perms = cfg["gql_mutation_delete_niue_insuree_perms"]
    def ready(self):
        from core.models import ModuleConfiguration
        cfg = ModuleConfiguration.get_or_default(MODULE_NAME, DEFAULT_CFG)
        self._configure_permissions(cfg)