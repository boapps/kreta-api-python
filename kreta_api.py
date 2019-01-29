#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import requests
import json

class KretaApi:
    """ api az e-Krétás lekérdezésekhez
    """

    def __init__(self):
        """ api inicializálása

        :param school_code: iskola kódja
        """

    def get_schools_json(self):
        """ lekéri a Krétás iskolákat
        """
        return requests.get("https://kretaglobalmobileapi.ekreta.hu/api/v1/Institute",
                            headers={"apiKey":"7856d350-1fda-45f5-822d-e1a2f3f1acf0"}).text

    def get_schools(self, json_string):
        schools_json = json.loads(json_string)
        schools = list()
        for sch in schools_json:
            school = Institute(sch["InstituteId"], sch["InstituteCode"], sch["Name"], sch["Url"],
                               sch["City"], sch["AdvertisingUrl"],
                               sch["FeatureToggleSet"]["JustificationFeatureEnabled"])
            schools.append(school)
        return schools

    def get_bearer_json(self, institute_code, username, password):
        """ lekéri az azonosításra használható bearer kód json-át
        """
        return requests.post("https://" + institute_code + ".e-kreta.hu/idp/api/v1/Token",
                             data="institute_code=" + institute_code + "&userName=" + username +
                             "&password=" + password + "&grant_type=password&client_id=" +
                             "919e0c1c-76a2-4646-a2fb-7085bbbf3c56").text

    def get_bearer(self, json_string):
        """ a json_string-ből elkészíti a Bearer objektumot
        :param json_string: a json, ami tartalmazza a szükséges infót
        """
        bearer_json = json.loads(json_string)

        access_token = bearer_json["access_token"]
        token_type = bearer_json["token_type"]
        expires_in = bearer_json["expires_in"]
        refresh_token = bearer_json["refresh_token"]

        return Bearer(access_token, token_type, expires_in, refresh_token)

    def get_student(self, institute_code, bearer):
        """ lekéri a tanuló adatait
        """
        return requests.get("https://" + institute_code + ".e-kreta.hu/mapi/api/v1/Student",
                            headers={"Authorization": "Bearer " + bearer}).text

class Bearer:
    """ Bearer
    """

    def __init__(self, access_token, token_type, expires_in, refresh_token):
        """ Bearer kód inicializálása
        :param access_token: maga a token, amivel a hitelesítést végezzük
        :param token_type: a token típusa
        :param expires_in: a token "minőségét megőrzi" ennyi ideig, utánna nem használható
        :param refresh_token: ezzel később új kódot kérhetünk le anélkül,
        hogy újra meg kellene adnunk a felhasználónevet és jelszót
        """
        self.access_token = access_token
        self.token_type = token_type
        self.expires_in = expires_in
        self.refresh_token = refresh_token

class Institute:
    """ Iskola
    """

    def __init__(self, institute_id, institute_code, name, url, city, advertising_url,
                 justification_feature_enabled):
        """ Iskola objektum inicializálása

        :param institute_id: iskola azanosítója
        :param institute_code: iskola kódja
        :param name: iskola neve
        :param url: iskola url-je
        :param city: a város, ahol az iskola található
        :param advertising_url: nem tudom mi
        :param justification_feature_enabled: nem tudom mi
        """
        self.institute_id = institute_id
        self.institute_code = institute_code
        self.name = name
        self.url = url
        self.city = city
        self.advertising_url = advertising_url
        self.justification_feature_enabled = justification_feature_enabled

    def __str__(self):
        return ("{" +
                "\n   id: " +  str(self.institute_id) +
                "\n   code: " +  str(self.institute_code) +
                "\n   name: " +  str(self.name) +
                "\n   URL: " +  str(self.url) +
                "\n   city: " +  str(self.city) +
                "\n   advertising URL: " +  str(self.advertising_url) +
                "\n   justification feature enabled: " +  str(self.justification_feature_enabled) +
                "\n}")

    def __repr__(self):
        return str(self)

