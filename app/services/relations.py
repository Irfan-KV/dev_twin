from typing import List, Iterable
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from app.schemas import RelationsOutput


def extract_relations(text: str, openai_api_key: str) -> Iterable[tuple[str, str, str]]:
    llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=openai_api_key)
    prompt = ChatPromptTemplate.from_template(
        """
		Extract all developer rationale relationships from the text.
		Return a list of triples (head, relation, tail).
		Text:
		{text}
		"""
    )
    llm_structured = llm.with_structured_output(RelationsOutput)
    result = llm_structured.invoke(prompt.format_prompt(text=text))
    relations = getattr(result, "relations", [])
    for rel in relations:
        yield rel.head, rel.relation, rel.tail
