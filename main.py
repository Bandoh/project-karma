from app.personal_agent import Agent
from app.vector_db import get_vector_store


def main():
    get_vector_store()
    prompt = input("How can i help you\n")
    while True:
        agent = Agent()
        resp = agent.run(prompt)
        print(resp)
        prompt = input()


if __name__ == "__main__":
    main()
