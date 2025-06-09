// 页面元素
const logoScreen = document.getElementById('logo-screen');
const startBtn = document.getElementById('start-btn');
const toySelectScreen = document.getElementById('toy-select-screen');
const toyBtns = document.querySelectorAll('.toy-btn');
const gameScreen = document.getElementById('game-screen');
const scoreSpan = document.getElementById('score');
const timerSpan = document.getElementById('timer');
const canvas = document.getElementById('game-canvas');
const ctx = canvas.getContext('2d');
const restartBtn = document.getElementById('restart-btn');

// 玩具 emoji
const toyEmojis = {
    fish: '🐟',
    ball: '⚽',
    mouse: '🐭'
};

// 预加载音效
const hitAudio = new Audio('https://cdn.pixabay.com/audio/2022/07/26/audio_124bfae5b2.mp3'); // 轻快点击音
const endAudio = new Audio('https://cdn.pixabay.com/audio/2022/03/15/audio_115b9b7b7e.mp3'); // 游戏结束音

let selectedToy = 'fish';
let score = 0;
let timeLeft = 30;
let gameInterval = null;
let timerInterval = null;
let toy = null;
let audioUnlocked = false;

function showScreen(screen) {
    logoScreen.style.display = 'none';
    toySelectScreen.style.display = 'none';
    gameScreen.style.display = 'none';
    screen.style.display = 'flex';
}

startBtn.onclick = () => {
    showScreen(toySelectScreen);
};

toyBtns.forEach(btn => {
    btn.onclick = () => {
        selectedToy = btn.dataset.toy;
        startGame();
    };
});

restartBtn.onclick = () => {
    showScreen(toySelectScreen);
};

function startGame() {
    score = 0;
    timeLeft = 30;
    scoreSpan.textContent = '分数: 0';
    timerSpan.textContent = '时间: 30';
    restartBtn.style.display = 'none';
    showScreen(gameScreen);
    toy = createToy();
    gameInterval = setInterval(gameLoop, 16);
    timerInterval = setInterval(() => {
        timeLeft--;
        timerSpan.textContent = `时间: ${timeLeft}`;
        if (timeLeft <= 0) {
            endGame();
        }
    }, 1000);
}

function endGame() {
    clearInterval(gameInterval);
    clearInterval(timerInterval);
    restartBtn.style.display = 'block';
    endAudio.currentTime = 0;
    endAudio.play().catch(() => {});
}

function createToy() {
    // 随机初始位置和速度
    const size = 48;
    return {
        x: Math.random() * (canvas.width - size),
        y: Math.random() * (canvas.height - size),
        vx: (Math.random() - 0.5) * 6,
        vy: (Math.random() - 0.5) * 6,
        size: size
    };
}

function gameLoop() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    // 移动玩具
    toy.x += toy.vx;
    toy.y += toy.vy;
    // 边界反弹
    if (toy.x < 0 || toy.x > canvas.width - toy.size) toy.vx *= -1;
    if (toy.y < 0 || toy.y > canvas.height - toy.size) toy.vy *= -1;
    // 发光特效
    ctx.save();
    ctx.shadowColor = 'rgba(255,255,0,0.7)';
    ctx.shadowBlur = 25;
    ctx.font = toy.size + 'px serif';
    ctx.textAlign = 'left';
    ctx.textBaseline = 'top';
    ctx.fillText(toyEmojis[selectedToy], toy.x, toy.y);
    ctx.restore();
    // 再画一遍正常emoji
    ctx.font = toy.size + 'px serif';
    ctx.textAlign = 'left';
    ctx.textBaseline = 'top';
    ctx.fillText(toyEmojis[selectedToy], toy.x, toy.y);
}

canvas.addEventListener('pointerdown', function(e) {
    // 首次交互解锁所有音频
    if (!audioUnlocked) {
        hitAudio.play().then(() => {
            hitAudio.pause();
            hitAudio.currentTime = 0;
        }).catch(() => {});
        endAudio.play().then(() => {
            endAudio.pause();
            endAudio.currentTime = 0;
        }).catch(() => {});
        audioUnlocked = true;
    }
    if (timeLeft <= 0) return;
    const rect = canvas.getBoundingClientRect();
    const x = (e.clientX - rect.left) * (canvas.width / rect.width);
    const y = (e.clientY - rect.top) * (canvas.height / rect.height);
    // 判断是否点中玩具
    if (
        x >= toy.x && x <= toy.x + toy.size &&
        y >= toy.y && y <= toy.y + toy.size
    ) {
        score++;
        scoreSpan.textContent = `分数: ${score}`;
        toy = createToy();
        hitAudio.currentTime = 0;
        hitAudio.play().catch(() => {});
    }
});

// 适配屏幕尺寸
function resizeCanvas() {
    const size = Math.min(window.innerWidth * 0.9, 400);
    canvas.width = size;
    canvas.height = size;
}
window.addEventListener('resize', resizeCanvas);
resizeCanvas(); 