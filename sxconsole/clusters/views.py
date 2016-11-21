# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''
import datetime
import json
from urllib import quote

from celery import states as celery_states
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.db.models.query import Q
from django.http import JsonResponse, StreamingHttpResponse, Http404
from django.shortcuts import redirect, get_object_or_404
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _, get_language
from django.views import generic
from sxclient.exceptions import SXClientException

from sxconsole import core
from sxconsole.accounts.forms import EmailForm
from sxconsole.accounts.models import Admin
from sxconsole.models import TaskMeta
from sxconsole.utils import clusters
from sxconsole.utils.decorators import super_admin_only, regular_cluster_only
from sxconsole.utils.views import ClusterViewMixin, PaginationMixin
from . import forms
from .access_log.fetch import prepare_access_log
from .models import AccessLogEntryModel
from .tasks import s3import


@super_admin_only
class CreateClusterView(generic.CreateView):
    """Creates a new Cluster."""
    template_name = 'clusters/cluster_form.html'
    form_class = forms.CreateClusterForm
    url_name = 'add_cluster'
    title = _("Adding a new cluster")

    def get_context_data(self, **kwargs):
        ctx = super(CreateClusterView, self).get_context_data(**kwargs)
        size_init = {
            'minValue': core._min_volume_size,
            'maxValue': clusters.get_free_cluster_space(),
        }
        try:
            size_init['value'] = ctx['form'].cleaned_data['size']
        except (AttributeError, KeyError):
            pass
        ctx['size_init'] = json.dumps(size_init)
        return ctx

    def form_valid(self, form):
        try:
            response = super(CreateClusterView, self).form_valid(form)
        except SXClientException as e:
            form.add_error(None, core.get_exception_msg(e))
            if form.instance.pk:
                form.instance.delete()
            return self.form_invalid(form)
        self.add_admin(form.cleaned_data['email'], self.object)
        return response

    def add_admin(self, email, cluster):
        """Add admin for the created cluster and notify the user."""
        if not email:
            return
        admin, invited = Admin.get_or_invite(email)
        if invited:
            messages.info(self.request, _(
                "Invitation has been sent to {}").format(email))
        cluster.admins.add(admin)


class DisplayClusterView(ClusterViewMixin, generic.DetailView):
    """Display a Cluster page."""
    template_name = 'clusters/cluster.html'
    url_name = 'cluster_detail'
    context_object_name = 'cluster'

    @property
    def title(self):
        return str(self.object)

    def get_context_data(self, **kwargs):
        cluster = Q(_clusters=self.object)
        regular_admin = Q(level=Admin.LEVELS.ADMIN)
        if self.request.user.is_superadmin:
            admins = Admin.objects.filter(cluster | ~regular_admin).distinct()
        else:
            admins = Admin.objects.filter(cluster & regular_admin)

        return super(DisplayClusterView, self).get_context_data(
            cluster_admins=admins,
            stats_data=self.get_stats_data(),
            **kwargs)

    def get_stats_data(self):
        def stat(value, limit):
            return {
                'value': value,
                'limit': limit,
            }

        c = self.object
        users = stat(len(c.users), c.max_users)
        volumes = stat(len(c.volumes), c.max_volumes)
        allocated_space = stat(clusters.get_allocated_space(c), c.size)
        space_usage = stat(c.used_size, c.size)

        stats_data = {
            'users': users,
            'volumes': volumes,
            'allocatedSpace': allocated_space,
            'spaceUsage': space_usage,
        }
        return json.dumps(stats_data)


@super_admin_only
@regular_cluster_only
class UpdateClusterView(ClusterViewMixin, generic.UpdateView):
    """Creates a new Cluster."""
    template_name = 'clusters/cluster_form.html'
    form_class = forms.ClusterForm
    url_name = 'edit_cluster'

    @property
    def title(self):
        return _("Updating {}").format(self.object)

    def get_initial(self):
        initial = super(UpdateClusterView, self).get_initial()
        if self.object.expiration:
            initial['expiration_date'] = self.object.expiration.expiration_date
        return initial

    def get_context_data(self, **kwargs):
        ctx = super(UpdateClusterView, self).get_context_data(**kwargs)
        vcluster_size = self.object.size or 0
        try:
            value = ctx['form'].cleaned_data['size']
        except (AttributeError, KeyError):
            value = vcluster_size
        size_init = {
            'minValue': core._min_volume_size,
            'maxValue': clusters.get_free_cluster_space() + vcluster_size,
            'value': value,
        }
        ctx['size_init'] = json.dumps(size_init)
        return ctx

    def form_valid(self, form):
        try:
            response = super(UpdateClusterView, self).form_valid(form)
        except SXClientException as e:
            form.add_error(None, core.get_exception_msg(e))
            return self.form_invalid(form)
        return response


