from enum import Enum

RES_INVALID = 3


class ResourceType(Enum):
    Datetime = 0
    MotivationQuote = 1
    ServerStats = 2


def humanize_resource_type(resource: ResourceType) -> str:
    if resource == ResourceType.Datetime:
        return 'Data e hora'
    elif resource == ResourceType.MotivationQuote:
        return 'Frase de motivação'
    else:
        return 'Estatísticas do servidor'
