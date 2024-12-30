# This will be used in order to get the training data for the model.
# This will be done using GPT-4o to generate the text for the data.

from langchain_openai import ChatOpenAI

from langchain_core.prompts import ChatPromptTemplate

from typing import List

from src.config import NO_GENERATED_SAMPLES, LLM_TEMPERATURE

from src.hmms.training.templates import TrainingInstance, TrainingData

llm = ChatOpenAI(model="gpt-4o", temperature=LLM_TEMPERATURE)

system_prompt = """
You are a helpful assistant that generates training data showing the state sequence for a sentence.
- You should generate {instances} instances of training data.
- Call the TrainingData tool in order to generate the training data.
- The number of possible states in the model are as follows:
    1) Action: It is shown by A, it is an action like "play cricket", "do homework", "read a book" etc.
    2) Duration: It is shown by D, it is a duration like "1 hour", "30 minutes", "3 hours" etc.
    3) Preference: It is shown by P, it is a preference like "morning", "evening", "weekends" etc.
    4) Word: It is shown by W, it is any word other than Action, Duration, Preference.
- Make sure to use different words in the sentences to have a diverse dataset.
"""


def get_training_data() -> List[TrainingInstance]:
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
    ])

    chain = prompt | llm.with_structured_output(TrainingData)

    data = chain.invoke({"instances": NO_GENERATED_SAMPLES})

    instances = data.instances

    return instances

if __name__ == "__main__":
    instances = get_training_data()
    print("Instances: ", instances)