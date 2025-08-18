"""
Gradio Chatbot using OpenAI API
"""

import gradio as gr
from openai import OpenAI

from src.core.config import settings
from src.utils.logger import logger

# OpenAI client initialization
client = OpenAI(api_key=settings.OPENAI_API_KEY)

# Available models with descriptions
MODELS = {
    "gpt-5": "最新フラッグシップモデル（最高性能・汎用性）",
    "gpt-5-mini": "コスト効率重視版（高性能ながら低価格）", 
    "gpt-5-nano": "軽量版（高速・最低コスト）"
}

# System prompt for chat
SYSTEM_PROMPT = """あなたは親しみやすく、丁寧で知識豊富なAIアシスタントです。
ユーザーの質問に対して、正確で有用な情報を提供し、自然な会話を心がけてください。
分からないことがあれば正直に「分からない」と答え、必要に応じて追加の質問をして、
ユーザーのニーズをより良く理解するよう努めてください。"""


def chat_with_openai(message: str, history: list, model: str):
    """
    OpenAI APIを使用してチャットを処理する
    
    Args:
        message: ユーザーのメッセージ
        history: 会話履歴
        model: 使用するモデル
    
    Returns:
        更新された会話履歴
    """
    try:
        logger.info(f"Chat request: model={model}")
        
        # 会話履歴をOpenAI形式に変換
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        for user_msg, assistant_msg in history:
            if user_msg:
                messages.append({"role": "user", "content": user_msg})
            if assistant_msg:
                messages.append({"role": "assistant", "content": assistant_msg})
        
        # 現在のメッセージを追加
        messages.append({"role": "user", "content": message})
        
        # OpenAI APIに送信
        response = client.chat.completions.create(
            model=model,
            messages=messages
        )
        
        assistant_response = response.choices[0].message.content
        logger.info("Chat response generated successfully")
        
        # 会話履歴を更新
        history.append((message, assistant_response))
        return history
        
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        error_message = f"エラーが発生しました: {str(e)}"
        history.append((message, error_message))
        return history


def reset_chat():
    """
    チャット履歴をリセットする
    
    Returns:
        空の会話履歴とクリアされた入力欄
    """
    logger.info("Chat history reset")
    return [], ""


# Gradio インターface作成
def create_interface():
    """
    Gradioインターフェースを作成する
    """
    with gr.Blocks(title="Gradio Chatbot", theme=gr.themes.Soft()) as app:
        gr.Markdown("# 🤖 Gradio Chatbot")
        gr.Markdown("OpenAI APIを使用したシンプルなチャットボットです。")
        
        with gr.Row():
            with gr.Column(scale=3):
                # チャット画面
                chatbot = gr.Chatbot(
                    label="チャット",
                    height=400,
                    show_copy_button=True
                )
                
                # ユーザー入力
                msg_input = gr.Textbox(
                    label="メッセージを入力",
                    placeholder="何でもお聞きください...",
                    lines=3,
                    max_lines=10
                )
                
                with gr.Row():
                    send_btn = gr.Button("送信", variant="primary")
                    clear_btn = gr.Button("リセット", variant="secondary")
            
            with gr.Column(scale=1):
                # モデル選択
                model_dropdown = gr.Dropdown(
                    choices=list(MODELS.keys()),
                    value="gpt-5-mini",
                    label="モデル選択",
                    info="使用するOpenAIモデルを選択"
                )
                
                # モデル説明
                model_info = gr.Textbox(
                    value=MODELS["gpt-5-mini"],
                    label="モデル説明",
                    interactive=False,
                    lines=2
                )
        
        # モデル選択時の説明更新
        def update_model_info(model):
            return MODELS.get(model, "")
        
        model_dropdown.change(
            fn=update_model_info,
            inputs=[model_dropdown],
            outputs=[model_info]
        )
        
        # チャット機能の接続
        def submit_message(message, history, model):
            if not message.strip():
                return history, ""
            return chat_with_openai(message, history, model), ""
        
        # 送信ボタンクリック時
        send_btn.click(
            fn=submit_message,
            inputs=[msg_input, chatbot, model_dropdown],
            outputs=[chatbot, msg_input]
        )
        
        # エンターキー送信
        msg_input.submit(
            fn=submit_message,
            inputs=[msg_input, chatbot, model_dropdown],
            outputs=[chatbot, msg_input]
        )
        
        # リセットボタンクリック時
        clear_btn.click(
            fn=reset_chat,
            outputs=[chatbot, msg_input]
        )
    
    return app


if __name__ == "__main__":
    logger.info("Starting Gradio Chatbot")
    
    # OpenAI APIキーの確認
    if not settings.OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY is not set")
        raise ValueError("OPENAI_API_KEY environment variable is required")
    
    # Gradioアプリの起動
    app = create_interface()
    app.launch(
        server_name="0.0.0.0",
        server_port=8080,
        show_api=False,
        show_error=True
    )
