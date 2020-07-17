from PIL import Image
import threading
import os
import re
import fnmatch
import getopt
import sys


class Resizer:
    def __init__(self):
        self.__errors_list = {"error_1": "The path to the file / folder is specified incorrectly.",
                              "error_2": "Final resolution must be entered.",
                              "error_3": "Unable to create new folder."
                              }
        self.__images_folders_paths = []
        self.__images_objects_paths = []
        self.__final_resolution = None
        self.__postfix = None
        self.__new_folder = None
        self.__acceptable_file_extensions = "jpeg|jpg|png|txt|gif|bmp|tiff|exif|bat|webp"

    def __console(self):
        self.__postfix = None
        self.__new_folder = None
        if len(sys.argv) == 1:
            input_string = input(": ")
        else:
            separator = " "
            input_string = separator.join(sys.argv[1:])

        # try to get exit/quit key
        if re.search(r"(?:^| |\n|-)(?:exit|quit)(?:|\n|$)", input_string, re.IGNORECASE):
            quit()

        # try to get help key
        if re.search(r"(?:^| |\n|-)(?:help|\?)(?:|\n|$)", input_string, re.IGNORECASE):
            self.__print_help()
            return 1

        # get -r (resolution) key from input
        r_pattern = r"-r \d+ ?\D ?\d+"
        r_data = re.findall(r_pattern, input_string, re.IGNORECASE)
        if not r_data:
            print(self.__errors_list["error_2"])
            return -1
        # get -r values
        self.__final_resolution = tuple(map(int, re.findall(r"\d+", r_data[0], re.IGNORECASE)))

        # delete -r key from input_string
        input_string = re.sub(r_pattern, "", input_string, re.IGNORECASE)

        # get -p (postfix) key from input
        p_pattern = r"-p ?.*(?:$| )"
        p_data = re.findall(p_pattern, input_string)
        # get -p value if it exists
        if p_data:
            self.__postfix = p_data[0][2:]
            self.__postfix = self.__postfix.strip()
            # delete -p key from input_string
            input_string = re.sub(p_pattern, "", input_string, re.IGNORECASE)

        # get -nl (resized images new location) key from input
        nl_pattern = r"-nl ?(?:[a-zA-Z]:)?(?:[\\/]+[\w _-]+)*"
        nl_data = re.findall(nl_pattern, input_string, re.IGNORECASE)
        # get -nl value if it exists
        if nl_data:
            if nl_data[0][len(nl_data[0]) - 1] is '-':
                nl_data[0] = nl_data[0][:len(nl_data)-2]
            self.__new_folder = nl_data[0][3:]
            self.__new_folder = self.__new_folder.strip()

            # delete -nl key from input_string
            input_string = re.sub(nl_pattern, "", input_string, re.IGNORECASE)

        pattern = r"(?:[a-zA-Z]:[\\/])?(?:[\\/]?[\w -_]+)*(?:\.(?:{0}))?(?:\n| |$|\Z|\|)"
        pattern = pattern.format(self.__acceptable_file_extensions)

        input_data = re.findall(pattern, input_string, re.IGNORECASE)

        input_data = list(filter(lambda x: re.search(r"^ *$", x, re.IGNORECASE) == None, input_data))
        input_data = list(map(str.strip, input_data))

        file_pattern = r"\.(?:{0})$"
        file_pattern = file_pattern.format(self.__acceptable_file_extensions)

        # main input data processing loop
        for x in input_data:

            if re.search(file_pattern, x, re.IGNORECASE):
                self.__images_objects_paths.append(x)

            else:
                self.__images_folders_paths.append(x)

        # process all images
        for x in self.__images_objects_paths:
            log = self.__resize_images(x, self.__final_resolution, self.__new_folder)
            if log is not 0:
                return log

        # process all folders
        for x in self.__images_folders_paths:
            log = self.__resize_folders_images(x, self.__final_resolution)
            if log is not 0:
                return log
        # debug
        # input()
        return 0

    def start_console_listen(self, infinite=True):
        while True:

            log = self.__console()
            if log is -1:
                try:
                    print(self.__errors_list[log])
                except IndexError:
                    print("Unknown error. Try again.")

            elif log is not 0 and log is not 1:
                print(log)

            if not infinite:
                break

    def __resize_images(self, image_path, image_resolution, new_folder):

        try:
            image = Image.open(image_path)
        except IOError as e:
            print(type(e))
            return e
        image = image.resize(image_resolution, Image.ANTIALIAS)

        if new_folder:
            if not os.path.exists(self.__new_folder):
                try:
                    os.mkdir(self.__new_folder)
                except OSError as e:
                    return e

            pattern = r"[\\/][\w\s.,;#@'\"]+(?:\.\w+)?(?:$| )"
            image_name = re.findall(pattern, image_path, re.IGNORECASE)[0]
            image_name = image_name.strip()
            if new_folder[-1] is '\\' or new_folder[-1] is '/' or image_name[0] is '\\' or image_name[0] is '/':
                image_path = new_folder + image_name
            else:
                image_path = new_folder + re.search(r"[\\/]", new_folder).group(0) + image_name

        pattern = r".(?:{0})$"
        pattern = pattern.format(self.__acceptable_file_extensions)
        image_extension = re.search(pattern, image_path, re.IGNORECASE).group(0)

        new_pathname_end = ""
        if self.__postfix:
            if re.search(pattern, self.__postfix, re.IGNORECASE):
                new_pathname_end = self.__postfix
            else:
                new_pathname_end = self.__postfix + image_extension
        else:
            new_pathname_end = "_" + str(self.__final_resolution[0]) + \
                               " x" + str(self.__final_resolution[1]) + \
                               image_extension

        new_image_path = re.sub(pattern, new_pathname_end, image_path, re.IGNORECASE)

        try:
            image.save(new_image_path)
        except IOError as e:
            return e

        return 0

    def __resize_folders_images(self, folder_path, image_resolution):

        listdir = os.listdir(folder_path)
        images = []
        pattern = r"[\w\s]+.(?:{0})"
        pattern = pattern.format(self.__acceptable_file_extensions)
        for file in listdir:
            if re.search(pattern, file):
                images.append(os.path.join(folder_path, file))
        for image in images:
            log = self.__resize_images(image, self.__final_resolution, self.__new_folder)
            if log is not 0:
                return log
        return 0

    @staticmethod
    def __print_help():
        print("""Use: path(one or more) [options (-r is always required)] 
        Input files or folders with files one-by-one with space or comma separate. 
        use 'help' key to open this reference.
        use 'quit' or 'exit' key to close this program.
        use '-r' key for setting new (final) resolution.
        use '-p' key to set postfix for resized images. It also works if you need to change image extension.
        use '-nl' key to set new location for resized images.
        """)


# main code part
application = Resizer()
if len(sys.argv) == 1:
    application.start_console_listen()
else:
    application.start_console_listen(False)
