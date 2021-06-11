# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0485_create_events_lu_edition_fac_mgr'),
    ]

    operations = [
        migrations.RunSQL(
            [("UPDATE osis_common_messagetemplate SET template=%s WHERE reference=%s AND format=%s AND language=%s;",
              ['''{% autoescape off %}
             <link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
             <p>Bonjour,</p>
             <p>Ceci est un message automatique g\u00e9n\u00e9r\u00e9 par le serveur OSIS – Merci de ne pas y r\u00e9pondre.</p>
             <p>Rapport d\u0027ex\u00e9cution de la proc\u00e9dure annuelle de copie des unit\u00e9s d\u0027enseignement pour l\u0027ann\u00e9e acad\u00e9mique {{ end_academic_year }}.</p>
            
            <p><strong>{{ luys_postponed }} UE copi\u00e9es de {{ academic_year }} en {{ end_academic_year }}.</strong></p>
             {% if luys_postponed %}
             <div class="w3-responsive">
             <table cellpadding="10" class="w3-table w3-striped w3-hoverable">
                 <thead>
                     <tr>
                         <th align="left">Code</th>
                         <th align="left">Intitul&eacute;</th>
                     </tr>
                 </thead>
                  <tbody>
                 {% for luy in luys_postponed_qs %}
                     <tr>
                         <td align="left">{{ luy.acronym|default:"" }}</td>
                         <td align="left">{{ luy.complete_title }}</td>
                     </tr>
                 {% endfor %}
                 </tbody>
             </table>
             </div>
             {% endif %}
             <br>
             
             <p><strong>{{ luys_ending_this_year }} UE avec une fin d\u0027enseignement en {{ academic_year }}.</strong></p>
             {% if luys_ending_this_year %}    
             <div class="w3-responsive">
             <table cellpadding="10" class="w3-table w3-striped w3-hoverable">
                 <thead>
                     <tr>
                         <th align="left">Code</th>
                         <th align="left">Intitul&eacute;</th>
                     </tr>
                 </thead>
                  <tbody>
                 {% for lu in luys_ending_this_year_qs %}
                     {% with luy=lu.learningunityear_set.last %}
                     <tr>
                         <td align="left">{{ luy.acronym|default:"" }}</td>
                         <td align="left">{{ luy.complete_title }}</td>
                     </tr>
                     {% endwith %}
                 {% endfor %}
                 </tbody>
             </table>
             </div>
             {% endif %}
             <br>
             
             <p><strong>{{ luys_already_existing }} UE existant pr\u00e9alablement en {{ end_academic_year }}.</strong></p>
             {% if luys_already_existing %}          
             <div class="w3-responsive">
             <table cellpadding="10" class="w3-table w3-striped w3-hoverable">
                 <thead>
                     <tr>
                         <th align="left">Code</th>
                         <th align="left">Intitul&eacute;</th>
                     </tr>
                 </thead>
                  <tbody>
                 {% for lu in luys_already_existing_qs %}
                     {% with luy=lu.learningunityear_set.last %}
                     <tr>
                         <td align="left">{{ luy.acronym|default:"" }}</td>
                         <td align="left">{{ luy.complete_title }}</td>
                     </tr>
                     {% endwith %}
                 {% endfor %}
                 </tbody>
             </table>
             </div>
             {% endif %}
             <br>
             
             {% if luys_with_errors %}
             <p><strong>Les unit\u00e9s d\u0027enseignement suivantes n\u0027ont pas \u00e9t\u00e9 recopi\u00e9es :</strong></p>
             <div class="w3-responsive">
             <table cellpadding="10" class="w3-table w3-striped w3-hoverable">
                 <thead>
                     <tr>
                         <th align="left">Code</th>
                         <th align="left">Intitul&eacute;</th>
                     </tr>
                 </thead>
                  <tbody>
                 {% for lu in luys_with_errors %}
                     {% with luy=lu.learningunityear_set.last %}
                     <tr>
                         <td align="left">{{ luy.acronym|default:"" }}</td>
                         <td align="left">{{ luy.complete_title }}</td>
                     </tr>
                     {% endwith %}
                 {% endfor %}
                 </tbody>
             </table>
             </div>
             <br>
             {% endif %}
             <p>Cordialement, Osis UCLouvain</p>
             {% endautoescape %}''',
               'luy_after_auto_postponement_html',
               'HTML',
               'fr-be'])], elidable=True
        ),
        migrations.RunSQL(
            [("UPDATE osis_common_messagetemplate SET template=%s WHERE reference=%s AND format=%s AND language=%s;",
              ['''<p>Bonjour,</p>
             <p>Ceci est un message automatique g\u00e9n\u00e9r\u00e9 par le serveur OSIS – Merci de ne pas y r\u00e9pondre.</p>
             <p>Rapport d\u0027ex\u00e9cution de la proc\u00e9dure annuelle de copie des unit\u00e9s d\u0027enseignement pour l\u0027ann\u00e9e acad\u00e9mique {{ end_academic_year }}.</p>
             
             <p><strong>{{ luys_postponed }} UE copi\u00e9es de {{ academic_year }} en {{ end_academic_year }}.<strong/></p>
             {% if luys_postponed %}
             <strong>Code - Intitul&eacute;</strong><br/>
                 {% for luy in luys_postponed_qs %}
                     {{ luy.acronym|default:"" }} - {{ luy.complete_title }}<br/>
                 {% endfor %}
             {% endif %}                       
             <br>
             
             <p><strong>{{ luys_ending_this_year }} UE avec une fin d\u0027enseignement en {{ academic_year }}.</strong></p>
             {% if luys_ending_this_year %}                    
             <strong>Code - Intitul&eacute;</strong><br/>
                 {% for lu in luyss_ending_this_year_qs %}
                     {% with luy=lu.learningunityear_set.last %}
                     {{ luy.acronym|default:"" }} - {{ luy.complete_title }}<br/>
                     {% endwith %}
                 {% endfor %}
             {% endif %}
             <br>     
              
             <p><strong>{{ luys_already_existing }} UE existant pr\u00e9alablement en {{ end_academic_year }}.</strong></p>
             {% if luys_already_existing %}                
                <strong>Code - Intitul&eacute;</strong><br/>
                    {% for lu in luys_ending_this_year_qs %}
                        {% with luy=lu.learningunityear_set.last %}
                        {{ luy.acronym|default:"" }} - {{ luy.complete_title }}<br/>
                        {% endwith %}
                    {% endfor %}
             {% endif %}
             <br>
             
             {% if luys_with_errors %}
                 <p><strong>Les unit\u00e9s d\u0027enseignement suivantes n\u0027ont pas \u00e9t\u00e9 recopi\u00e9es :</strong></p>
                 strong>Code - Intitul&eacute;</strong><br/>
                    {% for lu in luys_with_errors %}
                    {% with luy=lu.learningunityear_set.last %}
                        {{ luy.acronym|default:"" }} - {{ luy.complete_title }}<br/>
                     {% endwith %}
                    {% endfor %}
                 <br>
             {% endif %}
             
             <p>Cordialement, Osis UCLouvain</p>
             ''',
               'luy_after_auto_postponement_txt',
               'PLAIN',
               'fr-be'])], elidable=True
        ),
        migrations.RunSQL(
            [("UPDATE osis_common_messagetemplate SET template=%s WHERE reference=%s AND format=%s AND language=%s;",
              ['''{% autoescape off %}
             <p>Hello,</p>
             <p>This is an automatic message generated by the OSIS server – Please do not reply to this message.</p>
             <p>Report of the annual procedure of copy of the learning units for the academic year {{ end_academic_year }}.</p>
             
             <p><strong>{{ luys_postponed }} LU copied from {{ academic_year }} to {{ end_academic_year }}.</strong></p>
             {% if luys_postponed %}
             <div class="w3-responsive">
             <table cellpadding="10" class="w3-table w3-striped w3-hoverable">
                 <thead>
                     <tr>
                         <th align="left">Code</th>
                         <th align="left">Title</th>
                     </tr>
                 </thead>
                  <tbody>
                 {% for luy in luys_postponed_qs %}
                     <tr>
                         <td align="left">{{ luy.acronym|default:"" }}</td>
                         <td align="left">{{ luy.complete_title }}</td>
                     </tr>
                 {% endfor %}
                 </tbody>
             </table>
             </div>
             {% endif %}                  
             <br>
             
             <p><strong>{{ luys_ending_this_year }} LU ending in {{ academic_year }}.</strong></p>
             {% if luys_ending_this_year %}                    
             <div class="w3-responsive">
             <table cellpadding="10" class="w3-table w3-striped w3-hoverable">
                 <thead>
                     <tr>
                         <th align="left">Code</th>
                         <th align="left">Title</th>
                     </tr>
                 </thead>
                  <tbody>
                 {% for lu in luys_ending_this_year_qs %}
                     {% with luy=lu.learningunityear_set.last %}
                     <tr>
                         <td align="left">{{ luy.acronym|default:"" }}</td>
                         <td align="left">{{ luy.complete_title }}</td>
                     </tr>
                     {% endwith %}
                 {% endfor %}
                 </tbody>
             </table>
             </div>
             {% endif %}
             <br>
             
             <p><strong>{{ luys_already_existing }} LU already existing in {{ end_academic_year }}.</strong></p>
             {% if luys_already_existing %}                
             <div class="w3-responsive">
             <table cellpadding="10" class="w3-table w3-striped w3-hoverable">
                 <thead>
                     <tr>
                         <th align="left">Code</th>
                         <th align="left">Title</th>
                     </tr>
                 </thead>
                  <tbody>
                 {% for lu in luys_already_existing_qs %}
                     {% with luy=lu.learningunityear_set.last %}
                     <tr>
                         <td align="left">{{ luy.acronym|default:"" }}</td>
                         <td align="left">{{ luy.complete_title }}</td>
                     </tr>
                     {% endwith %}
                 {% endfor %}
                 </tbody>
             </table>
             </div>
             {% endif %}
             <br>
             
             {% if luys_with_errors %}
             <p><strong>Errors occured with the following learning units :</strong></p>
             <div class="w3-responsive">
             <table cellpadding="10" class="w3-table w3-striped w3-hoverable">
                 <thead>
                     <tr>
                         <th align="left">Code</th>
                         <th align="left">Title</th>
                     </tr>
                 </thead>
                  <tbody>
                 {% for lu in luys_with_errors %}
                     {% with luy=lu.learningunityear_set.last %}
                     <tr>
                         <td align="left">{{ luy.acronym|default:"" }}</td>
                         <td align="left">{{ luy.complete_title }}</td>
                     </tr>
                     {% endwith %}
                 {% endfor %}
                 </tbody>
             </table>
             </div>
             <br>
             {% endif %}
             
             <p>Regards, Osis UCLouvain</p>
             {% endautoescape off %}''',
               'luy_after_auto_postponement_html',
               'HTML',
               'en'])], elidable=True
        ),
        migrations.RunSQL(
            [("UPDATE osis_common_messagetemplate SET template=%s WHERE reference=%s AND format=%s AND language=%s;",
              ['''<p>Hello,</p>
             <p>This is an automatic message generated by the OSIS server – Please do not reply to this message.</p>
             <p>Report of the annual procedure of copy of the learning units for the academic year {{ end_academic_year }}.</p>
             
             <p><strong>{{ luys_postponed }} LU copied from {{ academic_year }} to {{ end_academic_year }}.</strong></p>
             {% if luys_postponed %}
             <strong>Code - Title</strong><br/>
                 {% for luy in luys_postponed_qs %}
                     {{ luy.acronym|default:"" }} - {{ luy.complete_title }}<br/>
                 {% endfor %}
             {% endif %}                             
             <br>
             
             <p><strong>{{ luys_ending_this_year }} LU ending in {{ academic_year }}.</strong></p>
             {% if luys_ending_this_year %}                    
             <strong>Code - Title</strong><br/>
                 {% for lu in luyss_ending_this_year_qs %}
                     {% with luy=lu.learningunityear_set.last %}
                     {{ luy.acronym|default:"" }} - {{ luy.complete_title }}<br/>
                     {% endwith %}
                 {% endfor %}
             {% endif %}
             <br>       
             
             <p><strong>{{ luys_already_existing }} LU already existing in {{ end_academic_year }}.</strong></p>
             {% if luys_already_existing %}                
                <strong>Code - Title</strong><br/>
                    {% for lu in luys_ending_this_year_qs %}
                        {% with luy=lu.learningunityear_set.last %}
                        {{ luy.acronym|default:"" }} - {{ luy.complete_title }}<br/>
                        {% endwith %}
                    {% endfor %}
             {% endif %}
             <br>
             
             {% if luys_with_errors %}
                 <p><strong>Errors occured with the following learning units :</strong></p>
                 <strong>Code - Title</strong><br/>
                    {% for lu in luys_with_errors %}
                    {% with luy=lu.learningunityear_set.last %}
                        {{ luy.acronym|default:"" }} - {{ luy.complete_title }}<br/>
                     {% endwith %}
                    {% endfor %}
                 <br>
             {% endif %}
             
             <p>Regards, Osis UCLouvain</p>
             ''',
               'luy_after_auto_postponement_txt',
               'PLAIN',
               'en'])], elidable=True
        ),
        migrations.RunSQL(
            [("UPDATE osis_common_messagetemplate SET template=%s WHERE reference=%s AND format=%s AND language=%s;",
              ['''{% autoescape off %}
                    <link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
                    <p>Bonjour,</p>
                    <p>Ceci est un message automatique g&eacute;n&eacute;r&eacute; par le serveur OSIS &ndash; Merci de ne pas y r&eacute;pondre.</p>
                    <p>Rapport d\u0027ex\u00e9cution de la proc\u00e9dure annuelle de copie des organisations de formation pour l\u0027ann\u00e9e acad\u00e9mique {{ current_academic_year }}.</p>
                    
                    <p><strong>{{ egys_postponed }} OF copi&eacute;es de {{ previous_academic_year }} en {{ current_academic_year }}.</strong></p>
                    {% if egys_postponed %}
                    <div class="w3-responsive">
                    <table cellpadding="10" class="w3-table w3-striped w3-hoverable">
                        <thead>
                            <tr>
                                <th></th>
                                <th align="left">Sigle</th>
                                <th align="left">Code</th>
                                <th align="left">Intitul&eacute;</th>
                            </tr>
                        </thead>
                        <tbody>
                        {% for egy in egys_postponed_qs %}
                            <tr>
                            {% ifchanged  egy.verbose_type%}
                                <th align="left">{{ egy.verbose_type }}</th>
                            {% else %}
                                <th></th>
                            {% endifchanged %}
                                <td align="left">{{ egy.acronym|default:"" }}</td>
                                <td align="left">{{ egy.partial_acronym|default:"" }}</td>
                                <td align="left">{{ egy.complete_title }}</td>
                            </tr>
                        {% endfor %}
                        </tbody>
                    </table>
                    </div>
                    {% endif %}
                    <br>
                    
                    <p><strong>{{ egys_ending_this_year }} OF avec une fin d&#39;enseignement en {{ previous_academic_year }}.</strong></p>
                    {% if egys_ending_this_year %}
                    <div class="w3-responsive">
                    <table cellpadding="10" class="w3-table w3-striped w3-hoverable">
                        <thead>
                            <tr>
                                <th></th>
                                <th align="left">Sigle</th>
                                <th align="left">Code</th>
                                <th align="left">Intitul&eacute;</th>
                            </tr>
                        </thead>
                        <tbody>
                        {% for eg in egys_ending_this_year_qs %}
                            {% with egy=eg.educationgroupyear_set.last %}
                            <tr>
                            {% ifchanged  egy.verbose_type%}
                                <th align="left">{{ egy.verbose_type }}</th>
                            {% else %}
                                <th></th>
                            {% endifchanged %}
                                <td align="left">{{ egy.acronym|default:"" }}</td>
                                <td align="left">{{ egy.partial_acronym|default:"" }}</td>
                                <td align="left">{{ egy.complete_title }}</td>
                            </tr>
                            {% endwith %}
                        {% endfor %}
                        </tbody>
                    </table>
                    </div>
                    {% endif %}
                    <br>
                    
                    <p><strong>{{ egys_already_existing }} OF existant pr&eacute;alablement en {{ current_academic_year }}.</strong></p>
                    {% if egys_already_existing %}
                    <div class="w3-responsive">
                    <table cellpadding="10" class="w3-table w3-striped w3-hoverable">
                        <thead>
                            <tr>
                                <th></th>
                                <th align="left">Sigle</th>
                                <th align="left">Code</th>
                                <th align="left">Intitul&eacute;</th>
                            </tr>
                        </thead>
                        <tbody>
                        {% for eg in egys_already_existing_qs %}
                            {% with egy=eg.educationgroupyear_set.last %}
                            <tr>
                            {% ifchanged  egy.verbose_type%}
                                <th align="left">{{ egy.verbose_type }}</th>
                            {% else %}
                                <th></th>
                            {% endifchanged %}
                                <td align="left">{{ egy.acronym|default:"" }}</td>
                                <td align="left">{{ egy.partial_acronym|default:"" }}</td>
                                <td align="left">{{ egy.complete_title }}</td>
                            </tr>
                            {% endwith %}
                        {% endfor %}
                        </tbody>
                    </table>
                    </div>
                    {% endif %}
                    <br>
                    
                    {% if egys_with_errors %}
                    <p><strong>Les organisations de formation suivantes n&#39;ont pas &eacute;t&eacute; recopi&eacute;es :</strong></p>
                    <div class="w3-responsive">
                    <table cellpadding="10" class="w3-table w3-striped w3-hoverable">
                        <thead>
                            <tr>
                                <th align="left">Sigle</th>
                                <th align="left">Code</th>
                                <th align="left">Intitul&eacute;</th>
                            </tr>
                        </thead>
                        <tbody>
                        {% for eg in egys_with_errors %}
                            {% with egy=eg.educationgroupyear_set.last %}
                            <tr>
                                <td align="left">{{ egy.acronym|default:"" }}</td>
                                <td align="left">{{ egy.partial_acronym|default:"" }}</td>
                                <td align="left">{{ egy.complete_title }}</td>
                            </tr>
                            {% endwith %}
                        {% endfor %}
                        </tbody>
                    </table>
                    </div>
                    <br>
                    {% endif %}
            
                    <p>Cordialement, Osis UCLouvain</p>
            {% endautoescape %}''',
               'egy_after_auto_postponement_html',
               'HTML',
               'fr-be'])], elidable=True
        ),
        migrations.RunSQL(
            [("UPDATE osis_common_messagetemplate SET template=%s WHERE reference=%s AND format=%s AND language=%s;",
              ['''<p>Bonjour,</p>
                    
                    <p>Ceci est un message automatique g&eacute;n&eacute;r&eacute; par le serveur OSIS &ndash; Merci de ne pas y r&eacute;pondre.</p>
                    
                    <p>Rapport d\u0027ex\u00e9cution de la proc\u00e9dure annuelle de copie des organisations de formation pour l\u0027ann\u00e9e acad\u00e9mique {{ current_academic_year }}.</p>
                    
                    <p><strong>{{ egys_postponed }} OF copi&eacute;es de {{ previous_academic_year }} en {{ current_academic_year }}.</strong></p>
                    {% if egys_postponed %}
                    <strong>Sigle - Code - Intitul&eacute;</strong><br/>
                        {% for egy in egys_postponed_qs %}
                            {% ifchanged  egy.verbose_type%}
                                <strong>{{ egy.verbose_type }}</strong><br/>
                            {% endifchanged %}
                            {{ egy.acronym|default:"" }} - {{ egy.partial_acronym|default:"" }} - {{ egy.complete_title }}<br/>
                        {% endfor %}
                    {% endif %}
                    <br>
                    
                    <p><strong>{{ egys_ending_this_year }} OF avec une fin d&#39;enseignement en {{ previous_academic_year }}.</strong></p>
                    {% if egys_ending_this_year %}
                    <strong>Sigle - Code - Intitul&eacute;</strong><br/>
                        {% for eg in egys_ending_this_year_qs %}
                            {% with egy=eg.educationgroupyear_set.last %}
                            {% ifchanged  egy.verbose_type%}
                                <strong>{{ egy.verbose_type }}</strong><br/>
                            {% endifchanged %}
                            {{ egy.acronym|default:"" }} - {{ egy.partial_acronym|default:"" }} - {{ egy.complete_title }}<br/>
                            {% endwith %}
                        {% endfor %}
                    {% endif %}
                    <br>
                    
                    <p><strong>{{ egys_already_existing }} OF existant pr&eacute;alablement en {{ current_academic_year }}.</strong></p>
                    {% if egys_already_existing %}
                    <strong>Sigle - Code - Intitul&eacute;</strong><br/>
                        {% for eg in egys_already_existing_qs %}
                            {% with egy=eg.educationgroupyear_set.last %}
                            {% ifchanged  egy.verbose_type%}
                                <strong>{{ egy.verbose_type }}</strong><br/>
                            {% endifchanged %}
                            {{ egy.acronym|default:"" }} - {{ egy.partial_acronym|default:"" }} - {{ egy.complete_title }}<br/>
                            {% endwith %}
                        {% endfor %}
                    {% endif %}
                    <br>
                    
                    {% if egys_with_errors %}
                        <p><strong>Les organisations de formation suivantes n&#39;ont pas &eacute;t&eacute; recopi&eacute;es :</strong></p>
                    
                    <strong>Sigle - Code - Intitul&eacute;</strong><br/>
                        {% for eg in egys_with_errors %}
                        {% with egy=eg.educationgroupyear_set.last %}
                            {{ egy.acronym|default:"" }} - {{ egy.partial_acronym|default:"" }} - {{ egy.complete_title }}<br/>
                         {% endwith %}
                        {% endfor %}
                        <br>
                    {% endif %}
                    <p>Cordialement, Osis UCLouvain</p>
                ''',
               'egy_after_auto_postponement_txt',
               'PLAIN',
               'fr-be'])], elidable=True
        ),
        migrations.RunSQL(
            [("UPDATE osis_common_messagetemplate SET template=%s WHERE reference=%s AND format=%s AND language=%s;",
              ['''{% autoescape off %}
                    <link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
                    <p>Hello,</p>
                    <p>This is an automatic message generated by the OSIS server &ndash; Please do not reply to this message.</p>
                    <p>Report of the annual procedure of copy of the education groups for the academic year {{ current_academic_year }}.</p>
                    
                    <p><strong>{{ egys_postponed }} EG copied from {{ previous_academic_year }} to {{ current_academic_year }}.</strong></p>
                    {% if egys_postponed %}
                    <div class="w3-responsive">
                    <table cellpadding="10" class="w3-table w3-striped w3-hoverable">
                        <thead>
                            <tr>
                                <th></th>
                                <th>Acronym</th>
                                <th>Code</th>
                                <th>Title</th>
                            </tr>
                        </thead>
                        <tbody>
                        {% for egy in egys_postponed_qs %}
                            <tr>
                            {% ifchanged  egy.verbose_type%}
                                <th>{{ egy.verbose_type }}</th>
                            {% else %}
                                <th></th>
                            {% endifchanged %}
                                <td>{{ egy.acronym|default:"" }}</td>
                                <td>{{ egy.partial_acronym|default:"" }}</td>
                                <td>{{ egy.complete_title }}</td>
                            </tr>
                        {% endfor %}
                        </tbody>
                    </table>
                    </div>
                    {% endif %}
                    <br>
                    
                    <p><strong>{{ egys_ending_this_year }} EG ending in {{ previous_academic_year }}.</strong></p>
                    {% if egys_ending_this_year %}
                    <div class="w3-responsive">
                    <table cellpadding="10" class="w3-table w3-striped w3-hoverable">
                        <thead>
                            <tr>
                                <th></th>
                                <th align="left">Acronym</th>
                                <th align="left">Code</th>
                                <th align="left">Title</th>
                            </tr>
                        </thead>
                        <tbody>
                        {% for eg in egys_ending_this_year_qs %}
                            {% with egy=eg.educationgroupyear_set.last %}
                            <tr>
                            {% ifchanged  egy.verbose_type%}
                                <th align="left">{{ egy.verbose_type }}</th>
                            {% else %}
                                <th></th>
                            {% endifchanged %}
                                <td align="left">{{ egy.acronym|default:"" }}</td>
                                <td align="left">{{ egy.partial_acronym|default:"" }}</td>
                                <td align="left">{{ egy.complete_title }}</td>
                            </tr>
                            {% endwith %}
                        {% endfor %}
                        </tbody>
                    </table>
                    </div>
                    {% endif %}
                    <br>
                    
                    <p><strong>{{ egys_already_existing }} EG already existing in {{ current_academic_year }}.</strong></p>
                    {% if egys_already_existing %}
                    <div class="w3-responsive">
                    <table cellpadding="10" class="w3-table w3-striped w3-hoverable">
                        <thead>
                            <tr>
                                <th></th>
                                <th>Acronym</th>
                                <th>Code</th>
                                <th>Title</th>
                            </tr>
                        </thead>
                        <tbody>
                        {% for eg in egys_already_existing_qs %}
                            {% with egy=eg.educationgroupyear_set.last %}
                            <tr>
                            {% ifchanged  egy.verbose_type%}
                                <th>{{ egy.verbose_type }}</th>
                            {% else %}
                                <th></th>
                            {% endifchanged %}
                                <td>{{ egy.acronym|default:"" }}</td>
                                <td>{{ egy.partial_acronym|default:"" }}</td>
                                <td>{{ egy.complete_title }}</td>
                            </tr>
                            {% endwith %}
                        {% endfor %}
                        </tbody>
                    </table>
                    </div>
                    {% endif %}
                    <br>
                    
                    {% if egys_with_errors %}
                        <p><strong>Errors occured with the following education groups :</strong></p>
                        <div class="w3-responsive">
                        <table cellpadding="10" class="w3-table w3-striped w3-hoverable">
                            <thead>
                                <tr>
                                    <th>Acronym</th>
                                    <th>Code</th>
                                    <th>Title</th>
                                </tr>
                            </thead>
            
                            <tbody>
                            {% for eg in egys_with_errors %}
                                {% with egy=eg.educationgroupyear_set.last %}
                                <tr>
                                    <td>{{ egy.acronym|default:"" }}</td>
                                    <td>{{ egy.partial_acronym|default:"" }}</td>
                                    <td>{{ egy.complete_title }}</td>
                                </tr>
                                {% endwith %}
                            {% endfor %}
                            </tbody>
                        </table>
                        </div>
                        <br>
                    {% endif %}
            
                    <p>Regards, Osis UCLouvain</p>
            {% endautoescape %}''',
               'egy_after_auto_postponement_html',
               'HTML',
               'en'])], elidable=True
        ),
        migrations.RunSQL(
            [("UPDATE osis_common_messagetemplate SET template=%s WHERE reference=%s AND format=%s AND language=%s;",
              ['''<p>Hello,</p>
                    
                    <p>This is an automatic message generated by the OSIS server &ndash; Please do not reply to this message.</p>
                    
                    <p>Report of the annual procedure of copy of the education groups for the academic year {{ current_academic_year }}.</p>
                    
                    <p><strong>{{ egys_postponed }} EG copied from {{ previous_academic_year }} to {{ current_academic_year }}.</strong></p>
                    {% if egys_postponed %}
                    
                    <strong>Acronym - Code - Title</strong><br/>
                        {% for egy in egys_postponed_qs %}
                            {% ifchanged  egy.verbose_type%}
                                <strong>{{ egy.verbose_type }}</strong><br/>
                            {% endifchanged %}
                            {{ egy.acronym|default:"" }} - {{ egy.partial_acronym|default:"" }} - {{ egy.complete_title }}<br/>
                        {% endfor %}
                    {% endif %}
                    <br>
                    
                    <p><strong>{{ egys_ending_this_year }} EG ending in {{ previous_academic_year }}.</strong></p>
                    {% if egys_ending_this_year %}
                    
                    <strong>Acronym - Code - Title</strong><br/>
                        {% for eg in egys_ending_this_year_qs %}
                            {% with egy=eg.educationgroupyear_set.last %}
                            {% ifchanged  egy.verbose_type%}
                                <strong>{{ egy.verbose_type }}</strong><br/>
                            {% endifchanged %}
                            {{ egy.acronym|default:"" }} - {{ egy.partial_acronym|default:"" }} - {{ egy.complete_title }}<br/>
                            {% endwith %}
                        {% endfor %}
                    {% endif %}
                    <br>
                    
                    <p><strong>{{ egys_already_existing }} EG already existing in {{ current_academic_year }}.</strong></p>
                    {% if egys_already_existing %}
                    
                    <strong>Acronym - Code - Title</strong><br/>
                        {% for eg in egys_already_existing_qs %}
                            {% with egy=eg.educationgroupyear_set.last %}
                            {% ifchanged  egy.verbose_type%}
                                <strong>{{ egy.verbose_type }}</strong><br/>
                            {% endifchanged %}
                            {{ egy.acronym|default:"" }} - {{ egy.partial_acronym|default:"" }} - {{ egy.complete_title }}<br/>
                            {% endwith %}
                        {% endfor %}
                    {% endif %}
                    <br>
                    
                    {% if egys_with_errors %}
                    
                        <p><strong>Errors occured with the following education groups :</strong></p>
                    
                    <strong>Acronym - Code - Title</strong><br/>
                        {% for eg in egys_with_errors %}
                        {% with egy=eg.educationgroupyear_set.last %}
                            {{ egy.acronym|default:"" }} - {{ egy.partial_acronym|default:"" }} - {{ egy.complete_title }}<br/>
                        {% endwith %}
                        {% endfor %}
                        <br>
                    {% endif %}
                    
                    <p>Regards, Osis UCLouvain</p>
                ''',
               'egy_after_auto_postponement_txt',
               'PLAIN',
               'en'])], elidable=True
        ),
    ]
