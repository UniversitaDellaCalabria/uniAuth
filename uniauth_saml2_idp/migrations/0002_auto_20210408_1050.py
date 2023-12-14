# Generated by Django 3.1.2 on 2021-04-08 10:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("uniauth_saml2_idp", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="serviceprovider",
            name="attribute_processor",
            field=models.CharField(
                blank=True,
                default="uniauth_saml2_idp.processors.ldap.LdapUnicalMultiAcademiaProcessor",
                help_text='"package.file.classname", example: "idp.processors.LdapAcademiaProcessor"',
                max_length=256,
            ),
        ),
    ]
