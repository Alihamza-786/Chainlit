import os
import chainlit as cl
from langgraph_app import agent
from chainlit.types import ThreadDict
from chainlit.data.sql_alchemy import SQLAlchemyDataLayer
from langchain_core.messages import HumanMessage, AIMessage

# Authentication
@cl.password_auth_callback
def auth_callback(username: str, password: str):
    if username == "admin" and password == "admin":
        return cl.User(identifier="admin", metadata={"role": "admin"})
    return None


# Data Layer
@cl.data_layer
def get_data_layer():
    conninfo = os.getenv("DATABASE_URL")
    
    if not conninfo:
        print("\nDATABASE_URL not found in environment variables.")
        return None

    try:
        data_layer = SQLAlchemyDataLayer(conninfo=conninfo)
        return data_layer
    except Exception as e:
        print(f"\n\nFailed to initialize SQLAlchemyDataLayer: {e}")
        return None

# Resume chat with proper message loading
@cl.on_chat_resume
async def on_chat_resume(thread: ThreadDict):

    try:
        steps = thread.get("steps", [])
        messages = []
        for step in steps:
            step_type = step.get("type")
            content = (step.get("output") or "").strip()
            if not content:
                continue  # skip empty rows
        
            if step_type == "user_message":
                messages.append(HumanMessage(content=content))
            elif step_type == "assistant_message":
                messages.append(AIMessage(content=content))
        cl.user_session.set("state", {"messages": messages})

    except Exception as e:
    
        print(f"\nError resuming chat: {e}")
        cl.user_session.set("state", {"messages": []})

# Chat Session Start
@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("state", {"messages": []})
    await cl.Message(content=f"👋 Hello! I'm your AI assistant. How can I help you today?").send()

# Handle Messages
@cl.on_message
async def on_message(msg: cl.Message):

    state = cl.user_session.get("state")
    state["messages"].append(HumanMessage(content=msg.content))

    final_state = await agent.ainvoke(state)

    cl.user_session.set("state", final_state)

# Chat Stop
@cl.on_stop
def on_stop():
    print("The user wants to stop the task!")

# Chat End
@cl.on_chat_end
def on_chat_end():
    print("The user disconnected!")