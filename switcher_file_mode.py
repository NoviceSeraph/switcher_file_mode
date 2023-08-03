from chardet.universaldetector import UniversalDetector

import argparse
import fnmatch
import sys
import os


class switcher_service():


    def __init__(self) -> None:
        parser = argparse.ArgumentParser()
        parser.add_argument('--Mode', choices = ['N', 'G', 'O'], 
                            help = 'N - номер группы, G - название группы, O - свой вариант, при этом варианте нужно ввести наименование группы в other')
        parser.add_argument('--Value', choices = ['one', 'all'], 
                            help = "one - один файл, необходимо ввести путь к файлу в команду path, all - нужно ввести путь к файлу в команду paths")
        parser.add_argument('--Path')
        parser.add_argument('--Paths')
        parser.add_argument('--Other')
        self.args = parser.parse_args()

    def switch_mode(self) -> bool:
        if self.args.Value == 'all':
            paths = self.find_required_files()
            for path in paths:
                self.changes_in_file(path)
            return True

        if self.args.Value == 'one':
            path = self.args.Path
            self.changes_in_file(path)
            return True
    
    def find_required_files(self) -> list:
        list_names_directories = list()
        list_files_directories = list()
        pattern = "test_*.py"

        if os.path.exists(self.args.Paths) == False:
            sys.exit()
        
        for names_directories in os.walk(self.args.Paths):
            if names_directories[0].find("__pycache__") != -1:
                continue
            list_names_directories.append(names_directories[0])

        for names_directories in list_names_directories:
            for entry in os.listdir(names_directories):
                if fnmatch.fnmatch(entry, pattern) and os.path.exists(os.path.join(names_directories, entry)) == True:
                    list_files_directories.append(os.path.join(names_directories, entry))

        return list_files_directories

    def changes_in_file(self, path = None):
        detector = UniversalDetector()

        with open(path, "rb") as file:
            for line in file:
                detector.feed(line)
                if detector.done:
                    break

        with open(path, 'r', encoding = detector.result['encoding']) as file:
            data = file.readlines()

        with open(path, 'w', encoding = detector.result['encoding']) as file:
            change = self.args.Other
            if self.args.Other == None:
                change = ''
            latch = False
            for line in data:
                if latch == False:
                    if self.args.Mode == 'N':
                        if not line.find("@decorators.workItemIds"):
                            change = line[line.find("(") + 1:-2]
                    if self.args.Mode == 'G':     
                        if not line.find("@decorators.suite"):
                            change = line[line.rfind(":") + 1:-3]    
                        if change == '':
                            change = "CommonGroup" 
                if not line.find('@pytest.mark.xdist_group'):
                    line = line[0:line.find("=") + 1] + '"' +  change + '"' + ')' + '\n'
                    latch = True
                file.write(line)

                    
if __name__ == "__main__":
    switcher = switcher_service()
    switcher.switch_mode()

