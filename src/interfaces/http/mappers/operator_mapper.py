from src.core.operator.read_models.operator_search_read_model import OperatorSearchReadModel
from src.interfaces.http.models.operator_model import OperatorsResponse

def map_operator_model_to_response(read_model: OperatorSearchReadModel) -> OperatorsResponse:
    return OperatorsResponse(
        id=read_model.id,
        name=read_model.name,
        description=read_model.description,
        logo=read_model.logo,
        foundation_year=read_model.foundation_year,
        rating=read_model.rating,
        reviews_count=read_model.reviews_count,
        specialisations=read_model.specialisations,
        features=read_model.features,
        certificates=read_model.certificates,
        verified=read_model.verified
    )
