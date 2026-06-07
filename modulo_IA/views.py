from django.shortcuts import render
from django.views.decorators.http import require_http_methods

# Create your views here.


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
