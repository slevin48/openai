# 🤖 DALL-E

```python
import openai

response = openai.Image.create(
  prompt="a funny corgi in a cartoon style",
  n=1,
  size="512x512"
)
image_url = response['data'][0]['url']
```

![corgi](img/funny%20corgi%20in%20a%20cartoon%20style.png)

## Image processing

Call to OpenAI API requires png image of the right size (e.g. 512x512). 

Two options to crop image:

### Streamlit app

https://github.com/turner-anderson/streamlit-cropper

![cropper](img/cropper_app.jpg)

### MATLAB Image tool

https://www.mathworks.com/help/images/ref/imageviewer-app.html

![imtool](img/imtool.jpg)

## Image variation

![](img/dechargement0.png)

![](img/dechargement1.png)

![](img/dechargement2.png)

![](img/dechargement3.png)

![](img/dechargement4.png)

## Inpainting

![](img/supermario.jpg)

## Resources:

* [DALL·E 2](https://openai.com/dall-e-2/)
* [DALL·E Editor Guide](https://help.openai.com/en/articles/6516417-dall-e-editor-guide)
* https://labs.openai.com/editor
* [RealPython tuto](https://realpython.com/generate-images-with-dalle-openai-api/)
* [Panel OpenAI](https://github.com/sophiamyang/panel_openai) + [tuto](https://towardsdatascience.com/chatgpt-and-dall-e-2-in-a-panel-app-1c921d7d9021)
* [PaintAI](https://github.com/DaanBio/printAI)