@super_admin_only
@regular_cluster_only
class DeleteClusterView(ClusterViewMixin, generic.DeleteView):
    """Creates a new Cluster."""
    template_name = 'delete.html'
    success_url = reverse_lazy('home')
    url_name = 'delete_cluster'

    def dispatch(self, *args, **kwargs):
        if self.object.can_be_deleted():
            return super(DeleteClusterView, self).dispatch(*args, **kwargs)
        messages.error(self.request, _(
            "To delete a cluster, delete its users and volumes first."))
        return redirect(self.object)

    @property
    def title(self):
        return _("Deleting {}").format(self.object)


@super_admin_only
@regular_cluster_only
class AddClusterAdminView(ClusterViewMixin, generic.FormView):
    """Adds an admin to the cluster administrators."""
    template_name = 'simple_form.html'
    form_class = EmailForm
    url_name = 'add_cluster_admin'

    @property
    def title(self):
        return _("New admin for {}").format(self.object)

    def form_valid(self, form):
        email = form.cleaned_data['email']
        admin, invited = Admin.get_or_invite(email)
        if invited:
            messages.info(self.request, _(
                "Invitation has been sent to {}").format(email))
        elif admin.is_superadmin:
            msg = _("User {} cannot be added").format(admin.email)
            form.add_error(None, msg)
            return self.form_invalid(form)

        self.object.admins.add(admin)
        return redirect(self.object)


@super_admin_only
@regular_cluster_only
class RemoveClusterAdminView(ClusterViewMixin, generic.TemplateView):
    """Removes an admin from the cluster administrators."""
    template_name = 'clusters/remove_admin.html'
    url_name = 'remove_cluster_admin'

    @property
    def title(self):
        return _("Removing admin {} from {}").format(self.admin, self.object)

    @cached_property
    def admin(self):
        return get_object_or_404(Admin, pk=self.kwargs['admin_pk'])

    def post(self, *args, **kwargs):
        self.object.admins.remove(self.admin)
        return redirect(self.object)


class AccessLogsFormView(ClusterViewMixin, generic.FormView):
    """Display access logs for the cluster."""
    form_class = forms.LogsFiltersForm
    url_name = 'access_logs_form'
    template_name = 'clusters/logs/form.html'

    def get_initial(self):
        initial = super(AccessLogsFormView, self).get_initial()
        today = datetime.date.today()
        initial['from_date'] = initial['till_date'] = today
        return initial

    def get_form_kwargs(self):
        kwargs = super(AccessLogsFormView, self).get_form_kwargs()
        if 'data' not in kwargs:
            kwargs['data'] = self.request.GET or kwargs['initial']
        return kwargs

    def form_valid(self, form):
        data = form.cleaned_data
        task = prepare_access_log(
            admin=self.request.user,
            from_=data['from_date'],
            till=data['till_date'],
            vcluster=(None if self.object.is_root else self.object.name),
            volume=data.get('volume_filter'),
            user=data.get('user_filter'),
        )
        return JsonResponse({'task_id': task.id})


class AccessLogsResultsView(ClusterViewMixin, PaginationMixin,
                            generic.FormView):
    form_class = forms.LogsFiltersForm
    template_name = 'clusters/logs/results.html'
    url_name = 'access_logs_result'
    page_size = 50

    @cached_property
    def task(self):
        try:
            return TaskMeta.objects.get(pk=self.kwargs['task_id'])
        except TaskMeta.DoesNotExist:
            raise Http404()

    def dispatch(self, *args, **kwargs):
        if self.task.status == celery_states.SUCCESS:
            return super(AccessLogsResultsView, self).dispatch(*args, **kwargs)
        else:
            raise Http404()

    def get_initial(self):
        query = self.task.info['query']
        return {
            'from_date': query['from'],
            'till_date': query['till'],
            'volume_filter': query['volume'],
            'user_filter': query['user'],
        }

    def get_pagination_source(self):
        task_id = self.task.id
        entries = AccessLogEntryModel.objects.filter(task_id=task_id)
        return entries


