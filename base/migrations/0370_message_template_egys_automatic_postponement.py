# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-10-31 13:01
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0369_auto_20181017_1215'),
    ]

    operations = [
        migrations.RunSQL(
            [(
             "INSERT INTO osis_common_messagetemplate (reference, subject, template, format, language) VALUES (%s, %s, %s, %s, %s);",
             ['egy_before_auto_postponement_html',
              'Lancement de la proc\u00e9dure annuelle de copie des organisations de formation',
              '{% autoescape off %}\r\n<p>Bonjour,</p>\r\n<p>Ceci est un message automatique g\u00e9n\u00e9r\u00e9 par le serveur OSIS – Merci de ne pas y r\u00e9pondre.</p>\r\n<p>Lancement de la proc\u00e9dure annuelle de copie des organisations de formation pour l\u0027ann\u00e9e acad\u00e9mique {{ end_academic_year }}.</p>\r\n<p>{{ egys_to_postpone }} UE à copier de {{ academic_year }} en {{ end_academic_year }}.</p>\r\n<p>{{ egys_ending_this_year }} OF avec une fin d\u0027enseignement en {{ academic_year }}.</p>\r\n<p>{{ egys_already_existing }} UE existant pr\u00e9alablement en {{ end_academic_year }}.</p><p>\r\nCordialement,\r\nOsis UCLouvain</p>\r\n{% endautoescape %}',
              'HTML',
              'fr-be'])], elidable=True
        ),
        migrations.RunSQL(
            [(
             "INSERT INTO osis_common_messagetemplate (reference, subject, template, format, language) VALUES (%s, %s, %s, %s, %s);",
             ['egy_before_auto_postponement_txt',
              'Lancement de la proc\u00e9dure annuelle de copie des organisations de formation',
              '<p>Bonjour,</p>\r\n<p>Ceci est un message automatique g\u00e9n\u00e9r\u00e9 par le serveur OSIS – Merci de ne pas y r\u00e9pondre.</p>\r\n<p>Lancement de la proc\u00e9dure annuelle de copie des organisations de formation pour l\u0027ann\u00e9e acad\u00e9mique {{ end_academic_year }}.</p>\r\n<p>{{ egys_to_postpone }} UE à copier de {{ academic_year }} en {{ end_academic_year }}.</p>\r\n<p>{{ egys_ending_this_year }} OF avec une fin d\u0027enseignement en {{ academic_year }}.</p>\r\n<p>{{ egys_already_existing }} UE existant pr\u00e9alablement en {{ end_academic_year }}.</p><p>\r\nCordialement,\r\nOsis UCLouvain</p>\r\n',
              'PLAIN',
              'fr-be'])], elidable=True
        ),
        migrations.RunSQL(
            [(
             "INSERT INTO osis_common_messagetemplate (reference, subject, template, format, language) VALUES (%s, %s, %s, %s, %s);",
             ['egy_before_auto_postponement_html',
              'Initiation of the annual procedure of copy of the education groups',
              '{% autoescape off %}\r\n<p>Hello,</p>\r\n<p>This is an automatic message generated by the OSIS server – Please do not reply to this message.</p>\r\n<p>Initiation of the annual procedure of copy of the learning units for the academic year {{ end_academic_year }}.</p>\r\n<p>{{ egys_to_postpone }} LU to copy from {{ academic_year }} to {{ end_academic_year }}.</p>\r\n<p>{{ egys_ending_this_year }} LU ending in {{ academic_year }}.</p>\r\n<p>{{ egys_already_existing }} LU already existing in {{ end_academic_year }}.</p><p>\r\nRegards,\r\nOsis UCLouvain</p>\r\n{% endautoescape off %}',
              'HTML',
              'en'])], elidable=True
        ),
        migrations.RunSQL(
            [(
             "INSERT INTO osis_common_messagetemplate (reference, subject, template, format, language) VALUES (%s, %s, %s, %s, %s);",
             ['egy_before_auto_postponement_txt',
              'Initiation of the annual procedure of copy of the education groups',
              '<p>Hello,</p>\r\n<p>This is an automatic message generated by the OSIS server – Please do not reply to this message.</p>\r\n<p>Initiation of the annual procedure of copy of the learning units for the academic year {{ end_academic_year }}.</p>\r\n<p>{{ egys_to_postpone }} LU to copy from {{ academic_year }} to {{ end_academic_year }}.</p>\r\n<p>{{ egys_ending_this_year }} LU ending in {{ academic_year }}.</p>\r\n<p>{{ egys_already_existing }} LU already existing in {{ end_academic_year }}.</p><p>\r\nRegards,\r\nOsis UCLouvain</p>\r\n',
              'PLAIN',
              'en'])], elidable=True
        ),
        migrations.RunSQL(
            [(
             "INSERT INTO osis_common_messagetemplate (reference, subject, template, format, language) VALUES (%s, %s, %s, %s, %s);",
             ['egy_after_auto_postponement_html',
              'Rapport d\u0027ex\u00e9cution de la proc\u00e9dure annuelle de copie des organisations de formation',
              '{% autoescape off %}\r\n<p>Bonjour,</p>\r\n<p>Ceci est un message automatique g\u00e9n\u00e9r\u00e9 par le serveur OSIS – Merci de ne pas y r\u00e9pondre.</p>\r\n<p>Lancement de la proc\u00e9dure annuelle de copie des organisations de formation pour l\u0027ann\u00e9e acad\u00e9mique {{ end_academic_year }}.</p>\r\n<p>{{ egys_postponed }} UE copi\u00e9es de {{ academic_year }} en {{ end_academic_year }}.</p>\r\n<p>{{ egys_ending_this_year }} OF avec une fin d\u0027enseignement en {{ academic_year }}.</p>\r\n<p>{{ egys_already_existing }} UE existant pr\u00e9alablement en {{ end_academic_year }}.</p>\r\n{% if egys_with_errors %}<p>Les organisations de formation suivantes n\u0027ont pas \u00e9t\u00e9 recopi\u00e9es :</p>\r\n<ul>{% for egy in egys_with_errors %}<li>{{ egy }}</li>{% endfor %}</ul>{% endif %}<p>\r\nCordialement,\r\nOsis UCLouvain</p>\r\n{% endautoescape %}',
              'HTML',
              'fr-be'])], elidable=True
        ),
        migrations.RunSQL(
            [(
             "INSERT INTO osis_common_messagetemplate (reference, subject, template, format, language) VALUES (%s, %s, %s, %s, %s);",
             ['egy_after_auto_postponement_txt',
              'Rapport d\u0027ex\u00e9cution de la proc\u00e9dure annuelle de copie des organisations de formation',
              '<p>Bonjour,</p>\r\n<p>Ceci est un message automatique g\u00e9n\u00e9r\u00e9 par le serveur OSIS – Merci de ne pas y r\u00e9pondre.</p>\r\n<p>Rapport d\u0027ex\u00e9cution de la proc\u00e9dure annuelle de copie des organisations de formation pour l\u0027ann\u00e9e acad\u00e9mique {{ end_academic_year }}.</p>\r\n<p>{{ egys_postponed }} UE copi\u00e9es de {{ academic_year }} en {{ end_academic_year }}.</p>\r\n<p>{{ egys_ending_this_year }} OF avec une fin d\u0027enseignement en {{ academic_year }}.</p>\r\n<p>{{ egys_already_existing }} UE existant pr\u00e9alablement en {{ end_academic_year }}.</p>\r\n{% if egys_with_errors %}<p>Les organisations de formation suivantes n\u0027ont pas \u00e9t\u00e9 recopi\u00e9es :</p>\r\n<ul>{% for egy in egys_with_errors %}<li>{{ egy }}</li>{% endfor %}</ul>{% endif %}<p>\r\nCordialement,\r\nOsis UCLouvain</p>\r\n',
              'PLAIN',
              'fr-be'])], elidable=True
        ),
        migrations.RunSQL(
            [(
             "INSERT INTO osis_common_messagetemplate (reference, subject, template, format, language) VALUES (%s, %s, %s, %s, %s);",
             ['egy_after_auto_postponement_html',
              'Report of the annual procedure of copy of the learning units',
              '{% autoescape off %}\r\n<p>Hello,</p>\r\n<p>This is an automatic message generated by the OSIS server – Please do not reply to this message.</p>\r\n<p>Report of the annual procedure of copy of the learning units for the academic year {{ end_academic_year }}.</p>\r\n<p>{{ egys_postponed }} LU copied from {{ academic_year }} to {{ end_academic_year }}.</p>\r\n<p>{{ egys_ending_this_year }} LU ending in {{ academic_year }}.</p>\r\n<p>{{ egys_already_existing }} LU already existing in {{ end_academic_year }}.</p>\r\n{% if egys_with_errors %}<p>Errors occured with the following learning units  :</p>\r\n<ul>{% for egy in egys_with_errors %}<li>{{ egy }}</li>{% endfor %}</ul>{% endif %}<p>\r\nRegards,\r\nOsis UCLouvain</p>\r\n{% endautoescape off %}',
              'HTML',
              'en'])], elidable=True
        ),
        migrations.RunSQL(
            [(
             "INSERT INTO osis_common_messagetemplate (reference, subject, template, format, language) VALUES (%s, %s, %s, %s, %s);",
             ['egy_after_auto_postponement_txt',
              'Report of the annual procedure of copy of the learning units',
              '<p>Hello,</p>\r\n<p>This is an automatic message generated by the OSIS server – Please do not reply to this message.</p>\r\n<p>Report of the annual procedure of copy of the learning units for the academic year {{ end_academic_year }}.</p>\r\n<p>{{ egys_postponed }} LU copied from {{ academic_year }} to {{ end_academic_year }}.</p>\r\n<p>{{ egys_ending_this_year }} LU ending in {{ academic_year }}.</p>\r\n<p>{{ egys_already_existing }} LU already existing in {{ end_academic_year }}.</p>\r\n{% if egys_with_errors %}<p>Errors occured with the following learning units  :</p>\r\n<ul>{% for egy in egys_with_errors %}<li>{{ egy }}</li>{% endfor %}</ul>{% endif %}<p>\r\nRegards,\r\nOsis UCLouvain</p>\r\n',
              'PLAIN',
              'en'])], elidable=True
        ),
    ]
