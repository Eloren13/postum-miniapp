// web_app/script.js
const tg = window.Telegram.WebApp;
const API_BASE = '';

// ===== СОСТОЯНИЕ =====
let state = {
    questions: [],
    currentIndex: 0,
    score: 0,
    correctCount: 0,
    totalQuestions: 10,
    currentTopic: null,
    filters: { discipline: 'all', topic: 'all', difficulty: 'all' }
};

let user = {
    id: null,
    score: 0,
    level: 1,
    xp: 0,
    correct_answers: 0,
    total_answers: 0,
    daily_streak: 0,
    achievements: []
};

// ===== ИНИЦИАЛИЗАЦИЯ =====
document.addEventListener('DOMContentLoaded', () => {
    tg.expand();
    
    if (tg.initDataUnsafe?.user) {
        user.id = tg.initDataUnsafe.user.id;
    }
    
    loadUserData();
    loadDailyQuestion();
    loadQuickTopics();
    loadDisciplines();
    loadAchievements();
    setupFilters();
});

// ===== API =====
async function api(endpoint, options = {}) {
    try {
        const res = await fetch(`${API_BASE}${endpoint}`, options);
        return await res.json();
    } catch (e) {
        console.error('API Error:', e);
        return null;
    }
}

// ===== НАВИГАЦИЯ =====
function showScreen(id) {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    document.getElementById(id).classList.add('active');
}

function goHome() {
    showScreen('main-screen');
    loadUserData();
}

// ===== ПОЛЬЗОВАТЕЛЬ =====
function loadUserData() {
    const saved = localStorage.getItem('art_quest_user');
    if (saved) {
        user = { ...user, ...JSON.parse(saved) };
        updateUI();
    }
}

function saveUser() {
    localStorage.setItem('art_quest_user', JSON.stringify(user));
    updateUI();
}

function updateUI() {
    document.getElementById('user-score').textContent = user.score || 0;
    document.getElementById('user-level').textContent = user.level || 1;
    document.getElementById('user-xp').textContent = user.xp || 0;
}

// ===== ЕЖЕДНЕВНЫЙ ВЫЗОВ =====
async function loadDailyQuestion() {
    const data = await api('/api/daily');
    if (data?.question) {
        document.getElementById('daily-question').textContent = data.question;
    }
    document.getElementById('daily-streak').textContent = `Серия: ${user.daily_streak || 0}`;
}

function startDaily() {
    startQuiz();
}

// ===== БЫСТРЫЕ ТЕМЫ =====
async function loadQuickTopics() {
    const data = await api('/api/topics/quick');
    if (data?.topics) {
        const container = document.getElementById('quick-topics-container');
        container.innerHTML = data.topics.map(t =>
            `<button class="quick-topic-btn" onclick="startTopicQuiz(${t.id})">${t.icon || '📚'} ${t.name}</button>`
        ).join('');
    }
}

// ===== ДИСЦИПЛИНЫ =====
async function loadDisciplines() {
    const data = await api('/api/disciplines');
    if (data) {
        const container = document.getElementById('disciplines-container');
        container.innerHTML = data.map(d =>
            `<div class="discipline-card" onclick="showSections(${d.id})">
                <span class="icon">${d.icon || '📚'}</span>
                <div class="name">${d.name}</div>
                <div class="desc">${d.description || ''}</div>
            </div>`
        ).join('');
    }
}

function showDisciplines() {
    showScreen('disciplines-screen');
    loadDisciplines();
}

async function showSections(id) {
    const data = await api(`/api/sections/${id}`);
    if (data) {
        showScreen('sections-screen');
        document.getElementById('sections-title').textContent = data.discipline_name || 'Разделы';
        document.getElementById('sections-container').innerHTML = data.sections.map(s =>
            `<div class="section-card" onclick="showTopics(${s.id})">
                <div class="name">${s.name}</div>
                <div class="desc">${s.description || ''}</div>
            </div>`
        ).join('');
    }
}

async function showTopics(id) {
    const data = await api(`/api/topics/${id}`);
    if (data) {
        showScreen('topics-screen');
        document.getElementById('topics-title').textContent = data.section_name || 'Темы';
        document.getElementById('topics-container').innerHTML = data.topics.map(t =>
            `<div class="topic-card" onclick="startTopicQuiz(${t.id})">
                <div class="name">${t.name}</div>
                <div class="desc">${t.description || ''}</div>
                <div class="count">${t.question_count || 0} вопросов</div>
            </div>`
        ).join('');
    }
}

