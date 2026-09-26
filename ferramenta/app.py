import os
import random
import subprocess
import sys
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
        .spinner { border: 4px solid rgba(255,255,255,0.1); width: 36px; height: 36px; border-radius: 50%; border-left-color: #ff4757; animation: spin 1s linear infinite; margin: 15px auto; display: none; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <div class="card">
        <h2>Babi Dias - Anti-Rastro 🍑</h2>
        <p>Modo Econômico de RAM Ativado</p>
        
        <form action="/processar" method="POST" enctype="multipart/form-data" onsubmit="mostrarLoading()">
            <label class="file-upload" id="label-file">
                📁 Escolher Vídeo da Galeria
                <input type="file" name="video" accept="video/*" required onchange="atualizarNome(this)">
            </label>
            <p id="nome-arquivo" style="font-size: 13px; color: #2ed573; margin-bottom: 15px; font-weight: bold;"></p>
            <button type="submit" id="btn-submit">Gerar Vídeo Único 🚀</button>
            <div class="spinner" id="spinner"></div>
            <div id="loading" class="loading">🔄 Otimizando e mutando vídeo... Aguarde o download!</div>
        </form>
    </div>

    <script>
        function atualizarNome(input) {
            if (input.files.length > 0) {
                document.getElementById('nome-arquivo').innerText = "Selecionado: " + input.files[0].name;
                document.getElementById('label-file').style.borderColor = "#2ed573";
            }
        }
        function mostrarLoading() {
            document.getElementById('btn-submit').style.display = 'none';
            document.getElementById('spinner').style.display = 'block';
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
    
    print(f"[LOG] 📥 Baixando arquivo para o servidor: {file.filename}", file=sys.stdout)
    file.save(input_path)
    
    zoom_fator = round(random.uniform(1.01, 1.02), 3)
    audio_pitch = round(random.uniform(0.99, 1.01), 3)
    
    # FORÇA A RESOLUÇÃO PARA 720p (HD) MÁXIMO PARA POUPAR A RAM DO RENDER
    # E usa preset ultrafast com threads limitadas
    comando = [
        'ffmpeg', '-y', '-i', input_path,
        '-vf', f"scale=720:-2,zoompan=z={zoom_fator}:d=1:s=720x1280",
        '-af', f"asetrate=44100*{audio_pitch},aresample=44100,atempo=1/{audio_pitch}",
        '-metadata', 'creation_time=2026-09-25T12:00:00Z',
        '-metadata', 'encoder=Lavf60.3.100',
        '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '28', '-threads', '2', '-c:a', 'aac',
        output_path
    ]
    
    # Se o zoompan falhar em algum formato exótico, tentamos um filtro de escala simples e seguro:
    comando_alternativo = [
        'ffmpeg', '-y', '-i', input_path,
        '-vf', f"scale=720:1280,setsar=1",
        '-af', f"asetrate=44100*{audio_pitch},aresample=44100,atempo=1/{audio_pitch}",
        '-metadata', 'creation_time=2026-09-25T12:00:00Z',
        '-metadata', 'encoder=Lavf60.3.100',
        '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '28', '-threads', '2', '-c:a', 'aac',
        output_path
    ]

    try:
        print("[LOG] 🚀 Rodando FFmpeg com limite de RAM...", file=sys.stdout)
        resultado = subprocess.run(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if resultado.returncode != 0:
            print("[LOG] ⚠️ Tentando método alternativo de renderização...", file=sys.stdout)
            subprocess.run(comando_alternativo, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        print("[LOG] ✨ Sucesso! Enviando arquivo processado.", file=sys.stdout)
        return send_file(output_path, as_attachment=True)

    except Exception as e:
        print(f"[LOG] ❌ Erro no processamento: {str(e)}", file=sys.stderr)
        return f"Erro ao processar o vídeo: O arquivo pode ser muito pesado para a nuvem gratuita. Tente um vídeo mais curto.", 500
    
    finally:
        if os.path.exists(input_path):
            try: os.remove(input_path)
            except: pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)