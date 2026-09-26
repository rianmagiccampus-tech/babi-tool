import os
import random
import subprocess
from flask import Flask, render_template_string, request, send_file, redirect, url_for

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Babi Dias | Anti-Rastro Video Tool</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #121212; color: #fff; text-align: center; padding: 20px; margin: 0; }
        .card { background: #1e1e1e; padding: 25px; border-radius: 15px; max-width: 400px; margin: auto; box-shadow: 0 4px 15px rgba(0,0,0,0.5); margin-top: 40px; }
        h2 { color: #ff4757; margin-bottom: 10px; }
        p { color: #a4b0be; font-size: 14px; }
        input[type="file"] { display: none; }
        .file-upload { background: #2f3542; border: 2px dashed #ff4757; padding: 20px; border-radius: 10px; cursor: pointer; display: block; margin: 20px 0; font-weight: bold; color: #ff4757; }
        button { background: #ff4757; color: white; border: none; padding: 12px 20px; border-radius: 8px; font-size: 16px; font-weight: bold; width: 100%; cursor: pointer; }
        button:active { background: #ff6b81; }
        .loading { display: none; margin-top: 15px; color: #ffa502; font-weight: bold; }
    </style>
</head>
<body>
    <div class="card">
        <h2>Babi Dias - Anti-Rastro 🍑</h2>
        <p>Limpe metadados, mude o hash e aplique mutação direto pelo celular.</p>
        
        <form action="/processar" method="POST" enctype="multipart/form-data" onsubmit="mostrarLoading()">
            <label class="file-upload">
                📁 Escolher Vídeo da Galeria
                <input type="file" name="video" accept="video/*" required onchange="atualizarNome(this)">
            </label>
            <p id="nome-arquivo" style="font-size: 12px; color: #fff; margin-bottom: 15px;"></p>
            <button type="submit" id="btn-submit">Gerar Vídeo Único 🚀</button>
            <div id="loading" class="loading">🔄 Processando mutação pesada... Aguarde!</div>
        </form>
    </div>

    <script>
        function atualizarNome(input) {
            if (input.files.length > 0) {
                document.getElementById('nome-arquivo').innerText = "Selecionado: " + input.files[0].name;
            }
        }
        function mostrarLoading() {
            document.getElementById('btn-submit').style.display = 'none';
            document.getElementById('loading').style.display = 'block';
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/processar', methods=['POST'])
def processar():
    if 'video' not in request.files:
        return redirect(url_for('index'))
    
    file = request.files['video']
    if file.filename == '':
        return redirect(url_for('index'))
    
    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    output_filename = f"unico_{file.filename}"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)
    
    file.save(input_path)
    
    zoom_fator = round(random.uniform(1.01, 1.03), 3)
    audio_pitch = round(random.uniform(0.98, 1.02), 3)
    
    comando = [
        'ffmpeg', '-y', '-i', input_path,
        '-vf', f"scale=iw*{zoom_fator}:ih*{zoom_fator},crop=in_w/1.02:in_h/1.02,noise=alls=5:allf=t+u",
        '-af', f"asetrate=44100*{audio_pitch},aresample=44100,atempo=1/{audio_pitch}",
        '-metadata', 'creation_time=2026-09-25T12:00:00Z',
        '-metadata', 'encoder=Lavf60.3.100',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '23', '-c:a', 'aac',
        output_path
    ]
    
    try:
        subprocess.run(comando, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        os.remove(input_path)
        return send_file(output_path, as_attachment=True)
    except Exception as e:
        return f"Erro ao processar vídeo: {e}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)