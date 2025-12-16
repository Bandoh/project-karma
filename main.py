# from app.personal_agent import Agent
from app.utils.vector_db import get_vector_store
from app.personal_assistant import Agent
from app.utils.memory_management import MemoryManager


def main():
    get_vector_store()
    prompt = input("Me: ")
    memory = MemoryManager()
    agent = Agent(memory)
    while True:

        resp = agent.run(prompt)
        print("Agent: " + resp)
        prompt = input("Me: ")


if __name__ == "__main__":
    main()
