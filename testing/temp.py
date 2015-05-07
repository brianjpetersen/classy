# standard libraries
pass
# third party libraries
pass
# first party libraries
import classy


class Root(classy.Controller):
	
	pass
	

class Child(Root):
	
	configuration = {'test': 2}


print(classy.Controller.configuration)
print(Root.configuration)
c = {'test': 1}
Root.configure(c)
print(classy.Controller.configuration)
print(Root.configuration)
print(Child.configuration)
print(c)

Root.allowed_methods.remove('delete')

print(Root.allowed_methods)
print(classy.Controller.allowed_methods)
print(Child.allowed_methods)