from django.shortcuts import reverse
from django.db.models import Q
from django.db.models.functions import Lower

from django.views import generic
from guardian.mixins import LoginRequiredMixin
from guardian.shortcuts import get_objects_for_user

from accounts.forms import UserStudiesForm
from accounts.models import User
from studies.models import Response, Study


class ParticipantListView(LoginRequiredMixin, generic.ListView):
    '''
    ParticipantListView shows a list of participants that have participated in studies
    related to organizations that the current user has permissions to.
    '''
    template_name = 'accounts/participant_list.html'
    queryset = User.objects.exclude(demographics__isnull=True)
    model = User

    def get_queryset(self):
        qs = super(ParticipantListView, self).get_queryset()
        return qs.filter(response__study__organization=self.request.user.organization)


class ParticipantDetailView(LoginRequiredMixin, generic.UpdateView):
    '''
    ParticipantDetailView shows information about a participant that has participated in studies
    related to organizations that the current user has permission to.
    '''
    queryset = User.objects.exclude(demographics__isnull=True).select_related('organization')
    fields = ('is_active', )
    template_name = 'accounts/participant_detail.html'
    model = User

    def get_queryset(self):
        qs = super(ParticipantDetailView, self).get_queryset()
        return qs.filter(response__study__organization=self.request.user.organization)

    def get_success_url(self):
        return reverse('exp:participant-detail', kwargs={'pk': self.object.id})


class ResponseListView(LoginRequiredMixin, generic.ListView):
    '''
    Displays a list of responses for studies that the current user can view.
    '''
    template_name = 'accounts/response_list.html'

    def get_queryset(self):
        studies = get_objects_for_user(self.request.user, 'studies.can_view')
        return Response.objects.filter(study__in=studies).order_by('study__name')


class ResponseDetailView(LoginRequiredMixin, generic.DetailView):
    '''
    Displays a response.
    '''
    template_name = 'accounts/response_detail.html'

    def get_queryset(self):
        studies = get_objects_for_user(self.request.user, 'studies.can_view')
        return Response.objects.filter(study__in=studies).order_by('study__name')


class ResearcherListView(LoginRequiredMixin, generic.ListView):
    '''
    Displays a list of researchers in the same organization as the current user.
    '''
    template_name = 'accounts/researcher_list.html'
    queryset = User.objects.filter(demographics__isnull=True)
    model = User

    def get_queryset(self):
        qs = super(ResearcherListView, self).get_queryset()
        # TODO this should probably use permissions eventually, just to be safe
        queryset = qs.filter(organization=self.request.user.organization)
        match = self.request.GET.get('match')
        if match:
            queryset = queryset.filter(Q(family_name__icontains=match) | Q(given_name__icontains=match)| Q(middle_name__icontains=match))
        sort = self.request.GET.get('sort')
        if sort:
            if 'family_name' in sort:
                queryset = queryset.order_by(Lower('family_name').asc()) if '-' in sort else queryset.order_by(Lower('family_name').desc())
        return queryset

    def post(self, request, *args, **kwargs):
        retval = super(ResearcherListView, self).get(request, *args, **kwargs)
        if 'delete' in self.request.POST:
            User.objects.get(pk=self.request.POST['delete']).delete()
        return retval

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['match'] = self.request.GET.get('match') or ''
        context['sort'] = self.request.GET.get('sort') or ''
        return context


class ResearcherDetailView(LoginRequiredMixin, generic.UpdateView):
    '''
    ResearcherDetailView shows information about a researcher and allows enabling or disabling
    a user.
    '''
    queryset = User.objects.filter(demographics__isnull=True)
    fields = ('is_active', )
    template_name = 'accounts/researcher_detail.html'
    model = User

    def get_success_url(self):
        return reverse('exp:researcher-detail', kwargs={'pk': self.object.id})

    def post(self, request, *args, **kwargs):
        retval = super(ResearcherDetailView, self).post(request, *args, **kwargs)
        if 'enable' in self.request.POST:
            self.object.is_active = True
        elif 'disable' in self.request.POST:
            self.object.is_active = False

        if self.request.POST.get('name') == 'given_name':
            self.object.given_name = self.request.POST['value']
        if self.request.POST.get('name') == 'middle_name':
            self.object.middle_name = self.request.POST['value']
        if self.request.POST.get('name') == 'family_name':
            self.object.family_name = self.request.POST['value']
        self.object.save()
        return retval


class AssignResearcherStudies(LoginRequiredMixin, generic.UpdateView):
    '''
    AssignUserStudies lists studies available and let's someone assign permissions
    to users.
    '''
    template_name = 'accounts/assign_studies_form.html'
    queryset = User.objects.filter(demographics__isnull=True)
    form_class = UserStudiesForm

    def get_success_url(self):
        return reverse('exp:researcher-list')

    def get_initial(self):
        permissions = ['studies.can_view', 'studies.can_edit']
        initial = super(AssignResearcherStudies, self).get_initial()
        initial['studies'] = get_objects_for_user(self.object, permissions)
        return initial

    def get_context_data(self, **kwargs):
        context = super(AssignResearcherStudies, self).get_context_data(**kwargs)
        # only show studies in their organization
        context['studies'] = Study.objects.filter(organization=context['user'].organization)
        return context


class ResearcherCreateView(LoginRequiredMixin, generic.CreateView):
    '''
    UserCreateView creates a user. It forces is_active to True; is_superuser
    and is_staff to False; and sets a random 12 char password.

    TODO Eventually this should email the user at their username/email once they
    are saved.
    TODO It should set an unusable password, send them an email to a url with that password
    in it as a token, let them set their own password after clicking the link. It should
    definitely check to make sure it's an unusable password before it allows the reset.
    '''
    model = User
    template_name = 'accounts/researcher_form.html'
    fields = (
        'username',
        'given_name',
        'middle_name',
        'family_name',
        'is_active',
        'is_staff',
        'is_superuser',
        'password'
    )

    def post(self, request, *args, **kwargs):
        # TODO put this on the view so that we can send the user an email once their user is saved
        # TODO alternatively send the password in a post_save signal under certain conditions
        self.user_password = User.objects.make_random_password(length=12)
        form = self.get_form()
        query_dict = form.data.copy()
        # implicitly add them to their creator's organization
        query_dict.update(is_active=True, is_superuser=False, is_staff=False, password=self.user_password)
        form.data = query_dict
        if form.is_valid():
            form.instance.organization = self.request.user.organization
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse('exp:researcher-detail', kwargs={'pk': self.object.id})
        # return reverse('exp:assign-studies', kwargs={'pk': self.object.id})
