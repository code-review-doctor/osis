# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2019-05-21 15:41
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0459_auto_20190617_1021'),
    ]

    operations = [
        migrations.RunSQL(
            """               
                update base_learningcontaineryear
                
                set 
                    requirement_entity_id = ecy_requirement.entity_id
                from 
                    base_entitycontaineryear as ecy_requirement
                where (
                    ecy_requirement.learning_container_year_id = base_learningcontaineryear.id 
                    and ecy_requirement.type = 'REQUIREMENT_ENTITY'
                )
            """,
            elidable=True
        ),

        migrations.RunSQL(
            """               
                update base_learningcontaineryear
                
                set 
                    allocation_entity_id = ecy_allocation.entity_id
                from 
                    base_entitycontaineryear as ecy_allocation
                where (
                    ecy_allocation.learning_container_year_id = base_learningcontaineryear.id 
                    and ecy_allocation.type = 'ALLOCATION_ENTITY'
                )
            """,
            elidable=True
        ),

        migrations.RunSQL(
            """               
                update base_learningcontaineryear
                
                set 
                    additional_entity_1_id = ecy_additionnal_1.entity_id
                from 
                    base_entitycontaineryear as ecy_additionnal_1
                where (
                    ecy_additionnal_1.learning_container_year_id = base_learningcontaineryear.id 
                    and ecy_additionnal_1.type = 'ADDITIONAL_REQUIREMENT_ENTITY_1'
                )
            """,
            elidable=True
        ),

        migrations.RunSQL(
            """               
                update base_learningcontaineryear
                
                set 
                    additional_entity_2_id = ecy_additionnal_2.entity_id
                from 
                    base_entitycontaineryear as ecy_additionnal_2
                where (
                    ecy_additionnal_2.learning_container_year_id = base_learningcontaineryear.id 
                    and ecy_additionnal_2.type = 'ADDITIONAL_REQUIREMENT_ENTITY_2'
                )
            """,
            elidable=True
        ),

    ]
