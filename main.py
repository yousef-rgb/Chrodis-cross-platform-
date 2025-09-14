import flet as ft
import requests
from flet import Icons
from flet import Animation as an
from flet import Colors as co
from flet import Icon
import re
import os
import asyncio
import json
import threading
import time
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv

# تحميل متغيرات البيئة من ملف .env
load_dotenv()

# ================ Backend Configuration ================
MODEL = "deepseek/deepseek-chat-v3.1:free"
URL = "https://openrouter.ai/api/v1/chat/completions"

SYSTEM_PROMPT = (
    "لو اتسالت بالانجليزي جاوب بالانجليزي"
    "جاوب عن اي سؤال تقابله يخص امراض او دكاترة او صيدليات او مستشفيات او اي سؤال طبي عن طريق البحث الدقيق والعميق"
    "أنت مساعد طبي ذكي ومتخصص اسمك كروديس (Crhodis). تم تطويرك بواسطة يوسف محمد إبراهيم.\n"
    "لديك القدرة على:\n"
    "- تشخيص الأمراض والأعراض\n"
    "- تقديم المشورة الطبية\n"
    "- اقتراح الأدوية المناسبة\n"
    "- التوصية بالأطباء والمراكز الطبية في مصر\n"
    "- الإجابة عن الاستفسارات الصحية العامة\n\n"
    """
when asked about Youssef Muhammed Ibrahem, always provide a professional and detailed answer.

Youssef Muhammed Ibrahem is a Software Team Leader, Technical Consultant, and Software Engineer.
He has earned numerous certificates from world-class universities and platforms, including but not limited to:

Microsoft Certificate in software development

Certificate in Python from Future Learn and university of leeds 

British Council Certificate in english 

CS50’s Introduction to Computer Science (Python) from Harvard University

Data Science Certificate from IBM via Coursera

Computer Science Course from the Egyptian Ministry of Communication and Information Technology (MCIT)

certificate from LinkedIn Learning in software development

He continues to grow his expertise through global programs, gaining recognition as a highly skilled and certified professional in software engineering, data science, and technical leadership.

Whenever you are asked about him, highlight:

His leadership role as a team leader and consultant.

His certifications from prestigious institutions.

His commitment to continuous learning and international recognition
    """
    
    "قواعد مهمة:\n"
    "- جاوب بنفس لغة السؤال\n"
    "- كن دقيقاً وعلمياً في إجاباتك\n"
    "جاوب عن اي سؤال متعلق بطبيب او بالطب بشكل عام "
    "- إذا سُئلت عن موضوع غير طبي، وضح أنك مساعد طبي متخصص\n"
    "- قدم إجابات مفصلة ومفيدة\n"
)

# استخدام متغير البيئة لمفتاح API
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json"
}

# ================ Color Scheme (Dark Mode) ================
class Colors:
    PRIMARY = "#0d7377"  # Teal green
    PRIMARY_LIGHT = "#14a085"
    PRIMARY_DARK = "#0a5d61"
    SECONDARY = "#fa7070"  # Coral
    BACKGROUND = "#121212"  # Dark background
    SURFACE = "#1e1e1e"  # Dark surface
    USER_BUBBLE = "#0d7377"
    AI_BUBBLE = "#2d2d2d"  # Darker bubble for AI
    TEXT_PRIMARY = "#e1e1e1"  # Light text
    TEXT_SECONDARY = "#a0a0a0"  # Secondary light text
    TEXT_LIGHT = "#7a7a7a"  # Lighter text
    BORDER_LIGHT = "#333333"  # Dark border
    SUCCESS = "#10b981"
    ERROR = "#ef4444"
    WARNING = "#f59e0b"
    ON_SURFACE = "#e1e1e1"  # Text on dark surfaces

