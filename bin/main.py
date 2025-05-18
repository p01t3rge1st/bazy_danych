import requests
from pypdf import PdfReader
import re
import pandas as pd
from pdf_menager import Pdf_menager
from pe_activities import PeActivities
from ui import UI
from db_menager import dbMenager

def main():
    Pdf_menager.get_info()
    Pdf_menager.download()
    text = Pdf_menager.convert_to_text()

    lines_list = text.splitlines()

    #print(*lines_list, sep='\n')

    all_pe_activities : PeActivities = PeActivities()

    all_pe_activities.add_list(lines_list)

    #all_pe_activities.print_activities()

    #UI.show_cancelled_classes(all_pe_activities.find_cancelled())

    #UI.show_upcoming_week(all_pe_activities)
    #UI.show_tomorow_classes(all_pe_activities)
    #UI.filtering(all_pe_activities,place="P-23",day="wtorek",day_end="czwartek")
    #UI.filtering(all_pe_activities,place="P-23", day="wtorek",time="8:00", time_end="9:00")
    UI.filtering(all_pe_activities,place="H-14", day="czwartek",time="16:00",name="ergometry")

    Pdf_menager.remove_file()

if __name__ ==  "__main__":
    main()

