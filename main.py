# Press ⌃R to execute script
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

from openai import OpenAI
import random
# import cv2
from PIL import ImageDraw, ImageFont
from PIL import Image as myImage
import string

import requests
from IPython.display import Image, display
import webbrowser

def get_image(prompt: str):
    client = OpenAI()

    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )

    image_url = response.data[0].url

    return image_url


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # image_url = get_image('a white siamese cat')

    # display(Image(url=image_url)) # might open the image here locally
    # webbrowser.open(image_url) # Open URL in a new tab, if a browser window is already open.

    # random number generator
    my_verse = random.randint(1, 6236)
    print("verse number:", my_verse)

    # getting the random ayah in arabic
    response_arabic = requests.get("http://api.alquran.cloud/v1/ayah/" + str(my_verse))
    data = response_arabic.json()
    final_quran_verse_arabic = str(data['data']['text'])
    print("english verse from api:", final_quran_verse_arabic)

    # using quran api to get a random ayah in english
    response = requests.get("http://api.alquran.cloud/v1/ayah/" + str(my_verse) + "/en.asad")
    data = response.json()
    final_quran_verse = data['data']['text']
    print("english verse from api:", final_quran_verse)

    # getting the random ayah's information

    img = myImage.open('generated_images/generated_image.png')
    draw = ImageDraw.Draw(img)
    font_size = 50
    font = ImageFont.truetype('AalmaghribiQuran.ttf', font_size)

    # calculating where we need to wrap text
    words = final_quran_verse.split(' ')

    # print("words:", words)

    line_width_pre = 0
    line_text_pre = ""
    max_width_pre = 1024 - 100
    position_pre = (50, (1024 / 2) - 25)
    line_counter = 0

    # TODO: make it interactive so that i have to confirm the generated text/image and if it doesnt produce a good one i can regenerate it.
    #  Also I need to get the name of the chapter and #:# associated with it
    #   Then I need to make the prompt of the generation exclude haram images such as depiction of faces and other things that are not allowed in islam
    #   in the end all i need to click is two buttons. one that regenerates text/image and the other that regenerates the image

    for word_pre in words:
        # Get the width and height of the current word
        word_width_pre = draw.textlength(word_pre, font=font)

        # Check if adding the current word exceeds the maximum width
        if line_width_pre + word_width_pre <= max_width_pre:
            # Add the word to the current line
            line_text_pre += word_pre + " "
            line_width_pre += word_width_pre
        else:
            line_counter += 1

    print("line text pre:", line_text_pre)
    # if there is a left over line then add one to the counter
    if line_text_pre != "":
        line_counter += 1

    print("line_counter:", line_counter)

    line_width = 0
    line_text = ""
    max_width = 1024 - 100
    position = (50, (1024 / 2) - 25)

    for word in words:
        # Get the width and height of the current word
        word_width = draw.textlength(word, font=font)

        # Check if adding the current word exceeds the maximum width
        if line_width + word_width <= max_width:
            # Add the word to the current line
            line_text += word + " "
            line_width += word_width
        else:
            # drawing border
            draw.text((position[0] - 2, position[1] - 2), line_text, font=font, fill='black')
            draw.text((position[0] + 2, position[1] - 2), line_text, font=font, fill='black')
            draw.text((position[0] - 2, position[1] + 2), line_text, font=font, fill='black')
            draw.text((position[0] + 2, position[1] + 2), line_text, font=font, fill='black')

            # Draw the current line and reset variables for the new line
            draw.text(position, line_text, font=font)

            # position = (position[0], position[1] + font.getsize(line_text)[1])
            position = (position[0], position[1] + font_size + 8)
            line_text = word + " "
            line_width = word_width

    # drawing black border
    draw.text((position[0] - 2, position[1] - 2), line_text, font=font, fill='black')
    draw.text((position[0] + 2, position[1] - 2), line_text, font=font, fill='black')
    draw.text((position[0] - 2, position[1] + 2), line_text, font=font, fill='black')
    draw.text((position[0] + 2, position[1] + 2), line_text, font=font, fill='black')

    # draw.text((10, 1024/2), final_quran_verse, font=font, fill=(255, 255, 0))
    draw.text(position, line_text, font=font, fill='white')

    # getting random characters to append to file name
    characters = string.ascii_letters + string.digits

    random_string = ''.join(random.choice(characters) for i in range(5))

    img.save('generated_images/generated_image' + random_string + '.png')








