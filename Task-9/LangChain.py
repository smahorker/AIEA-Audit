from langgraph.graph import StateGraph, START, END
from langchain_community.chat_models import ChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from typing import TypedDict, List
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

class GraphState(TypedDict):
    question: str
    relevant_context: List[str]
    reasoning: str
    logic_query: str
    result: str

def build_animal_graph():
    llm = ChatOpenAI(model_name="gpt-4", temperature=0)
    
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    if not os.path.exists("animal_db"):
        documents = [Document(page_content=fact) for fact in knowledge_base]
        splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=10)
        chunks = splitter.split_documents(documents)
        vectorstore = Chroma(persist_directory="animal_db", embedding_function=embeddings)
        vectorstore.add_documents(chunks)
    else:
        vectorstore = Chroma(persist_directory="animal_db", embedding_function=embeddings)
    
    retriever = vectorstore.as_retriever(k=3)
    
    reasoning_prompt = PromptTemplate.from_template(
        "Given these animal facts:\n"
        "{context}\n\n"
        "Question: {question}\n\n"
        "Think step by step about how to answer this question using the facts above. "
        "Then provide the final logic query needed to answer it.\n"
        "End your response with 'QUERY: [your logic query here]'"
    )
    
    graph = StateGraph(GraphState)
    
    def retrieve_context(state: GraphState) -> dict:
        docs = retriever.get_relevant_documents(state["question"])
        return {"relevant_context": [doc.page_content for doc in docs]}
    
    def chain_of_thought(state: GraphState) -> dict:
        context = "\n".join(state["relevant_context"])
        prompt = reasoning_prompt.format(question=state["question"], context=context)
        response = llm.invoke(prompt)
        return {"reasoning": response.content}
    
    def extract_logic_query(state: GraphState) -> dict:
        reasoning = state["reasoning"]
        query = ""
        for line in reasoning.split('\n'):
            if line.strip().startswith("QUERY:"):
                query = line.strip()[6:].strip()
                break
        return {"logic_query": query}
    
    def execute_logic_query(state: GraphState) -> dict:
        query = state["logic_query"]
        
        if not query:
            return {"result": "No query extracted"}
        
        if query in knowledge_base:
            return {"result": "True - fact found in knowledge base"}
        
        if "X" in query or "?" in query:
            results = []
            base_query = query.replace("X", "").replace("?", "").replace("(", "").replace(")", "")
            for fact in knowledge_base:
                if base_query in fact:
                    entity = fact.split("(")[1].split(")")[0]
                    results.append(entity)
            if results:
                return {"result": f"Results: {', '.join(results)}"}
            else:
                return {"result": "No matches found"}
        
        return {"result": "False - not found in knowledge base"}
    
    graph.add_node("retrieve_context", retrieve_context)
    graph.add_node("chain_of_thought", chain_of_thought)
    graph.add_node("extract_logic_query", extract_logic_query)
    graph.add_node("execute_logic_query", execute_logic_query)
    
    graph.add_edge(START, "retrieve_context")
    graph.add_edge("retrieve_context", "chain_of_thought")
    graph.add_edge("chain_of_thought", "extract_logic_query")
    graph.add_edge("extract_logic_query", "execute_logic_query")
    graph.add_edge("execute_logic_query", END)
    
    return graph.compile()

def main():
    os.environ["OPENAI_API_KEY"] = "your-openai-api-key"
    
    graph = build_animal_graph()
    
    test_questions = [
        "What animals can swim?",
        "Are penguins birds?",
        "Can eagles fly?",
        "What birds have feathers?"
    ]
    
    for question in test_questions:
        initial_state = GraphState(
            question=question,
            relevant_context=[],
            reasoning="",
            logic_query="",
            result=""
        )
        
        final_state = graph.invoke(initial_state)
        
        print(f"Question: {question}")
        print(f"Context: {final_state['relevant_context']}")
        print(f"Reasoning: {final_state['reasoning']}")
        print(f"Logic Query: {final_state['logic_query']}")
        print(f"Result: {final_state['result']}")
        print("-" * 50)

if __name__ == "__main__":
    main()
