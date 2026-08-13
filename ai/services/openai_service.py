from django.conf import settings

from openai import OpenAI


class OpenAIService:

    def __init__(self):

        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY تنظیم نشده است.")

        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

        self.model = settings.OPENAI_MODEL

    def ask(self, question, context=""):

        prompt = f"""
تو یک دستیار آموزشی برای دانشجویان هستی.

به سؤال کاربر بر اساس متن ارائه‌شده پاسخ بده.

متن:
{context}

سؤال:
{question}

پاسخ را به زبان فارسی،
واضح، دقیق و آموزشی ارائه کن.
"""

        response = self.client.responses.create(
            model=self.model,
            input=prompt,
        )

        return response.output_text

    def summarize(self, text):

        prompt = f"""
متن زیر یک نوت دانشجویی است.

آن را به زبان فارسی خلاصه کن.

قوانین:
- نکات اصلی را حفظ کن.
- اطلاعات مهم حذف نشود.
- پاسخ ساختارمند باشد.
- از تیتر و bullet point استفاده کن.

متن:

{text}
"""

        response = self.client.responses.create(
            model=self.model,
            input=prompt,
        )

        return response.output_text
