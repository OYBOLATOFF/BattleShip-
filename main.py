import random
from random import *
from tkinter import *
import colorama
colorama.init();
from colorama import Fore, Back, Style
import contextlib
with contextlib.redirect_stdout(None):
    import pygame
pygame.init();

#C:\Users\79771\Desktop\Программирование <--- Путь к папке с программами

try:
    with open('files/best_result.txt', 'r') as file:
        best_result = int(file.readline());
except FileNotFoundError:
    with open('files/best_result.txt', 'w+') as file:
        file.write("100"); best_result = 100;

battlefield = [[0]*12 for _ in range(12)]
ships = []; count = 0; buttons = {};
already_used = []; flag = True;
kill_sound = pygame.mixer.Sound("files/battleship sounds/kill_ship.wav");
hit_sound = pygame.mixer.Sound("files/battleship sounds/hit.mp3");
no_hit_sound = pygame.mixer.Sound("files/battleship sounds/no_hit.mp3");
bg_color = '#BAD7DF'

#ФУНКЦИЯ РАССТАНОВКИ КОРАБЛЕЙ. DECK - КОЛИЧЕСТВО ПАЛУБ, COUNT - КОЛИЧЕСТВО КОРАБЛЕЙ
def arrange_the_ships(deck, count):
    for _ in range(count):
        while True:
            start_line, start_column = randint(1,10), randint(1, 10);
            vertical = choice([True, False]); #direction в перевод с англ. = направление. direction - случайная цифра 1 или 2. Если 1 - корабль будет генерироваться вертикально, если 2 - горизонтально
            current_ship = []; #Массив конкретного генерирующегося корабля, как и писал выше в начале, в него будем записывать координаты корабля, а потом массив добавим в список кораблей ships
            #Следующую длинную строку сложно описать, т.к. это огромный генератор. Проще говоря, он просто охватывает все соседние клетки, в которых может появиться потенциальный корабль, если все они равны нулю, значит они свободны и там нет кораблей, соответственно нет соседей
            if vertical and start_line >= deck and all(battlefield[start_line-i][start_column] == 0 for i in range(deck)) and all(battlefield[start_line-i-j][start_column-1:start_column+2]==[0, 0, 0] for i in range(deck) for j in [-1, 0, 1]):
                for i in range(deck): 
                    battlefield[start_line-i][start_column] = 1 #Условие выше выполнилось, можно генерировать корабль. Проходимся по нужным индексам, и в них ставим единицу - идентификатор того, что там стоит корабль
                    current_ship.append((start_line-i, start_column)) #
                current_ship.append([deck]) #Все индексы корабля добавлены в его массив, последним элементом добавляю ещё один список с числом внутри - количеством палуб корабля, чтоб программа знала, скольки палубный корабль ранили/потопили
                ships.append(current_ship)
                break;
            #Всё аналогично тому, что я написал выше, только это корабль уже спавнится горизонтально
            elif start_column >= deck and all(battlefield[start_line][start_column-i] == 0 for i in range(deck)) and all( battlefield[start_line-j][start_column-i]==0 for i in range(-1,deck+1) for j in [-1,0,1]):
                for i in range(deck): 
                    battlefield[start_line][start_column-i] = 1
                    current_ship.append((start_line, start_column-i))
                current_ship.append([deck])
                ships.append(current_ship)
                break;

