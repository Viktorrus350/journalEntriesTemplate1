# файл journal.py - модуль, импортируемый сценарием journalEntriesTemplate1.py (или journalEntriesTemplate1.pyw)


from tkinter import *                  # импорт объектов для графического интерфейса
from tkinter.messagebox import *       # импорт объектов для диалоговых окон
import shelve                          # импорт модуля для работы с базой данных 

p1 = None                              # экземпляр класса Progr (присваивается из модуля journalEntriesTemplate1)
window = None                          # окно для журнала записей (присваивается из модуля journalEntriesTemplate1)

fieldnamesRecTab = None    # кортеж имен полей записи в таблице (передается из journalEntriesTemplate1)
fieldnamesRecTabCyr = None # кортеж имен полей на руском (передается из journalEntriesTemplate1)
fieldnamesRec = None       # кортеж имен полей для формы с одной записью (передается из journalEntriesTemplate1)
fieldnamesRecCyr = None    # словарь для перевода полей в кирилицу (передается из journalEntriesTemplate1)
fieldnamesRecFull = None   # кортеж всех полей в записи (передается из journalEntriesTemplate1)

activCh = 'А'                                      # буква, активная на текущий момент                                        # текущая запись
typeRec = ''                                       # тип выводимых на экран записей, '' - открытые, "с" - скрытые
dicRem = {}                                        # словарь оставшихся не выведенными записей

class Journal:
    def __init__(self, dbName, currentKey=None, dic_recs={}):
        self.dbName = dbName              # название журнала
        self.currentKey = currentKey      # номер текущей записи в журнале
        self.dic_recs = dic_recs      # словарь записей, который загружается из БД
                                      # и с которым программма динамически работеет,
                                      # чтобы затем измененные данные сохранить в БД

class Record:
    # класс Запись
    def __init__(self, keyRec, char, field1, field2, field3, 
                 field4, field5, field6, commen, delR=''):
        # инициализация атрибутов экземпляров класса
        self.keyRec = keyRec                   # ключ записи
        self.char = char                       # буква, на странице которой находится запись
        self.field1 = field1                   # метка, к чему относится запись
        self.field2 = field2                   # Поле2
        self.field3 = field3                   # Поле3
        self.field4 = field4                   # Поле4
        self.field5 = field5                   # Поле5
        self.field6 = field6                   # Поле6
        self.commen = commen                   # комментарий
        self.delR = delR                       # служебное поле для пометки записи:
                                               # ''- видимая, 'с' - скрытая, 'у' - удаляемая

def onDeleteRequest():
#    print('Got wm delete') # щелчок на кнопке X в окне: можно отменить или перехватить
    saveRec()
    window.destroy()         # возбудит событие <Destroy>

def makeWidgets():
    # создание графической формы
    global entriesRec, entRec, lab1, alph          # перечень глобальных переменных, которые будут использоваться и за пределами функции
    entRec = {}                                    # словарь, в который будут заносится объекты ввода entFind (поиск) и entKeyRec (ключ)
    window = Tk()                                  # создание главного окна
    window.title('Книги')                       # заголовок окна
    window.geometry('1260x600+0+0')                # размеры окна
