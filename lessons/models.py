from django.db import models


class PhysThemes(models.Model):
    id = models.AutoField(primary_key=True)
    theme = models.CharField(unique=True, max_length=100)

    def __str__(self):
        return self.theme

    class Meta:
        managed = False


class PhysTasks(models.Model):
    answer_choices = {
        'int': 'целое',
        'float': 'с плавающей точкой',
        'str': 'текстовое'
    }
    # Define default values for use elsewhere wia import
    default_values = {"theme": "Undefined", "cmplx": 1, "answer_type": "str", "trust": False}

    task_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField(help_text='Введите описание задачи...')
    theme = models.ForeignKey(to="PhysThemes", on_delete=models.CASCADE, to_field="theme",
                              default=default_values["theme"])
    complexity = models.IntegerField(blank=True, default=default_values["cmplx"])
    image = models.TextField(blank=True, null=True)
    answer = models.CharField(max_length=200)
    answer_type = models.CharField(max_length=10, choices=answer_choices, default=default_values["answer_type"])
    author = models.CharField(blank=True, null=True, max_length=200)
    trust = models.BooleanField(default=default_values["trust"])
    source = models.TextField(default="db")

    class Meta:
        ordering = ["-trust", "theme", "name"]

    def check_answer(self, user_answer: str) -> bool:
        return user_answer.replace(',', '.') == str(self.answer).replace(',', '.')

    def descr_shorter(self) -> str:
        if len(str(self.description)) > 100:
            res = self.description[:100] + "..."
        else:
            res = self.description
        return res
    descr_shorter.short_description = 'Краткое описание'

    def display_theme(self):
        return self.theme.theme
    display_theme.short_description = 'Тема'


