// web_app/script.js
// Заглушка на случай открытия вне Telegram (например, при тестировании
// в обычном браузере) — приложение не должно падать без Telegram API.
const tg = (window.Telegram && window.Telegram.WebApp) ? window.Telegram.WebApp : {
    ready() {}, expand() {},
    initDataUnsafe: {},
    colorScheme: window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'dark' : 'light',
    onEvent() {}, offEvent() {},
    setHeaderColor() {}, setBackgroundColor() {},
    BackButton: { show() {}, hide() {}, onClick() {} },
    HapticFeedback: { impactOccurred() {}, notificationOccurred() {}, selectionChanged() {} }
};
const API_BASE = '';

// ===== СОСТОЯНИЕ =====
let state = {
    questions: [],
    currentIndex: 0,
    score: 0,
    correctCount: 0,
    currentTopic: null,
    isDaily: false,
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
    last_daily_date: null
};

let dailyQuestionData = null;

// Карта: какой экран открыть по нажатию аппаратной/программной кнопки
// "Назад" в Telegram, в зависимости от того, что сейчас на экране.
const backHandlers = {
    'quiz-screen': goHome,
    'question-screen': () => confirmLeaveQuiz(),
    'result-screen': goHome,
    'learning-screen': goHome,
    'material-screen': showLearning,
    'disciplines-screen': goHome,
    'sections-screen': showDisciplines,
    'topics-screen': () => showScreen('sections-screen'),
    'stats-screen': goHome,
    'achievements-screen': goHome
};

// ===== ИНИЦИАЛИЗАЦИЯ =====
document.addEventListener('DOMContentLoaded', () => {
    tg.ready();
    tg.expand();

    applyTelegramTheme();
    tg.onEvent('themeChanged', applyTelegramTheme);

    tg.BackButton.onClick(() => {
        const current = document.querySelector('.screen.active')?.id;
        (backHandlers[current] || goHome)();
    });

    if (tg.initDataUnsafe?.user) {
        user.id = tg.initDataUnsafe.user.id;
        const name = tg.initDataUnsafe.user.first_name;
        if (name) {
            const el = document.getElementById('greeting-title');
            if (el) el.textContent = `👋 Привет, ${escapeHtml(name)}!`;
        }
    }

    loadUserData();
    loadDailyQuestion();
    loadQuickTopics();
    loadDisciplines();
    setupFilters();
});

// ===== ТЕМА =====
// У приложения — собственный монохромный стиль с золотыми акцентами
// (см. style.css). Из Telegram мы берём только признак "светлая/тёмная",
// а не произвольные цвета темы — иначе оформление могло бы поехать
// в случайный оттенок, который пользователь выбрал в настройках Telegram.
function applyTelegramTheme() {
    const root = document.documentElement;
    const scheme = tg.colorScheme === 'light' ? 'light' : 'dark';
    root.dataset.scheme = scheme;

    const bg = scheme === 'light' ? '#eceae6' : '#0c0c0e';
    if (tg.setBackgroundColor) {
        try { tg.setBackgroundColor(bg); } catch (e) {}
    }
    if (tg.setHeaderColor) {
        try { tg.setHeaderColor(bg); } catch (e) {}
    }
}

// ===== HAPTIC FEEDBACK =====
function haptic(type = 'light') {
    if (!tg.HapticFeedback) return;
    try {
        if (type === 'success' || type === 'error' || type === 'warning') {
            tg.HapticFeedback.notificationOccurred(type);
        } else if (type === 'selection') {
            tg.HapticFeedback.selectionChanged();
        } else {
            tg.HapticFeedback.impactOccurred(type); // 'light' | 'medium' | 'heavy'
        }
    } catch (e) {}
}

// ===== УТИЛИТЫ =====
function escapeHtml(str) {
    if (str === null || str === undefined) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

function todayStr() {
    return new Date().toISOString().slice(0, 10);
}

function toast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    const el = document.createElement('div');
    el.className = `toast ${type}`;
    el.textContent = message;
    container.appendChild(el);
    requestAnimationFrame(() => el.classList.add('show'));
    setTimeout(() => {
        el.classList.remove('show');
        setTimeout(() => el.remove(), 300);
    }, 3000);
}

