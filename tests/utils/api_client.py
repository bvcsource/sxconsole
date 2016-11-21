# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

import json

from rest_framework.test import APIClient


class BetterAPIClient(APIClient):
    """Implements status code checks and json parsing."""

    def _check_response(self, response, status, parse):
        # Check staus code
        if status is not None:
            assert response.status_code == status, \
                'expected: {}, got: {}, response:\n{}' \
                .format(status, response.status_code, response.content)
        # Parse response body
        if parse:
            response.data = json.loads(response.content)

    def _process_data(self, data, content_type):
        if content_type == 'application/json':
            data = json.dumps(data)
        return data

    def get(self, path, data=None, follow=False, status=200, parse=True,
            content_type='application/json', **extra):
        response = super(BetterAPIClient, self).get(
            path, data=data, follow=follow, **extra)
        self._check_response(response, status, parse)
        return response

    def post(self, path, data=None, format=None,
             content_type='application/json', follow=False, status=201,
             parse=True, **extra):
        data = self._process_data(data, content_type)
        response = super(BetterAPIClient, self).post(
            path, data=data, format=format, content_type=content_type, **extra)
        self._check_response(response, status, parse)
        return response

    def put(self, path, data=None, format=None,
            content_type='application/json', follow=False, status=200,
            parse=True, **extra):
        data = self._process_data(data, content_type)
        response = super(APIClient, self).put(
            path, data=data, format=format, content_type=content_type, **extra)
        self._check_response(response, status, parse)
        return response

    def patch(self, path, data=None, format=None,
              content_type='application/json', follow=False, status=200,
              parse=True, **extra):
        data = self._process_data(data, content_type)
        response = super(APIClient, self).patch(
            path, data=data, format=format, content_type=content_type, **extra)
        self._check_response(response, status, parse)
        return response

    def delete(self, path, data=None, format=None,
               content_type='application/json', follow=False, status=204,
               parse=True, **extra):
        data = self._process_data(data, content_type)
        response = super(APIClient, self).delete(
            path, data=data, format=format, content_type=content_type, **extra)
        return response
