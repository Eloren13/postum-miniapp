// web_app/script.js
let tg = window.Telegram.WebApp;
let currentState = {
    questions: [],
    currentIndex: 0,
    score: 0,
    correctCount: 0,
    currentTopic: null,
    currentDiscipline: null,
    totalQuestions: 10,
    filters: {
        discipline: 'all',
        topic: 'all',
        difficulty: 'all'
    }
};

let userData = {
    id: null,
    score: 0,
    level: 1,
    xp: 0,
    correct_answers: 0,
    total_answers: 0,
    daily_streak: 0,
    achievements: []
};

// Инициализация
document.addEventListener('DOMContentLoaded', function() {
    tg.expand();
    
    if (tg.initDataUnsafe && tg.initDataUnsafe.user) {
        userData.id = tg.initDataUnsafe.user.id;
        document.getElementById('user-name').textContent = tg.initDataUnsafe.user.first_name || 'Игрок';
    }
    
    loadUserData();
    loadDailyQuestion();
    loadQuickTopics();
    loadDisciplines();
    loadAchievements();
    setupQuizFilters();
});

// API Calls
const API_BASE = '';

async function apiCall(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, options);
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        return null;
    }
}

// Navigation
function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    document.getElementById(screenId).classList.add('active');
}

function goHome() {
    showScreen('main-screen');
    loadUserData();
}

// User Data
function loadUserData() {
    const saved = localStorage.getItem('art_quest_user');
    if (saved) {
        const data = JSON.parse(saved);
        userData = {...userData, ...data};
        updateUI();
    }
}

function saveUserData() {
    localStorage.setItem('art_quest_user', JSON.stringify(userData));
    updateUI();
}

function updateUI() {
    document.getElementById('user-score').textContent = `⭐ ${userData.score || 0}`;
    document.getElementById('user-level').textContent = `🏆 Ур.${userData.level || 1}`;
    document.getElementById('user-xp').textContent = `⚡ ${userData.xp || 0} XP`;
}

// Daily Challenge
async function loadDailyQuestion() {
    const data = await apiCall('/api/daily');
    if (data && data.question) {
        document.getElementById('daily-question').textContent = data.question;
    }
    document.getElementById('daily-streak').textContent = `🔥 Серия: ${userData.daily_streak || 0} дней`;
}

function startDaily() {
    startQuiz();
}

// Quick Topics
async function loadQuickTopics() {
    const data = await apiCall('/api/topics/quick');
    if (data && data.topics) {
        const container = document.getElementById('quick-topics-container');
        container.innerHTML = data.topics.slice(0, 4).map(t => 
            `<button class="quick-topic-btn" onclick="startTopicQuiz(${t.id})">${t.icon || '📚'} ${t.name}</button>`
        ).join('');
    }
}

// Disciplines
async function loadDisciplines() {
    const data = await apiCall('/api/disciplines');
    if (data) {
        const container = document.getElementById('disciplines-container');
        container.innerHTML = data.map(d => `
            <div class="discipline-card" onclick="showSections(${d.id})" style="border-color: ${d.color || 'transparent'}">
                <span class="icon">${d.icon || '📚'}</span>
                <div class="name">${d.name}</div>
                <div class="desc">${d.description || ''}</div>
            </div>
        `).join('');
    }
}

async function showSections(disciplineId) {
    currentState.currentDiscipline = disciplineId;
    const data = await apiCall(`/api/sections/${disciplineId}`);
    if (data) {
        showScreen('sections-screen');
        document.getElementById('sections-title').textContent = data.discipline_name || 'Разделы';
        const container = document.getElementById('sections-container');
        container.innerHTML = data.sections.map(s => `
            <div class="section-card" onclick="showTopics(${s.id})">
                <div class="name">${s.name}</div>
                <div class="desc">${s.description || ''}</div>
            </div>
        `).join('');
    }
}

async function showTopics(sectionId) {
    const data = await apiCall(`/api/topics/${sectionId}`);
    if (data) {
        showScreen('topics-screen');
        document.getElementById('topics-title').textContent = data.section_name || 'Темы';
        const container = document.getElementById('topics-container');
        container.innerHTML = data.topics.map(t => `
            <div class="topic-card" onclick="startTopicQuiz(${t.id})">
                <div class="name">${t.name}</div>
                <div class="desc">${t.description || ''}</div>
                <div style="font-size:11px;color:#888;margin-top:4px;">${t.question_count || 0} вопросов</div>
            </div>
        `).join('');
    }
}

// Learning
function showLearning() {
    showScreen('learning-screen');
    loadLearningMaterials();
}