#    window.bind('FocusIn', updatePage)             # при получении окном фокуса, обновление таблицы записей
#    window.bind('<Destroy>', doRootDestroy)              # для корневого и дочерних 
    window.protocol('WM_DELETE_WINDOW', onDeleteRequest) # на кнопке X окна (перехватывает нажатие кнопки Х)
    form1 = Frame(window)                          # создание внутри окна window контейнера form1
    form1.pack()
    lab1 = Label(form1, text=activCh, fg="#eee", bg="#333", width=5)  # метка, показывающая
    lab1.pack(side=LEFT)                                              # активную букву
    Label(form1, text='  ', width=30).pack(side=LEFT)                 # вспомагательная пустая метка для улучшения расположения
    alph = ["А", "Б", "В", "Г", "Д", "Е", "Ж", "З", "И", "К", "Л", "М", "Н", "О", "П", "Р", "С", "Т", 
            "У", "Ф", "Х", "Ц", "Ч", "Ш", "Щ", "Э", "Ю", "Я"]         # список букв
    for i in range(len(alph)):                     # создание кнопок с буквами
        Button(form1, text=alph[i], command=(lambda x=alph[i]: fetchChr(x))).pack(side=LEFT)
    ent = Entry(form1, width=27)                   # поле ввода для поиска
    ent.pack(side=LEFT)
    entRec['entFind'] = ent                        # поместить объект поля ввода в словарь entRec
    Button(form1, text="Поиск", command=fetchFind).pack(side=LEFT)     # создание кнопки Поиск
 
    form2 = Frame(window)                          # создание внутри окна window контейнера form2
    form2.pack()
    entriesRec = {}                # словарь, для занесения в него объектов Entry ячеек таблицы ввода записей
    for (ix, label) in enumerate(fieldnamesRecTabCyr): # создание надписей заголовков столбцов таблицы
        lab = Label(form2, text=label)
        lab.grid(row=2, column=ix)
    for i in range(1, 26):         # создаются ячейки таблицы для ввода записей
        for (ix, label) in enumerate(fieldnamesRecTab):
            if label == 'keyRec' or label == 'char' or label == 'delR':  # выделяются столбцы, которые потом будут иметь особый режим доступа
                ent = Entry(form2, state='normal', width=6)
            else:
                ent = Entry(form2, width=40)
                ent.bind('<Button-1>', getKey)
            ent.grid(row=i+2, column=ix)
            entriesRec[label+str(i)] = ent   # объекты ячеек таблицы заносятся в словарь, причем к имени 
                                             # столбца ячейки добавляется номер строки, 
                                             # тем самым однозначно определяются координаты ячейки,
                                             # что бы к ней обращаться
    form3 = Frame(window)                    # создание внутри окна window контейнера form3
    form3.pack()
    Button(window, text="Следующая страница", command=fetchNext).pack()  # кнопка Следующая страница
    Label(window, text='      ', width=10).pack(side=LEFT)       # вспомогательная пустая метка
    labKeyRec = Label(window, text='№').pack(side=LEFT)     # надпись перед полем ввода номера ключа
    ent = Entry(window, width=10)                                # поле ввода номера ключа
    ent.pack(side=LEFT)
    entRec['entKeyRec'] = ent             # занесение объекта поле ввода номера ключа в словарь entRec
    Button(window, text="Скрыть", command=hideRec).pack(side=LEFT)             # кнопка Скрыть (запись)
    Button(window, text="Показать скрытые", command=fetchHide).pack(side=LEFT) # кнопка Показать скрытые
    Button(window, text="Открыть", command=openRec).pack(side=LEFT)            # кнопка Открыть (запись)
    Label(window, text=' ', width=2).pack(side=LEFT)                           # вспомогательная пустая метка
    Button(window, text="Удалить", command=delKeyRec).pack(side=LEFT)          # кнопка удалить (запись)
    Label(window, text=' ', width=10).pack(side=LEFT)                           # вспомогательная пустая метка
    Button(window, text="Вывести запись", command=fetchRecord).pack(side=LEFT) # кнопка выводит запись в отдельной форме
    Label(window, text=' ', width=3).pack(side=LEFT)                           # вспомогательная пустая метка
    Button(window, text="Восстановить", command=updatePage).pack(side=LEFT)
    Label(window, text=' ', width=30).pack(side=LEFT)                     # вспомогательная пустая метка
    btns = Button(window, text="Сохранить", command=interSave).pack(side=LEFT)   # кнопка Сохранить (страницу)
    Label(window, text='      ', width=20).pack(side=LEFT)                     # вспомогательная пустая метка
    Button(window, text="Выход", command=fin).pack(side=LEFT)                  # кнопка Выход (из программы)
    return window                                              # функция makeWidgets возвращает окно window

def clear_sheet():
    # очистка листа
    for i in range(1, 26):
        for field in fieldnamesRecTab:
            if field == 'keyRec' or field == 'delR':              # для очистки полей keyRec и delR,
                entriesRec[field+str(i)].config(state='normal')   # нужно открыть их для записи
                entriesRec[field+str(i)].delete(0, END)
                entriesRec[field+str(i)].config(state='readonly')
            else:
                entriesRec[field+str(i)].delete(0, END)         # очистка остальных полей
def fetchChr(ch):
    # выбрать записи на букву ch
    global activCh, typeRec, lab1
    saveRec()                      # предварительно сохранить предыдущую страницу
    typeRec = ''                   # выбор для буквы делать только из открытых записей
    activCh = ch                   # сделать ch текущей буквой
    lab1.config(text=activCh)      # написать, для какой буквы выводятся записи
    dic_recsChr = {}                 # словарь, в который помещаются выбранные записи
    for key in p1.j1.dic_recs.keys():      # выбор записей и помещение их в словарь
        if p1.j1.dic_recs[key].char == ch:
            dic_recsChr[key] = p1.j1.dic_recs[key]
    fetch(dic_recsChr)                        # вывод записей в таблицу формы
def interSave():
    # принудительное сохранение текущей страницы и повторный вывод записей для этой буквы начиная с первой страницы
    fetchChr(activCh)
def fetchHide():
    # вывод скрытых записей
    global typeRec, lab1
    saveRec()
    lab1.config(text='скр')
    typeRec = 'с'              # выбор делать только из скрытых записей
    fetch(p1.j1.dic_recs)
