from PIL import Image
import threading
import os
import re
import fnmatch


class Resizer:
    def __init__(self):
        self.__errors_list = {"error_1": "The path to the file / folder is specified incorrectly.",
                              "error_2": "Error 2. Final resolution must be entered.",
                              }
        self.__images_folders_paths = []
        self.__images_objects_paths = []
        self.__final_resolution = None
        self.__acceptable_file_extensions = "jpeg|jpg|png|txt|gif|bmp|tiff|exif|bat|webp"

        # Input parameters flags
        self.__fm = False  # format key flag

    def __console(self):
        self.__fm = False
        input_string = input(": ")
        #input_string = "r://test1.txt      r://test2.txt  -ir 100 200"

        # get -ir key from input
        ir_pattern = r"-ir \d+ ?\D ?\d+"
        ir_data = re.findall(ir_pattern, input_string)
        if not ir_data:
            print(self.__errors_list["error_2"])
            return 2
        # get -ir values
        self.__final_resolution = tuple(map(int, re.findall(r"\d+", ir_data[0], re.IGNORECASE)))

        # delete -ir key from input_string
        input_string = re.sub(ir_pattern, "", input_string, re.IGNORECASE)

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

            elif re.search(r"^help$", x, re.IGNORECASE):
                self.__print_help()
                return 1
            elif re.search(r"^(?:exit|quit)$", x, re.IGNORECASE):
                quit()
            else:
                self.__images_folders_paths.append(x)
        for x in self.__images_objects_paths:
            self.__resize_images(x, self.__final_resolution)
        for x in self.__images_folders_paths:
            self.__resize_folders_images(x, self.__final_resolution)
        input()

    def start_console_listen(self):
        while(True):
            self.__console()

    def __resize_images(self, image_path, image_resolution):
        image = Image.open(image_path)
        image = image.resize(image_resolution, Image.ANTIALIAS)

        pattern = r".(?:{0})$"
        pattern = pattern.format(self.__acceptable_file_extensions)
        image_extension = re.search(pattern, image_path, re.IGNORECASE).group(0)
        new_image_path = re.sub(pattern,
        "_" + str(self.__final_resolution[0]) + "x" + str(self.__final_resolution[1])
                                + image_extension, image_path, re.IGNORECASE)

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

    def __print_help(self):
        print("""Use: path(one or more) [-ir [dec] [dec]] 
        Input files or folders with files one-by-one with space or comma separate. 
        use 'help' key to open this reference.
        use 'quit' or 'exit' ket to close this program.
        use '-ir' key for setting new resolution.
        """)


# main code part
resizer = Resizer()
resizer.start_console_listen()
#image = Image.open("R:\\test1.jpg")
#image = image.resize((400, 100), Image.ANTIALIAS)
#image.save("R:\\test2.png", "PNG")
