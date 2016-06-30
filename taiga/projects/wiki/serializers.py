# -*- coding: utf-8 -*-
# Copyright (C) 2014-2016 Andrey Antukh <niwi@niwi.nz>
# Copyright (C) 2014-2016 Jesús Espino <jespinog@gmail.com>
# Copyright (C) 2014-2016 David Barragán <bameda@dbarragan.com>
# Copyright (C) 2014-2016 Alejandro Alonso <alejandro.alonso@kaleidos.net>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from taiga.base.api import serializers
from taiga.projects.history import services as history_service
from taiga.projects.notifications.mixins import WatchedResourceModelSerializer
from taiga.projects.notifications.validators import WatchersValidator
from taiga.mdrender.service import render as mdrender

from . import models

import serpy

class WikiPageSerializer(WatchedResourceModelSerializer, serializers.LightSerializer):
    id = serpy.Field()
    project = serpy.Field(attr="project_id")
    slug = serpy.Field()
    content = serpy.Field()
    owner = serpy.Field(attr="owner_id")
    last_modifier = serpy.Field(attr="last_modifier_id")
    created_date = serpy.Field()
    modified_date = serpy.Field()

    html = serpy.MethodField()
    editions = serpy.MethodField()

    version = serpy.Field()

    def get_html(self, obj):
        return mdrender(obj.project, obj.content)

    def get_editions(self, obj):
        return history_service.get_history_queryset_by_model_instance(obj).count() + 1  # +1 for creation


class WikiLinkSerializer(serializers.LightSerializer):
    id = serpy.Field()
    project = serpy.Field(attr="project_id")
    title = serpy.Field()
    href = serpy.Field()
    order = serpy.Field()
