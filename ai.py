import requests
import os
import base64
from openai import OpenAI
import PIL


api_key = str(os.getenv('OPENKEY001', default=None))
org = str(os.getenv('OPENORG', default=None))
client = OpenAI(api_key=api_key, organization=org)


def encode_image(image=None):
    with open(image, 'rb') as file:
        return base64.b64encode(file.read()).decode('utf-8')

def get_ig_caption(image=None):
    base64_image = encode_image(image=image)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user",
            "content": [
                 {"type": "text", "text": "Write an instagram caption for this image. Use between six and eight appropriate hashtags."},
                {
                     "type": "image_url",
                    "image_url": {
                         "url": f"data:image/jpeg;base64,{base64_image}",
                        "detail": "low"
                    }
                }
            ]}
        ],
        max_tokens=300,
        temperature=0,
    )
    return response

    #to_print = response.choices[0].message.content
    #print(f'RESPONSE:\n\n {to_print}\n\n')
