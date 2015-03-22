from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required

from gf.gas.models import GAS

@login_required
def index(request):
    context = {
        'gas_list' : GAS.objects.filter(gasmember__person__user=request.user),
        'user' : request.user
    }
    return render_to_response("ui_ric1/index.html", context)