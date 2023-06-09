from django import template

register = template.Library()


@register.filter()
def censor(word):
    def multiple_replace(texts, replace_value):
        for i, j in replace_value.items():
            texts = texts.lower().replace(i, j)
        return texts

    # создаем словарь со значениями и строку, которую будет изменять
    replace_values = {'модели': 'м*****',
                      'джигурда': 'д*******',
                      'однако': 'о*****',
                      'директор': 'д*******',
                      'повтор': 'п*****'
                      }

    # изменяем и печатаем строку

    word = multiple_replace(word, replace_values)
    return word.capitalize()
