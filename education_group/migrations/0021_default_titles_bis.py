from django.db import migrations
from django.utils import timezone

from base.models.enums.education_group_types import GroupType
from education_group.models.group_year import GroupYear


def add_default_titles_to_common_core_and_complementary_module(apps, schema_editor):
    groups = GroupYear.objects.filter(
        academic_year__year__gt=2019,
        education_group_type__name__in=[
            GroupType.COMPLEMENTARY_MODULE.name,
            GroupType.COMMON_CORE.name
        ]
    )
    complementary_modules = groups.filter(education_group_type__name=GroupType.COMPLEMENTARY_MODULE.name)
    for cm in complementary_modules:
        cm.title_en = 'Additional lessons (complementary module) to the master course'
        cm.changed = timezone.now()

    common_cores = groups.filter(education_group_type__name=GroupType.COMMON_CORE.name)
    for cc in common_cores:
        cc.title_en = 'Content :'
        cc.changed = timezone.now()
    GroupYear.objects.bulk_update(
        list(common_cores) + list(complementary_modules),
        ['title_en', 'changed'],
        batch_size=1000
    )


class Migration(migrations.Migration):
    dependencies = [
        ('education_group', '0020_default_titles_and_credits'),
    ]

    operations = [
        migrations.RunPython(add_default_titles_to_common_core_and_complementary_module),
    ]
