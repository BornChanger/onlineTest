from flask import Flask, render_template, request
import language_tool_python
import speech_recognition as sr
import os
import base64
from pydub import AudioSegment
import requests

app = Flask(__name__)

# 设置请求体大小限制为 50 MB
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB

# 示例题目
questions = [
    {
        "type": "reading_multiple_choice",
        "question": "What is the capital of France?",
        "options": ["London", "Paris", "Berlin", "Madrid"],
        "answer": "Paris"
    },
    {
        "type": "listening_multiple_choice",
        "question": "What time does the train leave?",
        "options": ["10:05", "10:15", "10:50"],
        "answer": "10:15",
        "audio": "audio_q1.wav"  # 音频文件路径
    },
    {
        "type": "listening_short_answer",
        "question": "1. Where is the woman going for her holiday? 2. How long will she stay there?",
        "answer": "1. Spain 2. Two weeks",
        "audio": "audio_q2.wav"  # 音频文件路径
    },
    {
        "type": "reading_fill_in_blank",
        "question": "Complete the sentence: 'I usually go to school ______ bus.'",
        "answer": "by"
    },
    {
        "type": "writing_essay",
        "question": "Write a short essay (100-150 words) about your favorite hobby.",
        "answer": "Your essay should include: 1. What your hobby is. 2. Why you enjoy it. 3. How often you do it."
    },
    {
        "type": "speaking_self_introduction",
        "question": "Tell me about yourself. (Name, age, hobbies, etc.)",
        "answer": "My name is [Your Name]. I’m [Your Age] years old. I like playing football and reading books. I live in [Your City]."
    },
    {
        "type": "speaking_picture_description",
        "question": "Describe the picture. (假设图片是一个公园，有孩子和狗在玩耍)",
        "answer": "In the picture, there is a park. Some children are playing football, and a dog is running near them. The weather is sunny, and there are many trees in the park.",
        "image": "park.png"
    }
]

# 使用 LanguageTool API 检查作文
def check_grammar_with_languagetool(text):
    url = "https://api.languagetool.org/v2/check"
    data = {
        "text": text,
        "language": "en-US"
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        return response.json()  # 返回语法检查结果
    else:
        return None

# 语音转文本函数
def transcribe_audio(audio_file):
    recognizer = sr.Recognizer()
    
    # 使用 pydub 将音频文件转换为 WAV 格式
    audio = AudioSegment.from_file(audio_file)
    wav_path = audio_file.replace(".wav", "_converted.wav")
    audio.export(wav_path, format="wav")
    
    with sr.AudioFile(wav_path) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)
            return text
        except sr.UnknownValueError:
            return "Google Speech Recognition could not understand audio"
        except sr.RequestError:
            return "Could not request results from Google Speech Recognition"
        finally:
            os.remove(wav_path)  # 删除临时文件

# 口语打分函数
def evaluate_speaking(transcribed_text, correct_answer):
    # 简单打分逻辑：计算转录文本与参考答案的相似度
    transcribed_words = set(transcribed_text.lower().split())
    correct_words = set(correct_answer.lower().split())
    common_words = transcribed_words.intersection(correct_words)
    score = int((len(common_words) / len(correct_words)) * 10)  # 满分 10 分
    return min(score, 10)

@app.route('/')
def index():
    return render_template('index.html', questions=questions)

@app.route('/submit', methods=['POST'])
def submit():
    score = 0
    results = []
    for i in range(len(questions)):
        q = questions[i]
        if q["type"] == "reading_multiple_choice":
            user_answer = request.form.get(f'q{i}')  # 直接使用题目的索引作为名称
            if user_answer == q['answer']:
                score += 1
            results.append({"question": q["question"], "user_answer": user_answer, "correct_answer": q["answer"]})
        elif q["type"] == "listening_multiple_choice":
            user_answer = request.form.get(f'q{i}')  # 直接使用题目的索引作为名称
            if user_answer == q['answer']:
                score += 1
            results.append({"question": q["question"], "user_answer": user_answer, "correct_answer": q["answer"]})
        elif q["type"] == "reading_fill_in_blank":
            user_answer = request.form.get(f'q{i}_text')
            if user_answer.lower() == q['answer'].lower():
                score += 1
            results.append({"question": q["question"], "user_answer": user_answer, "correct_answer": q["answer"]})
        elif q["type"] == "listening_short_answer":
            user_answer = request.form.get(f'q{i}_text')
            if user_answer.lower() == q['answer'].lower():
                score += 1
            results.append({"question": q["question"], "user_answer": user_answer, "correct_answer": q["answer"]})
        elif q["type"] == "writing_essay":
            user_answer = request.form.get(f'q{i}_writing')
            grammar_result = check_grammar_with_languagetool(user_answer)
            errors = grammar_result["matches"] if grammar_result else []
            writing_score = max(0, 10 - len(errors))  # 每处错误扣 1 分
            score += writing_score  # 将作文得分累加到总分
            results.append({
                "question": q["question"],
                "user_answer": user_answer,
                "errors": errors,
                "score": writing_score
            })
        elif q["type"].startswith("speaking_"):
            audio_data = request.form.get(f'q{i}_audio')
            if audio_data:
                audio_path = f"static/audio_q{i}.wav"
                with open(audio_path, "wb") as f:
                    f.write(base64.b64decode(audio_data))
                transcribed_text = transcribe_audio(audio_path)
                speaking_score = evaluate_speaking(transcribed_text, q["answer"])
                score += speaking_score  # 将口语得分累加到总分
                results.append({
                    "question": q["question"],
                    "transcribed_text": transcribed_text,
                    "score": speaking_score
                })
                os.remove(audio_path)  # 删除临时音频文件
    return render_template('results.html', score=score, total=len(questions) * 10, results=results)

if __name__ == '__main__':
    app.run(debug=True)