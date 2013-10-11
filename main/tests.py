import base64
import urlparse
import requests

from httmock import HTTMock, urlmatch
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from main import views
from main.models import DataSet, FormhubService, FormhubOAuthToken
from main.utils import (get_valid_token, make_formhub_request,
                        fh_oauth_authorize_url, fh_oauth_token_url,
                        fh_test_form_path)


class TestBase(TestCase):
    def setUp(self):
        self.username = 'bob'
        self.password = 'bob'
        self.client = Client()
        self.base_url = 'http://testserver'
        self.ds_url = u'http://apps.dhis2.org/demo/api/dataSets/pBOMPrpg1QX'
        self.fh_url = u"http://formhub.org/ukanga/forms/dhis2form"
        self.ds_import_url = reverse(views.dataset_import)
        self.fh_import_url = reverse(views.formhub_import)

    def _create_user(self, username, password):
        user, created = User.objects.get_or_create(username=username)
        user.set_password(password)
        user.save()
        return user

    def _login(self, username, password):
        client = Client()
        assert client.login(username=username, password=password)
        return client

    def _create_user_and_login(self):
        self.user = self._create_user(self.username, self.password)
        self.client = self._login(self.username, self.password)

    def _set_auth_headers(self, username, password):
        return {
            'HTTP_AUTHORIZATION': 'Basic ' + base64.b64encode('%s:%s' \
                % (username, password)),
            }

    def _import_dataset(self):
        post_data = {'data_set_url': self.ds_url}
        response = self.client.post(self.ds_import_url, post_data)
        self.assertEqual(response.status_code, 200)

    def _import_formhub_form(self):
        post_data = {'formhub_url': self.fh_url}
        response = self.client.post(self.fh_import_url, post_data)
        self.assertEqual(response.status_code, 200)


class Main(TestBase):
    def test_index_page(self):
        response = self.client.get(reverse(views.main))
        self.assertEqual(response.status_code, 200)

    def test_import_dataset(self):
        response = self.client.get(self.ds_import_url)
        # need to login first, should redirect
        self.assertEqual(response.status_code, 401)
        self._create_user_and_login()
        # should be successful this time
        response = self.client.get(self.ds_import_url)
        self.assertEqual(response.status_code, 200)
        # check saved Dataset
        count = DataSet.objects.count()
        self.assertEqual(count, 0)
        self._import_dataset()
        self.assertEqual(DataSet.objects.count(), count + 1)

    def test_import_formhub_form(self):
        response = self.client.get(self.ds_import_url)
        # need to login first, should redirect
        self.assertEqual(response.status_code, 401)
        self._create_user_and_login()
        # should be successful this time
        response = self.client.get(self.fh_import_url)
        self.assertEqual(response.status_code, 200)
        # check saved Formhub service
        count = FormhubService.objects.count()
        self.assertEqual(count, 0)
        self._import_formhub_form()
        self.assertEqual(FormhubService.objects.count(), count + 1)

    def test_show_datasets(self):
        response = self.client.get(reverse(views.show_datasets))
        self.assertEqual(response.status_code, 200)

    def test_show_formhub_forms(self):
        response = self.client.get(reverse(views.show_formhub_forms))
        self.assertEqual(response.status_code, 200)

    def test_basic_http_authentication(self):
        url = reverse(views.dataset_import)
        # not logged in, redirects
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)
        self._create_user(self.username, self.password)
        # pass in Basic HTTP Authentication headers, invalid user/pass
        response = self.client.get(url,
            **self._set_auth_headers('dummy', 'nonexistent'))
        self.assertEqual(response.status_code, 401)
        # pass in Basic HTTP Authentication headers, correct user/pass
        response = self.client.get(url,
            **self._set_auth_headers(self.username, self.password))
        self.assertEqual(response.status_code, 200)


@urlmatch(netloc=r'^test.formhub$', path='/o/token/')
def formhub_oauth_token_mock(url, request):
    # only return success if the required params are set
    valid = True
    auth = "Basic {}".format(
        base64.b64encode("{}:{}".format(
            settings.FH_OAUTH_CLIENT_ID, settings.FH_OAUTH_CLIENT_SECRET)))
    if request.headers.get('Authorization') != auth:
        valid = False

    if valid:
        response = {
            'status_code': 200,
            'content': {
                "access_token": "Q6dJBs9Vkf7a2lVI7NKLT8F7c6DfLD",
                "token_type": "Bearer",
                "expires_in": 36000,
                "refresh_token": "53yF3uz79K1fif2TPtNBUFJSFhgnpE",
                "scope": "read write groups"
            }
        }
    else:
        response = {
            'status_code': 401,
            'content': {}
        }
    return response


