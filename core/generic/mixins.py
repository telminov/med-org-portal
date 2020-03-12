from django.core.paginator import Paginator
from django.http import HttpResponse
from django.utils.functional import cached_property
from django.views.generic.base import ContextMixin
from django.views.generic.edit import FormMixin as DjangoFormMixin


class RestPaginator(Paginator):
    def __init__(self, object_list, per_page, count, *arg, **kwargs):
        super().__init__(object_list, per_page, *arg, **kwargs)
        self._count = count

    @cached_property
    def count(self):
        return self._count


class RestListMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.count = None
        self.have_next = None
        self.have_previous = None

    def get_paginator(self, queryset, per_page, **kwargs):
        return RestPaginator(queryset, per_page, self.count or 0)

    def get_page_numbers(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        numbers = []
        if queryset:
            page = int(self.request.GET.get('page', 1))
            per_page = self.get_paginate_by(queryset)

            pag = self.get_paginator(queryset, per_page)
            all_numbers = list(pag.page_range)

            start = page - 4 if page - 4 > 1 else 0
            end = page + 3
            numbers = all_numbers[start:end]

        return self.have_previous, numbers, self.have_next


class FormMixin(DjangoFormMixin):
    data_method = None

    def get_form_kwargs(self):
        kwargs = {
            'initial': self.get_initial(),
            'prefix': self.get_prefix(),
        }

        kwargs.update({
            'data': getattr(self.request, self.data_method.upper() if self.data_method else 'GET') or None,
            'files': self.request.FILES or None
        })
        return kwargs


class BreadcrumbsMixin(ContextMixin):

    def get_breadcrumbs(self):
        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = self.get_breadcrumbs()
        return context


class TitleMixin(ContextMixin):
    title = None

    def get_title(self):
        return self.title

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.get_title()
        return context


class ExcelMixin:
    excel_name = None
    excel_method = 'get'
    excel_workbook_maker = None
    excel_params = ['excel']

    def get_workbook_maker(self):
        return self.excel_workbook_maker

    def get_excel(self) -> HttpResponse:
        maker = self.get_workbook_maker()
        workbook_maker_kwargs = self.get_workbook_maker_kwargs()

        maker_instance = maker(**workbook_maker_kwargs)
        excel_response = maker_instance.create_workbook()
        return excel_response

    def get_workbook_maker_kwargs(self, **kwargs):
        kwargs.update({
            'objects': self.get_queryset(),
            'title': self.get_excel_title(),
            'page': self.request.GET.get('page')
        })

        return kwargs

    def get_excel_title(self):
        return self.get_title()

    def get_excel_name(self):
        return self.excel_name or self.get_title()

    def get_excel_method(self):
        return self.excel_method

    def get(self, *args, **kwargs):
        if self.get_excel_method().lower() == 'get' and \
                any([excel_param in self.request.GET for excel_param in self.excel_params]):
            return self.get_excel()

        return super().get(*args, **kwargs)

    def post(self, *args, **kwargs):
        if self.get_excel_method().lower() == 'post' and \
                any([excel_param in self.request.POST for excel_param in self.excel_params]):
            return self.get_excel()

        return super().post(*args, **kwargs)

    def get_context_data(self, **kwargs):
        if self.get_workbook_maker():
            kwargs['add_excel'] = True

        return super().get_context_data(**kwargs)
