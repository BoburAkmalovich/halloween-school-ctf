import os
import re
from flask import Flask, jsonify, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "halloween-school-ctf-change-me")

CHALLENGES = [
    {"id":"portrait","number":"01","title":"Портрет, который шепчет","icon":"🖼️","story":"В старом холле висит портрет директора. Каждую полночь его глаза начинают светиться. Он шепчет: «Не всё видно на странице…»","task":"Найди спрятанный флаг на этой странице. Иногда веб-сыщики заглядывают в исходный код страницы: Ctrl+U или «Просмотреть код страницы».","placeholder":"HALLOWEEN{...}","answer":"HALLOWEEN{GHOST_IN_HTML}","hint":"Нажми Ctrl+U и поищи слово HALLOWEEN.","skill":"HTML и исходный код"},
    {"id":"cauldron","number":"02","title":"Шифр ведьминого котла","icon":"🧪","story":"В котле плавает записка. Буквы на ней сдвинуты ровно на три шага вперёд по английскому алфавиту.","task":"Расшифруй сообщение Цезаря: KDOORZHHQ{FDW_VDBV_PHRZ}.","placeholder":"Расшифрованный флаг","answer":"HALLOWEEN{CAT_SAYS_MEOW}","hint":"Чтобы отменить шифр, сдвигай каждую английскую букву на 3 назад: K→H, D→A.","skill":"Шифр Цезаря"},
    {"id":"robot","number":"03","title":"Запретная комната","icon":"🚪","story":"Школьный робот-уборщик знает, в какие комнаты ему нельзя заходить. Его список правил лежит в стандартном файле сайта.","task":"Открой /robots.txt, найди запретный путь и перейди по нему. Там спрятан следующий флаг.","placeholder":"Флаг из тайной комнаты","answer":"HALLOWEEN{ROBOTS_ARE_AFRAID}","hint":"Добавь /robots.txt после адреса сайта в строке браузера.","skill":"robots.txt и пути сайта"},
    {"id":"bat","number":"04","title":"Радио летучих мышей","icon":"🦇","story":"Стая летучих мышей передаёт короткие и длинные писки. На диктофоне записано: .... .- .-.. .-.. --- .-- . . -. / -... .- -","task":"Определи код и расшифруй два слова. Запиши ответ как HALLOWEEN{ДВА_СЛОВА}.","placeholder":"HALLOWEEN{...}","answer":"HALLOWEEN{HALLOWEEN_BAT}","hint":"Это азбука Морзе. Слэш разделяет слова, пробелы — буквы.","skill":"Азбука Морзе"},
    {"id":"mirror","number":"05","title":"Зеркало полуночи","icon":"🪞","story":"Последняя дверь отражается в старом зеркале. Надпись можно прочитать, только если развернуть её задом наперёд.","task":"Разверни строку: }DEKCAB_TON_SI_TI{NEEWOLLAH","placeholder":"Финальный флаг","answer":"HALLOWEEN{IT_IS_NOT_BACKED}","hint":"Читай строку с последнего символа к первому.","skill":"Преобразование строк"},
]

def normalize(value):
    return re.sub(r"\s+", "", value or "").upper()

@app.get("/")
def index(): return render_template("index.html", total=len(CHALLENGES))

@app.post("/start")
def start():
    session.clear(); session["name"]=(request.form.get("name") or "Охотник").strip()[:24]; session["level"]=0; session["hints"]=0
    return redirect(url_for("game"))

@app.get("/game")
def game():
    if "name" not in session: return redirect(url_for("index"))
    level=min(session.get("level",0),len(CHALLENGES))
    if level>=len(CHALLENGES): return redirect(url_for("finish"))
    return render_template("game.html",challenge=CHALLENGES[level],level=level,total=len(CHALLENGES),name=session["name"])

@app.post("/check")
def check():
    level=session.get("level",0)
    if "name" not in session or level>=len(CHALLENGES): return jsonify(ok=False,message="Сначала начни игру."),400
    if normalize(request.form.get("flag"))==normalize(CHALLENGES[level]["answer"]):
        session["level"]=level+1; return jsonify(ok=True,message="Печать разрушена! Дверь открыта.")
    return jsonify(ok=False,message="Заклинание не сработало. Проверь флаг и попробуй снова.")

@app.post("/hint")
def hint():
    level=session.get("level",0)
    if level>=len(CHALLENGES): return jsonify(hint="Все тайны уже раскрыты!")
    session["hints"]=session.get("hints",0)+1
    return jsonify(hint=CHALLENGES[level]["hint"])

@app.get("/finish")
def finish():
    if session.get("level",0)<len(CHALLENGES): return redirect(url_for("game"))
    return render_template("finish.html",name=session.get("name","Охотник"),hints=session.get("hints",0),challenges=CHALLENGES)

@app.get("/robots.txt")
def robots(): return "User-agent: *\nDisallow: /basement-13\n# Роботы боятся темноты...\n",200,{"Content-Type":"text/plain; charset=utf-8"}

@app.get("/basement-13")
def basement():
    return """<!doctype html><meta charset=utf-8><title>Подвал №13</title><style>body{background:#08060b;color:#ffb347;font:20px monospace;display:grid;place-items:center;min-height:100vh;text-align:center}div{padding:40px;border:1px solid #6d3b12}</style><div><h1>Ты нашёл запретную комнату!</h1><p>HALLOWEEN{ROBOTS_ARE_AFRAID}</p><small>Скопируй флаг и возвращайся назад.</small></div>"""

@app.get("/health")
def health(): return jsonify(status="ok")

if __name__=="__main__": app.run(host="0.0.0.0",port=8080,debug=False)
