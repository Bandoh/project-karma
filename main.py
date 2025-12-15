# from app.personal_agent import Agent
from app.vector_db import get_vector_store
from app.personal_assistant import Agent


def main():
    get_vector_store()
    prompt = input("Me: ")
    agent = Agent()
    while True:

        resp = agent.run(prompt)
        print("Agent: " + resp)
        prompt = input("Me: ")


if __name__ == "__main__":
    main()