function emptyState(message, icon = '📭') {
    return `<div class="empty-state"><span class="empty-icon">${icon}</span><p>${escapeHtml(message)}</p></div>`;
}

function skeletonGrid(count = 4) {
    return `<div class="skeleton-grid">${'<div class="skeleton skeleton-card"></div>'.repeat(count)}</div>`;
}

function skeletonRows(count = 4) {
    return '<div class="skeleton skeleton-row"></div>'.repeat(count);
}

// ===== API =====
async function api(endpoint, options = {}) {
    try {
        const res = await fetch(`${API_BASE}${endpoint}`, options);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return await res.json();
    } catch (e) {
        console.error('API Error:', e);
        toast('Не удалось загрузить данные. Проверьте соединение.', 'error');
        return null;
    }
}

// ===== НАВИГАЦИЯ =====
function showScreen(id) {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    document.getElementById(id).classList.add('active');

    if (id === 'main-screen') {
        tg.BackButton.hide();
    } else {
        tg.BackButton.show();
    }

    document.getElementById('app').scrollIntoView({ block: 'start', behavior: 'instant' in window ? 'instant' : 'auto' });
}

function goHome() {
    showScreen('main-screen');
    loadUserData();
    loadDailyQuestion();
}

function confirmLeaveQuiz() {
    if (state.questions.length && state.currentIndex < state.questions.length) {
        if (!confirm('Прервать викторину? Прогресс по текущей попытке не сохранится.')) return;
    }
    goHome();
}

// ===== ПОЛЬЗОВАТЕЛЬ =====
function loadUserData() {
    const saved = localStorage.getItem('art_quest_user');
    if (saved) {
        try {
            user = { ...user, ...JSON.parse(saved) };
        } catch (e) {}
    }
    updateUI();
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
    const btn = document.getElementById('daily-btn');
    const answeredToday = user.last_daily_date === todayStr();

    document.getElementById('daily-streak').textContent = `Серия: ${user.daily_streak || 0} 🔥`;

    if (answeredToday) {
        document.getElementById('daily-question').textContent = 'Ты уже ответил на сегодняшний вопрос — заходи завтра!';
        btn.textContent = '✅ Выполнено сегодня';
        btn.disabled = true;
        return;
    }

    document.getElementById('daily-question').textContent = 'Загрузка вопроса…';
    btn.textContent = 'Ответить на вызов';
    btn.disabled = false;

    const data = await api('/api/daily');
    if (data?.id) {
        dailyQuestionData = data;
        document.getElementById('daily-question').textContent = data.question;
    } else {
        document.getElementById('daily-question').textContent = 'Вопрос дня пока недоступен.';
        btn.disabled = true;
    }
}

function startDaily() {
    if (!dailyQuestionData) {
        toast('Вопрос дня ещё не загрузился, подождите секунду.', 'error');
        return;
    }
    state.questions = [dailyQuestionData];
    state.currentIndex = 0;
    state.score = 0;
    state.correctCount = 0;
    state.isDaily = true;
    showScreen('question-screen');
    showQuestion();
}

function updateDailyStreakOnCompletion() {
    const today = todayStr();
    if (user.last_daily_date === today) return; // уже засчитано

    const yesterday = new Date(Date.now() - 86400000).toISOString().slice(0, 10);
    user.daily_streak = (user.last_daily_date === yesterday) ? (user.daily_streak || 0) + 1 : 1;
    user.last_daily_date = today;
    saveUser();
}

// ===== БЫСТРЫЕ ТЕМЫ =====
async function loadQuickTopics() {
    const container = document.getElementById('quick-topics-container');
    container.innerHTML = '<div class="skeleton" style="height:36px;width:100%;border-radius:999px;"></div>';

    const data = await api('/api/topics/quick');
    if (data?.topics?.length) {
        container.innerHTML = data.topics.map(t =>
            `<button class="quick-topic-btn" onclick="haptic('light'); startTopicQuiz(${t.id})">${escapeHtml(t.icon || '📚')} ${escapeHtml(t.name)}</button>`
        ).join('');
    } else {
        container.innerHTML = '';
    }
}

