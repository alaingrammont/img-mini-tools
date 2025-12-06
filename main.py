import argparse,re
from pathlib import Path
from dataclasses import dataclass, field
from PIL import Image

# Positional Arguments ============================================//
parser = argparse.ArgumentParser()
parser.add_argument("image_input", 
	type= Path, 
	help= "path of the image to be analyzed"
)

parser.add_argument("image_output",
	type= Path,
	help= "path of the analyzed image"
)

# Optionals Arguments =============================================// 
parser.add_argument("--re-write",
	action= "store_true",
	help= "Rewrite the output image if it exists"
)

parser.add_argument("--crop",
	action= "store_true",
	help= "Returns a minimum rectangle containing all pixels whose alpha > 0"
) 

parser.add_argument("--re-size",
	type= int,	nargs= 2,
	metavar= ('WIDTH','HEIGHT'),
	help= "resize the image to the specified dimensions"
) 

parser.add_argument("--aspect-ratio",
	type= str,
	metavar= "WIDTH:HEIGHT",
	help= "Resize de the image to a specific aspect ratio without distorting it."
)
args = parser.parse_args()


# Positional Arguments Validation =================================// 
if not args.image_input.exists():
	raise FileNotFoundError(f"File not found: {args.image_input}")

extensions = [".ico",".png",".jpg",".jpeg",".webp"]
if not args.image_input.suffix in extensions:
	raise ValueError(
		f"The uploaded file is not compatible\n"
		f"	Input Route: {args.image_input}\n"
		f"	Supported Extensions: {extensions}"
	)

if not args.image_output.suffix in extensions:
	raise ValueError(
		f"The uploaded file is not compatible\n"
		f"	Output Route: {args.image_output}\n"
		f"	Supported Extensions: {extensions}"
	)


# Application Code ================================================//
img = Image.open(args.image_input)

if args.crop:
	img = img.convert("RGBA")
	alpha = img.split()[-1]
	bbox = alpha.getbbox()
	img = img.crop(bbox)

if args.aspect_ratio:
	aspect_s = args.aspect_ratio.split(":")
	aspect_w = int(aspect_s[0])
	aspect_h = int(aspect_s[1])

	w, h = img.size
	desired_ratio = aspect_w / aspect_h
	current_ratio = w / h
	
	if current_ratio > desired_ratio:
		# La imagen es "muy ancha": recortamos lados
		new_width = int(h * desired_ratio)
		offset = (w - new_width) // 2
		box = (offset, 0, offset + new_width, h)
	else:
		# La imagen es "muy alta": recortamos arriba/abajo
		new_height = int(w / desired_ratio)
		offset = (h - new_height) // 2
		box = (0, offset, w, offset + new_height)

	# Recortar
	img = img.crop(box)

if args.re_size:
	img = img.resize(tuple(args.re_size))

if args.image_output.exists() and not args.re_write:
	response = input("there is already an image with the same path. Do you want to rewrite the file?(Y/n): ")
	if response.lower() not in ("y","yes"):
		exit(0)

image_format = re.search(r"\w+",args.image_output.suffix).group().upper()
image_format = "JPEG" if image_format == "JPG" else image_format
img.save(args.image_output,format=image_format)
