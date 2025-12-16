from rest_framework import permissions
from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from django.contrib.auth.models import AbstractUser
from django.db.models import Q, QuerySet

from users.models import PUBLIC_GROUP_NAME
from addcorpus.models import Corpus


def corpus_name_from_request(request: Request):
    '''
    Extract the corpus name from a request
    '''
    # corpus name can be in kwargs, query params or data json...
    kwargs = request.parser_context['kwargs']
    query_params = request.query_params
    data_json = request.data
    # ... stored as 'corpus' or 'corpus_name'
    possible_corpus_specifications = (
        data.get('corpus', None) or data.get('corpus_name', None)
        for data in [kwargs, query_params, data_json]
    )
    # take the first value that is not None
    corpus = next(
        (corpus_name for corpus_name in possible_corpus_specifications if corpus_name),
        None
    )
    return corpus


def searchable_condition(user: AbstractUser) -> Q:
    '''
    Condition to determine whether a corpus is searchable for a user.

    Always requires that the corpus is active. In addition, users must have access to the
    corpus:
    - Anonymous users can search public corpora
    - Superusers can search anything
    - Normal users can search public corpora or get access through a group. Users can also
        search any active corpora that they can edit.
    '''
    is_active = Q(active=True)
    is_public = Q(groups__name=PUBLIC_GROUP_NAME)
    in_group = Q(groups__in=user.groups.all())

    is_editable = editable_condition(user)

    if user.is_anonymous:
        return is_active & is_public
    elif user.is_superuser:
        return is_active
    else:
        return is_active & (is_public | in_group | is_editable)


def searchable_corpora(user: AbstractUser) -> QuerySet[Corpus]:
    return Corpus.objects.filter(searchable_condition(user)).distinct()


def can_search(user: AbstractUser, corpus: Corpus) -> bool:
    return searchable_corpora(user).contains(corpus)


def can_edit_corpora(user: AbstractUser) -> bool:
    '''
    Whether the user has permission to edit corpora in general.
    '''
    if user.is_anonymous:
        return False
    else:
        return user.is_superuser or user.profile.can_edit_corpora


def editable_condition(user: AbstractUser) -> Q:
    '''
    Condition to determine whether a user is allowed to edit a corpus.

    If the user is not allowed to edit corpora at all, this will return an empty set.
    Otherwise, the user must own the corpus, and the corpus must not have Python
    definition.
    '''
    if not can_edit_corpora(user):
        return Q(pk__in=[]) # match nothing
    else:
        return Q(owner=user, has_python_definition=False)


def editable_corpora(user: AbstractUser) -> QuerySet[Corpus]:
    return Corpus.objects.filter(editable_condition(user))


def can_edit(user: AbstractUser, corpus: Corpus) -> bool:
    return editable_corpora(user).contains(corpus)


class CanSearchCorpus(permissions.BasePermission):
    message = 'You do not have permission to access this corpus'

    def has_permission(self, request, view):
        user = request.user
        corpus_name = corpus_name_from_request(request)

        # check if the corpus exists
        try:
            corpus = Corpus.objects.get(name=corpus_name)
        except:
            raise NotFound('Corpus does not exist')

        # check if the user has access
        return can_search(user, corpus)


class CanEditCorpus(permissions.BasePermission):
    '''
    The user is permitted to use the corpus definition API.

    This requires that the user can edit corpora in general. In addition, permission for
    an object requires that the user owns the corpus.

    For object permissions: the view may handle an object related to a corpus rather than
    the corpus object itself. Therefore, it must implement a method `corpus_from_object`,
    which fetches the corpus related to the requested object.
    '''

    message = 'You do not have permission to edit this corpus'

    def has_permission(self, request: Request, view) -> bool:
        return can_edit_corpora(request.user)

    def has_object_permission(self, request: Request, view, obj) -> bool:
        user = request.user
        corpus = view.corpus_from_object(obj)
        return can_edit(user, corpus)


class CanEditOrSearchCorpus(permissions.BasePermission):
    '''
    Either the user is permitted to edit the corpus, or it is a read-only request
    and the user is allowed to search the corpus.

    Typically used for corpus metadata that can be edited but is also accessible when
    searching. Note that if the user has editing permission, the corpus is not required
    to be active (i.e. it is not guaranteed to be complete).

    Like `CanEditCorpus`, this requires the view to implement corpus_from_object to check
    object permissions.
    '''

    message = 'You do not have access to this corpus'

    def has_permission(self, request: Request, view) -> bool:
        return self._is_safe_method(request) or can_edit_corpora(request.user)

    def has_object_permission(self, request: Request, view, obj) -> bool:
        user = request.user
        corpus = view.corpus_from_object(obj)

        if self._is_safe_method(request):
            return can_search(user, corpus) or can_edit(user, corpus)

        return can_edit(user, corpus)

    def _is_safe_method(self, request: Request):
        return request.method in permissions.SAFE_METHODS
