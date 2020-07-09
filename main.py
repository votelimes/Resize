from PIL import Image
import threading
import os
import re
import fnmatch


class Resizer:
    def __init__(self):
        self.__images_folders_paths = []
        self.__images_objects_paths = []
        self.__final_resolution = (0, 0)
        self.__acceptable_file_extensions = "jpeg|jpg|png|txt|gif|bmp|tiff|exif|bat|webp"

    def __console(self):
        #input_string = input(": ")
        input_string = "r://test1.txt      r://test2.txt -ir 100x200 "
        pattern = r"(?:[a-zA-Z]:[\\\/])?(?:[\\\/]?[\w -]+)*(?:\.(?:{0}))?(?:\n| |$|\Z|\|)"
        pattern = pattern.format(self.__acceptable_file_extensions)

        input_data = re.findall(pattern, input_string)

        input_data = list(filter(lambda x: re.search(r"^ *$", x) == None, input_data))
        input_data = list(map(str.strip, input_data))

        file_pattern = r"\.({0})$"
        file_pattern = file_pattern.format(self.__acceptable_file_extensions)
        for x in input_data:

            if re.search(file_pattern, x):
                self.__images_objects_paths.append(x)

            elif re.search(r"^-ir \d+ ?\D ?\d+$", x):
                self.__final_resolution = re.findall(r"\d+", x)

            else:
                self.__images_folders_paths(x)
        for x in self.__images_objects_paths:
            self.__resize_images(x, self.__final_resolution)
        input()

    def start_console_listen(self):
        while(True):
            self.__console()

    def __resize_images(self, image_path, image_resolution):
        image = Image.open(image_path)
        image = image.resize(image_resolution, Image.ANTIALIAS)

        pattern = r".{0}"
        pattern = pattern.format(self.__acceptable_file_extensions)
        image_extension = re.match(pattern, image_path)
        new_image_path = re.sub(pattern,
        "_"+self.__final_resolution[0]+"x"+self.__final_resolution[1]+image_extension, image_path)
        del image_extension[0]

        image.save(new_image_path, image_extension)
    def __resize_folders_images(self):
        pass


# main code part
resizer = Resizer()
resizer.start_console_listen()
#image = Image.open("R:\\test1.jpg")
#image = image.resize((400, 100), Image.ANTIALIAS)
#image.save("R:\\test2.png", "PNG")
