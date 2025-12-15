from app.personal_agent import Agent
from app.vector_db import get_vector_store


def main():
    get_vector_store()
    prompt = input("Me: ")
    while True:
        agent = Agent()
        resp = agent.run(prompt)
        print("Agent: " + resp)
        prompt = input("Me: ")


if __name__ == "__main__":
    main()
