from datetime import datetime, date, timedelta

import matplotlib.pyplot as plt
from matplotlib import patches 
from math import floor

#from Booking.calendar_api import FORMAT_DATETIME
#------------------------------------------------------------------------------

def print_time(x):
    return f'{floor(x)}:{round((x - floor(x)) * 60) :02}'

def draw_schedule(schedule, day: datetime, pad = 0.4, delta = 0.04):

    cur_time = datetime.now()
    hour_now = cur_time.minute / 60 + cur_time.hour
    next_booking = 0

    booked_intervals = []
# Обработка квантов броней
    
    for booking in schedule:
        start_time = datetime.strptime(booking['start'], FORMAT_DATETIME)
        end_time = datetime.strptime(booking['end'], FORMAT_DATETIME)

        

        if start_time.date() == day.date():
            hours_start = (start_time.hour * 60 + start_time.minute) / 60  
        else:
            hours_start = 0
        
        if end_time.date() == day.date():
            hours_end = (end_time.hour * 60 + end_time.minute) / 60
        else:
            hours_end = 24
            
        if start_time.date() == day.date() and \
            end_time.date() == day.date():
            booked_intervals.append((hours_start, hours_end))
        
        if start_time.date() == (day + timedelta(days=1)).date() and \
            next_booking > start_time.hour * 60 + start_time.minute + 24:
            next_booking = start_time.hour * 60 + start_time.minute + 24
    
    if next_booking == 0:
        next_booking = 48
    
    if len(booked_intervals) == 0:
        return None
    else:
        booked_intervals = sorted(booked_intervals, key = lambda x: x[0])
#подсчет высоты рисункаы
    y_limit = 0
    last_time = 0
    for booking in booked_intervals:
        if last_time == booking[0]:
            y_limit += 2
        else:
            y_limit += 3
        last_time = booking[1]
    if last_time != 24 or next_booking != 24:
        y_limit += 1
    figsize = (16,y_limit)

    x_limit = figsize[1] / y_limit * figsize[0]

# Подготовка к отрисовке
    now_color = 'black'
    plt.figure(figsize = figsize, dpi = 100)
    ax = plt.subplot()
    if hour_now > 18 or hour_now < 8:
        plt.rcParams['figure.facecolor'] = 'xkcd:dark grey'
        now_color = 'white'
        ax.set_facecolor('xkcd:dark grey')

    plt.xlim(-0.3, x_limit + 0.3)
    plt.ylim(0, y_limit)
    plt.gca().invert_yaxis()

    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    ax.get_xaxis().set_ticks([])
    ax.get_yaxis().set_ticks([])
    
    i = -2
    last_time = 0
    for booking in booked_intervals:
        if last_time == booking[0]:
            i += 2
        else:
            i += 3
#отрисовка прямоугольников занятых квантов
        rect = patches.FancyBboxPatch((pad, i + pad + delta),
                                      x_limit - pad * 2, 
                                      2 - pad * 2 - delta * 2,
                                      boxstyle = f'round,pad = {pad}', 
                                      color = 'xkcd:muted pink')
        ax.add_patch(rect)

        ax.text(x = 1, y = ( i + 0.9), s = 'Бронь: Имя брони', fontsize = 36, color = 'black')
        ax.text(x = 1, y = (i + 1.7), s = f'{print_time(booking[0])} - {print_time(booking[1])}', \
                fontsize = 30, color = 'black', style='italic')
#отрисовка промежутков свободного времени
        if not last_time == booking[0]:
            ax.axvline( x=1, ymin = 1/y_limit*(y_limit + 0.9 - i), ymax = 1/y_limit*(y_limit + 0.1 - i), color = 'gray')
            ax.text(x = 1.5, y = (-0.3 + i), s = f'свободно: {floor(booking[0] - last_time)}ч ' + \
                    f'{round((booking[0] - last_time - floor(booking[0] - last_time)) * 60) :02}мин', \
                    fontsize = 36, color = 'gray',  style='italic')
# отрисовка линии текущего времени
        if day == date.today() and hour_now > last_time and hour_now < booking[0] and last_time != booking[0]:
            y_cord = (hour_now - last_time) / (booking[0] - last_time) + i - 1
            ax.axhline(y_cord, xmin = 0.01, xmax= 1, linewidth = 4, color = now_color)
            ax.plot(0, y_cord, marker=".", markersize=60, color = now_color)
        if day == date.today() and hour_now >= booking[0] and hour_now <= booking[1]:
            y_cord = (hour_now - booking[0]) / (booking[1] - booking[0]) * 2 + i
            ax.axhline(y_cord, xmin = 0.01, xmax= 0.07, linewidth = 4, color = now_color)
            ax.plot(0, y_cord, marker=".", markersize=60, color = now_color)
        
        last_time = booking[1]

#drow last free interval 
    if last_time != 24 or next_booking != 24:
        i += 3
        ax.axvline( x=1, ymin = 1/y_limit*(y_limit + 0.9 - i), ymax = 1/y_limit*(y_limit + 0.1 - i), color = 'gray')
        if next_booking != 48:
            ax.text(x = 1.5, y = (-0.35 + i), s = f'свободно до завтра {floor(next_booking - 24)}:' + \
                    f'{round((next_booking - 24 - floor(next_booking - 24)) * 60) :02}', \
                    fontsize = 36, color = 'gray',  style='italic')
        else:
             ax.text(x = 1.5, y = (-0.35 + i), s = f'свободно более 24ч', \
                    fontsize = 36, color = 'gray',  style='italic')
                
#        ax.text(x = 1.5, y = (-0.35 + i), s = f'свободно: {floor(next_booking - last_time)}ч ' + \
#                    f'{round((next_booking - last_time - floor(next_booking - last_time)) * 60) :02}мин', \
#                    fontsize = 36, color = 'gray',  style='italic')
                
        if day == date.today() and hour_now >= last_time:
            y_cord = (hour_now - last_time) / (24 - last_time) + i - 1
            ax.axhline(y_cord, xmin = 0.01, xmax= 0.07, linewidth = 4, color = now_color)
            ax.plot(0, y_cord, marker=".", markersize=60, color = now_color)

    image_path = f'tests/schedule.png'
    plt.savefig(image_path, 
                bbox_inches = 'tight', 
                pad_inches = 0)
    return image_path
