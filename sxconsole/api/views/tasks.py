# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

from rest_framework.decorators import api_view
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from sxconsole.api.serializers import TaskMetaSerializer


@api_view()
def task_status(request, *args, **kwargs):
    serializer_class = TaskMetaSerializer
    model = serializer_class.Meta.model
    tasks_queryset = model.objects.visible_to(request.user)

    task_id = kwargs['uuid']
    try:
        task = tasks_queryset.get(id=task_id)
    except (ValueError, model.DoesNotExist):
        raise NotFound()
    serializer = serializer_class(task)
    return Response(serializer.data)
