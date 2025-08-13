"""
Template Python app for CloudRun deployment
Replace this with your actual app implementation
"""

from src.utils.logger import logger

# === STREAMLIT EXAMPLE ===
# import streamlit as st
# 
# st.title("Hello World")
# st.write("This is a Streamlit app!")
# logger.info("Streamlit app started")

# === GRADIO EXAMPLE ===
import gradio as gr

def greet(name):
    logger.info(f"Greeting {name}")
    return f"Hello {name}!"

iface = gr.Interface(fn=greet, inputs="text", outputs="text", flagging_mode="never")
if __name__ == "__main__":
    logger.info("Starting Gradio app")
    iface.launch(server_name="0.0.0.0", server_port=8080)

# === DASH EXAMPLE ===
# import dash
# from dash import html, dcc
# 
# app = dash.Dash(__name__)
# 
# app.layout = html.Div([
#     html.H1("Hello World"),
#     html.Div("This is a Dash app!"),
#     dcc.Graph(
#         figure={
#             'data': [{'x': [1, 2, 3], 'y': [4, 5, 6], 'type': 'bar'}],
#             'layout': {'title': 'Sample Chart'}
#         }
#     )
# ])
# 
# if __name__ == "__main__":
#     logger.info("Starting Dash app")
#     app.run_server(host="0.0.0.0", port=8080, debug=False)

# === SIMPLE FLASK EXAMPLE (as default) ===
# from flask import Flask

# app = Flask(__name__)

# @app.route("/")
# def hello():
#     logger.info("Hello endpoint called")
#     return "Hello World! Replace this with your app implementation."

# @app.route("/health")
# def health():
#     return {"status": "healthy"}

# if __name__ == "__main__":
#     logger.info("Starting Flask app")
#     app.run(host="0.0.0.0", port=8080)
