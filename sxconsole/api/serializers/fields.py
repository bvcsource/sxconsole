# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

import datetime

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from sizefield.utils import parse_size


class SizeField(serializers.Field):

    def to_representation(self, num):
        """Output machine-readable values."""
        return num

    def to_internal_value(self, data):
        """Accept human-readable input."""
        try:
            return parse_size(data)
        except ValueError:
            return


class ChoicesField(serializers.ChoiceField):
    """Field for handling djchoices. It uses choice names instead of ids."""

    def __init__(self, *args, **kwargs):
        # Process default
        default = kwargs.pop('default', None)
        if default:
            kwargs['default'] = default
        # Process choices
        self.choices_class = kwargs.pop('choices')
        choices = []
        for id, desc in self.choices_class.choices:
            display_name = self.choices_class.values[id]
            choices.append((id, display_name))
        kwargs['choices'] = choices
        super(ChoicesField, self).__init__(*args, **kwargs)

    def to_representation(self, choice):
        return choice

    def to_internal_value(self, name):
        return name


def validate_future_date(date):
    today = datetime.date.today()
    if date < today:
        raise serializers.ValidationError(
            _("You can't set a date in the past."),
        )


class ClusterExpirationField(serializers.DateField):
    validators = (validate_future_date,)

    def get_attribute(self, obj):
        return obj.expiration

    def to_representation(self, cluster_expiration):
        """Output machine-readable values."""
        if cluster_expiration is not None:
            return cluster_expiration.expiration_date