def fetch(dicR):
    # вывод записей из заданнго словаря
    global dicRem                        # словарь записей, оставшихся не выведенными
    clear_sheet()                        # очистка таблицы
    count = 1                            # счетчик показывающий номер строки, в которую выводится запись
    dicRe = dicR.copy()                  # словарь, ведущий учет записей, которые еще не выведены
    while count <= 25 and len(dicRe):    # в цикле, заполнение строк таблицы записями
        for key in dicR.keys():            # в цикле вывод записи удовлетворяющей условию
            if dicR[key].delR == typeRec:
                record = dicR[key]                   # запись для вывода
                for field in fieldnamesRecTab:          # в цикле последовательное заполнение полей в строке
                    if field == 'keyRec' or field == 'delR':    # поля, которые необходимо открыть для записи
                        entriesRec[field+str(count)].config(state='normal')
                        entriesRec[field+str(count)].insert(0, getattr(record, field))
                        entriesRec[field+str(count)].config(state='readonly')
                    else:
                        entriesRec[field+str(count)].insert(0, getattr(record, field))  # все остальные поля
                count += 1         # переход к следующей строке таблицы
                dicRe.pop(key)     # удаление записи, которая выведена из словаря учета оставшихся записей           
                if count > 25:     # если все строки таблицы заполнены, то выход из цикла while
                    break
            else:
                dicRe.pop(key) # удаление из словаря учета записи, которая не удовлетворяет условию вывода в таблицу
    dicRem = dicRe.copy()      # словарь записей, оставшихся не выведенными
 
def fetchNext():
    # вывод на следующей странице записей, оставшихся не выведенными
    saveRec()
    fetch(dicRem)

def updatePage():
    # обновление страницы
    global activCh, typeRec, lab1
    lab1.config(text=activCh)      # написать, для какой буквы выводятся записи
    dic_recsChr = {}                 # словарь, в который помещаются выбранные записи
    for key in p1.j1.dic_recs.keys():      # выбор записей и помещение их в словарь
        if p1.j1.dic_recs[key].char == activCh:
            dic_recsChr[key] = p1.j1.dic_recs[key]
    fetch(dic_recsChr)                        # вывод записей в таблицу формы
 
def delKeyRec():
    # физическое удаление из базы данных записи, которая указана в ячейке entKeyRec
    key = entRec['entKeyRec'].get()  # из ячейки entKeyRec берется ключ записи для удаления
    if key.isnumeric() and (key in p1.j1.dic_recs.keys()): # проверка, указан ли номер существующей записи
        if askyesno('Подтверждение', 'Удалить запись без возможности востановления?'):  # подтверждение на удаление
            del p1.j1.dic_recs[key]               # запись удаляется из динамического словаря p1.j1.dic_recs
            db = shelve.open(p1.j1.nameBook)    # открывается база данных
            del db[key]                      # указанная запись физически удаляется из базы данных
            db.close()                       # база данных закрывается
            for i in range(1, 26): # ищется строка таблицы с этой записью, и помечается как удаленная, 
                if entriesRec['keyRec'+str(i)].get() == key:         # что бы потом при сохранении страницы,
                    entriesRec['delR'+str(i)].config(state='normal') # она не была вновь занесена в базу данных
                    entriesRec['delR'+str(i)].insert(0, 'у')
                    entriesRec['delR'+str(i)].config(state='readonly')
            entRec['entKeyRec'].delete(0, END)            # очищается ячейка, содержащая номер удаляемой записи
        else:
            showinfo('Отмена', 'Удаление записи отменено')   # удаление отменено
    else:
        showinfo('Отмена', 'Укажите номер существующей записи') # не указан номер записи
def hideRec():
    # пометить как скрытую
    key = entRec['entKeyRec'].get()  # из ячейки entKeyRec берется ключ записи для сокрытия
    for i in range(1, 26):           # ищется строка таблицы с этой записью, и помечается как скрытая
        if entriesRec['keyRec'+str(i)].get() == key:
            entriesRec['delR'+str(i)].config(state='normal')
            entriesRec['delR'+str(i)].insert(0, 'с')
            entriesRec['delR'+str(i)].config(state='readonly')
    entRec['entKeyRec'].delete(0, END)           # очищается ячейка, содержащая номер скрываемой записи записи
def openRec():
    # открыть скрытую запись
    key = entRec['entKeyRec'].get()   # из ячейки entKeyRec берется ключ записи для открытия
    for i in range(1, 26):            # ищется строка таблицы с этой записью, и помечается как открытая
        if entriesRec['keyRec'+str(i)].get() == key:
            entriesRec['delR'+str(i)].config(state='normal')
            entriesRec['delR'+str(i)].delete(0, END)
            entriesRec['delR'+str(i)].insert(0, '')
            entriesRec['delR'+str(i)].config(state='readonly')
    entRec['entKeyRec'].delete(0, END)           # очищается ячейка, содержащая номер открываемой записи 
 
