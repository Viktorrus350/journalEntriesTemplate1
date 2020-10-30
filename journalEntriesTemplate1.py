""" "Журнал записей" Шаблон """
# файл journalEntriesTemplate1.pyw (расширение .pyw необходимо для подавления окна DOS)
# в модуле journalEntriesTemplate1 заменить Поле1 внутри кода на название соответствующее теме
# в модуле journalEntriesTemplate1 заменить Поле2 внутри кода на название соответствующее теме
# в модуле journalEntriesTemplate1 заменить Поле3 внутри кода на название соответствующее теме
# в модуле journalEntriesTemplate1 заменить Поле4 внутри кода на название соответствующее теме
# в модуле journalEntriesTemplate1 заменить Поле5 внутри кода на название соответствующее теме
# в модуле journalEntriesTemplate1 заменить Поле6 внутри кода на название соответствующее теме
# в строке 70 заменить название экземпляра программы (имя базы данных), которое находится в атрибуте nameBook

from tkinter import *               # импорт объектов для графического интерфейса
from tkinter.messagebox import *    # импорт объектов для диалоговых окон
import shelve                       # импорт модуля для работы с базой данных 
import journal as mJ                # импорт модуля с формой журнала
import record as mR                 # импорт модуля с формой для одной выбранной записи

class Progr:
    # создание класса моделирующего данные программы и ее дествия
    def __init__(self, dbName, j1=None):
        self.j1 = mJ.Journal(dbName)    # создание экземпляра j1 класса Journal
        self.dbName = dbName
        self.fieldnamesRecTab = ('keyRec', 'char', 'field1', 'field2', 'field3', 'commen', 'delR')  # кортеж имен полей записи в таблице
        self.fieldnamesRecTabCyr = ('№№', 'Буква', 'Поле1', 'Поле2', 'Поле3', 'Комментарий', 'тип')  # кортеж имен полей на руском
        self.fieldnamesRec = ('char', 'field1', 'field2', 'field3', 'field4', 'field5', 'field6', 'commen')   # кортеж имен полей для формы с одной записью
        self.fieldnamesRecCyr = {'char':'Буква', 'field1':'Поле1', 'field2':'Поле2', 'field3':'Поле3', 'field4':'Поле4', 'field5':'Поле5', 'field6':'Поле6', 'commen':'Комментарий'} # словарь для перевода полей в кирилицу
        self.fieldnamesRecFull = ('keyRec', 'char', 'field1', 'field2', 'field3', 'field4', 'field5', 'field6',
                            'commen', 'delR')     # кортеж всех полей в записи

        self.activCh = 'А'                                      # буква, активная на текущий момент                                        # текущая запись
        self.typeRec = ''                                       # тип выводимых на экран записей, '' - открытые, "с" - скрытые
        self.dicRem = {}                                        # словарь оставшихся не выведенными записей

    def load_DB(self):
        # загрузка записей из базы данных db1, при необходимости добавить дополнительные БД
        db1 = shelve.open(self.j1.dbName)     # открытие базы данных (имя берется
                                              # из атрибута dbName экземпляра класса Data)
        self.j1.dic_recs = dict(db1.items())  # загрузка записей из базы данных в атрибут dic_recs
                                              # экземпляра класса Data (в словарь экземпляра класса)
        db1.close()                           # закрытие базы данных

    def save_DB(self):
        # сохранение записей в базе данных db1, при необходимости добавить дополнительные БД
        db1 = shelve.open(self.j1.dbName)     # открытие базы данных
        for (key, record) in self.j1.dic_recs.items():  # запись содержимого из словаря dic_recs
            db1[key] = record                       # экземпляра j1 класса Data в базу данных
        db1.close()                           # закрытие базы данных

    def open_Journal(self):
        mJ.p1 = p1            # передача в модуль journal экземпляра p1 класса программы Progr
        mJ.fieldnamesRecTab = p1.fieldnamesRecTab       # кортеж имен полей записи в таблице
        mJ.fieldnamesRecTabCyr = p1.fieldnamesRecTabCyr # кортеж имен полей на руском
        mJ.fieldnamesRec = p1.fieldnamesRec             # кортеж имен полей для формы с одной записью
        mJ.fieldnamesRecCyr = p1.fieldnamesRecCyr       # словарь для перевода полей в кирилицу
        mJ.fieldnamesRecFull = p1.fieldnamesRecFull     # кортеж всех полей в записи
        mJ.window = mJ.makeWidgets()    # создание формы
        mJ.fetchChr('А')                # вывод в качестве стартовой страницу с буквой "А"
        mJ.window.mainloop()            # передача управления форме

    def open_Record(self):
        mR.p1 = p1             # передача в модуль record экземпляра p1 класса программы Progr
        mR.fieldnamesRec = p1.fieldnamesRec   # имена полей у записи (передается в модуль record)
        mR.fieldnamesRecCyr = p1.fieldnamesRecCyr   # словарь для перевода полей в кирилицу (передается в модуль record)
        mR.record = p1.j1.dic_recs[p1.j1.currentKey]    # экземпляр записи для вывода в форме в модуле
        mR.winRec = mR.makeWidgets()       # создание в модуле формы с одной записью
        mR.fetchRecord(mR.record)         # вывод в форме в модуле указанной записи
        mR.winRec.mainloop()                  # передача управления форме в модуле

if __name__ == '__main__':
    p1 = Progr("Записи")     # создание экземпляра класса Progr
    p1.load_DB()             # загрузка записей из внешней БД в словарь dic_recs

    p1.open_Journal()
