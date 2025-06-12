from langchain.llms import OpenAI
from langchain.schema import Document
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
import os

knowledge_base = [
    "bird(robin)", "bird(penguin)", "bird(eagle)",
    "mammal(dog)", "mammal(cat)", "mammal(whale)",
    "fish(salmon)", "fish(shark)",
    "can_fly(robin)", "can_fly(eagle)",
    "can_swim(penguin)", "can_swim(whale)", "can_swim(salmon)",
    "has_feathers(robin)", "has_feathers(penguin)", "has_feathers(eagle)",
    "warm_blooded(robin)", "warm_blooded(penguin)", "warm_blooded(dog)"
]

def setup_vector_store(api_key):
    os.environ["OPENAI_API_KEY"] = api_key
    embeddings = OpenAIEmbeddings()
    documents = [Document(page_content=fact) for fact in knowledge_base]
    return FAISS.from_documents(documents, embeddings)

def convert_nl_to_logic(question, api_key):
    llm = OpenAI(temperature=0)
    
    prompt = f"""
    Convert this natural language question into a logic query format.
    Use predicates like: bird(X), can_fly(X), mammal(X), etc.
    
    Examples:
    "Can penguins fly?" -> "can_fly(penguin)"
    "Are robins birds?" -> "bird(robin)"
    "What animals can swim?" -> "can_swim(X)"
    
    Question: {question}
    Logic query:
    """
    
    response = llm(prompt)
    return response.strip().rstrip('.')

def simple_fact_check(logic_query):
    if 'X' in logic_query or '?' in logic_query:
        results = []
        for fact in knowledge_base:
            if logic_query.replace('X', '').replace('?', '').replace('(', '').replace(')', '') in fact:
                entity = fact.split('(')[1].split(')')[0]
                results.append(entity)
        return results
    else:
        return logic_query in knowledge_base

def get_context_for_query(vector_store, query):
    docs = vector_store.similarity_search(query, k=3)
    return [doc.page_content for doc in docs]

def run_logical_inference(question, api_key):
    vector_store = setup_vector_store(api_key)
    
    logic_query = convert_nl_to_logic(question, api_key)
    
    relevant_facts = get_context_for_query(vector_store, logic_query)
    
    result = simple_fact_check(logic_query)
    
    llm = OpenAI(temperature=0)
    explanation_prompt = f"""
    Question: {question}
    Logic Query: {logic_query}
    Relevant Facts: {', '.join(relevant_facts)}
    Query Result: {result}
    
    Provide a clear true/false answer and explain the reasoning:
    """
    
    explanation = llm(explanation_prompt)
    
    return {
        'question': question,
        'logic_query': logic_query,
        'result': result,
        'relevant_facts': relevant_facts,
        'explanation': explanation,
        'trace': f"Converted '{question}' to '{logic_query}', found result: {result}"
    }

def main():
    api_key = "SECRET"
    
    test_questions = [
        "Can penguins fly?",
        "Are robins birds?", 
        "What animals can swim?",
        "Do eagles have feathers?",
        "Are whales warm blooded?"
    ]
    
    for question in test_questions:
        result = run_logical_inference(question, api_key)
        
        print(f"Question: {result['question']}")
        print(f"Logic Query: {result['logic_query']}")
        print(f"Result: {result['result']}")
        print(f"Relevant Facts: {result['relevant_facts']}")
        print(f"Trace: {result['trace']}")
        print(f"Explanation: {result['explanation']}")
        print("-" * 50)

if __name__ == "__main__":
    main()

