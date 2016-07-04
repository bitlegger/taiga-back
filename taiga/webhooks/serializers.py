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

from django.core.exceptions import ObjectDoesNotExist

from taiga.base.api import serializers
from taiga.base.fields import PgArrayField, JsonField

from taiga.front.templatetags.functions import resolve as resolve_front_url

from taiga.projects.history import models as history_models
from taiga.projects.issues import models as issue_models
from taiga.projects.milestones import models as milestone_models
from taiga.projects.services import get_logo_big_thumbnail_url
from taiga.projects.tasks import models as task_models
from taiga.projects.tagging.fields import TagsField
from taiga.projects.userstories import models as us_models
from taiga.projects.wiki import models as wiki_models

from taiga.users.gravatar import get_gravatar_url
from taiga.users.services import get_photo_or_gravatar_url

from .models import Webhook, WebhookLog

import serpy

########################################################################
## WebHooks
########################################################################

class WebhookSerializer(serializers.LightSerializer):
    id = serpy.Field()
    project = serpy.Field(attr="project_id")
    name = serpy.Field()
    url = serpy.Field()
    key = serpy.Field()
    logs_counter = serpy.MethodField()

    def get_logs_counter(self, obj):
        return obj.logs.count()


class WebhookLogSerializer(serializers.LightSerializer):
    id = serpy.Field()
    webhook = serpy.Field()
    url = serpy.Field()
    status = serpy.Field()
    request_data = serpy.Field()
    request_headers = serpy.Field()
    response_data = serpy.Field()
    response_headers = serpy.Field()
    duration = serpy.Field()
    created = serpy.Field()


########################################################################
## User
########################################################################

class UserSerializer(serializers.LightSerializer):
    id = serpy.Field(attr="pk")
    permalink = serpy.MethodField()
    gravatar_url = serpy.MethodField()
    username = serpy.MethodField()
    full_name = serpy.MethodField()
    photo = serpy.MethodField()

    def get_permalink(self, obj):
        return resolve_front_url("user", obj.username)

    def get_gravatar_url(self, obj):
        return get_gravatar_url(obj.email)

    def get_username(self, obj):
        return obj.get_username()

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_photo(self, obj):
        return get_photo_or_gravatar_url(obj)

    def to_value(self, instance):
        if instance is None:
            return None

        return super().to_value(instance)

########################################################################
## Project
########################################################################

class ProjectSerializer(serializers.LightSerializer):
    id = serpy.Field(attr="pk")
    permalink = serpy.MethodField()
    name = serpy.MethodField()
    logo_big_url = serpy.MethodField()

    def get_permalink(self, obj):
        return resolve_front_url("project", obj.slug)

    def get_name(self, obj):
        return obj.name

    def get_logo_big_url(self, obj):
        return get_logo_big_thumbnail_url(obj)


########################################################################
## History Serializer
########################################################################

class HistoryDiffField(serpy.Field):
    def to_value(self, value):
        # Tip: 'value' is the object returned by
        #      taiga.projects.history.models.HistoryEntry.values_diff()

        ret = {}

        for key, val in value.items():
            if key in ["attachments", "custom_attributes"]:
                ret[key] = val
            elif key == "points":
                ret[key] = {k: {"from": v[0], "to": v[1]} for k, v in val.items()}
            else:
                ret[key] = {"from": val[0], "to": val[1]}

        return ret


class HistoryEntrySerializer(serializers.LightSerializer):
    comment = serpy.Field()
    comment_html = serpy.Field()
    delete_comment_date = serpy.Field()
    comment_versions = serpy.Field()
    edit_comment_date = serpy.Field()
    diff = HistoryDiffField(attr="values_diff")


########################################################################
## _Misc_
########################################################################