// ===== ДИСЦИПЛИНЫ =====
async function loadDisciplines() {
    const container = document.getElementById('disciplines-container');
    container.innerHTML = skeletonGrid(6);

    const data = await api('/api/disciplines');
    if (data?.length) {
        container.innerHTML = data.map(d =>
            `<div class="discipline-card" onclick="haptic('light'); showSections(${d.id})">
                <span class="icon">${escapeHtml(d.icon || '📚')}</span>
                <div class="name">${escapeHtml(d.name)}</div>
                <div class="desc">${escapeHtml(d.description || '')}</div>
            </div>`
        ).join('');
    } else {
        container.innerHTML = emptyState('Дисциплины пока не добавлены.', '📚');
    }
}

function showDisciplines() {
    showScreen('disciplines-screen');
    loadDisciplines();
}

async function showSections(id) {
    const container = document.getElementById('sections-container');
    showScreen('sections-screen');
    container.innerHTML = skeletonGrid(4);

    const data = await api(`/api/sections/${id}`);
    if (data) {
        document.getElementById('sections-title').textContent = data.discipline_name || 'Разделы';
        if (data.sections?.length) {
            container.innerHTML = data.sections.map(s =>
                `<div class="section-card" onclick="haptic('light'); showTopics(${s.id})">
                    <div class="name">${escapeHtml(s.name)}</div>
                    <div class="desc">${escapeHtml(s.description || '')}</div>
                </div>`
            ).join('');
        } else {
            container.innerHTML = emptyState('В этой дисциплине пока нет разделов.', '📂');
        }
    }
}

async function showTopics(id) {
    const container = document.getElementById('topics-container');
    showScreen('topics-screen');
    container.innerHTML = skeletonGrid(4);

    const data = await api(`/api/topics/${id}`);
    if (data) {
        document.getElementById('topics-title').textContent = data.section_name || 'Темы';
        if (data.topics?.length) {
            container.innerHTML = data.topics.map(t =>
                `<div class="topic-card" onclick="haptic('light'); startTopicQuiz(${t.id})">
                    <div class="name">${escapeHtml(t.name)}</div>
                    <div class="desc">${escapeHtml(t.description || '')}</div>
                    <div class="count">${t.question_count || 0} вопросов</div>
                </div>`
            ).join('');
        } else {
            container.innerHTML = emptyState('В этом разделе пока нет тем.', '📄');
        }
    }
}

// ===== ОБУЧЕНИЕ =====
function showLearning() {
    showScreen('learning-screen');
    loadLearning();
}

async function loadLearning() {
    const container = document.getElementById('learning-container');
    container.innerHTML = skeletonRows(5);

    const data = await api('/api/learning');
    if (data?.length) {
        container.innerHTML = data.map(item =>
            `<div class="learning-item" onclick="haptic('light'); showMaterial(${item.id})">
                <div>
                    <div class="title">${escapeHtml(item.title)}</div>
                    <div class="desc">${escapeHtml(item.description || '')}</div>
                </div>
                <span class="arrow">›</span>
            </div>`
        ).join('');
    } else {
        container.innerHTML = emptyState('Обучающих материалов пока нет.', '📖');
    }
}

async function showMaterial(id) {
    const data = await api(`/api/material/${id}`);
    if (data?.id) {
        showScreen('material-screen');
        document.getElementById('material-title').textContent = data.title;
        document.getElementById('material-content').innerHTML = escapeHtml(data.content).replace(/\n/g, '<br>');
        state.currentTopic = data.topic_id;
    } else {
        toast('Не удалось загрузить материал.', 'error');
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
        const prev = select.value;
        select.innerHTML = '<option value="all">Все дисциплины</option>' +
            data.map(d => `<option value="${d.id}">${escapeHtml(d.icon || '')} ${escapeHtml(d.name)}</option>`).join('');
        select.value = prev || 'all';
    }
}

