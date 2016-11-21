# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

from django.db import models
from djchoices.choices import DjangoChoicesMeta


class ChoiceField(models.CharField):

    def __init__(self, **kwargs):
        choices = kwargs['choices']
        if isinstance(choices, DjangoChoicesMeta):
            kwargs['choices'] = choices.choices
            kwargs['max_length'] = max(len(l) for l in choices.values)

        super(ChoiceField, self).__init__(**kwargs)
