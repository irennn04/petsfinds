import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum
import hashlib
import secrets
import json
import base64
from dataclasses import dataclass, asdict
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os

# ===================== МОДЕЛИ ДАННЫХ =====================

class PlatformType(Enum):
    ANIMAL_ID = "animal-id"
    PETLINK = "petlink"
    HOMEAGAIN = "homeagain"
    SMARTTAG = "smarttag"
    EUROPETNET = "europetnet"
    FINDBEST = "findbest"

@dataclass
class PetData:
    microchip_id: str
    pet_name: str
    species: str
    breed: str
    color: str
    birth_date: str
    owner_name: str
    owner_phone: str
    owner_email: str
    address: str
    medical_notes: Optional[str] = None
    emergency_contact: Optional[str] = None

# ===================== ОСНОВНОЙ КЛАСС =====================

class UnifiedPetRegistry:
    """Единый реестр питомцев"""
    
    def __init__(self):
        self.registry = {}
        
    async def register_pet_globally(self, pet_data: PetData) -> Dict:
        """Регистрация питомца"""
        
        # Генерируем уникальный ID
        unified_id = hashlib.sha256(
            f"{pet_data.microchip_id}{datetime.now().timestamp()}".encode()
        ).hexdigest()[:16]
        
        # Создаём запись
        record = {
            'unified_id': unified_id,
            'microchip_id': pet_data.microchip_id,
            'pet_name': pet_data.pet_name,
            'species': pet_data.species,
            'breed': pet_data.breed,
            'color': pet_data.color,
            'birth_date': pet_data.birth_date,
            'owner_name': self._encrypt(pet_data.owner_name),
            'owner_phone': self._encrypt(pet_data.owner_phone),
            'owner_email': self._encrypt(pet_data.owner_email),
            'address': self._encrypt(pet_data.address),
            'medical_notes': pet_data.medical_notes,
            'emergency_contact': pet_data.emergency_contact,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'platforms': {}
        }
        
        # Имитируем регистрацию в разных базах
        platforms = ['Animal-ID', 'HomeAgain', 'EuroPetNet', 'Tasso', 'PetLink', 'FindBest']
        
        for platform in platforms:
            record['platforms'][platform] = {
                'status': 'registered',
                'registered_at': datetime.now().isoformat(),
                'platform_id': hashlib.md5(
                    f"{platform}{pet_data.microchip_id}".encode()
                ).hexdigest()[:10]
            }
        
        # Сохраняем запись
        self.registry[unified_id] = record
        
        return {
            'status': 'success',
            'unified_id': unified_id,
            'microchip_id': pet_data.microchip_id,
            'platforms_registered': len(platforms),
            'message': f'Питомец {pet_data.pet_name} успешно зарегистрирован в {len(platforms)} базах!'
        }
    
    async def search_pet(self, microchip_id: str) -> Dict:
        """Поиск питомца по чипу"""
        
        # Ищем в реестре
        for uid, record in self.registry.items():
            if record['microchip_id'] == microchip_id:
                return {
                    'found': True,
                    'pet_data': {
                        'pet_name': record['pet_name'],
                        'species': record['species'],
                        'breed': record['breed'],
                        'color': record['color'],
                        'birth_date': record['birth_date'],
                        'unified_id': uid
                    },
                    'platforms': record['platforms'],
                    'message': 'Питомец найден!'
                }
        
        # Если не нашли - имитируем поиск по внешним базам
        return {
            'found': False,
            'microchip_id': microchip_id,
            'platforms_checked': {
                'Animal-ID': {'status': 'not_found'},
                'HomeAgain': {'status': 'not_found'},
                'EuroPetNet': {'status': 'not_found'},
                'Tasso': {'status': 'not_found'},
                'PetLink': {'status': 'not_found'},
                'FindBest': {'status': 'not_found'}
            },
            'message': 'Питомец не найден в базах данных'
        }
    
    def _encrypt(self, data: str) -> str:
        """Шифрование данных (заглушка)"""
        return base64.b64encode(data.encode()).decode()

# ===================== СОЗДАЁМ ПРИЛОЖЕНИЕ =====================

app = FastAPI(title="🐾 UniPet - Единая база чипированных животных")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Создаём экземпляр реестра
registry = UnifiedPetRegistry()

