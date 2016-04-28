##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2016 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.shortcuts import render, get_object_or_404,redirect
from django.contrib.auth.decorators import login_required
from pprint import pprint
from base import models as mdl
from dissertation.models.proposition_dissertation import PropositionDissertation
from dissertation.models.adviser import Adviser
from dissertation.forms import PropositionDissertationForm

@login_required
def proposition_dissertations(request):
    proposition_dissertations = PropositionDissertation.objects.all()
    return render(request, 'proposition_dissertations_list.html', {'proposition_dissertations': proposition_dissertations})

@login_required
def proposition_dissertation_detail(request, pk):
    proposition_dissertation = get_object_or_404(PropositionDissertation, pk=pk)
    person = mdl.person.find_by_user(request.user)
    adviser = Adviser.find_by_person(person)
    return render(request, 'proposition_dissertation_detail.html', {'proposition_dissertation': proposition_dissertation, 'adviser': adviser})

@login_required
def proposition_dissertation_edit(request, pk):
    proposition_dissertation = get_object_or_404(PropositionDissertation, pk=pk)
    person = mdl.person.find_by_user(request.user)
    adviser = Adviser.find_by_person(person)
    if proposition_dissertation.author==adviser:
        if request.method == "POST":
            form = PropositionDissertationForm(request.POST, instance=proposition_dissertation)
            if form.is_valid():
                proposition_dissertation = form.save(commit=False)
                proposition_dissertation.save()
                return redirect('proposition_dissertation_detail', pk=proposition_dissertation.pk)
        else:
            form = PropositionDissertationForm(instance=proposition_dissertation)
        return render(request, 'proposition_dissertation_edit.html', {'form': form})
    else:
        return render(request, 'proposition_dissertations_list.html', {'proposition_dissertations': proposition_dissertations})

@login_required
def proposition_dissertations_search(request):
    proposition_dissertations = PropositionDissertation.search(title=request.GET['title'])
    return render(request, "proposition_dissertations_list.html", {'proposition_dissertations': proposition_dissertations})

@login_required
def proposition_dissertation_new(request):
    if request.method == "POST":
        form = PropositionDissertationForm(request.POST)
        if form.is_valid():
            form.save()
            proposition_dissertations = PropositionDissertation.objects.all()
            return render(request, 'proposition_dissertations_list.html', {'proposition_dissertations': proposition_dissertations})
    else:
        person = mdl.person.find_by_user(request.user)
        adviser = Adviser.find_by_person(person)
        form = PropositionDissertationForm(initial={'author': adviser})
        form.fields['author'].widget.attrs['disabled'] = True
    return render(request, 'proposition_dissertation_edit.html', {'form': form})

@login_required
def proposition_dissertation_my(request):
    person = mdl.person.find_by_user(request.user)
    adviser = Adviser.find_by_person(person)
    proposition_dissertations = PropositionDissertation.objects.filter(author=adviser)
    return render(request, 'proposition_dissertations_list.html', {'proposition_dissertations': proposition_dissertations})
