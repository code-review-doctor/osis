# Generated by Django 2.2.13 on 2021-11-03 14:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('base', '0612_auto_20211018_1706'),
        ('reference', '0009_auto_20211025_1239'),
    ]

    operations = [
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latin', models.PositiveIntegerField(default=0, verbose_name='Latin')),
                ('greek', models.PositiveIntegerField(default=0, verbose_name='Greek')),
                ('chemistry', models.PositiveIntegerField(default=0, verbose_name='Chemistry')),
                ('physic', models.PositiveIntegerField(default=0, verbose_name='Physic')),
                ('biology', models.PositiveIntegerField(default=0, verbose_name='Biology')),
                ('german', models.PositiveIntegerField(default=0, verbose_name='German')),
                ('dutch', models.PositiveIntegerField(default=0, verbose_name='Dutch')),
                ('english', models.PositiveIntegerField(default=0, verbose_name='English')),
                ('french', models.PositiveIntegerField(default=0, verbose_name='french')),
                ('modern_languages_other_label', models.CharField(blank=True, default='', help_text='If other language, please specify', max_length=25, verbose_name='Other')),
                ('modern_languages_other_hours', models.PositiveIntegerField(blank=True, null=True)),
                ('mathematics', models.PositiveIntegerField(default=0, verbose_name='Mathematics')),
                ('it', models.PositiveIntegerField(default=0, verbose_name='IT')),
                ('social_sciences', models.PositiveIntegerField(default=0, verbose_name='Social sciences')),
                ('economic_sciences', models.PositiveIntegerField(default=0, verbose_name='Economic sciences')),
                ('other_label', models.CharField(blank=True, default='', help_text='If other optional domains, please specify', max_length=25, verbose_name='Other')),
                ('other_hours', models.PositiveIntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ForeignHighSchoolDiploma',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('result', models.CharField(choices=[('NOT_KNOWN_YET_RESULT', 'Not known yet'), ('LT_65_RESULT', 'Less than 65%'), ('BTW_65_AND_75_RESULT', 'Between 65 and 75%'), ('GT_75_RESULT', 'More than 75%')], max_length=25, null=True, verbose_name='At which result level do you consider yourself?')),
                ('foreign_diploma_type', models.CharField(choices=[('NATIONAL_BACHELOR', 'National Bachelor (or government diploma, ...)'), ('EUROPEAN_BACHELOR', 'European Bachelor (Schola Europaea)'), ('INTERNATIONAL_BACCALAUREATE', 'International Baccalaureate')], max_length=50, null=True, verbose_name='What diploma did you get (or will you get)?')),
                ('other_linguistic_regime', models.CharField(blank=True, default='', max_length=25, verbose_name='If other linguistic regime, please clarify')),
                ('academic_graduation_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='base.AcademicYear', verbose_name='Please mention the academic graduation year')),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='reference.Country', verbose_name='Organizing country')),
                ('linguistic_regime', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='reference.Language', verbose_name='Linguistic regime')),
                ('person', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='base.Person')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BelgianHighSchoolDiploma',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('result', models.CharField(choices=[('NOT_KNOWN_YET_RESULT', 'Not known yet'), ('LT_65_RESULT', 'Less than 65%'), ('BTW_65_AND_75_RESULT', 'Between 65 and 75%'), ('GT_75_RESULT', 'More than 75%')], max_length=25, null=True, verbose_name='At which result level do you consider yourself?')),
                ('community', models.CharField(choices=[('FRENCH_SPEAKING', 'French-speaking Community of Belgium'), ('FLEMISH_SPEAKING', 'Flemish-speaking Community'), ('GERMAN_SPEAKING', 'German-speaking Community')], max_length=25, null=True, verbose_name='In what Community did (do) you follow last year of high school?')),
                ('educational_type', models.CharField(blank=True, choices=[('TEACHING_OF_GENERAL_EDUCATION', 'Teaching of general education'), ('TRANSITION_METHOD', 'Transition method'), ('ARTISTIC_TRANSITION', 'Artistic transition'), ('QUALIFICATION_METHOD', 'Qualification method'), ('ARTISTIC_QUALIFICATION', 'Artistic qualification'), ('PROFESSIONAL_EDUCATION', 'Professional education'), ('PROFESSIONAL_EDUCATION_AND_MATURITY_EXAM', 'Professional education + Maturity exam')], max_length=50, null=True, verbose_name='What type of education did (do) you follow?')),
                ('educational_other', models.CharField(blank=True, default='', max_length=50, verbose_name='Other education, to specify')),
                ('course_repeat', models.BooleanField(default=False, verbose_name='Did you repeat certain study years during your studies?')),
                ('course_orientation', models.BooleanField(default=False, verbose_name='Did you change of orientation during your studies?')),
                ('institute', models.CharField(blank=True, default='', max_length=25, verbose_name='Institute')),
                ('other_institute', models.CharField(blank=True, default='', help_text='In case you could not find your institute in the list, please mention it below. ', max_length=500, verbose_name='Another institute')),
                ('academic_graduation_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='base.AcademicYear', verbose_name='Please mention the academic graduation year')),
                ('person', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='base.Person')),
                ('schedule', models.OneToOneField(help_text='Please complete here below the schedule of your last year of high school, indicating for each domain the number of hours of education followed per week (h/w). ', null=True, on_delete=django.db.models.deletion.CASCADE, to='osis_profile.Schedule')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
