##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
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

from base.tests.factories.academic_year import AcademicYearFactory
from dissertation.models import adviser
from dissertation.models.dissertation_role import count_by_dissertation, search_by_dissertation_and_role
from dissertation.tests.models.test_faculty_adviser import create_faculty_adviser
from dissertation.views.dissertation import adviser_can_manage
from django.test import TestCase
from django.core.urlresolvers import reverse
from base.tests.factories.offer_year import OfferYearFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.offer import OfferFactory
from base.tests.factories.student import StudentFactory
from dissertation.tests.factories.adviser import AdviserManagerFactory, AdviserTeacherFactory
from dissertation.tests.factories.dissertation import DissertationFactory
from dissertation.tests.factories.faculty_adviser import FacultyAdviserFactory
from dissertation.tests.factories.offer_proposition import OfferPropositionFactory
from dissertation.tests.factories.proposition_dissertation import PropositionDissertationFactory
from dissertation.tests.factories.proposition_offer import PropositionOfferFactory


class DissertationViewTestCase(TestCase):

    def setUp(self):
        self.manager = AdviserManagerFactory()
        a_person_teacher = PersonFactory.create(first_name='Pierre', last_name='Dupont')
        self.teacher = AdviserTeacherFactory(person=a_person_teacher)
        a_person_teacher2 = PersonFactory.create(first_name='Marco', last_name='Millet')
        self.teacher2 = AdviserTeacherFactory(person=a_person_teacher2)
        a_person_student = PersonFactory.create(last_name="Durant", user=None)
        student = StudentFactory.create(person=a_person_student)
        self.offer1 = OfferFactory(title="test_offer1")
        self.offer2 = OfferFactory(title="test_offer2")
        self.academic_year1 = AcademicYearFactory()
        self.academic_year2 = AcademicYearFactory(year=self.academic_year1.year-1)
        self.offer_year_start1 = OfferYearFactory(acronym="test_offer1", offer=self.offer1,
                                             academic_year=self.academic_year1)
        offer_year_start2 = OfferYearFactory(academic_year=self.academic_year2, acronym="test_offer2", offer=self.offer1)
        self.offer_proposition1 = OfferPropositionFactory(offer=self.offer1)
        self.offer_proposition2 = OfferPropositionFactory(offer=self.offer2)
        FacultyAdviserFactory(adviser=self.manager, offer=self.offer1)


        roles = ['PROMOTEUR', 'CO_PROMOTEUR', 'READER', 'PROMOTEUR', 'ACCOMPANIST', 'PRESIDENT']
        status = ['DRAFT', 'COM_SUBMIT', 'EVA_SUBMIT', 'TO_RECEIVE', 'DIR_SUBMIT', 'DIR_SUBMIT']

        for x in range(0, 6):
            proposition_dissertation = PropositionDissertationFactory(author=self.teacher,
                                                                      creator=a_person_teacher,
                                                                      title='Proposition {}'.format(x)
                                                                      )
            PropositionOfferFactory(proposition_dissertation=proposition_dissertation,
                                    offer_proposition=self.offer_proposition1)

            DissertationFactory(author=student,
                                title='Dissertation {}'.format(x),
                                offer_year_start=self.offer_year_start1,
                                proposition_dissertation=proposition_dissertation,
                                status=status[x],
                                active=True,
                                dissertation_role__adviser=self.teacher,
                                dissertation_role__status=roles[x]
                                )
        self.dissertation_1 = DissertationFactory(author=student,
                                           title='Dissertation 2017',
                                           offer_year_start=self.offer_year_start1,
                                           proposition_dissertation=proposition_dissertation,
                                           status='DIR_SUBMIT',
                                           active=True,
                                           dissertation_role__adviser=self.teacher2,
                                           dissertation_role__status='PROMOTEUR')


    def test_get_dissertations_list_for_teacher(self):
        self.client.force_login(self.teacher.person.user)
        url = reverse('dissertations_list')
        response = self.client.get(url)
        self.assertEqual(response.context[-1]['adviser_list_dissertations'].count(), 1)  # only 1 because 1st is DRAFT
        self.assertEqual(response.context[-1]['adviser_list_dissertations_copro'].count(), 1)
        self.assertEqual(response.context[-1]['adviser_list_dissertations_reader'].count(), 1)
        self.assertEqual(response.context[-1]['adviser_list_dissertations_accompanist'].count(), 1)
        self.assertEqual(response.context[-1]['adviser_list_dissertations_president'].count(), 1)

    def test_get_dissertations_list_for_manager(self):
        self.client.force_login(self.manager.person.user)
        url = reverse('manager_dissertations_list')
        response = self.client.get(url)
        self.assertEqual(response.context[-1]['dissertations'].count(), 7)

    def test_search_dissertations_for_manager(self):
        self.client.force_login(self.manager.person.user)
        url = reverse('manager_dissertations_search')

        response = self.client.get(url, data={"search": "no result search"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context[-1]['dissertations'].count(), 0)

        response = self.client.get(url, data={"search": "Dissertation 2"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context[-1]['dissertations'].count(), 2)

        response = self.client.get(url, data={"search": "Proposition 3"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context[-1]['dissertations'].count(), 1)

        response = self.client.get(url, data={"search": "Dissertation"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context[-1]['dissertations'].count(), 7)

        response = self.client.get(url, data={"search": "Dissertation",
                                              "offer_prop_search": self.offer_proposition1.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context[-1]['dissertations'].count(), 7)

        response = self.client.get(url, data={"search": "Dissertation",
                                              "offer_prop_search": self.offer_proposition2.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context[-1]['dissertations'].count(), 0)

        response = self.client.get(url, data={"academic_year": self.academic_year1.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context[-1]['dissertations'].count(), 7)

        response = self.client.get(url, data={"academic_year": self.academic_year2.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context[-1]['dissertations'].count(), 0)

        response = self.client.get(url, data={"status_search": "COM_SUBMIT"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context[-1]['dissertations'].count(), 1)

        response = self.client.get(url, data={"search": "test_offer"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context[-1]['dissertations'].count(), 7)

        response = self.client.get(url, data={"search": "Durant"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context[-1]['dissertations'].count(), 7)

        response = self.client.get(url, data={"search": "Dupont"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context[-1]['dissertations'].count(), 7)

    def test_adviser_can_manage_dissertation(self):
        manager = AdviserManagerFactory()
        manager2 = AdviserManagerFactory()
        a_person_teacher = PersonFactory.create(first_name='Pierre', last_name='Dupont')
        a_person_teacher2 = PersonFactory.create(first_name='Marco', last_name='Millet')
        teacher = AdviserTeacherFactory(person=a_person_teacher)
        teacher2 = AdviserTeacherFactory(person=a_person_teacher2)
        a_person_student = PersonFactory.create(last_name="Durant", user=None)
        student = StudentFactory.create(person=a_person_student)
        offer_year_start = OfferYearFactory(academic_year=self.academic_year1, acronym="test_offer2")
        offer_year_start2 = OfferYearFactory(acronym="test_offer3", academic_year=offer_year_start.academic_year)
        offer = offer_year_start.offer
        offer2 = offer_year_start2.offer
        FacultyAdviserFactory(adviser=manager, offer=offer)
        create_faculty_adviser(manager, offer)
        create_faculty_adviser(manager2, offer2)
        proposition_dissertation = PropositionDissertationFactory(author=teacher,
                                                                  creator=a_person_teacher,
                                                                  title='Proposition1')
        dissertation = DissertationFactory(author=student,
                                           title='Dissertation 2017',
                                           offer_year_start=offer_year_start,
                                           proposition_dissertation=proposition_dissertation,
                                           status='DIR_SUBMIT',
                                           active=True,
                                           dissertation_role__adviser=teacher,
                                           dissertation_role__status='PROMOTEUR')
        self.assertEqual(adviser_can_manage(dissertation, manager), True)
        self.assertEqual(adviser_can_manage(dissertation, manager2), False)
        self.assertEqual(adviser_can_manage(dissertation, teacher), False)


    def test_get_all_advisers(self):
        res = adviser.find_all_advisers()
        self.assertEqual(res.count(),3)

    def test_find_by_last_name_or_email(self):
        res=adviser.find_by_last_name_or_email('Dupont')
        self.assertEqual(res.count(), 1)
        for i in res:
            self.assertEqual(i.person.last_name, 'Dupont')


    def test_get_adviser_list_json(self):
        self.client.force_login(self.manager.person.user)
        response = self.client.get('/dissertation/get_adviser_list/',{'term':'Dupont'})
        self.assertEqual(response.status_code, 200)
        data_json = response.json()
        self.assertEqual(len(data_json), 1)
        for i in data_json:
            self.assertEqual(i['last_name'], 'Dupont')


    def test_manager_dissertations_jury_by_ajax(self):
        self.client.force_login(self.manager.person.user)
        dissert_role_count = count_by_dissertation(self.dissertation_1)
        response = self.client.post('/dissertation/manager_dissertations_jury_new_by_ajax/', {'pk_dissertation': str(self.dissertation_1.id)})
        self.assertEqual(response.status_code, 400)
        response = self.client.post('/dissertation/manager_dissertations_jury_new_by_ajax/',
                                    {'pk_dissertation': str(self.dissertation_1.id), 'status_choice' : 'READER'})
        self.assertEqual(response.status_code, 400)
        response = self.client.post('/dissertation/manager_dissertations_jury_new_by_ajax/',
                                    {'pk_dissertation' : str(self.dissertation_1.id),
                                     'status_choice' : 'READER' ,
                                     'adviser_pk' : str(self.teacher.id)})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(dissert_role_count + 1 , count_by_dissertation(self.dissertation_1))
        response2 = self.client.get('/dissertation/manager_dissertations_role_delete_by_ajax/999999')
        self.assertEqual(response2.status_code, 404)
        liste_dissert_roles=search_by_dissertation_and_role(self.dissertation_1, 'READER')
        for element in liste_dissert_roles:
            dissert_role_count = count_by_dissertation(self.dissertation_1)
            response2 = self.client.get('/dissertation/manager_dissertations_role_delete_by_ajax/'+str(element.id))
            if self.assertEqual(response2.status_code, 200):
                self.assertEqual(count_by_dissertation(self.dissertation_1), dissert_role_count-1)



