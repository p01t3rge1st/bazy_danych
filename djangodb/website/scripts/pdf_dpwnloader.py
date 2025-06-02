import requests
from pypdf import PdfReader
import re
import os

class Pdf_menager:
    """A class used to represent PDF menager 
    """
    user_agent = "scrapping_script/1.0"
    headers = {'User-Agent': user_agent}
    urls = [
        "https://swfis.pwr.edu.pl/fcp/JGBUKOQtTKlQhbx08SlkTWwVQX2o8DAoHNiwFE1xVSXhXFVZpCFghUHcKVigEQUw/81/public/konsultacje/fakultety_24l.pdf"
    ]
    reader : PdfReader
    path : str = "/Users/" + os.getlogin() + "/Desktop/fakultetZima.pdf"

    @classmethod
    def get_info(cls) -> None:
        """Sends HTTP request to a server"""
        for url in cls.urls:
                r = requests.get(url, headers=cls.headers, stream=True)
                if r.status_code == 200:
                    with open(cls.path, "wb") as fd:
                        fd.write(r.content)

#'/Users/micha/Desktop/fakultetZima.pdf'
    @classmethod
    def download(cls) -> None:
        """Download a document"""
        cls.reader = PdfReader(cls.path)

    @classmethod
    def convert_to_text(cls) -> str:
        """Extract text from PDF file"""
        count = cls.reader.get_num_pages()
        text : str = ""
        for i in range(count):
            page = cls.reader.pages[i]
            text += page.extract_text()
        return cls.pa4(text)
    
    @classmethod
    def remove_file(cls) -> None:
        """Erase the file from OS"""
        if os.path.exists(cls.path):
            os.remove(cls.path)
        else:
            print("The file does not exist")

    @classmethod
    def parse_classes(cls, text):
        result = []
        lines = text.splitlines()
        for line in lines:
            if not line.strip():
                continue
            parts = line.split()
            if len(parts) < 6:
                continue
            day = parts[0]
            time = parts[1]
            building = parts[2]
            room = parts[3]
            discipline = parts[4]
            instructor = parts[5]
            notes = " ".join(parts[6:]) if len(parts) > 6 else ""
            result.append({
                "day": day,
                "time": time,
                "building": building,
                "room": room,
                "discipline": discipline,
                "instructor": instructor,
                "notes": notes
            })
        return result
    
    @classmethod
    def run(cls):
        cls.get_info()
        cls.download()
        text = cls.convert_to_text()
        data = cls.parse_classes(text)
        cls.remove_file()
        return data

def main() -> None:
    Pdf_menager.get_info()
    Pdf_menager.download()
    text = Pdf_menager.convert_to_text()
    print(text)
    print('\n')
    Pdf_menager.remove_file()
    

if __name__ == "__main__":
    main()