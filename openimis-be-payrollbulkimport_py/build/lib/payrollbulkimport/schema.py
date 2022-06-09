from core.schema import signal_mutation_module_validate
from django.db.models import Q
import graphene
from django.core.exceptions import PermissionDenied
from graphene_django.filter import DjangoFilterConnectionField
from core import prefix_filterset, filter_validity
from core import models as core_models
from core.schema import TinyInt, SmallInt, OpenIMISMutation, OrderedDjangoFilterConnectionField
from .models import *
from django.utils.translation import gettext as _
import graphene_django_optimizer as gql_optimizer

from .gql_mutations import *

class Mutation(graphene.ObjectType):
    create_bulk_import_payroll = CreateBulkImportPayrollMutation.Field()
