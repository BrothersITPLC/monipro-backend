# views/alert_insight_view.py

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from agents.agent import build_insight_agent
from zabbixproxy.functions.alert_functions.get_single_alert import get_single_alerts


class AlertInsightAPIView(APIView):

    def post(self, request):
        try:
            trigger_id = request.data.get("triggerid")
            if not trigger_id:
                return Response(
                    {"error": "Missing trigger ID"}, status=status.HTTP_400_BAD_REQUEST
                )

            alert_data = get_single_alerts(trigger_id)
            if "error" in alert_data:
                return Response(
                    {"error": alert_data["error"]},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            agent = build_insight_agent()
            result = agent.invoke({"alert": alert_data})

            return Response(
                {"insight": result["explanation"]}, status=status.HTTP_200_OK
            )

        except Exception as e:
            print(f"Error: {str(e)}")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
