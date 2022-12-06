# 🤖 OpenAI

Test OpenAI API

## DALL-E

```python
import openai

response = openai.Image.create(
  prompt="a funny corgi",
  n=1,
  size="512x512"
)
image_url = response['data'][0]['url']
```

![corgi](img/corgi.png)

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

## Resources:

* [DALL·E 2](https://openai.com/dall-e-2/)
* [DALL·E Editor Guide](https://help.openai.com/en/articles/6516417-dall-e-editor-guide)
* https://labs.openai.com/editor
