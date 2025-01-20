from tinydb import TinyDB, Query
from datetime import datetime
import click
# DATABASE MANAGEMENT

# Conectar a la base de datos (se crea si no existe)
db = TinyDB('schedule.json')
time_format = "%H:%M"


# Leer (Consultar) registros
#timebooks = schedule.all()

# Actualizar un registro
#schedule.update({'book': "08-12"}, Query().id == 1)


# Eliminar un registro
#timebooks.remove(Schedule.book== '1')

class Schedule:
 
    def __init__(self, data):
        self.__dict__.update(data)

class Book:
 
    def __init__(self, data):
        self.__dict__.update(data)

    

def _get_date_today():
    # Get current date
    current_date = datetime.now()
    # Format it to dd/mm/yyyy
    formatted_date = current_date.strftime("%d/%m/%Y")
    return formatted_date

# DONE: Check how many time you've

def available_hours():
    today_date = _get_date_today()
    today_record = db.table('schedule').get(Query().day == today_date)
    current_time = datetime.now().strftime(time_format)

    if today_record:
        # Ensure the 'end_of_day' string has both hour and minute (e.g., "20" becomes "20:00")
        end_of_day_str = today_record['end_of_day']
        if len(end_of_day_str) == 2:  # Handle the case where it’s just the hour (e.g., '20')
            end_of_day_str += ":00"

        # Convert today's end time and current time to datetime objects
        end_of_day = datetime.strptime(end_of_day_str, time_format)
        current_time_obj = datetime.strptime(current_time, time_format)

        # Calculate the time difference
        available_time = end_of_day - current_time_obj

        # Ensure we handle the result properly
        if available_time.days >= 0:  # Ensure we don't have negative time
            available_hours = str(available_time)
            available_hours = available_hours.split(":")
            return available_hours[0]+":"+available_hours[1]

        else:
            return "No available time left for today."


# TODO: Check available time's worth value

# TODO: book/unbook a timebox
def time_booking(start_time, end_time, reasons, day):
    """Book a time box for a list of reasons"""
    if day == "Today":
        day = _get_date_today()
    book_storage = db.table('book')
    new_id = len(book_storage.all()) + 1
    book_data = {
        'id': new_id,
        "day" : day,
        "from" : start_time,
        "to" : end_time,
        "reasons" : reasons
    }
    book_storage.insert(book_data)
    print("New time book added with id: "+str(new_id))
    return new_id
    

# DONE: set personal dayily timing

def personal_daily_timing(start_time, end_time):
    """Define the personal day-to-day schedule based on the start and end time of the working day."""
    # Crear (Insertar) un nuevo registro
    schedule = db.table('schedule')
    new_id = len(schedule.all()) + 1
    day = _get_date_today()

    # Convertir los tiempos a cadenas en lugar de objetos datetime
    start_time_str = datetime.strptime(start_time, time_format).strftime(time_format)
    end_time_str = datetime.strptime(end_time, time_format).strftime(time_format)

    # Calcular las horas disponibles
    start_dt = datetime.strptime(start_time, time_format)
    end_dt = datetime.strptime(end_time, time_format)
    available_hours = str(end_dt - start_dt)
    available_hours = available_hours[:5]

    daily_timing = {
        'id': new_id,
        'day': day,
        'start_of_day': start_time_str,  # Guardamos como cadena
        'end_of_day': end_time_str,      # Guardamos como cadena
        'available_hours': available_hours,
    }
    schedule.insert(daily_timing)
    print("New daily timing added")
    return new_id

def getById(theId,table):
    return db.table(table).get(Query().id==theId)

def getBooksForDay(day=_get_date_today()):
    return db.table('book').search(Query().day==day)

@click.group()
def cli():
    """Command-line interface for schedule management"""
    pass


@click.command()
@click.option('--start', prompt='Military hour of daily start',
              help='What hour your day is starting up?')
@click.option('--end', prompt='Military hour of daily end',
              help='What hour your day is ending up?')
def day(start, end):
    """Insert personaly daily timing for the day"""
    id = personal_daily_timing(start, end)
    print(str(getById(id,'schedule')).replace("_"," "))

@click.command()
def avt():
    """Know current available hours"""
    print("Available hours: " + available_hours())

@click.command()
@click.option('--from_time', prompt='Military hour of time booking start',
              help='What hour your book is starting up?')
@click.option('--to', prompt='Military hour of time booking end',
              help='What hour your book is ending up?')
@click.option('--x', prompt='Reason for booking',
              help='What are you booking your gold-worthing time for?')
@click.option('--day', default="Today", 
              help='When you want to use this book of time? (optional)', 
              prompt='What day this book is for', required=False)
def book(from_time, to, x, day):
    """Book a time block into a day"""
    id_book = time_booking(from_time, to, x, day)
    print(str(getById(id_book,'book')))

@click.command()
def books():
    """Know your day's time books"""
    print(str(getBooksForDay()).removeprefix("[{").removesuffix("}]").replace('{','\n').replace("},","\n"))


cli.add_command(day)
cli.add_command(avt)
cli.add_command(book)
cli.add_command(books)

if __name__ == "__main__":
    cli()
