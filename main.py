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
                              "error_2": "Error 2. Final resolution must be entered.",
                              }
        self.__images_folders_paths = []
        self.__images_objects_paths = []
        self.__final_resolution = None
        self.__postfix = None
        self.__acceptable_file_extensions = "jpeg|jpg|png|txt|gif|bmp|tiff|exif|bat|webp"

        # Input parameters flags
        self.__fm = False  # format key flag

    def __console(self):
        self.__fm = False
        self.__postfix = None
        if len(sys.argv) == 1:
            input_string = input(": ")
        else:
            separator = " "
            input_string = separator.join(sys.argv[1:])
        #input_string = "r://test1.txt      r://test2.txt  -r 100 200" # debug

        # try to get exit/quit key
        if re.search(r"(?:^| |\n|-)(?:exit|quit)(?:|\n|$)", input_string, re.IGNORECASE):
            quit()

        # try to get help key
        if re.search(r"(?:^| |\n|-)(?:help|\?)(?:|\n|$)", input_string, re.IGNORECASE):
            self.__print_help()
            return 1

        # get -r (resolution) key from input
        ir_pattern = r"-r \d+ ?\D ?\d+"
        ir_data = re.findall(ir_pattern, input_string)
        if not ir_data:
            print(self.__errors_list["error_2"])
            return -2
        # get -r values
        self.__final_resolution = tuple(map(int, re.findall(r"\d+", ir_data[0], re.IGNORECASE)))

        # delete -r key from input_string
        input_string = re.sub(ir_pattern, "", input_string, re.IGNORECASE)

        # get -p (postfix) key from input
        p_pattern = r"-p ?.*(?:$| )"
        p_data = re.findall(p_pattern, input_string)
        # get -p value if it exists
        if p_data:
            self.__postfix = p_data[0][2:]
            self.__postfix = self.__postfix.strip()
            # delete -p key from input_string
            input_string = re.sub(p_pattern, "", input_string, re.IGNORECASE)

        pattern = r"(?:[a-zA-Z]:[\\\/])?(?:[\\\/]?[\w -]+)*(?:\.(?:{0}))?(?:\n| |$|\Z|\|)"
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
            self.__resize_images(x, self.__final_resolution)

        # process all folders
        for x in self.__images_folders_paths:
            self.__resize_folders_images(x, self.__final_resolution)

        # debug
        # input()

    def start_console_listen(self, infinite=True):
        while True:
            self.__console()
            if not infinite:
                break

    def __resize_images(self, image_path, image_resolution):
        image = Image.open(image_path)
        image = image.resize(image_resolution, Image.ANTIALIAS)

        pattern = r".(?:{0})$"
        pattern = pattern.format(self.__acceptable_file_extensions)
        image_extension = re.search(pattern, image_path, re.IGNORECASE).group(0)

        new_pathname_end = ""
        if self.__postfix:
            new_pathname_end = self.__postfix + image_extension
        else:
            new_pathname_end = "_" + str(self.__final_resolution[0]) + \
                               "x" + str(self.__final_resolution[1]) + \
                               image_extension

        new_image_path = re.sub(pattern, new_pathname_end, image_path, re.IGNORECASE)

        if self.__fm is not False:
            image.save(new_image_path, image_extension[1:])
        elif self.__fm is False:
            image.save(new_image_path)

    def __resize_folders_images(self, folder_path, image_resolution):

        listdir = os.listdir(folder_path)
        images = []
        pattern = r"[\w\s]+.(?:{0})"
        pattern = pattern.format(self.__acceptable_file_extensions)
        for file in listdir:
            if re.search(pattern, file):
                images.append(os.path.join(folder_path, file))
        for image in images:
            self.__resize_images(image, self.__final_resolution)
        return 0

    @staticmethod
    def __print_help(self):
        print("""Use: path(one or more) [-r [dec] [dec]] 
        Input files or folders with files one-by-one with space or comma separate. 
        use 'help' key to open this reference.
        use 'quit' or 'exit' ket to close this program.
        use '-r' key for setting new resolution.
        use '-k' key to set postfix for resized images.
        """)


# main code part
application = Resizer()
if len(sys.argv) == 1:
    application.start_console_listen()
else:
    application.start_console_listen(False)
