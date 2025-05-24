from langchain_community.llms import Ollama
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
import re


class OllamaMultiTurnAgent:
    def __init__(self, model_name="yi"):
        self.llm = Ollama(model=model_name, temperature=0.3)
        self.memory = ConversationBufferMemory(memory_key="chat_history")
        self.step = 0
        self.previous_questions = set()

        self.initial_questions = [
            "問題：你心情好的時候喜歡待在什麼地方？\n選項一：室內\n選項二：室外",
            "問題：你心情不好的時候喜歡待在什麼地方？\n選項一：室內\n選項二：室外"
        ]

        self.follow_up_prompt = PromptTemplate(
            input_variables=["chat_history", "last_answer", "previous_titles"],
            template="""
你是一位活動推薦助理，正在根據使用者的回覆進行問卷調查。

你要設計一個「新的問題」，以更了解他的個性與偏好，並使用以下格式：

---
問題：這裡是你設計的新問題？
選項一：這是第一個選項
選項二：這是第二個選項
---

⚠️ 請注意：
1. 僅輸出三行，格式如上。
2. 問題必須與下列對話內容有關。
3. 請**避免重複以下問題**或語意相似的問題：
{previous_titles}
4. 禁止添加開場白、說明或 JSON 包裝。
5. 僅使用繁體中文輸出。

對話紀錄：
{chat_history}

使用者剛剛回答：{last_answer}
"""
        )
        self.follow_up_chain = self.follow_up_prompt | self.llm

        self.summary_prompt = PromptTemplate(
            input_variables=["chat_history"],
            template="你是一位活動推薦專家。以下是與使用者的對話內容：\n{chat_history}\n\n請根據這些回答推薦一個最適合他的休閒娛樂活動，並簡短說明推薦原因（不超過100字）。請用繁體中文回答。"
        )
        self.summary_chain = self.summary_prompt | self.llm

    def extract_question_block(self, text):
        match = re.search(
            r"(問題：.+?)\n(選項一：.+?)\n(選項二：.+?)(?:\n|$)",
            text.strip(),
            re.DOTALL
        )
        return '\n'.join(match.groups()).strip() if match else None

    def get_question_title(self, question_text):
        return question_text.strip().split('\n')[0]

    def get_next_question(self, user_answer=None):
        if user_answer:
            self.memory.chat_memory.add_user_message(user_answer)
            self.step += 1

        if self.step < len(self.initial_questions):
            question = self.initial_questions[self.step]
            self.memory.chat_memory.add_ai_message(question)
            self.previous_questions.add(self.get_question_title(question))
            return question

        for i in range(10):
            previous_titles = "\n".join(self.previous_questions)
            raw_output = self.follow_up_chain.invoke({
                "chat_history": self.memory.buffer,
                "last_answer": user_answer,
                "previous_titles": previous_titles
            }).strip()

            question = self.extract_question_block(raw_output)

            if question:
                title = self.get_question_title(question)
                if title not in self.previous_questions:
                    self.previous_questions.add(title)
                    self.memory.chat_memory.add_ai_message(question)
                    return question
                else:
                    print(f"⚠️ 第 {i+1} 次問題重複：{title}")
            else:
                print(f"⚠️ 第 {i+1} 次輸出未通過格式驗證：\n{raw_output}\n")

        return "⚠️ 抱歉，無法產生符合格式且不重複的問題。請稍後再試。"

    def summarize_recommendation(self):
        return self.summary_chain.invoke({
            "chat_history": self.memory.buffer
        })