@urlmatch(netloc=r'^test.formhub$',
          path='/api/v1/forms/larryweya/714/form.json')
def formhub_form_mock(url, request):
    # only return success if the required params are set
    valid = True

    if 'Authorization' in request.headers and "Bearer" not in\
            request.headers.get('Authorization'):
        valid = False

    if valid:
        response = {
            'status_code': 200,
            'content': {
                "default_language": "default",
                "id_string": "good_eats",
                "children": [
                    {
                        "name": "submit_data",
                        "type": "today"
                    }
                ]
            }
        }
    else:
        response = {
            'status_code': 403
        }
    return response


@urlmatch(netloc=r'^test.formhub$', path='/o/authorize/')
def formhub_oauth_authorize_mock(url, request):
    response = {
        'status_code': 302,
        'headers': {
            'Location': "{0}?state=pDrle4isHK1oGLOsVMTMHvzHu5lglq"
                        "&code=jkHxxuM9kvI5dqozYpxNufD9lHhpd8".format(
                settings.FH_OAUTH_REDIRECT_URL)
        }
    }
    return response


class TestFHOAuth(TestBase):
    def setUp(self):
        super(TestFHOAuth, self).setUp()
        self._create_user_and_login()

    def _get_auth_token(self):
        url = reverse(views.oauth)
        fh_authorize_url = self.client.get(url)['location']
        with HTTMock(formhub_oauth_authorize_mock):
            response = requests.get(fh_authorize_url)
        params = urlparse.parse_qs(
            urlparse.urlparse(response.headers['Location']).query)
        return params['state'][0], params['code'][0]

    def test_redirect_to_token_url(self):
        url = reverse(views.oauth)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        parsed_url = urlparse.urlparse(response['location'])
        expected_location = "{0}://{1}{2}".format(
            parsed_url.scheme, parsed_url.netloc, parsed_url.path)
        self.assertEqual(expected_location, fh_oauth_authorize_url())
        params = urlparse.parse_qs(parsed_url.query)
        self.assertIn(settings.FH_OAUTH_CLIENT_ID, params['client_id'])
        self.assertIn(settings.FH_OAUTH_REDIRECT_URL, params['redirect_uri'])

    def test_token_request(self):
        """
        Test when the authorization request is redirected back to our application
        """
        state, code = self._get_auth_token()
        url = reverse(views.oauth)
        with HTTMock(formhub_oauth_token_mock):
            response = self.client.get(url, {
                'state': state,
                'code': code
            })
        self.assertIn(
            "Your account has been linked.", response.cookies['messages'].value)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            urlparse.urlparse(response['location']).path,
            reverse(views.formhub_import))

    def test_subsequent_token_request(self):
        """
        Test subsequent auth token requests are handled gracefully
        """
        state, code = self._get_auth_token()
        url = reverse(views.oauth)
        with HTTMock(formhub_oauth_token_mock):
            response = self.client.get(url, {
                'state': state,
                'code': code
            })
        with HTTMock(formhub_oauth_token_mock):
            response = self.client.get(url, {
                'state': state,
                'code': code
            })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            urlparse.urlparse(response['location']).path,
            reverse(views.formhub_import))

    def test_redirect_on_user_cancel_auth(self):
        """
        Test that we redirect to the formhub_import view if the user cancels the authorization request
        """
        url = reverse(views.oauth)
        response = self.client.get(url, {
            'error': 'access_denied'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            urlparse.urlparse(response['location']).path,
            reverse(views.formhub_import))

    def test_make_formhub_request_without_token(self):
        url = fh_test_form_path()
        method = 'GET'

        with HTTMock(formhub_form_mock):
            response = make_formhub_request(url, method)
        self.assertEqual(response.status_code, 200)

    def test_make_formhub_request_with_valid_token(self):
        token = FormhubOAuthToken(user=self.user)
        token.access_token = 'aBCDe'
        token.refresh_token = '1234'
        token.token_type = 'Bearer'
        token.expires_in = 36000
        token.scope = "['read', 'write']"

        url = fh_test_form_path()
        method = 'GET'

        with HTTMock(formhub_form_mock, formhub_oauth_token_mock):
            response = make_formhub_request(url, method, None, token)
        self.assertEqual(response.status_code, 200)

    def test_make_formhub_request_with_expired_token(self):
        token = FormhubOAuthToken(user=self.user)
        token.access_token = 'aBCDe'
        token.refresh_token = '1234'
        token.token_type = 'Bearer'
        token.expires_in = -1800
        token.scope = "['read', 'write']"

        url = fh_test_form_path()
        method = 'GET'

        with HTTMock(formhub_form_mock, formhub_oauth_token_mock):
            response = make_formhub_request(url, method, None, token)
        self.assertEqual(response.status_code, 200)
