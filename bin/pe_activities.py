import re
from datetime import *

class PeActivities:
    """Class stores all lessons in a list as strings"""
    def __init__(self):
        self.activities : str = []

    def add_activities(self, activity : str) -> None:
        self.activities.append(activity)   

    def add_list(self, lines_list: list) -> None:
        """Add to a list with regex formula"""
        date : str = None
        current_day : str = None
        pattern_days = r"poniedziałek|wtorek|środa|czwartek|piątek"
        pattern_2 = r'^[ABCDE]'
        pattern_3 = r"(\d{2}:\d{2})-(\d{2}:\d{2})"
        pattern_4 = r"-1-.."
        pattern_5 = r"[HP]\-[12][3-4][A-E]"
        date_pattern = r"(\d{2}[-./]\d{2}[-./]\d{4}) \((poniedziałek|wtorek|środa|czwartek|piątek|sobota|niedziela)\)"

        for current_line in lines_list:
            current_line = current_line.strip()

            match = re.search(date_pattern, current_line)
            if match:
                date = match.group(1)
                current_day = match.group(2)

            if re.search(pattern_days, current_line) and not re.search(date_pattern, current_line):  
                self.add_activities(f"{current_line}")
            
            if re.search(pattern_2, current_line) and re.search(pattern_3, current_line):
                current_line = re.sub(pattern_5, lambda m: m.group()[4], current_line)
                current_line = re.sub(pattern_2,"P-23", current_line)
                current_line = re.sub(pattern_4,"H-14", current_line)               
                self.add_activities(f"{current_day} {current_line} {date}")


    
    def print_activities(self) -> None:
        print(*self.activities, sep ="\n")

    def find_cancelled(self) -> list:
        """Find cancelled lessons"""
        pattern : str= "odwołane"
        pattern_2 : str = r"\d{2}.\d{2}.\d{4}"

        deleted_pe_activities : PeActivities = []

        for i in range(0, len(self.activities)): 
            current_line = self.activities[i]
            previous_line = self.activities[i - 1]
            
            if re.search(pattern, current_line):
                if len(current_line) > len(pattern):
                    deleted_pe_activities.append(current_line)
            
            elif re.search(pattern_2, current_line):
                text_with_date : str =  previous_line + " " + current_line  
                deleted_pe_activities.append(previous_line)
        
        return deleted_pe_activities
    
    def return_activity_index(self, i : int) -> int:
        """Return value, that depends on what day it is. Same way as it is in the "date" library - weekday() method"""
        patterns = {"poniedziałek" : 0, "wtorek" : 1, 
                    "środa" : 2, "czwartek" : 3, "piątek" : 4}
        for key, value in patterns.items():
            if re.search(key, self.activities[i]):
                return value
                
    def get_activities(self) -> list:
        return self.activities
    
    def get_acivity(self, i : int) -> str:
        return self.activities[i]
    
    def get_time(self, i : int) -> list:
        """Return list of two elements. Elements are: start and the end of lesson."""
        pattern = r"(\d{2}:\d{2})-(\d{2}:\d{2})"
        match = re.search(pattern, self.activities[i])
        return match.groups() if match else []
       
def main():
    example = PeActivities()
    example.add_activities("Przykładowe zajęcia odwołane")
    example.add_activities("poniedziałek 18:50-20:20 P-23 2.0.17 siłownia Banaszczyk Grzegorz 16.12.2024 odwołane")
    example.add_activities("Trening siłowy")
    #print(*example.find_cancelled(), sep='\n')
    example.get_time(1)


if __name__ == "__main__":
   main()