#ПРОВЕРКА НА ПОПАДАНИЕ/ПОТОПЛЕНИЕ N-ПАЛУБНОГО КОРАБЛЯ
def check_for_a_hit( btn, coord ):
    global count, generate_btn, already_used, buttons, win_sound, lefts, best_result
    count += 1;
    count_lbl.configure(text=f'Количество попыток: {count}')
    x = coord[0];
    y = coord[1];
    flag = 0;
    already_used.append(str(coord[0])+str(coord[1]))
    btn.configure(text='X', bg='red', fg='white',command=lambda: text_lbl.configure(text='Вы уже били в эту точку!', fg='red'))
    for ship in ships:
        if (x,y) in ship:
            hit_sound.play()
            already_used[-1] = int(already_used[-1])
            btn.configure(bg='green', text='✓')
            flag = 1;
            ship.remove((x,y)) #Человек ввёл координаты Х и У, если такая координата есть хоть в одном корабле - игрок попал. Методом remove координату удаляем из списка
            if len(ship) > 1: #Если в списке корабля остались ещё координаты, значит остались ещё палубы, значит корабль лишь ранен, но не потоплен
                text_lbl.configure(text=f'Вы попали в {ship[-1][0]}-х палубный корабль!', fg='green')
            elif len(ship) == 1: #Если остался один элемент - вложенный список с количеством палуб внутри, а координат не осталось, значит корабль потоплен
                hit_sound.stop(); kill_sound.play();
                text_lbl.configure(text=f'Вы потопили {ship[-1][0]}-х палубный корабль!', fg='green');
                lefts[ship[-1][0]].set( lefts[ship[-1][0]].get()-1 )
            if all(len(ship) == 1 for ship in ships):
                text_lbl.place(x=365, y=650, width=500, height=50);
                generate_btn = Button(root, text='Нажмите, если желаете сгенерировать поле заново', bg='green', fg='white', font=('Arial', 13, 'bold'), command=generate_table);
                generate_btn.place(x=365, y=600, width=500, height=50);
                text_lbl.configure(text='Игра окончена. Вы потопили все корабли');
                best_result = min(best_result, count);
                for adress in [[column, line] for column in range(1,11) for line in range(1,11)]:
                    if str(adress[0])+str(adress[1]) not in already_used and int(str(adress[0])+str(adress[1])) not in already_used:
                        buttons[str(adress[0])+str(adress[1])].configure(state=DISABLED, bg='#ebebeb');
    if flag == 0: #Если игрок попал, 1 присваивается flag, если нет, то он остаётся 0. Соответственно, если flag = 0, то игрок не попал, выводим сообщение об этом 
        no_hit_sound.play();
        text_lbl.configure(text='Увы, но вы не попали по кораблю', fg='red');

#ГЕНЕРИРУЕТ ТАБЛИЦУ, НА КОТОРОЙ МОЖНО ИГРАТЬ
def generate_table():
    global battlefield, ships, count, buttons, already_used, generate_btn, text_lbl, lefts, best_result_lbl
    best_result_lbl.configure(text=str(best_result))
    for index in range(1,5):
        lefts[index].set(5-index)
    text_lbl['text'] = ''
    generate_btn.destroy();
    generate_btn = 0; count = 0;
    battlefield = [[0]*12 for _ in range(12)]
    ships = []; count = 0; buttons = {}; already_used = [];
    arrange_the_ships(4,1); arrange_the_ships(3,2); arrange_the_ships(2,3); arrange_the_ships(1,4);
    for coord in [[column, line] for column in range(1,11) for line in range(1,11)]:
        now_btn = Button(battle_frame, bg='white', bd=4, font=('Arial', 20), relief=GROOVE)
        now_btn.configure(command = lambda button=now_btn, coord=coord: check_for_a_hit(button, coord));
        now_btn.place(x=(coord[1]-1)*50, y=(coord[0]-1)*50, width=50, height=50)
        buttons[str(coord[0])+str(coord[1])] = now_btn

#ФУНКЦИЯ ВЫВОДА ПОДСКАЗКИ
def pod():
    global battlefield, buttons, already_used, flag
    if flag:
        for coord in [[column, line] for column in range(1,11) for line in range(1,11)]:
            if battlefield[coord[0]][coord[1]] == 1:
                if int(str(coord[0])+str(coord[1])) in already_used:
                    buttons[str(coord[0])+str(coord[1])].configure(text='✓', bg='green', fg='white')
                else:
                    buttons[str(coord[0])+str(coord[1])].configure(text='X', bg='red', fg='white')
            else:
                buttons[str(coord[0])+str(coord[1])].configure(fg='white', bg='white', text='')
    else:
        for coord in [[column, line] for column in range(1,11) for line in range(1,11)]:
            if str(coord[0])+str(coord[1]) in already_used:
                buttons[str(coord[0])+str(coord[1])].configure(text='X', bg='red', fg='white')
            elif int(str(coord[0])+str(coord[1])) in already_used:
                buttons[str(coord[0])+str(coord[1])].configure(fg='white', bg='green', text='✓')
            else:
                buttons[str(coord[0])+str(coord[1])].configure(fg='white', bg='white', text='')
    flag = not(flag)