async function loadLearningMaterials() {
    const data = await apiCall('/api/learning');
    if (data) {
        const container = document.getElementById('learning-container');
        container.innerHTML = data.map(item => `
            <div class="learning-item" onclick="showMaterial(${item.id})">
                <div class="title">${item.title}</div>
                <div class="description">${item.description || ''}</div>
            </div>
        `).join('');
    }
}

async function showMaterial(materialId) {
    const data = await apiCall(`/api/material/${materialId}`);
    if (data) {
        showScreen('material-screen');
        document.getElementById('material-title').textContent = data.title;
        document.getElementById('material-content').innerHTML = data.content.replace(/\n/g, '<br>');
        currentState.currentTopic = data.topic_id;
    }
}

function startQuizFromMaterial() {
    if (currentState.currentTopic) {
        startTopicQuiz(currentState.currentTopic);
    }
}

// Quiz
function showQuiz() {
    showScreen('quiz-screen');
    setupQuizFilters();
}

async function setupQuizFilters() {
    const disciplines = await apiCall('/api/disciplines');
    if (disciplines) {
        const select = document.getElementById('quiz-discipline');
        select.innerHTML = '<option value="all">Все дисциплины</option>' + 
            disciplines.map(d => `<option value="${d.id}">${d.icon || ''} ${d.name}</option>`).join('');
    }
}

async function updateQuizTopics() {
    const disciplineId = document.getElementById('quiz-discipline').value;
    const select = document.getElementById('quiz-topic');
    select.innerHTML = '<option value="all">Все темы</option>';
    
    if (disciplineId !== 'all') {
        const data = await apiCall(`/api/discipline-topics/${disciplineId}`);
        if (data) {
            data.forEach(t => {
                select.innerHTML += `<option value="${t.id}">${t.name}</option>`;
            });
        }
    }
}

async function startQuiz() {
    currentState.filters = {
        discipline: document.getElementById('quiz-discipline').value,
        topic: document.getElementById('quiz-topic').value,
        difficulty: document.getElementById('quiz-difficulty').value
    };
    
    // Строим URL запроса
    let url = '/api/questions/random?limit=10';
    if (currentState.filters.topic !== 'all') url += `&topic=${currentState.filters.topic}`;
    if (currentState.filters.discipline !== 'all') url += `&discipline=${currentState.filters.discipline}`;
    if (currentState.filters.difficulty !== 'all') url += `&difficulty=${currentState.filters.difficulty}`;
    
    const data = await apiCall(url);
    if (data && data.length > 0) {
        currentState.questions = data;
        currentState.currentIndex = 0;
        currentState.score = 0;
        currentState.correctCount = 0;
        showScreen('question-screen');
        showQuestion();
    } else {
        alert('К сожалению, вопросов по выбранным критериям не найдено. Попробуйте другие фильтры.');
    }
}

function startTopicQuiz(topicId) {
    currentState.currentTopic = topicId;
    apiCall(`/api/questions/topic/${topicId}?limit=10`)
        .then(data => {
            if (data && data.length > 0) {
                currentState.questions = data;
                currentState.currentIndex = 0;
                currentState.score = 0;
                currentState.correctCount = 0;
                showScreen('question-screen');
                showQuestion();
            } else {
                alert('Вопросов по этой теме пока нет.');
            }
        });
}

function showQuestion() {
    if (currentState.currentIndex >= currentState.questions.length) {
        showResult();
        return;
    }
    
    const q = currentState.questions[currentState.currentIndex];
    document.getElementById('question-counter').textContent = 
        `${currentState.currentIndex + 1}/${currentState.questions.length}`;
    document.getElementById('progress-fill').style.width = 
        `${((currentState.currentIndex + 1) / currentState.questions.length) * 100}%`;
    document.getElementById('question-text').textContent = q.question;
    document.getElementById('question-topic').textContent = q.topic_name || '';
    document.getElementById('question-explanation').style.display = 'none';
    
    const container = document.getElementById('options-container');
    container.innerHTML = '';
    
    const options = JSON.parse(q.options);
    options.forEach((option, index) => {
        const btn = document.createElement('button');
        btn.className = 'option-btn';
        btn.textContent = option;
        btn.dataset.index = index;
        btn.onclick = () => selectAnswer(index, q.correct_answer);
        container.appendChild(btn);
    });
}

