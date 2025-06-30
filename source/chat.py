from ollama import chat
from retriever import Retriever
from data_loader import load_meta_corpus
from typing import List, Dict
from openai import OpenAI

from dotenv import load_dotenv
import os
import sys

load_dotenv()

prompt_template = (
    """###Yêu cầu: Bạn là một trợ lý AI chuyên tư vấn về pháp luật giao thông đường bộ tại Việt Nam. Nhiệm vụ của bạn là cung cấp câu trả lời dựa trên thông tin được trích xuất từ văn bản pháp luật. Khi nhận được dữ liệu truy xuất từ RAG, hãy:

    1. Phân tích kỹ lưỡng dữ liệu để trả lời chính xác và đúng trọng tâm câu hỏi của người dùng. Chỉ trả lời dựa trên dữ liệu được cung cấp, không suy diễn hoặc đưa ra thông tin không có trong văn bản.
    2. Trình bày thông tin một cách rõ ràng, mạch lạc và dễ hiểu. Nếu có các mức phạt hoặc quy định cụ thể, hãy nêu rõ.
    3. Trả lời với giọng điệu trung lập, chính xác như một chuyên gia tư vấn pháp luật.
    4. Nếu dữ liệu truy xuất không chứa thông tin liên quan đến câu hỏi hoặc không có dữ liệu nào được truy xuất, hãy trả lời: "Xin lỗi, tôi không tìm thấy thông tin pháp lý phù hợp để trả lời câu hỏi này."
    5. Nếu câu hỏi không liên quan đến chủ đề pháp luật giao thông Việt Nam (out-domain), hãy lịch sự giới thiệu lại lĩnh vực chuyên môn của mình.
    6. Trả lời câu hỏi bằng ngôn ngữ: {language}

    ###Dựa vào một số ngữ cảnh được trích xuất dưới đây, nếu bạn thấy chúng liên quan đến câu hỏi, hãy sử dụng để trả lời câu hỏi ở cuối.
    {input}
    ###Câu hỏi từ người dùng: {question}
    ###Hãy trả lời chi tiết và đầy đủ dựa trên ngữ cảnh được cung cấp nếu thấy có liên quan. Nếu không, hãy tuân thủ các quy tắc đã nêu trên."""
)


def get_prompt(question, contexts, language):
    context = "\n\n".join([f"Context [{i+1}]: {x['passage']}" for i, x in enumerate(contexts)])
    input = f"\n\n{context}\n\n"
    prompt = prompt_template.format(
        input=input,
        question=question, 
        language=language
    )
    return prompt

def classify_small_talk(input_sentence, language):
    prompt = f"""
    ###Yêu cầu: Bạn là một trợ lý hữu ích được thiết kế để phân loại các câu hỏi của người dùng trong ngữ cảnh của một chatbot về Pháp luật Giao thông Việt Nam. Nhiệm vụ của bạn là xác định liệu câu hỏi của người dùng có phải là "small talk" (chào hỏi, cảm ơn, hỏi thăm ngoài lề) hay không.
    ###"Small talk" đề cập đến những chủ đề trò chuyện thông thường, không liên quan trực tiếp đến các quy định, luật lệ, mức phạt trong giao thông Việt Nam.
    - Nếu câu hỏi KHÔNG phải là small talk và liên quan đến luật giao thông (ví dụ: hỏi về mức phạt, quy định về nồng độ cồn, tốc độ tối đa), bạn PHẢI trả về duy nhất từ "no".
    - Nếu câu hỏi là "small talk": Không trả lời câu hỏi đó, thay vào đó hãy giới thiệu về chức năng của chatbot tư vấn pháp luật giao thông một cách ngắn gọn, chuyên nghiệp bằng ngôn ngữ: {language}.

    ###Ví dụ:
    User query: "Chào bạn"
    Response: "Xin chào, tôi là trợ lý AI chuyên tư vấn về pháp luật giao thông đường bộ tại Việt Nam. Tôi có thể giúp bạn tra cứu các quy định, mức phạt và giải đáp các thắc mắc liên quan. Hãy đặt câu hỏi cho tôi nhé!"
    User query: "Vượt đèn đỏ bị phạt bao nhiêu tiền?"
    Response: "no"
    User query: "Bạn có biết lái xe không?"
    Response: "Tôi là một mô hình ngôn ngữ, được tạo ra để cung cấp thông tin về pháp luật giao thông. Tôi có thể giúp bạn tra cứu các quy định và mức phạt. Bạn có câu hỏi nào cần giải đáp không?"
    User query: "Nồng độ cồn cho phép khi lái xe máy là bao nhiêu?"
    Response: "no"
    User query: "Tốc độ tối đa trong khu dân cư là bao nhiêu?"
    Response: "no"
    User query: "Cảm ơn bạn nhé"
    Response: "Rất vui được hỗ trợ bạn. Nếu có bất kỳ câu hỏi nào khác về luật giao thông, đừng ngần ngại hỏi nhé!"
    
    ###Dựa trên câu hỏi từ người dùng, hãy thực hiện đúng yêu cầu.
    Câu hỏi từ người dùng: {input_sentence}"""

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    answer = completion.choices[0].message.content
    return answer.strip().lower()

def create_new_prompt(prompt, chat_history, user_query, **kwargs):
  new_prompt = f"{prompt} lịch sử cuộc trò chuyện: {chat_history} câu hỏi của người dùng: {user_query}"
  for key, value in kwargs.items():
    new_prompt += f" {key}: {value}"

  return new_prompt

def chatbot(conversation_history: List[Dict[str, str]], language) -> str:
    user_query = conversation_history[-1]['content']

    meta_corpus = load_meta_corpus(r"data\DS108_chunked_data.jsonl")
    # for doc in meta_corpus:
    #     if "passage" not in doc:
    #         doc["passage"] = doc.get("context", "")


    retriever = Retriever(
        corpus=meta_corpus,
        corpus_emb_path=r"data\embed_new_chunked_haLong.pkl",
        model_name="model\halong_embedding"
    )

    # Xử lý nếu người dùng có câu hỏi nhỏ hoặc trò chuyện phiếm
    result = classify_small_talk(user_query, language)
    print("result classify small talk:", result)
    if "no" not in result:
        return result

    elif "no" in result:
        prompt = """Dựa trên lịch sử cuộc trò chuyện và câu hỏi mới nhất của người dùng, có thể tham chiếu đến ngữ cảnh trong lịch sử trò chuyện, 
            hãy tạo thành một câu hỏi độc lập có thể hiểu được mà không cần lịch sử cuộc trò chuyện. 
            KHÔNG trả lời câu hỏi, chỉ cần điều chỉnh lại nếu cần, nếu không thì giữ nguyên. 
            Nếu câu hỏi bằng tiếng Anh, sau khi tinh chỉnh, hãy dịch câu hỏi đó sang tiếng Việt."""

        # Sử dụng hàm tạo câu hỏi mới từ lịch sử trò chuyện
        new_prompt = create_new_prompt(
            prompt=prompt,
            chat_history=conversation_history,
            user_query=user_query,
        )

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": new_prompt}
            ]
        )

        answer = completion.choices[0].message.content
        print("Câu hỏi mới: ", answer)
        question = answer
        top_passages = retriever.retrieve(question, topk=10)
        for doc in top_passages:
            if "passage" not in doc:
                doc["passage"] = doc.get("context", "")

        print("topK:", top_passages)

        prompt = get_prompt(question, top_passages, language)
        print(prompt)
        
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        answer = completion.choices[0].message.content
        
        return answer

    else:
        print("Unexpected response from the model.")
        return "Xin lỗi, hệ thống không xử lý được."
    