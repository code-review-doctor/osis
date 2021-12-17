# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-10-31 13:01
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0008_scorehistory'),
    ]

    operations = [
        migrations.RunSQL(
            [("UPDATE osis_common_messagetemplate SET template=%s WHERE reference=%s AND format=%s AND language=%s;",
             ["<p>{% autoescape off %}</p>\r\n\r\n<h3>Soumission de notes</h3>\r\n\r\n<p><em>Ceci est un message automatique g&eacute;n&eacute;r&eacute; par le serveur OSIS &ndash; Merci de ne pas y r&eacute;pondre.</em></p>\r\n\r\n<p><br />\r\nNous vous informons qu&#39;une soumission de notes &agrave; &eacute;t&eacute; effectu&eacute;e pour <strong>{{ learning_unit_name }}</strong></p>\r\n\r\n<p>{{ submitted_enrollments }}</p>\r\n\r\n<p>Statut : {{ encoding_status }}</p>\r\n\r\n<p>{{ signature }}</p>\r\n\r\n<p>{% endautoescape %}</p>",
              "assessments_scores_submission_html",
              'HTML',
              'fr-be'])], elidable=True
        ),
        migrations.RunSQL(
            [("UPDATE osis_common_messagetemplate SET template=%s WHERE reference=%s AND format=%s AND language=%s;",
             ["<p><em>Ceci est un message automatique g&eacute;n&eacute;r&eacute; par le serveur OSIS &ndash; Merci de ne pas y r&eacute;pondre.</em><br />\r\n<br />\r\nNous vous informons qu&#39;une soumission de notes &agrave; &eacute;t&eacute; effectu&eacute;e pour {{ learning_unit_name }}</p>\r\n\r\n<p>{{ submitted_enrollments }}</p>\r\n\r\n<p>Statut : {{ encoding_status }}</p>",
              "assessments_scores_submission_txt",
              'PLAIN',
              'fr-be'])], elidable=True
        ),
    ]
