# Generated by Django 2.2.24 on 2022-01-05 13:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('attribution', '0010_auto_20211117_1038'),
    ]

    operations = [
        migrations.RunSQL(
            [("UPDATE osis_common_messagetemplate SET template = %s WHERE reference='applications_confirmation_txt'; ",
              ['''
                           {% autoescape off %}
                               <p><i>Ceci est un message automatique généré par le serveur OSIS – Merci de ne pas y répondre.</i></p>
                               <p>A l'attention de {{first_name}} {{last_name}}.</p>
                               <p>Nous accusons réception de vo(tre)s candidature(s) au(x) cours suivant(s) :</p>
                               <p>{{applications}}</p>

                               <p>La publication des candidatures retenues est prévue pour le {{application_courses_publication_date}} sur le site de l'<a href="https://uclouvain.be/fr/decouvrir/espace-emploi-ti.html">UCLouvain</a>.</p>
                            {% endautoescape off %}
                           '''])],
        ),
        migrations.RunSQL(
            [("UPDATE osis_common_messagetemplate SET template = %s WHERE reference='applications_confirmation_html'; ",
              ['''
                           {% autoescape off %}
                              <p><i>Ceci est un message automatique généré par le serveur OSIS – Merci de ne pas y répondre.</i></p>
                              <p>A l'attention de {{first_name}} {{last_name}}.</p>
                              <p>Nous accusons réception de vo(tre)s candidature(s) au(x) cours suivant(s) :</p>
                              <p>{{applications}}</p>

                              <p>La publication des candidatures retenues est prévue pour le {{application_courses_publication_date}} sur le site de l'<a href="https://uclouvain.be/fr/decouvrir/espace-emploi-ti.html">UCLouvain</a>.</p>
                           {% endautoescape off %}
                           '''])],
        ),
    ]
