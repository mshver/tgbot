import sqlite3
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import random
from config import TOKEN
import buttons


bot = Bot(token=TOKEN)  # Создаем объект бота


dp = Dispatcher(bot)  # Создаем диспетчер для обработки сообщений бота


conn = sqlite3.connect('grades.db')  # Создаем базу данных SQLite
cur = conn.cursor()


cur.execute('''CREATE TABLE IF NOT EXISTS grades
               (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, subject TEXT, grade INTEGER)''')


subjects = ['Математика', 'Русский язык', 'История', 'Физика', 'Английский язык']
students = ['Иванов', 'Петров', 'Сидоров', 'Кузнецов', 'Соколов', 'Попов', 'Лебедев', 'Козлов', 'Новиков', 'Морозов']

for student in students:
    for subject in subjects:
        for i in range(6):
            grade = random.randint(2, 5)
            cur.execute(f"INSERT INTO grades (name, subject, grade) VALUES ('{student}', '{subject}', {grade})")


conn.commit()  # Сохраняем изменения в базе данных


keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)  # Создаем клавиатуру с кнопками для выбора ученика
for student in students:
    button = types.KeyboardButton(student)
    keyboard.add(button)


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer("Выберите ученика, чтобы увидеть его оценки:", reply_markup=keyboard)


@dp.message_handler(lambda message: message.text in students)
async def select_student(message: types.Message):
    student_name = message.text
    response = f"Оценки ученика {student_name}:\n"
    cur.execute(f"SELECT subject, grade FROM grades WHERE name='{student_name}'")
    grades = cur.fetchall()
    if grades:
        for subject in subjects:
            subject_grades = [str(g[1]) for g in grades if g[0] == subject]
            if subject_grades:
                response += f"{subject}: {', '.join(subject_grades)}\n"
            else:
                response += f"{subject}: нет данных\n"
        await message.answer(response)
    else:
        await message.answer(f"Нет данных об успеваемости ученика {student_name}.")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

# Закрываем соединение с базой данных
conn.close()