function selectAnswer(selected, correct) {
    const buttons = document.querySelectorAll('.option-btn');
    buttons.forEach((btn, index) => {
        btn.disabled = true;
        if (index === correct) btn.classList.add('correct');
        if (index === selected && selected !== correct) btn.classList.add('wrong');
    });
    
    const q = currentState.questions[currentState.currentIndex];
    const isCorrect = selected === correct;
    
    if (isCorrect) {
        currentState.score += 10;
        currentState.correctCount++;
        userData.correct_answers = (userData.correct_answers || 0) + 1;
        userData.xp = (userData.xp || 0) + 15;
    }
    userData.total_answers = (userData.total_answers || 0) + 1;
    saveUserData();
    
    // Показываем объяснение
    if (q.explanation) {
        const expl = document.getElementById('question-explanation');
        expl.style.display = 'block';
        expl.textContent = '💡 ' + q.explanation;
    }
    
    // Отправляем прогресс на сервер
    saveProgress(q.id, isCorrect);
    
    setTimeout(() => {
        currentState.currentIndex++;
        showQuestion();
    }, 3000);
}

function showResult() {
    showScreen('result-screen');
    const total = currentState.questions.length;
    const correct = currentState.correctCount;
    const percentage = Math.round((correct / total) * 100);
    const earnedXP = correct * 15;
    
    let title = '📚 Хороший результат!';
    let emoji = '👍';
    if (percentage >= 90) { title = '🌟 Блестяще! Вы настоящий эрудит!'; emoji = '🏆'; }
    else if (percentage >= 70) { title = '🎯 Отлично! Продолжайте в том же духе!'; emoji = '⭐'; }
    else if (percentage >= 50) { title = '📖 Неплохо! Почитайте материалы и попробуйте снова.'; emoji = '📚'; }
    else { title = '💪 Ничего страшного! Каждая ошибка — это новый урок.'; emoji = '🎓'; }
    
    document.getElementById('result-title').textContent = `${emoji} ${title}`;
    document.getElementById('result-stats').innerHTML = `
        <div class="stat-item"><span class="label">Правильных ответов</span><span class="value">${correct}/${total}</span></div>
        <div class="stat-item"><span class="label">Процент правильных</span><span class="value">${percentage}%</span></div>
        <div class="stat-item"><span class="label">Набрано очков</span><span class="value">${currentState.score}</span></div>
        <div class="stat-item"><span class="label">Заработано XP</span><span class="value">+${earnedXP}</span></div>
    `;
    
    userData.score = (userData.score || 0) + currentState.score;
    userData.xp = (userData.xp || 0) + earnedXP;
    userData.level = Math.floor(userData.xp / 100) + 1;
    saveUserData();
    checkAchievements();
}

// Achievements
async function loadAchievements() {
    const data = await apiCall('/api/achievements');
    if (data) {
        const container = document.getElementById('achievements-container');
        container.innerHTML = data.map(a => `
            <div class="achievement ${a.unlocked ? 'unlocked' : 'locked'}">
                <span class="icon">${a.icon || '🏅'}</span>
                <div class="info">
                    <div class="name">${a.name}</div>
                    <div class="desc">${a.description} ${a.unlocked ? '✅' : `(${a.progress || 0}/${a.condition_value})`}</div>
                </div>
            </div>
        `).join('');
    }
}

async function checkAchievements() {
    const data = await apiCall('/api/check-achievements', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(userData)
    });
    if (data && data.unlocked) {
        loadAchievements();
    }
}

// Stats
function showStats() {
    showScreen('stats-screen');
    const container = document.getElementById('stats-container');
    container.innerHTML = `
        <div class="stat-item"><span class="label">🏆 Всего очков</span><span class="value">${userData.score || 0}</span></div>
        <div class="stat-item"><span class="label">📈 Уровень</span><span class="value">${userData.level || 1}</span></div>
        <div class="stat-item"><span class="label">⚡ Опыт (XP)</span><span class="value">${userData.xp || 0}</span></div>
        <div class="stat-item"><span class="label">✅ Правильных ответов</span><span class="value">${userData.correct_answers || 0}</span></div>
        <div class="stat-item"><span class="label">📝 Всего ответов</span><span class="value">${userData.total_answers || 0}</span></div>
        <div class="stat-item"><span class="label">🎯 Точность</span><span class="value">${userData.total_answers ? Math.round((userData.correct_answers / userData.total_answers) * 100) : 0}%</span></div>
        <div class="stat-item"><span class="label">🔥 Серия дней</span><span class="value">${userData.daily_streak || 0}</span></div>
        <div class="stat-item"><span class="label">🏅 Достижений</span><span class="value">${userData.achievements ? userData.achievements.length : 0}</span></div>
    `;
}

function showDisciplines() {
    showScreen('disciplines-screen');
    loadDisciplines();
}

function showAchievements() {
    showScreen('achievements-screen');
    loadAchievements();
}

// Progress saving
function saveProgress(questionId, correct) {
    // Отправляем на сервер (если доступен)
    const data = {
        user_id: userData.id,
        question_id: questionId,
        correct: correct
    };
    
    fetch('/api/progress', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    }).catch(() => { /* Игнорируем ошибки */ });
}
