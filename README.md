# kreta-python-api

WIP

Megvalósított api a kréta rendszerhez, Pythonban.

Példa:

```python
from kreta_api import *

student = Student("klik00000000","7000000000","xxxxxxxxxx")
student.refresh()

print(student)
print(student.name)
```

TODO:
 - docs
 - event
 - órarend