class SearchClustersView(generic.View):
    """Return a list of clusters matching the query."""
    url_name = 'search_clusters_ajax'

    def get(self, *args, **kwargs):
        query = self.request.GET.get('query')
        if query:
            clusters = self.request.user.clusters \
                .regular() \
                .filter(name__icontains=query)[:10]
        else:
            clusters = []
        clusters = [{'pk': c.pk, 'name': c.name} for c in clusters]
        return JsonResponse(clusters, safe=False)


@regular_cluster_only
class S3ImportView(ClusterViewMixin, generic.FormView):
    """Imports data from S3."""
    template_name = 'clusters/s3import/form.html'
    form_class = forms.S3ImportForm
    url_name = 's3import'
    title = _("Import data from an S3 service")

    def get_context_data(self, **kwargs):
        context = super(S3ImportView, self).get_context_data(**kwargs)
        context['pk'] = self.kwargs['pk']
        tasks = TaskMeta.objects.filter(
            type=TaskMeta.TYPES.S3IMPORT, cluster_id=context['pk']) \
            .order_by('-queue_date')
        context['tasks'] = tasks
        return context

    def get_form_kwargs(self):
        kwargs = super(S3ImportView, self).get_form_kwargs()
        kwargs['cluster'] = self.object
        return kwargs

    def form_valid(self, form):
        pk = self.object.pk
        lang = get_language()
        email = self.request.user.email
        task = s3import.import_from_s3.delay(
            s3_host=form.cleaned_data['s3_host'],
            s3_port=form.cleaned_data['s3_port'],
            s3_key_id=form.cleaned_data['s3_key_id'],
            s3_secret_key=form.cleaned_data['s3_secret_key'],
            email_address=email,
            cluster_pk=pk,
            default_size=form.cleaned_data['default_size'],
            replica_count=form.cleaned_data['replicas'],
            s3_validate_certs=form.cleaned_data['s3_validate_certs'],
            language=lang)
        owner_id = Admin.objects.get(email=email).id
        TaskMeta.objects.create(
            id=task.id, cluster_id=pk, admin_id=owner_id,
            type=TaskMeta.TYPES.S3IMPORT)
        return redirect('s3import_single_task', pk=pk, taskid=task.task_id)


@regular_cluster_only
class S3ImportSingleTaskView(ClusterViewMixin, generic.TemplateView):
    """Contains the status info of an S3 import task."""
    template_name = 'clusters/s3import/task_status.html'
    url_name = 's3import_single_task'
    title = _("S3 import task status")

    def get_context_data(self, **kwargs):
        context = super(S3ImportSingleTaskView, self) \
            .get_context_data(**kwargs)
        task = TaskMeta.objects.get(id=self.kwargs['taskid'])

        context['ready'] = task.ready
        context['end_date'] = task.end_date
        context['status'] = task.status
        if isinstance(task.info, Exception):
            context['info'] = ': '.join(
                [type(task.info).__name__, str(task.info)])
        else:
            context['info'] = None
        if task.status == 'PROGRESS':
            context['copied'] = task.info.get('copied', 0)
            context['skipped'] = task.info.get('skipped', 0)
            context['total'] = task.info.get('total', 0)
            context['current_from'] = task.info.get('current_from', '')
            context['current_to'] = task.info.get('current_to', '')
            context['data_size'] = task.info.get('data_size', None)
        try:
            # Try to obtain the lists from an exception object
            # - either both are present or none is
            context['imported_buckets'] = task.info.imported_buckets
            context['skipped_buckets'] = task.info.skipped_buckets
        except AttributeError:
            # Try to obtain the lists from a result dict
            # - either both are present or none is
            try:
                context['imported_buckets'] = (
                    task.info.get('imported_buckets', None))
                context['skipped_buckets'] = (
                    task.info.get('skipped_buckets', None))
            except AttributeError:
                context['imported_buckets'] = None
                context['skipped_buckets'] = None
        return context


def download_response(stream, filename):
    """Util for serving a file."""
    response = StreamingHttpResponse(
        stream,
        content_type='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename=' + \
        quote(filename.encode('utf-8'))
    return response
