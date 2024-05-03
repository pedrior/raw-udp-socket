from enum import Enum

class Request(Enum):
    Datetime = 0
    MotivationQuote = 1
    ServerStats = 2


def humanize_resquest(request: Request) -> str:
    if request == Request.Datetime:
        return 'Data e hora'
    elif request == Request.MotivationQuote:
        return 'Frase de motivação'
    else:
        return 'Estatísticas do servidor'
