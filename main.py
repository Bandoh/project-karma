from app.personal_agent import agent_run
from app.vector_db import get_vector_store


def main():
    get_vector_store()
    agent_run("Who is Kelvin Quansah to you?")


if __name__ == "__main__":
    main()
