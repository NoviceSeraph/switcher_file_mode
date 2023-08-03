from chardet.universaldetector import UniversalDetector

import argparse
import fnmatch
import sys
import os


class switcher_service():


    def __init__(self) -> None:
        pass

    def switch_mode(self) -> bool:
        args = self.setup()        

        if args.Value == 'all':
            paths = self.find_required_files(args.Paths)
            print(paths)
            for path in paths:
                self.changes_in_file(args, path)
            return True

        if args.Value == 'one':
            path = args.Path
            self.changes_in_file(args, path)
            return True
    
    def setup(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--Mode', choices = ['N', 'G', 'O'], 
                            help = 'N - номер группы, G - название группы, O - свой вариант, при этом варианте нужно ввести наименование группы в other')
        parser.add_argument('--Value', choices = ['one', 'all'], 
                            help = "one - один файл, необходимо ввести путь к файлу в команду path, all - нужно ввести путь к файлу в команду paths")
        parser.add_argument('--Path')
        parser.add_argument('--Paths')
        parser.add_argument('--Other')
        args = parser.parse_args()
        return args
    
    def find_required_files(self, path_to_directory : str) -> list:
        list_names_directories = list()
        list_files_directories = list()
        pattern = "test_*.py"

        if os.path.exists(path_to_directory) == False:
            sys.exit()
        
        for names_directories in os.walk(path_to_directory):
            if names_directories[0].find("__pycache__") != -1:
                continue
            list_names_directories.append(names_directories[0])

        for names_directories in list_names_directories:
            for entry in os.listdir(names_directories):
                if fnmatch.fnmatch(entry, pattern) and os.path.exists(os.path.join(names_directories, entry)) == True:
                    list_files_directories.append(os.path.join(names_directories, entry))

        return list_files_directories

    def changes_in_file(self, args, path = None):
        detector = UniversalDetector()
        number = ''
        group = ''

        with open(path, "rb") as file:
            for line in file:
                detector.feed(line)
                if detector.done:
                    break

        with open(path, 'r', encoding = detector.result['encoding']) as file:
            data = file.readlines()

        with open(path, 'w', encoding = detector.result['encoding']) as file:
            for line in data:
                other = args.Other
                if args.Other == None:
                    other = ''
                if args.Mode == 'N':
                    if line.find("@decorators.workItemIds") != -1:
                        index = line.find("(")
                        number = line[index + 1:-2]
                        other = ''
                if args.Mode == 'G':     
                    if line.find("@decorators.suite") != -1:
                        index = line.rfind(":")
                        group = line[index + 1:-3]    
                        other = ''
                    if group == '':
                        group = "CommonGroup" 
                if line.find('@pytest.mark.xdist_group') != -1:
                    index = line.find("=")
                    result = line[0:index + 1] + '"' +  group + number + other + '"' + ')' + '\n'
                    file.write(result)
                    continue
                file.write(line)

                    
if __name__ == "__main__":
    switcher = switcher_service()
    switcher.switch_mode()

