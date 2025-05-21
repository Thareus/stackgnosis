import json
import logging
import re
from urllib.parse import urlencode, urlparse, parse_qs
from django.conf import settings
from django.conf.global_settings import MEDIA_URL
from django.contrib.auth.mixins import AccessMixin, LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import QuerySet
from django.db.models.deletion import ProtectedError, RestrictedError
from django.forms.models import model_to_dict
from django.http import QueryDict, JsonResponse, Http404
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, DetailView, ListView
from django.views.generic.edit import FormView, ModelFormMixin
from rest_framework import status
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_200_OK
from rest_framework.views import APIView

from backend.base_forms import CSVUploadForm, ImageUploadForm

###
logger = logging.getLogger('django')
###

class BaseView(LoginRequiredMixin, TemplateView):
    """
    Extends the template view with some useful context and methods
    that might be fundamentally useful for other views
    """
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Include some navigation information
        context.update({
            "site_name": "Stackgnosis",
            "url_name": re.sub(" ", "_", self.request.resolver_match.url_name),
            "path": self.request.path,
            "back": self.request.META.get('HTTP_REFERER', None),
            "view_name": self.request.resolver_match.view_name,
        })
        return context

    def get_querydict_from_request_method(self):
        return getattr(self.request, self.request.method).copy()

    def get_querydict(self):
        """
        Finds and returns the querydict as a normal dictionary.
        The querydict may exist several places. They are ordered below in order of which takes precedence.
        """
        if hasattr(self, 'querydict'):
            return self.querydict
        if 'querydict' in self.request.session:
            # print("FROM REQUEST SESSION") # This leads to issues when trying to load more objects from the dashboard.
            url_querydict = self.request.session.pop('querydict', {})
            querydict = parse_qs(url_querydict)
        elif hasattr(self.request, self.request.method) and bool(len(getattr(self.request, self.request.method))): #
            # print("FROM REQUEST METHOD")
            querydict = self.get_querydict_from_request_method()
        elif self.kwargs:
            # print("FROM KWARGS")
            querydict = self.kwargs
        elif hasattr(self.request, "data"):
            # print("FROM DATA")
            if isinstance(self.request.data, str):
                querydict = json.loads(self.request.data)
            else:
                querydict = {key: value for key, value in self.request.data.items()}
        else:
            querydict = {}
        # Assign as attribute
        self.querydict = querydict
        logger.info(f"QUERYDICT: {self.querydict}")
        return self.querydict

    def get_http_referer_querydict(self, request):
        referer = request.headers.get('Referer', "")
        # Split query from url
        referer_url_query = parse_qs(urlparse(referer).query)
        self.querydict = {}
        for key, value in referer_url_query.copy().items():
            if len(value) == 1:
                self.querydict[key] = value[0]
            elif len(value) > 1:
                self.querydict[key] = value
            else:
                raise ValueError(f"Length of value for {key} is {len(value)}: {value}")
        return self.querydict

    def collapse_querydict_values(self, querydict):
        """
        For a given querydict, which will have all its values stored as
        lists, this function will return a querydict with all the
        singular or empty values "unlisted"
        """
        collapsed_querydict = {}
        for key in querydict.keys():
            try:
                value = querydict.getlist(key)
            except AttributeError:
                value = querydict.get(key)
            if len(value) == 0:
                continue
            if len(value) <= 1:
                collapsed_querydict[key] = value[0]
            elif len(value) > 1:
                collapsed_querydict[key] = value
            else:
                raise ValueError(f"Length of value for {key} is {len(value)}: {value}")
        return collapsed_querydict

    def clean_querydict(self, querydict):
        """
        Returns a new querydict with empty keys removed.
        :param querydict:
        """
        querydict = {key: value for key, value in querydict.items() if value[0] != ''}
        clean_querydict = QueryDict('', mutable=True)
        clean_querydict.update(querydict)
        return clean_querydict


class BaseModelView(BaseView):
    """
    Provides a unified interface for working with Models and Nodes,
    where the adaptation could not be built into the BaseNodeModel class
    """
    model = None
    context_object_name = None
    related_fields = None

    def get_order_by(self):
        """
        Looks for the queryset ordering field within the querydict,
        then in the model's default ordering field, but where there
        is not a model provided, it will return none.
        """
        
        if 'order_by' in self.querydict:
            try:
                return [self.querydict.pop('order_by')]
            except AttributeError:
                return self.model._meta.ordering
        else:
            return self.model._meta.ordering
            

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Adds some information related to the model
        context.update({
            'model_name': self.model.__name__,
            'model_name_verbose': self.model._meta.verbose_name.lower(),
            'model_name_plural': self.model._meta.verbose_name_plural.lower(),
            'default_related_name': self.model._meta.default_related_name.lower(),
            'app_label': self.model._meta.app_label.lower(),
        })
        return context