class CustomAttributesValuesWebhookSerializerMixin(serializers.LightSerializer):
    custom_attributes_values = serpy.MethodField()

    def custom_attributes_queryset(self, project):
        raise NotImplementedError()

    def get_custom_attributes_values(self, obj):
        def _use_name_instead_id_as_key_in_custom_attributes_values(custom_attributes, values):
            ret = {}
            for attr in custom_attributes:
                value = values.get(str(attr["id"]), None)
                if value is not  None:
                    ret[attr["name"]] = value

            return ret

        try:
            values =  obj.custom_attributes_values.attributes_values
            custom_attributes = self.custom_attributes_queryset(obj.project).values('id', 'name')

            return _use_name_instead_id_as_key_in_custom_attributes_values(custom_attributes, values)
        except ObjectDoesNotExist:
            return None


class RolePointsSerializer(serializers.LightSerializer):
    role = serpy.MethodField()
    name = serpy.MethodField()
    value = serpy.MethodField()

    def get_role(self, obj):
        return obj.role.name

    def get_name(self, obj):
        return obj.points.name

    def get_value(self, obj):
        return obj.points.value


class UserStoryStatusSerializer(serializers.LightSerializer):
    id = serpy.Field(attr="pk")
    name = serpy.MethodField()
    slug = serpy.MethodField()
    color = serpy.MethodField()
    is_closed = serpy.MethodField()
    is_archived = serializers.serpy.MethodField()

    def get_name(self, obj):
        return obj.name

    def get_slug(self, obj):
        return obj.slug

    def get_color(self, obj):
        return obj.color

    def get_is_closed(self, obj):
        return obj.is_closed

    def get_is_archived(self, obj):
        return obj.is_archived


class TaskStatusSerializer(serializers.LightSerializer):
    id = serpy.Field(attr="pk")
    name = serpy.MethodField()
    slug = serpy.MethodField()
    color = serpy.MethodField()
    is_closed = serpy.MethodField()


    def get_name(self, obj):
        return obj.name

    def get_slug(self, obj):
        return obj.slug

    def get_color(self, obj):
        return obj.color

    def get_is_closed(self, obj):
        return obj.is_closed


class IssueStatusSerializer(serializers.LightSerializer):
    id = serpy.Field(attr="pk")
    name = serpy.MethodField()
    slug = serpy.MethodField()
    color = serpy.MethodField()
    is_closed = serpy.MethodField()

    def get_name(self, obj):
        return obj.name

    def get_slug(self, obj):
        return obj.slug

    def get_color(self, obj):
        return obj.color

    def get_is_closed(self, obj):
        return obj.is_closed


class IssueTypeSerializer(serializers.LightSerializer):
    id = serpy.Field(attr="pk")
    name = serpy.MethodField()
    color = serpy.MethodField()


    def get_name(self, obj):
        return obj.name

    def get_color(self, obj):
        return obj.color


class PrioritySerializer(serializers.LightSerializer):
    id = serpy.Field(attr="pk")
    name = serpy.MethodField()
    color = serpy.MethodField()


    def get_name(self, obj):
        return obj.name

    def get_color(self, obj):
        return obj.color


class SeveritySerializer(serializers.LightSerializer):
    id = serpy.Field(attr="pk")
    name = serpy.MethodField()
    color = serpy.MethodField()


    def get_name(self, obj):
        return obj.name

    def get_color(self, obj):
        return obj.color


########################################################################
## Milestone
########################################################################

class MilestoneSerializer(serializers.LightSerializer):
    id = serpy.Field()
    name = serpy.Field()
    slug = serpy.Field()
    estimated_start = serpy.Field()
    estimated_finish = serpy.Field()
    created_date = serpy.Field()
    modified_date = serpy.Field()
    closed = serpy.Field()
    disponibility = serpy.Field()
    permalink = serializers.SerializerMethodField("get_permalink")
    project = ProjectSerializer()
    owner = UserSerializer()

    def get_permalink(self, obj):
        return resolve_front_url("taskboard", obj.project.slug, obj.slug)


########################################################################
## User Story
########################################################################

