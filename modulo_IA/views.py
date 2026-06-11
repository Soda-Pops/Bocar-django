from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view
import requests

# Create your views here.

PREDICTIONS_ENDPOINT = 'http://ec2-54-226-35-6.compute-1.amazonaws.com:8000/predictions'


@require_http_methods(["GET", "POST"])
def panel_reentrenamiento(request):
	reentrenamiento_solicitado = request.method == 'POST'
	return render(
		request,
		'modulo_ia/panel_reentrenamiento.html',
		{
			'reentrenamiento_solicitado': reentrenamiento_solicitado,
		},
	)


@api_view(['POST'])
def predictions_proxy(request):
	try:
		upstream_response = requests.post(
			PREDICTIONS_ENDPOINT,
			json=request.data,
			timeout=30,
		)
	except requests.Timeout:
		return JsonResponse(
			{'detail': 'Prediction service timed out.'},
			status=504,
		)
	except requests.RequestException:
		return JsonResponse(
			{'detail': 'Prediction service is unavailable.'},
			status=502,
		)

	content_type = upstream_response.headers.get('content-type', 'application/json')
	return HttpResponse(
		upstream_response.content,
		status=upstream_response.status_code,
		content_type=content_type,
	)
