from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("photos", "0003_image_embeddings_face_count"),
    ]

    operations = [
        migrations.AddField(
            model_name="room",
            name="description",
            field=models.TextField(blank=True, null=True),
        ),
    ]