class Student:
    """ Információt tárol a diákról (jegyek, név, születési dátum stb.)
    """
    def __init__(self, institute_code, username, password):
        """ diák inicializálása
        :param institute_code: iskola kódja
        :param username: a diák felhasználóneve
        :param password: a diák jelszava
        """
        self.institute_code = institute_code
        self.username = username
        self.password = password

        self.student_string = ""

        self.student_id = None
        self.school_year_id = None
        self.name = None
        self.name_of_birth = None
        self.place_of_birth = None
        self.mothers_name = None
        self.address_list = list()
        self.date_of_birth_utc = None
        self.institute_name = None
        self.evaluation_list = list()
        self.average_list = list()
        self.absence_list = list()
        self.note_list = list()
        self.form_teacher = None
        self.tutelary_list = list()

    def __str__(self):
        return self.student_string

    def __repr__(self):
        return str(self)

    def refresh(self):
        """ Betölti a diák adatai a Student objektumba
        """
        bearer_json = KretaApi().get_bearer_json(self.institute_code, self.username, self.password)
        bearer = KretaApi().get_bearer(bearer_json)

        self.student_string = KretaApi().get_student(self.institute_code, bearer.access_token)
        print(self.student_string[0:5000])

        student_json = json.loads(self.student_string)
        self.name = student_json["Name"]
        self.student_id = student_json["StudentId"]
        self.school_year_id = student_json["SchoolYearId"]
        self.name_of_birth = student_json["NameOfBirth"]
        self.place_of_birth = student_json["PlaceOfBirth"]
        self.mothers_name = student_json["MothersName"]
        for address in student_json["AddressDataList"]:
            self.address_list.append(address)
        self.date_of_birth_utc = student_json["DateOfBirthUtc"]
        self.institute_name = student_json["InstituteName"]
        for evaluation in student_json["Evaluations"]:
            e_item = Evaluation(evaluation["EvaluationId"], evaluation["Form"],
                                evaluation["FormName"], evaluation["Type"], evaluation["TypeName"],
                                evaluation["Subject"], evaluation["SubjectCategory"],
                                evaluation["SubjectCategoryName"], evaluation["Theme"],
                                evaluation["Mode"], evaluation["Weight"], evaluation["Value"],
                                evaluation["NumberValue"], evaluation["SeenByTutelaryUTC"],
                                evaluation["Teacher"], evaluation["Date"],
                                evaluation["CreatingTime"])
            self.evaluation_list.append(e_item)
        for avr in student_json["SubjectAverages"]:
            average = Average(avr["Subject"], avr["SubjectCategory"], avr["SubjectCategoryName"],
                              avr["Value"], avr["ClassValue"], avr["Difference"])
            self.average_list.append(average)
        for absnc in student_json["Absences"]:
            absence = Absence(absnc["AbsenceId"], absnc["Type"], absnc["TypeName"], absnc["Mode"],
                              absnc["ModeName"], absnc["Subject"], absnc["SubjectCategory"],
                              absnc["SubjectCategoryName"], absnc["DelayTimeMinutes"],
                              absnc["Teacher"], absnc["LessonStartTime"], absnc["NumberOfLessons"],
                              absnc["CreatingTime"], absnc["JustificationState"],
                              absnc["JustificationStateName"], absnc["JustificationType"],
                              absnc["JustificationTypeName"], absnc["SeenByTutelaryUTC"])
            self.absence_list.append(absence)
        for note in student_json["Notes"]:
            n_item = Note(note["NoteId"], note["Type"], note["Title"], note["Content"],
                          note["SeenByTutelaryUTC"], note["Teacher"], note["Date"],
                          note["CreatingTime"])
            self.note_list.append(n_item)
        self.form_teacher = FormTeacher(student_json["FormTeacher"]["TeacherId"],
                                        student_json["FormTeacher"]["Name"],
                                        student_json["FormTeacher"]["Email"],
                                        student_json["FormTeacher"]["PhoneNumber"])
        for tut in student_json["Tutelaries"]:
            tutelary = Tutelary(tut["TutelaryId"], tut["Name"], tut["Email"], tut["PhoneNumber"])
            self.tutelary_list.append(tutelary)

class Tutelary:
    """ Szülő
    """
    def __init__(self, tutelary_id, name, email, phone_number):
        self.tutelary_id = tutelary_id
        self.name = name
        self.email = email
        self.phone_number = phone_number

    def __str__(self):
        return ("{" +
                "\n   id: " + str(self.tutelary_id) +
                "\n   name: " + str(self.name) +
                "\n   e-mail: " + str(self.email) +
                "\n   phone number: " + str(self.phone_number) +
                "\n}")

    def __repr__(self):
        return str(self)

