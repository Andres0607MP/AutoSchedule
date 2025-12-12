from rest_framework import serializers
from .models import QueueTicket
from datetime import datetime, date

class QueueTicketSerializer(serializers.ModelSerializer):
    hora_estimada = serializers.TimeField(required=False)

    class Meta:
        model = QueueTicket
        fields = '__all__'

    def validate(self, data):
        """
        Si solo envían la hora, completar la fecha automáticamente (hoy).
        Si envían fecha+hora completa también funciona.
        """
        hora = data.get("hora_estimada")

        if isinstance(hora, datetime):
            return data

        if hora:
            hoy = date.today()
            data["hora_estimada"] = datetime.combine(hoy, hora)

        return data