# ===================== HTML СТРАНИЦА =====================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🐾 UniPet - Единая база чипированных животных</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            color: white;
            padding: 30px 0;
        }
        
        .header h1 {
            font-size: 42px;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        
        .header p {
            font-size: 18px;
            opacity: 0.9;
        }
        
        .card {
            background: white;
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        
        .card-title {
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 20px;
            color: #2C3E50;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .search-box {
            display: flex;
            gap: 10px;
        }
        
        .search-input {
            flex: 1;
            padding: 15px 20px;
            border: 2px solid #E1E8ED;
            border-radius: 15px;
            font-size: 16px;
            outline: none;
            transition: border-color 0.3s;
        }
        
        .search-input:focus {
            border-color: #667eea;
        }
        
        .btn {
            padding: 15px 30px;
            border: none;
            border-radius: 15px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            color: white;
        }
        
        .btn-search {
            background: linear-gradient(135deg, #667eea, #764ba2);
        }
        
        .btn-search:hover {
            transform: scale(1.05);
        }
        
        .btn-register {
            background: linear-gradient(135deg, #2ECC71, #27AE60);
            width: 100%;
            margin-top: 10px;
        }
        
        .btn-register:hover {
            transform: scale(1.02);
        }
        
        .form-group {
            margin-bottom: 15px;
        }
        
        .form-label {
            display: block;
            font-weight: 600;
            margin-bottom: 5px;
            color: #2C3E50;
            font-size: 14px;
        }
        
        .form-input {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #E1E8ED;
            border-radius: 10px;
            font-size: 15px;
            outline: none;
            transition: border-color 0.3s;
        }
        
        .form-input:focus {
            border-color: #667eea;
        }
        
        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }
        
        .result {
            margin-top: 20px;
            padding: 20px;
            border-radius: 15px;
            display: none;
        }
        
        .result.show {
            display: block;
        }
        
        .result.success {
            background: #D5F5E3;
            border: 2px solid #2ECC71;
        }
        
        .result.info {
            background: #EBF5FB;
            border: 2px solid #3498DB;
        }
        
        .result.error {
            background: #FADBD8;
            border: 2px solid #E74C3C;
        }
        
        .platform-list {
            list-style: none;
            margin-top: 15px;
        }
        
        .platform-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 10px 15px;
            background: white;
            border-radius: 10px;
            margin-bottom: 8px;
        }
        
        .status-badge {
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }
        
        .status-badge.registered {
            background: #D5F5E3;
            color: #27AE60;
        }
        
        .status-badge.not-found {
            background: #FDEBD0;
            color: #E67E22;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .stat-item {
            text-align: center;
            padding: 20px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .stat-number {
            font-size: 36px;
            font-weight: 800;
            color: #667eea;
        }
        
        .stat-label {
            font-size: 14px;
            color: #7F8C8D;
            margin-top: 5px;
        }
        
        @media (max-width: 600px) {
            .form-row { grid-template-columns: 1fr; }
            .search-box { flex-direction: column; }
            .stats { grid-template-columns: 1fr; }
            .header h1 { font-size: 28px; }
        }
        
        .emoji-large { font-size: 60px; text-align: center; margin: 20px 0; }
        
        .loading {
            display: inline-block;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🐾 UniPet</h1>
            <p>Международная база чипированных животных</p>
        </div>
        
        <div class="stats">
            <div class="stat-item">
                <div class="stat-number">1.2M+</div>
                <div class="stat-label">Питомцев в базе</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">47</div>
                <div class="stat-label">Стран</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">6</div>
                <div class="stat-label">Подключённых баз</div>
            </div>
        </div>
        
        <!-- ПОИСК -->
        <div class="card">
            <div class="card-title">🔍 Поиск питомца по чипу</div>
            <div class="search-box">
                <input type="text" class="search-input" id="searchInput" 
                       placeholder="Введите 15-значный номер чипа" maxlength="15">
                <button class="btn btn-search" onclick="searchPet()">🔍 Найти</button>
            </div>
            <div id="searchResult" class="result"></div>
        </div>
        
        <!-- РЕГИСТРАЦИЯ -->
        <div class="card">
            <div class="card-title">📝 Регистрация питомца</div>
            <form id="registerForm">
                <div class="form-group">
                    <label class="form-label">Номер чипа *</label>
                    <input type="text" class="form-input" id="chipId" placeholder="15 цифр" maxlength="15" required>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label class="form-label">Кличка *</label>
                        <input type="text" class="form-input" id="petName" placeholder="Барсик" required>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Вид *</label>
                        <select class="form-input" id="species" required>
                            <option value="">Выберите...</option>
                            <option value="Собака">🐕 Собака</option>
                            <option value="Кошка">🐈 Кошка</option>
                            <option value="Другое">🐾 Другое</option>
                        </select>
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label class="form-label">Порода</label>
                        <input type="text" class="form-input" id="breed" placeholder="Лабрадор">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Окрас</label>
                        <input type="text" class="form-input" id="color" placeholder="Чёрный">
                    </div>
                </div>
                <div class="form-group">
                    <label class="form-label">Дата рождения</label>
                    <input type="date" class="form-input" id="birthDate">
                </div>
                <div class="form-group">
                    <label class="form-label">Имя владельца *</label>
                    <input type="text" class="form-input" id="ownerName" placeholder="Иван Петров" required>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label class="form-label">Телефон *</label>
                        <input type="tel" class="form-input" id="ownerPhone" placeholder="+7 (900) 000-00-00" required>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Email *</label>
                        <input type="email" class="form-input" id="ownerEmail" placeholder="ivan@example.com" required>
                    </div>
                </div>
                <button type="submit" class="btn btn-register">✅ Зарегистрировать питомца</button>
            </form>
            <div id="registerResult" class="result"></div>
        </div>
    </div>
    
    <script>
        async function searchPet() {
            const chipId = document.getElementById('searchInput').value.trim();
            const resultDiv = document.getElementById('searchResult');
            
            if (!chipId || chipId.length !== 15) {
                resultDiv.className = 'result error show';
                resultDiv.innerHTML = '❌ Пожалуйста, введите 15-значный номер чипа';
                return;
            }
            
            resultDiv.className = 'result info show';
            resultDiv.innerHTML = '<span class="loading">⏳</span> Ищем по международным базам...';
            
            try {
                const response = await fetch(`/api/search/${chipId}`);
                const data = await response.json();
                
                if (data.found) {
                    resultDiv.className = 'result success show';
                    resultDiv.innerHTML = `
                        <h3>✅ Питомец найден!</h3>
                        <p><strong>Кличка:</strong> ${data.pet_data.pet_name}</p>
                        <p><strong>Вид:</strong> ${data.pet_data.species}</p>
                        <p><strong>Порода:</strong> ${data.pet_data.breed || 'Не указана'}</p>
                        <p><strong>Окрас:</strong> ${data.pet_data.color || 'Не указан'}</p>
                        <p><strong>Дата рождения:</strong> ${data.pet_data.birth_date || 'Не указана'}</p>
                        <h4 style="margin-top:15px;">📋 Статус в базах:</h4>
                        <ul class="platform-list">
                            ${Object.entries(data.platforms).map(([name, info]) => `
                                <li class="platform-item">
                                    <span>${name}</span>
                                    <span class="status-badge ${info.status === 'registered' ? 'registered' : 'not-found'}">
                                        ${info.status === 'registered' ? '✅ Зарегистрирован' : '❌ Не найден'}
                                    </span>
                                </li>
                            `).join('')}
                        </ul>
                    `;
                } else {
                    resultDiv.className = 'result error show';
                    resultDiv.innerHTML = `
                        <h3>❌ Питомец не найден</h3>
                        <p>Чип ${data.microchip_id} не зарегистрирован ни в одной базе</p>
                        <p>Пожалуйста, <a href="#registerForm" style="color: #667eea;">зарегистрируйте</a> питомца</p>
                    `;
                }
            } catch (error) {
                resultDiv.className = 'result error show';
                resultDiv.innerHTML = '❌ Ошибка при поиске. Попробуйте позже.';
            }
        }
        
        document.getElementById('registerForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const resultDiv = document.getElementById('registerResult');
            
            const petData = {
                microchip_id: document.getElementById('chipId').value,
                pet_name: document.getElementById('petName').value,
                species: document.getElementById('species').value,
                breed: document.getElementById('breed').value,
                color: document.getElementById('color').value,
                birth_date: document.getElementById('birthDate').value,
                owner_name: document.getElementById('ownerName').value,
                owner_phone: document.getElementById('ownerPhone').value,
                owner_email: document.getElementById('ownerEmail').value,
                address: '',
                medical_notes: null,
                emergency_contact: null
            };
            
            resultDiv.className = 'result info show';
            resultDiv.innerHTML = '<span class="loading">⏳</span> Регистрируем в международных базах...';
            
            try {
                const response = await fetch('/api/register', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(petData)
                });
                
                const data = await response.json();
                
                if (data.status === 'success') {
                    resultDiv.className = 'result success show';
                    resultDiv.innerHTML = `
                        <div class="emoji-large">🎉</div>
                        <h3>✅ ${data.message}</h3>
                        <p><strong>ID регистрации:</strong> ${data.unified_id}</p>
                        <p><strong>Зарегистрирован в базах:</strong> ${data.platforms_registered}</p>
                        <p style="margin-top: 10px; color: #7F8C8D;">
                            📱 Скачайте мобильное приложение для подтверждения данных
                        </p>
                    `;
                    document.getElementById('registerForm').reset();
                }
            } catch (error) {
                resultDiv.className = 'result error show';
                resultDiv.innerHTML = '❌ Ошибка при регистрации. Попробуйте позже.';
            }
        });
        
        // Поиск по Enter
        document.getElementById('searchInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') searchPet();
        });
    </script>
</body>
</html>
"""

# ===================== API РОУТЫ =====================

@app.get("/", response_class=HTMLResponse)
async def home():
    """Главная страница"""
    return HTML_TEMPLATE

@app.get("/api/search/{microchip_id}")
async def search_pet(microchip_id: str):
    """Поиск питомца по чипу"""
    result = await registry.search_pet(microchip_id)
    return result

@app.post("/api/register")
async def register_pet(pet_data: PetData):
    """Регистрация питомца"""
    result = await registry.register_pet_globally(pet_data)
    return result

@app.get("/api/health")
async def health_check():
    """Проверка работоспособности"""
    return {
        "status": "OK",
        "timestamp": datetime.now().isoformat(),
        "service": "UniPet Registry",
        "version": "1.0.0"
    }

# ===================== ЗАПУСК =====================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)