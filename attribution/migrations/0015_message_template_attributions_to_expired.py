# Generated by Django 2.2.24 on 2021-11-17 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attribution', '0014_merge_20220106_1142'),
    ]

    operations = [
        migrations.RunSQL(
            [("INSERT INTO osis_common_messagetemplate (template, subject, reference, format, language) "
              "VALUES(%s, %s, %s ,%s ,%s);",
              ['''
                        {% autoescape off %}
                            <p><em>Ceci est un message automatique g&eacute;n&eacute;r&eacute; par le serveur OSIS &ndash; Merci de ne pas y r&eacute;pondre.</em></p>
                            <p>A l&#39;attention de {{first_name}} {{last_name}}.</p>
                            <br/>
                            <p>Nous attirons votre attention sur le fait que certaines de vos charges arrivent &agrave; &eacute;ch&eacute;ance :</p>
                            <p>{{ending_attributions}}</p>
                            <br/>
                            <p>Le d&eacute;p&ocirc;t des candidatures aux cours vacants est possible jusqu’au {{end_date}}, pour plus 
                            d&#39;informations : <a href="https://uclouvain.be/fr/decouvrir/cours-vacants.html">https://uclouvain.be/fr/decouvrir/cours-vacants.html</a></p> 
                        {% endautoescape off %}
                        ''',
               'Charges d&#39;enseignement arrivant &agrave; &eacute;ch&eacute;ance',
               'ending_attributions_txt',
               'PLAIN',
               'fr-be'])],
        ),
        migrations.RunSQL(
            [("INSERT INTO osis_common_messagetemplate (template, subject, reference, format, language) "
              "VALUES(%s, %s, %s ,%s ,%s);",
              ['''
                           {% autoescape off %}
                            <p><em>Ceci est un message automatique généré par le serveur OSIS – Merci de ne pas y répondre.</em></p>
                            <p>A l'attention de {{first_name}} {{last_name}}.</p>
                            <br>
                            <p>Nous attirons votre attention sur le fait que certaines de vos charges arrivent à échéance :</p>
                            <p>{{ending_attributions}}</p>
                            <br>
                            <p>Le dépôt des candidatures aux cours vacants est possible jusqu’au {{end_date}}, pour plus 
                            d’informations : <a href="https://uclouvain.be/fr/decouvrir/cours-vacants.html">https://uclouvain.be/fr/decouvrir/cours-vacants.html</a></p>
                            {% endautoescape off %}
                           ''',
               'Charges d&#39;enseignement arrivant &agrave; &eacute;ch&eacute;ance',
               'ending_attributions_html',
               'HTML',
               'fr-be'])],
        ),
    ]
