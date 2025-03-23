from langchain.schema import SystemMessage
from langchain.prompts import ChatPromptTemplate
from langchain.chains import TransformChain, LLMChain


def create_aggregation_chain(llm):
    # 聚合结果处理
    def transform_results(inputs: dict) -> dict:
        raw_data = inputs["raw_results"]
        aggregated = []
        for source, content in raw_data.items():
            aggregated.append(f"## {source.upper()} RESULTS:\n{content}")
        return {"aggregated_text": "\n\n".join(aggregated)}

    transform_chain = TransformChain(
        input_variables=["raw_results"],
        output_variables=["aggregated_text"],
        transform=transform_results
    )

    # 摘要生成
    summary_prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content="你是一个专业的内容摘要助手"),
        ("user",
         "请根据以下聚合结果生成简洁摘要：\n"
         "{aggregated_text}\n"
         "要求：用中文输出，不超过200字"
         )
    ])
    summary_chain = LLMChain(llm=llm, prompt=summary_prompt)

    return transform_chain | summary_chain