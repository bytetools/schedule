# from: https://codeyz.com/development/python/how-to-check-a-users-membership-in-a-group-in-a-template/
from django import template
 
register = template.Library() 
  
@register.filter(name='has_group') 
def has_group(user, group_name):
  return user.groups.filter(name=group_name).exists() 
