# Generated by Django 2.2.13 on 2021-02-05 10:34

from django.db import migrations
from django.db.models import Count

from base.models.group_element_year import GroupElementYear

YEAR_FROM = 2019


def fix_order(apps, schema_editor):
    problematic_element_parents = find_problematic_parents()

    print("Problematic parents: {}".format(len(problematic_element_parents)))

    for parent_element_id in problematic_element_parents:
        reorder_children(parent_element_id)
        print(str(parent_element_id))


def find_problematic_parents():
    return GroupElementYear.objects.filter(
        parent_element__group_year__academic_year__year__gte=YEAR_FROM
    ).values(
        "parent_element",
        "order",
    ).annotate(
        num_children_order=Count("order")
    ).filter(
        num_children_order__gt=1
    ).values_list("parent_element", flat=True)


def reorder_children(parent_element_id: int):
    links = GroupElementYear.objects.filter(parent_element__id=parent_element_id).order_by("order")
    for order, link in enumerate(links, start=1):
        link.order = order
        link.save()


class Migration(migrations.Migration):
    dependencies = [
        ('base', '0565_auto_20210203_1310'),
    ]

    operations = [
        migrations.RunPython(fix_order, elidable=True),
    ]
