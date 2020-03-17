import dataclasses
import datetime

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy

import core.generic.mixins
import core.generic.views

from core import forms
from core.mis.direction import Direction
from core.mis.service_client import Mis


class Search(PermissionRequiredMixin, core.generic.mixins.FormMixin, core.generic.mixins.RestListMixin,
             core.generic.views.ListView):
    template_name = 'core/directions/list.html'
    form_class = forms.DirectionSearch
    title = 'Направления'
    permission_required = 'core.view_direction'
    paginate_by = 50
    mis_request_path = Mis.DIRECTIONS_LIST_URL

    def get_breadcrumbs(self):
        return [
            ('Главная', reverse('core:index')),
            (self.title, ''),
        ]

    def get_initial(self):
        initial = super().get_initial()
        initial['date_from'] = datetime.date.today()
        return initial

    def get_filter_params(self):
        return dict(self.request.GET) or self.get_initial()


class Edit(PermissionRequiredMixin, core.generic.views.EditView):
    template_name = 'core/directions/edit.html'
    form_class = forms.DirectionEdit
    data_method = 'post'
    pk_url_kwarg = 'number'

    def get_success_url(self):
        return reverse_lazy('core:direction_list')

    def get_permission_required(self):
        perm = 'core.add_direction'
        if self.get_object():
            perm = 'core.change_direction'

        return [perm]

    def get_initial(self):
        initial = super().get_initial()
        obj = self.get_object()
        if obj:
            initial.update(dataclasses.asdict(obj))
            if initial.get('org'):
                initial['org'] = initial['org']['id']

            if initial.get('law_items_section_1'):
                initial['law_items_section_1'] = [l_i['id'] for l_i in initial['law_items_section_1']]

            if initial.get('law_items_section_2'):
                initial['law_items_section_2'] = [l_i['id'] for l_i in initial['law_items_section_2']]

            if initial.get('pay_method'):
                initial['pay_method'] = initial['pay_method']['id']

        return initial

    def get_object(self):
        object_pk = self.kwargs.get(self.pk_url_kwarg)
        if object_pk:
            self.object = Direction.get(direction_id=object_pk)

        return self.object

    def form_valid(self, form):
        if self.kwargs.get(self.pk_url_kwarg):
            success, description = Direction.edit(direction_id=self.kwargs[self.pk_url_kwarg], params=form.cleaned_data)
        else:
            success, description = Direction.create(params=form.cleaned_data)

        if success:
            messages.success(self.request, description)
        else:
            messages.error(self.request, description)
            return self.form_invalid(form)

        return redirect(self.get_success_url())

    def get_breadcrumbs(self):
        return [
            ('Главная', reverse('core:index')),
            ('Направления', reverse('core:direction_list')),
            (self.get_title(), ''),
        ]


class Delete(PermissionRequiredMixin, core.generic.views.DeleteView):
    success_url = reverse_lazy('core:direction_list')
    breadcrumb = 'Удалить'
    permission_required = 'core.delete_direction'
    pk_url_kwarg = 'number'

    def get_object(self, *args, **kwargs):
        object_pk = self.kwargs.get(self.pk_url_kwarg)
        self.object = Direction.get(direction_id=object_pk)

        return self.object

    def get_breadcrumbs(self):
        direction = self.get_object()
        return [
            ('Главная', reverse('core:index')),
            ('Направления', reverse('core:direction_list')),
            (direction, reverse('core:direction_edit', kwargs={'number': direction.number})),
            (self.breadcrumb, ''),
        ]

    def delete(self, *args, **kwargs):
        success, description = Direction.delete(direction_id=self.kwargs.get(self.pk_url_kwarg))

        if success:
            messages.success(self.request, description)
        else:
            messages.error(self.request, description)
            return self.render_to_response(self.get_context_data())

        return redirect(self.success_url)