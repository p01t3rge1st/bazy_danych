from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css):
    return field.as_widget(attrs={"class": css})

@register.filter
def get_reservation(reservations, student_and_class):
    student, c = student_and_class
    return reservations.get(class_field=c, student_index=student)

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)