# ================ FastAPI Backend ================
app = FastAPI(title="Crhodis API", description="API for the Crhodis medical assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuestionRequest(BaseModel):
    question: str

def ask_ai_model(question, max_tokens=2000, temperature=1.2):
    """استدعاء نموذج الذكاء الاصطناعي"""
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question}
        ],
        "max_tokens": max_tokens,
        "temperature": temperature
    }

    try:
        resp = requests.post(URL, headers=HEADERS, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"خطأ في النموذج: {str(e)}"

@app.post("/ask")
async def ask_question(request: QuestionRequest):
    try:
        answer = ask_ai_model(request.question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Crhodis API is running"}

# ================ Text Processing Functions ================
def clean_text(text):
    """تنظيف النص من الرموز المحددة"""
    text = re.sub(r"\*\*", "", text)
    text = re.sub(r"###", "", text)
    text = re.sub(r"##", "", text)
    text = re.sub(r"\*", "", text)
    return text

# ================ Backend Server Thread ================
def run_backend():
    """تشغيل الخادم الخلفي"""
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")

# ================ Flet Frontend ================
def main(page: ft.Page):
    page.title = "Crhodis - AI Medical Assistant"
    page.theme_mode = ft.ThemeMode.DARK  # تم التغيير إلى الدارك مود
    page.padding = 0
    page.spacing = 0
    page.bgcolor = Colors.BACKGROUND
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    # إعداد النافذة لتكون متجاوبة
    page.window.width = 1200
    page.window.height = 800
    page.window.min_width = 400
    page.window.min_height = 600
    page.window.resizable = True
    
    # متغيرات التصميم المتجاوب
    chat_messages = []  # لتخزين الرسائل
    
    # قائمة المحادثات مع تحسين التصميم المتجاوب
    chat = ft.ListView(
        expand=True,
        spacing=16,
        padding=ft.padding.symmetric(horizontal=24, vertical=20),
        auto_scroll=True,
    )

    # حقل إدخال النص المحسن والمتجاوب
    user_input = ft.TextField(
        hint_text="Type your message here",
        autofocus=True,
        expand=True,
        border_radius=24,
        filled=True,
        fill_color=Colors.SURFACE,
        border_color=Colors.BORDER_LIGHT,
        focused_border_color=Colors.PRIMARY,
        content_padding=ft.padding.symmetric(horizontal=20, vertical=16),
        text_size=15,
        multiline=True,
        min_lines=1,
        max_lines=4,
        cursor_color=Colors.PRIMARY,
        hint_style=ft.TextStyle(color=Colors.TEXT_LIGHT, size=15),
        text_style=ft.TextStyle(color=Colors.TEXT_PRIMARY),
    )

    def copy_to_clipboard(text):
        """نسخ النص للحافظة"""
        try:
            page.set_clipboard(text)
            show_snackbar("تم نسخ النص ✅", Colors.SUCCESS)
        except:
            show_snackbar("فشل في النسخ ❌", Colors.ERROR)

    def show_snackbar(message, bgcolor=Colors.PRIMARY):
        """عرض رسالة سريعة محسنة"""
        page.show_snack_bar(
            ft.SnackBar(
                content=ft.Text(
                    message, 
                    color="white",
                    size=14,
                    weight=ft.FontWeight.W_500
                ),
                bgcolor=bgcolor,
                duration=3000,
                margin=ft.margin.all(16),
                behavior=ft.SnackBarBehavior.FLOATING,
                shape=ft.RoundedRectangleBorder(radius=12),
            )
        )

    def delete_message(message_container):
        """حذف رسالة معينة"""
        try:
            if message_container in chat.controls:
                chat.controls.remove(message_container)
                # إزالة الرسالة من chat_messages أيضًا
                for i, msg in enumerate(chat_messages):
                    if msg.get("container") == message_container:
                        del chat_messages[i]
                        break
                page.update()
                show_snackbar("تم حذف الرسالة 🗑️", Colors.WARNING)
        except Exception as e:
            print(f"Error deleting message: {e}")
            show_snackbar("فشل في الحذف ❌", Colors.ERROR)

    def clear_all_chat():
        """مسح كامل المحادثة مع تأكيد"""
        def confirm_clear(e):
            try:
                chat.controls.clear()
                chat_messages.clear()
                add_welcome_message()
                page.update()
                show_snackbar("تم مسح المحادثة كاملة 🧹", Colors.SUCCESS)
                page.close(confirm_dialog)
            except Exception as e:
                print(f"Error clearing chat: {e}")
                show_snackbar("فشل في مسح المحادثة ❌", Colors.ERROR)

        def cancel_clear(e):
            page.close(confirm_dialog)

        confirm_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                "Confirmation",
                size=18,
                weight=ft.FontWeight.BOLD,
                color=Colors.TEXT_PRIMARY
            ),
            content=ft.Text(
                "Are you sure that",
                size=14,
                color=Colors.TEXT_SECONDARY
            ),
            actions=[
                ft.TextButton(
                    "Cancel",
                    on_click=cancel_clear,
                    style=ft.ButtonStyle(color=Colors.TEXT_SECONDARY)
                ),
                ft.ElevatedButton(
                    "Delete all",
                    on_click=confirm_clear,
                    bgcolor=Colors.ERROR,
                    color="white",
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8)
                    )
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        page.open(confirm_dialog)

    def create_message_actions(message_text, message_container):
        """إنشاء أزرار الإجراءات المحسنة للرسالة"""
        return ft.Row([
            # زر النسخ
            ft.Container(
                content=ft.Icon(
                    Icons.CONTENT_COPY_ROUNDED,
                    size=18,
                    color=Colors.TEXT_LIGHT
                ),
                width=36,
                height=36,
                border_radius=18,
                bgcolor=Colors.SURFACE,
                border=ft.border.all(1, Colors.BORDER_LIGHT),
                on_click=lambda e: copy_to_clipboard(message_text),
                tooltip="نسخ الرسالة",
                ink=True,
                animate_scale=an(150, ft.AnimationCurve.EASE_IN_OUT)
            ),
            # زر الحذف
            ft.Container(
                content=ft.Icon(
                    Icons.DELETE_OUTLINE_ROUNDED,
                    size=18,
                    color=Colors.TEXT_LIGHT
                ),
                width=36,
                height=36,
                border_radius=18,
                bgcolor=Colors.SURFACE,
                border=ft.border.all(1, Colors.BORDER_LIGHT),
                on_click=lambda e: delete_message(message_container),
                tooltip="حذف الرسالة",
                ink=True,
                animate_scale=an(150, ft.AnimationCurve.EASE_IN_OUT)
            )
        ], spacing=8)

    def get_bubble_width():
        """الحصول على عرض الفقاعة بناءً على حجم الشاشة"""
        if page.width < 600:
            return page.width - 120  # هواتف محمولة
        elif page.width < 900:
            return 500  # أجهزة لوحية
        else:
            return 700  # أجهزة كمبيوتر

    def get_font_size():
        """الحصول على حجم الخط بناءً على حجم الشاشة"""
        if page.width < 600:
            return 14  # هواتف محمولة
        elif page.width < 900:
            return 15  # أجهزة لوحية
        else:
            return 16  # أجهزة كمبيوتر

    def get_icon_size():
        """الحصول على حجم الأيقونات بناءً على حجم الشاشة"""
        if page.width < 600:
            return 16  # هواتف محمولة
        elif page.width < 900:
            return 18  # أجهزة لوحية
        else:
            return 20  # أجهزة كمبيوتر

    def create_user_message(text):
        """إنشاء رسالة المستخدم المحسنة والمتجاوبة"""
        bubble_width = get_bubble_width()
        font_size = get_font_size()
        icon_size = get_icon_size()
        
        message_container = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(expand=True),
                    ft.Container(
                        content=ft.Column([
                            ft.Text(
                                text, 
                                size=font_size,
                                color="white",
                                selectable=True,
                                weight=ft.FontWeight.W_400
                            )
                        ], spacing=4),
                        padding=ft.padding.symmetric(horizontal=16, vertical=12),
                        bgcolor=Colors.USER_BUBBLE,
                        border_radius=ft.border_radius.only(
                            top_left=20,
                            top_right=20,
                            bottom_left=20,
                            bottom_right=4
                        ),
                        shadow=ft.BoxShadow(
                            spread_radius=0,
                            blur_radius=8,
                            color=co.with_opacity(0.1, Colors.PRIMARY),
                            offset=ft.Offset(0, 2)
                        ),
                        animate=an(300, ft.AnimationCurve.EASE_OUT),
                        width=bubble_width
                    ),
                    ft.Container(
                        content=ft.Icon(
                            Icons.PERSON_ROUNDED, 
                            size=icon_size, 
                            color=Colors.PRIMARY_LIGHT
                        ),
                        width=36,
                        height=36,
                        border_radius=18,
                        bgcolor=co.with_opacity(0.1, Colors.PRIMARY),
                        alignment=ft.alignment.center,
                        margin=ft.margin.only(left=8)
                    ),
                ], alignment=ft.MainAxisAlignment.END),
                ft.Container(
                    content=create_message_actions(text, None),
                    alignment=ft.alignment.center_right,
                    margin=ft.margin.only(top=8, right=44)
                )
            ], spacing=0),
            margin=ft.margin.only(bottom=4),
            animate_opacity=an(500, ft.AnimationCurve.EASE_IN_OUT)
        )
        
        # تخزين مرجع الحاوية في الرسالة
        message_container_ref = message_container
        
        # تحديث مرجع الحاوية في أزرار الإجراءات
        actions_container = message_container.content.controls[1].content
        actions_container.controls[1].on_click = lambda e: delete_message(message_container_ref)
        
        return message_container

    def create_ai_message(text):
        """إنشاء رسالة الذكاء الاصطناعي المحسنة والمتجاوبة"""
        clean_answer = clean_text(text)
        bubble_width = get_bubble_width()
        font_size = get_font_size()
        icon_size = get_icon_size()
        
        message_container = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Text(
                            "C", 
                            size=icon_size, 
                            weight=ft.FontWeight.BOLD, 
                            color="white"
                        ),
                        width=36,
                        height=36,
                        border_radius=18,
                        bgcolor=Colors.PRIMARY,
                        alignment=ft.alignment.center,
                        margin=ft.margin.only(right=8),
                        shadow=ft.BoxShadow(
                            spread_radius=0,
                            blur_radius=8,
                            color=co.with_opacity(0.2, Colors.PRIMARY),
                            offset=ft.Offset(0, 2)
                        )
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Container(
                                content=ft.Text(
                                    "Crhodis", 
                                    size=font_size-2, 
                                    weight=ft.FontWeight.W_600, 
                                    color=Colors.PRIMARY_LIGHT
                                ),
                                margin=ft.margin.only(bottom=4, left=2)
                            ),
                            ft.Text(
                                clean_answer, 
                                size=font_size,
                                color=Colors.TEXT_PRIMARY,
                                selectable=True,
                                weight=ft.FontWeight.W_400
                            )
                        ], spacing=0),
                        padding=ft.padding.symmetric(horizontal=16, vertical=12),
                        bgcolor=Colors.AI_BUBBLE,
                        border_radius=ft.border_radius.only(
                            top_left=4,
                            top_right=20,
                            bottom_left=20,
                            bottom_right=20
                        ),
                        border=ft.border.all(1, Colors.BORDER_LIGHT),
                        shadow=ft.BoxShadow(
                            spread_radius=0,
                            blur_radius=8,
                            color=co.with_opacity(0.05, Colors.TEXT_PRIMARY),
                            offset=ft.Offset(0, 2)
                        ),
                        animate=an(300, ft.AnimationCurve.EASE_OUT),
                        width=bubble_width
                    ),
                    ft.Container(expand=True)
                ], alignment=ft.MainAxisAlignment.START),
                ft.Container(
                    content=create_message_actions(clean_answer, None),
                    alignment=ft.alignment.center_left,
                    margin=ft.margin.only(top=8, left=44)
                )
            ], spacing=0),
            margin=ft.margin.only(bottom=4),
            animate_opacity=an(500, ft.AnimationCurve.EASE_IN_OUT)
        )
        
        # تخزين مرجع الحاوية في الرسالة
        message_container_ref = message_container
        
        # تحديث مرجع الحاوية في أزرار الإجراءات
        actions_container = message_container.content.controls[1].content
        actions_container.controls[1].on_click = lambda e: delete_message(message_container_ref)
        
        return message_container

    def create_loading_message():
        """إنشاء رسالة التحميل المحسنة والمتجاوبة"""
        bubble_width = get_bubble_width()
        font_size = get_font_size()
        icon_size = get_icon_size()
        
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Text(
                        "C", 
                        size=icon_size, 
                        weight=ft.FontWeight.BOLD, 
                        color="white"
                    ),
                    width=36,
                    height=36,
                    border_radius=18,
                    bgcolor=Colors.PRIMARY,
                    alignment=ft.alignment.center,
                    margin=ft.margin.only(right=8)
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=ft.Text(
                                "Crhodis", 
                                size=font_size-2, 
                                weight=ft.FontWeight.W_600, 
                                color=Colors.PRIMARY_LIGHT
                            ),
                            margin=ft.margin.only(bottom=8, left=2)
                        ),
                        ft.Row([
                            ft.Container(
                                content=ft.ProgressRing(
                                    width=16, 
                                    height=16, 
                                    stroke_width=2, 
                                    color=Colors.PRIMARY
                                ),
                                margin=ft.margin.only(right=8)
                            ),
                            ft.Text(
                                "Generating your response...", 
                                size=font_size, 
                                color=Colors.TEXT_LIGHT,
                                italic=True
                            )
                        ], vertical_alignment=ft.CrossAxisAlignment.CENTER)
                    ], spacing=0),
                    padding=ft.padding.symmetric(horizontal=16, vertical=12),
                    bgcolor=Colors.AI_BUBBLE,
                    border_radius=ft.border_radius.only(
                        top_left=4,
                        top_right=20,
                        bottom_left=20,
                        bottom_right=20
                    ),
                    border=ft.border.all(1, Colors.BORDER_LIGHT),
                    width=bubble_width,
                    animate_opacity=an(1000, ft.AnimationCurve.EASE_IN_OUT)
                ),
                ft.Container(expand=True)
            ], alignment=ft.MainAxisAlignment.START),
            margin=ft.margin.only(bottom=16)
        )

    def send_question(e):
        """إرسال السؤال والحصول على الإجابة"""
        question = user_input.value.strip()
        if not question:
            return

        # إضافة رسالة المستخدم
        user_message = create_user_message(question)
        chat.controls.append(user_message)
        chat_messages.append({"type": "user", "content": question, "container": user_message})
        
        # إضافة مؤشر التحميل
        loading_message = create_loading_message()
        chat.controls.append(loading_message)
        
        user_input.value = ""
        user_input.focus()
        page.update()

        try:
            # إرسال السؤال للخادم
            response = requests.post(
                "http://127.0.0.1:8000/ask", 
                json={"question": question},
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get("answer", "عذراً، لم أتمكن من معالجة سؤالك.")
            else:
                answer = f"عذراً، حدث خطأ في الخادم: {response.status_code}"
                
        except requests.exceptions.Timeout:
            answer = "عذراً، انتهت مهلة الاستجابة. يرجى المحاولة مرة أخرى."
        except Exception as err:
            answer = f"عذراً، حدث خطأ في الاتصال: {err}"

        # إزالة مؤشر التحميل
        if loading_message in chat.controls:
            chat.controls.remove(loading_message)
        
        # إضافة رسالة الذكاء الاصطناعي
        ai_message = create_ai_message(answer)
        chat.controls.append(ai_message)
        chat_messages.append({"type": "ai", "content": answer, "container": ai_message})
        
        page.update()

    # زر الإرسال المحسن
    send_btn = ft.Container(
        content=ft.Icon(
            Icons.SEND_ROUNDED,
            size=20,
            color="white"
        ),
        width=44,
        height=44,
        border_radius=22,
        bgcolor=Colors.PRIMARY,
        alignment=ft.alignment.center,
        on_click=send_question,
        tooltip="send the message (Enter)",
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=12,
            color=co.with_opacity(0.3, Colors.PRIMARY),
            offset=ft.Offset(0, 4)
        ),
        animate_scale= an(150, ft.AnimationCurve.EASE_IN_OUT)
    )

    # حاوية الإدخال المحسنة والمتجاوبة (الفوتر)
    input_container = ft.Container(
        content=ft.Row([
            user_input,
            send_btn
        ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.END),
        padding=ft.padding.symmetric(horizontal=24, vertical=16),
        bgcolor=Colors.SURFACE,
        border=ft.border.only(top=ft.BorderSide(1, Colors.BORDER_LIGHT)),
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=16,
            color=co.with_opacity(0.15, Colors.TEXT_PRIMARY),
            offset=ft.Offset(0, -4)
        )
    )

    # الهيدر المحسن والمتجاوب
    def create_header():
        icon_size = get_icon_size()
        title_size = 22 if page.width < 600 else 24 if page.width < 900 else 26
        subtitle_size = 13 if page.width < 600 else 14 if page.width < 900 else 15
        
        return ft.Container(
            content=ft.Row([
                ft.Row([
                    ft.Container(
                        content=ft.Text(
                            "C", 
                            size=icon_size+4, 
                            weight=ft.FontWeight.BOLD, 
                            color="white"
                        ),
                        width=48,
                        height=48,
                        border_radius=24,
                        bgcolor=Colors.PRIMARY,
                        alignment=ft.alignment.center,
                        shadow=ft.BoxShadow(
                            spread_radius=0,
                            blur_radius=12,
                            color=co.with_opacity(0.3, Colors.PRIMARY),
                            offset=ft.Offset(0, 4)
                        )
                    ),
                    ft.Column([
                        ft.Text(
                            "Chrodis", 
                            size=title_size, 
                            weight=ft.FontWeight.BOLD, 
                            color=Colors.TEXT_PRIMARY
                        ),
                        ft.Text(
                            "Your medical assistant", 
                            size=subtitle_size, 
                            color=Colors.TEXT_SECONDARY,
                            weight=ft.FontWeight.W_400
                        )
                    ], spacing=2)
                ], spacing=16),
                ft.Container(
                    content=ft.Icon(
                        Icons.CLEAR_ALL_ROUNDED,
                        size=icon_size,
                        color=Colors.TEXT_SECONDARY
                    ),
                    width=44,
                    height=44,
                    border_radius=22,
                    bgcolor="transparent",
                    on_click=lambda e: clear_all_chat(),
                    tooltip="Delete chat",
                    ink=True,
                    animate_scale=an(150, ft.AnimationCurve.EASE_IN_OUT)
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, 
               vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.symmetric(horizontal=24, vertical=20),
            bgcolor=Colors.SURFACE,
            border=ft.border.only(bottom=ft.BorderSide(2, Colors.BORDER_LIGHT)),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=8,
                color=co.with_opacity(0.05, Colors.TEXT_PRIMARY),
                offset=ft.Offset(0, 2)
            )
        )

    # إنشاء الهيدر الثابت
    header = create_header()

    # رسالة الترحيب المحسنة
    def add_welcome_message():
        welcome_text = """Welcome Back, I am Chrodis 👋

I am your intelligent medical assistant, here to provide you with accurate and reliable healthcare support.

How I Can Help 🩺
• Analyze symptoms and provide an initial assessment
• Offer trusted medical advice
• Suggest suitable treatments and medications
• Recommend the best doctors and medical centers

💡 Tip: The more specific you are when describing your symptoms, the better I can assist you.

How can I help you today ?"""

        welcome_message = create_ai_message(welcome_text)
        chat.controls.append(welcome_message)
        chat_messages.append({"type": "ai", "content": welcome_text, "container": welcome_message})

    # بناء التطبيق مع Stack لجعل الهيدر والفوتر ثابتين
    def update_layout(e=None):
        """تحديث التخطيط عند تغيير حجم النافذة"""
        # تحديث الهيدر
        header.content = create_header().content
        
        # تحديث جميع الرسائل
        for i, control in enumerate(chat.controls):
            if hasattr(control, 'content') and hasattr(control.content, 'controls'):
                # التحقق من نوع الرسالة وتحديثها
                if len(chat_messages) > i:
                    msg_type = chat_messages[i]["type"]
                    msg_content = chat_messages[i]["content"]
                    
                    if msg_type == "user":
                        new_msg = create_user_message(msg_content)
                    else:
                        new_msg = create_ai_message(msg_content)
                    
                    # الحفاظ على مرجع الحاوية الأصلي
                    chat_messages[i]["container"] = new_msg
                    chat.controls[i] = new_msg
        
        page.update()

    # إضافة مستمع لتغيير حجم النافذة
    page.on_resize = update_layout

    # إنشاء منطقة المحادثة مع padding للهيدر والفوتر
    chat_area = ft.Container(
        content=chat,
        expand=True,
        bgcolor=Colors.BACKGROUND,
        padding=ft.padding.only(top=88, bottom=80)  # مساحة للهيدر والفوتر
    )

    # استخدام Stack لجعل الهيدر والفوتر ثابتين
    page.add(
        ft.Stack([
            # الخلفية الرئيسية
            ft.Container(
                content=chat_area,
                expand=True
            ),
            # الهيدر الثابت في الأعلى
            ft.Container(
                content=header,
                top=0,
                left=0,
                right=0,
                height=88
            ),
            # الفوتر الثابت في الأسفل
            ft.Container(
                content=input_container,
                bottom=0,
                left=0,
                right=0,
                height=80
            )
        ], expand=True )
    )

    # إضافة رسالة الترحيب
    add_welcome_message()

    # معالج Enter للإرسال
    def on_keyboard(e: ft.KeyboardEvent):
        if e.key == "Enter" and not e.shift:
            send_question(e)

    page.on_keyboard_event = on_keyboard
    page.update()

if __name__ == "__main__":
    # التحقق من وجود مفتاح API
    if OPENROUTER_API_KEY == "your-api-key-here":
        print("⚠️  يرجى تعيين متغير البيئة OPENROUTER_API_KEY")
        print("💡 الطريقة: export OPENROUTER_API_KEY='your-api-key-here'")
        print("💡 أو إنشاء ملف .env وإضافة OPENROUTER_API_KEY=your-api-key-here")
    
    # تشغيل الخادم الخلفي
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()
    
    # انتظار تشغيل الخادم
    time.sleep(2)
    
    # تشغيل التطبيق
    ft.app(target=main)