class BaseModelAPI(APIView, BaseModelView):
    """
    Methods 	Urls 	                            Action
    GET 	    api/{app}/{model}/ 	                get all {model}
    GET 	    api/{app}/{model}/{identifier} 	    get {instance} by identifier
    GET 	    api/{app}/{model}?**{key}=[value] 	find all {model} for which all {key} = {value}'
    POST 	    api/{app}/{model}/ 	                add new {model}
    PUT 	    api/{app}/{model}/{identifier} 	    update {instance} by identifier
    PATCH 	    api/{app}/{model}/{identifier} 	    partial update {instance} by identifier
    DELETE 	    api/{app}/{model}/{identifier} 	    remove {instance} by identifier
    """
    model = None
    serializer_class = None
    lookup_field = 'slug' # Default
    lookup_url_kwarg = 'slug' # Default
    queryset = None
    per_page = 50  # Allows to be overwritten for objects with thin querysets.

    def get_serializer_class(self):
        if self.serializer_class is None:
            raise NotImplementedError("serializer_class not set")
        return self.serializer_class

    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        serializer_class = self.get_serializer_class()
        return serializer_class(*args, **kwargs)

    def get_querydict(self):
        super().get_querydict()
        # Order
        self.order_by = self.get_order_by()
        # Page
        self.page = int(self.querydict.pop('page', 1))
        return self.querydict

    def get_queryset(self):
        if not hasattr(self, 'querydict'):
            self.get_querydict()
        if self.querydict:
            return self.model.objects.filter(**self.querydict)
        else:
            return self.model.objects.all()

    def paginate_objects(self, objects, page):
        # Pagination
        paginator = Paginator(objects,
                              self.per_page)  # If per_page attribute is updated remember to update the Select2 configuration in the script.js file to match.
        page_obj = None
        if page > paginator.num_pages:
            pass
        else:
            try:
                page_obj = paginator.get_page(page)
            except (EmptyPage, PageNotAnInteger):
                page_obj = paginator.page(1)
            except KeyError:
                pass
            return page_obj

    def get(self, request, *args, **kwargs):
        """
        GET     list        api/{app}/{model}/                get all of {model}
        GET     instance    api/{app}/{model}/{identifier}    get instance by {identifier}
        GET     query       api/{app}/{model}/?**{query}       get subset by query
        """
        self.get_querydict()
        objects = self.get_queryset()
        count = objects.count()
        # Nature of Response is determined by count of objects
        if count > settings.MAX_QUERYSET_SIZE:
            logger.warning("Too many objects found")
            return Response({"message": 'Too many objects found, please submit a more specific query', 'results': [], 'count': 0}, status=status.HTTP_204_NO_CONTENT)
        elif count > 1:
            objects = objects.order_by(*self.order_by)
            page = self.paginate_objects(objects, self.page)
            if page:
                objects = self.serializer_class(page.object_list, many=True).data
                return Response({"message": 'Success', 'results': objects, 'count': count}, status=status.HTTP_200_OK)
            else: # Requested page may be out of range.
                return Response({"message": 'No results', 'results': [], 'count': 0}, status=status.HTTP_404_NOT_FOUND)
        elif count == 1:
            object = self.serializer_class(objects, many=True).data
            return Response({"message": 'Success', 'results': object, 'count': count}, status=status.HTTP_200_OK)
        elif count == 0:
            return Response({"message": 'No results', 'results': [], 'count': count}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, *args, **kwargs):
        """
        POST    instance    api/{app}/{model}/    add new {model} instance
        """
        self.get_querydict()
        serializer = self.get_serializer(data=self.querydict)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(data=serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                message = str(e)
                logger.error(f"Exception on save: {message}")
                return Response({"message": message}, status=status.HTTP_400_BAD_REQUEST)
        else:
            logger.error(f"{serializer.__class__.__name__} ERRORS: {serializer.errors}")
            return Response(data={"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self):
        if hasattr(self, 'object'):
            return self.object
        queryset = self.get_queryset()
        get_kwargs = {self.lookup_field: self.kwargs[self.lookup_url_kwarg]}
        try:
            self.object = queryset.get(**get_kwargs)
        except queryset.model.DoesNotExist:
            error_message = f"Could not find {self.model.__name__} with {get_kwargs}"
            logger.error(error_message)
            return Response(data={"message":error_message}, status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(self.request, self.object) # May raise a permission denied
        return self.object

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance=instance, data=self.querydict, partial=partial)
        if serializer.is_valid():
            try:
                serializer.save()
            except Exception as e:
                message = str(e)
                logger.error(f"Exception on save: {message}")
                return Response({"message": message}, status=status.HTTP_400_BAD_REQUEST)
        else:
            logger.error(f"{serializer.__class__.__name__} ERRORS: {serializer.errors}")
            return Response(data={"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        """
        PUT     instance    api/{app}/{model}/{identifier}     update identified {instance}
        """
        # Add missing fields
        for field in self.model._meta.fields:
            if field.name not in self.querydict.keys():
                self.querydict[field.name] = ""
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        """
        PATCH     instance    api/{app}/{model}/{identifier}       partially update identified {instance}
        PATCH     list        api/{app}/{model}/{condition}       partial update subset by shortcut {condition}
        """
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """
        DELETE     instance    api/{app}/{model}/{identifier}     delete {instance}
        """
        try:
            self.object = self.get_object()
            self.object.delete()
        except ProtectedError as e:
            logger.error(e)
            return JsonResponse(data={"message":f"This object is protected. It may have dependent related objects: {e.protected_objects}"}, status=status.HTTP_400_BAD_REQUEST)
        except Http404 as e:
            return Response(
                data={"message": f"Could not find object; identifier is {self.lookup_field}"},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(status=status.HTTP_200_OK)


class BaseFormView(BaseView, FormView):
    template_name = None
    form_class = None
    success_url = None

    def form_valid(self, form):
        """If the form is valid, redirect to the supplied URL."""
        return JsonResponse(self.get_success_url())

    def form_invalid(self, form):
        """If the form is invalid, return an error message and the errors."""
        return JsonResponse(
            data={"message": f"Please correct the errors on the form", "errors": str(form.errors)},
            status=status.HTTP_400_BAD_REQUEST
        )

    def get_next_url(self):
        """
        The form may supply its own redirect information based on the context where it was accessed,
        or will simply go back to the previous page as a fallback.
        """
        if not hasattr(self, 'next'):
            self.next = self.querydict.pop('next', self.request.META.get('HTTP_REFERER'))
        return self.next

    def get_success_url(self):
        if self.success_url:
            return self.success_url

        if hasattr(self, 'object') and hasattr(self.object, 'get_absolute_url'):
            return self.object.get_absolute_url()

        return self.get_next_url()

class BaseModelFormView(BaseModelAPI, ModelFormMixin, AccessMixin):
    form_class = None
    lookup_url_kwarg = None
    renderer_classes = [TemplateHTMLRenderer]
    model = None

    def get_initial_form_data(self):
        """
        For any given initial object, prefill the form with data including the foreign keys of the object.
        """
        if hasattr(self, 'initial_form_data'):
            return self.initial_form_data
        elif hasattr(self, 'object') and self.object:
            # When editing an object, the object's data is supplied to the form.
            self.initial_form_data = model_to_dict(self.object)
        else:
            # Data may be pre-supplied as parameters.
            self.initial_form_data = self.querydict

        # # Get values for ModelChoiceFields (ForeignKeys)
        # form_fields = self.form_class.base_fields
        # model_choice_fields = [x for x in form_fields if 'ModelChoiceField' in str(type(form_fields[x]))]
        # # Get models of these fields
        # model_choice_models = [model for model in self.model_dict if model.lower() in model_choice_fields]
        # for model in model_choice_models:
        #     # Attempt to get model choice field instance
        #     if model in self.initial_form_data:
        #         try:
        #             model_lookup = {self.model_dict[model]._meta.pk.name: self.initial_form_data[model]}
        #             self.initial_form_data[model] = self.model_dict[model].objects.get(**model_lookup)
        #         except (TypeError, self.model_dict[model].DoesNotExist):
        #             continue
        #     else:
        #         # It would be useful to preload model_choice_field queryset objects as choices but
        #         # for most models the number of objects is prohibitive and
        #         # so select2 ajax requests are used in a custom Select2 widget
        #         continue
        return self.initial_form_data

    def get_form_kwargs(self):
        """
        Return the keyword arguments for instantiating the form.
        Overrides the default method to improve getting initial form data.
        """
        kwargs = {
            # 'initial': self.initial(), # Overridden with get_initial_form_data (below)
            'initial': self.get_initial_form_data(),
            'prefix': self.get_prefix(),
        }
        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        if hasattr(self, 'object'):
            kwargs['instance'] = self.object
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        context['allow_delete'] = getattr(self, 'allow_delete', True)
        if hasattr(self, 'object'): # Originally if self.object leading to AttributeError.
            context['object'] = self.object
            context_object_name = self.get_context_object_name(self.object)
            if context_object_name:
                context[context_object_name] = self.object
        return context

    def get(self, request, *args, **kwargs):
        self.get_querydict()
        self.object = self.get_object()
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context=context)

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        self.object = form.save()
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        """
        Because forms may only be submitted through POST, this function redirects to the appropriate API endpoint.
        When forms are submitted, they arrive as a dictionary of string values.
        Form.is_valid() calls clean() on each field, which transforms values for ForeignKeys into their related objects.
        Form data is then intended to be sent to the API where it is ingested by the serializer, but this expects plain text values.
        However, not cleaning the forms means that some crucial cleaning methods are skipped.
        """
        self.get_querydict()
        method = self.querydict.get('_method', 'post')
        # Cleaning form-submitted data
        if method in ['post', 'put', 'patch']:
            form = self.form_class(self.querydict)
            if form.is_valid():
                pass
            else:
                return self.form_invalid(form)

        # Method Rerouting to API
        if method == 'post':
            return super().post(request, *args, **kwargs)
        elif method == 'put':
            return self.put(request, *args, **kwargs)
        elif method == 'patch':
            return self.patch(request, *args, **kwargs)
        elif method == 'delete':
            return self.delete(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        try:
            return super().delete(request, *args, **kwargs)
        except (ProtectedError, RestrictedError) as e:
            self.template_name = 'elements/protected_errorlist.html'
            if e.__class__.__name__ == 'ProtectedError':
                protected_objects = list(e.__dict__['protected_objects'])[:5]
            elif e.__class__.__name__ == 'RestrictedError':
                protected_objects = list(e.__dict__['restricted_objects'])[:5]
            else:
                protected_objects = "None Found"
            context = {
                'model': self.model,
                'protected_objects': protected_objects,
                'message': "Bad Request"
            }
            return self.render_to_response(
                context=context,
                status=status.HTTP_400_BAD_REQUEST,
            )


class BaseModelDetailView(
    BaseModelView,
    DetailView,
    AccessMixin
):
    model = None
    context_object_name = None
    template_name = None
    serializer_class = None
    lookup_field = None
    lookup_url_kwarg = None
    related_fields = None


class BaseModelListView(BaseModelView, ListView):
    template_name = 'base_model_list.html'
    model = None
    model_type = None
    filterset_class = None
    per_page = 50 # Allows to be overwritten for objects with thin querysets.
    page = None
    order_by = None
    ordering = None

    def get_order_by(self):
        try:
            return self.querydict['order_by']
        except KeyError:
            return self.model._meta.ordering

    def get_ordering(self):
        """Return the field or fields to use for ordering the queryset."""
        return self.order_by

    def get_querydict(self):
        super().get_querydict()
        # Order
        self.order_by = self.get_order_by()
        # Page
        self.page = int(self.querydict.pop('page', 1))
        return self.querydict

    def get_queryset(self):
        """
        Return the list of items for this view.

        The return value must be an iterable and may be an instance of
        `QuerySet` in which case `QuerySet` specific behavior will be enabled.
        """
        self.model_type = self.model_type
        if self.queryset is not None:
            queryset = self.queryset
            if isinstance(queryset, QuerySet):
                queryset = queryset.all()
        elif self.model is not None:
            queryset = self.model._default_manager.all()
        else:
            raise ImproperlyConfigured(
                "%(cls)s is missing a QuerySet. Define "
                "%(cls)s.model, %(cls)s.queryset, or override "
                "%(cls)s.get_queryset()." % {"cls": self.__class__.__name__}
            )
        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)
        return queryset

    def get_context_data(self, **kwargs):
        # Data
        self.object_list = self.get_queryset()
        context = super().get_context_data(**kwargs)
        if any(list(self.querydict.values())):
            context['querydict'] = self.querydict
            self.object_list = self.get_queryset()
            if self.object_list.count() > settings.MAX_QUERYSET_SIZE:
                context['readable_query'] = {self.model.__name__:{"Too many objects found":"Please submit a more specific query."}}
                self.object_list = self.model.objects.none()
            else:
                # Querydict translations
                context['url_querydict'] = urlencode(self.querydict) # used in Pagination
        else:
            self.object_list = self.model.objects.all()
        # Page
        context['page'] = self.page
        count = len(self.object_list) # TODO Change to table_count
        if count:
            # Object List
            self.object_list = self.object_list[:settings.MAX_QUERYSET_SIZE]
            context['queryset_length'] = f"{len(self.object_list)} of {count}"
            context['page_obj'] = self.paginate_objects(self.object_list, self.page)
        else:
            context['queryset_length'] = 0
        context['table_path'] = getattr(
            self, 'table_path', f"{self.model._meta.app_label}/{self.model._meta.default_related_name}/table.html"
        )
        return context

    def paginate_objects(self, objects, page):
        # Pagination
        paginator = Paginator(objects, self.per_page) # If per_page attribute is updated, remember to update the Select2 configuration in the script.js file to match.
        if page > paginator.num_pages:
            return None
        else:
            try:
                page_obj = paginator.get_page(page)
                return page_obj
            except (EmptyPage, PageNotAnInteger):
                page_obj = paginator.page(1)
                return page_obj
            except KeyError:
                pass

    def load_more_objects(self, **kwargs):
        context = {}
        context = self.get_queryset_context(context)
        if context['page_obj']:
            # Model Table
            table_body = f"{self.model._meta.app_label}/{self.model._meta.default_related_name}/table_body.html"
            table_body = render_to_string(table_body, context)
            return JsonResponse(data={"message":"Success", "table_body": table_body}, status=status.HTTP_200_OK)
        else:
            return JsonResponse(data={"message": "No more results"}, status=status.HTTP_200_OK)

    @method_decorator(csrf_exempt)
    def get(self, request, *args, **kwargs):
        """
        Overrides to intercept ajax requests which will be made for loading more data in the table.
        """
        # if self.request_is_ajax():
        #     if hasattr(self, 'load_more'):
        #         return self.load_more_objects()
        self.querydict = self.get_querydict()
        return super().get(request,*args, **kwargs)

class ModelDashboard(BaseModelListView):
    """
    Adds information for constructing a dashboard around the model list.
    """
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quick_filters_path = f"{self.model._meta.app_label.lower()}/{self.model._meta.default_related_name}/quick_filters.html"
        context['filter_path'] = quick_filters_path
        return context

class BaseModelCSVUploadView(BaseModelFormView):
    template_name = 'upload_csv.html'
    form_class = CSVUploadForm
    required_fields = None

    def get_form_kwargs(self):
        return {}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.required_fields:
            raise AttributeError('required_fields cannot be None')
        else:
            context['required_fields'] = self.required_fields
        return context

    def process_csv(self):
        raise NotImplementedError('method \'process_csv\' has no default behavior and must be defined')

    def form_valid(self, form):
        file = form.cleaned_data['file']
        if not file.name.endswith('.csv'):
            return self.form_invalid(form)
        try:
            self.process_csv()
        except Exception as e:
            return self.form_invalid(form)
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)

from django.core.files.storage import default_storage

class ImageUploadView(BaseModelFormView):
    form_class = ImageUploadForm
    template_name = None
    image_field = None
    identifier_field = None

    def get_image_name(self):
        object_identifier = getattr(self.object, self.identifier_field)
        return f"{MEDIA_URL}/{self.model.__name__}/{object_identifier}/{self.image_field}"

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        self.object = self.get_object()
        if form.is_valid():
            uploaded_file = form.cleaned_data['image']
            # Check if file already exists, delete it if so.
            image_name = self.get_image_name()
            if default_storage.exists(image_name):
                default_storage.delete(image_name)
            # Now save the new file under the same name.
            path = default_storage.save(image_name, uploaded_file)
            setattr(self.object, self.image_field, path)
            self.object.save()
            return JsonResponse({"message":"Image Successfully Uploaded"}, status=HTTP_200_OK)
        else:
            return JsonResponse({"message":"Something went wrong"}, status=HTTP_500_INTERNAL_SERVER_ERROR)
        # return render(request, self.template_name, {'form': form})