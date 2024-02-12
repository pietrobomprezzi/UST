#--------------CONVERTING TO GIFS
from PIL import Image
import os
import imageio



# quarter + jan 15 military comm %GDP

#convert to gif

def create_gif(folder_path, output_gif_path, fps= 1,loop=1):
    images = []

    # Get the list of JPG files in the folder
    jpg_files = [f for f in os.listdir(folder_path) if f.endswith('.jpg')]

    # Sort the files to ensure correct order
    sorted_list = sorted(jpg_files, key=lambda x: int(x.split('_')[0]))

    # Read each image and append to the list
    for jpg_file in sorted_list:
        image_path = os.path.join(folder_path, jpg_file)
        images.append(imageio.imread(image_path))

    # Create the GIF
    imageio.mimsave(output_gif_path, images, fps=fps,loop=loop)

#military comm maps gdp
folder_path = "output/twitter"
output_gif_path = "output/FOR_CT.gif"
create_gif(folder_path, output_gif_path)

