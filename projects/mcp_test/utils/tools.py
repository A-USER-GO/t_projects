from langchain_openai import OpenAI, ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from openai import OpenAI
from PIL import Image
from io import BytesIO
import requests


# 1. 使用 LangChain 优化提示词（可选）
def refine_prompt(raw_prompt: str) -> str:
    """
    通过 LangChain 的链式调用优化原始提示词
    """
    template = ChatPromptTemplate.from_messages([
        ("system", "你是一个提示词优化助手，为 DALL-E 3 生成更详细的描述。"),
        ("user", "原始描述：{input}")
    ])
    llm = ChatOpenAI(model='gpt-3.5-turbo')

    chain = template | llm | StrOutputParser()
    refined_prompt = chain.invoke({"input": raw_prompt})
    return refined_prompt


# 2.
def generate_image(prompt: str, save_path:str = "./output.png") -> bytes:
    """
    调用 DALL-E 3 生成图片
    """
    try:
        # 配置 OpenAI 客户端
        client = OpenAI()
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="hd",
            n=1
        )
        image_url = response.data[0].url

        # 下载图片
        image_data = requests.get(image_url).content
        image = Image.open(BytesIO(image_data))
        image.save(save_path)
        return image_data

    except Exception as e:
        print(f"生成失败: {str(e)}")
        return None


def text_convert_images_tool(text: str) -> bytes:
    """文字转图片工具"""

    refined_prompt = refine_prompt(text)
    print(f"优化后的提示词: {refined_prompt}")

    # 生成并显示图片
    return generate_image(refined_prompt)