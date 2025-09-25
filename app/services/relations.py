from typing import List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from app.schemas import KnowledgeGraphOutput


def extract_kg(text: str, openai_api_key: str) -> KnowledgeGraphOutput:
    llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=openai_api_key)
    prompt = ChatPromptTemplate.from_template(
        """
        You are an expert knowledge graph builder.
        Your goal is to read raw unstructured text and extract entities and relationships
        to build a graph database (Neo4j).
        Overview of the product:
        - Maintains full context of feature development
        - Captures tasks, decisions, developers' contributions, reasoning, constraints
        - Aggregates data from multiple sources like Notion, meeting transcripts, Git commits, PRDs, Figma
        Instructions:
        1. Identify all **entities** mentioned in the text.
        - For each entity, use:
            - `name`: human-readable identifier, replace space with underscore
            - `label`: same as `name` (each entity should be unique)
        - Do NOT restrict labels to predefined types. Each entity must be distinct.
        2. Identify all **relationships** between entities:
        - `from`: entity name
        - `to`: entity name
        - `type`: relationship type (WORKED_ON, CONTRIBUTED_TO, MODIFIED_BY, IMPACTS, BASED_ON, ASSIGNED, AUTHORED, DESCRIBES, etc.)
        - `explanation`: brief reasoning or context
        3. Use only facts explicitly stated or strongly implied.
        Text:
        \"\"\"{text}\"\"\"
        """
    )
    llm_structured = llm.with_structured_output(KnowledgeGraphOutput)
    result = llm_structured.invoke(prompt.format_prompt(text=text))
    return result
