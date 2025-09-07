import os
import asyncio
import chainlit as cl
from typing import TypedDict, List
from langgraph.graph import StateGraph
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, BaseMessage, AIMessage

# Initialize LLM
llm = ChatOllama(model="qwen2.5", streaming=True)

# Define agent state
class AgentState(TypedDict):
    messages: List[BaseMessage]

# Separated streaming function
async def stream_llm_response(messages: List[BaseMessage]) -> AIMessage:
    msg = cl.Message(content="")
    await msg.send()

    content = ""
    try:
        async for chunk in llm.astream(messages):
            if chunk.content:
                content += chunk.content
                await msg.stream_token(chunk.content)
    except asyncio.CancelledError:
        print("\n⚠️ Streaming was interrupted.")
        pass

    await msg.update()
    return AIMessage(content=content)

# LangGraph node
async def llm_node(state: AgentState) -> AgentState:

    response = await stream_llm_response(state["messages"])
    state["messages"].append(AIMessage(content=response.content))

    print("\nFINAL STATE: ", state)
    return state


# Build LangGraph
graph = StateGraph(AgentState)
graph.add_node("llm", llm_node)
graph.set_entry_point("llm")
graph.set_finish_point("llm")
agent = graph.compile()

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

@cl.on_stop
def on_stop():
    print("The user wants to stop the task!")