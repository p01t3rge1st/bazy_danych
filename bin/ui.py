from pe_activities import PeActivities
import re
from datetime import *

class UI:
    
    @staticmethod
    def show_upcoming_week(all_classes : PeActivities):
        today = date.today().weekday()
        today_date = date.today()
        pattern = "Filia"
        date_pattern = r"(\d{2}[-./]\d{2}[-./]\d{4})"
        dates = [] # list with classes with dates

        day_offset = 0  # counter of day shift
        for i, activity in enumerate(all_classes.get_activities()):     #print days (today) - Friday
            if all_classes.return_activity_index(i) >= today and not re.search(pattern, all_classes.get_acivity(i)):
                if i > 0:
                    if all_classes.return_activity_index(i) != all_classes.return_activity_index(i - 1) and all_classes.return_activity_index(i - 1) >= today:
                        day_offset += 1
                current_date = today_date + timedelta(days=day_offset)
                match = re.search(date_pattern,activity)       
                if match and datetime.strptime(match.group(),"%d.%m.%Y").date() >= today_date:
                    dates.append(f"{activity}")
                elif not match:      
                    dates.append(f"{activity} {current_date.strftime('%d.%m.%Y')}")

        next_week_start = today_date + timedelta(days=(7 - today))              #omit weekend
        if next_week_start.weekday() != 0:
            next_week_start += timedelta(days=(7 - next_week_start.weekday()))  # ensure it is Monday
        day_offset = (next_week_start - today_date).days

        for i, activity in enumerate(all_classes.get_activities()):     #print days Monday - (a week later from Today)
            if all_classes.return_activity_index(i) <= today and not re.search(pattern, all_classes.get_acivity(i)):
                if i > 0:
                    if all_classes.return_activity_index(i) != all_classes.return_activity_index(i - 1):
                        day_offset += 1
                current_date = today_date + timedelta(days=day_offset)
                match = re.search(date_pattern,activity)       
                if match and datetime.strptime(match.group(),"%d.%m.%Y").date() >= today_date:
                    dates.append(f"{activity}")
                    continue
                elif not match:      
                    dates.append(f"{activity} {current_date.strftime('%d.%m.%Y')}")

        print(*dates, sep='\n')
            
    @staticmethod
    def show_cancelled_classes(all_classes : list[PeActivities]):
        print(*all_classes, sep='\n')

    @staticmethod
    def return_day_index(day : str) -> int:
        patterns = {"poniedziałek" : 0, "wtorek" : 1, 
                    "środa" : 2, "czwartek" : 3, "piątek" : 4}
        for key, value in patterns.items():
            if re.search(key, day):
                return value

    @staticmethod
    def filtering(all_classes : PeActivities, place : str = None, day : str = None, day_end : str = None, 
                  time : str = None, time_end :str = None, name : str = None): #by day, time, place, sports and combined
        dates = []

        conditions = {
            "place": re.compile(place) if place else None,
            "name": re.compile(name) if name else None
        }

        day_start_index : int = None
        day_end_index : int = None

        if day != None:
            day_start_index = UI.return_day_index(day)
        if day_end != None:
            day_end_index = UI.return_day_index(day_end)

        user_time_start = datetime.strptime(time, "%H:%M").time() if time else None
        user_time_end = datetime.strptime(time_end, "%H:%M").time() if time_end else None

        for i, activity in enumerate(all_classes.get_activities()):
            match = True

            for key, regex in conditions.items():
                if regex and not regex.search(all_classes.get_acivity(i)):
                    match = False
                    break

            if match and (user_time_start or user_time_end):
                time_list = all_classes.get_time(i)
                if time_list:
                    activity_start = datetime.strptime(time_list[0], "%H:%M").time()
                    activity_end = datetime.strptime(time_list[1], "%H:%M").time()

                    if (user_time_start and activity_start < user_time_start) or (user_time_end and activity_end > user_time_end):
                        match = False

            if match:
                if day and day_end:
                    if(all_classes.return_activity_index(i) < day_start_index or all_classes.return_activity_index(i) > day_end_index):
                        match = False
                if day and day_end == None:
                    if(all_classes.return_activity_index(i) < day_start_index or all_classes.return_activity_index(i) > day_start_index):
                        match = False

            if match:
                dates.append(activity)

        print(*dates, sep='\n')

    @staticmethod
    def show_tomorow_classes(all_classes : PeActivities):
        today = date.today().weekday()
        today_date = date.today()
        tomorrow_date = today_date + timedelta(days=1)
        tomorrow = today + 1
        if today > 4:
            tomorrow_date = today_date + timedelta(days=7 - today)
            tomorrow = today + (7 - today)
        pattern = "Filia"
        date_pattern = r"(\d{2}[-./]\d{2}[-./]\d{4})"
        dates = [] # list with classes with dates

        if today >= 4:
            for i, activity in enumerate(all_classes.get_activities()):
                if all_classes.return_activity_index(i) == 0 and not re.search(pattern, all_classes.get_acivity(i)):
                    if re.search(date_pattern, all_classes.get_acivity(i)): 
                        dates.append(f"{activity}")
                    else:
                        dates.append(f"{activity} {tomorrow_date}")
        else:
            for i, activity in enumerate(all_classes.get_activities()):
                if all_classes.return_activity_index(i) == tomorrow and not re.search(pattern, all_classes.get_acivity(i)):
                    if re.search(date_pattern, all_classes.get_acivity(i)): 
                        dates.append(f"{activity}")
                    else:
                        dates.append(f"{activity} {tomorrow_date}")

        print(*dates, sep='\n')

def main():
   example_list = ["dzien itd",
                  "wtorek 18:50-20:20 P-23 2.0.17 siłownia Jan Kowalski",
                  "piątek 18:50-20:20 P-23 2.0.17 siłownia Piotr Nowak",
                  "poniedziałek 18:50-20:20 P-23 2.0.17 siłownia Błażej Andrzej 17.12.2024 odwołane"]
   example_activities = PeActivities()
   example_activities.add_list(example_list)
   #cancelled_classes = example_activities.find_cancelled()
   #UI.show_cancelled_classes(cancelled_classes)

   UI.show_upcoming_week(example_activities)

if __name__ == "__main__":
   main()