try:
    import tkinter
    from tkinter import ttk
except ImportError:
    import Tkinter as tkinter
    import ttk
from tkinter import StringVar, Label
import calendar


class DateTimeCalendar:
    """
    The widget returns date and time in a dictionary. To get this dictionary
    you have to use a get_date_time() function.
    Attributes
    ----------
    master : object
        tkinter root window object
    callback : function
        A function to receiving selected date and time
    date_time : dict
        A dictionary where every date and time element is a key
    Public Functions
    ----------------
    get_date_time()
        Returns a dictionary of date and time elements
    Example
    -------
    def callback(result):
        print(result)   # prints the date_time dict
    root = tkinter.Tk()
    calendar = DateTimeCalendar(root)
    root.mainloop()
    date_time = calendar.get_date_time()
    # the keys are: 'year', 'month', 'day', 'hours', 'minutes' and 'seconds'
    print(date_time['year'])
    print(date_time['minutes'])
    """

    datetime = calendar.datetime.datetime

    def __init__(self, master, callback=None):
        """
        Parameters
        ----------
        master : object
            tkinter root window object
        """
        width, height = 285, 300
        # Place the calendar to where the mouse cursor
        ws = master.winfo_screenwidth()
        hs = master.winfo_screenheight()
        xc = master.winfo_pointerx()
        yc = master.winfo_pointery()
        master.title('Calendar')
        master.geometry('%dx%d+%d+%d' % (width,
                                         height,
                                         xc - width if xc + width > ws else xc,
                                         yc - height if yc + height > hs else yc))
        master.resizable(False, False)
        master.attributes('-topmost', 1)
        self.master = master

        # App's private variables
        self._months = self._get_month_names()
        self._months_days = self._get_months_days_dict()
        self._clicked_button = None
        self._days_buttons = None
        self._now = self.datetime.now()
        today = self._now
        self.date_time = {'year': today.year, 'month': today.month, 'day': today.day, 'hour': today.hour,
                          'minutes': today.minute, 'seconds': today.second}
        self._date = '%d-%s-%s' % (today.year, str(today.month) if today.month > 9 else '0%d' % today.month,
                                   str(today.day) if today.day > 9 else '0%d' % today.day)
        self._time = '%s%s%s%s%s' % (str(today.hour) if today.hour > 9 else '0' + str(today.hour), ':',
                                     str(today.minute) if today.minute > 9 else '0' + str(today.minute), ':',
                                     str(today.second) if today.second > 9 else '0' + str(today.second)
                                     )
        self._callback = callback

        # Configures style for app's widgets
        self._configure_style()

        # Date fields
        self._place_date_fields()

        # Weekday fields
        self._place_weekday_fields()

        # Day of month fields
        self._enable_month_days()

        # Time fields
        self._place_time_fields()

        ttk.Button(master, text='OK', command=self._select_date_time, style='Select.TButton') \
            .place(x=225, y=255, width=35, height=35)

    def _get_month_names(self):
        """Returns list of month names"""

        return 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'

    def _get_months_days_dict(self):
        """
        Returns a dictionary where keys are months and values are their
        number of days
        """

        months_days = dict()
        months_days['January'] = 31
        months_days['February'] = 28
        months_days['March'] = 31
        months_days['April'] = 30
        months_days['May'] = 31
        months_days['June'] = 30
        months_days['July'] = 31
        months_days['August'] = 31
        months_days['September'] = 30
        months_days['October'] = 31
        months_days['November'] = 30
        months_days['December'] = 31

        return months_days

    def _configure_style(self):
        """Contains all style configurations"""

        style = ttk.Style()

        # Root window's background color
        style.configure('TLabel', background='#e0dfde')
        style.configure('TButton', background='#e0dfde')

        # Custom style
        style.configure('Hor.TFrame', background='#6a9eba')
        style.configure('Ver.TFrame', background='#000000')

        style.configure('TCombobox', selectbackground=[('normal', 'white')])
        style.configure('TCombobox', selectforeground=[('normal', 'black')])

        style.configure('Day.Off.TButton', background='#d9d9d9', relief='flat')
        style.configure('Day.TButton', background='#e0dfde', relief='flat')
        style.configure('Day.Clicked.TButton', background='#8cd0f5', relief='flat')
        style.configure('Select.TButton', background='#6a9eba', foreground='#ffffff', font=('', 8, 'bold'))

    def _place_weekday_fields(self):
        # Weekday of the month buttons
        x = 15
        y = 45
        WEEKS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
        for i in range(7):
            lb = Label(self.master, text=WEEKS[i], borderwidth=2, relief='groove')
            lb.place(x=x, y=y, width=35, height=35)
            if i % 6 == 0:
                lb.config(bg='gray')
            x += 35

    def _place_date_fields(self):
        """Creates all relevant to date fields"""

        # Month selection fields
        ttk.Label(self.master, text='Month:').place(x=10, y=15)
        self._month = StringVar()
        month_combobox = ttk.Combobox(self.master, width=9, textvariable=self._month)
        month_combobox.place(x=60, y=13)
        month_combobox.bind('<<ComboboxSelected>>', self._enable_month_days)
        self._month_combobox = month_combobox
        self._load_months()

        # Year selection fields
        ttk.Label(self.master, text='Year:').place(x=165, y=15)
        self._year = StringVar()
        year_combobox = ttk.Combobox(self.master, width=5, textvariable=self._year)
        year_combobox.place(x=205, y=13)
        year_combobox.bind('<<ComboboxSelected>>', self._enable_month_days)
        self._year_combobox = year_combobox
        self._load_years()

    def _place_day_fields(self):
        """Creates all relevant to day of month fields"""

        # Days of the month buttons
        if not self._days_buttons:
            days_buttons = []
            days = 31
            for i in range(1, days + 1):
                # Creates a button with disabled state
                button = ttk.Button(self.master, text=str(i))
                button.configure(command=lambda btn=button: self._day_button_callback(btn))
                days_buttons.append(button)
            self._days_buttons = days_buttons

        weekday = self.datetime(int(self._year.get()), self._month_combobox.current() + 1, 1).weekday()
        weekday = 0 if weekday == 6 else (weekday + 1)
        x = 15 + 35 * weekday
        y = 80
        weekday += 1
        for i in range(len(self._days_buttons)):
            button = self._days_buttons[i]
            button.place(x=x, y=y, width=35, height=35)
            # button.state(['disabled'])
            button.configure(style='Day.TButton')
            if (i + weekday) % 7 == 0 or (i + weekday) % 7 == 1:
                button.configure(style='Day.Off.TButton')
            if i == self._now.day:
                button.focus()
                self._day_button_callback(button)
            # Updates the x,y location
            x += 35
            if (i + weekday) % 7 == 0:
                x = 15
                y += 35

    def _place_time_fields(self):
        """Creates all relevant to time fields"""

        # Hour selection fields
        hour_combobox = ttk.Combobox(self.master, width=3,
                                     values=list(map(lambda x: '0' + str(x) if x < 10 else x, [*range(24)])))
        hour_combobox.place(x=92, y=265, width=38)
        hour_combobox.bind('<<ComboboxSelected>>', self._load_time)
        hour_combobox.current(self._now.hour)
        self._hour_combobox = hour_combobox
        ttk.Label(self.master, text=':').place(x=130, y=265)

        # Minutes selection fields
        minutes_combobox = ttk.Combobox(self.master, width=3,
                                        values=list(map(lambda x: '0' + str(x) if x < 10 else x, [*range(60)])))
        minutes_combobox.place(x=137, y=265, width=38)
        minutes_combobox.bind('<<ComboboxSelected>>', self._load_time)
        minutes_combobox.current(self._now.minute)
        self._minutes_combobox = minutes_combobox
        ttk.Label(self.master, text=':').place(x=175, y=265)

        seconds_combobox = ttk.Combobox(self.master, width=3,
                                        values=list(map(lambda x: '0' + str(x) if x < 10 else x, [*range(60)])))
        seconds_combobox.place(x=182, y=265, width=38)
        seconds_combobox.bind('<<ComboboxSelected>>', self._load_time)
        seconds_combobox.current(self._now.second)
        self._seconds_combobox = seconds_combobox

    def _load_months(self):
        """Loads months names into combobox"""

        self._month_combobox.configure(values=self._months)
        self._month_combobox.current(self._now.month - 1)

    def _load_years(self):
        """Loads years into combobox: current year +/- 50"""

        years = [*range(self._now.year - 50, self._now.year + 51)]
        years.reverse()
        self._year_combobox.configure(values=years)
        self._year_combobox.current(years.index(self._now.year))

    def _enable_month_days(self, event=None):
        """Enables relevant days of a selected month"""

        month = self._month_combobox.get()
        year = self._year_combobox.get()

        if month and year:
            # Fields are not empty
            days = self._months_days[month]

            year = int(year)
            if month == 'February':
                # Leap year - 29 days
                if (year % 4 == 0 and year % 100 != 0) \
                        or (year % 400 == 0 and year % 3200 != 0):
                    days += 1

            self._place_day_fields()

            i = 0
            while i <= days - 1:
                # Enables days of a month
                self._days_buttons[i].state(['!disabled'])
                i += 1

            while i < 31:
                # Disables days that exceed the number of days in a month
                self._days_buttons[i].state(['disabled'])
                i += 1

    def _day_button_callback(self, button):
        """A callback of a days of the month button"""

        if self._clicked_button:
            self._clicked_button.configure(style='Day.TButton')

        button.configure(style='Day.Clicked.TButton')
        self._clicked_button = button

        # Updates selected_date_label text
        month = self._month_combobox.get()
        month = self._months.index(month) + 1
        day = button.cget('text')
        year = self._year_combobox.get()

        date = '%s-%s-%s' % (year, str(month) if month > 9 else '0%d' % month,
                             day if int(day) > 9 else '0%s' % day)
        self._date = date

    def _load_time(self, event=None):
        """Time selection fields\' callback"""

        hour = self._hour_combobox.get()
        minutes = self._minutes_combobox.get()
        seconds = self._seconds_combobox.get()

        if hour and minutes and seconds:
            # No empty fields
            time = hour + ':' + minutes + ':' + seconds
            self._time = time

    def _select_date_time(self):
        """Creates and saves a dictionary of date and time.

        After a dictionary is created the window is closed.
        """

        month = self._month_combobox.get()
        year = self._year_combobox.get()

        day = ''
        if self._clicked_button:
            day = self._clicked_button.cget('text')

        hour = self._hour_combobox.get()
        minutes = self._minutes_combobox.get()
        seconds = self._seconds_combobox.get()

        if month and year and day and hour and minutes and seconds:

            date_time = {}

            month = str(self._months.index(month) + 1)
            if int(month) < 10:
                month = '0' + month

            if int(day) < 10:
                day = '0' + day

            date_time['year'] = year
            date_time['month'] = month
            date_time['day'] = day

            date_time['hour'] = hour
            date_time['minutes'] = minutes
            date_time['seconds'] = seconds

            self.date_time = date_time
            if self._callback:
                self._callback(date_time)
            self.master.destroy()

    def get_date_time(self):
        """Returns a dictionary of date and time elements"""

        return self.date_time

