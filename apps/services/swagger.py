from drf_spectacular.utils import extend_schema, OpenApiParameter

service_list_docs = extend_schema(
    parameters=[
        OpenApiParameter(name="name", description="Filtrar por nombre", required=False, type=str),
        OpenApiParameter(name="category", description="Filtrar por categoría", required=False, type=str),
        OpenApiParameter(name="duration_gte", description="Duración mínima", required=False, type=int),
        OpenApiParameter(name="duration_lte", description="Duración máxima", required=False, type=int),
    ]
)
