# from app.agentic_mode.personal_model import Agent
from app.agentic_mode.raw_model import Agent

# from app.personal_assistant import Agent

from app.utils.vector_db import get_vector_store
import json

from app.utils.memory_management import MemoryManager


# def main():
#     get_vector_store()
#     prompt = input("Me: ")
#     memory = MemoryManager()
#     agent = Agent()
#     while True:

#         resp = agent.run(prompt,"user")
#         print("Agent: " + resp)
#         prompt = input("Me: ")


# if __name__ == "__main__":
#     main()

get_vector_store()
a = Agent()

a.llm.reset()

messages = [
    "hi",
    "who is Kelvin Quansah",
    "can you list the files here",
    "can you show me what in the toml file",
    "can you give me a summary of what i am trying to do based on the toml file you just saw",
    "what other tools will you like to have access to",
    "recommend an anime to me if i liked an anime called Erased",
    "find out about steins gate for me",
]

for message in messages:
    print(f"User: {message}")
    resp = a.run(message, "user")
    print(f"Karma: {resp}")


with open("output.json", "w+") as out:
    json.dump(a.conversation, out)
    out.close()
