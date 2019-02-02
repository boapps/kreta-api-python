# kreta-api-python

Megvalósított api a kréta rendszerhez, Pythonban.

Példa:

```python
from kreta_api import *

student = Student("klik00000000","7000000000","xxxxxxxxxx") # a tanuló adatait inicializáljuk
student.refresh_bearer() # azonosító kód lekérése
student.refresh_student() # tanuló adatainak lekérése

print(student) # tanulóhoz tartozó adatok kiírása
print(student.name) # tanuló nevének kiírása
print(student.evaluation_list[0].subject) # ebből a tantárgyból kapta a legújabb jegyet
```

TODO:
 - docs
 - error handling