class UserStorySerializer(CustomAttributesValuesWebhookSerializerMixin, serializers.LightSerializer):
    id = serpy.Field()
    ref = serpy.Field()
    project = ProjectSerializer()
    is_closed = serpy.Field()
    created_date = serpy.Field()
    modified_date = serpy.Field()
    finish_date = serpy.Field()
    subject = serpy.Field()
    client_requirement = serpy.Field()
    team_requirement = serpy.Field()
    generated_from_issue = serpy.Field(attr="generated_from_issue_id")
    external_reference = serpy.Field()
    tribe_gig = serpy.Field()
    watchers = serpy.MethodField()
    is_blocked = serpy.Field()
    blocked_note = serpy.Field()
    tags = serpy.Field()
    permalink = serializers.SerializerMethodField("get_permalink")
    owner = UserSerializer()
    assigned_to = UserSerializer()
    points = serpy.MethodField()
    status = UserStoryStatusSerializer()
    milestone = MilestoneSerializer()

    def get_permalink(self, obj):
        return resolve_front_url("userstory", obj.project.slug, obj.ref)

    def custom_attributes_queryset(self, project):
        return project.userstorycustomattributes.all()

    def get_watchers(self, obj):
        return list(obj.get_watchers().values_list("id", flat=True))

    def get_points(self, obj):
        return RolePointsSerializer(obj.role_points.all(), many=True).data

########################################################################
## Task
########################################################################

class TaskSerializer(CustomAttributesValuesWebhookSerializerMixin, serializers.LightSerializer):
    id = serpy.Field()
    ref = serpy.Field()
    created_date = serpy.Field()
    modified_date = serpy.Field()
    finished_date = serpy.Field()
    subject = serpy.Field()
    us_order = serpy.Field()
    taskboard_order = serpy.Field()
    is_iocaine = serpy.Field()
    external_reference = serpy.Field()
    watchers = serpy.MethodField()
    is_blocked = serpy.Field()
    blocked_note = serpy.Field()
    description = serpy.Field()
    tags = serpy.Field()
    permalink = serializers.SerializerMethodField("get_permalink")
    project = ProjectSerializer()
    owner = UserSerializer()
    assigned_to = UserSerializer()
    status = TaskStatusSerializer()
    user_story = UserStorySerializer()
    milestone = MilestoneSerializer()

    def get_permalink(self, obj):
        return resolve_front_url("task", obj.project.slug, obj.ref)

    def custom_attributes_queryset(self, project):
        return project.taskcustomattributes.all()

    def get_watchers(self, obj):
        return list(obj.get_watchers().values_list("id", flat=True))

########################################################################
## Issue
########################################################################

class IssueSerializer(CustomAttributesValuesWebhookSerializerMixin, serializers.LightSerializer):
    id = serpy.Field()
    ref = serpy.Field()
    created_date = serpy.Field()
    modified_date = serpy.Field()
    finished_date = serpy.Field()
    subject = serpy.Field()
    external_reference = serpy.Field()
    watchers = serpy.MethodField()
    description = serpy.Field()
    tags = serpy.Field()
    permalink = serializers.SerializerMethodField("get_permalink")
    project = ProjectSerializer()
    milestone = MilestoneSerializer()
    owner = UserSerializer()
    assigned_to = UserSerializer()
    status = IssueStatusSerializer()
    type = IssueTypeSerializer()
    priority = PrioritySerializer()
    severity = SeveritySerializer()

    def get_permalink(self, obj):
        return resolve_front_url("issue", obj.project.slug, obj.ref)

    def custom_attributes_queryset(self, project):
        return project.issuecustomattributes.all()

    def get_watchers(self, obj):
        return list(obj.get_watchers().values_list("id", flat=True))

########################################################################
## Wiki Page
########################################################################

class WikiPageSerializer(serializers.LightSerializer):
    id = serpy.Field()
    slug = serpy.Field()
    content = serpy.Field()
    created_date = serpy.Field()
    modified_date = serpy.Field()
    permalink = serializers.SerializerMethodField("get_permalink")
    project = ProjectSerializer()
    owner = UserSerializer()
    last_modifier = UserSerializer()

    def get_permalink(self, obj):
        return resolve_front_url("wiki", obj.project.slug, obj.slug)
