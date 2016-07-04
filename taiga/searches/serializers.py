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

from taiga.projects.issues.models import Issue
from taiga.projects.userstories.models import UserStory
from taiga.projects.tasks.models import Task
from taiga.projects.wiki.models import WikiPage

import serpy

class IssueSearchResultsSerializer(serializers.LightSerializer):
    id = serpy.Field()
    ref = serpy.Field()
    subject = serpy.Field()
    status = serpy.Field(attr="status_id")
    assigned_to = serpy.Field(attr="assigned_to_id")


class TaskSearchResultsSerializer(serializers.LightSerializer):
    id = serpy.Field()
    ref = serpy.Field()
    subject = serpy.Field()
    status = serpy.Field(attr="status_id")
    assigned_to = serpy.Field(attr="assigned_to_id")


class UserStorySearchResultsSerializer(serializers.LightSerializer):
    id = serpy.Field()
    ref = serpy.Field()
    subject = serpy.Field()
    status = serpy.Field(attr="status_id")
    total_points = serpy.MethodField()
    milestone_name = serpy.MethodField()
    milestone_slug = serpy.MethodField()

    def get_milestone_name(self, obj):
        return obj.milestone.name if obj.milestone else None

    def get_milestone_slug(self, obj):
        return obj.milestone.slug if obj.milestone else None

    def get_total_points(self, obj):
        assert hasattr(obj, "total_points_attr"), "instance must have a total_points_attr attribute"
        return obj.total_points_attr


class WikiPageSearchResultsSerializer(serializers.LightSerializer):
    id = serpy.Field()
    slug = serpy.Field()
