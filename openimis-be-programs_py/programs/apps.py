from django.apps import AppConfig

MODULE_NAME = "programs"

DEFAULT_CFG = {
    "gql_query_prSchemes_perms": ["130001"],
    "gql_query_prScheme_perms": ["130001"],
    "gql_mutation_create_prScheme_perms": ["130002"],
    "gql_mutation_update_prScheme_perms": ["130003"],
    "gql_mutation_delete_prScheme_perms": ["13004"],
    "gql_query_programs_perms": ["130005"],
    "gql_mutation_create_programs_perms": ["130006"],
    "gql_mutation_update_programs_perms": ["130007"],
    "gql_mutation_delete_programs_perms": ["13008"],
    "gql_mutation_duplicate_perSchemes_perms" :["13009"],
}

class ProgramsConfig(AppConfig):
    name = 'programs'

    gql_query_prSchemes_perms = []
    gql_query_prScheme_perms = []
    gql_mutation_create_prScheme_perms = []
    gql_mutation_update_prScheme_perms = []
    gql_mutation_delete_prScheme_perms = []
    gql_query_programs_perms = []
    gql_mutation_create_programs_perms = []
    gql_mutation_update_programs_perms = []
    gql_mutation_delete_programs_perms = []
    gql_mutation_duplicate_perSchemes_perms =[]

    def _configure_permissions(self, cfg):
        ProgramsConfig.gql_query_prSchemes_perms = cfg["gql_query_prSchemes_perms"]
        ProgramsConfig.gql_query_prScheme_perms = cfg["gql_query_prScheme_perms"]
        ProgramsConfig.gql_mutation_create_prScheme_perms = cfg["gql_mutation_create_prScheme_perms"]
        ProgramsConfig.gql_mutation_update_prScheme_perms = cfg["gql_mutation_update_prScheme_perms"]
        ProgramsConfig.gql_mutation_delete_prScheme_perms = cfg["gql_mutation_delete_prScheme_perms"]
        ProgramsConfig.gql_query_programs_perms = cfg["gql_query_programs_perms"]
        ProgramsConfig.gql_mutation_create_programs_perms = cfg["gql_mutation_create_programs_perms"]
        ProgramsConfig.gql_mutation_update_programs_perms = cfg["gql_mutation_update_programs_perms"]
        ProgramsConfig.gql_mutation_delete_programs_perms = cfg["gql_mutation_delete_programs_perms"]
        ProgramsConfig.gql_mutation_duplicate_perSchemes_perms = cfg["gql_mutation_duplicate_perScheme_perms"]

    def ready(self):
        from core.models import ModuleConfiguration
        cfg = ModuleConfiguration.get_or_default(MODULE_NAME, DEFAULT_CFG)
        self._configure_permissions(cfg)