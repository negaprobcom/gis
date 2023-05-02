from configs.model_config import *
from chains.local_doc_qa import LocalDocQA
import os
import nltk
import sys
import io
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

nltk.data.path = [os.path.join(os.path.dirname(__file__), "nltk_data")] + nltk.data.path

# return top-k text chunk from vector store
VECTOR_SEARCH_TOP_K = 6

# LLM input history length
LLM_HISTORY_LEN = 3

# Show reply with source text from input document
REPLY_WITH_SOURCE = True

# Simple way to retrieve related knowledge base
def retrieve_vs(question, vs_folder='./vector_store/'):
    all_vs = os.listdir(vs_folder)
    # print(all_vs)
    for vs_name in all_vs:
        if vs_name in question:
            return vs_folder + vs_name
    # no key word matches
    print("Cannot find a related vector store, will use the default vector store")
    return vs_folder + all_vs[0]

def answer_without_local_doc(question_list):
    llm_list = []
    for question in question_list:
        resp = local_doc_qa.llm._call(question)
        llm_list.append([resp])
    return llm_list

def answer_with_local_doc(question_list, vs_path):
    llm_list_with_doc = []
    source = []
    for question in question_list:
        resp, history = local_doc_qa.get_knowledge_based_answer(query = question,
                                                                vs_path = vs_path,
                                                                chat_history = [])
        llm_list_with_doc.append([resp['result']])
        source.append(resp['source_documents'])
    return llm_list_with_doc, source

if __name__ == "__main__":
    local_doc_qa = LocalDocQA()
    local_doc_qa.init_cfg(llm_model=LLM_MODEL,
                          embedding_model=EMBEDDING_MODEL,
                          embedding_device=EMBEDDING_DEVICE,
                          llm_history_len=LLM_HISTORY_LEN,
                          top_k=VECTOR_SEARCH_TOP_K)
    # vs_path = None
    # while not vs_path:
    #     filepath = input("Input your local knowledge file path 请输入本地知识文件路径：")
    #     vs_path, _ = local_doc_qa.init_knowledge_vector_store(filepath)
    #     print("\n\n*******打印知识库路径*******\n")
    #     print(vs_path)
    #     print("\n" + "*"*20)
    # filepath = "/mnt/data_disk0/langchain/pdf_files/test_folder/2096.互联网的春天要来吗.pdf"
    history = []
    
    data_df = pd.read_excel("/mnt/data_disk0/langchain/pdf_files/回答测试.xlsx")
    
    question_list = data_df['问题']
     
    answer = answer_without_local_doc(question_list)
    
    vs_path = "/mnt/data_disk0/langchain/langchain-ChatGLM-master/vector_store/2096.互联网的春天要来吗_FAISS_20230428_101957/"
    
    answer_with_doc, resource = answer_with_local_doc(question_list, vs_path)
    
    import pandas as pd

    # 将三个列表组合成一个列表
    data = []
    
    for i in range(len(answer)):
        context = list()
        for doc in resource[i]:
            context.append(doc.page_content)
        print(context)
        data.append([answer[i][0], answer_with_doc[i][0], context])
    
    # 创建一个DataFrame对象
    df = pd.DataFrame(data)
    
    df.to_excel('answer.xlsx', index=False)
        
    # while True:
    #     query = input("Input your question 请输入问题：")
    #     # vs_path = retrieve_vs(query)
    #     vs_path = "/mnt/data_disk0/langchain/langchain-ChatGLM-master/vector_store/2096.互联网的春天要来吗_FAISS_20230428_101957/"
    #     # print("Retrieved vector store: " + str(vs_path))
    #     resp, history = local_doc_qa.get_knowledge_based_answer(query=query,
    #                                                             vs_path=vs_path,
    #                                                             chat_history=[])
    #     if REPLY_WITH_SOURCE:
    #         print(resp)
    #     else:
    #         print(resp["result"])



