import psutil
import time
import threading
import os.path as ospath
import re

# Create blacklist file if it does not exist
if ospath.isfile("blacklist.txt") == False:
    blf = open("blacklist.txt", "x")
    blf.close()

# Create daily app times log file if it does not exist
if ospath.isfile("app_times_log.txt") == False:
    atlf = open("app_times_log.txt", "x")
    atlf.close()

# Create global app times log file if it does not exist
if ospath.isfile("total_app_times_log.txt") == False:
    tatlf = open("total_app_times_log.txt", "x")
    tatlf.close()

# Declare variables
app_names = []
time_limits = []
app_times_open = {app_names[i] : 0 for i in range(len(app_names))}


# Checks if apps are open
def check_app_status(app_name):
    for proc in psutil.process_iter():
        try:
            if proc.name().lower().partition(".")[0] == app_name.lower():
                return True
            else:
                return False
        except psutil.NoSuchProcess:
            return False


# Closes app
def close_app(app_name):
    for proc in psutil.process_iter():
        try:
            if proc.name().lower().partition(".")[0] == app_name.lower():
                proc.kill()
        except psutil.NoSuchProcess:
            print("No such process")
            pass


# Daily reset of daily app open times
def reset_app_open_times():
    while True:
        for item in app_times_open.keys():
            app_times_open[item] = 0

        time.sleep(86400)


# Log how long an app is open in a day
def log_app_open_times():
    n = 1
    while True:
        for app in app_times_open.keys():
            if check_app_status(app):
                app_times_open[app] += 1
        
        # Daily app time open
        for item in app_times_open.keys():
            with open("app_times_log.txt", "r+") as atlf:
                atlf.write(f"{item} : {app_times_open[item]}\n")

        # Total app time open
        with open("total_app_times_log.txt", "r+") as tatlf:
            if len(tatlf.readlines()) == 0:
                tatlf.write(f"{item} : {app_times_open[item]}\n")
            else:    
                for item in app_times_open.keys():
                    data = tatlf.readlines()
                    temp_ind = 0

                    if re.match(f"^{item}.*", item):
                        temp_ind = app_names.index(item)
                        previous_time = int(data[temp_ind].split(": ")[2])
                        data[temp_ind] = f"{item} : {previous_time + app_times_open[item]}, {n}\n"
        
        n += 1
        time.sleep(60)


# Check how long an app has been open for in a day
def check_app_times():
    while True:
        for app in app_times_open.keys():
            if app_times_open[app] >= time_limits[app_names.index(app)]:
                close_app(app)
                app_times_open[app] = 0

        time.sleep(60)


# Initiates daemon threads that run the above functions
resetter = threading.Thread(target=reset_app_open_times)
resetter.daemon = True
app_time_logger = threading.Thread(target=log_app_open_times)
app_time_logger.daemon = True

# Main loop
while True:
    # Checking if threads are alive and starting them if nessacary
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
    [5] Show how long you have used an app today
    [6] Show how long you have used an app since you started using it
    [7] Show how long on average you use an app per day
    [8] Exit
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

    # Show how long you have used an app today
    elif choice == 5:
        with open("app_times_log.txt", "r") as atlfile:
            print(" minutes \n".join(atlfile.readlines()))

    # Total app time open
    elif choice == 6:
        with open("total_app_times_log.txt", "r") as tatlfile:
            print(" minutes \n".join([item.partition(",")[0] for item in tatlfile.readlines()]))

    # Average time open for a specific app
    elif choice == 7:
        selected_app = input("Enter the name of an app on your blacklist: ")
        with open("total_app_times_log.txt", "r") as tatlfile:
            data = tatlfile.readlines()
            for item in data:
                if re.match(f"^{selected_app}.*", item):
                    day_count = int(item.partition(", ")[2].partition(" \n")[0])
                    print(f"You use {selected_app} for around {str(int(item.partition(': ')[2].partition(', ')[0]) / day_count)} minutes per day")

    # Exit
    elif choice == 8:
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

    for item in app_names:
        if item not in app_times_open.keys():
            app_times_open[item] = time_limits[app_names.index(item)]