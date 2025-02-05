from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView




class AccountView(LoginRequiredMixin, TemplateView):
    template_name = 'account/index.html'

