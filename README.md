# 🤖 OpenAI

Test OpenAI API

```python
import openai

response = openai.Image.create(
  prompt="a funny corgi",
  n=1,
  size="1024x1024"
)
image_url = response['data'][0]['url']
```

![corgi](img/corgi.png)