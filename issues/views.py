from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import redirect, render
from django.views.generic import ListView, DetailView

from .forms import IssueReportForm
from .models import IssueReport


@login_required
def report_issue(request):
    if request.method == 'POST':
        form = IssueReportForm(request.POST, request.FILES)
        if form.is_valid():
            issue = form.save(commit=False)
            issue.user = request.user if request.user.is_authenticated else None
            issue.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'گزارش با موفقیت ثبت شد.'})
            return redirect(request.POST.get('page_url', '/'))
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = IssueReportForm(initial={'page_url': request.META.get('HTTP_REFERER', '')})
    return render(request, 'issues/report_form.html', {'form': form})


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return HttpResponseForbidden('دسترسی ندارید')
        return redirect('adv:login')


class IssueListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = IssueReport
    template_name = 'issues/issue_list.html'
    context_object_name = 'issues'
    paginate_by = 20


class IssueDetailView(LoginRequiredMixin, StaffRequiredMixin, DetailView):
    model = IssueReport
    template_name = 'issues/issue_detail.html'
    context_object_name = 'issue'
