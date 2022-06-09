from django.apps import AppConfig


MODULE_NAME = 'service_provider'


DEFAULT_CFG = {
    "gql_query_service_provider_legalForms_perms": ["130001"],
    "gql_query_service_provider_legalForm_perms": ["130001"],
    "gql_mutation_create_service_provider_legalForm_perms": ["130002"],
    "gql_mutation_update_service_provider_legalForm_perms": ["130003"],
    "gql_mutation_delete_service_legalForm_perms": ["12004"],
    
    "gql_query_service_provider_levels_perms": ["130004"],
    "gql_query_service_provider_level_perms": ["130004"],
    "gql_mutation_create_service_provider_level_perms": ["130005"],
    "gql_mutation_update_service_provider_level_perms": ["130006"],
    "gql_mutation_delete_service_level_perms": ["12005"],
    
    "gql_query_service_provider_subLevels_perms": ["130007"],
    "gql_query_service_provider_subLevel_perms": ["130007"],
    "gql_mutation_create_service_provider_subLevel_perms": ["130008"],
    "gql_mutation_update_service_provider_subLevel_perms": ["130009"],
    "gql_mutation_delete_service_subLevel_perms": ["12006"],
    
    "gql_query_service_providers_perms": ["130011"],
    "gql_query_service_provider_perms": ["130011"],
    "gql_mutation_create_service_provider_perms": ["130012"],
    "gql_mutation_update_service_provider_perms": ["130013"],
    "gql_mutation_delete_service_provider_perms": ["12007"],
    
    "gql_query_pay_points_perms": ["130014"],
    "gql_query_pay_point_perms": ["130014"],
    "gql_mutation_create_pay_point_perms": ["130015"],
    "gql_mutation_update_pay_point_perms": ["130016"],
    "gql_mutation_delete_pay_point_perms": ["12008"]
}

class ServiceProviderConfig(AppConfig):
    name = MODULE_NAME
    
    gql_query_service_provider_legalForms_perms = []
    gql_query_service_provider_legalForm_perms = []
    gql_mutation_create_service_provider_legalForm_perms= []
    gql_mutation_update_service_provider_legalForm_perms= []
    gql_mutation_delete_service_legalForm_perms = []
    
    gql_query_service_provider_levels_perms = []
    gql_query_service_provider_level_perms = []
    gql_mutation_create_service_provider_level_perms = []
    gql_mutation_update_service_provider_level_perms = []
    gql_mutation_delete_service_level_perms = []
    
    gql_query_service_provider_subLevels_perms = []
    gql_query_service_provider_subLevel_perms = []
    gql_mutation_create_service_provider_subLevel_perms = []
    gql_mutation_update_service_provider_subLevel_perms = []
    gql_mutation_delete_service_subLevel_perms = []
    
    gql_query_service_providers_perms = []
    gql_query_service_provider_perms = []
    gql_mutation_create_service_provider_perms = []
    gql_mutation_update_service_provider_perms = []
    gql_mutation_delete_service_provider_perms = []
    
    gql_query_pay_points_perms = []
    gql_query_pay_point_perms = []
    gql_mutation_create_pay_point_perms = []
    gql_mutation_update_pay_point_perms = []
    gql_mutation_delete_pay_point_perms = []
    
    def _configure_permissions(self, cfg):
        
        ServiceProviderConfig.gql_query_service_provider_legalForms_perms = cfg["gql_query_service_provider_legalForms_perms"]
        ServiceProviderConfig.gql_query_service_provider_legalForm_perms = cfg["gql_query_service_provider_legalForm_perms"]
        ServiceProviderConfig.gql_mutation_create_service_provider_legalForm_perms = cfg["gql_mutation_create_service_provider_legalForm_perms"]
        ServiceProviderConfig.gql_mutation_update_service_provider_legalForm_perms = cfg["gql_mutation_update_service_provider_legalForm_perms"]
        ServiceProviderConfig.gql_mutation_delete_service_legalForm_perms = cfg["gql_mutation_delete_service_legalForm_perms"]

        
        ServiceProviderConfig.gql_query_service_provider_levels_perms = cfg["gql_query_service_provider_levels_perms"]
        ServiceProviderConfig.gql_query_service_provider_level_perms = cfg["gql_query_service_provider_level_perms"]
        ServiceProviderConfig.gql_mutation_create_service_provider_level_perms = cfg["gql_mutation_create_service_provider_level_perms"]
        ServiceProviderConfig.gql_mutation_update_service_provider_level_perms = cfg["gql_mutation_update_service_provider_level_perms"]
        ServiceProviderConfig.gql_mutation_delete_service_level_perms = cfg["gql_mutation_delete_service_level_perms"]

        
        ServiceProviderConfig.gql_query_service_provider_subLevels_perms = cfg["gql_query_service_provider_subLevels_perms"]
        ServiceProviderConfig.gql_query_service_provider_subLevel_perms = cfg["gql_query_service_provider_subLevel_perms"]
        ServiceProviderConfig.gql_mutation_create_service_provider_subLevel_perms = cfg["gql_mutation_create_service_provider_subLevel_perms"]
        ServiceProviderConfig.gql_mutation_update_service_provider_subLevel_perms = cfg["gql_mutation_update_service_provider_subLevel_perms"]
        ServiceProviderConfig.gql_mutation_delete_service_subLevel_perms = cfg["gql_mutation_delete_service_subLevel_perms"]

        
        ServiceProviderConfig.gql_query_service_providers_perms = cfg["gql_query_service_providers_perms"]
        ServiceProviderConfig.gql_query_service_provider_perms = cfg["gql_query_service_provider_perms"]
        ServiceProviderConfig.gql_mutation_create_service_provider_perms = cfg["gql_mutation_create_service_provider_perms"]
        ServiceProviderConfig.gql_mutation_update_service_provider_perms = cfg["gql_mutation_update_service_provider_perms"]
        ServiceProviderConfig.gql_mutation_delete_service_provider_perms = cfg["gql_mutation_delete_service_provider_perms"]

        ServiceProviderConfig.gql_query_pay_points_perms = cfg["gql_query_pay_points_perms"]
        ServiceProviderConfig.gql_query_pay_point_perms = cfg["gql_query_pay_point_perms"]
        ServiceProviderConfig.gql_mutation_create_pay_point_perms = cfg["gql_mutation_create_pay_point_perms"]
        ServiceProviderConfig.gql_mutation_update_pay_point_perms = cfg["gql_mutation_update_pay_point_perms"]
        ServiceProviderConfig.gql_mutation_delete_pay_point_perms = cfg["gql_mutation_delete_pay_point_perms"]

    def ready(self):
        from core.models import ModuleConfiguration
        cfg = ModuleConfiguration.get_or_default(MODULE_NAME, DEFAULT_CFG)
        self._configure_permissions(cfg)