async function updateQuizTopics() {
    const disciplineId = document.getElementById('quiz-discipline').value;
    const select = document.getElementById('quiz-topic');
    select.innerHTML = '<option value="all">Все темы</option>';
    if (disciplineId !== 'all') {
        const data = await api(`/api/discipline-topics/${disciplineId}`);
        if (data) data.forEach(t => {
            select.innerHTML += `<option value="${t.id}">${escapeHtml(t.name)}</option>`;
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
        state.isDaily = false;
        showScreen('question-screen');
        showQuestion();
    } else {
        toast('Вопросов по выбранным критериям не найдено.', 'error');
    }
}

function startTopicQuiz(id) {
    api(`/api/questions/topic/${id}?limit=10`).then(data => {
        if (data?.length) {
            state.questions = data;
            state.currentIndex = 0;
            state.score = 0;
            state.correctCount = 0;
            state.isDaily = false;
            showScreen('question-screen');
            showQuestion();
        } else {
            toast('Вопросов по этой теме пока нет.', 'error');
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
    document.getElementById('question-difficulty').textContent = '⭐'.repeat(q.difficulty || 1);
    document.getElementById('question-explanation').style.display = 'none';

    const container = document.getElementById('options-container');
    container.innerHTML = '';
    let options = [];
    try { options = JSON.parse(q.options); } catch (e) { options = []; }
    options.forEach((opt, i) => {
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
    haptic(isCorrect ? 'success' : 'error');

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
    }, 2600);
}

function showResult() {
    showScreen('result-screen');
    const total = state.questions.length;
    const correct = state.correctCount;
    const pct = total ? Math.round((correct / total) * 100) : 0;

    let emoji = '📚', title = 'Хороший результат!';
    if (pct >= 90) { emoji = '🏆'; title = 'Блестяще! Вы — эрудит!'; }
    else if (pct >= 70) { emoji = '⭐'; title = 'Отлично! Продолжайте!'; }
    else if (pct >= 50) { emoji = '📖'; title = 'Неплохо! Учитесь дальше.'; }
    else { emoji = '💪'; title = 'Ничего страшного! Попробуйте снова.'; }

    if (state.isDaily) {
        title = correct > 0 ? 'Вызов дня пройден!' : 'В следующий раз получится!';
    }

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

    if (state.isDaily) {
        updateDailyStreakOnCompletion();
    }

    saveUser();
    haptic(pct >= 50 ? 'success' : 'warning');
    checkAchievements();
}

// ===== ДОСТИЖЕНИЯ =====
function showAchievements() {
    showScreen('achievements-screen');
    loadAchievements();
}

async function loadAchievements() {
    const container = document.getElementById('achievements-container');
    container.innerHTML = skeletonRows(4);

    const params = new URLSearchParams({
        user_id: user.id || '',
        correct_answers: user.correct_answers || 0,
        score: user.score || 0
    });
    const data = await api(`/api/achievements?${params.toString()}`);
    if (data?.length) {
        container.innerHTML = data.map(a =>
            `<div class="achievement ${a.unlocked ? 'unlocked' : 'locked'}">
                <span class="icon">${a.unlocked ? escapeHtml(a.icon || '🏅') : '🔒'}</span>
                <div class="info">
                    <div class="name">${escapeHtml(a.name)}</div>
                    <div class="desc">${escapeHtml(a.description)} ${a.unlocked ? '✅' : `(${a.progress || 0}/${a.condition_value})`}</div>
                </div>
            </div>`
        ).join('');
    } else {
        container.innerHTML = emptyState('Достижения пока не добавлены.', '🏅');
    }
}

async function checkAchievements() {
    if (!user.id) return;
    const data = await api('/api/check-achievements', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            id: user.id,
            correct_answers: user.correct_answers,
            score: user.score
        })
    });
    if (data?.unlocked?.length) {
        data.unlocked.forEach(name => toast(`🏅 Новое достижение: ${name}!`, 'success'));
    }
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
    if (!user.id) return;
    fetch('/api/progress', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: user.id, question_id: qId, correct })
    }).catch(() => {});
}
