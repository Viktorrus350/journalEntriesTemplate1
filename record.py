# файл record.py - модуль, импортируемый сценарием journalEntriesTemplate1.py (или journalEntriesTemplate1.pyw)

from tkinter import *                              # импорт объектов для графического интерфейса
from tkinter import Toplevel                       # класс дополнительных окон
from tkinter.messagebox import showerror           # всплывающее окно диалога сообщающее об ошибке
import shelve                                      # импорт модуля для работы с базой данных 

p1 = None                   # экземпляр класса Progr (передается из journalEntriesTemplate1)
winRec = None

fieldnamesRec = None #p1.fieldnamesRec       # имена полей у записи (передается из journalEntriesTemplate1)
fieldnamesRecCyr = None #p1.fieldnamesRecCyr    # словарь для перевода полей в кирилицу (передается из journalEntriesTemplate1)
record = None              # экземпляр записи для вывода в форме (передается через функцию)

entriesRec = {}          # словарь, для занесения в него объектов Entry ячеек формы ввода записи

def onDeleteRequest():
#    print('Got wm delete') # щелчок на кнопке X в окне: можно отменить или перехватить
    saveRec()        # сохранение текущей записи
    winRec.destroy()  # закрытие окна текущей записи (возбудит событие <Destroy>)
    p1.open_Journal()    # открытие окна журнала

def makeWidgets():       # создание графической формы для вывода одной записи
    global entriesRec
    winRec = Tk()                 # создание дополнительного окна для второй формы
    winRec.title('Книга')               # заголовок окна
    winRec.geometry('500x250+350+150')  # размеры окна
    winRec.protocol('WM_DELETE_WINDOW', onDeleteRequest) # на кнопке X окна (перехватывает нажатие кнопки Х)
    form = Frame(winRec)             # создание фрейма
    form.pack(side=TOP, expand=YES, fill=BOTH)   # упаковка фрейма
    entriesRec = {}                              # словарь содержащий объекты Entry
    for (ix, label) in enumerate(fieldnamesRec): # формирование названия полей и полей ввода Entry
        lab = Label(form, text= fieldnamesRecCyr[label]) # название поля (в кирилице)
        ent = Entry(form, width=200)             # поле ввода
        lab.grid(row=ix, column=0)                  # размещение по сетке
        ent.grid(row=ix, column=1)
        entriesRec[label] = ent                  # запись в словарь
    Button(winRec, text="Сохранить", command=saveRec).pack(side=LEFT)  # кнопка Сохранить
    Button(winRec, text="Выход", command=fin).pack(side=RIGHT)  # закрывает одно окно
    return winRec          # возвращает второе окно со сформированной второй формой

#def recBook(recordsBook):
    # функция для передачи в модуль экземпляра t1 книги класса RecordsBook
    global t1
    t1 = recordsBook       # содержит экземпляр t1 класса RecordsBook
#def curRec(curRecord):
    # функция для передачи в модуль экземпляра текущей записи класса Record
    global record
    _record = curRecord   # экземпляр записи переданный в модуль

def fetchRecord(record):
    # вывод в форме указанной записи
    for field in fieldnamesRec:
        entriesRec[field].insert(0, getattr(record, field)) # для каждого поля заполняется виджет Entry
def saveRec():
    # сохранение записи (занесение в экземпляр записи содержимого формы и сохранение экземпляра) 
    global record            # экземпляр записи выведенный в форме
    key = record.keyRec      # ключ записи
    for field in fieldnamesRec:   # занесение в экземпляр записи содержимого формы
        setattr(record, field, entriesRec[field].get())
        #print(record)                    # печать атрибутов для отладки
    p1.j1.dic_recs[key] = record   # сохранение экземпляра записи в словаре книги
    p1.save_DB()  # словарь t1.dicRec сохраняется во внешней базе данных "Книги"

def fin():            # сохранение перед закрытием окна 
    saveRec()        # сохранение текущей записи
    winRec.destroy()  # закрытие окна текущей записи (возбудит событие <Destroy>)
    p1.open_Journal()    # открытие окна журнала