// ===== ОБУЧЕНИЕ =====
function showLearning() {
    showScreen('learning-screen');
    loadLearning();
}

async function loadLearning() {
    const data = await api('/api/learning');
    if (data) {
        document.getElementById('learning-container').innerHTML = data.map(item =>
            `<div class="learning-item" onclick="showMaterial(${item.id})">
                <div class="title">${item.title}</div>
                <div class="desc">${item.description || ''}</div>
            </div>`
        ).join('');
    }
}

async function showMaterial(id) {
    const data = await api(`/api/material/${id}`);
    if (data) {
        showScreen('material-screen');
        document.getElementById('material-title').textContent = data.title;
        document.getElementById('material-content').innerHTML = data.content.replace(/\n/g, '<br>');
        state.currentTopic = data.topic_id;
    }
}

function startQuizFromMaterial() {
    if (state.currentTopic) startTopicQuiz(state.currentTopic);
}

// ===== ВИКТОРИНА =====
function showQuiz() {
    showScreen('quiz-screen');
    setupFilters();
}

async function setupFilters() {
    const data = await api('/api/disciplines');
    if (data) {
        const select = document.getElementById('quiz-discipline');
        select.innerHTML = '<option value="all">Все дисциплины</option>' +
            data.map(d => `<option value="${d.id}">${d.icon || ''} ${d.name}</option>`).join('');
    }
}

async function updateQuizTopics() {
    const disciplineId = document.getElementById('quiz-discipline').value;
    const select = document.getElementById('quiz-topic');
    select.innerHTML = '<option value="all">Все темы</option>';
    if (disciplineId !== 'all') {
        const data = await api(`/api/discipline-topics/${disciplineId}`);
        if (data) data.forEach(t => {
            select.innerHTML += `<option value="${t.id}">${t.name}</option>`;
        });
    }
}

async function startQuiz() {
    state.filters = {
        discipline: document.getElementById('quiz-discipline').value,
        topic: document.getElementById('quiz-topic').value,
        difficulty: document.getElementById('quiz-difficulty').value
    };
    
    let url = '/api/questions/random?limit=10';
    if (state.filters.topic !== 'all') url += `&topic=${state.filters.topic}`;
    if (state.filters.discipline !== 'all') url += `&discipline=${state.filters.discipline}`;
    if (state.filters.difficulty !== 'all') url += `&difficulty=${state.filters.difficulty}`;
    
    const data = await api(url);
    if (data?.length) {
        state.questions = data;
        state.currentIndex = 0;
        state.score = 0;
        state.correctCount = 0;
        showScreen('question-screen');
        showQuestion();
    } else {
        alert('Вопросов по выбранным критериям не найдено.');
    }
}

function startTopicQuiz(id) {
    api(`/api/questions/topic/${id}?limit=10`).then(data => {
        if (data?.length) {
            state.questions = data;
            state.currentIndex = 0;
            state.score = 0;
            state.correctCount = 0;
            showScreen('question-screen');
            showQuestion();
        } else {
            alert('Вопросов по этой теме пока нет.');
        }
    });
}

function showQuestion() {
    if (state.currentIndex >= state.questions.length) {
        showResult();
        return;
    }
    
    const q = state.questions[state.currentIndex];
    document.getElementById('question-counter').textContent = `${state.currentIndex + 1}/${state.questions.length}`;
    document.getElementById('progress-fill').style.width = `${((state.currentIndex + 1) / state.questions.length) * 100}%`;
    document.getElementById('question-text').textContent = q.question;
    document.getElementById('question-topic').textContent = `📚 ${q.topic_name || 'Тема'}`;
    document.getElementById('question-explanation').style.display = 'none';
    
    const container = document.getElementById('options-container');
    container.innerHTML = '';
    JSON.parse(q.options).forEach((opt, i) => {
        const btn = document.createElement('button');
        btn.className = 'option-btn';
        btn.textContent = opt;
        btn.onclick = () => selectAnswer(i, q.correct_answer);
        container.appendChild(btn);
    });
}

