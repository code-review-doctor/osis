# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-22 13:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0011_offeryear_offer_parent'),
    ]

    operations = [
        migrations.RunSQL(
        """CREATE OR REPLACE FUNCTION update_changed_column()
        RETURNS TRIGGER AS $$
        BEGIN
            IF (TG_OP = 'UPDATE') THEN
                -- Si on ne fournit pas de nouvelle date
                IF (NEW.changed IS NULL) OR (NEW.changed = OLD.changed) THEN
                    NEW.changed := now();
                    RETURN NEW;
                END IF;
                -- Condition ci-dessous pour si jamais le record a été modifié entre
                -- le début et la fin de (ou pendant) l'exécution du script de synchronisation
                IF (OLD.changed > NEW.changed) THEN
                    NEW.changed := OLD.changed;
                END IF;
            ELSE
                IF (NEW.changed IS NULL) THEN
                    NEW.changed := now();
                    RETURN NEW;
                END IF;
            END IF;
            RETURN NEW;
        END;
        $$ language 'plpgsql';"""
        ),


    ]
