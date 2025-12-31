# from app.agentic_mode.personal_model import Agent
from app.agentic_mode.raw_model import Agent
# from app.personal_assistant import Agent
from app.utils.vector_db import get_vector_store

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


a = Agent()
resp = a.run("hi","user")
print(resp)
resp = a.run("can you list the files here","user")
print(resp)
resp = a.run("can you show me what in the toml file","user")
print(resp)
resp = a.run("can you give me a summary of what i am trying to do based on the toml file you just saw","user")
print(resp)
resp = a.run("what other tools will you like to have access to","user")
print(resp)
resp = a.run("recommend an anime to me if i liked an anime called Erased...use tool","user")
print(resp)