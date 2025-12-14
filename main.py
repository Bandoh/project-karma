from app.personal_agent import agent_run
from app.vector_db import get_vector_store


def main():
    get_vector_store()
    agent_run("change me name from Kelvin Quansah to Kelvin Rudolph in your memory")


if __name__ == "__main__":
    main()