def fetchFind():
    # поиск записей по заданной строке
    global lab1
    saveRec()
    clear_sheet()
    lab1.config(text='поиск')      # сигнализирует о режиме поиска
    strF = entRec['entFind'].get().lower() # строка для поиска берется из ячейки entFind
    dicFind = {}                   # словарь, для занесения в него найденных записей
    for key in p1.j1.dic_recs.keys():   # в тлефонном справочнике ищутся записи содержащие искомую строку
        record = p1.j1.dic_recs[key]
        for field in fieldnamesRecFull:
        #for field in fieldnamesRecTab:
            if (field != 'keyRec' and field != 'char' and field != 'delR' and # поиск в полях, за исключением перечисленных
                getattr(record, field).lower().find(strF) != -1):
                dicFind[key] = record
                break
    fetch(dicFind)                  # вывод найденных записей
def saveRec():
    # сохранение текущей страницы
    global typeRec
    for i in range(1, 26):       # просмотр строк и при наличии хотя бы в одном поле строки данных, сохранение ее
        key = entriesRec['keyRec'+str(i)].get() # проверка наличия в строке ключа
        if entriesRec['delR'+str(i)].get() == 'у': # записи помеченные как удаленные пропускаются
            continue
        elif key:                # иначе, если запись не удаленная и с ключом, то она перезаписывается
            record = p1.j1.dic_recs[key]
            for field in fieldnamesRecTab:
                setattr(record, field, entriesRec[field+str(i)].get())
            p1.j1.dic_recs[key] = record
        else: # иначе, если в строке нет ключа, но в одном из полей есть данные, то создается запись-экземпляр
            existRec = False                                               # и помещается а словарь p1.j1.dic_recs
            for field in fieldnamesRecTab:
                if entriesRec[field+str(i)].get(): existRec = True # Если существует запись в поле на этой строке
            if existRec:     # если данные в строке существуют, то создается запись
                if entriesRec['char'+str(i)].get():  # если поле буквы не пусто, то в запись заносится эта буква
                    char = entriesRec['char'+str(i)].get()
                else:              # иначе в запись заносится буква, являющаяся на данный момент активной
                    char = activCh
                field1 = entriesRec['field1'+str(i)].get()             # заполняются переменные
                field2 = entriesRec['field2'+str(i)].get()             # для формирования записи
                field3 = entriesRec['field3'+str(i)].get()
                field4 = ''
                field5 = ''
                field6 = ''
                commen = entriesRec['commen'+str(i)].get()
                if len(p1.j1.dic_recs)>0: # если телефонный справочник не пуст, то к максимальному значению ключа 
                    L = sorted(p1.j1.dic_recs.items(), key=lambda item: int(item[0]))  # прибавляется единица
                    keyRec = str(int(L[-1][0]) + 1)
                else:        # иначе записи присваивается ключ равный 1
                    keyRec = "1"
                record = Record(keyRec, char, field1, field2, field3, field4, field5, field6, commen) # создается запись, экземпляр класса Record
                p1.j1.dic_recs[keyRec] = record     #  и записывается в словарь p1.j1.dic_recs
    p1.save_DB()  # словарь p1.j1.dic_recs сохраняется во внешней базе данных "Книги"

def get_key(val):
    # функция для возврата ключа из словаря по значению
    for key, value in entriesRec.items():    # перебираем пары (ключ, значение)
         if val == value:                    # и находим ключ, у которого заданное значение
             return key
    print("key doesn't exist")

def getKey(event):
    # получить ключ записи
    currStr = get_key(event.widget)[6:]           # номер текущей строки
    currKey = entriesRec['keyRec'+currStr].get()  # ключ текущей записи
    entRec['entKeyRec'].delete(0, END)            # очистка ячейки указывающей выбранный номер записи
    entRec['entKeyRec'].insert(0, currKey)        # запись текущего номера записи в ячейку выбранного номера записи

def fetchRecord():
    # вывод формы с одной записью
    saveRec()                     # сохранение текущей страницы таблицы
    currentKey = entRec['entKeyRec'].get()   # из ячейки entKeyRec берется ключ записи
    if currentKey.isnumeric() and (currentKey in p1.j1.dic_recs.keys()): # проверка, указан ли номер существующей записи
        p1.j1.currentKey = currentKey       # p1.j1.dic_recs[currentKey]    # экземпляр записи для вывода в форме в модуле
        window.destroy()
        p1.open_Record()                          # открытие окна текущей записи
    else:
        showinfo('Отмена', 'Укажите номер существующей записи') # не указан номер записи
 
def fin():            # сохранение перед закрытием окна (в том числе крестом)
    saveRec()         # сохранение текущей страницы
    window.destroy()  # закрытие окна