class FormTeacher:
    """ Osztályfőnök
    """
    def __init__(self, teacher_id, name, email, phone_number):
        self.teacher_id = teacher_id
        self.name = name
        self.email = email
        self.phone_number = phone_number

    def __str__(self):
        return ("{" +
                "\n   id: " + str(self.teacher_id) +
                "\n   name: " + str(self.name) +
                "\n   e-mail: " + str(self.email) +
                "\n   phone number: " + str(self.phone_number) +
                "\n}")

    def __repr__(self):
        return str(self)

class Note:
    """ Feljegyzés
    """
    def __init__(self, note_id, e_type, title, content, seen_by_tutelary_utc, teacher, date, creating_time):
        self.note_id = note_id
        self.e_type = e_type
        self.title = title
        self.content = content
        self.seen_by_tutelary_utc = seen_by_tutelary_utc
        self.teacher = teacher
        self.date = date
        self.creating_time = creating_time

    def __str__(self):
        return ("{" +
                "\n   id: " +  str(self.note_id) +
                "\n   type: " +  str(self.e_type) +
                "\n   title: " +  str(self.title) +
                "\n   content: " +  str(self.content) +
                "\n   seen by tutelary utc: " +  str(self.seen_by_tutelary_utc) +
                "\n   teacher: " +  str(self.teacher) +
                "\n   date: " +  str(self.date) +
                #"\n   creating time: " + str(self.creating_time) +
                "\n}")

    def __repr__(self):
        return str(self)

class Absence:
    """ Hiányzás
    """

    def __init__(self, absence_id, e_type, type_name, mode, mode_name, subject, subject_category, subject_category_name, delay_time_minutes, teacher, lesson_start_time, number_of_lessons, creating_time, justification_state, justification_state_name, justification_type, justification_type_name, seen_by_tutelary_utc):
        self.absence_id = absence_id
        self.e_type = e_type
        self.type_name = type_name
        self.mode = mode
        self.mode_name = mode_name
        self.subject = subject
        self.subject_category = subject_category
        self.subject_category_name = subject_category_name
        self.delay_time_minutes = delay_time_minutes
        self.teacher = teacher
        self.lesson_start_time = lesson_start_time
        self.number_of_lessons = number_of_lessons
        self.creating_time = creating_time
        self.justification_state = justification_state
        self.justification_state_name = justification_state_name
        self.justification_type = justification_type
        self.justification_type_name = justification_type_name
        self.seen_by_tutelary_utc = seen_by_tutelary_utc

    def __str__(self):
        return ("{" +
                "\n   id: " +  str(self.absence_id) +
                "\n   type: " +  str(self.e_type) +
                "\n   type name: " +  str(self.type_name) +
                "\n   subject: " +  str(self.subject) +
                "\n   subject category: " +  str(self.subject_category) +
                "\n   subject category name: " +  str(self.subject_category_name) +
                "\n   mode: " +  str(self.mode) +
                "\n   mode name: " +  str(self.mode_name) +
                "\n   delay time minutes: " +  str(self.delay_time_minutes) +
                "\n   lesson start time: " +  str(self.lesson_start_time) +
                "\n   number of lessons: " +  str(self.number_of_lessons) +
                "\n   seen by tutelary utc: " +  str(self.seen_by_tutelary_utc) +
                "\n   teacher: " +  str(self.teacher) +
                "\n   justification state: " +  str(self.justification_state) +
                "\n   justification state_name: " +  str(self.justification_state_name) +
                "\n   justification type: " +  str(self.justification_type) +
                "\n   justification type name: " +  str(self.justification_type_name) +
                #"\n   creating time: " + str(self.creating_time) +
                "\n}")

    def __repr__(self):
        return str(self)

