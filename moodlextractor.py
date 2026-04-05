import requests
from bs4 import BeautifulSoup
import base64
import mimetypes
from io import BytesIO
from copy import copy
from PIL import Image
import re
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-name", help="Name of file with exported questions that script will generate.", type=str)
parser.add_argument("-url", help="URL pointing to the question bank page.", type=str)
parser.add_argument("-quality", help="Quality of image (in percent).", type=int)
parser.add_argument("-sesskey", help="Moodle sesskey.", type=str)
parser.add_argument("-session", help="Moodle session from cookies.", type=str)

args = parser.parse_args()

cookies = {
    'MoodleSession': args.session,
}

files = {
    'sesskey': (None, args.sesskey),
    'fill': (None, 'Fill in correct responses'),
}

questions_page = requests.get(args.url, cookies=cookies)

soup = BeautifulSoup(questions_page.text, "lxml")
elements = soup.find_all('a')

links = [e.get('href') for e in elements if isinstance(e.get('href'), str)]

root_document = None

c = 0
for link in links:
    if 'question/preview.php' in link:
       c += 1
       print(c)
       question = requests.get(link, cookies=cookies)
       
       response_form = BeautifulSoup(question.text, "lxml").css.select_one('form#responseform')
       try:
           answer_url = response_form.attrs['action']
           answer = requests.post(answer_url, cookies=cookies, files=files)
           
           soup = BeautifulSoup(answer.text, "lxml")
           
           for img in soup.find_all('img'):
               img_src = img.attrs['src']

               if not img_src.startswith('http'):
                   continue

               mimetype = mimetypes.guess_type(img_src)[0]
               original_image = requests.get(img_src, cookies=cookies).content
               
               try:
                   question_img = Image.open(BytesIO(original_image))
                   compressed_image = BytesIO()
                   try:
                       question_img.save(compressed_image, format="JPEG", quality=args.quality, optimize=True)
                   except OSError:
                       rgb_im = question_img.convert('RGB')
                       rgb_im.save(compressed_image, format="JPEG") # вернуть quality и optimize
                   
                   img_b64 =  base64.b64encode(compressed_image.getvalue())

                   img.attrs['src'] = \
                       "data:%s;base64,%s" % (mimetype, img_b64.decode('utf-8'))
               except:
                    pass
       except Exception as e:
           print(e)
       if root_document == None:   
           div_techinfosizer = soup.find('div', id='techinfo_sizer'); div_techinfosizer.decompose()
           div_techinfo = soup.find('div', id='techinfo'); div_techinfo.decompose()
           div_info = soup.find('div', class_='info'); div_info.decompose()
           div_previewcontrols = soup.find('div', id='previewcontrols'); div_previewcontrols.decompose()
           div_previewcontrols = soup.find('form', 
                attrs={"action": lambda x: x and x.endswith("question/preview.php")}
           ); 
           div_previewcontrols.decompose()

           some_bullshit_link = soup.find('a', text='Download this question in Moodle XML format'); some_bullshit_link.decompose()
           
           for tag in soup.find_all('script'):
               tag.decompose()
           root_document = copy(soup)
       else:
           main_document_section = root_document.find('div', class_='content');
           new_section = soup.find('div', class_='content');
           main_document_section.insert_after(new_section)       
       f = open(f'{args.name}.html', 'w', encoding = 'utf-8')
       f.write(str(root_document))
       f.flush()

f.close()
