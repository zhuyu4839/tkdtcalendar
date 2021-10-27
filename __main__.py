import tkinter
from tkdtcalendar import DateTimeCalendar


def callback(result):
        print(result)   # prints the date_time dict

root = tkinter.Tk()
calendar = DateTimeCalendar(root, callback)
root.mainloop()
date_time = calendar.get_date_time()
# the keys are: 'year', 'month', 'day', 'hours', 'minutes' and 'seconds'
print(date_time['year'])
print(date_time['minutes'])