class Evaluation:
    """ Jegy
    """

    def __init__(self, evaluation_id, form, form_name, e_type, type_name, subject, subject_category, subject_category_name, theme, mode, weight, value, number_value, seen_by_tutelary_utc, teacher, date, creating_time):
        self.evaluation_id = evaluation_id
        self.form = form
        self.form_name = form_name
        self.e_type = e_type
        self.type_name = type_name
        self.subject = subject
        self.subject_category = subject_category
        self.subject_category_name = subject_category_name
        self.theme = theme
        self.mode = mode
        self.weight = weight
        self.value = value
        self.number_value = number_value
        self.seen_by_tutelary_utc = seen_by_tutelary_utc
        self.teacher = teacher
        self.date = date
        self.creating_time = creating_time

    def __str__(self):
        return ("{" +
                "\n   id: " +  str(self.evaluation_id) +
                "\n   form: " +  str(self.form) +
                "\n   form name: " +  str(self.form_name) +
                "\n   type: " +  str(self.e_type) +
                "\n   type name: " +  str(self.type_name) +
                "\n   subject: " +  str(self.subject) +
                "\n   subject category: " +  str(self.subject_category) +
                "\n   subject category name: " +  str(self.subject_category_name) +
                "\n   theme: " +  str(self.theme) +
                "\n   mode: " +  str(self.mode) +
                "\n   weight: " +  str(self.weight) +
                "\n   value: " +  str(self.value) +
                "\n   number value: " +  str(self.number_value) +
                "\n   seen by tutelary utc: " +  str(self.seen_by_tutelary_utc) +
                "\n   teacher: " +  str(self.teacher) +
                "\n   date: " +  str(self.date) +
                #"\n   creating time: " + str(self.creating_time) +
                "\n}")

    def __repr__(self):
        return str(self)

class Average:
    """ Átlag
    """
    def __init__(self, subject, subject_category, subject_category_name, value, class_value, difference):
        self.subject = subject
        self.subject_category = subject_category
        self.subject_category_name = subject_category_name
        self.value = value
        self.class_value = class_value
        self.difference = difference

    def __str__(self):
        return ("{" +
                "\n   subject: " +  str(self.subject) +
                "\n   subject category: " +  str(self.subject_category) +
                "\n   subject category name: " +  str(self.subject_category_name) +
                "\n   value: " +  str(self.value) +
                "\n   class value: " +  str(self.class_value) +
                "\n   difference: " +  str(self.difference) +
                "\n}")

    def __repr__(self):
        return str(self)

class Lesson:
    """ Óra
    """
    def __init__(self, lesson_id, count, date, start_time, end_time, subject, subject_category_name, classroom, class_group, teacher, deputy_teacher, state, state_name, presence_type, presence_type_name, theme, homework, calendar_ora_type):
        self.lesson_id = lesson_id
        self.count = count
        self.date = date
        self.start_time = start_time
        self.end_time = end_time
        self.subject = subject
        self.subject_category_name = subject_category_name
        self.classroom = classroom
        self.class_group = class_group
        self.teacher = teacher
        self.deputy_teacher = deputy_teacher
        self.state = state
        self.state_name = state_name
        self.presence_type = presence_type
        self.presence_type_name = presence_type_name
        self.theme = theme
        self.homework = homework
        self.calendar_ora_type = calendar_ora_type

    def __str__(self):
        return ("{" +
                "\n   id: " +  str(self.lesson_id) +
                "\n   count: " +  str(self.count) +
                "\n   date: " +  str(self.date) +
                "\n   start time: " +  str(self.start_time) +
                "\n   end_time: " +  str(self.end_time) +
                "\n   subject: " +  str(self.subject) +
                "\n   subject category name: " +  str(self.subject_category_name) +
                "\n   classroom: " +  str(self.classroom) +
                "\n   class group: " +  str(self.class_group) +
                "\n   teacher: " +  str(self.teacher) +
                "\n   deputy teacher: " +  str(self.deputy_teacher) +
                "\n   state: " +  str(self.state) +
                "\n   state name: " +  str(self.state_name) +
                "\n   presence type: " +  str(self.presence_type) +
                "\n   presence type name: " +  str(self.presence_type_name) +
                "\n   theme: " +  str(self.theme) +
                "\n   homework: " +  str(self.homework) +
                "\n   calendar ora type: " +  str(self.calendar_ora_type) +
                "\n}")

    def __repr__(self):
        return str(self)
