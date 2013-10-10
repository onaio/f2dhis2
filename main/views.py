import json

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.utils import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.shortcuts import redirect
from django.utils.translation import ugettext as _
from requests_oauthlib import OAuth2Session

from main.forms import (DataSetImportForm, FormhubImportForm,
                        DataValueSetForm, FHDataElementForm)

from main.models import (FormhubService, DataQueue, DataValueSet, DataElement,
                         FormDataElement, DataSet, FormhubOAuthToken)
from main.tasks import process_dqueue
from main.utils import process_data_queue, basic_http_auth


def main(request):
    context = RequestContext(request)
    return render_to_response("index.html", context_instance=context)


def initiate_formhub_request(request, id_string, uuid):
    context = RequestContext(request)
    try:
        fs = FormhubService.objects.get(id_string=id_string)
    except FormhubService.DoesNotExist:
        context.contents = _(u"Unknown Service")
        context.status = False
    else:
        dq, created = DataQueue.objects.get_or_create(service=fs, data_id=uuid)
        dq.processed = False
        dq.save()
        context.status = context.status = True
        context.contents = _(u"OK")
        # call process queue asynchronously
        process_dqueue.delay()
    response = {"status": context.status, "contents": context.contents}
    if 'callback' in request.GET and request.GET.get('callback') != '':
        callback = request.GET.get('callback')
        return HttpResponse("%s(%s)" % (callback, json.dumps(response)),
                            mimetype='application/json')
    return HttpResponse(json.dumps(response), mimetype='application/json')


@basic_http_auth
@login_required
def dataset_import(request):
    context = RequestContext(request)
    context.form = DataSetImportForm()
    if request.method == 'POST':
        form = DataSetImportForm(request.POST)
        context.rs = form.ds_import()
        if context.rs is False:
            context.failed = True
    context.datasets = DataSet.objects.all()
    return render_to_response("dataset-import.html", context_instance=context)


def show_datasets(request):
    context = RequestContext(request)
    context.datasets = DataSet.objects.all()
    return render_to_response("dataset-import.html", context_instance=context)


@login_required
def formhub_import(request):
    context = RequestContext(request)
    context.form = FormhubImportForm()
    if request.method == 'POST':
        form = FormhubImportForm(request.POST)
        try:
            fhs = form.fh_import()
        except IntegrityError, e:
            context.message = _(u"Form has already been uploaded.")
        else:
            if fhs:
                context.fhservice = fhs
            else:
                context.message = _(u"Failed to import from formhub.")
    context.fhforms = FormhubService.objects.all()
    return  render_to_response("formhub-import.html", context_instance=context)


def show_formhub_forms(request):
    context = RequestContext(request)
    context.fhforms = FormhubService.objects.all()
    return  render_to_response("formhub-import.html", context_instance=context)


@login_required
def process_dataqueue(request):
    context = RequestContext(request)
    context.processed = process_data_queue()
    return render_to_response("process-queue.html", context_instance=context)


@login_required
def create_datavalueset(request):
    context = RequestContext(request)
    form = DataValueSetForm()
    if request.method == 'POST':
        form = DataValueSetForm(request.POST)
        if form.is_valid():
            form.save()
            context.success = True
    context.form = form
    return  render_to_response("dvs.html", context_instance=context)


@login_required
def match_datavalueset_to_data_elements(request):
    context = RequestContext(request)
    form = FHDataElementForm()
    context.fde_list = None
    if request.method == 'POST':
        form = FHDataElementForm(request.POST)
        dvs = DataValueSet.objects.get(pk=int(request.POST['dvs']))
        form.set_fh_fields(dvs.service)
        if form.is_valid():
            # form.save()
            de = DataElement.objects.get(pk=form.cleaned_data['data_elements'])
            try:
                fde = FormDataElement()
                fde.data_value_set = dvs
                fde.form_field = form.cleaned_data['fh_fields']
                fde.data_element = de
                fde.save()
            except IntegrityError:
                context.success = False
                context.msg = _(u"Match already saved.")
            else:
                context.success = True
                context.msg = _(u"Successfully saved.")
        else:
            context.success = False
            context.msg = _(u"Failed to save.")
        context.fde_list = list(FormDataElement.objects\
                        .filter(data_value_set=dvs)\
                        .values('data_value_set', 
                                'data_element__name', 'form_field'))
        if request.is_ajax():
            response = {'success': context.success, 'msg': context.msg,
                        'fde_list': context.fde_list}
            return HttpResponse(json.dumps(response))
    context.form = form
    return render_to_response("dvs-to-elements.html", context_instance=context)


def get_matchdvsform(request, dvs_id):
    """
    Returns the form elements string of FHDataElementForm
    given a data value set id
    """
    context = RequestContext(request)
    form = FHDataElementForm(request.GET)
    form.set_data_elements_choices(dvs_id)
    dvs = DataValueSet.objects.get(pk=dvs_id)
    form.set_fh_fields(dvs.service)
    context.form = form
    return render_to_response("dvs-to-elements-form.html",
                              context_instance=context)


@login_required
def oauth(request):
    # prepare the url based on the client id
    session = OAuth2Session(
        settings.FH_OAUTH_CLIENT_ID,
        redirect_uri=settings.FH_OAUTH_REDIRECT_URL)
    session.verify = settings.FH_OAUTH_VERIFY_SSL

    # check if we have both code and state params
    if 'code' in request.GET and 'state' in request.GET:
        # todo: check state against cached state from initial auth request
        token = session.fetch_token(
            settings.FH_OAUTH_TOKEN_URL, code=request.GET['code'])
        # store tokens
        try:
            stored_token = FormhubOAuthToken.objects.get(user=request.user)
        except FormhubOAuthToken.DoesNotExist:
            stored_token = FormhubOAuthToken(user=request.user)

        stored_token.access_token = token['access_token']
        stored_token.refresh_token = token['refresh_token']
        stored_token.token_type = token['token_type']
        stored_token.expires_in = token['expires_in']
        stored_token.scope = token['scope']
        stored_token.save()
        return redirect(formhub_import)
    elif 'error' in request.GET:
        return redirect(formhub_import)
    else:
        authorization_url, state = session.authorization_url(
            settings.FH_OAUTH_AUTHORIZE_URL)
        return HttpResponseRedirect(authorization_url)