#ФУНКЦИЯ СОЗДАНИЯ ОКНА С ПРАВИЛАМИ ИГРЫ
def help_window():
    window = Toplevel(root)
    window.title('Правила "Морского Боя"'); window.resizable(width=False, height=False); window.geometry('1300x170');
    window['bg'] = '#d5e8ed'
    Label(window, text='''Правила игры в "Морской Бой":
        Игровое поле представляет собой квадрат 10x10 клеток. На этом поле в хаотичном порядке расположены корабли
        Корабли не могут стоять рядом, расстояние между ними - минимум одна клетка
        Цель игры - потопить все корабли, находящиеся на игровом поле
        Слева отображена панель, показывающая, сколько кораблей осталось потопить''', fg='green', bg='#d5e8ed', anchor='w', font=('Arial', 15, 'bold')).place(x=0, y=0)
    Button(window, bg='green', fg='white', font=('Arial', 20, 'bold'), text='Понятно', command=lambda: window.destroy(), anchor='n', relief=GROOVE, bd=3).place(x=0, y=130, relwidth=1, relheight=1);

#СОЗДАНИЕ ОКНА ПРОГРАММЫ
root = Tk() #Создаём окно программы
root.geometry('1200x800+500+100') #Задаём размеры окна
root.resizable(width=False, height=False); #Отключаем возможность изменить размер вручную
root.title('Морской Бой') #Устанавливаем заголовок в окне
root.iconphoto(False, PhotoImage(file='files/Иконки/battleship.png')) #Устанавливаем иконку
root['bg'] = bg_color

#КНОПКА, КОТОРАЯ ОТКРЫВАЕТ ОКНО С ПРАВИЛАМИ ИГРЫ
help_btn = Button(root, text='ПРАВИЛА ИГРЫ', bg='blue', fg='white', font=('Arial', 15, 'bold'), command=help_window).place(x=20, y=60);

#СОЗДАНИЕ ПОЛЕ БОЯ, НА КОТОРОМ БУДУТ ГЕНЕРИРОВАТЬСЯ КЛЕТКИ КОРАБЛЕЙ
battle_frame = Frame(width=500, height=500, bg='red');
battle_frame.place(x=365, y=100)

#СОЗДАНИЕ ТЕКСТА, КОТОРЫЙ БУДЕТ ПОКАЗЫВАТЬ СТАТУС 'ПОПАЛ/НЕ ПОПАЛ/УЖЕ БИЛ В КЛЕТКУ' И Т.Д
text_lbl = Label(root, text='', fg='blue', font=('Arial', 17, 'bold'), bg=bg_color);
text_lbl.place(x=365, y=600, width=500, height=50);

#СЧЁТЧИК ПОПЫТОК ВВЕРХУ ОКНА
count_lbl = Label(root, text=f'Количество попыток: {count}', font=('Gabriola', 30, 'bold'), bg=bg_color)
count_lbl.place(x=15, y=-20);

#КНОПКА, ЧТОБЫ НАЧАТЬ ИГРУ ЗАНОВО
generate_btn = Button(root, text='Нажмите, если желаете сгенерировать поле заново', bg='green', fg='white', font=('Arial', 13, 'bold'), command=generate_table);
generate_btn.place(x=365, y=600, width=0, height=0);

#ЗАГОЛОВОК ИГРЫ МОРСКОЙ БОЙ
title_lbl = Label(root, text='МОРСКОЙ БОЙ', fg='black', font=('Anime Ace v02', 25, 'bold'), bg=bg_color).place(x=475, y=55);

#КНОПКА-ПЛЮСИК, КОТОРАЯ ПОДСКАЗЫВАЕТ, ГДЕ КОРАБЛИ
podskazka = Button(root, command=pod, text='+', bg='green', fg='white', font=('Arial', 30, 'bold'));
podskazka.place(x=865, y=100, width=25, height=25);

