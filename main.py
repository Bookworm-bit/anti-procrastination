import psutil
import time
import threading

# Create blacklist file
blf = open("blacklist.txt", "x")
blf.close()

app_names = []
time_limits = []
app_times_open = {app_names[i] : 0 for i in range(len(app_names))}

def check_app_status(app_name):
    for proc in psutil.process_iter():
        try:
            if proc.name() == app_name:
                return True
            else:
                return False
        except psutil.NoSuchProcess:
            return False


def close_app(app_name):
    for proc in psutil.process_iter():
        try:
            if proc.name() == app_name:
                proc.kill()
        except psutil.NoSuchProcess:
            pass


def reset_app_open_times():
    while True:
        for item in app_times_open.keys():
            app_times_open[item] = 0

        time.sleep(86400)


def log_app_open_times():
    while True:
        for app in app_times_open.keys():
            if check_app_status(app):
                app_times_open[app] += 1

        time.sleep(60)


resetter = threading.Thread(target=reset_app_open_times)
resetter.daemon = True
app_time_logger = threading.Thread(target=log_app_open_times)
app_time_logger.daemon = True

while True:
    if resetter.is_alive == False:
        resetter.start()

    if app_time_logger.is_alive == False:
        app_time_logger.start()
    
    start_len = len(app_names)

    print("""
    Welcome to Bookworm-bit's anti-procrastination app
    [1] Add an app to your blacklist
    [2] Modify an app on your blacklist
    [3] Remove an app on your blacklist
    [4] Show blacklist
    [5] Exit
    """)

    try:
        choice = int(input("Enter a number from the list above: "))
    except ValueError:
        print("Please enter a number from the list above")
        continue
    # Adding app to blacklist
    if choice == 1:
        app_index = 0
        app_name = input(
            "Enter the name of the app you want to add to your blacklist: ")
        
        with open("blacklist.txt", "r+") as blfile:
            blfile.write(app_name)
            app_index = len(blfile.readlines()) - 1
        print("App added to blacklist!")

        time_limit = input(
            "Enter the time limit you want to set for this app (minutes): ")
        try:
            time_limit = int(time_limit)
        except ValueError:
            print("Please enter a number")
            continue
        with open("blacklist.txt", "r+") as blfile:
            blfile.readlines()[app_index] += f" [{str(time_limit)}]"
            app_names.append(app_name)
            time_limits.append(time_limit)

    # Modifying app on blacklist
    elif choice == 2:
        app_index = 0
        app_times = []
        app_in_blacklist = False

        app_name = input(
            "Enter the name of the app you want to modify on your blacklist: ")
        with open("blacklist.txt", "r+") as blfile:
            data = blfile.readlines()
            app_names = [app.partition(" [")[0] for app in data]
            app_times = [app.partition(" [")[2].partition("]")[0] for app in data]
        
        if app_name in app_names:
            app_index = app_names.index(app_name)
            app_in_blacklist = True
        else:
            print("App not found in blacklist")
            continue
        
        if app_in_blacklist:
            time_limit = input(
                "Enter the new time limit you want to set for this app (minutes): ")
            try:
                time_limit = int(time_limit)
            except ValueError:
                print("Please enter a number")
                continue

            with open("blacklist.txt", "r+") as blfile:
                blfile.readlines()[app_index] = f"{app_name} [{str(time_limit)}]"
                time_limits.append(time_limit)
            print("App modified on blacklist!")
    
    # Removing app from blacklist
    elif choice == 3:
        app_index = 0
        app_names = []
        app_times = []
        app_in_blacklist = False

        app_name = input(
            "Enter the name of the app you want to remove from your blacklist: ")
        with open("blacklist.txt", "r+") as blfile:
            data = blfile.readlines()
            app_names = [app.partition(" [")[0] for app in data]
        
        if app_name in app_names:
            app_index = app_names.index(app_name)
            app_in_blacklist = True
        else:
            print("App not found in blacklist")
            continue
            
        if app_in_blacklist:
            with open("blacklist.txt", "r+") as blfile:
                blfile.readlines().pop(app_index)
            print("App removed from blacklist!")
            app_names.pop(app_index)

    # Print blacklist
    elif choice == 4:
        with open("blacklist.txt", "r") as blfile:
            print(blfile.readlines())

    # Exit
    elif choice == 5:
        break
    
    # App checking
    with open('blacklist.txt', 'r') as blfile:
        data = blfile.readlines()
        app_names = [app.partition(" [")[0] for app in data]
        app_times = [app.partition(" [")[2].partition("]")[0] for app in data]

        for app in app_names:
            if check_app_status(app):
                close_app(app)
                print(f"Closed {app}")
            else:
                continue
    end_len = len(app_names)

    if start_len < end_len:
        for i in range(end_len - start_len, -1 * (end_len - start_len) - 1, -1):
            app_times_open[app_names[i]] = 0