function selectAnswer(selected, correct) {
    const btns = document.querySelectorAll('.option-btn');
    btns.forEach((b, i) => {
        b.disabled = true;
        if (i === correct) b.classList.add('correct');
        if (i === selected && selected !== correct) b.classList.add('wrong');
    });
    
    const q = state.questions[state.currentIndex];
    const isCorrect = selected === correct;
    
    if (isCorrect) {
        state.score += 10;
        state.correctCount++;
        user.correct_answers = (user.correct_answers || 0) + 1;
        user.xp = (user.xp || 0) + 15;
    }
    user.total_answers = (user.total_answers || 0) + 1;
    saveUser();
    
    if (q.explanation) {
        const el = document.getElementById('question-explanation');
        el.style.display = 'block';
        el.textContent = '💡 ' + q.explanation;
    }
    
    saveProgress(q.id, isCorrect);
    
    setTimeout(() => {
        state.currentIndex++;
        showQuestion();
    }, 3000);
}

function showResult() {
    showScreen('result-screen');
    const total = state.questions.length;
    const correct = state.correctCount;
    const pct = Math.round((correct / total) * 100);
    
    let emoji = '📚', title = 'Хороший результат!';
    if (pct >= 90) { emoji = '🏆'; title = 'Блестяще! Вы — эрудит!'; }
    else if (pct >= 70) { emoji = '⭐'; title = 'Отлично! Продолжайте!'; }
    else if (pct >= 50) { emoji = '📖'; title = 'Неплохо! Учитесь дальше.'; }
    else { emoji = '💪'; title = 'Ничего страшного! Попробуйте снова.'; }
    
    document.getElementById('result-emoji').textContent = emoji;
    document.getElementById('result-title').textContent = title;
    document.getElementById('result-stats').innerHTML = `
        <div class="stat-row"><span class="label">✅ Правильных ответов</span><span class="value">${correct}/${total}</span></div>
        <div class="stat-row"><span class="label">🎯 Точность</span><span class="value">${pct}%</span></div>
        <div class="stat-row"><span class="label">⭐ Заработано очков</span><span class="value">${state.score}</span></div>
        <div class="stat-row"><span class="label">⚡ Получено XP</span><span class="value">+${correct * 15}</span></div>
    `;
    
    user.score = (user.score || 0) + state.score;
    user.xp = (user.xp || 0) + correct * 15;
    user.level = Math.floor(user.xp / 100) + 1;
    saveUser();
    checkAchievements();
}

// ===== ДОСТИЖЕНИЯ =====
function showAchievements() {
    showScreen('achievements-screen');
    loadAchievements();
}

async function loadAchievements() {
    const data = await api('/api/achievements');
    if (data) {
        document.getElementById('achievements-container').innerHTML = data.map(a =>
            `<div class="achievement ${a.unlocked ? 'unlocked' : 'locked'}">
                <span class="icon">${a.icon || '🏅'}</span>
                <div class="info">
                    <div class="name">${a.name}</div>
                    <div class="desc">${a.description} ${a.unlocked ? '✅' : `(${a.progress || 0}/${a.condition_value})`}</div>
                </div>
            </div>`
        ).join('');
    }
}

async function checkAchievements() {
    const data = await api('/api/check-achievements', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(user)
    });
    if (data?.unlocked?.length) loadAchievements();
}

// ===== СТАТИСТИКА =====
function showStats() {
    showScreen('stats-screen');
    const acc = user.total_answers ? Math.round((user.correct_answers / user.total_answers) * 100) : 0;
    document.getElementById('stats-container').innerHTML = [
        { label: '🏆 Всего очков', value: user.score || 0 },
        { label: '📈 Уровень', value: user.level || 1 },
        { label: '⚡ Опыт (XP)', value: user.xp || 0 },
        { label: '✅ Правильных ответов', value: user.correct_answers || 0 },
        { label: '📝 Всего ответов', value: user.total_answers || 0 },
        { label: '🎯 Точность', value: `${acc}%` },
        { label: '🔥 Серия дней', value: user.daily_streak || 0 }
    ].map(s =>
        `<div class="stat-row"><span class="label">${s.label}</span><span class="value">${s.value}</span></div>`
    ).join('');
}

// ===== ПРОГРЕСС =====
function saveProgress(qId, correct) {
    fetch('/api/progress', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: user.id, question_id: qId, correct })
    }).catch(() => {});
}
