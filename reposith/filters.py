import django_filters
from autenticad.models import Media

class MediaFilter(django_filters.FilterSet):
    # Aqui você pode adicionar campos para filtrar
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains', label="Nome da Imagem")
    description = django_filters.CharFilter(field_name='description', lookup_expr='icontains', label="Descrição")
    event_date = django_filters.DateFilter(field_name='event_date', lookup_expr='exact', label="Data do Evento")

    class Meta:
        model = Media
        fields = ['name', 'description', 'event_date']  # Campos pelos quais você pode filtrar
