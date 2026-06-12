from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view
import requests

# Create your views here.

PREDICTIONS_ENDPOINT = 'http://ec2-54-226-35-6.compute-1.amazonaws.com:8000/predictions'


def _json_safe_payload(payload):
	try:
		return dict(payload)
	except (TypeError, ValueError):
		return payload


def _read_upstream_error(response):
	content_type = response.headers.get('content-type', '')
	if 'application/json' in content_type:
		try:
			return {
				'type': 'json',
				'body': response.json(),
			}
		except ValueError:
			pass

	text = response.text.strip()
	return {
		'type': 'text' if text else 'empty',
		'body': text or None,
	}


def _prediction_error_payload(*, detail, request_payload, upstream_status=None, upstream_error=None, exception=None):
	payload = {
		'detail': detail,
		'upstream': {
			'url': PREDICTIONS_ENDPOINT,
			'status_code': upstream_status,
			'error': upstream_error,
		},
		'request_payload': _json_safe_payload(request_payload),
	}
	if exception is not None:
		payload['upstream']['exception'] = {
			'type': exception.__class__.__name__,
			'message': str(exception),
		}
	return payload


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
	except requests.Timeout as exc:
		return JsonResponse(
			_prediction_error_payload(
				detail='Prediction service timed out.',
				request_payload=request.data,
				exception=exc,
			),
			status=504,
		)
	except requests.RequestException as exc:
		return JsonResponse(
			_prediction_error_payload(
				detail='Prediction service is unavailable.',
				request_payload=request.data,
				exception=exc,
			),
			status=502,
		)

	if not upstream_response.ok:
		upstream_error = _read_upstream_error(upstream_response)
		return JsonResponse(
			_prediction_error_payload(
				detail='Prediction service returned an error.',
				request_payload=request.data,
				upstream_status=upstream_response.status_code,
				upstream_error=upstream_error,
			),
			status=upstream_response.status_code,
		)

	content_type = upstream_response.headers.get('content-type', 'application/json')
	return HttpResponse(
		upstream_response.content,
		status=upstream_response.status_code,
		content_type=content_type,
	)