#СОЗДАНИЕ ОКНА, НА КОТОРОМ БУДЕТ СТАТИСТИКА ОСТАВШИХСЯ КОРАБЛЕЙ
c = Canvas(bg=bg_color, width=350, height=180, highlightthickness=0)
c.place(x=10, y=190);

#ГЕНЕРИРУЕМ КВАДРАТИКИ-ПАЛУБЫ КАЖДОГО КОРАБЛЯ, НАПРОТИВ НИХ - ВИДЖЕТ MESSAGE, ПОКАЗЫВАЮЩИЙ, СКОЛЬКО N ПАЛУБНЫХ КОРАБЛЕЙ ОСТАЛОСЬ
for i in range(30, 121, 30):
    c.create_rectangle(i, 10, i+30, 40, fill='black', outline=bg_color)
for i in range(30, 91, 30):
    c.create_rectangle(i, 50, i+30, 80, fill='black', outline=bg_color)
for i in range(30, 61, 30):
    c.create_rectangle(i, 90, i+30, 120, fill='black', outline=bg_color)
c.create_rectangle(30, 130, 60, 160, fill='black', outline=bg_color)

#ЗАГОЛОВОК БЛОКА ОСТАВШИХСЯ КОРАБЛЕЙ
left_message = Label(root, text='Кораблей осталось', font=('Anime Ace v02', 12, 'bold'), bg=bg_color).place(x=35, y=165);

#ПРИВЯЗЫВАЕМ СЧЁТЧИКИ INTVAR-ОМ, ЧТОБЫ В РЕАЛЬНОМ ВРЕМЕНИ МЕНЯТЬ СТАТИСТИКУ
left_4 = IntVar(); left_3 = IntVar(); left_2 = IntVar(); left_1 = IntVar();
left_4.set(1); left_3.set(2); left_2.set(3); left_1.set(4); #УСТАНАВЛИВАЕМ ИЗНАЧАЛЬНОЕ КОЛИЧЕСТВО КОРАБЛЕЙ

#РАССТАВЛЯЕМ КВАДРАТИКИ-СЧЁТЧИКИ, НА КОТОРЫХ ВЫСВЕЧЕНО КОЛИЧЕСТВО КОРАБЛЕЙ
left_4_msg = Message(root, textvariable=left_4, fg='black', font=15, relief=GROOVE, bd=3); left_4_msg.place(x=185, y=200, width=30, height=30);
left_3_msg = Message(root, textvariable=left_3, fg='black', font=15, relief=GROOVE, bd=3); left_3_msg.place(x=185, y=240, width=30, height=30);
left_2_msg = Message(root, textvariable=left_2, fg='black', font=15, relief=GROOVE, bd=3); left_2_msg.place(x=185, y=280, width=30, height=30);
left_1_msg = Message(root, textvariable=left_1, fg='black', font=15, relief=GROOVE, bd=3); left_1_msg.place(x=185, y=320, width=30, height=30);
lefts = [0, left_1, left_2, left_3, left_4]; #КАЖДЫЙ СЧЁТЧИК ЗАПИСЫВАЕМ КАК ОБЪЕКТ В МАССИВ, ЧТОБ УДОБНО МЕНЯТЬ ИХ ПОКАЗАТЕЛЬ ПРИ УБИЙСТВЕ

#ПОКАЗАТЕЛЬ ЛУЧШЕГО РЕЗУЛЬТАТА
Label(root, text='Лучший результат: ', fg='black', bg=bg_color, font=('Gabriola', 30, 'bold')).place(x=830, y=-20);
best_result_lbl = Label(root, text='', font=('Gabriola', 30, 'bold'), bg=bg_color, fg='black');
best_result_lbl.place(x=1125, y=-20);

#ГОТОВО. ГЕНЕРИРУЕМ КОРАБЛИ И НАЧИНАЕМ ИГРУ!
generate_table();

#ЗАПУСКАЕМ ОКНО
root.mainloop()

with open('files/best_result.txt', 'w+') as file:
    file.write(str(best_result))