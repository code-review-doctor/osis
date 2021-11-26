# Generated by Django 2.2.24 on 2021-11-17 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attribution', '0009_delete_attribution'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tutorapplication',
            name='function',
        ),
        migrations.AlterField(
            model_name='tutorapplication',
            name='volume_lecturing',
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=6, null=True),
        ),
        migrations.AlterField(
            model_name='tutorapplication',
            name='volume_pratical_exercice',
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=6, null=True),
        ),
        migrations.RunSQL(
            [("UPDATE osis_common_messagetemplate SET template = %s WHERE reference='applications_confirmation_txt'; ",
              ['''
                       {% autoescape off %}
                           <p>Ceci est un message automatique généré par le serveur OSIS – Merci de ne pas y répondre.</p>
                           <p>A l'attention de {{first_name}} {{last_name}}.</p>
                           <p>Nous accusons réception de vo(tre)s candidature(s) aux cours suivants :</p>
                           <p>- directement via votre bureau, pour la (les) charge(s) suivante(s) :</p>
                           <p>{{applications}}</p>

                           <p>Un accusé de réception définitif vous sera transmis à la fin de la période de candidature.</p>
                           <p>La publication des candidatures retenues est prévue pour le mois de mai {{application_courses_targeted_year}} sur le site de l'UCL.</p>
                        {% endautoescape off %}
                       '''])],
        ),
        migrations.RunSQL(
            [("UPDATE osis_common_messagetemplate SET template = %s WHERE reference='applications_confirmation_html'; ",
              ['''
                       {% autoescape off %}
                          <p>Ceci est un message automatique généré par le serveur OSIS – Merci de ne pas y répondre.</p>
                          <p>A l'attention de {{first_name}} {{last_name}}.</p>
                          <p>Nous accusons réception de vo(tre)s candidature(s) aux cours suivants :</p>
                          <p>- directement via votre bureau, pour la (les) charge(s) suivante(s) :</p>
                          <p>{{applications}}</p>

                          <p>Un accusé de réception définitif vous sera transmis à la fin de la période de candidature.</p>
                          <p>La publication des candidatures retenues est prévue pour le mois de mai {{application_courses_targeted_year}} sur le site de l'UCL.</p>
                       {% endautoescape off %}
                       '''])],
        ),
    ]
